# Prompt Manager

A cross-platform prompt management application written in Python with a native Tkinter interface.

## Features

- Store prompts as markdown files with metadata (ID, name, description, tags).
- Automatic saving with version history and file locking.
- Search prompts by wildcard, regex, or fuzzy matching.
- Launch LLMs in the default browser via configurable buttons.
- Choose a directory on the file system for prompts.

## Usage

Run the application:

```bash
python -m promptmgr.app
```

Prompts are saved in the selected directory as Markdown files. Each save places the latest version at the top and previous versions below.
