import pytest
from smsn_telegram_notify import TelegramNotify
from unittest.mock import patch, Mock


def test_should_send_respects_interval():
    notifier = TelegramNotify(token="t", chat_id="c")
    with patch('smsn_telegram_notify.notify.time.time', side_effect=[10, 12, 18]):
        assert notifier._should_send('text') is True
        assert notifier._should_send('text') is False
        assert notifier._should_send('text') is True


def test_safe_telegram_post_success():
    notifier = TelegramNotify(token="t", chat_id="c")
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"ok": True}
    notifier.session.post = Mock(return_value=mock_response)
    assert notifier._safe_telegram_post("https://example.com", data={"chat_id": "c"}) is True


def test_safe_telegram_post_http_error():
    notifier = TelegramNotify(token="t", chat_id="c")
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "error"
    notifier.session.post = Mock(return_value=mock_response)
    assert notifier._safe_telegram_post("https://example.com") is False
