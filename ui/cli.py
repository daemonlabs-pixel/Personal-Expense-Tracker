
from decimal import Decimal
from sqlite3 import IntegrityError

from tracker.categories import (
    create_category,
    delete_category,
    list_categories,
    update_category,
    DuplicateCategoryError,
    CategoryInUseError,
)

from tracker.transactions import (
    create_transaction,
    delete_transaction,
    list_transactions,
    update_transaction,
    get_transaction,
    CategoryNonExistentError,
)

from tracker.summaries import (
    get_totals,
    get_expense_total,
    get_income_total,
    get_balance,
)


# --------------------------------------------------
# MONEY FORMATTING
# --------------------------------------------------

def format_money(amount: int, currency_code: str) -> str:
    """Format a stored integer amount for display."""
    if currency_code == "XOF":
        return f"{amount:,} XOF"

    # EUR and USD are stored in cents.
    major_units = Decimal(amount) / Decimal("100")
    return f"{major_units:,.2f} {currency_code}"


def amount_to_input(amount: int, currency_code: str) -> str:
    """Convert a stored amount into a string suitable for backend input."""
    if currency_code == "XOF":
        return str(amount)

    # Convert stored cents back into a decimal amount.
    major_units = Decimal(amount) / Decimal("100")
    return f"{major_units:.2f}"


def get_categories_by_id() -> dict:
    """Build a mapping from category IDs to category names."""
    return {
        category["id"]: category["name"]
        for category in list_categories()
    }


def display_transaction(
    transaction: dict,
    categories_by_id: dict | None = None,
) -> None:
    """Display a transaction in a readable format."""
    if categories_by_id is None:
        categories_by_id = get_categories_by_id()

    category_name = categories_by_id.get(
        transaction["category_id"],
        "Unknown category",
    )

    print(f"Transaction ID: {transaction['id']}")
    print(f"Amount: {format_money(transaction['amount'], transaction['currency_code'])}")
    print(f"Type: {transaction['transaction_type']}")
    print(f"Category: {category_name} (ID: {transaction['category_id']})")
    print(f"Description: {transaction['description'] or 'None'}")
    print(f"Date: {transaction['date']}")
    print(f"Currency: {transaction['currency_code']}")


def collect_summary_filters() -> tuple:
    """Collect the optional filters used by the summary functions."""
    currency_code = input(
        "Currency [XOF]: "
    ).strip() or "XOF"

    start_date = input(
        "Start date (YYYY-MM-DD, optional): "
    ).strip() or None

    end_date = input(
        "End date (YYYY-MM-DD, optional): "
    ).strip() or None

    category_input = input(
        "Category ID (optional): "
    ).strip()

    category_id = int(category_input) if category_input else None

    return currency_code, start_date, end_date, category_id


# --------------------------------------------------
# MAIN MENU
# --------------------------------------------------

def display_menu():
    print("\n---- PERSONAL EXPENSE TRACKER ----")
    print("1. Create category")
    print("2. View categories")
    print("3. Rename category")
    print("4. Delete category")
    print("5. Add transaction")
    print("6. List transactions")
    print("7. View transaction details")
    print("8. Edit transaction")
    print("9. Delete transaction")
    print("10. View financial summary")
    print("0. Exit")


def run_cli():
    while True:
        display_menu()
        choice = input("Enter your choice (0-10): ").strip()

        match choice:
            case "1":
                create_category_menu()
            case "2":
                view_categories_menu()
            case "3":
                rename_category_menu()
            case "4":
                delete_category_menu()
            case "5":
                add_transaction_menu()
            case "6":
                list_transactions_menu()
            case "7":
                view_transaction_menu()
            case "8":
                edit_transaction_menu()
            case "9":
                delete_transaction_menu()
            case "10":
                view_summary_menu()
            case "0":
                print("Exiting Expense Tracker. See you later!")
                break
            case _:
                print("Invalid choice. Please enter a number between 0 and 10.")


# --------------------------------------------------
# CATEGORY MENUS
# --------------------------------------------------

def create_category_menu():
    category_name = input("Enter the category name: ")

    try:
        category = create_category(category_name)

        print(
            f"Category created successfully: "
            f"ID: {category['id']}, name :'{category['name']}'."
        )

    except DuplicateCategoryError as error:
        print(f"Creation failed: {error}")

    except (ValueError, TypeError) as error:
        print(f"Creation failed: Invalid category name. {error}")


def view_categories_menu():
    categories = list_categories()

    if not categories:
        print("No categories found.")
        return

    print(f"\nTotal categories: {len(categories)}")
    print("Categories:")

    for category in categories:
        print(f"ID: {category['id']} | Name: {category['name']}")


