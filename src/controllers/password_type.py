from typing import Optional, List
from database.connection import execute_query


class PasswordType:
    def __init__(
        self, 
        id: int, 
        name: str
    ):
        self.id = id
        self.name = name

    @classmethod
    def create(cls, name: str) -> Optional['PasswordType']:
        try:
            response = execute_query(
                "INSERT INTO password_types (name) VALUES (?) RETURNING *",
                (name.strip(),)
            )

            if response != []:
                return cls(
                    id=response[0][0],
                    name=response[0][1],
                )
            return None
            
        except Exception as e:
            print(f"exception-on-create: {e}")
            return None

    @classmethod
    def get(cls, id: int) -> Optional['PasswordType']:
        try:
            response = execute_query(
                "SELECT * FROM password_types WHERE id = ?",
                (id,)
            )
            
            if response != []:
                return cls(
                    id=response[0][0], 
                    name=response[0][1],
                )
            return None

        except Exception as e:
            print(f"exception-on-get: {e}")
            return None

    @classmethod
    def get_all(cls) -> List['PasswordType']:
        try:
            response = execute_query("SELECT * FROM password_types ORDER BY name")
            
            types = []
            if response:
                for row in response:
                    types.append(
                        cls(
                            id=row[0], 
                            name=row[1]
                        )
                    )
            return types

        except Exception as e:
            print(f"exception-on-get-all: {e}")
            return []

    def update(self, name: str) -> bool:
        try:
            if not self.id:
                return False

            execute_query(
                f"UPDATE password_types SET name = ? WHERE id = ?", 
                (name.strip(), self.id)
            )
            
            self.name = name.strip() if name else self.name

            return True

        except Exception as e:
            print(f"exception-on-update: {e}")
            return False

    def delete(self) -> bool:
        try:
            if not self.id:
                return False
            
            execute_query(
                "DELETE FROM password_types WHERE id = ?",
                (self.id,)
            )
            
            return True

        except Exception as e:
            print(f"exception-on-delete: {e}")
            return False
