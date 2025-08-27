"""
Chat command for interactive MSA reasoning conversations
"""

import click
from reasoning_kernel.cli.ui import UIManager


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def chat(verbose: bool):
    """Start an interactive chat session with the MSA reasoning engine"""
    ui_manager = UIManager(verbose=verbose)
    ui_manager.print_info("Chat mode is not yet implemented")
    ui_manager.print_info("Use 'reasoning-kernel interactive' for interactive mode")