def rename_category_menu():
    try:
        category_id = int(input("Enter the category ID: "))
        new_name = input("Enter the new category name: ")

        category = update_category(category_id, new_name)

        if category is None:
            print("Renaming failed: No category exists with that ID.")
        else:
            print(
                f"Category renamed successfully: "
                f"ID: {category['id']}, name: '{category['name']}'."
            )

    except DuplicateCategoryError as error:
        print(f"Renaming failed: {error}")

    except (ValueError, TypeError) as error:
        print(f"Renaming failed: Invalid ID or category name. {error}")


def delete_category_menu():
    try:
        category_id = int(input("Enter the category ID to delete: "))

        category = next(
            (
                item for item in list_categories()
                if item["id"] == category_id
            ),
            None,
        )

        if category is None:
            print("Deletion failed: No category exists with that ID.")
            return

        print(f"Selected category: {category['name']}")
        confirmation = input("Delete this category? (y/n): ").strip().lower()

        if confirmation != "y":
            print("Deletion cancelled.")
            return

        deleted = delete_category(category_id)

        if deleted:
            print("Category deleted successfully.")
        else:
            print("Deletion failed: The category no longer exists.")

    except CategoryInUseError as error:
        print(f"Deletion failed: {error}")

    except (ValueError, TypeError) as error:
        print(f"Deletion failed: Invalid category ID. {error}")


# --------------------------------------------------
# TRANSACTION MENUS
# --------------------------------------------------

def add_transaction_menu():
    # A transaction must reference an existing category.
    categories = list_categories()

    if not categories:
        print("You must create a category before adding a transaction.")
        return

    print("\nAvailable categories:")
    for category in categories:
        print(f"ID: {category['id']} | Name: {category['name']}")

    amount = input("Enter the amount: ").strip()
    transaction_type = input(
        "Transaction type (income/expense): "
    ).strip()

    category_input = input("Enter the category ID: ").strip()
    description = input("Description (optional): ").strip() or None
    date = input("Date (YYYY-MM-DD, blank for today): ").strip() or None
    currency_code = input("Currency [XOF]: ").strip() or "XOF"

    try:
        category_id = int(category_input)

        # The backend validates and converts the amount.
        transaction = create_transaction(
            amount=amount,
            transaction_type=transaction_type,
            category_id=category_id,
            description=description,
            date=date,
            currency_code=currency_code,
        )

        print("\nTransaction created successfully.")
        display_transaction(transaction)

    except CategoryNonExistentError as error:
        print(f"Creation failed: {error}")

    except IntegrityError as error:
        print(f"Creation failed because of a database constraint: {error}")

    except (ValueError, TypeError) as error:
        print(f"Creation failed: Invalid transaction details. {error}")


def list_transactions_menu():
    print("Leave optional filters blank to include all values.")

    category_input = input("Category ID (optional): ").strip()
    transaction_type = input("Transaction type (optional): ").strip() or None
    start_date = input("Start date (optional): ").strip() or None
    end_date = input("End date (optional): ").strip() or None
    currency_code = input("Currency (optional): ").strip() or None

    try:
        category_id = int(category_input) if category_input else None

        transactions = list_transactions(
            category_id=category_id,
            transaction_type=transaction_type,
            start_date=start_date,
            end_date=end_date,
            currency_code=currency_code,
        )

        if not transactions:
            print("No transactions found for the selected filters.")
            return

        categories_by_id = get_categories_by_id()

        print(f"\nTransactions found: {len(transactions)}")

        for transaction in transactions:
            print("\n------------------------------")
            display_transaction(transaction, categories_by_id)

    except CategoryNonExistentError as error:
        print(f"Listing failed: {error}")

    except (ValueError, TypeError) as error:
        print(f"Listing failed: Invalid filter. {error}")


def view_transaction_menu():
    try:
        transaction_id = int(input("Enter the transaction ID: "))
        transaction = get_transaction(transaction_id)

        if transaction is None:
            print("No transaction exists with that ID.")
            return

        display_transaction(transaction)

    except (ValueError, TypeError) as error:
        print(f"Viewing failed: Invalid transaction ID. {error}")


