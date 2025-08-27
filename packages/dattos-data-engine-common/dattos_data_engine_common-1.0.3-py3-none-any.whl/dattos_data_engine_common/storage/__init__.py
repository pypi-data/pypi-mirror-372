from .models import StorageConfig, StorageProvider
from .base import StorageStrategy
from .azure_strategy import AzureStorageStrategy
from .aws_strategy import AwsStorageStrategy


class StorageProviderFactory:
    @staticmethod
    def create_storage_strategy(storage_config: StorageConfig) -> StorageStrategy:
        if storage_config.provider == StorageProvider.AZURE:
            return AzureStorageStrategy(storage_config.connection_string)
        elif storage_config.provider == StorageProvider.AWS:
            return AwsStorageStrategy(storage_config.connection_string)
        else:
            raise ValueError(
                f"Provedor de armazenamento não suportado: {storage_config.provider}"
            )
