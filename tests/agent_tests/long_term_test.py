from agent.agent_service import AgentService


def long_term_memory():

    agent = AgentService()

    agent.run(
        query="Remember that I prefer email.",
        user_id="user-1",
        session_id="session-1",
    )

    result = agent.run(
        query="How should you contact me?.",
        user_id="user-1",
        session_id="session-2",
    )

    return result


if __name__ == "__main__":
    print(long_term_memory())