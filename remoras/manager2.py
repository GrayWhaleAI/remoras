import requests
from requests.auth import HTTPBasicAuth


from uuid import uuid4
import json
import os
from typing import Union
from datetime import datetime

from .structs import BasicAuth, TokenConfig, ProjectConfig, FeedPayload
from .data_validation import validate_items, validate_policies
from .utils import load_obj_or_path

ENDPOINT = "https://app.productgenius.io"

class GWManager:
    def __init__(self,
        basic_auth:BasicAuth = None,
        project_config:ProjectConfig = None,
        token_config:TokenConfig = None,
        project_dir:str = "genius_project"
    ):
        assert (basic_auth and project_config) or token_config, "To manage a project you must pass either token_config, or (basic_auth, and project_config)"
        assert not (basic_auth and project_config and token_config), "Do not pass all three `basic_auth`, `token_config` and `project_config`. Either `token_config`, or (`basic_auth` and `project_config`)"

        self.basic_auth = basic_auth
        self.project_config = project_config
        self.token_config = token_config
        self.project_dir = project_dir

        self.project = ProjectManager(self)
        self.items = ItemManager(self)
        self.policies = PolicyManager(self)
        self.models = ModelManager(self)
        self.data = DataManager(self)

    @classmethod
    def from_token(self, token_config:TokenConfig):
        return GWManager(token_config=token_config)

    @classmethod
    def from_auth(self, basic_auth:BasicAuth, project_config:ProjectConfig):
        return GWManager(basic_auth=basic_auth, project_config=project_config)

     
    def save_token_config(self) -> None:
        """Save our token to the `project_dir` directory, if a `token_config` has not been set nothing will hapen"""
        os.makedirs(self.project_dir, exist_ok=True) # make our project dir if it does not exist
        assert self.token_config, "No token config to save"

        with open(f"{self.project_dir}/token.json", "w") as f:
            json.dump({"project_name": self.token_config.project_name, "token": self.token_config.token}, f, indent=2)

    # def build(self, items_or_path:Union[str, list], policies_or_path:Union[str, list]):
        

class ProjectManager:
    def __init__(self,
        manager: GWManager
    ):
        self.manager = manager

    def create(self):
        assert self.manager.basic_auth and self.manager.project_config, "Root manager needs to have BasicAuth and ProjectConfig to create a new project"
        auth = HTTPBasicAuth(username=self.manager.basic_auth.username, password=self.manager.basic_auth.password)
        r = requests.post(f"{ENDPOINT}/hackathon/project/create", auth=auth, json=self.manager.project_config.dict())
        r.raise_for_status()

        response = r.json()
        self.manager.token_config = TokenConfig(
            project_name=self.manager.project_config.project_name,
            token = response["access_token"]
        )

        self.manager.save_token_config()

    def update(self, update:dict):
        assert self.manager.token_config, "No token config set in the GWManager"
        r = requests.put(f"{ENDPOINT}/platform/project/{self.manager.token_config.project_name}", headers=self.manager.token_config.auth_header(), json=update)
        r.raise_for_status()

        return r.json()


class ItemManager:
    def __init__(
        self,
        manager: GWManager
    ):
        self.manager = manager

    def _get_endpoint(self):
        assert self.manager.token_config, "No token_config set in GWManager"
        return f"{ENDPOINT}/platform/project/{self.manager.token_config.project_name}/items"
    

    def add(self, items_or_path:Union[str, list]):
        items = load_obj_or_path(items_or_path)
        validate_items(items)

        r = requests.post(
            f"{self._get_endpoint()}/create",
            headers=self.manager.token_config.auth_header(),
            json=items
        )
        r.raise_for_status()

        return r.json()

    def get(self, item_id:str):
        r = requests.get(
            f"{self._get_endpoint()}/{item_id}",
            headers=self.manager.token_config.auth_header()
        )
        r.raise_for_status()
        return r.json()

    def list(self, params={"page": 1, "count": 10}):
        r = requests.get(
            f"{self._get_endpoint()}/list",
            headers=self.manager.token_config.auth_header(),
            params=params
        )
        r.raise_for_status()

        return r.json()

    def update(self, item_id:str, update:dict):
        validate_items([update])

        r = requests.put(
            f"{self._get_endpoint()}/{item_id}/update",
            headers=self.manager.token_config.auth_header(),
            json=update
        )
        r.raise_for_status()
        return r.json()

    def delete(self, item_id:str):
        r = requests.delete(
            f"{self._get_endpoint()}/{item_id}/delete",
            headers=self.manager.token_config.auth_header()
        )
        r.raise_for_status()
        return r.json()
    
        
