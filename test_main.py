import pytest
import httpx
import respx  

from fastapi.testclient import TestClient
from main import app, fake_users_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_test_database():
    """Garante o isolamento limpando o banco em memória antes de cada teste."""
    fake_users_db.clear()

# 1. Teste de integração para a raiz (Adaptado para o padrão FastAPI)
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

# 2. Teste de login com um provedor válido
def test_login_with_valid_provider():
    response = client.get("/auth/login/google")
    assert response.status_code == 200
    assert "auth_url" in response.json()
    assert "google" in response.json()["auth_url"]

# 3. Teste de login com um provedor inválido
def test_login_with_invalid_provider():
    response = client.get("/auth/login/facebook")
    assert response.status_code == 400
    assert response.json()["detail"] == "Provedor não suportado"

# 4. Teste de callback com sucesso e persistência
@respx.mock
def test_callback_success_and_user_creation():
    respx.post("https://oauth.fake/google/token").mock(
        return_value=httpx.Response(
            200,
            json={
                "email": "vito@exemplo.com",
                "name": "Vito Andrade",
                "provider": "google"
            }   
        )
    )

    response = client.get("/auth/callback?code=valid_code_123&provider=google")
    assert response.status_code == 200
    assert response.json()["status"] == "authenticated"
    assert response.json()["user"]["email"] == "vito@exemplo.com"
    assert "vito@exemplo.com" in fake_users_db

# 5. Teste de callback com código expirado ou inválido
@respx.mock
def test_callback_with_expired_code():
    respx.post("https://oauth.fake/google/token").mock(
        return_value=httpx.Response(400, json={"detail": "Código expirado"})
    )

    response = client.get("/auth/callback?code=expired_code&provider=google")
    assert response.status_code == 400
    assert response.json()["detail"] == "Token/Código expirado ou inválido"

# 6. Teste de callback com serviço externo fora do ar (Erro 503)
@respx.mock
def test_callback_external_service_unavailable():
    respx.post("https://oauth.fake/google/token").mock(
        side_effect=httpx.ConnectError("Erro de conexão")
    )

    response = client.get("/auth/callback?code=valid_code_123&provider=google")
    assert response.status_code == 503
    assert response.json()["detail"] == "Serviço externo indisponível"

# 7. Teste de callback sem passar o código obrigatório
def test_callback_without_code():
    response = client.get("/auth/callback?provider=google")
    assert response.status_code == 401
    assert response.json()["detail"] == "Código de autenticação não informado"
    
# 8. Teste do Monitor de Saúde e Métricas (Health)
def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "CONNECTED"
    assert "metrics" in response.json()





@respx.mock
def test_fluxo_completo_e2e_autenticacao_e_saude():
    """
    TESTE E2E: Simula toda a jornada real de um cliente.
    1. Inicia login no provedor Google.
    2. Recebe o callback com sucesso salvando os dados.
    3. Verifica se as métricas globais de saúde computaram o sucesso.
    """
    # Passo 1: Iniciar fluxo de login
    response_login = client.get("/auth/login/google")
    assert response_login.status_code == 200

    # Mock da chamada interna
    respx.post("https://oauth.fake/google/token").mock(
        return_value=httpx.Response(200, json={"email": "vito@test.com", "name": "Vito Andrade"})
    )

    # Passo 2: Callback com o código recebido do provedor
    response_callback = client.get("/auth/callback?provider=google&code=code123")
    assert response_callback.status_code == 200
    assert response_callback.json()["status"] == "authenticated"

    # Passo 3: Garantir que a rota de Saúde capturou as métricas de sucesso
    response_health = client.get("/health")
    assert response_health.status_code == 200
    assert response_health.json()["metrics"]["callbacks_sucesso"] >= 1
    
def test_cenario_mutacao_provocada():
    resposta = client.get("/auth/login/facebook")
    
    assert resposta.status_code == 400
    assert resposta.json()["detail"] == "Provedor não suportado"