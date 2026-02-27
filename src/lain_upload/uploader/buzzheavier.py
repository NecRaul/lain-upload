from .base import BaseUploader


class BuzzheavierUploader(BaseUploader):
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_max_size = 100 * 1000 * 1000 * 1000
        self.file_max_size_str = "100GB"
        self.http_method = "PUT"
        self.api_endpoint = f"https://w.buzzheavier.com/{file_path.name}"

    def _build_fields(self, file_name, file):
        return {"file": (file_name, file)}

    @staticmethod
    def _extract_url(response):
        return f"https://buzzheavier.com/{response.json()['data']['id']}"
