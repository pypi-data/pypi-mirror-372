from agents.schemas import parse_agent_reply


def test_parse_tool():
    a = parse_agent_reply("TOOL:http_get:https://example.com")
    assert a.kind == "tool"
    assert a.tool_name == "http_get"
    assert a.tool_argument.startswith("https://")


def test_parse_respond():
    a = parse_agent_reply("RESPOND:Hello world")
    assert a.kind == "respond"
    assert a.content == "Hello world"


def test_parse_fallback():
    a = parse_agent_reply("Just answer plainly")
    assert a.kind == "respond"
    assert a.content == "Just answer plainly"
