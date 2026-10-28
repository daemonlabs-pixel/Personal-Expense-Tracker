import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from database.connection import initialize_database, get_connection
from tracker.categories import create_category
from tracker.transactions import (
    create_transaction,
    get_transaction,
    list_transactions,
    update_transaction,
    delete_transaction,
    CategoryNonExistentError,
)


class TestTransactions(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_expenses.db"
        initialize_database(self.db_path)

        self.db_patch = patch(
            "database.connection.expenses_db_path",
            self.db_path,
        )
        self.db_patch.start()

        self.category = create_category("Food")
        self.category_id = self.category["id"]

    def tearDown(self):
        self.db_patch.stop()
        self.temp_dir.cleanup()

    def add_transaction(
        self,
        amount="1500",
        transaction_type="expense",
        category_id=None,
        description="Lunch",
        date="2026-10-20",
        currency_code="XOF",
    ):
        if category_id is None:
            category_id = self.category_id

        return create_transaction(
            amount,
            transaction_type,
            category_id,
            description,
            date,
            currency_code,
        )

    # Create tests

    def test_create_transaction(self):
        transaction = self.add_transaction()

        self.assertGreater(transaction["id"], 0)
        self.assertEqual(transaction["amount"], 1500)
        self.assertEqual(transaction["transaction_type"], "expense")
        self.assertEqual(transaction["category_id"], self.category_id)
        self.assertEqual(transaction["description"], "Lunch")
        self.assertEqual(transaction["date"], "2026-10-20")
        self.assertEqual(transaction["currency_code"], "XOF")

    def test_create_transaction_with_eur_amount(self):
        transaction = self.add_transaction(
            amount="12.50",
            currency_code="EUR",
        )

        # EUR amounts are stored as integer cents.
        self.assertEqual(transaction["amount"], 1250)
        self.assertEqual(transaction["currency_code"], "EUR")

    def test_create_transaction_with_default_date(self):
        from datetime import date

        transaction = create_transaction(
            "1000", "expense", self.category_id
        )

        self.assertEqual(transaction["date"], date.today().isoformat())

    def test_create_transaction_with_empty_description(self):
        transaction = self.add_transaction(description="   ")

        self.assertIsNone(transaction["description"])

    def test_create_transaction_rejects_missing_category(self):
        with self.assertRaises(CategoryNonExistentError):
            self.add_transaction(category_id=999)

    def test_create_transaction_rejects_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.add_transaction(amount="0")

    def test_create_transaction_rejects_invalid_type(self):
        with self.assertRaises(ValueError):
            self.add_transaction(transaction_type="transfer")

    def test_create_transaction_rejects_invalid_date(self):
        with self.assertRaises(ValueError):
            self.add_transaction(date="2026-02-30")

    # Get tests

    def test_get_transaction(self):
        created = self.add_transaction()

        self.assertEqual(
            get_transaction(created["id"]),
            created,
        )

    def test_get_transaction_returns_none_when_missing(self):
        self.assertIsNone(get_transaction(999))

    def test_get_transaction_rejects_invalid_id(self):
        with self.assertRaises(TypeError):
            get_transaction("1")

        with self.assertRaises(ValueError):
            get_transaction(0)

    # List tests

    def test_list_transactions_returns_all(self):
        first = self.add_transaction(amount="1000")
        second = self.add_transaction(amount="2000")

        transactions = list_transactions()

        self.assertEqual(len(transactions), 2)
        self.assertIn(first, transactions)
        self.assertIn(second, transactions)

    def test_list_transactions_returns_empty_list(self):
        self.assertEqual(list_transactions(), [])

    def test_list_transactions_filters_by_category(self):
        other_category = create_category("Transport")
        self.add_transaction()
        transport_transaction = self.add_transaction(
            category_id=other_category["id"]
        )

        results = list_transactions(category_id=other_category["id"])

        self.assertEqual(results, [transport_transaction])

    def test_list_transactions_filters_by_type(self):
        self.add_transaction(transaction_type="expense")
        income = self.add_transaction(
            amount="5000",
            transaction_type="income",
        )

        self.assertEqual(list_transactions(transaction_type="income"), [income])

    def test_list_transactions_filters_by_currency(self):
        self.add_transaction(currency_code="XOF")
        eur = self.add_transaction(amount="12.50", currency_code="EUR")

        self.assertEqual(list_transactions(currency_code="EUR"), [eur])

    def test_list_transactions_filters_by_date_range(self):
        self.add_transaction(date="2026-10-01")
        middle = self.add_transaction(date="2026-10-15")
        self.add_transaction(date="2026-10-30")

        results = list_transactions(
            start_date="2026-10-10",
            end_date="2026-10-20",
        )

        self.assertEqual(results, [middle])

    def test_list_transactions_filters_by_start_date(self):
        self.add_transaction(date="2026-10-01")
        later = self.add_transaction(date="2026-10-15")

        self.assertEqual(
            list_transactions(start_date="2026-10-10"),
            [later],
        )

    def test_list_transactions_filters_by_end_date(self):
        earlier = self.add_transaction(date="2026-10-01")
        self.add_transaction(date="2026-10-15")

        self.assertEqual(
            list_transactions(end_date="2026-10-10"),
            [earlier],
        )

    def test_list_transactions_rejects_start_date_after_end_date(self):
        with self.assertRaises(ValueError):
            list_transactions(
                start_date="2026-10-20",
                end_date="2026-10-10",
            )

    def test_list_transactions_rejects_missing_category(self):
        with self.assertRaises(CategoryNonExistentError):
            list_transactions(category_id=999)

    # Update tests

    def test_update_transaction(self):
        created = self.add_transaction()

        updated = update_transaction(
            created["id"],
            "2500",
            "income",
            self.category_id,
            "Refund",
            "2026-10-21",
            "XOF",
        )

        self.assertEqual(
            updated,
            {
                "id": created["id"],
                "amount": 2500,
                "transaction_type": "income",
                "category_id": self.category_id,
                "description": "Refund",
                "date": "2026-10-21",
                "currency_code": "XOF",
            },
        )

        self.assertEqual(get_transaction(created["id"]), updated)

    def test_update_transaction_returns_none_when_missing(self):
        self.assertIsNone(
            update_transaction(
                999,
                "1000",
                "expense",
                self.category_id,
                None,
                "2026-10-20",
                "XOF",
            )
        )

    def test_update_transaction_rejects_missing_category(self):
        created = self.add_transaction()

        with self.assertRaises(CategoryNonExistentError):
            update_transaction(
                created["id"],
                "1000",
                "expense",
                999,
                None,
                "2026-10-20",
                "XOF",
            )

    # Delete tests

    def test_delete_transaction(self):
        created = self.add_transaction()

        self.assertTrue(delete_transaction(created["id"]))
        self.assertIsNone(get_transaction(created["id"]))

    def test_delete_transaction_returns_false_when_missing(self):
        self.assertFalse(delete_transaction(999))

    def test_delete_transaction_rejects_invalid_id(self):
        with self.assertRaises(TypeError):
            delete_transaction("1")

        with self.assertRaises(ValueError):
            delete_transaction(0)
