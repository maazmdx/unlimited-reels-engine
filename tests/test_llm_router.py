import json
from engine.llm_router import _extract_json_text


def test_extract_json_text_direct_json():
    raw = '{"key": "value", "count": 42}'
    extracted = _extract_json_text(raw)
    assert json.loads(extracted) == {"key": "value", "count": 42}


def test_extract_json_text_markdown_wrapped():
    raw = 'Here is the result:\n```json\n{"action": "test", "valid": true}\n```\nHope that helps!'
    extracted = _extract_json_text(raw)
    assert json.loads(extracted) == {"action": "test", "valid": True}


def test_extract_json_text_chatter_wrapped():
    raw = 'The requested output is {"dialogue": [{"speaker": "dad", "text": "hello"}]}. Thank you.'
    extracted = _extract_json_text(raw)
    parsed = json.loads(extracted)
    assert "dialogue" in parsed
    assert parsed["dialogue"][0]["speaker"] == "dad"
