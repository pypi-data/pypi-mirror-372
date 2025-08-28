"""Command line interface for segee package."""

from __future__ import annotations

import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol, runtime_checkable

from segee import MaxSegmentTree, MinSegmentTree, SumSegmentTree


class TreeType(Enum):
    """Available segment tree types."""

    SUM = ("sum", SumSegmentTree, "sum")
    MIN = ("min", MinSegmentTree, "minimum")
    MAX = ("max", MaxSegmentTree, "maximum")

    def __init__(self, name: str, tree_class: type, operation_name: str):
        self.tree_name = name
        self.tree_class = tree_class
        self.operation_name = operation_name


class AppCommandType(Enum):
    """Application command types for segment tree operations."""

    SET = "set"
    ADD = "add"
    QUERY = "query"


class SlashCommandType(Enum):
    """Slash command types for application control."""

    RESET = "reset"
    HOME = "home"
    HELP = "help"


class SystemCommandType(Enum):
    """System command types for program control."""

    QUIT = "quit"


@dataclass(frozen=True)
class CLIConfig:
    """Configuration for CLI display and behavior."""

    leaf_cell_width: int = 12
    command_rows: int = 20
    tree_size: int = 16
    border_color: str = "\033[90m"
    color_reset: str = "\033[0m"
    index_color: str = "\033[33m"
    command_width: int = 32
    gap_width: int = 8


@dataclass
class CommandResult:
    """Result of command execution."""

    message: str | None = None
    action: str | None = None
    should_add_to_history: bool = True


@runtime_checkable
class SegmentTreeProtocol(Protocol):
    """Protocol for segment tree operations."""

    def __len__(self) -> int: ...
    def __getitem__(self, index: int) -> float: ...
    def __setitem__(self, index: int, value: float) -> None: ...
    def sum(self, left: int, right: int) -> float: ...
    def minimum(self, left: int, right: int) -> float: ...
    def maximum(self, left: int, right: int) -> float: ...


class ValueParser:
    """Parser for command values supporting inf and -inf."""

    @staticmethod
    def parse_value(value_str: str) -> float:
        """Parse value string, supporting inf and -inf."""
        match value_str.lower():
            case "inf" | "infinity":
                return float("inf")
            case "-inf" | "-infinity":
                return float("-inf")
            case _:
                return int(value_str)


