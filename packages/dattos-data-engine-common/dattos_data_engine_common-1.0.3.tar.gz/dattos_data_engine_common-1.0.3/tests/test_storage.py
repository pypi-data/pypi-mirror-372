import unittest
from unittest.mock import patch, Mock
from src.dattos_data_engine_common.storage import (
    StorageProviderFactory,
    AzureStorageStrategy,
)


class TestStorageProviderFactory(unittest.TestCase):
    @patch("src.storage.AzureStorageStrategy")
    def test_get_storage_provider_azure(self, mock_azure_strategy):
        mock_azure_strategy_instance = Mock()
        mock_azure_strategy.return_value = mock_azure_strategy_instance

        storage_config = Mock(
            provider="Azure", connection_string="dummy_connection_string"
        )
        storage_strategy = StorageProviderFactory.get_storage_provider(storage_config)

        assert isinstance(storage_strategy, AzureStorageStrategy)
        assert storage_strategy == mock_azure_strategy_instance


if __name__ == "__main__":
    unittest.main()
