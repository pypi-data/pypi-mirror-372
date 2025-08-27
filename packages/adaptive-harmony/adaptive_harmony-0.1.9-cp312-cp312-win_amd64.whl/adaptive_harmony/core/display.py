from rich.console import Console
from rich.table import Table
import textwrap
from adaptive_harmony import StringThread, TokenizedThread


def _stringthread_repr(self: StringThread) -> str:
    """Rich-based __repr__ for StringThread."""
    # Get turns from the thread
    turns = self.get_turns()

    # Create a table without borders
    table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    table.add_column("Role", style="bold blue", no_wrap=True, justify="right")
    table.add_column("Content", overflow="fold")

    wrap_width = 90

    for turn in turns:
        # Wrap content if needed
        if wrap_width > 0 and turn.content:
            wrapped_lines = []
            for line in turn.content.split("\n"):
                if line:
                    wrapped = textwrap.fill(line, width=wrap_width)
                    wrapped_lines.append(wrapped)
                else:
                    wrapped_lines.append("")
            content = "\n".join(wrapped_lines)
        else:
            content = turn.content

        table.add_row(turn.role.upper(), content)

    # Capture the output with horizontal lines
    from io import StringIO

    buffer = StringIO()
    # Use styling for __repr__ since it's typically for interactive display
    console = Console(file=buffer, width=120, markup=False)

    # Get max width for the separator line
    max_role_len = max(len(turn.role) for turn in turns) if turns else 0
    total_width = max_role_len + 2 + wrap_width
    separator = "─" * total_width

    # Print with separators like the Rust version
    buffer.write(separator + "\n")
    console.print(table)
    buffer.write(separator + "\n")

    return buffer.getvalue().rstrip()


def _tokenizedthread_repr(self: TokenizedThread) -> str:
    """Rich-based __repr__ for TokenizedThread."""
    # Get turns from the thread
    turns = self.get_turns()

    # Create a table without borders
    table = Table(show_header=False, show_edge=False, box=None, padding=(0, 1))
    table.add_column("Role", style="bold blue", no_wrap=True, justify="right")
    table.add_column("Tokens", overflow="fold")

    for turn in turns:
        # Format tokens as a string of integers
        tokens_str = " ".join(str(t) for t in turn.content)

        table.add_row(turn.role.upper(), tokens_str)

    # Capture the output with horizontal lines
    from io import StringIO

    buffer = StringIO()
    # Use styling for __repr__ since it's typically for interactive display
    console = Console(file=buffer, width=120, markup=False)

    # Get max width for the separator line
    max_role_len = max(len(turn.role) for turn in turns) if turns else 0
    # Estimate token display width (rough estimate)
    total_width = max_role_len + 2 + 90
    separator = "─" * total_width

    # Print with separators like the Rust version
    buffer.write(separator + "\n")
    console.print(table)
    buffer.write(separator + "\n")

    return buffer.getvalue().rstrip()
