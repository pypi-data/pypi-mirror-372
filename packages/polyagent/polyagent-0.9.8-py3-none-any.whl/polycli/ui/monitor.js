import { h, render } from "preact";
import { useEffect, useMemo, useRef, useState } from "preact/hooks";
import htm from "htm";
import { marked } from "marked";
import mermaid from "mermaid";
const html = htm.bind(h);

// Initialize Mermaid
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  themeVariables: {
    primaryColor: '#2563eb',
    primaryTextColor: '#ffffff',
    primaryBorderColor: '#1d4ed8',
    lineColor: '#64748b',
    secondaryColor: '#f1f5f9',
    tertiaryColor: '#ffffff'
  }
});

// Utilities
const j = (v) => { try { return JSON.stringify(v, null, 2); } catch { return String(v); } };

// Function to render markdown with Mermaid and formula support
async function renderMarkdownWithMermaid(content) {
  // Configure marked options for better markdown rendering
  marked.setOptions({
    breaks: true,        // Enable line breaks
    gfm: true,          // Enable GitHub Flavored Markdown
    headerIds: false,   // Don't generate header IDs
    mangle: false,      // Don't mangle email addresses
    sanitize: false,    // Don't sanitize HTML
    pedantic: false,    // Don't be pedantic
    smartLists: true,   // Use smarter list behavior
    smartypants: false  // Don't use smartypants
  });
  
  // First, render with marked
  const html = marked.parse(content);

  // Create a temporary div to parse the HTML
  const tempDiv = document.createElement('div');
  tempDiv.innerHTML = html;
  
  // Process mermaid code blocks
  const mermaidBlocks = tempDiv.querySelectorAll('pre code[class*="language-mermaid"]');

  for (const block of mermaidBlocks) {
    const pre = block.parentElement;
    const mermaidCode = block.textContent;

    try {
      // Create a div for the mermaid diagram
      const mermaidDiv = document.createElement('div');
      mermaidDiv.className = 'mermaid';

      // Replace the pre block with the mermaid div
      pre.replaceWith(mermaidDiv);

      // Render the mermaid diagram
      const { svg } = await mermaid.render('mermaid-' + Math.random().toString(36).substr(2, 9), mermaidCode);
      mermaidDiv.innerHTML = svg;
    } catch (error) {
      console.error('Error rendering mermaid diagram:', error);
      // Keep the original code block if mermaid fails
      pre.replaceWith(block);
    }
  }

  return tempDiv.innerHTML;
}
// Detect base path from current URL (e.g., /session/xxx/ -> /session/xxx)
const basePath = window.location.pathname.replace(/\/$/, '').replace(/\/index\.html$/, '');
async function getJSON(url, opts){ 
  // Make URLs relative to base path
  const fullUrl = url.startsWith('/') ? basePath + url : url;
  const r = await fetch(fullUrl, opts); 
  if(!r.ok) throw new Error(await r.text()); 
  return r.json(); 
}
function post(url, body){ return getJSON(url, { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body||{}) }); }