class CommandParser:
    """Parser for CLI commands."""

    def __init__(self, config: CLIConfig):
        self.config = config
        self.value_parser = ValueParser()

    def parse_command_type(
        self, command: str
    ) -> AppCommandType | SlashCommandType | SystemCommandType | None:
        """Parse command string to appropriate command type, or None if unknown."""
        match command.lower():
            case "set" | "s":
                return AppCommandType.SET
            case "add" | "a":
                return AppCommandType.ADD
            case "query" | "q":
                return AppCommandType.QUERY
            case "/reset":
                return SlashCommandType.RESET
            case "/home":
                return SlashCommandType.HOME
            case "/help":
                return SlashCommandType.HELP
            case "quit" | "exit":
                return SystemCommandType.QUIT
            case _:
                return None

    def parse_command(
        self, cmd: str, tree: SegmentTreeProtocol, tree_type: TreeType
    ) -> CommandResult:
        """Parse and validate command."""
        parts = cmd.strip().split()
        if not parts:
            return CommandResult()

        command_type = self.parse_command_type(parts[0])

        # Handle unknown command
        if command_type is None:
            return CommandResult(
                message=f"Unknown command: '{parts[0]}'. Type '/help' for available commands."
            )

        try:
            match command_type:
                case AppCommandType.SET:
                    return self._handle_set_command(parts, tree)
                case AppCommandType.ADD:
                    return self._handle_add_command(parts, tree)
                case AppCommandType.QUERY:
                    return self._handle_query_command(parts, tree, tree_type)
                case SlashCommandType.RESET:
                    return CommandResult(action="reset", should_add_to_history=False)
                case SlashCommandType.HOME:
                    return CommandResult(action="home", should_add_to_history=False)
                case SlashCommandType.HELP:
                    return CommandResult(action="show_help", should_add_to_history=False)
                case SystemCommandType.QUIT:
                    return CommandResult(action="quit", should_add_to_history=False)
        except ValueError as e:
            return CommandResult(message=f"Invalid format: {e}")
        except Exception as e:
            return CommandResult(message=f"Error: {e}")

    def _handle_set_command(self, parts: list[str], tree: SegmentTreeProtocol) -> CommandResult:
        """Handle set command."""
        if len(parts) != 3:
            return CommandResult(
                message=f"Usage: set <index> <value> (need exactly 2 arguments, got {len(parts) - 1})"
            )

        index = int(parts[1])
        value = self.value_parser.parse_value(parts[2])

        if not (0 <= index < len(tree)):
            return CommandResult(
                message=f"Index Error: {index} is out of range [0, {len(tree) - 1}] (size={len(tree)})"
            )

        tree[index] = value
        return CommandResult()  # Silent success

    def _handle_add_command(self, parts: list[str], tree: SegmentTreeProtocol) -> CommandResult:
        """Handle add command."""
        if len(parts) != 3:
            return CommandResult(
                message=f"Usage: add <index> <value> (need exactly 2 arguments, got {len(parts) - 1})"
            )

        index = int(parts[1])
        value = self.value_parser.parse_value(parts[2])

        if not (0 <= index < len(tree)):
            return CommandResult(
                message=f"Index Error: {index} is out of range [0, {len(tree) - 1}] (size={len(tree)})"
            )

        tree[index] += value
        return CommandResult()  # Silent success

    def _handle_query_command(
        self, parts: list[str], tree: SegmentTreeProtocol, tree_type: TreeType
    ) -> CommandResult:
        """Handle query command."""
        if len(parts) != 3:
            return CommandResult(
                message=f"Usage: query <left> <right> (need exactly 2 arguments, got {len(parts) - 1})"
            )

        left, right = int(parts[1]), int(parts[2])

        if not (0 <= left < right <= len(tree)):
            return CommandResult(
                message=f"Range Error: [{left}, {right}] is invalid for size {len(tree)}"
            )

        match tree_type:
            case TreeType.SUM:
                result = tree.sum(left, right)
            case TreeType.MIN:
                result = tree.minimum(left, right)
            case TreeType.MAX:
                result = tree.maximum(left, right)

        return CommandResult(message=str(result))


