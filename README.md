# Newton

A simple management system for the Genius Hackathon API.

## How to install

Create a virtual environment for your project:
1. `uv venv` or `python -m venv .venv`
2. activate the virtual environment `source .venv/bin/activate` (follow OS specific instructions)
3. clone this repo either into your project or somewhere near by `git clone `

## Required Features
- [x] Create a new Genius Project
- [x] Safely store tokens and projects
- [x] Upload, edit, and delete `items` and `instructions`
- [x] Easily retrieve `items` via payloads

## Brainstorming

Okay so my first instinct is to do some kind of class for the project management,
provide in either `username`, and `password` for creation of new projects, or `token`
to utilize existing projects.


