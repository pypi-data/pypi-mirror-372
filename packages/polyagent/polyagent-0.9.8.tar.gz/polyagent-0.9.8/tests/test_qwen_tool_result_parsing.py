import polycli
agent = polycli.PolyAgent()
agent.load_state("tests/test_data/toolresultbug.jsonl")
print(agent.messages.to_format("standard"))