// Data hook
function useSessionModel(){
  const [records, setRecords] = useState([]);
  const [paused, setPaused] = useState(false);
  const [pendingInjections, setPendingInjections] = useState({}); // agent_id -> [messages]
  const recMapRef = useRef(new Map());

  useEffect(() => {
    let es;
    (async () => {
      try {
        const init = await getJSON('/records');
        setPaused(!!init.paused);
        const recs = init.records || [];
        setRecords(recs);
        recMapRef.current = new Map(recs.map(r => [r.id, r]));
        // Restore pending injections from backend
        if (init.pending_injections) {
          setPendingInjections(init.pending_injections);
        }
      } catch (e) { console.error(e); }

      try {
        es = new EventSource(basePath + '/events');

        es.onopen = () => {
          console.log('SSE connected');
        };

        es.onmessage = (ev) => {
          if (!ev.data) return;
          let payload;
          try {
            payload = JSON.parse(ev.data);
          } catch (err) {
            console.error('Failed to parse SSE data:', ev.data, err);
            return;
          }
          const { type } = payload;

          if (type === 'paused') {
            setPaused(!!payload.value);
            if (!payload.value) {
              // Clear pending injections when resuming
              setPendingInjections({});
            }
            return;
          }

          if (type === 'record-start' || type === 'record-finish') {
            const rec = payload.record;
            if (!rec) {
              console.warn('No record in payload:', payload);
              return;
            }
            if (rec.id == null) {
              console.warn('Record missing ID:', rec);
              return;
            }

            const m = recMapRef.current;
            const prev = m.get(rec.id);

            if (!prev) {
              m.set(rec.id, rec);
              setRecords(old => [...old, rec]);
            } else {
              const merged = { ...prev, ...rec };
              if (prev.agents && rec.agents) {
                merged.agents = { ...prev.agents };
                for (const k of Object.keys(rec.agents)) {
                  merged.agents[k] = { ...(prev.agents[k]||{}), ...(rec.agents[k]||{}) };
                }
              }
              m.set(rec.id, merged);
              setRecords(old => old.map(r => r.id === rec.id ? merged : r));
            }
          }
        };

        es.onerror = (e) => {
          console.error('SSE connection error (will auto-reconnect):', e);
        };
      } catch (e) { console.error('SSE setup failed', e); }
    })();
    return () => { if (es) es.close(); };
  }, []);

  return { records, paused, setPaused, pendingInjections, setPendingInjections };
}

// Message Item Component with Mermaid support
function MessageItem({ msg }) {
  const [renderedContent, setRenderedContent] = useState('');

  useEffect(() => {
    renderMarkdownWithMermaid(msg.content).then(html => {
      setRenderedContent(html);
    });
  }, [msg.content]);
  
  return html`
    <div class="message-item">
      <div class="message-role">${msg.role.toUpperCase()}</div>
      <div class="message-content" dangerouslySetInnerHTML=${{ __html: renderedContent }}></div>
    </div>
  `;
}

