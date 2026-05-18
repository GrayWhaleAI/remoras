from remoras import GeniusManager, TokenConfig, BasicAuth, ProjectConfig, FeedPayload, GWManager
import json
from dotenv import load_dotenv
import os
import asyncio


async def main():
    print("Hello from newton!")

    load_dotenv()
    # basic_auth = BasicAuth(username=os.environ.get("GENIUS_USERNAME"), password=os.environ.get("GENIUS_PASSWORD"))
    # project_config = ProjectConfig(project_name="newtontest4", project_summary="no", hacker_email="calblanco1125@gmail.com")

    # manager = GeniusManager(basic_auth=basic_auth, project_config=project_config, project_dir="test4/")
    # manager.create_project("../Mach-III/genius/tools.json", "../Mach-III/genius/prompts.json", remove_ai_instruction=True)

    
    # basic_auth = BasicAuth.load_from_file("genius/auth.json")
    # project_config = ProjectConfig.load_from_file("genius/project_config.json")

    # manager = GeniusManager(basic_auth=basic_auth, project_config=project_config)

    # manager.create_project("../Mach-III/genius/tools.json", "../Mach-III/genius/prompts.json")

    # payload = FeedPayload()
    # print(payload.dict())
    
    # manager = GeniusManager(token_config=TokenConfig.load_from_file("test4/token.json"))
    # manager.promote_most_recent_model() #Optional if you do not already have a model promoted
    # items = manager.batch_to_items()

    # print(items)
    #

    manager = GWManager.from_token(TokenConfig.load("../pear-proxy/genius_project/token.json"))

    await manager.websocket.initiate()

    test_payload = {
        "id": "something",
        "type": "socket_pagination_request",
        "search_prompt": "I want to make a new project for manipulating the stock market using builtin python libraries.",
        "events": [],
        "batch_count": 3
    }

    output = await manager.websocket.send_json(test_payload)
    print(type(output))

    jsoned = json.loads(output)

    tools = [json.loads(tool["product"]["body"]) for tool in jsoned["cards"]]

    print([tool["name"] for tool in tools])
if __name__ == "__main__":
    asyncio.run(main())
