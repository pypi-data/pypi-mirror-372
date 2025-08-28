"""Console script for langchain_arxiv."""

import typer
from rich.console import Console

from langchain_arxiv import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for langchain_arxiv."""
    console.print("Replace this message by putting your code into "
               "langchain_arxiv.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
