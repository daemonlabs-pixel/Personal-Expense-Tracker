# Personal Expense Tracker

## Overview

Personal Expense Tracker is a command-line application built with Python and SQLite for managing personal income and expenses.

It allows users to organize transactions into categories, filter financial records, and view summaries of their income, expenses, and balance. The application also validates user input and handles invalid operations with error messages.

## Features

### Transaction Management

- Create, view, edit, and delete income and expense transactions.
- Record financial transactions with validated input.

### Category Management

- Create, view, rename, and delete categories.
- Organize transactions by category.
- Prevent deletion of categories associated with existing transactions.

### Transaction Filtering

- Filter transactions by category.
- Filter transactions by transaction type.
- Filter transactions by currency.
- Filter transactions by date range.

### Financial Summaries

- Calculate total income.
- Calculate total expenses.
- View the balance between income and expenses.
- Apply supported filters to financial summaries.

### Input Validation and Error Handling

- Validate user input before processing operations.
- Handle invalid values and operations with appropriate error messages.
- Enforce database constraints to preserve data integrity.

## Technologies

- Python 3.14.8
- SQLite
- Python standard library
- `unittest` for automated testing

## Requirements

- Python 3.14.8 or a compatible Python version.
- No third-party Python packages are currently required.

## Installation and Setup

### 1. Clone the Repository

Clone the repository and navigate to the project directory:

```bash
git clone <repository-url>
cd "Personal Expense Tracker"
```

Replace `<repository-url>` with the URL of your GitHub repository.

### 2. Check Python Installation

Make sure Python is installed:

```bash
python --version
```

Python 3.14.8 is the version used to develop this project.

### 3. Run the Application

From the project root directory, launch the application:

```bash
python app.py
```

The application initializes the database and launches the command-line interface.

## Usage

When you run `python app.py`, the following main menu is displayed:

```text
---- PERSONAL EXPENSE TRACKER ----
1. Create category
2. View categories
3. Rename category
4. Delete category
5. Add transaction
6. List transactions
7. View transaction details
8. Edit transaction
9. Delete transaction
10. View financial summary
0. Exit
```

Enter the number corresponding to the operation you want to perform, then follow the prompts displayed by the application.

### Available Operations

- **Create category:** Create a category to organize transactions.
- **View categories:** Display the available categories.
- **Rename category:** Change the name of an existing category.
- **Delete category:** Remove a category, provided it is not associated with existing transactions.
- **Add transaction:** Record an income or expense transaction.
- **List transactions:** Display transactions, with supported filtering options.
- **View transaction details:** Display the details of a specific transaction.
- **Edit transaction:** Modify an existing transaction.
- **Delete transaction:** Remove a transaction.
- **View financial summary:** Display financial totals, including income, expenses, and balance.
- **Exit:** Close the application.

## Database and Data Storage

The application uses SQLite for local data storage. The database file is located at `data/expenses.db`, relative to the project root.

### Database Initialization

Every time the application starts, `app.py` calls `initialize_database()` to ensure that the database schema is initialized. If the database file does not exist, SQLite creates it automatically, provided that the `data/` directory already exists.

The schema uses `CREATE TABLE IF NOT EXISTS` to avoid recreating existing tables and to preserve stored data.

### Data Persistence

Categories and transactions are stored in the SQLite database and remain available after the application is closed and restarted. Database changes are committed to save successful operations.

### Data Management

- **Category deletion:** Categories associated with existing transactions cannot be deleted. The application prevents their deletion to preserve data integrity.
- **Transaction deletion:** Successfully deleted transactions are permanently removed from the database under normal operation.
- **Data integrity:** Database constraints enforce valid transaction types, positive amounts, supported currencies, unique category names, and valid relationships between categories and transactions.

The local database file is excluded from version control to avoid publishing personal financial records.

## Testing

The project includes an automated test suite built with Python's built-in `unittest` framework.

### Running the Tests

From the project root directory, run:

```bash
python -m unittest discover -s tests -v
```

### Test Coverage

The test suite covers:

- Database initialization, schema constraints, and data persistence.
- Category creation, retrieval, updates, and deletion.
- Transaction creation, retrieval, updates, deletion, and filtering.
- Input validation for amounts, currencies, dates, descriptions, categories, and transaction IDs.
- Financial summaries, including income, expenses, and balance calculations.
- Error handling for invalid inputs and operations.

### Test Results

The test suite was executed successfully, with all 120 tests passing.

```text
Ran 120 tests in 5.518s

OK
```

The execution time may vary depending on the machine and environment.

## Project Structure

```text
Personal Expense Tracker/
├── app.py
├── database/
│   ├── __init__.py
│   ├── connection.py
│   └── schema.sql
├── tracker/
│   ├── __init__.py
│   ├── categories.py
│   ├── transactions.py
│   ├── summaries.py
│   └── validation.py
├── ui/
│   ├── __init__.py
│   └── cli.py
├── tests/
│   ├── __init__.py
│   ├── test_categories.py
│   ├── test_database.py
│   ├── test_summaries.py
│   ├── test_transactions.py
│   └── test_validation.py
├── data/
│   └── .gitkeep
├── .gitignore
├── README.md
└── requirements.txt
```

### File Responsibilities

#### Application Entry Point

- **`app.py`**: Initializes the database and launches the command-line interface.

#### Database

- **`database/connection.py`**: Manages SQLite database connections and initializes the database using the SQL schema.
- **`database/schema.sql`**: Defines the database structure, including the categories and transactions tables, constraints, and relationships.
- **`database/__init__.py`**: Marks the database directory as a Python package.

#### Business Logic

- **`tracker/categories.py`**: Handles category management, including creating, retrieving, listing, renaming, and deleting categories, with appropriate error handling.
- **`tracker/transactions.py`**: Handles income and expense transactions, including creating, retrieving, listing, updating, and deleting transactions, with filtering options.
- **`tracker/summaries.py`**: Calculates financial summaries, including total income, total expenses, and balance, with optional currency, date range, and category filters.
- **`tracker/validation.py`**: Validates user input, including transaction amounts, currencies, dates, transaction types, descriptions, category names, and IDs.
- **`tracker/__init__.py`**: Marks the tracker directory as a Python package.

#### User Interface

- **`ui/cli.py`**: Provides the command-line interface through which users interact with the application, enter information, and view results and error messages.
- **`ui/__init__.py`**: Marks the UI directory as a Python package.

#### Automated Tests

The `tests/` directory contains automated tests for database operations, category management, transaction management, input validation, and financial summaries.

- **`tests/test_database.py`**: Tests database initialization and database-related behavior.
- **`tests/test_categories.py`**: Tests category management operations and category-related validation and error handling.
- **`tests/test_transactions.py`**: Tests transaction operations and relevant validation and error handling.
- **`tests/test_validation.py`**: Tests input validation functions.
- **`tests/test_summaries.py`**: Tests financial summary calculations and filtering behavior.

#### Data and Configuration

- **`data/`**: Stores the locally generated SQLite database. The `.gitkeep` file preserves the directory in Git while the database itself is excluded from version control.
- **`.gitignore`**: Specifies generated files, local databases, Python caches, virtual environments, and other files that should not be tracked by Git.
- **`requirements.txt`**: Lists third-party Python dependencies. The project currently uses Python's standard library and does not require third-party packages.
- **`README.md`**: Documents the project's purpose, features, architecture, setup, usage, and testing instructions.