class TreeVisualizer:
    """Handles segment tree visualization."""

    def __init__(self, config: CLIConfig):
        self.config = config
        self.levels = [1, 2, 4, 8, 16]

    def get_tree_value(self, tree: SegmentTreeProtocol | None, level: int, pos: int) -> str:
        """Get value for visualization based on level and position."""
        if tree is None:
            return "0"

        if level == 4:  # Leaf level - user indices 0-15
            user_index = pos
            if user_index < len(tree):
                value = tree[user_index]
                return self._format_value(value)
            return "0"

        # Internal nodes - try direct access first
        try:
            if hasattr(tree, "_data") and hasattr(tree, "_offset"):
                internal_idx = self._calculate_internal_index(level, pos)
                if internal_idx < len(tree._data):
                    value = tree._data[internal_idx]
                    return self._format_value(value)

            # Fallback: range queries
            return self._get_fallback_value(tree, level, pos)
        except (AttributeError, IndexError, ValueError, TypeError):
            return "?"

    def _calculate_internal_index(self, level: int, pos: int) -> int:
        """Calculate internal tree index for given level and position."""
        match level:
            case 0:
                return 0
            case 1:
                return 1 + pos
            case 2:
                return 3 + pos
            case 3:
                return 7 + pos
            case _:
                return 0

    def _get_fallback_value(self, tree: SegmentTreeProtocol, level: int, pos: int) -> str:
        """Get value using range queries as fallback."""
        size = len(tree)

        match level:
            case 0:  # Root - entire range
                return str(tree.sum(0, size) if hasattr(tree, "sum") else 0)
            case 1:  # Level 1 - left/right half
                mid = size // 2
                if pos == 0:
                    return str(tree.sum(0, mid) if hasattr(tree, "sum") else 0)
                return str(tree.sum(mid, size) if hasattr(tree, "sum") else 0)
            case 2:  # Level 2 - quarters
                quarter = size // 4
                start, end = pos * quarter, (pos + 1) * quarter
                return str(tree.sum(start, end) if hasattr(tree, "sum") else 0)
            case 3:  # Level 3 - eighths
                eighth = size // 8
                start, end = pos * eighth, (pos + 1) * eighth
                return str(tree.sum(start, end) if hasattr(tree, "sum") else 0)
            case _:
                return "0"

    def _format_value(self, value: float) -> str:
        """Format value for display."""
        if value == float("inf"):
            return "inf"
        if value == float("-inf"):
            return "-inf"
        return str(value)

    def draw_tree_structure(self, tree: SegmentTreeProtocol | None = None) -> list[str]:
        """Draw segment tree structure as pyramid."""
        lines = []

        for level_idx, cell_count in enumerate(self.levels):
            level_from_bottom = len(self.levels) - 1 - level_idx
            cell_width = self.config.leaf_cell_width * (2**level_from_bottom)

            h_line = self.config.border_color + "─" * (cell_width - 1) + self.config.color_reset

            # Top border for first level only
            if level_idx == 0:
                lines.append(self._create_top_border(cell_count, cell_width, h_line))

            # Empty padding line
            lines.append(self._create_empty_line(cell_count, cell_width))

            # Content line with values
            lines.append(self._create_content_line(tree, level_idx, cell_count, cell_width))

            # Empty padding line
            lines.append(self._create_empty_line(cell_count, cell_width))

            # Bottom border
            lines.append(self._create_bottom_border(cell_count, cell_width, h_line))

        # Add index numbers for leaf level
        if level_idx == len(self.levels) - 1:
            lines.append(self._create_index_line(cell_count, self.config.leaf_cell_width))

        return lines

    def _create_top_border(self, cell_count: int, cell_width: int, h_line: str) -> str:
        """Create top border line."""
        if cell_count == 1:
            return (
                self.config.border_color
                + "┌"
                + self.config.color_reset
                + h_line
                + self.config.border_color
                + "┐"
                + self.config.color_reset
            )

        separator = self.config.border_color + "┬" + self.config.color_reset + h_line
        return (
            self.config.border_color
            + "┌"
            + self.config.color_reset
            + h_line
            + separator * (cell_count - 1)
            + self.config.border_color
            + "┐"
            + self.config.color_reset
        )

    def _create_bottom_border(self, cell_count: int, cell_width: int, h_line: str) -> str:
        """Create bottom border line."""
        if cell_count == 1:
            return (
                self.config.border_color
                + "└"
                + self.config.color_reset
                + h_line
                + self.config.border_color
                + "┘"
                + self.config.color_reset
            )

        separator = self.config.border_color + "┴" + self.config.color_reset + h_line
        return (
            self.config.border_color
            + "└"
            + self.config.color_reset
            + h_line
            + separator * (cell_count - 1)
            + self.config.border_color
            + "┘"
            + self.config.color_reset
        )

    def _create_empty_line(self, cell_count: int, cell_width: int) -> str:
        """Create empty padding line."""
        line = self.config.border_color + "│" + self.config.color_reset
        for _ in range(cell_count):
            line += (
                " " * (cell_width - 1) + self.config.border_color + "│" + self.config.color_reset
            )
        return line

    def _create_content_line(
        self, tree: SegmentTreeProtocol | None, level: int, cell_count: int, cell_width: int
    ) -> str:
        """Create content line with tree values."""
        line = self.config.border_color + "│" + self.config.color_reset

        for i in range(cell_count):
            value = self.get_tree_value(tree, level, i)
            value_padding = (cell_width - 1 - len(value)) // 2
            left_pad = value_padding
            right_pad = cell_width - 1 - len(value) - left_pad
            line += (
                " " * left_pad
                + value
                + " " * right_pad
                + self.config.border_color
                + "│"
                + self.config.color_reset
            )

        return line

    def _create_index_line(self, cell_count: int, cell_width: int) -> str:
        """Create index number line for leaf level."""
        line = " "  # Left border alignment

        for i in range(cell_count):
            index_str = f"{self.config.index_color}{i}{self.config.color_reset}"
            visible_len = len(str(i))
            index_padding = (cell_width - 1 - visible_len) // 2
            left_pad = index_padding
            right_pad = cell_width - 1 - visible_len - left_pad
            line += " " * left_pad + index_str + " " * right_pad
            if i < cell_count - 1:
                line += " "

        return line


