# Newton

A simple management system for the Genius Hackathon API.

## How to install

Create a virtual environment for your project:
1. `uv venv` or `python -m venv .venv`
2. Activate the virtual environment `source .venv/bin/activate` (follow OS specific instructions)
3. Clone this repo either into your project or somewhere near by `git clone https://github.com/GrayWhaleAI/newton.git`
4. With your virtual environment activated `cd newton`, `uv pip install -e .` or `pip install -e .`

> You will ideally see something like `newton = 0.1.0` installed or something like that

## How to use
In your project you can import as so:

```python
from genius import GeniusManager, TokenConfig, FeedPayload
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
from genius import GeniusManager, BasicAuth, ProjectConfig

basic_auth = BasicAuth(username="provided_username", password="provided_password")
project_config = ProjectConfig(project_name="MyCoolProject", project_summary="This is my super cool project", hacker_email="mycool@email.com")

manager = GeniusManager(basic_auth=basic_auth, project_config=project_config)
```

The `provided_username` and `provided_password` should be replaced with the actual username and password given to you
during the hackathon.

#### `token_config` : `TokenConfig`
If we already have a database that exists and have a token for the project, as well as the project's name we
can utilize the `TokenConfig` class.

**Example**
```python
from genius import GeniusManager, TokenConfig

token_config = TokenConfig(project_name="MyCoolProject", token="supersecrettoken199999")
manager = GeniusManager(token_config=token_config)
```

## Required Features
- [x] Create a new Genius Project
- [x] Safely store tokens and projects
- [x] Upload, edit, and delete `items` and `instructions`
- [x] Easily retrieve `items` via payloads

## Brainstorming

Okay so my first instinct is to do some kind of class for the project management,
provide in either `username`, and `password` for creation of new projects, or `token`
to utilize existing projects.


