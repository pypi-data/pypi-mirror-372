import pytest

from snakestack.config import SnakeStackSettings

pytestmark = [
    pytest.mark.unit,
    pytest.mark.config,
    pytest.mark.asyncio
]

class TestConfig:

    async def test_should_raise_value_error_when_receive_invalid_filters(
        self,
        faker
    ):
        with pytest.raises(ValueError, match="Invalid filter"):
            SnakeStackSettings(snakestack_log_default_filters=faker.uuid4())

    async def test_should_raise_value_error_when_receive_invalid_formatter(
        self,
        faker
    ):
        with pytest.raises(ValueError, match="Invalid formatter"):
            SnakeStackSettings(snakestack_log_default_formatter=faker.uuid4())

    async def test_should_raise_value_error_when_receive_invalid_excluded_name(
        self
    ):
        with pytest.raises(TypeError, match="Invalid excluded name filter"):
            SnakeStackSettings(snakestack_log_filter_excluded_name=True)

    async def test_should_return_settings_when_receive_valid_filter(
        self
    ):
        for value in ["request_id", "excluded_name"]:
            result = SnakeStackSettings(snakestack_log_default_filters=value)
            assert result.snakestack_log_default_filters == value

    async def test_should_return_settings_when_receive_valid_formatter(
        self
    ):
        for value in ["default", "custom_json", "with_request_id"]:
            result = SnakeStackSettings(snakestack_log_default_formatter=value)
            assert result.snakestack_log_default_formatter == value

    async def test_should_return_settings_when_receive_valid_excluded_name_filter(
        self
    ):
        result = SnakeStackSettings(snakestack_log_filter_excluded_name="a, b")
        assert isinstance(result.snakestack_log_filter_excluded_name, list)
        assert result.snakestack_log_filter_excluded_name == ["a", "b"]