def edit_transaction_menu():
    try:
        transaction_id = int(input("Enter the transaction ID to edit: "))
        current = get_transaction(transaction_id)

        if current is None:
            print("Editing failed: No transaction exists with that ID.")
            return

        print("\nCurrent transaction:")
        display_transaction(current)

        print("\nPress Enter to keep each existing value.")

        currency_input = input(
            f"Currency [{current['currency_code']}]: "
        ).strip()

        currency_code = currency_input or current["currency_code"]

        if currency_code.strip().upper() == current["currency_code"]:
            # Convert the stored value back into a user-entered amount.
            default_amount = amount_to_input(
                current["amount"],
                current["currency_code"],
            )
            amount = input(f"Amount [{default_amount}]: ").strip()
            amount = amount or default_amount
        else:
            # A currency change requires a new amount because the
            # previous stored integer may represent a different unit.
            amount = input(
                f"New amount in {currency_code} (required): "
            ).strip()

        transaction_type = input(
            f"Type [{current['transaction_type']}]: "
        ).strip() or current["transaction_type"]

        category_input = input(
            f"Category ID [{current['category_id']}]: "
        ).strip()

        category_id = (
            int(category_input)
            if category_input
            else current["category_id"]
        )

        description_input = input(
            f"Description [{current['description'] or 'None'}] "
            "(enter '-' to clear): "
        ).strip()

        if description_input == "-":
            description = None
        elif description_input == "":
            description = current["description"]
        else:
            description = description_input

        date = input(
            f"Date [{current['date']}]: "
        ).strip() or current["date"]

        # The backend performs validation and unit conversion.
        updated = update_transaction(
            transaction_id=transaction_id,
            amount=amount,
            transaction_type=transaction_type,
            category_id=category_id,
            description=description,
            date=date,
            currency_code=currency_code,
        )

        if updated is None:
            print("Editing failed: No transaction exists with that ID.")
        else:
            print("\nTransaction updated successfully.")
            display_transaction(updated)

    except CategoryNonExistentError as error:
        print(f"Editing failed: {error}")

    except IntegrityError as error:
        print(f"Editing failed because of a database constraint: {error}")

    except (ValueError, TypeError) as error:
        print(f"Editing failed: Invalid transaction details. {error}")


def delete_transaction_menu():
    try:
        transaction_id = int(input("Enter the transaction ID to delete: "))
        transaction = get_transaction(transaction_id)

        if transaction is None:
            print("Deletion failed: No transaction exists with that ID.")
            return

        print("\nTransaction selected for deletion:")
        display_transaction(transaction)

        confirmation = input(
            "Delete this transaction? (y/n): "
        ).strip().lower()

        if confirmation != "y":
            print("Deletion cancelled.")
            return

        deleted = delete_transaction(transaction_id)

        if deleted:
            print("Transaction deleted successfully.")
        else:
            print("Deletion failed: The transaction no longer exists.")

    except (ValueError, TypeError) as error:
        print(f"Deletion failed: Invalid transaction ID. {error}")

    except IntegrityError as error:
        print(f"Deletion failed because of a database constraint: {error}")


# --------------------------------------------------
# FINANCIAL SUMMARY MENU
# --------------------------------------------------

def view_summary_menu():
    while True:
        print("\n---- FINANCIAL SUMMARY ----")
        print("1. View complete summary")
        print("2. View total income")
        print("3. View total expenses")
        print("4. View balance")
        print("0. Return to main menu")

        choice = input("Enter your choice (0-4): ").strip()

        if choice == "0":
            return

        if choice not in {"1", "2", "3", "4"}:
            print("Invalid choice. Please enter a number between 0 and 4.")
            continue

        try:
            currency_code, start_date, end_date, category_id = (
                collect_summary_filters()
            )

            if choice == "1":
                totals = get_totals(
                    currency_code=currency_code,
                    start_date=start_date,
                    end_date=end_date,
                    category_id=category_id,
                )

                print("\nComplete financial summary:")
                print(
                    f"Income: "
                    f"{format_money(totals['income_minor'], totals['currency_code'])}"
                )
                print(
                    f"Expenses: "
                    f"{format_money(totals['expense_minor'], totals['currency_code'])}"
                )
                print(
                    f"Balance: "
                    f"{format_money(totals['balance_minor'], totals['currency_code'])}"
                )

            elif choice == "2":
                total = get_income_total(
                    currency_code,
                    start_date,
                    end_date,
                    category_id,
                )
                print(f"Total income: {format_money(total, currency_code.upper())}")

            elif choice == "3":
                total = get_expense_total(
                    currency_code,
                    start_date,
                    end_date,
                    category_id,
                )
                print(f"Total expenses: {format_money(total, currency_code.upper())}")

            elif choice == "4":
                balance = get_balance(
                    currency_code,
                    start_date,
                    end_date,
                    category_id,
                )
                print(f"Balance: {format_money(balance, currency_code.upper())}")

        except CategoryNonExistentError as error:
            print(f"Summary failed: {error}")

        except (ValueError, TypeError) as error:
            print(f"Summary failed: Invalid filter. {error}")
