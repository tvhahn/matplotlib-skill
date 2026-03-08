# Python One-Shot Script

You write self-contained Python scripts as single files - no modules, no packages, everything in one file. They can be executed with `uv run script_name.py` without needing a virtual environment or separate requirements file. They always start with this comment (according to PEP 723):

```python
# /// script
# requires-python = ">=3.12"
# ///
```

Use underscore naming: `fetch_api_data.py`, `process_csv.py`, `backup_database.py`

## With Dependencies

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
#     "click",
# ]
# ///

import requests

def main():
    # Hardcode values here or use CLI arguments
    api_url = "https://api.example.com/data"
    response = requests.get(api_url)
    print(response.json())

if __name__ == "__main__":
    main()
```

## CLI Arguments Example

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["click"]
# ///

import click

@click.command()
@click.argument("input_file")
@click.option("--output", "-o")
def main(input_file, output):
    # Your tool logic here
    pass

if __name__ == "__main__":
    main()
```
