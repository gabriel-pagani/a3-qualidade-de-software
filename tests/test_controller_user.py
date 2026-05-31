import pytest
from unittest.mock import patch, MagicMock
from sqlite3 import IntegrityError
from controllers.user import User
from controllers.password import Password

# Fixture para criar um usuário base para os testes
@pytest.fixture
def setup_user():
    user, status, msg = User.create(username="test_user", master_password="test_password_123")
    return user


def test_create_new_user():
    user, status, msg = User.create(username="new_user", master_password="secure_password")

    assert user is not None
    assert user.username == "new_user"
    assert status == "success"


def test_create_duplicate_user(setup_user):
    # Tenta criar um usuário com o mesmo username da fixture
    user, status, msg = User.create(username="test_user", master_password="another_password")

    assert user is None
    assert status == "warning"
    assert "already exists" in msg


@patch('controllers.user.execute_query')
def test_create_user_exception(mock_execute_query):
    mock_execute_query.side_effect = Exception("Erro simulado de banco de dados")
    
    user, status, msg = User.create(username="error_user", master_password="123")
    
    assert user is None
    assert status == "error"


def test_login_success(setup_user):
    user, user_key, status, msg = User.login("test_user", "test_password_123")

    assert user is not None
    assert user_key is not None
    assert status == "success"


def test_login_invalid_password(setup_user):
    user, user_key, status, msg = User.login("test_user", "wrong_password")

    assert user is None
    assert user_key is None
    assert status == "warning"


def test_login_invalid_username():
    user, user_key, status, msg = User.login("nonexistent_user", "123")

    assert user is None
    assert user_key is None
    assert status == "warning"


@patch('controllers.user.execute_query')
def test_login_exception(mock_execute_query):
    mock_execute_query.side_effect = Exception("Erro simulado de banco de dados")
    
    user, user_key, status, msg = User.login("test_user", "123")
    
    assert user is None
    assert user_key is None
    assert status == "error"


def test_update_user_username(setup_user):
    user = setup_user
    
    # Atualiza apenas o username
    result = user.update(
        current_master_password="test_password_123", 
        new_username="updated_user"
    )
    
    assert result is True
    assert user.username == "updated_user"


def test_update_user_password(setup_user):
    user = setup_user
    old_hash = user.master_password_hash
    
    # Atualiza a senha mestra
    result = user.update(
        current_master_password="test_password_123", 
        new_master_password="new_secure_password"
    )
    
    assert result is True
    assert user.master_password_hash != old_hash
    
    # Valida se o login funciona com a nova senha
    logged_user, _, status, _ = User.login("test_user", "new_secure_password")
    assert logged_user is not None
    assert status == "success"


def test_update_user_invalid_current_password(setup_user):
    user = setup_user
    
    # Tenta atualizar informando a senha atual incorreta
    result = user.update(
        current_master_password="wrong_password", 
        new_username="hacker_user"
    )
    
    assert result is False


def test_update_user_no_data(setup_user):
    user = setup_user
    
    # Tenta dar update sem informar nenhum dado novo
    result = user.update(current_master_password="test_password_123")
    
    assert result is False


@patch('controllers.user.get_connection')
def test_update_user_exception(mock_get_connection, setup_user):
    # Simula um erro no cursor que forçará o "rollback"
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("Erro simulado de banco")
    mock_conn.cursor.return_value = mock_cursor
    mock_get_connection.return_value = mock_conn

    user = setup_user
    result = user.update(
        current_master_password="test_password_123", 
        new_username="fail_user"
    )
    
    assert result is False
    # Garante que o rollback foi chamado para reverter a transação em caso de erro
    mock_conn.rollback.assert_called_once()
