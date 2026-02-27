import json
from .exceptions import GeniusValidationError

def validate_items(items: list[dict]):
    for item in items:
        try:
            assert "title" in item, f"'title' field was not found inside of item {item}"
            assert "description" in item, f"'description' field was not found inside of item {item}"
            assert "external_url" in item, f"'external_url' field was not found inside of item {item}"
            assert "image_url" in item, f"'image_url' field was not found inside of item {item}"
        except AssertionError as e:
            raise GeniusValidationError(e.args)
    

def validate_instructions(instructions: list[dict]):
    for instruction in instructions:
        try:
            assert "promptlet" in instruction, f"'promptlet' field not found inside of instruction: {instruction}"
        except AssertionError as e:
            raise GeniusValidationError(e.args)

def validate_policies(policies: list[dict]):
    for policy in policies:
        try:
            assert "policy" in policy, "'policy' field not found inside of object"
        except AssertionError as e:
            raise GeniusValidationError(e.args)
    
