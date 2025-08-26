import sys

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from lhammai_cli.history import ConversationHistory
from lhammai_cli.schema import Role
from lhammai_cli.settings import settings
from lhammai_cli.utils import get_llm_response

console = Console()


@click.command
@click.option("--prompt", "-p", help="Prompt to send to the LLM")
@click.option("--model", "-m", default=settings.model, help="LLM model to use")
@click.option("--api-base", default=settings.api_base, help="Host to connect to")
def main(prompt: str | None, model: str, api_base: str) -> None:
    """Interact with any LLM."""
    stdin_content = ""
    if not sys.stdin.isatty():
        stdin_content = sys.stdin.read().strip()

    if stdin_content and prompt:
        final_prompt = f"{prompt} {stdin_content}"
    elif stdin_content:
        final_prompt = stdin_content
    elif prompt:
        final_prompt = prompt
    else:
        console.print("\n❌ Error: [red]No input provided. Use -p/--prompt option or pipe content to stdin[/red]")
        sys.exit(1)

    console.print(f"\n✨ Connected to [cyan]'{model}'[/cyan] at [cyan]'{api_base}'[/cyan]\n")

    # Initialize conversation history
    history = ConversationHistory.start_new(model, api_base)
    try:
        history.add_message(Role.USER, final_prompt)
        response = get_llm_response(final_prompt, model, api_base)
        if response:
            history.add_message(Role.ASSISTANT, response)
            history.save_to_disk()

            response_panel = Panel(
                Markdown(response), title="🤖 Assistant", title_align="left", border_style="cyan", padding=(1, 1)
            )
            console.print(response_panel)
        else:
            console.print(f"\n❌ LLM response: [red]No response received from {model}[/red]")
    except Exception as e:
        console.print(f"\n❌ An error occurred: [red]{e}[/red]")
