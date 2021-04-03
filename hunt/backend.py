from django.conf import settings
from storages.backends.azure_storage import AzureStorage


class AzureMediaStorage(AzureStorage):
    account_name = settings.AZURE_ACCOUNT_NAME
    account_key = settings.AZURE_ACCOUNT_KEY
    azure_container = settings.AZURE_MEDIA_CONTAINER
    expiration_secs = 900


class AzureStaticStorage(AzureStorage):
    account_name = settings.AZURE_ACCOUNT_NAME
    account_key = settings.AZURE_ACCOUNT_KEY
    azure_container = settings.AZURE_STATIC_CONTAINER
    overwrite_files = True
