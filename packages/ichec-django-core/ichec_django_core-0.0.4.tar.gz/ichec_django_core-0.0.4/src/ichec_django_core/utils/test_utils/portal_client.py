import logging

from .rest_client import RestClient
from .models import get_path_from_item, get_path_from_type, Resource

logger = logging.getLogger(__name__)


class PortalClient(RestClient):
    def create_user(self, data: dict) -> dict:
        return self.post("users", data)

    def get_items(self, item_t) -> list:
        ret_json = self.get(get_path_from_type(item_t))
        if ret_json:
            return [item_t(**item) for item in ret_json]
        return []

    def create_item(self, resource: Resource) -> dict:
        return self.post(get_path_from_item(resource), dict(resource))

    def delete_item(self, resource: Resource):
        self.delete(f"{get_path_from_item(resource)}/{resource.id}/")
