from pathlib import Path
import unittest
import tempfile
import sqlite3

from database.connection import get_connection, initialize_database


class Test_database(unittest.TestCase):

    def test_initialize_creates_tables(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "expenses.db"
            initialize_database(db_path)

            conn = None
            try:
                conn = get_connection(db_path)
                cursor = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                )
                result = cursor.fetchall()
                table_result = [row[0] for row in result]

                self.assertIn("categories", table_result)
                self.assertIn("transactions", table_result)
            finally:
                if conn is not None:
                    conn.close()

    def test_initialize_preserves_existing_data(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "expenses.db"
            initialize_database(db_path)

            conn = None
            try:
                conn = get_connection(db_path)
                conn.execute(
                    "INSERT INTO categories (name) VALUES (?)",
                    ("Food",)
                )
                conn.commit()
            finally:
                if conn is not None:
                    conn.close()

            initialize_database(db_path)

            conn = None
            try:
                conn = get_connection(db_path)
                cursor = conn.execute(
                    "SELECT name FROM categories WHERE name = ?",
                    ("Food",)
                )
                result = cursor.fetchone()

                self.assertIsNotNone(result)
                self.assertEqual("Food", result[0])
            finally:
                if conn is not None:
                    conn.close()

    def test_foreign_keys_are_enabled(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "expenses.db"
            conn = None

            try:
                conn = get_connection(db_path)
                cursor = conn.execute("PRAGMA foreign_keys")
                result = cursor.fetchone()

                self.assertEqual(1, result[0])
            finally:
                if conn is not None:
                    conn.close()

    def test_transaction_rejects_nonexistent_category(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "expenses.db"
            initialize_database(db_path)

            conn = None
            try:
                conn = get_connection(db_path)

                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        """
                        INSERT INTO transactions
                        (amount, transaction_type, category_id, date, currency_code)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (1000, "expense", 999, "2026-10-17", "XOF")
                    )
            finally:
                if conn is not None:
                    conn.close()

    def test_category_deletion_restricted_when_in_use(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "expenses.db"
            initialize_database(db_path)

            conn = None
            try:
                conn = get_connection(db_path)
                cursor = conn.execute(
                    "INSERT INTO categories (name) VALUES (?)",
                    ("Food",)
                )
                category_id = cursor.lastrowid
                conn.commit()

                conn.execute(
                    """
                    INSERT INTO transactions
                    (amount, transaction_type, category_id, date, currency_code)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (1000, "expense", category_id, "2026-10-17", "XOF")
                )
                conn.commit()

                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        "DELETE FROM categories WHERE id = ?",
                        (category_id,)
                    )
            finally:
                if conn is not None:
                    conn.close()

    def test_transaction_rejects_invalid_date_format(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "expenses.db"
            initialize_database(db_path)

            conn = None
            try:
                conn = get_connection(db_path)
                cursor = conn.execute(
                    "INSERT INTO categories (name) VALUES (?)",
                    ("Salary",)
                )
                category_id = cursor.lastrowid

                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        """
                        INSERT INTO transactions
                        (amount, transaction_type, category_id, date, currency_code)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (25000, "income", category_id, "17-10-2026", "EUR")
                    )
            finally:
                if conn is not None:
                    conn.close()

    def test_transaction_rejects_nonpositive_amount(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "expenses.db"
            initialize_database(db_path)

            conn = None
            try:
                conn = get_connection(db_path)
                cursor = conn.execute(
                    "INSERT INTO categories (name) VALUES (?)",
                    ("Food",)
                )
                category_id = cursor.lastrowid

                for amount in (0, -100):
                    with self.subTest(amount=amount):
                        with self.assertRaises(sqlite3.IntegrityError):
                            conn.execute(
                                """
                                INSERT INTO transactions
                                (amount, transaction_type, category_id, date, currency_code)
                                VALUES (?, ?, ?, ?, ?)
                                """,
                                (amount, "expense", category_id,
                                 "2026-10-17", "XOF")
                            )
            finally:
                if conn is not None:
                    conn.close()

    def test_transaction_rejects_invalid_type(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "expenses.db"
            initialize_database(db_path)

            conn = None
            try:
                conn = get_connection(db_path)
                cursor = conn.execute(
                    "INSERT INTO categories (name) VALUES (?)",
                    ("Food",)
                )
                category_id = cursor.lastrowid

                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        """
                        INSERT INTO transactions
                        (amount, transaction_type, category_id, date, currency_code)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (1000, "transfer", category_id,
                         "2026-10-17", "XOF")
                    )
            finally:
                if conn is not None:
                    conn.close()

    def test_transaction_rejects_unsupported_currency(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "expenses.db"
            initialize_database(db_path)

            conn = None
            try:
                conn = get_connection(db_path)
                cursor = conn.execute(
                    "INSERT INTO categories (name) VALUES (?)",
                    ("Food",)
                )
                category_id = cursor.lastrowid

                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        """
                        INSERT INTO transactions
                        (amount, transaction_type, category_id, date, currency_code)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (1000, "expense", category_id,
                         "2026-10-17", "GBP")
                    )
            finally:
                if conn is not None:
                    conn.close()

    def test_category_name_is_case_insensitive_unique(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "expenses.db"
            initialize_database(db_path)

            conn = None
            try:
                conn = get_connection(db_path)
                conn.execute(
                    "INSERT INTO categories (name) VALUES (?)",
                    ("Food",)
                )

                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(
                        "INSERT INTO categories (name) VALUES (?)",
                        ("food",)
                    )
            finally:
                if conn is not None:
                    conn.close()