class CommandAreaRenderer:
    """Handles command area rendering."""

    def __init__(self, config: CLIConfig):
        self.config = config

    def draw_command_area(self, commands: list[str] | None = None) -> list[str]:
        """Draw user command area with command history."""
        if commands is None:
            commands = []

        lines = []
        lines.append(
            f"{self.config.border_color}┌─────── COMMAND ──────────────┐{self.config.color_reset}"
        )

        display_commands = (
            commands[-self.config.command_rows :]
            if len(commands) > self.config.command_rows
            else commands
        )

        for i in range(self.config.command_rows):
            if i < len(display_commands):
                cmd = display_commands[i].replace("\t", " ")[:28]
                lines.append(
                    f"{self.config.border_color}│{self.config.color_reset} {cmd:<28} {self.config.border_color}│{self.config.color_reset}"
                )
            elif i == len(display_commands):
                lines.append(
                    f"{self.config.border_color}│{self.config.color_reset} >                            {self.config.border_color}│{self.config.color_reset}"
                )
            else:
                lines.append(
                    f"{self.config.border_color}│{self.config.color_reset}                              {self.config.border_color}│{self.config.color_reset}"
                )

        lines.append(
            f"{self.config.border_color}└──────────────────────────────┘{self.config.color_reset}"
        )
        return lines


class DisplayManager:
    """Manages screen display and layout."""

    def __init__(self, config: CLIConfig):
        self.config = config
        self.visualizer = TreeVisualizer(config)
        self.command_renderer = CommandAreaRenderer(config)

    @staticmethod
    def get_terminal_width() -> int:
        """Get terminal width, default to 80 if not available."""
        try:
            return os.get_terminal_size().columns
        except OSError:
            return 80

    def display_split_screen(
        self, commands: list[str] | None = None, tree: SegmentTreeProtocol | None = None
    ) -> None:
        """Display split screen: command area | tree structure."""
        command_lines = self.command_renderer.draw_command_area(commands)
        tree_lines = self.visualizer.draw_tree_structure(tree)

        # Ensure both areas have same height
        max_height = max(len(command_lines), len(tree_lines))
        while len(command_lines) < max_height:
            command_lines.append(" " * 30)
        while len(tree_lines) < max_height:
            tree_lines.append("")

        # Clear screen and display
        os.system("clear" if os.name == "posix" else "cls")
        for command_line, tree_line in zip(command_lines, tree_lines, strict=False):
            gap = " " * self.config.gap_width
            print(f"{command_line:<{self.config.command_width}}{gap}{tree_line}")

    @staticmethod
    def display_logo() -> None:
        """Display Segee startup logo."""
        logo = """
    ✦ ･ ｡ ‧ ˚ ꒰ ⋆ ･ ｡ ‧ ˚ ✦ ˚ ‧ ｡ ･ ⋆ ꒱ ˚ ‧ ｡ ･ ✦

      ███████╗███████╗ ██████╗ ███████╗███████╗
     ██╔════╝██╔════╝██╔════╝ ██╔════╝██╔════╝
     ███████╗█████╗  ██║  ███╗█████╗  █████╗
     ╚════██║██╔══╝  ██║   ██║██╔══╝  ██╔══╝
     ███████║███████╗╚██████╔╝███████╗███████╗
     ╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚══════╝

       ✦ CUI Segment Tree Calculator ✦

    ✦ ･ ｡ ‧ ˚ ꒰ ⋆ ･ ｡ ‧ ˚ ✦ ˚ ‧ ｡ ･ ⋆ ꒱ ˚ ‧ ｡ ･ ✦
"""
        print(logo)


