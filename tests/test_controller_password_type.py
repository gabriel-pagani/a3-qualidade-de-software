from unittest.mock import patch
from controllers.password_type import PasswordType


def test_create_new_password_type():
    new_password_type = PasswordType.create(name="Test")

    assert new_password_type is not None
    assert new_password_type.name == "Test"


def test_create_invalid_password_type():
    invalid_password_type = PasswordType.create(name=123)

    assert invalid_password_type is None


def test_create_duplicate_password_type():
    PasswordType.create(name="Test")
    duplicate_password_type = PasswordType.create(name="Test")

    assert duplicate_password_type is None


def test_get_password_type():
    new_password_type = PasswordType.create(name="Test")
    password_type = PasswordType.get(id=new_password_type.id)

    assert password_type is not None
    assert password_type.name == "Test"


def test_get_invalid_or_nonexistent_password_type():
    invalid_password_type = PasswordType.get(id="abc")
    nonexistent_password_type = PasswordType.get(id=123)

    assert invalid_password_type is None
    assert nonexistent_password_type is None


@patch('controllers.password_type.execute_query')
def test_get_password_type_exception(mock_execute_query):
    mock_execute_query.side_effect = Exception("Erro simulado de banco de dados")
    
    password_type = PasswordType.get(id=1)
    
    assert password_type is None


def test_get_all_password_types():
    PasswordType.create(name="Test")
    PasswordType.create(name="Test2")
    PasswordType.create(name="Test3")
    password_types = PasswordType.get_all()

    assert password_types is not []

    for pwt in password_types:
        assert pwt.name in ["Test", "Test2", "Test3"]
