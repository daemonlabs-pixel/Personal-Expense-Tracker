import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from database.connection import initialize_database
from tracker.categories import create_category
from tracker.transactions import create_transaction, CategoryNonExistentError
from tracker.summaries import (
    get_totals,
    get_income_total,
    get_expense_total,
    get_balance,
)


class TestSummaries(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_expenses.db"
        initialize_database(self.db_path)

        self.db_patch = patch(
            "database.connection.expenses_db_path",
            self.db_path,
        )
        self.db_patch.start()

        self.food = create_category("Food")
        self.transport = create_category("Transport")

    def tearDown(self):
        self.db_patch.stop()
        self.temp_dir.cleanup()

    def add_transaction(
        self,
        amount,
        transaction_type,
        category_id=None,
        date="2026-10-15",
        currency_code="XOF",
    ):
        if category_id is None:
            category_id = self.food["id"]

        return create_transaction(
            amount=str(amount),
            transaction_type=transaction_type,
            category_id=category_id,
            date=date,
            currency_code=currency_code,
        )

    def add_sample_transactions(self):
        self.add_transaction("10000", "income", date="2026-10-01")
        self.add_transaction("3000", "expense", date="2026-10-05")
        self.add_transaction("5000", "income", date="2026-10-10")
        self.add_transaction("2000", "expense", date="2026-10-20")

    # get_totals tests

    def test_get_totals_calculates_income_expense_and_balance(self):
        self.add_sample_transactions()

        self.assertEqual(
            get_totals("XOF"),
            {
                "currency_code": "XOF",
                "income_minor": 15000,
                "expense_minor": 5000,
                "balance_minor": 10000,
            },
        )

    def test_get_totals_returns_zero_when_no_transactions(self):
        self.assertEqual(
            get_totals("XOF"),
            {
                "currency_code": "XOF",
                "income_minor": 0,
                "expense_minor": 0,
                "balance_minor": 0,
            },
        )

    def test_get_totals_filters_by_category(self):
        self.add_transaction("10000", "income", self.food["id"])
        self.add_transaction("3000", "expense", self.transport["id"])

        self.assertEqual(
            get_totals("XOF", category_id=self.food["id"]),
            {
                "currency_code": "XOF",
                "income_minor": 10000,
                "expense_minor": 0,
                "balance_minor": 10000,
            },
        )

    def test_get_totals_filters_by_currency(self):
        self.add_transaction("10000", "income", currency_code="XOF")
        self.add_transaction("12.50", "expense", currency_code="EUR")

        self.assertEqual(
            get_totals("EUR"),
            {
                "currency_code": "EUR",
                "income_minor": 0,
                "expense_minor": 1250,
                "balance_minor": -1250,
            },
        )

    def test_get_totals_filters_by_date_range(self):
        self.add_transaction("10000", "income", date="2026-10-01")
        self.add_transaction("3000", "expense", date="2026-10-15")
        self.add_transaction("5000", "income", date="2026-10-30")

        self.assertEqual(
            get_totals(
                "XOF",
                start_date="2026-10-10",
                end_date="2026-10-20",
            ),
            {
                "currency_code": "XOF",
                "income_minor": 0,
                "expense_minor": 3000,
                "balance_minor": -3000,
            },
        )

    def test_get_totals_rejects_invalid_currency(self):
        with self.assertRaises(ValueError):
            get_totals("GBP")

    def test_get_totals_rejects_missing_category(self):
        with self.assertRaises(CategoryNonExistentError):
            get_totals("XOF", category_id=999)

    def test_get_totals_rejects_start_date_after_end_date(self):
        with self.assertRaises(ValueError):
            get_totals(
                "XOF",
                start_date="2026-10-20",
                end_date="2026-10-10",
            )

    # get_income_total tests

    def test_get_income_total(self):
        self.add_sample_transactions()
        self.assertEqual(get_income_total("XOF"), 15000)

    def test_get_income_total_returns_zero_when_no_income(self):
        self.add_transaction("3000", "expense")
        self.assertEqual(get_income_total("XOF"), 0)

    def test_get_income_total_filters_by_category(self):
        self.add_transaction("10000", "income", self.food["id"])
        self.add_transaction("5000", "income", self.transport["id"])

        self.assertEqual(
            get_income_total("XOF", category_id=self.food["id"]),
            10000,
        )

    def test_get_income_total_filters_by_start_date(self):
        self.add_transaction("10000", "income", date="2026-10-01")
        self.add_transaction("5000", "income", date="2026-10-15")

        self.assertEqual(
            get_income_total("XOF", start_date="2026-10-10"),
            5000,
        )

    def test_get_income_total_filters_by_end_date(self):
        self.add_transaction("10000", "income", date="2026-10-01")
        self.add_transaction("5000", "income", date="2026-10-15")

        self.assertEqual(
            get_income_total("XOF", end_date="2026-10-10"),
            10000,
        )

    def test_get_income_total_rejects_missing_category(self):
        with self.assertRaises(CategoryNonExistentError):
            get_income_total("XOF", category_id=999)

    # get_expense_total tests

    def test_get_expense_total(self):
        self.add_sample_transactions()
        self.assertEqual(get_expense_total("XOF"), 5000)

    def test_get_expense_total_returns_zero_when_no_expenses(self):
        self.add_transaction("3000", "income")
        self.assertEqual(get_expense_total("XOF"), 0)

    def test_get_expense_total_filters_by_category(self):
        self.add_transaction("3000", "expense", self.food["id"])
        self.add_transaction("2000", "expense", self.transport["id"])

        self.assertEqual(
            get_expense_total("XOF", category_id=self.food["id"]),
            3000,
        )

    def test_get_expense_total_filters_by_date_range(self):
        self.add_transaction("3000", "expense", date="2026-10-05")
        self.add_transaction("2000", "expense", date="2026-10-15")
        self.add_transaction("1000", "expense", date="2026-10-25")

        self.assertEqual(
            get_expense_total(
                "XOF",
                start_date="2026-10-10",
                end_date="2026-10-20",
            ),
            2000,
        )

    def test_get_expense_total_rejects_missing_category(self):
        with self.assertRaises(CategoryNonExistentError):
            get_expense_total("XOF", category_id=999)

    # get_balance tests

    def test_get_balance(self):
        self.add_sample_transactions()
        self.assertEqual(get_balance("XOF"), 10000)

    def test_get_balance_can_be_negative(self):
        self.add_transaction("2000", "income")
        self.add_transaction("5000", "expense")
        self.assertEqual(get_balance("XOF"), -3000)

    def test_get_balance_returns_zero_when_no_transactions(self):
        self.assertEqual(get_balance("XOF"), 0)

    def test_get_balance_filters_by_category(self):
        self.add_transaction("10000", "income", self.food["id"])
        self.add_transaction("3000", "expense", self.food["id"])
        self.add_transaction("5000", "income", self.transport["id"])

        self.assertEqual(
            get_balance("XOF", category_id=self.food["id"]),
            7000,
        )
