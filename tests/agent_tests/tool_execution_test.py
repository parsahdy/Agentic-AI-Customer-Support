from agent.tools.registry import ToolRegistry



def test_get_order_tool():

    registry = ToolRegistry()

    tool = registry.create("get_order")

    state = {
        "query": "Where is my order?",
        "user_id": "user_1",
        "session_id": "session_1",
    }

    arguments = {
        "order_id": 123
    }

    result = tool.run(
        state=state,
        arguments=arguments
    )

    print("\nTool result:")
    print(result)


    assert result.success is True
    assert result.result["order_id"] == 123



if __name__ == "__main__":
    test_get_order_tool()