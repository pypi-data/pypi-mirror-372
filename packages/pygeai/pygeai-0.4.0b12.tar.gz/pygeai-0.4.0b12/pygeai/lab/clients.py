from pygeai import logger
from pygeai.admin.clients import AdminClient
from pygeai.core.base.clients import BaseClient
from pygeai.core.common.exceptions import APIError


class AILabClient(BaseClient):

    def __init__(self, api_key: str = None, base_url: str = None, alias: str = None, project_id: str = None):
        super().__init__(api_key, base_url, alias)
        self.project_id = project_id if project_id else self.__get_project_id()

    def __get_project_id(self):
        response = None
        try:
            response = AdminClient().validate_api_token()
            return response.get("projectId")
        except Exception as e:
            logger.error(f"Error retrieving project_id from GEAI. Response: {response}: {e}")
            raise APIError(f"Error retrieving project_id from GEAI: {e}")