# reasoning_kernel/interfaces/cli/interactive.py
import rich
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn
import asyncio


class NaturalLanguageCLI:
    """Enhanced CLI with natural language understanding"""

    def __init__(self, reasoning_kernel):
        self.console = Console()
        self.kernel = reasoning_kernel
        self.session_history = []

    async def start_interactive_session(self):
        """Start an interactive reasoning session"""
        self.console.print(
            Panel.fit(
                "[bold cyan]🧠 Reasoning Kernel v1.0[/bold cyan]\n"
                "[dim]Natural Language Cognitive Reasoning System[/dim]",
                border_style="cyan",
            )
        )

        while True:
            try:
                # Get user input with rich formatting
                query = await self._get_input()

                if query.lower() in ["exit", "quit", "bye"]:
                    self.console.print("[yellow]Goodbye! 👋[/yellow]")
                    break

                # Process with visual feedback
                await self._process_with_feedback(query)

            except KeyboardInterrupt:
                self.console.print("\n[red]Interrupted[/red]")
                break

    async def _process_with_feedback(self, query: str):
        """Process query with rich visual feedback"""
        with self.console.status("[bold green]Thinking...", spinner="dots"):
            # Show reasoning steps
            result = await self.kernel.process_query(query)

        # Display results in formatted panels
        self._display_results(result)

    def _display_results(self, result: Dict):
        """Display results with rich formatting"""
        # Create result panel
        panel = Panel(
            result["answer"],
            title=f"[green]Answer (Confidence: {result['confidence']:.2%})[/green]",
            border_style="green",
        )
        self.console.print(panel)

        # Show reasoning trace if verbose
        if self.verbose_mode:
            trace_table = Table(title="Reasoning Trace")
            trace_table.add_column("Step", style="cyan")
            trace_table.add_column("Action", style="magenta")
            trace_table.add_column("Result", style="green")

            for step in result["reasoning_trace"]:
                trace_table.add_row(str(step["number"]), step["action"], step["result"])

            self.console.print(trace_table)
