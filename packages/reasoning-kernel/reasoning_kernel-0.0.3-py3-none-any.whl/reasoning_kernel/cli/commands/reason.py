"""
Reason command for structured reasoning operations
"""

import click
from reasoning_kernel.cli.ui import UIManager


@click.command()
@click.argument("query", required=False)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def reason(query: str, verbose: bool):
    """Perform structured reasoning on a query"""
    ui_manager = UIManager(verbose=verbose)
    
    if not query:
        ui_manager.print_info("Please provide a query to reason about")
        ui_manager.print_info("Example: reasoning-kernel reason 'Why do markets crash?'")
        return
    
    ui_manager.print_info("Structured reasoning mode is not yet implemented")
    ui_manager.print_info(f"Query: {query}")
    ui_manager.print_info("Use 'reasoning-kernel analyze' for analysis mode")