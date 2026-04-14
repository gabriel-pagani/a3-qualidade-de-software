import re


def validate_master_password(master_password: str) -> bool:
    return bool(len(master_password) >= 15)
