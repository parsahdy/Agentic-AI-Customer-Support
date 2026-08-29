from agent.tools.registry import ToolRegistry



def test_tool_schemas():

    registry = ToolRegistry()

    tools = registry.get_tools()

    for tool in tools:

        print(f"\nTool: {tool.name}")
        print(f"Description: {tool.description}")
        print(f"Schmas: {tool.args_schema}")

        if tool.args_schema:
            print(
                "Field:",
                tool.args_schema.model_fields
            )

    get_order = registry.create("get_order")

    assert get_order.args_schema is not None
    assert "order_id" in get_order.args_schema.model_fields


if __name__ == "__main__":
    test_tool_schemas()