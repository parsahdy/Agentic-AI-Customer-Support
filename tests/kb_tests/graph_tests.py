from agent.graph import build_graph


graph = build_graph()

state = {
    "messages": [],
    "user_id": "user-1",
    "session_id": "session-1",
    "query": "What is the status of order 123?",
    "retrieved_documents": [],
    "tool_calls": [],
    "tool_results": [],
    "iteration": 0,
    "max_iteration": 5,
    "final_answer": "",
    "error": None,
    "metadata": {},
    "route": None,
}

result = graph.invoke(state)

print(result["final_answer"])
print(result["tool_results"])
print(result["iteration"])