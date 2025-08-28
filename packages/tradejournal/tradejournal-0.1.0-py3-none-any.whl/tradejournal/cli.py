"""Command line interface for TradeJournal.

Provides a ``trade`` entry point that can be extended with sub‑commands.
"""

import argparse
import sys


def _build_parser() -> argparse.ArgumentParser:
    """Create the top‑level argument parser.

    The parser defines a ``trade`` command with optional sub‑commands.
    Currently only a ``show`` placeholder is implemented.
    """
    parser = argparse.ArgumentParser(prog="trade", description="Trade journal CLI")
    subparsers = parser.add_subparsers(dest="command", help="sub‑command")

    # ``show`` command – placeholder that displays a simple message.
    show_parser = subparsers.add_parser("show", help="Show journal entries")
    show_parser.add_argument(
        "--count",
        type=int,
        default=10,
        help="Number of recent entries to display (default: 10)",
    )

    # ``add`` command – collects trade details and (for now) prints them.
    add_parser = subparsers.add_parser("add", help="Add a new trade entry")
    add_parser.add_argument(
        "-s",
        "--symbol",
        required=True,
        help="Ticker symbol of the instrument",
    )
    add_parser.add_argument(
        "-q",
        "--quantity",
        type=float,
        required=True,
        help="Quantity of the trade",
    )
    add_parser.add_argument(
        "-p",
        "--price",
        type=float,
        required=True,
        help="Execution price",
    )
    add_parser.add_argument(
        "-r",
        "--risk",
        type=float,
        required=False,
        default=None,
        help="Risk associated with the trade (defaults to config value)",
    )

    # ``list`` command – displays stored trades.
    list_parser = subparsers.add_parser("list", help="List stored trade entries")
    list_parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=None,
        help="Maximum number of recent trades to display (default: all)",
    )

    # ``delete`` command – removes a trade entry by its ID.
    delete_parser = subparsers.add_parser("delete", help="Delete a trade entry by ID")
    delete_parser.add_argument(
        "trade_id",
        help="Identifier of the trade to delete (e.g., 8defde0689b30249)",
    )

    # ``complete`` command – mark a trade as completed up or down, or list completions.
    complete_parser = subparsers.add_parser("complete", help="Mark trade as up/down or list completions")
    complete_sub = complete_parser.add_subparsers(dest="action", help="completion action")
    # ``up`` and ``down`` actions take a trade ID.
    up_parser = complete_sub.add_parser("up", help="Mark trade as up")
    up_parser.add_argument("trade_id", help="Trade ID to mark as up")
    down_parser = complete_sub.add_parser("down", help="Mark trade as down")
    down_parser.add_argument("trade_id", help="Trade ID to mark as down")
    # ``list`` action shows all completions.
    complete_sub.add_parser("list", help="List completed trades")

    return parser


