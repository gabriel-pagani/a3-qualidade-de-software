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


def test_delete_user(setup_user):
    user = setup_user
    result = user.delete()
    
    assert result is True
    
    # Tenta logar após deletar, deve falhar
    logged_user, _, _, _ = User.login("test_user", "test_password_123")
    assert logged_user is None


@patch('controllers.user.get_connection')
def test_delete_user_exception(mock_get_connection, setup_user):
    # Simula um erro no cursor durante a deleção
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.execute.side_effect = Exception("Erro simulado de banco")
    mock_conn.cursor.return_value = mock_cursor
    mock_get_connection.return_value = mock_conn

    user = setup_user
    result = user.delete()
    
    assert result is False
    mock_conn.rollback.assert_called_once()


def test_get_last_logged_user(setup_user):
    # Logamos com o usuário recém criado (isso insere um registro na tabela login_history)
    User.login("test_user", "test_password_123")
    
    last_user = User.get_last_logged_user()
    
    assert last_user == "test_user"


@patch('controllers.user.execute_query')
def test_get_last_logged_user_exception(mock_execute_query):
    mock_execute_query.side_effect = Exception("Erro simulado de banco de dados")
    
    last_user = User.get_last_logged_user()
    
    assert last_user is None


def test_update_password_migration_exception(setup_user):
    # Cobre o "except Exception as e:" dentro do loop for da re-criptografia
    user = setup_user
    
    # Faz login para pegar a chave do usuário e criar uma senha
    _, user_key, _, _ = User.login(user.username, "test_password_123")
    Password.create(
        user_id=user.id, 
        user_key=user_key, 
        meta_data={"service": "Google"}, 
        secret_data={"password": "123"}
    )
    
    # Mocka a função decrypt_data para falhar propositalmente durante a migração
    with patch('controllers.user.decrypt_data') as mock_decrypt:
        mock_decrypt.side_effect = Exception("Falha simulada na descriptografia")
        
        result = user.update(
            current_master_password="test_password_123",
            new_master_password="new_password_456"
        )
        
        # A exceção no loop deve ser levantada, pega pelo except externo e retornar False
        assert result is False


def test_update_user_admin_status(setup_user):
    # Cobre o bloco "if is_admin is not None:"
    user = setup_user
    
    # Salva o status anterior e inverte
    new_admin_status = not user.is_admin
    
    result = user.update(
        current_master_password="test_password_123",
        is_admin=new_admin_status
    )
    
    assert result is True
    assert user.is_admin == new_admin_status


def test_update_user_integrity_error(setup_user):
    # Cobre o "except IntegrityError as e:" no método update
    user1 = setup_user
    
    # Cria um segundo usuário
    user2, _, _ = User.create(username="second_user", master_password="password_123")
    
    # Tenta atualizar o username do user2 para o username do user1 (que já existe no banco)
    # Isso forçará o banco a lançar um IntegrityError devido à constraint UNIQUE
    result = user2.update(
        current_master_password="password_123",
        new_username=user1.username
    )
    
    assert result is False


@patch('controllers.user.get_connection')
def test_delete_user_integrity_error(mock_get_connection, setup_user):
    # Cobre o "except IntegrityError as e:" no método delete
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    # Simula um erro de integridade sendo lançado pela query do banco
    mock_cursor.execute.side_effect = IntegrityError("Erro de integridade simulado")
    mock_conn.cursor.return_value = mock_cursor
    mock_get_connection.return_value = mock_conn

    user = setup_user
    result = user.delete()
    
    assert result is False
    # Garante que o banco chamou o rollback para cancelar a transação
    mock_conn.rollback.assert_called_once()


def test_update_user_password_with_existing_passwords(setup_user):
    user = setup_user
    
    # 1. Faz login para pegar a user_key atual
    _, user_key, _, _ = User.login("test_user", "test_password_123")
    
    # 2. Cria uma senha vinculada a este usuário (isso garante que o loop for será executado)
    new_password = Password.create(
        user_id=user.id,
        user_key=user_key,
        meta_data={"service": "Netflix", "login": "user@netflix.com"},
        secret_data={"password": "netflix_password"},
        type_id=None
    )
    
    # Guardamos os IVs antigos para comprovar que foram alterados
    old_metadata_iv = new_password.metadata_iv
    old_secret_iv = new_password.secret_iv
    
    # 3. Atualiza a senha mestra (Isso forçará a execução do bloco try inteiro dentro do loop!)
    result = user.update(
        current_master_password="test_password_123", 
        new_master_password="new_super_secure_password"
    )
    
    assert result is True
    
    # 4. Verifica se a senha no banco foi re-criptografada e teve seus IVs atualizados
    updated_password = Password.get(id=new_password.id)
    assert updated_password.metadata_iv != old_metadata_iv
    assert updated_password.secret_iv != old_secret_iv
