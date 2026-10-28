from decimal import Decimal, InvalidOperation
from datetime import date

def validate_currency(currency_code: str)->str:
    currency = ["XOF","EUR","USD"]
    if (not isinstance(currency_code, str)):
        raise ValueError

    currency_code = currency_code.strip().upper()
    if (currency_code not in currency):
        raise ValueError
    return currency_code


def validate_amount(amount:str, currency_code:str)->int:
    if(not isinstance(amount, str)):
        raise TypeError
    try:
        amount = Decimal(amount)
    except (InvalidOperation, TypeError):
        raise ValueError

    if(not amount.is_finite()):
        raise ValueError


    if(amount<=0):
        raise ValueError
    currency_code = validate_currency(currency_code)
    if (currency_code == "XOF"):
        if(amount.as_tuple().exponent < 0):
            raise ValueError
        amount = int(amount)
        return amount

    elif(currency_code =="EUR" or currency_code ==  "USD"):
        if(amount.as_tuple().exponent <-2):
            raise ValueError
        amount = int(amount * 100)
        return amount



def validate_transaction_type(transaction_type: str) -> str:
    if(not isinstance(transaction_type, str)):
        raise TypeError
    transaction_type = transaction_type.strip().lower()
    if(transaction_type != "income" and transaction_type != "expense"):
        raise ValueError
    return transaction_type



def validate_date(date_value : str | None = None) -> str:
    if(not isinstance(date_value, str) and date_value is not None):
        raise TypeError

    if(date_value is None):
        date_value = date.today()
        date_value = date_value.isoformat()
    else:
        try:
           parsed_date= date.fromisoformat(date_value)
        except ValueError:
            raise ValueError
        date_value = parsed_date.isoformat()
    return date_value



def validate_category_name(name: str) -> str:
   if (not isinstance(name,str)):
       raise TypeError
   name = name.strip()
   if(name ==""):
       raise ValueError
   return name





def validate_description(description: str | None = None) -> str| None:
    if( not isinstance(description, str) and description is not None):
        raise TypeError
    if (description is None):
        return None
    description = description.strip()
    if(description ==""):
        return None
    return description



def validate_category_id(category_id: int) -> int:
    if type(category_id) is not int:
        raise TypeError
    if(category_id <=0):
        raise ValueError

    return category_id

def validate_transaction_id(transaction_id: int) -> int:
   if type(transaction_id) is not int:
       raise TypeError

   if transaction_id <=0:
       raise ValueError
   return transaction_id
