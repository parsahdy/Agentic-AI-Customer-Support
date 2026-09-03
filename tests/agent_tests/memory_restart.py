import sys

from agent.agent_service import AgentService


class RestartTest:

    @staticmethod
    def first_test():
        print("=== FIRST RUN ===")

        agent = AgentService()

        result = agent.run(
            query="My order number is 1234, remember that.",
            user_id="user-1",
            session_id="session-1",
        )

        print("First run completed.")
        print("Result:")
        print(result)

        agent.close()

    @staticmethod
    def second_test():
        print("=== SECOND RUN ===")

        agent = AgentService()

        result = agent.run(
            query="What was my order number?",
            user_id="user-1",
            session_id="session-2",
        )

        print("Second run completed.")
        print("Result:")
        print(result)

        agent.close()


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:")
        print("  python -m tests.agent_tests.memory_restart first")
        print("  python -m tests.agent_tests.memory_restart second")
        sys.exit(1)

    test_type = sys.argv[1].lower()

    if test_type == "first":
        RestartTest.first_test()

    elif test_type == "second":
        RestartTest.second_test()

    else:
        print("Invalid test type.")
        print("Use: first or second")
        sys.exit(1)