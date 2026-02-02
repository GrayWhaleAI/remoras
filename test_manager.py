from genius import GeniusManager, BasicAuth, ProjectConfig, TokenConfig
import pytest
import requests

# Tests
# 1. Test for construction errors
# 2. Test save and load token
# 3. Test header creation
# 4. Test make project
#     - test working
#     - test error throwing
# 5. Test upload items
# 6. Test upload instructions
# 7. Test CRUD on items
# 8. Test CRUD on instructions
# 9. Test create_model
#

def test_manager_construction():
    with pytest.raises(AssertionError):
        manager = GeniusManager() # should raise an exception because no configs are sent
    
        manager = GeniusManager(basic_auth=BasicAuth(username="a", password="b")) #should raise an exception because we need project_config as well

        manager = GeniusManager(project_config=ProjectConfig(project_name="a", project_summary="b", hacker_email="c"))

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
        return MockItemResponse()

    monkeypatch.setattr(requests, "get", mock_get)
    monkeypatch.setattr(requests, "post", mock_get)

def test_batch(mock_response):
    manager = GeniusManager(token_config=TokenConfig(project_name="test", token="123"))
    items = manager.batch()

    assert items == ["1", "2", "3"]
    
    
        
