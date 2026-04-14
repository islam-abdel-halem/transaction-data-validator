"""Object-oriented models for processed e-commerce transaction data.

This module defines transaction classes and a loader class that reads
structured transaction records from ``processed_data.txt`` and converts
them into Python objects for easier reuse and maintenance.
"""

from __future__ import annotations

import json
from pathlib import Path


class Transaction:
    """Represent a basic e-commerce transaction.

    Attributes are stored with protected naming conventions to encourage
    interaction through methods rather than direct attribute access.
    """

    def __init__(self, transaction_id: str, amount: float, region: str, date: str) -> None:
        """Initialize a transaction object.

        Parameters:
            transaction_id: The unique transaction identifier.
            amount: The monetary value of the transaction.
            region: The geographic region associated with the transaction.
            date: The transaction date as a string.
        """
        self._id = transaction_id
        self._amount = amount
        self._region = region
        self._date = date

    def get_details(self) -> str:
        """Return a formatted description of the transaction.

        Returns:
            A human-readable string containing the transaction details.
        """
        return (
            f"Transaction ID: {self._id}, "
            f"Amount: {self._amount:.2f}, "
            f"Region: {self._region}, "
            f"Date: {self._date}"
        )


class InternationalTransaction(Transaction):
    """Represent a transaction that includes international currency metadata."""

    def __init__(
        self,
        transaction_id: str,
        amount: float,
        region: str,
        date: str,
        currency_code: str,
    ) -> None:
        """Initialize an international transaction object.

        Parameters:
            transaction_id: The unique transaction identifier.
            amount: The monetary value of the transaction.
            region: The geographic region associated with the transaction.
            date: The transaction date as a string.
            currency_code: The currency code assigned to the transaction.
        """
        super().__init__(transaction_id, amount, region, date)
        self._currency_code = currency_code

    def get_details(self) -> str:
        """Return a formatted description including the currency code.

        Returns:
            A human-readable string containing the international
            transaction details.
        """
        return f"{super().get_details()}, Currency Code: {self._currency_code}"


class DataLoader:
    """Load processed transaction records and convert them into objects."""

    def __init__(self, filepath: str) -> None:
        """Initialize the loader with a processed data file path.

        Parameters:
            filepath: Path to the processed transaction data file.
        """
        self._filepath = filepath
        self._transactions: list[Transaction] = []

    @staticmethod
    def validate_amount(amount: float) -> bool:
        """Check whether a transaction amount is positive.

        Parameters:
            amount: The transaction amount to validate.

        Returns:
            True if the amount is greater than zero; otherwise, False.
        """
        return amount > 0

    @staticmethod
    def _get_currency_code(region: str) -> str:
        """Return a currency code based on region.

        Parameters:
            region: The region code from the processed transaction record.

        Returns:
            A best-effort currency code for the given region.
        """
        currency_by_region = {
            "EU": "EUR",
            "APAC": "JPY",
            "ME": "AED",
            "CA": "CAD",
            "LATAM": "MXN",
        }
        return currency_by_region.get(region, "USD")

    def load_transactions(self) -> list[Transaction]:
        """Read processed data and instantiate transaction objects.

        Domestic transactions from the ``US`` region are loaded as
        ``Transaction`` objects. Non-US transactions are loaded as
        ``InternationalTransaction`` objects with an inferred currency code.

        Returns:
            A list of loaded transaction objects.

        Raises:
            FileNotFoundError: If the processed data file cannot be found.
            json.JSONDecodeError: If the file content is not valid JSON.
        """
        self._transactions = []

        with open(self._filepath, "r", encoding="utf-8") as source_file:
            records = json.load(source_file)

        for record in records:
            amount = float(record["amount"])

            if not self.validate_amount(amount):
                continue

            if record["region"] == "US":
                transaction = Transaction(
                    transaction_id=record["id"],
                    amount=amount,
                    region=record["region"],
                    date=record["date"],
                )
            else:
                transaction = InternationalTransaction(
                    transaction_id=record["id"],
                    amount=amount,
                    region=record["region"],
                    date=record["date"],
                    currency_code=self._get_currency_code(record["region"]),
                )

            self._transactions.append(transaction)

        return self._transactions

    def get_transactions(self) -> list[Transaction]:
        """Return the internal list of loaded transaction objects.

        Returns:
            A list of ``Transaction`` or ``InternationalTransaction`` objects.
        """
        return self._transactions


def main() -> None:
    """Load processed transactions and print their formatted details."""
    processed_path = Path(__file__).with_name("processed_data.txt")
    loader = DataLoader(str(processed_path))
    transactions = loader.load_transactions()

    print(f"Transactions loaded: {len(transactions)}")
    for transaction in transactions:
        print(transaction.get_details())


if __name__ == "__main__":
    main()
