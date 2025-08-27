"""
Interactive wizard for guided MSA reasoning
"""

import click
from reasoning_kernel.cli.ui import UIManager


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
def wizard(verbose: bool):
    """Interactive wizard for guided MSA reasoning"""
    ui_manager = UIManager(verbose=verbose)
    
    ui_manager.print_header("MSA Reasoning Engine Wizard")
    ui_manager.print_info("Welcome to the interactive MSA reasoning wizard!")
    ui_manager.print_warning("The full wizard is not yet implemented")
    ui_manager.print_info("Available alternatives:")
    ui_manager.print_info("  • reasoning-kernel interactive - Interactive mode")
    ui_manager.print_info("  • reasoning-kernel analyze <scenario> - Direct analysis")
    ui_manager.print_info("  • reasoning-kernel stages parse <scenario> - Individual stages")