def main(argv: list[str] | None = None) -> None:
    """Entry point for the ``trade`` console script.

    Args:
        argv: Optional list of arguments (defaults to ``sys.argv[1:]``).
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = _build_parser()
    # Ensure the SQLite database exists in the user's home directory before any
    # command execution. ``init_db`` will create the file and schema if needed.
    from tradejournal.store import init_db
    init_db()
    args = parser.parse_args(argv)

    # Dispatch based on selected sub‑command.
    if args.command == "show":
        # In a real implementation this would query stored trades.
        print(f"Showing the latest {args.count} trade entries (placeholder).")
    elif args.command == "add":
        # Persist the trade using SQLite storage and print the generated ID.
        from tradejournal.store import save_trade, load_config

        config = load_config()
        default_risk = config.get("default_risk", 5)
        # Use the supplied risk if provided, otherwise fall back to the default.
        risk_val = args.risk if args.risk is not None else default_risk

        trade_id = save_trade(
            symbol=args.symbol,
            quantity=args.quantity,
            price=args.price,
            risk=risk_val,
        )
        print(
            f"Trade added – ID: {trade_id}, symbol={args.symbol}, "
            f"quantity={args.quantity}, price={args.price}, risk={risk_val}"
        )
    elif args.command == "list":
        # Retrieve and display stored trades according to config ordering.
        from tradejournal.store import list_trades, load_config

        # Exclude completed trades from the listing.
        from tradejournal.store import get_completed_ids
        completed_ids = get_completed_ids()
        rows = [row for row in list_trades(limit=args.limit) if row[0] not in completed_ids]
        if not rows:
            print("No trades recorded.")
        else:
            # Rich table output respecting column ordering from config.
            from rich.table import Table
            from rich.console import Console

            # Load column ordering from config.
            config = load_config()
            ordering = config.get(
                "column_ordering",
                ["ID", "Symbol", "Qty", "Price", "Risk", "Timestamp", "Value", "Downside", "Upside", "DownPrice", "UpPrice"],
            )

            from rich import box
            console = Console()
            # Restore original table style with minimal box and default header color.
            table = Table(show_header=True, box=box.SQUARE_DOUBLE_HEAD)
            # Dynamically add columns with semantic colors.
            for col in ordering:
                # Special placeholder for blank columns.
                if col.lower() == "blank" or col == "":
                    # Add an empty column header; cells will be empty strings.
                    table.add_column("", style="grey70", header_style="grey70")
                    continue
                # Determine cell and header styles based on meaning.
                if col == "ID":
                    cell_style = "dim"
                    header_style = "dim"
                    width = 18
                elif col == "Symbol":
                    cell_style = "bold cyan"
                    header_style = "bold cyan"
                    width = 6
                elif col == "Timestamp":
                    cell_style = "grey70"
                    header_style = "grey70"
                    width = None
                elif col in {"Downside", "DownPrice"}:
                    cell_style = "red"
                    header_style = "red"
                    width = None
                elif col in {"Upside", "UpPrice"}:
                    cell_style = "green"
                    header_style = "green"
                    width = None
                else:
                    cell_style = "grey70"
                    header_style = "grey70"
                    width = None
                # Add column with appropriate width/justification and header style.
                if width:
                    table.add_column(col, style=cell_style, header_style=header_style, width=width)
                else:
                    table.add_column(col, style=cell_style, header_style=header_style, justify="right")

            from datetime import datetime
            now = datetime.now()
            # Accumulate net totals.
            net_value = 0.0
            net_downside = 0.0
            net_upside = 0.0
            for row in rows:
                trade_id, symbol, qty, price, risk, ts = row
                # Compute days ago for timestamp.
                if hasattr(ts, "date"):
                    delta_days = (now.date() - ts.date()).days
                    if delta_days == 0:
                        ts_str = "today"
                    else:
                        ts_str = f"{delta_days}d ago"
                else:
                    ts_str = str(ts)
                # Compute derived columns.
                value = price * qty
                downprice = (1.0 - (risk * 0.01)) * price
                upprice = (1.0 + (risk * 0.02)) * price
                downside = downprice * qty
                upside = upprice * qty
                net_value += value
                net_downside += downside
                net_upside += upside
                # Map column names to string values.
                col_map = {
                    "ID": trade_id,
                    "Symbol": symbol,
                    "Qty": f"{qty:.2f}",
                    "Price": f"{price:.2f}",
                    "Risk": f"{risk:.2f}",
                    "Timestamp": ts_str,
                    "Value": f"{value:.2f}",
                    "Downside": f"{downside:.2f}",
                    "Upside": f"{upside:.2f}",
                    "DownPrice": f"{downprice:.2f}",
                    "UpPrice": f"{upprice:.2f}",
                }
                table.add_row(*[col_map.get(col, "") for col in ordering])
            console.print(table)
            # Render net summary table.
            # Render a concise summary table matching the style used for completions.
            summary = Table(show_header=False, box=box.SQUARE_DOUBLE_HEAD)
            summary.add_column("Metric", style="bold")
            summary.add_column("Value", justify="right")
            summary.add_row("Net Value", f"{net_value:.2f}")
            summary.add_row("Net Downside", f"{net_downside:.2f}", style='red')
            summary.add_row("Net Upside", f"{net_upside:.2f}", style='green')
            console.print(summary)
        # No further action needed.
        return
    elif args.command == "delete":
        # Delete the specified trade.
        from tradejournal.store import delete_trade

        deleted = delete_trade(args.trade_id)
        if deleted:
            print(f"Trade {args.trade_id} deleted.")
        else:
            print(f"Trade {args.trade_id} not found.")
    elif args.command == "complete":
        from tradejournal.store import complete_trade, list_completions
        if args.action == "list":
            rows = list_completions()
            if not rows:
                print("No completions recorded.")
            else:
                from rich.table import Table
                from rich.console import Console
                from rich import box
                console = Console()
                table = Table(show_header=True, box=box.SQUARE_DOUBLE_HEAD)
                table.add_column("Trade ID", style="dim")
                table.add_column("Symbol", style="bold cyan")
                table.add_column("Direction", style="magenta")
                table.add_column("Timestamp", style="grey70")
                # Show profit column as well.
                table.add_column("Profit", style="yellow", justify="right")
                for trade_id, symbol, direction, ts, profit in rows:
                    # Determine style based on direction.
                    style = "green" if direction == "up" else "red"
                    table.add_row(trade_id, symbol, direction, str(ts), f"{profit:.2f}", style=style)
                console.print(table)
                # Compute summary statistics: success rate and net profit.
                up_count = sum(1 for _, _, direction, _, _ in rows if direction == "up")
                down_count = sum(1 for _, _, direction, _, _ in rows if direction == "down")
                net_profit = sum(profit for _, _, _, _, profit in rows)
                total = up_count + down_count
                success_pct = (up_count / total * 100) if total else 0.0
                # Render a summary table.
                summary = Table(show_header=False, box=box.SQUARE_DOUBLE_HEAD)
                summary.add_column("Metric", style="bold")
                summary.add_column("Value", justify="right")
                summary.add_row("% Success", f"{success_pct:.2f}%")
                if net_profit > 0:
                    summary.add_row("Net profit", f"{net_profit:.2f}", style='green')
                else:
                    summary.add_row("Net profit", f"{net_profit:.2f}", style='red')
                console.print(summary)
        elif args.action in ("up", "down"):
            success = complete_trade(args.trade_id, args.action)
            if success:
                print(f"Trade {args.trade_id} marked as {args.action}.")
            else:
                print(f"Failed to mark trade {args.trade_id} as {args.action}.")
        else:
            # Should not happen due to argparse choices.
            print("Invalid completion action.")
    else:
        # No sub‑command provided – show help.
        parser.print_help()
        # No sub‑command provided – show help.
        parser.print_help()


if __name__ == "__main__":
    main()
