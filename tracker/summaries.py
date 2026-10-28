from .validation  import validate_currency, validate_date, validate_category_id
from .categories import get_category
from .transactions import CategoryNonExistentError
from database.connection import get_connection


def get_totals(
    currency_code: str,
    start_date: str | None = None,
    end_date: str | None = None,
    category_id: int | None = None,
) -> dict:
    parameters =[]
    conditions = []

    currency_code = validate_currency(currency_code)
    parameters.append(currency_code)
    conditions.append("currency_code = ?")

    if category_id is not None:
        category_id = validate_category_id(category_id)
        if get_category(category_id) is None:
            raise CategoryNonExistentError("A category with this id doesn't exist")
        parameters.append(category_id)
        conditions.append("category_id = ?")

    if start_date is not None and end_date is None:
        start_date = validate_date(start_date)
        parameters.append(start_date)
        conditions.append("date >= ?")
    elif start_date is None and end_date is not None:
        end_date = validate_date(end_date)
        parameters.append(end_date)
        conditions.append("date <= ?")

    elif start_date is not None and end_date is not None:
        start_date = validate_date(start_date)
        end_date = validate_date(end_date)
        if start_date > end_date:
            raise ValueError
        parameters.append(start_date)
        conditions.append("date >= ?")
        parameters.append(end_date)
        conditions.append("date <= ?")

    conn = None
    try:
        conn = get_connection()
        query = "SELECT COALESCE(SUM(CASE WHEN transaction_type = 'income' THEN amount ELSE 0 END), 0) AS income_minor, COALESCE(SUM(CASE WHEN transaction_type = 'expense' THEN amount ELSE 0 END), 0) AS expense_minor FROM transactions"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        cursor = conn.execute(query,parameters)
        result = cursor.fetchone()
        income_minor = result[0]
        expense_minor = result[1]
        balance = income_minor- expense_minor
        totals_dict = {"currency_code": currency_code, "income_minor": income_minor, "expense_minor": expense_minor, "balance_minor": balance}

    finally:
        if conn is not None:
            conn.close()
    return totals_dict



def get_income_total(
    currency_code: str,
    start_date: str | None = None,
    end_date: str | None = None,
    category_id: int | None = None,
) -> int:
    parameters =[]
    conditions= []

    currency_code = validate_currency(currency_code)
    parameters.append(currency_code)
    conditions.append("currency_code = ?")

    if category_id is not None:
        category_id = validate_category_id(category_id)
        if get_category(category_id) is None:
            raise CategoryNonExistentError("A category with this id doesn't exist")
        parameters.append(category_id)
        conditions.append("category_id = ?")

    if start_date is not None and end_date is None:
        start_date = validate_date(start_date)
        parameters.append(start_date)
        conditions.append("date >= ?")

    elif start_date is None and end_date is not None:
        end_date = validate_date(end_date)
        parameters.append(end_date)
        conditions.append("date <= ?")


    elif start_date is not None and end_date is not None:
        start_date = validate_date(start_date)
        end_date = validate_date(end_date)
        if start_date > end_date:
            raise ValueError
        parameters.append(start_date)
        conditions.append("date >= ?")
        parameters.append(end_date)
        conditions.append("date <= ?")

    transaction_type = "income"
    parameters.append(transaction_type)
    conditions.append("transaction_type = ?")

    conn = None
    try:
        conn = get_connection()
        query = "SELECT COALESCE(SUM(amount),0)  FROM transactions"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        cursor = conn.execute(query,parameters)
        result = cursor.fetchone()
        total_income = result[0]
    finally:
        if conn is not None:
            conn.close()
    return total_income





def get_expense_total(
    currency_code: str,
    start_date: str | None = None,
    end_date: str | None = None,
    category_id: int | None = None,
) -> int:
    parameters =[]
    conditions= []

    currency_code = validate_currency(currency_code)
    parameters.append(currency_code)
    conditions.append("currency_code = ?")

    if category_id is not None:
        category_id = validate_category_id(category_id)
        if get_category(category_id) is None:
            raise CategoryNonExistentError("A category with this id doesn't exist")
        parameters.append(category_id)
        conditions.append("category_id = ?")

    if start_date is not None and end_date is None:
        start_date = validate_date(start_date)
        parameters.append(start_date)
        conditions.append("date >= ?")

    elif start_date is None and end_date is not None:
        end_date = validate_date(end_date)
        parameters.append(end_date)
        conditions.append("date <= ?")


    elif start_date is not None and end_date is not None:
        start_date = validate_date(start_date)
        end_date = validate_date(end_date)
        if start_date > end_date:
            raise ValueError
        parameters.append(start_date)
        conditions.append("date >= ?")
        parameters.append(end_date)
        conditions.append("date <= ?")

    transaction_type = "expense"
    parameters.append(transaction_type)
    conditions.append("transaction_type = ?")

    conn = None
    try:
        conn = get_connection()
        query = "SELECT COALESCE(SUM(amount),0) FROM transactions"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        cursor = conn.execute(query,parameters)
        result = cursor.fetchone()
        total_expense = result[0]

    finally:
        if conn is not None:
            conn.close()
    return total_expense



def get_balance(
    currency_code: str,
    start_date: str | None = None,
    end_date: str | None = None,
    category_id: int | None = None,
) -> int:

    total_income = get_income_total(currency_code,start_date,end_date,category_id)
    total_expense = get_expense_total(currency_code,start_date,end_date,category_id)
    balance = total_income - total_expense

    return balance