// Agent Panel Component
function AgentPanel({ records, paused, onPause, onResume, onInject, pendingInjections, setPendingInjections, onAgentChange, onFilterChange }){
  const [selectedAgent, setSelectedAgent] = useState('');
  const [filterPatterns, setFilterPatterns] = useState(false);
  const [inputText, setInputText] = useState('');
  const messageHistoryRef = useRef(null);
  const userScrolledRef = useRef(false);

  // Get all unique agents
  const agents = useMemo(() => {
    const s = new Set();
    records.forEach(r => Object.values(r.agents || {}).forEach(meta => s.add(meta.id ?? 'unnamed')));
    return Array.from(s).sort();
  }, [records]);

  // Set initial agent and notify parent
  useEffect(() => {
    if (!selectedAgent && agents.length) {
      setSelectedAgent(agents[0]);
      onAgentChange(agents[0]);
    }
    if (selectedAgent && !agents.includes(selectedAgent) && agents.length) {
      setSelectedAgent(agents[0]);
      onAgentChange(agents[0]);
    }
  }, [agents, selectedAgent]);

  // Notify parent when selection changes
  useEffect(() => {
    onAgentChange(selectedAgent);
    // Scroll to bottom when agent changes
    if (messageHistoryRef.current) {
      setTimeout(() => {
        const scrollContainer = messageHistoryRef.current.querySelector('.message-history-inner');
        if (scrollContainer) {
          scrollContainer.scrollTop = scrollContainer.scrollHeight;
        }
      }, 50); // Small delay to ensure DOM is updated
    }
  }, [selectedAgent]);

  // Notify parent when filter changes
  useEffect(() => {
    onFilterChange(filterPatterns);
  }, [filterPatterns]);

  // Aggregate messages for selected agent
  const agentMessages = useMemo(() => {
    if (!selectedAgent) return [];

    // Find the most recent record with this agent's messages
    let latestMessages = [];

    // Go through records in reverse to find the latest messages for this agent
    for (let i = records.length - 1; i >= 0; i--) {
      const rec = records[i];
      const agents = rec.agents || {};

      for (const [param, meta] of Object.entries(agents)) {
        if ((meta.id ?? 'unnamed') === selectedAgent && meta.messages) {
          // Found the latest messages for this agent
          latestMessages = meta.messages || [];
          break;
        }
      }

      if (latestMessages.length > 0) break;
    }

    // Return the full message history
    return latestMessages.map((msg, idx) => ({
      messageIdx: idx,
      ...msg
    }));
  }, [selectedAgent, records]);

  // Auto-scroll when messages update for current agent (only if user hasn't scrolled)
  useEffect(() => {
    if (messageHistoryRef.current && agentMessages.length > 0) {
      const scrollContainer = messageHistoryRef.current.querySelector('.message-history-inner');
      if (scrollContainer && !userScrolledRef.current) {
        // Only auto-scroll if user hasn't manually scrolled
        setTimeout(() => {
          scrollContainer.scrollTop = scrollContainer.scrollHeight;
        }, 50);
      }
    }
  }, [agentMessages.length]);

  // Track if user has manually scrolled
  useEffect(() => {
    const scrollContainer = messageHistoryRef.current?.querySelector('.message-history-inner');
    if (!scrollContainer) return;

    const handleScroll = () => {
      const isAtBottom = Math.abs(scrollContainer.scrollHeight - scrollContainer.scrollTop - scrollContainer.clientHeight) < 5;
      userScrolledRef.current = !isAtBottom;
    };

    scrollContainer.addEventListener('scroll', handleScroll);
    return () => scrollContainer.removeEventListener('scroll', handleScroll);
  }, [selectedAgent]); // Reset when agent changes

  const scrollToBottom = () => {
    const scrollContainer = messageHistoryRef.current?.querySelector('.message-history-inner');
    if (scrollContainer) {
      scrollContainer.scrollTop = scrollContainer.scrollHeight;
      userScrolledRef.current = false;
    }
  };

  const handleInject = async () => {
    if (!inputText.trim() || !selectedAgent) return;

    // Add to pending injections
    setPendingInjections(prev => ({
      ...prev,
      [selectedAgent]: [...(prev[selectedAgent] || []), inputText.trim()]
    }));

    // Send to server
    await onInject(selectedAgent, inputText.trim());
    setInputText('');

    // Scroll to bottom after sending
    setTimeout(scrollToBottom, 100);
  };

  const agentPending = pendingInjections[selectedAgent] || [];

  return html`
    <div class="agent-panel">
      <div class="agent-selector">
        <select value=${selectedAgent} onChange=${e => setSelectedAgent(e.target.value)}>
          ${agents.length === 0 && html`<option value="">No agents yet</option>`}
          ${agents.map(id => html`<option value=${id}>${id}</option>`)}
        </select>
        <label class="filter-checkbox">
          <input 
            type="checkbox" 
            checked=${filterPatterns} 
            onChange=${e => setFilterPatterns(e.target.checked)}
          />
          Filter patterns
        </label>
      </div>
      
      <div class="message-history" ref=${messageHistoryRef}>
        <div class="message-history-inner">
          ${agentMessages.length === 0 && agentPending.length === 0 && html`
            <div style="text-align: center; color: var(--muted); padding: 20px;">
              No messages yet for this agent
            </div>
          `}
          ${agentMessages.map(msg => html`
            <${MessageItem} msg=${msg} />
          `)}
          
          ${agentPending.length > 0 && html`
            <div class="pending-section">
              <div class="pending-header">Pending Injections (will send on resume):</div>
              ${agentPending.map(text => html`
                <div class="pending-item">${text}</div>
              `)}
            </div>
          `}
        </div>
      </div>
      
      <div class="injection-controls">
        <input 
          class="injection-input"
          type="text"
          placeholder=${paused ? "Type message to inject..." : "Pause to inject messages"}
          value=${inputText}
          onInput=${e => setInputText(e.target.value)}
          onKeyDown=${e => e.key === 'Enter' && paused && handleInject()}
          disabled=${!paused}
        />
        <button 
          class="btn btn-inject" 
          onClick=${handleInject}
          disabled=${!paused || !inputText.trim()}
        >
          Send
        </button>
        <button 
          class=${paused ? 'btn btn-resume' : 'btn btn-pause'}
          onClick=${paused ? onResume : onPause}
        >
          ${paused ? 'Resume' : 'Pause'}
        </button>
      </div>
    </div>
  `;
}

