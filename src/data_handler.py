"""File-based transaction processing utilities for e-commerce data.

This module reads raw transaction records from a text file, validates and
parses each line, stores valid transactions as dictionaries, tracks unique
regions with a set, and writes cleaned results to an output file.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from src.data_validator import validate_transaction

logger = logging.getLogger(__name__)


def parse_transaction_line(line: str) -> dict[str, str | float]:
    """Parse one raw transaction line into a structured dictionary.

    Parameters:
        line: A raw transaction string expected to contain four
            comma-separated fields.

    Returns:
        A dictionary with the keys 'id', 'amount', 'region', and 'date'.

    Raises:
        ValueError: If the transaction format is invalid or the amount
            cannot be converted to a float.
        IndexError: If one of the required fields is missing while parsing.
    """
    if not validate_transaction(line):
        raise ValueError(
            "Record must contain exactly four comma-separated values with "
            "a numeric amount."
        )

    fields = [field.strip() for field in line.split(",")]

    return {
        "id": fields[0],
        "amount": float(fields[1]),
        "region": fields[2],
        "date": fields[3],
    }


def write_processed_data(
    output_path: str, transactions: list[dict[str, str | float]]
) -> None:
    """Write structured transaction data to an output file.

    Parameters:
        output_path: The destination file path for processed data.
        transactions: A list of structured transaction dictionaries.

    Returns:
        None.
    """
    with open(output_path, "w", encoding="utf-8") as output_file:
        json.dump(transactions, output_file, indent=4)


def process_file(filepath: str, output_path: str) -> tuple[list[dict[str, str | float]], set[str]]:
    """Read, validate, and process a raw transaction file.

    The function safely opens the input file, parses valid transaction lines
    into dictionaries, collects unique region values in a set, writes the
    processed transactions to 'output_path', and returns both the
    transactions and unique regions.

    Parameters:
        filepath: The path to the raw transaction text file.
        output_path: The path to output processed JSON records.

    Returns:
        A tuple containing:
        - A list of valid transaction dictionaries.
        - A set of unique regions found in the valid records.
    """
    structured_transactions: list[dict[str, str | float]] = []
    unique_regions: set[str] = set()

    try:
        with open(filepath, "r", encoding="utf-8") as source_file:
            for line_number, raw_line in enumerate(source_file, start=1):
                line = raw_line.strip()

                if not line:
                    continue

                try:
                    transaction = parse_transaction_line(line)
                except (ValueError, IndexError) as error:
                    logger.warning(f"Skipping line {line_number}: {error}")
                    continue

                structured_transactions.append(transaction)
                unique_regions.add(str(transaction["region"]))

        write_processed_data(output_path, structured_transactions)
        return structured_transactions, unique_regions

    except FileNotFoundError:
        logger.error(f"File not found: {filepath}. Please check the file path and try again.")
        return [], set()

    finally:
        logger.info(f"File operation attempt complete for: {filepath}")


