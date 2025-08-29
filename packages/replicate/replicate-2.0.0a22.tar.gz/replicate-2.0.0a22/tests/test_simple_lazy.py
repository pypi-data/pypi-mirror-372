"""Test lazy client creation in replicate.use()."""

import os
import sys
from unittest.mock import MagicMock, patch


def test_use_does_not_raise_without_token():
    """Test that replicate.use() works even when no API token is available."""
    sys.path.insert(0, "src")

    with patch.dict(os.environ, {}, clear=True):
        with patch.dict(sys.modules, {"cog": None}):
            import replicate

            # Should not raise an exception
            model = replicate.use("test/model")  # type: ignore[misc]
            assert model is not None


def test_cog_current_scope():
    """Test that cog.current_scope().context is read on each client creation."""
    sys.path.insert(0, "src")

    mock_context = MagicMock()
    mock_context.items.return_value = [("REPLICATE_API_TOKEN", "test-token-1")]

    mock_scope = MagicMock()
    mock_scope.context = mock_context

    mock_cog = MagicMock()
    mock_cog.current_scope.return_value = mock_scope

    with patch.dict(os.environ, {}, clear=True):
        with patch.dict(sys.modules, {"cog": mock_cog}):
            import replicate

            model = replicate.use("test/model")  # type: ignore[misc]

            # Access the client property - this should trigger client creation and cog.current_scope call
            _ = model._client

            assert mock_cog.current_scope.call_count == 1

            # Change the token and access client again - should trigger another call
            mock_context.items.return_value = [("REPLICATE_API_TOKEN", "test-token-2")]

            # Create a new model to trigger another client creation
            model2 = replicate.use("test/model2")  # type: ignore[misc]
            _ = model2._client

            assert mock_cog.current_scope.call_count == 2
