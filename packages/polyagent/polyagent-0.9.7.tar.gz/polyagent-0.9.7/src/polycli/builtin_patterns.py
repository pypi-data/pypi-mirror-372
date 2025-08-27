from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from .orchestration import pattern, batch
from .polyagent import PolyAgent
from .adapters import RunResult
import json

@pattern
def notify(agent: PolyAgent, msg: str, source="User"):
    notify_text = f"A message from {source}:\n{msg}"
    agent.messages.add_user_message(notify_text)

@pattern
def tell(speaker: PolyAgent, listener: PolyAgent, instruction="Your current status.", model="glm-4.5"):
    # Use the agent's id attribute
    speaker_id = speaker.id
    listener_id = listener.id
    instruction_prompt = f"Your task now is to send a message to agent {listener_id}. The purpose is communication and information exchange. Explain honestly in detail what you know about [{instruction}]. Your full response will be sent directly. So begin directly with the message's content."
    message = speaker.run(instruction_prompt, cli="no-tools", model=model).content
    message_prompt = f"Your inbox: message from agent {speaker_id}:\n{message}"
    listener.messages.add_user_message(message_prompt)

@pattern
def get_status(agent: PolyAgent, n_exchanges: int = 3, model: str = "glm-4.5"):
    """
    Generate a status report of the agent's recent work.
    
    Args:
        n_exchanges: Number of recent user interactions to summarize.
        model: Model to use for generating the report.
    
    Returns:
        A structured status report.
    """
    prompt = f"""Analyze and summarize your work on the last {n_exchanges} user interactions (<5 sentences).

Structure your response as:
Analysis: [What types of tasks were worked on, any patterns or challenges encountered]
Key Outcomes: [What was accomplished, created, fixed, or discovered]
Current Status: [Any pending items, next steps, or relevant context]"""
    
    return agent.run(prompt, model=model, ephemeral=True).content


class WritingPlan(BaseModel):
    """Schema for multi-head writing plan"""
    sections: List[Dict[str, str]] = Field(
        description="List of sections to write, each with 'title' and 'instructions'"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "sections": [
                    {
                        "title": "Introduction", 
                        "instructions": "Write an introduction covering..."
                    },
                    {
                        "title": "Technical Details",
                        "instructions": "Explain the technical implementation..."
                    }
                ]
            }
        }


@pattern
def multi_head_write(
    agent: PolyAgent,
    prompt: str,
    model: Optional[str] = None,
    max_sections: int = 10,
    section_token_limit: int = 20000,
    planning_model: Optional[str] = None,
    writing_model: Optional[str] = None,
    verbose: bool = True
) -> RunResult:
    """
    Multi-head parallel writing pattern.
    
    Splits a complex writing task into sections, writes them in parallel,
    then concatenates the results.
    
    Args:
        agent: The main agent to use for planning
        prompt: The writing task prompt
        model: Default model to use (can be overridden by planning/writing models)
        max_sections: Maximum number of sections to create (1-10)
        section_token_limit: Token limit for each section writer
        planning_model: Model to use for planning (defaults to model)
        writing_model: Model to use for section writing (defaults to model)
        verbose: Print progress information
        
    Returns:
        RunResult with concatenated content from all sections
    """
    
    # Determine models to use
    planning_model = planning_model or model or "glm-4.5"
    writing_model = writing_model or model or "glm-4.5"
    
    # Clamp max_sections
    max_sections = min(max(1, max_sections), 10)
    
    if verbose:
        print(f"[Multi-Head Write] Planning with {planning_model}...")
    
    # Step 1: Create structured plan
    planning_prompt = f"""
You are a content architect. Break down this writing task into {max_sections} or fewer distinct sections.
Each section should be self-contained and focus on a specific aspect.

Writing Task:
{prompt}

Create a plan with clear sections. Each section needs:
1. A descriptive title
2. Specific instructions for what to write

Make sure sections don't overlap and together they fully address the task.
If the task is simple, use fewer sections. Complex tasks can use up to {max_sections} sections.
"""
    
    plan_result = agent.run(
        planning_prompt,
        model=planning_model,
        schema_cls=WritingPlan,
        ephemeral=True,
        max_tokens=section_token_limit
    )
    
    if not plan_result.is_success:
        return RunResult({
            "status": "error",
            "message": f"Planning failed: {plan_result.error_message}"
        })
    
    # Parse the plan
    try:
        if hasattr(plan_result, 'data') and plan_result.data:
            plan = plan_result.data
        else:
            # Try to parse from content
            plan = json.loads(plan_result.content)
    except Exception as e:
        return RunResult({
            "status": "error", 
            "message": f"Failed to parse plan: {e}"
        })
    
    sections = plan.get('sections', [])
    
    if not sections:
        return RunResult({
            "status": "error",
            "message": "No sections generated in plan"
        })
    
    if verbose:
        print(f"[Multi-Head Write] Created {len(sections)} sections:")
        for i, section in enumerate(sections, 1):
            print(f"  {i}. {section.get('title', 'Untitled')}")
    
    # Step 2: Create writer agents for each section
    writers = []
    for i, section in enumerate(sections):
        writer = PolyAgent(
            id=f"{agent.id}_section_{i}",
            max_tokens=section_token_limit
        )
        writers.append((writer, section))
    
    if verbose:
        print(f"[Multi-Head Write] Starting parallel writing with {len(writers)} writers...")
    
    # Step 3: Write sections in parallel using patterns
    @pattern  
    def write_section(writer: PolyAgent, title: str, instructions: str, original_task: str):
        section_prompt = f"""
Context (original task): {original_task}

Write the following section for a larger document. Focus only on this specific section.

Your assined section title: {title}

Instructions: {instructions}

Write only the content for your assigned section. Do not include the section title in your response.
"""
        
        result = writer.run(
            section_prompt,
            model=writing_model,
            ephemeral=True,
            max_tokens=section_token_limit
        )
        return result
    
    # Execute sections in parallel and get futures
    with batch():
        futures = []
        for writer, section in writers:
            future = write_section(
                writer, 
                section.get('title', 'Section'),
                section.get('instructions', 'Write this section'),
                prompt
            )
            futures.append((section.get('title', 'Section'), future))
    
    # Step 4: Collect and concatenate results from futures
    final_content = []
    failed_sections = []
    
    for title, future in futures:
        try:
            # Access result through the future (transparently proxies to RunResult)
            if future.is_success:
                # Add section with title
                final_content.append(f"## {title}\n\n{future.content}")
            else:
                failed_sections.append(title)
                if verbose:
                    print(f"[Multi-Head Write] Warning: Section '{title}' failed: {future.error_message}")
        except Exception as e:
            failed_sections.append(title)
            if verbose:
                print(f"[Multi-Head Write] Warning: Section '{title}' raised exception: {e}")
    
    if not final_content:
        return RunResult({
            "status": "error",
            "message": f"All sections failed to generate"
        })
    
    # Join all sections
    concatenated = "\n\n".join(final_content)
    
    if verbose:
        print(f"[Multi-Head Write] Completed: {len(final_content)}/{len(sections)} sections")
        print(f"[Multi-Head Write] Total length: {len(concatenated)} characters")
        if failed_sections:
            print(f"[Multi-Head Write] Failed sections: {', '.join(failed_sections)}")
    
    # Return successful result
    return RunResult({
        "status": "success",
        "message": {
            "role": "assistant",
            "content": concatenated
        },
        "metadata": {
            "sections_planned": len(sections),
            "sections_completed": len(final_content),
            "sections_failed": len(failed_sections),
            "total_length": len(concatenated)
        }
    })

