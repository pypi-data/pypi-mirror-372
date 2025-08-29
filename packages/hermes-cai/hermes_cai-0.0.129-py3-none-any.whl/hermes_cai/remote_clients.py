from google.cloud import storage


class GCSClient:
    _gcs_client = None

    @classmethod
    def get_client(cls):
        if cls._gcs_client is None:
            cls._gcs_client = storage.Client()
        return cls._gcs_client