class HelpSystem:
    """Manages help display."""

    def __init__(self, config: CLIConfig):
        self.config = config

    def display_help_screen(self, tree_type: TreeType) -> None:
        """Display full-screen help and wait for Enter to return."""
        os.system("clear" if os.name == "posix" else "cls")

        operation_desc = {TreeType.SUM: "sum", TreeType.MIN: "minimum", TreeType.MAX: "maximum"}

        help_content = f"""
{self.config.border_color}╔══════════════════════════════════════════════════════════════════════════╗
║                            SEGEE HELP - {tree_type.tree_name.upper()} TREE                            ║
╠══════════════════════════════════════════════════════════════════════════╣{self.config.color_reset}

{self.config.border_color}📋 BASIC COMMANDS:{self.config.color_reset}
  set/s <index> <value>    Set element at index to value
  add/a <index> <value>    Add value to element at index
  query/q <left> <right>   Query range [left, right) (half-open)

{self.config.border_color}🔧 SPECIAL COMMANDS:{self.config.color_reset}
  /reset                   Clear tree and command history
  /home                    Return to tree type selection
  /help                    Show this help screen
  quit/exit               Exit the program

{self.config.border_color}📝 EXAMPLES:{self.config.color_reset}
  s 0 10                  → Set tree[0] = 10
  s 3 inf                 → Set tree[3] = inf (infinity)
  s 7 -inf                → Set tree[7] = -inf (negative infinity)
  a 5 -3                  → Add -3 to tree[5]
  q 2 7                   → Query range [2, 7) - indices 2,3,4,5,6

{self.config.border_color}ℹ️  NOTES:{self.config.color_reset}
  • Tree size: {self.config.tree_size} elements (indices 0-{self.config.tree_size - 1})
  • All indices are 0-based
  • Query range is [left, right) - left inclusive, right exclusive
  • {tree_type.tree_name.title()} tree returns {operation_desc[tree_type]} of the range

{self.config.border_color}🎨 VISUALIZATION:{self.config.color_reset}
  • Bottom row: Your data (indices 0-{self.config.tree_size - 1})
  • Upper rows: Internal tree nodes
  • Yellow numbers: Array indices
  • Real-time updates after each command

{self.config.border_color}╚══════════════════════════════════════════════════════════════════════════╝{self.config.color_reset}

Press Enter to return to interactive mode..."""

        print(help_content)
        try:
            input()
        except (EOFError, KeyboardInterrupt):
            pass


class TreeSelector:
    """Handles tree type selection."""

    def select_tree_type(self) -> TreeType:
        """Select segment tree type."""
        print("Select segment tree type:")
        print("1. Sum Segment Tree")
        print("2. Min Segment Tree")
        print("3. Max Segment Tree")

        while True:
            try:
                choice = input("Enter choice (1-3): ")
                match choice:
                    case "1":
                        return TreeType.SUM
                    case "2":
                        return TreeType.MIN
                    case "3":
                        return TreeType.MAX
                    case _:
                        print("Invalid choice. Please enter 1, 2, or 3.")
            except (EOFError, KeyboardInterrupt):
                print("\nExiting...")
                sys.exit(0)


class InteractiveSession:
    """Manages interactive command session."""

    def __init__(self, config: CLIConfig, tree_type: TreeType):
        self.config = config
        self.tree_type = tree_type
        self.tree = tree_type.tree_class(config.tree_size)
        self.commands: list[str] = []
        self.parser = CommandParser(config)
        self.display = DisplayManager(config)
        self.help_system = HelpSystem(config)

    def run(self) -> str | None:
        """Run interactive session, returns action or None."""
        while True:
            self.display.display_split_screen(self.commands, self.tree)

            try:
                cmd = input("\n> ")
                if not cmd.strip():
                    continue

                result = self.parser.parse_command(cmd, self.tree, self.tree_type)

                match result.action:
                    case "quit":
                        print("Goodbye!")
                        return None
                    case "reset":
                        self.tree = self.tree_type.tree_class(self.config.tree_size)
                        self.commands = []
                        continue
                    case "home":
                        return "home"
                    case "show_help":
                        self.help_system.display_help_screen(self.tree_type)
                        continue

                if result.should_add_to_history:
                    self.commands.append(f"> {cmd}")
                    if result.message:
                        self.commands.append(result.message)

            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                return None


class SegeeApplication:
    """Main application class."""

    def __init__(self):
        self.config = CLIConfig()
        self.display = DisplayManager(self.config)
        self.tree_selector = TreeSelector()

    def run(self) -> None:
        """Run the main application loop."""
        while True:
            self.display.display_logo()
            tree_type = self.tree_selector.select_tree_type()

            print(f"\nSelected: {tree_type.tree_name.title()} Segment Tree")
            print(
                "\nCommands: set/s <index> <value>, add/a <index> <value>, query/q <left> <right> (half-open)"
            )
            print("Special: /reset (clear), /home (return here), /help (show commands)")
            print("All indices are 0-based. Press Ctrl+C to exit.")
            input("\nPress Enter to start interactive mode...")

            session = InteractiveSession(self.config, tree_type)
            result = session.run()

            if result != "home":
                break


def main() -> None:
    """Main entry point for the segee CLI."""
    app = SegeeApplication()
    app.run()


if __name__ == "__main__":
    main()
