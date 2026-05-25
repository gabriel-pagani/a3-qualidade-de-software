from typing import Optional, List
from datetime import datetime
from database.connection import execute_query
from utils.cryptor import encrypt_data


class Password:
    def __init__(
        self,
        id: int,
        user_id: int,
        type_id: Optional[int],
        metadata_iv: bytes,
        encrypted_metadata: bytes,
        secret_iv: bytes, 
        encrypted_secret: bytes,
        created_at: datetime,
        updated_at: Optional[datetime],
    ):
        self.id = id
        self.user_id = user_id
        self.type_id = type_id
        self.metadata_iv = metadata_iv
        self.encrypted_metadata = encrypted_metadata
        self.secret_iv = secret_iv
        self.encrypted_secret = encrypted_secret
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def create(
        cls,         
        user_id: int,
        user_key: bytes,
        meta_data: dict,
        secret_data: dict,
        type_id: Optional[int] = None,
    ) -> Optional['Password']:
        try:
            associated_data = f'user_id:{user_id};'.encode()
            
            meta_iv, enc_meta = encrypt_data(user_key, meta_data, associated_data)
            sec_iv, enc_sec = encrypt_data(user_key, secret_data, associated_data)
            
            response = execute_query(
                "INSERT INTO passwords (user_id, type_id, metadata_iv, encrypted_metadata, secret_iv, encrypted_secret) VALUES (?, ?, ?, ?, ?, ?) RETURNING *",
                (user_id, type_id, meta_iv, enc_meta, sec_iv, enc_sec)
            )

            if response != []:
                return cls(
                    id=response[0][0],
                    user_id=response[0][1],
                    type_id=response[0][2],
                    metadata_iv=response[0][3],
                    encrypted_metadata=response[0][4],
                    secret_iv=response[0][5],
                    encrypted_secret=response[0][6],
                    created_at=response[0][7],
                    updated_at=response[0][8],
                )
            
        except Exception as e:
            print(f"exception-on-create: {e}")
            return None

    @classmethod
    def get(cls, id: int) -> Optional['Password']:
        try:
            response = execute_query(
                "SELECT * FROM passwords WHERE id = ?",
                (id,)
            )

            if response != []:
                return cls(
                    id=response[0][0],
                    user_id=response[0][1],
                    type_id=response[0][2],
                    metadata_iv=response[0][3],
                    encrypted_metadata=response[0][4],
                    secret_iv=response[0][5],
                    encrypted_secret=response[0][6],
                    created_at=response[0][7],
                    updated_at=response[0][8],
                )
            return None

        except Exception as e:
            print(f"exception-on-get: {e}")
            return None

    @classmethod
    def get_all_by_user(cls, user_id: int) -> List['Password']:
        try:
            response = execute_query(
                "SELECT * FROM passwords WHERE user_id = ?",
                (user_id,),
            )

            passwords = []
            if response:
                for row in response:
                    passwords.append(
                        cls(
                            id=row[0],
                            user_id=row[1],
                            type_id=row[2],
                            metadata_iv=row[3],
                            encrypted_metadata=row[4],
                            secret_iv=row[5],
                            encrypted_secret=row[6],
                            created_at=row[7],
                            updated_at=row[8],
                        )
                    )
            return passwords

        except Exception as e:
            print(f"exception-on-get-all: {e}")
            return []

    def update(
        self,
        user_key: bytes,
        type_id: Optional[int] = None,
        meta_data: Optional[dict] = None,
        secret_data: Optional[dict] = None,
    ) -> bool:
        try:
            associated_data = f'user_id:{self.user_id};'.encode()
            fields = list()
            values = list()
            
            if type_id is not None:
                fields.append("type_id = ?")
                values.append(None if type_id == 0 else type_id)
            
            if meta_data:
                m_iv, e_m = encrypt_data(user_key, meta_data, associated_data)
                fields.extend(["metadata_iv = ?", "encrypted_metadata = ?"])
                values.extend([m_iv, e_m])
                self.metadata_iv = m_iv
                self.encrypted_metadata = e_m
                
            if secret_data:
                s_iv, e_s = encrypt_data(user_key, secret_data, associated_data)
                fields.extend(["secret_iv = ?", "encrypted_secret = ?"])
                values.extend([s_iv, e_s])
                self.secret_iv = s_iv
                self.encrypted_secret = e_s

            if not fields:
                return False

            values.append(self.id)
            execute_query(
                f"UPDATE passwords SET {', '.join(fields)} WHERE id = ?", 
                tuple(values)
            )

            return True

        except Exception as e:
            print(f"exception-on-update: {e}")
            return False

    def delete(self) -> bool:
        try:
            execute_query(
                "DELETE FROM passwords WHERE id = ?",
                (self.id,)
            )
            
            return True

        except Exception as e:
            print(f"exception-on-delete: {e}")
            return False
