from unittest.mock import MagicMock
from langchain_core.messages import AIMessage, ToolMessage
from agent.state import InvestigationState
from agent.controller import AgentController


def test_investigation_state_duplicate_prevention():
    state = InvestigationState("How does X work?")
    tool_name = "find_symbol"
    tool_args = {"name": "Flask"}

    assert not state.is_duplicate_tool_call(tool_name, tool_args)
    state.record_tool_call(tool_name, tool_args, [{"name": "Flask"}])

    assert state.is_duplicate_tool_call(tool_name, tool_args)
    assert state.tool_call_count == 1
    assert len(state.discovered_symbols) == 1
    assert "Flask" in state.discovered_symbols


def test_agent_controller_max_iterations_limit():
    mock_llm = MagicMock()
    # LLM keeps calling tool indefinitely
    mock_response = AIMessage(
        content="",
        tool_calls=[{"name": "mock_tool", "args": {"q": "search"}, "id": "call_1"}]
    )
    mock_llm.bind_tools.return_value.invoke.return_value = mock_response

    mock_tool = MagicMock(return_value={"result": "data"})
    tools_dict = {"mock_tool": mock_tool}

    controller = AgentController(
        llm=mock_llm,
        tools_dict=tools_dict,
        max_iterations=3,
        max_tool_calls=5
    )

    result = controller.run_investigation("Test question")
    assert result["status"] == "limit_reached"
    assert result["state"]["iterations"] == 3


def test_agent_controller_duplicate_tool_call_handled():
    mock_llm = MagicMock()
    # LLM requests exact same tool call twice
    resp1 = AIMessage(content="", tool_calls=[{"name": "dummy", "args": {"a": 1}, "id": "1"}])
    resp2 = AIMessage(content="", tool_calls=[{"name": "dummy", "args": {"a": 1}, "id": "2"}])
    resp3 = AIMessage(content="Final grounded answer.", tool_calls=[])

    mock_llm.bind_tools.return_value.invoke.side_effect = [resp1, resp2, resp3]

    mock_func = MagicMock(return_value={"data": 123})
    controller = AgentController(llm=mock_llm, tools_dict={"dummy": mock_func})

    result = controller.run_investigation("Question")
    assert result["status"] == "completed"
    assert result["answer"] == "Final grounded answer."
    # The tool should only be executed once despite being called twice
    assert mock_func.call_count == 1


def test_agent_controller_handles_429_quota_error():
    mock_llm = MagicMock()
    quota_err = Exception("429 RESOURCE_EXHAUSTED Quota exceeded")
    mock_llm.invoke.side_effect = quota_err
    mock_llm.bind_tools.return_value.invoke.side_effect = quota_err

    controller = AgentController(llm=mock_llm, tools_dict={})
    result = controller.run_investigation("Question")

    assert result["status"] == "quota_exhausted"
    assert "Gemini LLM quota exhausted" in result["error"]

