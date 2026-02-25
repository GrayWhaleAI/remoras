from remoras import GeniusManager, BasicAuth, ProjectConfig, TokenConfig, FeedPayload, GeniusValidationError
import pytest
import requests
import os


TEST_AUTH = BasicAuth(username="a", password="b")
TEST_PROJECT = ProjectConfig(project_name="test", project_summary="something", hacker_email="123@email.com")
TEST_TOKEN = TokenConfig(project_name="test", token="123456789")

@pytest.fixture
def remove_project_dir():
    dir_path = os.path.join(os.path.dirname(__file__), 'genius_project/')
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        os.removedirs(dir_path)
        
def test_manager_construction_assertions(remove_project_dir):
    """Check basic construction assertions
    1. Exception for no args,
    2. Exception for only passing BasicAuth
    3. Exception for only passing ProjectConfig
    4. Exception for passing all 3 BasicAuth, ProjectConfig, and TokenConfig
    """
    with pytest.raises(AssertionError):
        manager = GeniusManager() # should raise an exception because no configs are sent
    
        manager = GeniusManager(basic_auth=TEST_AUTH) #should raise an exception because we need project_config as well

        manager = GeniusManager(project_config=TEST_PROJECT) # Exception for not providing auth

        manager = GeniusManager(token_config=TEST_TOKEN, basic_auth=TEST_AUTH, project_config=TEST_PROJECT) # Should fail because we provide all three

def test_manager_construction_from_methods(remove_project_dir):
    """Check to ensure the GeniusManager.from_token_config(TokenConfig) and GeniusManager_from_auth_config(BasicAuth, ProjectConfig) methods work"""

    manager = GeniusManager.from_token_config(TEST_TOKEN)
    assert manager.token_config

    manager = GeniusManager.from_auth_config(TEST_AUTH, TEST_PROJECT)
    assert manager.basic_auth and manager.project_config


def test_manager_construction(remove_project_dir):
    """Test valid constructions
    1. BasicAuth and ProjectConfig,
    2. TokenConfig,
    3. The `from_token_config` function
    4. The `from_auth_config` function
    """
    # Basic auth and Project Conf construction
    manager = GeniusManager(basic_auth=TEST_AUTH, project_config=TEST_PROJECT)
    assert manager.token_config is None, "Got a Token Config when we should not have"

    # TokenConfig construction
    manager = GeniusManager(token_config=TEST_TOKEN)
    assert manager.basic_auth is None and manager.project_config is None

    manager = GeniusManager.from_token_config(TEST_TOKEN)
    assert manager.token_config

    manager = GeniusManager.from_auth_config(TEST_AUTH, TEST_PROJECT)
    assert manager.basic_auth and manager.project_config

# PyTest Fixture class
class MockMirrorResponse():
    def __init__(self, payload):
        self.payload = payload

    def json(self):
        return self.payload

    @staticmethod
    def raise_for_status():
        return
        

class MockItemResponse():
    @staticmethod
    def json():
        return ["1", "2", "3"]

    @staticmethod
    def raise_for_status():
        return None


@pytest.fixture
def mock_response(monkeypatch):

    def mock_get(*args, **kwargs):
        return MockItemResponse()

    def mock_post(*args, **kwargs):
        return MockMirrorResponse(kwargs["json"])

    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(requests, "post", mock_post)
    monkeypatch.setattr(requests, "put", mock_post)

def test_validations(mock_response):
    """Test that the upload functions will not work from the validation functions"""
    bad_title = [{"titl": "d", "description": "a", "external_url": "b", "image_url": "c"}]
    bad_desc = [{"title": "d", "descriptio": "a", "external_url": "b", "image_url": "c"}]
    bad_ext = [{"titl": "d", "description": "a", "external_ur": "b", "image_url": "c"}]
    bad_img = [{"titl": "d", "description": "a", "external_url": "b", "image_ur": "c"}]
    bad_instruction = [{"promtler": "misspelled promptlet field"}]

    manager = GeniusManager.from_token_config(TEST_TOKEN)

    with pytest.raises(GeniusValidationError):
        manager.upload_items(bad_title)
        manager.upload_items(bad_desc)
        manager.upload_items(bad_ext)
        manager.upload_items(bad_img)

        manager.upload_instructions(bad_instruction)
    
        
def test_batch(mock_response):
    """Test batch call and make sure payload looks like default FeedPayload"""
    manager = GeniusManager(token_config=TokenConfig(project_name="test", token="123"))
    payload = manager.batch()

    assert payload == FeedPayload().dict()

def test_update_item_filter(mock_response):
    manager = GeniusManager.from_token_config(TEST_TOKEN)
    fake_item = {
        "id": 0,
        "title": "Your mom",
        "description": "cow",
        "external_url": "https://cow.com",
        "image_url": "https://imgur.com/cow",
        "metadata": [
            {
                "name": "legs",
                "value": 4
            },
            {
                "name": "available",
                "value": True
            }
        ]
    }

    post_filter_item = manager.update_item(0, fake_item)

    meta = post_filter_item.get('metadata')
    assert 'available' not in [m.get('name') for m in meta]
    
        