// Pattern Timeline Component
function PatternTimeline({ records, filterAgent, filterEnabled }){
  const [page, setPage] = useState(0);
  const [expandedRecords, setExpandedRecords] = useState(new Set());
  const [activeBatchTabs, setActiveBatchTabs] = useState({}); // Track active tab for each batch
  const itemsPerPage = 7; // Reduced from 10 to 7

  // Group records by batch_id and filter
  const groupedRecords = useMemo(() => {
    let recs = [...records];

    // Filter by agent if enabled
    if (filterEnabled && filterAgent) {
      recs = recs.filter(rec =>
        Object.values(rec.agents || {}).some(meta => (meta.id ?? 'unnamed') === filterAgent)
      );
    }

    // Group by batch_id
    const groups = [];
    const batchMap = new Map();

    recs.forEach(rec => {
      if (rec.batch_id !== null && rec.batch_id !== undefined) {
        // Part of a batch
        if (!batchMap.has(rec.batch_id)) {
          const batchGroup = {
            type: 'batch',
            batch_id: rec.batch_id,
            records: [],
            status: 'running'
          };
          batchMap.set(rec.batch_id, batchGroup);
          groups.push(batchGroup);
        }
        batchMap.get(rec.batch_id).records.push(rec);
        // Update batch status based on all records in the batch
        const batch = batchMap.get(rec.batch_id);
        if (batch.records.every(r => r.status === 'done')) {
          batch.status = 'done';
        } else if (batch.records.some(r => r.status === 'running')) {
          batch.status = 'running';
        }
      } else {
        // Standalone pattern
        groups.push({
          type: 'single',
          record: rec
        });
      }
    });

    // Sort batches by their index
    groups.forEach(group => {
      if (group.type === 'batch') {
        group.records.sort((a, b) => (a.batch_index || 0) - (b.batch_index || 0));
      }
    });

    // Reverse to show newest first
    return groups.reverse();
  }, [records, filterAgent, filterEnabled]);

  // Pagination
  const totalPages = Math.ceil(groupedRecords.length / itemsPerPage);
  const currentGroups = groupedRecords.slice(page * itemsPerPage, (page + 1) * itemsPerPage);

  // Auto-scroll to first page when new records arrive
  useEffect(() => {
    if (page > 0 && groupedRecords.length > records.length) {
      setPage(0);
    }
  }, [groupedRecords.length]);

  const toggleExpanded = (recordId) => {
    setExpandedRecords(prev => {
      const next = new Set(prev);
      if (next.has(recordId)) {
        next.delete(recordId);
      } else {
        next.add(recordId);
      }
      return next;
    });
  };

  const setActiveTab = (batchId, tabIndex) => {
    setActiveBatchTabs(prev => ({
      ...prev,
      [batchId]: tabIndex
    }));
  };

  return html`
    <div class="pattern-timeline">
      <div class="timeline-content">
        ${currentGroups.length === 0 && html`
          <div class="muted" style="text-align: center; padding: 40px;">
            ${filterEnabled ? 'No patterns found for selected agent' : 'No patterns executed yet'}
          </div>
        `}
        
        ${currentGroups.map((group, idx) => {
          if (group.type === 'single') {
            // Render single pattern as before
            const rec = group.record;
            const status = rec.status || 'done';
            const agentList = Object.entries(rec.agents || {}).map(([param, meta]) => 
              `${param}: ${meta.id ?? 'unnamed'}`
            );
            const isExpanded = expandedRecords.has(rec.id);
            
            return html`
              <div 
                class=${'pattern-card' + (status === 'running' ? ' running' : '')}
                onClick=${() => toggleExpanded(rec.id)}
              >
                <div class="pattern-header">
                  <div style="flex: 1;">
                    <span class="pattern-title">
                      #${groupedRecords.length - (page * itemsPerPage + idx)} ${rec.pattern}
                    </span>
                    <div class="pattern-agents" style="margin-top: 4px;">
                      ${agentList.join(', ')}
                    </div>
                  </div>
                  <span class=${'badge ' + status}>${status}</span>
                </div>
                
                ${isExpanded && html`
                  <div class="pattern-details" onClick=${(e) => e.stopPropagation()}>
                    <div style="margin-bottom: 8px">
                      <strong>Inputs:</strong>
                      <pre style="font-size: 11px; margin-top: 4px;">${j(rec.inputs || {})}</pre>
                    </div>
                    ${status === 'done' && html`
                      <div>
                        <strong>Result:</strong>
                        <pre style="font-size: 11px; margin-top: 4px;">${j(rec.result)}</pre>
                      </div>
                    `}
                  </div>
                `}
              </div>
            `;
          } else {
            // Render batch as tabbed interface
            const activeTab = activeBatchTabs[group.batch_id] || 0;
            const activeRec = group.records[activeTab];
            const isExpanded = expandedRecords.has(group.batch_id);
            
            return html`
              <div class=${'batch-card' + (group.status === 'running' ? ' running' : '')}>
                <div class="batch-header" onClick=${() => toggleExpanded(group.batch_id)}>
                  <span class="batch-title">
                    #${groupedRecords.length - (page * itemsPerPage + idx)} Batch
                  </span>
                  <span class=${'badge ' + group.status}>${group.status}</span>
                </div>
                
                <div class="batch-tabs">
                  ${group.records.map((rec, tabIdx) => html`
                    <button 
                      class=${'tab' + (activeTab === tabIdx ? ' active' : '')}
                      onClick=${(e) => {
                        e.stopPropagation();
                        setActiveTab(group.batch_id, tabIdx);
                      }}
                    >
                      ${rec.pattern}
                      ${rec.status === 'running' && html`
                        <span class="tab-status">⏳</span>
                      `}
                    </button>
                  `)}
                </div>
                
                ${activeRec && html`
                  <div class="tab-content">
                    <div class="pattern-agents">
                      ${Object.entries(activeRec.agents || {}).map(([param, meta]) => 
                        `${param}: ${meta.id ?? 'unnamed'}`
                      ).join(', ')}
                    </div>
                    
                    ${isExpanded && html`
                      <div class="pattern-details">
                        <div style="margin-bottom: 8px">
                          <strong>Inputs:</strong>
                          <pre style="font-size: 11px; margin-top: 4px;">${j(activeRec.inputs || {})}</pre>
                        </div>
                        ${activeRec.status === 'done' && html`
                          <div>
                            <strong>Result:</strong>
                            <pre style="font-size: 11px; margin-top: 4px;">${j(activeRec.result)}</pre>
                          </div>
                        `}
                      </div>
                    `}
                  </div>
                `}
              </div>
            `;
          }
        })}
      </div>
      
      <div class="pagination">
        <button 
          onClick=${() => setPage(0)} 
          disabled=${page === 0 || totalPages === 0}
        >
          First
        </button>
        <button 
          onClick=${() => setPage(p => Math.max(0, p - 1))} 
          disabled=${page === 0 || totalPages === 0}
        >
          Prev
        </button>
        <span style="padding: 0 12px; font-size: 13px;">
          Page ${totalPages > 0 ? page + 1 : 0} of ${Math.max(1, totalPages)}
        </span>
        <button 
          onClick=${() => setPage(p => Math.min(totalPages - 1, p + 1))} 
          disabled=${page === totalPages - 1 || totalPages === 0}
        >
          Next
        </button>
        <button 
          onClick=${() => setPage(totalPages - 1)} 
          disabled=${page === totalPages - 1 || totalPages === 0}
        >
          Last
        </button>
      </div>
    </div>
  `;
}

// Main App Component
function App(){
  const { records, paused, pendingInjections, setPendingInjections } = useSessionModel();
  const [selectedAgent, setSelectedAgent] = useState('');
  const [filterEnabled, setFilterEnabled] = useState(false);

  async function onPause(){ await post('/pause'); }
  async function onResume(){ await post('/resume'); }
  async function onInject(agentId, text){ await post('/inject', { agent_id: agentId, text }); }

  return html`
    <div class="main-layout">
      <${AgentPanel}
        records=${records}
        paused=${paused}
        onPause=${onPause}
        onResume=${onResume}
        onInject=${onInject}
        pendingInjections=${pendingInjections}
        setPendingInjections=${setPendingInjections}
        onAgentChange=${setSelectedAgent}
        onFilterChange=${setFilterEnabled}
      />
      <${PatternTimeline}
        records=${records}
        filterAgent=${selectedAgent}
        filterEnabled=${filterEnabled}
      />
    </div>
  `;
}

render(html`<${App}/>`, document.getElementById('app'));