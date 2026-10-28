from .validation import validate_category_name, validate_category_id
from database.connection import get_connection
from  sqlite3 import IntegrityError

class DuplicateCategoryError(Exception):
    pass

class CategoryInUseError(Exception):
    pass


def create_category(name: str) -> dict:
    name = validate_category_name(name)
    conn = None
    try:
        conn = get_connection()
        cursor = conn.execute("INSERT INTO categories (name) VALUES(?)", (name,))
        categories_dict= {"id":cursor.lastrowid, "name": name}
        conn.commit()
    except IntegrityError as error:
        if conn is not None:
            conn.rollback()

        if "UNIQUE constraint failed: categories.name" in str(error):
                raise DuplicateCategoryError("A category with this name already exists")
        raise

    finally:
        if(conn is not None):
            conn.close()

    return categories_dict




def get_category(category_id: int) -> dict | None:
    category_id = validate_category_id(category_id)
    conn = None
    try:
        conn = get_connection()
        cursor = conn.execute("SELECT name FROM categories WHERE id = ?", (category_id,))
        result = cursor.fetchone()
        if result is None:
            return None
        category_dict = {"id": category_id, "name": result[0]}
    finally:
        if conn is not None:
            conn.close()
    return category_dict



def list_categories() -> list[dict]:
    conn =None
    category_dict_list = []
    try:
        conn = get_connection()
        cursor = conn.execute("SELECT id, name FROM categories")
        result = cursor.fetchall()
        for row in result:
            category_dict = {"id": row[0], "name": row[1]}
            category_dict_list.append(category_dict)
    finally:
        if conn is not None:
            conn.close()

    return category_dict_list



def update_category(category_id: int, name: str) -> dict | None:
    name = validate_category_name(name)
    category_id = validate_category_id(category_id)
    conn = None
    try:
        conn = get_connection()
        cursor = conn.execute("UPDATE categories Set name =? WHERE id = ?",(name,category_id,))
        if(cursor.rowcount == 0):
            return None
        conn.commit()
        category_dict = get_category(category_id)
    except IntegrityError as error:
            if conn is not None:
                conn.rollback()

            if "UNIQUE constraint failed: categories.name" in str(error):
                    raise DuplicateCategoryError("A category with this name already exists")
            raise

    finally:
        if conn is not None:
            conn.close()

    return category_dict


def delete_category(category_id: int) -> bool:
    category_id = validate_category_id(category_id)
    conn = None
    try:
        conn = get_connection()
        cursor =  conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        if cursor.rowcount == 0:
            return False
        conn.commit()
    except IntegrityError as error:
        if conn is not None:
            conn.rollback()
        if "FOREIGN KEY constraint failed" in str(error):
            raise CategoryInUseError("cannot delete a category that has transactions")

        raise
    finally:
        if conn is not None:
            conn.close()
    return True
