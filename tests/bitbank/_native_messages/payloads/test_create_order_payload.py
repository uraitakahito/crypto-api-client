"""CreateOrderPayload tests"""

from crypto_api_client.bitbank._native_messages.create_order_payload import (
    CreateOrderPayload,
)


def test_content_str_extracts_data_object():
    """Verify content_str correctly extracts "data" object"""
    json_str = '''
    "data": {
        "order_id": 12345678,
        "pair": "btc_jpy",
        "side": "buy",
        "type": "limit",
        "status": "UNFILLED",
        "price": "5000000",
        "amount": "0.001",
        "executed_amount": "0",
        "average_price": "0",
        "ordered_at": 1614556800000,
        "executed_at": null,
        "canceled_at": null,
        "trigger_price": null,
        "post_only": false
    }
    '''

    payload = CreateOrderPayload(json_str)
    content = payload.content_str

    # Verify content_str returns expected JSON string
    assert '"order_id"' in content
    assert '12345678' in content
    assert '"pair"' in content
    assert '"btc_jpy"' in content

    # Verify "data": is not included (only object part is extracted)
    assert '"data"' not in content


def test_content_str_preserves_structure():
    """Verify content_str preserves JSON structure"""
    json_str = '''
    "data": {
        "order_id": 12345678,
        "pair": "btc_jpy"
    }
    '''

    payload = CreateOrderPayload(json_str)
    content = payload.content_str

    # Verify it can be parsed as JSON object
    import json

    parsed = json.loads(content)

    assert parsed["order_id"] == 12345678
    assert parsed["pair"] == "btc_jpy"
