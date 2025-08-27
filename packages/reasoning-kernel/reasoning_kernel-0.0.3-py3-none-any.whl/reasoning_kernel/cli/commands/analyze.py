"""
Analyze command for scenario analysis (alias for the main analyze command)
"""

import click
from reasoning_kernel.cli.ui import UIManager


@click.command()
@click.argument("scenario", required=False)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def analyze(scenario: str, verbose: bool):
    """Analyze a scenario (alias for main analyze command)"""
    ui_manager = UIManager(verbose=verbose)
    
    if not scenario:
        ui_manager.print_info("Please provide a scenario to analyze")
        ui_manager.print_info("Example: reasoning-kernel analyze 'Market volatility in tech stocks'")
        return
    
    ui_manager.print_info("This is an alias command")
    ui_manager.print_info(f"Scenario: {scenario}")
    ui_manager.print_info("Use the main 'reasoning-kernel analyze' command for full analysis")