class PolicyManager:
    def __init__(
        self,
        manager: GWManager
    ):
        self.manager = manager

    def _get_endpoint(self):
        assert self.manager.token_config, "No token_config in GWManager"
        return f"{ENDPOINT}/platform/{self.manager.token_config.project_name}/models/policies"

    def add(self, policies_or_path:Union[str, list]):
        policies = load_obj_or_path(policies_or_path)
        validate_policies(policies)

        r = requests.post(
            f"{self._get_endpoint()}",
            headers=self.manager.token_config.auth_header(),
            json=policies
        )
        r.raise_for_status()
        return r.json()

    def list(self):
        r = requests.get(
            f"{self._get_endpoint()}",
            headers=self.manager.token_config.auth_header()
        )
        r.raise_for_status()
        return r.json()
    
    def get(self, policy_id:str):
        r = requests.get(
            f"{self._get_endpoint()}/{policy_id}",
            headers=self.manager.token_config.auth_header()
        )
        r.raise_for_status()
        return r.json()

    def update(self, policy_id:str, update:dict):
        validate_policies([update])
        r = requests.put(
            f"{self._get_endpoint()}/{policy_id}",
            headers=self.manager.token_config.auth_header(),
            json=update
        )
        r.raise_for_status()
        return r.json()

    def delete(self, policy_id:str):
        r = requests.delete(
            f"{self._get_endpoint()}/{policy_id}",
            headers=self.manager.token_config.auth_header()
        )
        r.raise_for_status()
        return r.json()

    def enable(self, policy_id:str, enabled:bool):
        r = requests.put(
            f"{self._get_endpoint()}/{policy_id}/enable",
            headers=self.manager.token_config.auth_header(),
            json={"enabled": enabled}
        )
        r.raise_for_status()
        return r.json()
    
        
class ModelManager:
    def __init__(
        self,
        manager: GWManager
    ):
        self.manager = manager

    def _get_endpoint(self):
        assert self.manager.token_config, "No token_config set in GWManager"
        return f"{ENDPOINT}/platform/{self.manager.token_config.project_name}/models"

    def get(self, model_id:str):
        r = requests.get(
            f"{self._get_endpoint()}/{model_id}",
            headers=self.manager.token_config.auth_header()
        )

        r.raise_for_status()
        return r.json()

    def train(self, model_id:str=None):
        model = {"model_id": model_id} if model_id else {}
        r = requests.post(
            f"{self._get_endpoint()}/train",
            headers=self.manager.token_config.auth_header(),
            json=model
        )
        r.raise_for_status()

        return r.json()

    def activate(self, model_id:str):
        r = requests.post(
            f"{self._get_endpoint()}/{model_id}/activate",
            headers=self.manager.token_config.auth_header()
        )
        r.raise_for_status()

        return r.json()

    def list(self):
        assert self.manager.token_config, "No token_config in GWManager"
        endpoint = f"{ENDPOINT}/hackathon/{self.manager.token_config.project_name}/model/list"

        r = requests.get(
            endpoint,
            headers=self.manager.token_config.auth_header()
        )

        r.raise_for_status()
        return r.json()

class DataManager:
    def __init__(
        self,
        manager: GWManager
    ):
        self.manager = manager

    def _get_endpoint(self):
        assert self.manager.token_config, "No token_config in GWManager"
        return f"{ENDPOINT}/hackathon/{self.manager.token_config.project_name}"

    def feed(self, payload:FeedPayload, session_id=None):
        session_id = uuid4() if not session_id else session_id
        r = requests.post(
            f"{self._get_endpoint()}/feed/{session_id}",
            headers=self.manager.token_config.auth_header(),
            json=payload.dict()
        )
        r.raise_for_status()
        return r.json()
       

    def batch(self, payload:FeedPayload, session_id=None):
        session_id = uuid4() if not session_id else session_id
        r = requests.post(
            f"{self._get_endpoint()}/batch/{session_id}",
            headers=self.manager.token_config.auth_header(),
            json=payload.dict()
        )
        r.raise_for_status()
        return r.json()

    
    
        
