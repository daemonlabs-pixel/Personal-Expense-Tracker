import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from database.connection import initialize_database
from tracker.categories import (
    create_category,
    get_category,
    list_categories,
    update_category,
    delete_category,
    DuplicateCategoryError,
    CategoryInUseError,
)


class TestCategories(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_expenses.db"

        initialize_database(self.db_path)

        # Redirect the category module's default database to our test database.
        self.db_patch = patch(
            "database.connection.expenses_db_path",
            self.db_path,
        )
        self.db_patch.start()

    def tearDown(self):
        self.db_patch.stop()
        self.temp_dir.cleanup()

    def test_create_category(self):
        category = create_category("Food")

        self.assertIsInstance(category["id"], int)
        self.assertGreater(category["id"], 0)
        self.assertEqual(category["name"], "Food")

    def test_create_category_strips_whitespace(self):
        category = create_category("  Food  ")

        self.assertEqual(category["name"], "Food")

    def test_create_category_rejects_duplicate_name(self):
        create_category("Food")

        with self.assertRaises(DuplicateCategoryError):
            create_category("Food")

    def test_create_category_rejects_case_insensitive_duplicate(self):
        create_category("Food")

        with self.assertRaises(DuplicateCategoryError):
            create_category("food")

    def test_create_category_rejects_invalid_name(self):
        with self.assertRaises(TypeError):
            create_category(123)

        with self.assertRaises(ValueError):
            create_category("   ")

    def test_get_category(self):
        created = create_category("Transport")

        category = get_category(created["id"])

        self.assertEqual(
            category,
            {"id": created["id"], "name": "Transport"},
        )

    def test_get_category_returns_none_for_missing_category(self):
        self.assertIsNone(get_category(999))

    def test_get_category_rejects_invalid_id(self):
        with self.assertRaises(TypeError):
            get_category("1")

        with self.assertRaises(ValueError):
            get_category(0)

    def test_list_categories_returns_all_categories(self):
        food = create_category("Food")
        transport = create_category("Transport")

        categories = list_categories()

        self.assertEqual(len(categories), 2)
        self.assertIn(food, categories)
        self.assertIn(transport, categories)

    def test_list_categories_returns_empty_list(self):
        self.assertEqual(list_categories(), [])

    def test_update_category(self):
        created = create_category("Food")

        updated = update_category(created["id"], "Groceries")

        self.assertEqual(
            updated,
            {"id": created["id"], "name": "Groceries"},
        )

    def test_update_category_returns_none_for_missing_category(self):
        self.assertIsNone(update_category(999, "Food"))

    def test_update_category_rejects_duplicate_name(self):
        create_category("Food")
        transport = create_category("Transport")

        with self.assertRaises(DuplicateCategoryError):
            update_category(transport["id"], "Food")

    def test_update_category_rejects_invalid_name_and_id(self):
        created = create_category("Food")

        with self.assertRaises(ValueError):
            update_category(created["id"], "   ")

        with self.assertRaises(TypeError):
            update_category("1", "Groceries")

    def test_delete_category(self):
        created = create_category("Food")

        result = delete_category(created["id"])

        self.assertTrue(result)
        self.assertIsNone(get_category(created["id"]))

    def test_delete_category_returns_false_for_missing_category(self):
        self.assertFalse(delete_category(999))

    def test_delete_category_rejects_invalid_id(self):
        with self.assertRaises(TypeError):
            delete_category("1")

        with self.assertRaises(ValueError):
            delete_category(0)

    def test_delete_category_rejects_category_in_use(self):
        category = create_category("Food")

        conn = None
        try:
            from database.connection import get_connection

            conn = get_connection()
            conn.execute(
                """
                INSERT INTO transactions
                    (amount, transaction_type, category_id, description,
                     date, currency_code)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (1000, "expense", category["id"], "Lunch",
                 "2026-10-26", "XOF"),
            )
            conn.commit()
        finally:
            if conn is not None:
                conn.close()

        with self.assertRaises(CategoryInUseError):
            delete_category(category["id"])


if __name__ == "__main__":
    unittest.main()
