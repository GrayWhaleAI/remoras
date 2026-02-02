from dataclasses import dataclass, field
import os
import json


# Named dict for HTTPBasicAuth requirements
@dataclass
class BasicAuth:
    username:str
    password:str

    @classmethod
    def load_from_file(self, path:str):
        assert os.path.exists(path), "File path does not exist"

        with open(path, 'r') as f:
            auth = json.loads(f.read())

        assert auth.get("username") and auth.get("password"), "Fields `username` and `password` were not found. Ensure both are present in your auth json file!"

        return BasicAuth(username=auth.get("username"), password=auth.get("password"))

    def __dir__(self):
        return {"username": self.username, "password": self.password}

# Named dict for project management via a token
@dataclass
class TokenConfig:
    token:str
    project_name:str

    @classmethod
    def load_from_file(self, path:str):
        assert os.path.exists(path), "File path does not exist"

        with open(path, 'r') as f:
            token = json.loads(f.read())

        assert token.get("project_name") and token.get("token"), "Fields `project_name` and `token` were not found. Ensure both are present in your token json file!"

        return TokenConfig(project_name=token.get("project_name"), token=token.get("token"))

    def __dir__(self):
        return {"project_name": self.project_name, "token": self.token}

# Named dict for new project requirements
@dataclass
class ProjectConfig:
    hacker_email:str
    project_name:str
    project_summary:str
    
    @classmethod
    def load_from_file(self, path:str):
        assert os.path.exists(path), "File path does not exist"

        with open(path, 'r') as f:
            project = json.loads(f.read())

        assert project.get("project_name") and project.get("project_summary") and project.get("hacker_email"), "Fields `project_name` and `project_summary` and `hacker_email` were not found. Ensure both are present in your project json file!"

        return ProjectConfig(project_name=project.get("project_name"), project_summary=project.get("project_summary"), hacker_email=project.get("hacker_email"))

    def __dir__(self): #old way of doing this (recently learned about the vars(self) trick)
        return {"project_name": self.project_name, "project_summary": self.project_summary, "hacker_email": self.hacker_email}

    def dict(self):
        return vars(self)

# Named dict for Feed/Batch endpoint payloads
@dataclass
class FeedPayload:
    page:int = 1 
    batch_count:int = 10
    events: list[dict] = field(default_factory=list)
    search_prompt: str = ""

    def dict(self):
        return vars(self)



