from remoras.manager import GWManager
from remoras.structs import WebsocketPayload, Event, TokenConfig, BasicAuth, ProjectConfig, FeedPayload
import json
from dotenv import load_dotenv
import os
import asyncio


async def main():

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

    test_payload = WebsocketPayload(
        id="something",
        search_prompt = "I want to make a new project for manipulating the stock market using builtin python libraries.",
    )

    

    output = await manager.websocket.send_json(test_payload.dict())

    print(output)
    # jsoned = json.loads(output)
    # tools = [json.loads(tool["product"]["body"]) for tool in jsoned["cards"]]

    # saved_id = jsoned['cards'][0]['id']
    # print(saved_id)
    # print([tool['name'] for tool in tools])

    # test_event = Event.create(
    #     id=saved_id,
    #     organization_id=manager.token_config.project_name,
    #     visitor_id="cal",
    #     session_id="something",
    #     weight=4
    # )

    # test_payload_1 = WebsocketPayload(
    #     id="subsequent",
    #     events=[test_event]
    # )

    
    # output = await manager.websocket.send_json(test_payload_1.dict())


    # jsoned = json.loads(output)
    # tools = [json.loads(tool["product"]["body"]) for tool in jsoned["cards"]]

    # saved_id = jsoned['cards'][0]['id']
    # print(saved_id)
    # print([tool['name'] for tool in tools])

    

    # event = Event.create("1", "2", "3", "4", 10)
    # print(event)
    # print(event.dict())

    # websocket_payload = WebsocketPayload(id="id", events=[event])
    # print(websocket_payload.dict())

    # print()

    
if __name__ == "__main__":
    asyncio.run(main())
