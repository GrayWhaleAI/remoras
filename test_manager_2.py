from remoras import GWManager, BasicAuth, ProjectConfig, TokenConfig, FeedPayload, GeniusValidationError
import pytest
import requests
import os
import shutil

# Static Values
TEST_AUTH = BasicAuth(username="a", password="b")
TEST_PROJECT = ProjectConfig(project_name="test", project_summary="something", hacker_email="123@email.com")
TEST_TOKEN = TokenConfig(project_name="test", token="123456789")

TEST_ITEM = {"title": "a", "description": "b", "external_url": "c", "image_url": "d"}

# Pytest fixture set up
#
# Delete the auto-generated files
@pytest.fixture
def remove_project_dir():
    dir_path = os.path.join(os.path.dirname(__file__), 'genius_project/')

    yield
    
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        shutil.rmtree(dir_path)

# Mock requests library
class MockBaseResponse():
    @staticmethod
    def raise_for_status():
        return

class MockGetResponse(MockBaseResponse):
    @staticmethod
    def json():
        return ["1", "2", "3"]

class MockMirrorResponse(MockBaseResponse):
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload

class MockDeleteResponse(MockBaseResponse):
    @staticmethod
    def json():
        return True

class MockAuthToken(MockBaseResponse):
    @staticmethod
    def json():
        return {"access_token": "abc"}

@pytest.fixture
def mock_auth_response(monkeypatch):
    def mock_auth(*args, **kwargs):
        return MockAuthToken()

    def mock_put(*args, **kwargs):
        return MockMirrorResponse(kwargs["json"])

    monkeypatch.setattr(requests, "post", mock_auth)
    monkeypatch.setattr(requests, "put", mock_put)

@pytest.fixture
def mock_response(monkeypatch):

    def mock_get(*args, **kwargs):
        return MockGetResponse()

    def mock_post(*args, **kwargs):
        return MockMirrorResponse(kwargs["json"])

    def mock_delete(*args, **kwargs):
        return MockDeleteResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(requests, "post", mock_post)
    monkeypatch.setattr(requests, "put", mock_post)
    monkeypatch.setattr(requests, "delete", mock_delete)


def test_invalid_construction(remove_project_dir):
    with pytest.raises(AssertionError):
        GWManager(basic_auth=TEST_AUTH) # need both basic auth and project config
        GWManager(project_config=TEST_PROJECT)

        GWManager(basic_auth=TEST_AUTH, project_config=TEST_PROJECT, token_config=TEST_TOKEN) # should not pass all three

        GWManager() # fails because no configs

def test_valid_construction(remove_project_dir):
    manager = GWManager(basic_auth=TEST_AUTH, project_config=TEST_PROJECT)
    assert manager.project_config and manager.basic_auth, "Did not instantiate correctly with basic_auth and project_config"

    manager = GWManager(token_config=TEST_TOKEN)
    assert manager.token_config, "Did not instantiate correctly with token_config"

    manager = GWManager.from_auth(TEST_AUTH, TEST_PROJECT)
    assert manager.basic_auth and manager.project_config, "Did not instantiate with `from_auth` method"

    manager = GWManager.from_token(TEST_TOKEN)
    assert manager.token_config, "Did not instantiate with `from_token` method"


def test_project_manager(remove_project_dir, mock_auth_response):
    manager = GWManager.from_auth(TEST_AUTH, TEST_PROJECT)

    manager.project.create()

    assert manager.token_config and manager.token_config.token == "abc", "Unable to parse token_config and token from create call"

    response = manager.project.update({"project_name": "test"})
    assert response and response["project_name"] == "test", "Did not send update correctly"

def test_item_manager(mock_response):
    manager = GWManager.from_token(TEST_TOKEN)

    r = manager.items.add([TEST_ITEM])
    assert r and TEST_ITEM in r, "Test item not uploaded"

    r = manager.items.get("something")
    assert r and "1" in r, "Test item get not passed"

    r = manager.items.list()
    assert r and ["1", "2", "3"] == r, "Test item list not passed"

    r = manager.items.update("some_id", {"title": "b", "description": "c", "external_url": "d", "image_url": "a"})
    assert r and "description" in r, "Test item update not passed"

    r = manager.items.delete("some_id")
    assert r, "Test item delete not passed"

def test_policy_manager(mock_response):
    manager = GWManager.from_token(TEST_TOKEN)

    r = manager.policies.add([{"policy": "a"}])
    assert r and {"policy": "a"} in r, "Add policy not passed"

    r = manager.policies.get("some_id")
    assert r and "1" in r, "Get policy not passed"

    r = manager.policies.update("some_id", {"policy": "b"})
    assert r and "policy" in r, "Update policy not passed"

    r = manager.policies.delete("some_id")
    assert r, "Delete policy not passed"

    r = manager.policies.list()
    assert r and ["1", "2", "3"] == r, "List policies not passed"

    r = manager.policies.enable("some_id", True)
    assert r and r["enabled"], "Enable policy not passed"

def test_model_manager(mock_response):
    manager = GWManager.from_token(TEST_TOKEN)

    r = manager.models.list()
    assert r and ["1", "2", "3"] == r, "List models not passed"

    r = manager.models.get("some_id")
    assert r and "1" in r, "Get models not passed"

    r = manager.models.train({"model_id": "something"})
    assert r and "model_id" in r, "Train models not passed"
    
def test_data_manager(mock_response):
    manager = GWManager.from_token(TEST_TOKEN)

    r = manager.data.feed(FeedPayload())
    assert r and "search_prompt" in r, "Feed not passed"

    r = manager.data.batch(FeedPayload())
    assert r and "search_prompt" in r, "Batch not passed"
