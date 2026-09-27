import pytest
from app.agent.tools import tool_calculator, tool_mock_database_lookup, tool_controlled_doc_search
from app.agent.graph import build_langgraph_agent

def test_calculator_tool_valid_math():
    res = tool_calculator("100 + 25 * 4")
    assert res["success"] is True
    assert res["result"] == 200

def test_calculator_tool_rejects_unsafe_code():
    res = tool_calculator("__import__('os').system('ls')")
    assert res["success"] is False
    assert "error" in res

def test_database_lookup_tool_normal_query():
    res = tool_mock_database_lookup("orders", "1001", is_secured=True)
    assert res["success"] is True
    assert res["record"]["order_id"] == "1001"
    assert res["record"]["customer"] == "John Doe"

def test_database_lookup_tool_blocks_sql_injection():
    res = tool_mock_database_lookup("orders", "1001; DROP TABLE customers; --", is_secured=True)
    assert res["success"] is False
    assert res["blocked"] is True
    assert res["threat"] == "SQL_INJECTION"

def test_controlled_doc_search_tool():
    res = tool_controlled_doc_search("return policy")
    assert res["success"] is True
    assert "30 days" in res["content"]

def test_langgraph_workflow_compiles():
    agent = build_langgraph_agent()
    assert agent is not None
