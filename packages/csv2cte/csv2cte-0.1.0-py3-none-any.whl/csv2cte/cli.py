#!/usr/bin/env python3
"""
csv2cte – Transform a CSV file into a PostgreSQL VALUES‑based CTE.

Features
--------
* Automatic detection of numeric vs. text columns.
* Optional ``--coltypes`` JSON string to override or explicitly set SQL types.
* Typer based command line interface with nice help output.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List

import typer

app = typer.Typer(
    add_completion=False, help="Convert CSV files to a PostgreSQL VALUES‑based CTE."
)


# ----------------------------------------------------------------------
# Helper utilities (escaping & type checks)
# ----------------------------------------------------------------------


def escape_sql_str(value: str) -> str:
    """Escape single quotes for safe SQL literals."""
    return value.replace("'", "''")


TEXT_TYPES = {"text", "varchar", "char", "character varying"}


def is_numeric(s: str) -> bool:
    """Return True if *s* can be parsed as a float number."""
    try:
        float(s)
        return True
    except ValueError:
        return False


def process_value(val: str, col_type: str | None = None) -> str:
    """
    Convert a raw CSV field into its SQL literal representation.

    * Empty strings → ``NULL``.
    * With an explicit ``col_type`` we obey it (text=>quoted, numeric=>bare when possible,
      date/timestamp=>quoted).
    * Without a specific type we try numeric detection; everything else becomes quoted text.
    """
    if val == "":
        return "NULL"

    col_lc = (col_type or "").lower()

    # Text‑type – always quote
    if col_lc in TEXT_TYPES:
        return f"'{escape_sql_str(val)}'"

    # Numeric family – keep as is when it looks numeric, otherwise quote.
    if col_lc in {
        "integer",
        "int",
        "bigint",
        "numeric",
        "float",
        "double precision",
        "real",
    }:
        return val if is_numeric(val) else f"'{escape_sql_str(val)}'"

    # Date / timestamp families – quoted string works (PostgreSQL will cast)
    if any(tok in col_lc for tok in ("date", "time")):
        return f"'{escape_sql_str(val)}'"

    # No explicit type: auto‑detect numeric, otherwise treat as text.
    if not col_type:
        return val if is_numeric(val) else f"'{escape_sql_str(val)}'"

    # Unknown custom type – safest route is to quote it.
    return f"'{escape_sql_str(val)}'"


# ----------------------------------------------------------------------
# Column‑type detection and merging
# ----------------------------------------------------------------------


def guess_column_types(rows: List[List[str]], headers: List[str]) -> Dict[str, str]:
    """
    Simple heuristic:

        * If **every** non‑empty cell in a column is numeric → ``numeric``.
        * Otherwise → ``text``.

    Returns a mapping of the original header string to its guessed type.
    """
    col_type_map: Dict[str, str] = {}
    for idx, header in enumerate(headers):
        all_numeric = True
        for row in rows:
            if idx >= len(row):
                continue  # ignore malformed short lines
            cell = row[idx].strip()
            if not cell:  # empty cells do not affect detection
                continue
            if not is_numeric(cell):
                all_numeric = False
                break
        col_type_map[header] = "numeric" if all_numeric else "text"
    return col_type_map


def build_column_type_map(
    headers: List[str],
    rows: List[List[str]],
    override_json: str | None,
) -> Dict[str, str]:
    """
    Produce a final column → SQL‑type mapping.

     - Guess numeric/text for every column.
     - Apply any JSON overrides supplied via ``--coltypes`` (case‑insensitive).

    The returned dictionary uses the **exact** header strings as keys,
    which is convenient for later lookup when rendering rows.
    """
    guessed = guess_column_types(rows, headers)

    if not override_json:
        return guessed

    # ------------------------------------------------------------------
    # Parse user overrides
    # ------------------------------------------------------------------
    try:
        raw_overrides: Dict[str, str] = json.loads(override_json)
        if not isinstance(raw_overrides, dict):
            raise ValueError("JSON must be an object mapping column names to types.")
    except json.JSONDecodeError as exc:
        typer.secho(
            f"❌ Could not parse --coltypes JSON: {exc}", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1) from exc
    except Exception as exc:  # pragma: no cover – defensive programming
        typer.secho(
            f"❌ Invalid column‑type overrides: {exc}", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1) from exc

    lowered_guess = {k.lower(): v for k, v in guessed.items()}

    # Apply overrides (case‑insensitive on both sides)
    for raw_key, raw_val in raw_overrides.items():
        lowered_guess[raw_key.strip().lower()] = raw_val.strip()

    # Re‑attach original header case
    final: Dict[str, str] = {}
    for hdr in headers:
        final[hdr] = (lowered_guess.get(hdr.lower())) or "text"
    return final


# ----------------------------------------------------------------------
# Build the CTE string
# ----------------------------------------------------------------------


def build_cte(
    rows: Iterable[List[str]],
    headers: List[str],
    cte_name: str = "cte_data",
    table_alias: str = "t",
    column_type_map: Dict[str, str] | None = None,
) -> str:
    """
    Assemble the final PostgreSQL CTE.

    * ``rows`` – already‑read CSV rows.
    * ``headers`` – original header line (used verbatim in output).
    * ``column_type_map`` – mapping header → SQL type; if omitted each cell gets
      auto‑detection as performed by :func:`process_value`.
    """
    col_list_sql = ",\n    ".join(headers)

    rendered_rows: List[str] = []
    for row in rows:
        literals = [
            process_value(val, column_type_map.get(col) if column_type_map else None)
            for col, val in zip(headers, row)
        ]
        rendered_rows.append(f"({', '.join(literals)})")

    values_sql = ",\n    ".join(rendered_rows)

    return (
        f"WITH {cte_name} AS (\n"
        "  SELECT *\n"
        "  FROM (VALUES\n"
        f"    {values_sql}\n"
        "  ) AS "
        f"{table_alias}(\n"
        f"    {col_list_sql}\n"
        "  )\n"
        ")\n"
        f"SELECT * FROM {cte_name};"
    )


# ----------------------------------------------------------------------
# Typer command
# ----------------------------------------------------------------------


@app.command()
def convert(
    csv_file: typer.FileText = typer.Option(
        ..., "--file", "-f", help="Path to the CSV file; use '-' for stdin."
    ),
    name: str = typer.Option(
        "cte_data", "--name", "-n", help="CTE identifier used in the generated SQL."
    ),
    alias: str = typer.Option("t", "--alias", "-a", help="Table alias inside the CTE."),
    coltypes: str | None = typer.Option(
        None,
        "--coltypes",
        "-c",
        help=(
            "JSON string mapping column names to explicit SQL types. "
            "Overrides automatic detection."
        ),
    ),
    output: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Write the generated CTE into this file (UTF‑8). If omitted, prints to stdout.",
    ),
) -> None:
    """
    Convert a CSV file into a PostgreSQL VALUES‑based Common Table Expression.
    """

    # ------------------------------------------------------------------
    # Load all rows so we can auto‑detect column types before rendering
    # ------------------------------------------------------------------
    try:
        reader = csv.reader(csv_file)
        headers: List[str] = next(reader)  # empty file → StopIteration handled below
        data_rows: List[List[str]] = list(reader)
    except StopIteration:
        typer.secho(
            "❌ The supplied CSV appears to be empty.", fg=typer.colors.RED, err=True
        )
        raise typer.Exit(code=1)
    except csv.Error as exc:  # pragma: no cover – unlikely unless malformed CSV
        typer.secho(f"❌ Error reading CSV file: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    # ------------------------------------------------------------------
    # Determine column types (auto‑detect + optional overrides)
    # ------------------------------------------------------------------
    col_type_map = build_column_type_map(headers, data_rows, coltypes)

    cte_sql = build_cte(
        rows=data_rows,
        headers=headers,
        cte_name=name,
        table_alias=alias,
        column_type_map=col_type_map,
    )

    if output:
        try:
            output.write_text(cte_sql + "\n", encoding="utf-8")
            typer.secho(f"✅ CTE written to {output}", fg=typer.colors.GREEN)
        except OSError as exc:  # pragma: no cover – defensive
            typer.secho(
                f"❌ Could not write file {output}: {exc}",
                fg=typer.colors.RED,
                err=True,
            )
            raise typer.Exit(code=1)
    else:
        typer.echo(cte_sql)


# ----------------------------------------------------------------------
def run() -> None:
    """Console‑script entry point registered as ``csv2cte``."""
    app()


if __name__ == "__main__":
    # Allows quick test via: python -m csv2cte
    run()
