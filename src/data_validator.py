"""Utilities for validating and cleaning raw e-commerce transaction data.

This module provides a simple first-pass ingestion workflow:
1. Validate raw transaction strings.
2. Clean and structure valid records into tuples.
3. Recursively calculate total sales from cleaned transactions.
"""

from __future__ import annotations


# Lambda function required by the task to extract the transaction ID.
extract_transaction_id = lambda transaction: transaction[0]


def validate_transaction(record: str) -> bool:
    """Validate a raw transaction record.

    A valid transaction must contain exactly four comma-separated fields:
    transaction ID, amount, region, and date. This function also confirms
    that none of the fields are empty and that the amount can be converted
    to a float.

    Parameters:
        record: A raw transaction string such as
            'ID-1234, 150.50, US, 2023-10-01'.

    Returns:
        True if the record matches the expected structure and contains a
        numeric amount; otherwise, False.
    """
    fields = record.split(",")

    if len(fields) != 4:
        return False

    cleaned_fields = [field.strip() for field in fields]

    if "" in cleaned_fields:
        return False

    try:
        float(cleaned_fields[1])
    except ValueError:
        return False
    else:
        return True


def clean_and_structure(raw_data_list: list[str]) -> list[tuple[str, float, str, str]]:
    """Clean raw transaction strings and structure valid records.

    The function loops through each raw transaction string, validates it,
    trims extra whitespace, converts the amount to a float, and stores
    valid transactions as tuples in the form:
    (transaction_id, amount, region, date).

    Parameters:
        raw_data_list: A list of raw transaction strings.

    Returns:
        A list of structured tuples for all valid transactions.
    """
    clean_transactions: list[tuple[str, float, str, str]] = []

    for record in raw_data_list:
        if validate_transaction(record):
            transaction_id, amount_text, region, date = [
                field.strip() for field in record.split(",")
            ]
            structured_record = (
                transaction_id,
                float(amount_text),
                region,
                date,
            )
            clean_transactions.append(structured_record)

    return clean_transactions


def calculate_total_sales(transaction_list: list[tuple[str, float, str, str]]) -> float:
    """Recursively calculate the total sales amount.

    Parameters:
        transaction_list: A list of cleaned transaction tuples in the form
            (transaction_id, amount, region, date).

    Returns:
        The sum of all transaction amounts as a float.
    """
    if not transaction_list:
        return 0.0

    current_amount = transaction_list[0][1]
    remaining_total = calculate_total_sales(transaction_list[1:])
    return current_amount + remaining_total


