import requests
from uuid import uuid4
import json
from requests.auth import HTTPBasicAuth
import os
from typing import Union
from .structs import BasicAuth, TokenConfig, ProjectConfig, FeedPayload
from .data_validation import validate_items, validate_instructions
from datetime import datetime

# Normal endpoint for these operations. If this changes just update this field
ENDPOINT = "https://app.productgenius.io/hackathon"

class GeniusManager:
    """GeniusManager handles new and old genius projects.

        Constructor Args:
            - `basic_auth`: Using the BasicAuth class you can pass provided `username` and `password` for new project creation. If this arg is specified `project_config` must also be specified
            - `project_config`: Using the ProjectConfig class pass in `hacker_email`, `project_name`, and `project_summary` for project creation. Must be used in conjunction with `basic_auth`
            - `token_config`: Using the TokenConfig class pass in your `token` and `project_name` to utilize an existing project
            - `project_dir`: A directory to save tokens and other project info to. 
    """    
    def __init__(self,
        basic_auth:BasicAuth = None,
        token_config:TokenConfig = None,
        project_config:ProjectConfig = None,
        project_dir:str = "genius_project"
    ):

        assert (basic_auth and project_config) or token_config, "To manage a project you must pass either token_config, or (basic_auth, and project_config)"
        assert not (basic_auth and project_config and token_config), "Do not pass all three `basic_auth`, `token_config` and `project_config`. Either `token_config`, or (`basic_auth` and `project_config`)"

        self.basic_auth = basic_auth
        self.project_config = project_config
        self.token_config = token_config
        self.project_dir = project_dir

        os.makedirs(self.project_dir, exist_ok=True) # make our project dir if it does not exist

    @classmethod
    def from_token_config(self, token_config:TokenConfig):
        """Create a manager from a TokenConfig

        Arg:
            token_config: TokenConfig

        Examples:

        1. manager = GeniusManager.from_token_config(TokenConfig(token="sometokenhere", project_name="myproject"))
        2. manager = GeniusManager.from_token_config(TokenConfig.load_from_file("my_token.json"))
        """
        return GeniusManager(token_config=token_config)

    @classmethod
    def from_auth_config(self, basic_auth:BasicAuth, project_config:ProjectConfig):
        """Create a manager from a BasicAuth and ProjectConfig

        Arg:
            basic_auth: BasicAuth
            project_config: ProjectConfig

        Examples:

        1. manager = GeniusManager.from_auth_config(BasicAuth(username="username_here", password="my_password"), ProjectConfig(project_name="my_project", project_summary="summary", hacker_email="myemail@me.com"))
        2. manager = GeniusManager.from_auth_config(BasicAuth.load_from_file("auth.json"), ProjectConfig.load_from_file("project.json"))
        """
        return GeniusManager(basic_auth=basic_auth, project_config=project_config)        

    def save_token_config(self) -> None:
        """Save our token to the `project_dir` directory, if a `token_config` has not been set nothing will hapen"""
        assert self.token_config, "No token config to save"

        with open(f"{self.project_dir}/token.json", "w") as f:
            json.dump({"project_name": self.token_config.project_name, "token": self.token_config.token}, f, indent=2)
        
               
    def _make_token_header(self) -> dict:
        """Simple header creation function"""
        assert self.token_config, "No token config to make headers with."

        return {"Authorization": f"Bearer {self.token_config.token}"}
    
    
    def make_project(self) -> None:
        """Create a new genius project. This requires the class to have `basic_auth` and `project_config` set before running.
            If those variables are not set an AssertionError will be thrown. If the request does not completet
            an HTTPError will be thrown.

            This function will also generate a token 
        """
        # Create an HTTPBasicAuth object to handle initial communication to API
        assert self.basic_auth and self.project_config, "BasicAuth and ProjectConfig not set. Try setting these before making a new project"
        basic = HTTPBasicAuth(self.basic_auth.username, self.basic_auth.password)

        # Send create request and throw an error if http does not connect
        r = requests.post(f"{ENDPOINT}/project/create", json=self.project_config.__dir__(), auth=basic)
        r.raise_for_status()

        # Get our created token out, create a TokenConfig class that we store into `token_config`
        response_json = r.json()
        self.token_config = TokenConfig(project_name=self.project_config.project_name, token=response_json["access_token"])

        # Save our created token to `project_dir`
        self.save_token_config()
        
    def _load_obj_or_path(self, obj):
        
        if type(obj) is str:
            assert os.path.exists(obj), f"Unable to find specified file at {obj}"

            with open(obj, 'r') as f:
                objs = json.loads(f.read())
        else: # we have a list
            objs = obj

        return objs

    def upload_items(self, items_or_path:Union[str, list]) -> None:
        """Upload Genius items to the backend. Ensure you are using the proper format otherwise an HTTPError will be thrown

            Args:
                - `items_or_path`: Send either a list of genius items or a path to a json file containing genius items                
        """

        # We have a file path so load the json first and set items to the loaded data
        items = self._load_obj_or_path(items_or_path)
        # items could not be loaded so throw an AssertionError
        assert items, "Items could not be loaded, or were not passed"

        validate_items(items) # An assertion error will be thrown if we are unable to validate item sturcture

        # send items to backend
        assert self.token_config, "token_config not set unable to manage items"
        r = requests.post(f"{ENDPOINT}/project/{self.token_config.project_name}/items/create", json=items, headers=self._make_token_header())
        r.raise_for_status()
        
    def upload_instructions(self, instructions_or_path:Union[str, list]) -> None:
        """Upload instructions / prompts to the genius model

            Args:
                - `instructions_or_path`: Can be either a string or a list, its type will determine how it is interpreted
                    if str -> treat like a filepath and load the items
                    if list -> treat as raw items 
        """
        # check if we have a filepath, if so load the file with json
        instructions = self._load_obj_or_path(instructions_or_path)
        assert instructions, "Instructions could not be loaded"
        validate_instructions(instructions) # An assertion error will be thrown if we are unable to validate instruction structure
        # make request to upload
        assert self.token_config, "token_config not set unable to manage instructions"
        r = requests.post(f"{ENDPOINT}/{self.token_config.project_name}/model/instruction/create", json=instructions, headers=self._make_token_header())
        r.raise_for_status()


    def list_instructions(self):
        """List all available instructions"""
        assert self.token_config, "No token config"
        r = requests.get(f"{ENDPOINT}/{self.token_config.project_name}/model/instruction/list", headers=self._make_token_header())
        r.raise_for_status()

        return r.json()

    def update_instruction(self, promptlet_id:str, promptlet:dict):
        assert self.token_confg, "No token config"
        r = requests.put(f"{ENDPOINT}/{self.token_config.project_name}/model/instruction/{promptlet_id}/update", json=promptlet, headers=self._make_token_header())
        r.raise_for_status()

    def delete_instruction(self, promptlet_id:str):
        assert self.token_config, "No token config"
        r = requests.delete(f"{ENDPOINT}/{self.token_config.project_name}/model/instruction/{promptlet_id}/delete", headers=self._make_token_header())
        r.raise_for_status()

    
    # @TODO: When product genius updates the ai generated prompt to have a identifier this should be updated
    def remove_ai_generated_instruction(self) -> bool:
        """Remove the AI generated instruction (Call this after creating more than 10 items)
        if called after uploading instructions behavior is undefined and you might lose your created
        instructions
        """
        # Check for required token config
        instructions = self.list_instructions()

        # ensure we have something to delete
        if len(instructions) > 0:
            ai_instruction = instructions[0]
            self.delete_instruction(ai_instruction["id"])
            return True

        return False
           
    
    def create_model(self):
        """Simple model creation"""
        # Assert that we have a token config to use
        assert self.token_config, "token_config must be set before creating a model"

        r = requests.post(f"{ENDPOINT}/{self.token_config.project_name}/model/create", headers=self._make_token_header())
        r.raise_for_status()
        

    def create_project(self, items_or_path:Union[str, list], instructions_or_path:Union[str, list], remove_ai_instruction=False):
        """Full end to end creation of model"""

        #Call Validation methods before starting
        validate_items(self._load_obj_or_path(items_or_path))
        validate_instructions(self._load_obj_or_path(instructions_or_path))

        
        # Make the project 
        print("Making Project")
        self.make_project()

        # Upload the items
        print("Uploading Items")
        self.upload_items(items_or_path)

        # If remove_ai_instruction flag is present, remove the AI generated prompt before we add instructions
        if remove_ai_instruction:
            print("Removing AI Prompt")
            self.remove_ai_generated_instruction()

        # Upload our instructions
        print("Uploading Instructions")
        self.upload_instructions(instructions_or_path)

        # Initiate training of the model
        print("Training Model")
        self.create_model()

    
    def list_items(self, page=1, count=10) -> list:
        """List items that have been uploaded"""
        assert self.token_config, "No token config in use"

        r = requests.get(f"{ENDPOINT}/project/{self.token_config.project_name}/items/list", params={"page": page, "count": count}, headers=self._make_token_header())
        r.raise_for_status()

        return r.json()
    
    def get_item(self, item_id:str) -> dict:
        """Get a single item from an item_id"""
        assert self.token_config, "No token config in use"

        r = requests.get(f"{ENDPOINT}/project/{self.token_config.project_name}/items/{item_id}", headers=self._make_token_header())
        r.raise_for_status()

        return r.json()

    def update_item(self, item_id:str, updated_item:dict):
        assert self.token_config, "No token config"

        metadata = updated_item.get('metadata', []) # Thanks Cheldawg. Filters out the `available` metadata which was causing errors on upload
        updated_item['metadata'] = [meta for meta in metadata if meta.get('name') != 'available']
        
        r = requests.put(f"{ENDPOINT}/project/{self.token_config.project_name}/items/{item_id}/update", json=updated_item, headers=self._make_token_header())
        r.raise_for_status()

        return r.json()

    def delete_item(self, item_id:str):
        assert self.token_config, "No token config"

        r = requests.delete(f"{ENDPOINT}/project/{self.token_config.project_name}/items/{item_id}/delete", headers=self._make_token_header())
        r.raise_for_status()
    
    
    

    def batch(self, session_id:str=None, payload:FeedPayload = FeedPayload()) -> list:
        """Call the batch endpoint utilizing a session_id and a payload

            Args:
                - `session_id`: If not passed will utilize a uuid4() string
                - `payload`: Default payload can be seen in the FeedPayload constructor
        """
        assert self.token_config, "No token config in use"

        # set a random session id if one is not provided
        session_id = uuid4() if not session_id else session_id

        r = requests.post(f"{ENDPOINT}/{self.token_config.project_name}/batch/{session_id}", json=payload.dict(), headers=self._make_token_header())
        r.raise_for_status()

        return r.json()

    def batch_to_items(self, session_id:str=None, payload:FeedPayload = FeedPayload())->list:
        """Wrapper call for `batch` that will convert item_ids into actual items via `get_item`"""
        batch_items = self.batch(session_id, payload)

        items = [self.get_item(item_id) for item_id in batch_items]

        return items
        

    def list_models(self):
        """List available models"""
        assert self.token_config, "No token config in use"

        r = requests.get(f"{ENDPOINT}/{self.token_config.project_name}/model/list", headers=self._make_token_header())
        r.raise_for_status()

        return r.json()

    def promote_most_recent_model(self):
        """Utilizing the list_models function determine the most recently created / trained model and promote it"""
        # Call our list models method to return all models
        models = self.list_models()

        # Convert the time string into a float, then grab the biggest number
        models = [{"iso_time": datetime.fromisoformat(model["created_at"]), **model} for model in models]
        most_recent = max(models, key=lambda model: model["iso_time"])

        self.promote_model(most_recent["id"])


    def promote_model(self, model_id:str):
        # Call the promotion endpoint using the most_recent id
        r = requests.post(f"{ENDPOINT}/{self.token_config.project_name}/model/{model_id}/promote", headers=self._make_token_header())
        r.raise_for_status()
        
