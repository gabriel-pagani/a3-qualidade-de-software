import os
import pytest
from unittest.mock import patch
from controllers.password import Password
from controllers.user import User
from controllers.password_type import PasswordType


@pytest.fixture
def setup_user():
    User.create(username="test_user", master_password="test_password_123")
    user, user_key, _, _ = User.login("test_user", "test_password_123")
    return user, user_key


def test_create_new_password(setup_user):
    user, user_key = setup_user

    new_password = Password.create(
        user_id=user.id,
        user_key=user_key,
        meta_data={"service": "Google", "login": "test@gmail.com"},
        secret_data={"password": "secure_password"},
        type_id=None
    )

    assert new_password is not None
    assert new_password.user_id == user.id


def test_create_invalid_password(setup_user):
    _, user_key = setup_user

    invalid_password = Password.create(
        user_id=9999,
        user_key=user_key,
        meta_data={"service": "Google"},
        secret_data={"password": "123"}
    )

    assert invalid_password is None


@patch('controllers.password.execute_query')
def test_create_password_exception(mock_execute_query, setup_user):
    mock_execute_query.side_effect = Exception("Erro simulado de banco de dados")
    user, user_key = setup_user

    password = Password.create(
        user_id=user.id,
        user_key=user_key,
        meta_data={"service": "Google"},
        secret_data={"password": "123"}
    )

    assert password is None


def test_get_password(setup_user):
    user, user_key = setup_user
    new_password = Password.create(
        user_id=user.id,
        user_key=user_key,
        meta_data={"service": "Google"},
        secret_data={"password": "123"}
    )

    password = Password.get(id=new_password.id)

    assert password is not None
    assert password.id == new_password.id
    assert password.user_id == user.id


def test_get_invalid_or_nonexistent_password():
    invalid_password = Password.get(id="abc")
    nonexistent_password = Password.get(id=9999)

    assert invalid_password is None
    assert nonexistent_password is None


@patch('controllers.password.execute_query')
def test_get_password_exception(mock_execute_query):
    mock_execute_query.side_effect = Exception("Erro simulado de banco de dados")

    password = Password.get(id=1)

    assert password is None


def test_get_all_by_user(setup_user):
    user, user_key = setup_user
    Password.create(user.id, user_key, {"service": "Google"}, {"password": "123"})
    Password.create(user.id, user_key, {"service": "Facebook"}, {"password": "abc"})

    passwords = Password.get_all_by_user(user_id=user.id)

    assert passwords != []
    assert len(passwords) == 2


@patch('controllers.password.execute_query')
def test_get_all_by_user_exception(mock_execute_query):
    mock_execute_query.side_effect = Exception("Erro simulado de banco de dados")

    passwords = Password.get_all_by_user(user_id=1)

    assert passwords == []


def test_update_password(setup_user):
    user, user_key = setup_user
    new_password = Password.create(
        user_id=user.id,
        user_key=user_key,
        meta_data={"service": "Google"},
        secret_data={"password": "123"}
    )

    old_metadata_iv = new_password.metadata_iv

    result = new_password.update(
        user_key=user_key,
        meta_data={"service": "Google Updated"},
        secret_data={"password": "new_password"}
    )

    updated_password = Password.get(id=new_password.id)

    assert result is True
    assert updated_password is not None
    assert updated_password.metadata_iv != old_metadata_iv


def test_update_password_invalid(setup_user):
    user, user_key = setup_user
    new_password = Password.create(
        user_id=user.id,
        user_key=user_key,
        meta_data={"service": "Google"},
        secret_data={"password": "123"}
    )

    result = new_password.update(
        user_key=user_key
    )

    assert result is False


@patch('controllers.password.execute_query')
def test_update_password_exception(mock_execute_query, setup_user):
    mock_execute_query.side_effect = Exception("Erro simulado de banco de dados")
    user, user_key = setup_user

    new_password = Password(
        id=1, user_id=user.id, type_id=None,
        metadata_iv=b'', encrypted_metadata=b'',
        secret_iv=b'', encrypted_secret=b'',
        created_at=None, updated_at=None
    )

    result = new_password.update(
        user_key=user_key,
        meta_data={"service": "Google"}
    )

    assert result is False


def test_delete_password(setup_user):
    user, user_key = setup_user
    new_password = Password.create(
        user_id=user.id,
        user_key=user_key,
        meta_data={"service": "Google"},
        secret_data={"password": "123"}
    )

    result = new_password.delete()
    password = Password.get(id=new_password.id)

    assert result is True
    assert password is None


@patch('controllers.password.execute_query')
def test_delete_password_exception(mock_execute_query):
    mock_execute_query.side_effect = Exception("Erro simulado de banco de dados")

    new_password = Password(
        id=1, user_id=1, type_id=None,
        metadata_iv=b'', encrypted_metadata=b'',
        secret_iv=b'', encrypted_secret=b'',
        created_at=None, updated_at=None
    )
    result = new_password.delete()

    assert result is False


def test_update_password_type_id(setup_user):
    user, user_key = setup_user
    
    pw_type = PasswordType.create(name="Social Media")
    
    new_password = Password.create(
        user_id=user.id,
        user_key=user_key,
        meta_data={"service": "Twitter"},
        secret_data={"password": "123"},
        type_id=None
    )
    
    result = new_password.update(
        user_key=user_key,
        type_id=pw_type.id
    )
    
    updated_password = Password.get(id=new_password.id)

    assert result is True
    assert updated_password.type_id == pw_type.id


def test_update_password_type_id_to_none(setup_user):
    user, user_key = setup_user
    
    pw_type = PasswordType.create(name="Email")
    
    new_password = Password.create(
        user_id=user.id,
        user_key=user_key,
        meta_data={"service": "Gmail"},
        secret_data={"password": "123"},
        type_id=pw_type.id
    )
    
    result = new_password.update(
        user_key=user_key,
        type_id=0
    )
    
    updated_password = Password.get(id=new_password.id)

    assert result is True
    assert updated_password.type_id is None
