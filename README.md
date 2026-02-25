# Remoras

A simple management system for the Genius Hackathon API.

[remora](https://en.wikipedia.org/wiki/Remora)


Changed name from `newton` to `remoras` if you see `newton` or `genius` somewhere this is an artifact
of the old name. `remoras` was available on pypi

## How to install

### PyPi
`pip install remoras`

[PyPi Link](https://pypi.org/project/remoras/)

### From Source
If you are interested in modifying or contributing to `remoras`

####  Requirements
1. Python >= 3.12


Create a virtual environment for your project:
1. `uv venv` or `python -m venv .venv`
2. Activate the virtual environment `source .venv/bin/activate` (follow OS specific instructions)
3. Clone this repo either into your project or somewhere near by `git clone https://github.com/GrayWhaleAI/remoras.git`
4. With your virtual environment activated `cd newton`, `uv pip install -e .` or `pip install -e .`

> You will ideally see something like `remoras = 0.1.0` installed or something like that

## How to use
In your project you can import as so:

```python
from remoras import GeniusManager, TokenConfig, FeedPayload
```

### `GeniusManager`

The `GeniusManager` class is the main class you will be interacting with to utilize
product genius databases.

It takes in four keyword arguments:
- `basic_auth`,
- `token_config`,
- `project_config`,
- `project_dir`

#### `basic_auth`: `BasicAuth`, and `project_config` : `ProjectConfig`
The `basic_auth` argument works in conjunction with the `project_config` argument.
Both of these arguments must be present to create a new project using a genius database.

The `BasicAuth` class provides a stricter way of passing the authorization information for project creation.
The `ProjectConfig` class provides a stricter way of passing the name and information of your project for project creation.

**Example**
```python
from remoras import GeniusManager, BasicAuth, ProjectConfig

basic_auth = BasicAuth(username="provided_username", password="provided_password")
project_config = ProjectConfig(project_name="MyCoolProject", project_summary="This is my super cool project", hacker_email="mycool@email.com")

manager = GeniusManager(basic_auth=basic_auth, project_config=project_config)
```

The `provided_username` and `provided_password` should be replaced with the actual username and password given to you
during the hackathon.

Both `BasicAuth` and `ProjectConfig` can load their information from a `.json` file via `load_from_file()`

**Example**
```python
from remoras import BasicAuth, ProjectConfig, GeniusManager

basic_auth = BasicAuth.load_from_file("file_with_my_auth.json")
project_config = ProjectConfig.load_from_file("file_with_my_project_info.json")

manager = GeniusManager(basic_auth=basic_auth, project_config=project_config)
```

> Make sure your loaded file contains the same fields as the class. For `BasicAuth`: `username`, `password`, For `ProjectConfig`: `project_name`, `project_summary`, `hacker_email`.

#### `token_config` : `TokenConfig`
If we already have a database that exists and have a token for the project, as well as the project's name we
can utilize the `TokenConfig` class.

**Example**
```python
from remoras import GeniusManager, TokenConfig

token_config = TokenConfig(project_name="MyCoolProject", token="supersecrettoken199999")
manager = GeniusManager(token_config=token_config)
```

> TokenConfig also exposes `load_from_file` which can be used in the same way as the `BasicAuth` and `ProjectConfig` classes, required fields are `project_name` and `token`

#### `project_dir`
The `project_dir` argument just tells this library where to save generated tokens (if you are making a new project)


### Making a new project

#### Pre-Requisites

##### Items
As a **pre-requisite** make sure that you already have some items formatted into the `genius` format
[Official Docs](https://gamalon.github.io/genius-hackathon-documentation/) (look at Step 2 of "GettingStarted")

**Example**
```json
[
  {
    "title": "Something",
    "description": "Well ain't that something",
    "image_url": "https://animalfactguide.com/wp-content/uploads/2022/03/koala_iStock-140396797-scaled.jpg",
    "external_url": "https://google.com",
    "id": "1",
    "metadata": [
      {"name": "someValue", "value": 1},
      {"name": "someOtherValue", "value": "Hello"}
    ]
  }, ...
]
```

> Ensure that `image_url` and `external_url` are both valid. `image_url` needs to resolve to an image, and
`external_url` needs to resolve to a webpage.

> One trick (if your app is not image/card focused) is to just use the same `image_url` and `external_url` for all items.

##### Instructions
You will also need a set of instructions for your model. The format for these can be seen under Step 3 of Getting Started in the
previously linked docs.

**Example**
```json
[
  {
    "promptlet": "You do big things"
  },
  {
    "promptlet": "You do really big things"
  }
]
```

#### Using the `GeniusManager`
As long as we have either a variable containing our `items`, and `prompts` or
have that information in some files we can utilize the `GeniusManager` to create and manage our project.

The `GeniusManager` class exposes a function called `create_project`. This function
will build your model from start to finish and is the easiest way to utilize this class.

> You will need to wait for an email that says `Training complete` or something along those lines
before you will be able to actually use the model.

**Example**
```python
from remoras import GeniusManager, BasicAuth, ProjectConfig

# load in our required auth and configuration for creating a new project
basic_auth = BasicAuth.load_from_file("myauth.json")
project_config = ProjectConfig.load_from_file("myconfig.json")

# create the manager
manager = GeniusManager(basic_auth=basic_auth, project_config=project_config)

manager.create_project(items, instructions) # if we have variables `items` and `instructions` we can pass them directly

# OR using file paths

manager.create_project(items_path, instructions_path) # assuming these variables contain a string pointing to those files i.e items_path = "myfolder/items.json" and instructions_path = "myfolder/instructions.json"
```

This will create a `token.json` file inside of `project_dir` (default: "genius_project/")
that can be used to create a `TokenConfig` class for later use.


### Getting items from an Existing Project

**Example**
```python
from remoras import GeniusManager, TokenConfig, FeedPayload

# Load our token configuration for an existing project (this will be made by `create_project` as in previous example)
token_config = TokenConfig.load_from_file("genius_project/token.json")

manager = GeniusManager(token_config=token_config)

# If we have not promoted a model we should do so now
manager.promote_most_recent_model() # this will promote the most recently trained model to being the active model

payload = FeedPayload(
  page=1, #paginated results
  batch_count=1, #number of items to return
  events=[], # For event information see the official docs
  search_prompt="I want something!" # this can be an initial user search or any string you like
)

items = manager.batch_to_items(payload=payload)
# optionally you can pass a session_id to this function

items = manager.batch_to_items(session_id="my_custom_id", payload=payload)
# if a session_id is not passed a random uuid is used instead.
```

### Other Operations
The `GeniusManager` class also exposes CRUD operations on items, and instructions.

#### Items

##### .upload_items(items_or_path: Union\[str, list\])
This can take in either a file path or a list of genius items and upload them to your project
you will need to re-train a model after doing this.

##### .list_items(page:int=1, count:int=10)
This will return items. You can paginate over results or just set the count to the number of items you have / large number

##### .get_item(item_id:str)
This will return the item given its id. This function is used by `batch_to_items` to convert item ids into usable items

##### .update_item(item_id:str, updated_item:dict)
You can update an item using its id and sending a new `genius` formatted item

##### .delete_item(item_id:str)
Remove an Item

#### Instructions

##### .upload_instructions(instructions_or_path: Union\[str, list\])
This is used in `create_project` to upload instructions. Pass either a list of instructions or a file path as a string

##### .list_instructions()
Returns all instructions available to the model

##### .update_instruction(promptlet_id:str, promptlet:dict)
Update an instruction with new information

##### .delete_instruction(promptlet_id:str)
Remove an instruction
