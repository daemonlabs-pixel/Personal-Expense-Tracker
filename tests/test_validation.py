import unittest
from datetime import date

from tracker.validation import (
    validate_amount,
    validate_currency,
    validate_category_id,
    validate_category_name,
    validate_description,
    validate_date,
    validate_transaction_id,
    validate_transaction_type,
)


class Test_validation(unittest.TestCase):

    # Currency tests

    def test_validate_currency_accepts_supported_currencies(self):
        for currency in ("XOF", "EUR", "USD"):
            with self.subTest(currency=currency):
                self.assertEqual(validate_currency(currency), currency)

    def test_validate_currency_normalizes_input(self):
        self.assertEqual(validate_currency(" eur "), "EUR")

    def test_validate_currency_rejects_non_string(self):
        with self.assertRaises(ValueError):
            validate_currency(120)

    def test_validate_currency_rejects_unsupported_currency(self):
        with self.assertRaises(ValueError):
            validate_currency("GBP")

    def test_validate_currency_rejects_empty_string(self):
        with self.assertRaises(ValueError):
            validate_currency(" ")

    # Amount tests

    def test_validate_amount_accepts_xof(self):
        self.assertEqual(validate_amount("1500", "XOF"), 1500)

    def test_validate_amount_accepts_eur(self):
        self.assertEqual(validate_amount("12.50", "EUR"), 1250)

    def test_validate_amount_accepts_usd(self):
        self.assertEqual(validate_amount("9.99", "USD"), 999)

    def test_validate_amount_accepts_currency_case_variations(self):
        self.assertEqual(validate_amount("12.50", "eur"), 1250)

    def test_validate_amount_rejects_non_string(self):
        with self.assertRaises(TypeError):
            validate_amount(12, "XOF")

    def test_validate_amount_rejects_invalid_numeric_string(self):
        for amount in ("x", "1.em", ""):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    validate_amount(amount, "XOF")

    def test_validate_amount_rejects_non_finite_values(self):
        for amount in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    validate_amount(amount, "EUR")

    def test_validate_amount_rejects_zero_and_negative(self):
        for amount in ("0", "-1", "-0.01"):
            with self.subTest(amount=amount):
                with self.assertRaises(ValueError):
                    validate_amount(amount, "EUR")

    def test_validate_amount_rejects_decimal_xof(self):
        with self.assertRaises(ValueError):
            validate_amount("12.50", "XOF")

    def test_validate_amount_rejects_more_than_two_decimal_places(self):
        with self.assertRaises(ValueError):
            validate_amount("12.345", "EUR")

    def test_validate_amount_rejects_invalid_currency(self):
        with self.assertRaises(ValueError):
            validate_amount("12.50", "GBP")

    # Transaction type tests

    def test_validate_transaction_type_accepts_valid_types(self):
        self.assertEqual(validate_transaction_type("income"), "income")
        self.assertEqual(validate_transaction_type("expense"), "expense")

    def test_validate_transaction_type_normalizes_input(self):
        self.assertEqual(validate_transaction_type(" INCOME "), "income")
        self.assertEqual(validate_transaction_type("Expense"), "expense")

    def test_validate_transaction_type_rejects_non_string(self):
        with self.assertRaises(TypeError):
            validate_transaction_type(12)

    def test_validate_transaction_type_rejects_invalid_value(self):
        with self.assertRaises(ValueError):
            validate_transaction_type("curry")

    def test_validate_transaction_type_rejects_empty_string(self):
        with self.assertRaises(ValueError):
            validate_transaction_type(" ")

    # Date tests

    def test_validate_date_defaults_to_today(self):
        self.assertEqual(validate_date(), date.today().isoformat())

    def test_validate_date_accepts_none(self):
        self.assertEqual(validate_date(None), date.today().isoformat())

    def test_validate_date_accepts_valid_iso_date(self):
        self.assertEqual(validate_date("2026-03-14"), "2026-03-14")

    def test_validate_date_rejects_non_string(self):
        with self.assertRaises(TypeError):
            validate_date(12)

    def test_validate_date_rejects_invalid_format(self):
        with self.assertRaises(ValueError):
            validate_date("03-14-2026")

    def test_validate_date_rejects_impossible_calendar_date(self):
        with self.assertRaises(ValueError):
            validate_date("2026-02-30")

    # Category name tests

    def test_validate_category_name_strips_whitespace(self):
        self.assertEqual(validate_category_name(" Food "), "Food")

    def test_validate_category_name_rejects_non_string(self):
        with self.assertRaises(TypeError):
            validate_category_name(12)

    def test_validate_category_name_rejects_empty_name(self):
        with self.assertRaises(ValueError):
            validate_category_name("")

    def test_validate_category_name_rejects_whitespace_only_name(self):
        with self.assertRaises(ValueError):
            validate_category_name("   ")

    # Description tests

    def test_validate_description_accepts_none(self):
        self.assertIsNone(validate_description(None))

    def test_validate_description_rejects_non_string(self):
        with self.assertRaises(TypeError):
            validate_description(12)

    def test_validate_description_converts_empty_to_none(self):
        self.assertIsNone(validate_description(""))

    def test_validate_description_converts_whitespace_to_none(self):
        self.assertIsNone(validate_description("   "))

    def test_validate_description_strips_whitespace(self):
        self.assertEqual(
            validate_description(" Clothing for the family "),
            "Clothing for the family",
        )

    # Category ID tests

    def test_validate_category_id_accepts_positive_integer(self):
        self.assertEqual(validate_category_id(1), 1)

    def test_validate_category_id_rejects_non_integer(self):
        for category_id in ("12", 1.5, True):
            with self.subTest(category_id=category_id):
                with self.assertRaises(TypeError):
                    validate_category_id(category_id)

    def test_validate_category_id_rejects_zero_and_negative(self):
        for category_id in (0, -10):
            with self.subTest(category_id=category_id):
                with self.assertRaises(ValueError):
                    validate_category_id(category_id)

    # Transaction ID tests

    def test_validate_transaction_id_accepts_positive_integer(self):
        self.assertEqual(validate_transaction_id(2), 2)

    def test_validate_transaction_id_rejects_non_integer(self):
        for transaction_id in ("12", 1.5, True):
            with self.subTest(transaction_id=transaction_id):
                with self.assertRaises(TypeError):
                    validate_transaction_id(transaction_id)

    def test_validate_transaction_id_rejects_zero_and_negative(self):
        for transaction_id in (0, -1):
            with self.subTest(transaction_id=transaction_id):
                with self.assertRaises(ValueError):
                    validate_transaction_id(transaction_id)
