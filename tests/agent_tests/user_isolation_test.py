from agent.agent_service import AgentService


def user_isolation_test():

    agent = AgentService()

    
    agent.run(
        query="My order number is 1234.",
        user_id="user-1",
        session_id="session-1",
    )

    result = agent.run(
        query="What is my order number?",
        user_id="user_2",
        session_id="session-1"
    )

    return result
    
    
if __name__ == "__main__":
    print(user_isolation_test())
