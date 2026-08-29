from agent.tools.registry import ToolRegistry


def test_registry_lists_tools():

    registry = ToolRegistry()

    tools = registry.get_tools()

    print("\nRegistered tools:")

    for tool in tools:
        print(
            f"- {tool.name}: {tool.description}"
        )

    assert len(tools) == 5


if __name__ == "__main__":
    test_registry_lists_tools()
