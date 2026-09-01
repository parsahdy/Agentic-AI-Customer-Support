from agent.agent_service import AgentService


def session_isolation_test():

    agent = AgentService()

    
    agent.run(
        query="My order number is 1234.",
        user_id="user-1",
        session_id="session-1",
    )

    result = agent.run(
        query="What is my order number?",
        user_id="user_1",
        session_id="session-2"
    )

    return result
    
    
if __name__ == "__main__":
    print(session_isolation_test())
