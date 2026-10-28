from .validation import validate_amount,validate_currency,validate_description,validate_transaction_type,validate_category_id,validate_date, validate_transaction_id
from database.connection import get_connection
from sqlite3 import IntegrityError
from .categories import get_category

class CategoryNonExistentError(Exception):
   pass

def create_transaction(
    amount: str,
    transaction_type :str,
    category_id:int,
   description: str | None = None,
   date: str | None = None,
   currency_code: str = "XOF",
) -> dict:
   currency_code = validate_currency(currency_code)
   amount = validate_amount(amount, currency_code)
   transaction_type = validate_transaction_type(transaction_type)
   category_id = validate_category_id(category_id)
   description = validate_description(description)
   date = validate_date(date)

   result= get_category(category_id)
   if result is None:
      raise CategoryNonExistentError("The category doesn't exist")

   conn = None
   try:
      conn = get_connection()
      cursor = conn.execute("INSERT INTO transactions (amount,transaction_type,category_id,description,date,currency_code) VALUES(?,?,?,?,?,?)",(amount,transaction_type,category_id,description, date, currency_code,))
      transaction_dict = {"id": cursor.lastrowid, "amount":amount,
                          "transaction_type": transaction_type, "category_id": category_id,
                          "description": description, "date": date,
                          "currency_code": currency_code}
      conn.commit()
   except IntegrityError as error:
      if conn is not None:
         conn.rollback()
      raise

   finally:
      if conn is not None:
         conn.close()
   return transaction_dict




def get_transaction(transaction_id: int) -> dict | None:
   transaction_id= validate_transaction_id(transaction_id)
   conn = None
   try:
      conn = get_connection()
      cursor = conn.execute("SELECT amount,transaction_type,category_id, description,date, currency_code FROM transactions WHERE id = ?", (transaction_id,))
      result = cursor.fetchone()
      if result is None:
         return None
      transaction_dict = {"id": transaction_id, "amount": result[0],"transaction_type": result[1],"category_id": result[2], "description": result[3],"date": result[4],
                          "currency_code": result[5]}
   finally:
      if conn is not None:
         conn.close()

   return transaction_dict




def list_transactions(
category_id: int | None = None,
    transaction_type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    currency_code: str | None = None,
) -> list[dict]:
   transactions_dict_list = []
   conditions= []
   parameters = []
   if category_id is not None:
      category_id = validate_category_id(category_id)
      if get_category( category_id) is None:
         raise CategoryNonExistentError("No category with this id exists")
      parameters.append(category_id)
      conditions.append("category_id = ?")

   if transaction_type is not None:
      transaction_type = validate_transaction_type(transaction_type)
      parameters.append(transaction_type)
      conditions.append("transaction_type = ?")

   if currency_code is not None:
      currency_code = validate_currency(currency_code)
      parameters.append(currency_code)
      conditions.append("currency_code = ?")


   if start_date is not None and end_date is None:
      start_date = validate_date(start_date)
      parameters.append(start_date)
      conditions.append("date >= ?")

   elif end_date is not None and start_date is None:
      end_date = validate_date(end_date)
      parameters.append(end_date)
      conditions.append("date <= ?")

   elif start_date is not None and end_date is not None:
      start_date = validate_date(start_date)
      end_date = validate_date(end_date)
      if start_date > end_date:
         raise ValueError("Start date cannot be later than end date")
      parameters.append(start_date)
      conditions.append("date >= ?")
      parameters.append(end_date)
      conditions.append("date <= ?")
   conn =None

   try:
      conn =get_connection()
      query = "SELECT * FROM transactions"
      if conditions: # the if conditions will work when the list is not empty so when conditions is not empty it will work
         query += " WHERE "+  " AND ".join(conditions)

      cursor = conn.execute(query,parameters)
      result = cursor.fetchall()
      for row in result:
         transactions_dict = {"id": row[0],"amount": row[1],"transaction_type": row[2], "category_id":row[3], "description":row[4],"date":row[5],"currency_code": row[6]}
         transactions_dict_list.append(transactions_dict)

   finally:
      if conn is not None:
         conn.close()
   return transactions_dict_list



def update_transaction(
    transaction_id: int,
    amount: str,
    transaction_type: str,
    category_id: int,
    description: str | None,
    date: str,
    currency_code: str,
) -> dict | None:
   transaction_type = validate_transaction_type(transaction_type)
   transaction_id = validate_transaction_id(transaction_id)
   category_id = validate_category_id(category_id)
   description = validate_description(description)
   date = validate_date(date)
   currency_code= validate_currency(currency_code)
   amount = validate_amount(amount,currency_code)
   conn = None
   if get_category(category_id) is None:
      raise CategoryNonExistentError("No category with this id exists")

   try:
      conn = get_connection()
      cursor  = conn.execute("UPDATE transactions SET amount =?, transaction_type =?, category_id =?, description = ?, date =?,  currency_code = ? WHERE id = ?",(amount,transaction_type,category_id,description,date,currency_code,transaction_id,))
      if cursor.rowcount ==0:
         return None

      conn.commit()
      transactions_dict = {"id":transaction_id,"amount": amount, "transaction_type": transaction_type, "category_id":category_id, "description":description,"date":date,"currency_code":currency_code}
   except IntegrityError:
      if conn is not None:
         conn.rollback()
      raise
   finally:
      if conn is not None:
         conn.close()

   return transactions_dict



def delete_transaction(transaction_id: int) -> bool:
   transaction_id = validate_transaction_id(transaction_id)
   conn = None
   try:
      conn = get_connection()
      result = conn.execute("DELETE FROM transactions WHERE id =?", (transaction_id,))
      if result.rowcount ==0:
         return False
      conn.commit()
   except IntegrityError as error:
      if conn is not None:
         conn.rollback()
      raise
   finally:
      if conn is not None:
         conn.close()
   return True
