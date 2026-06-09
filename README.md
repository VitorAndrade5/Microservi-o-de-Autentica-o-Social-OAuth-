## Cenários de Teste Implementados

O projeto possui testes automatizados com pytest e TestClient, cobrindo os principais fluxos do microsserviço de autenticação social.

### 1. Rota raiz

Verifica se a API está ativa e respondendo corretamente.

### 2. Login com provedor válido

Testa se os provedores aceitos, como Google e GitHub, retornam uma URL simulada de autenticação.

### 3. Login com provedor inválido

Testa se a API bloqueia provedores não suportados, como Facebook, retornando erro 400.

### 4. Callback com sucesso

Simula uma resposta positiva da API externa OAuth usando mock com respx. O usuário retornado é salvo no banco de dados em memória usado nos testes.

### 5. Callback com código expirado

Simula uma resposta negativa da API externa, validando se a aplicação retorna erro 400 quando o código OAuth é inválido ou expirado.

### 6. Callback com serviço externo indisponível

Simula uma falha de conexão com o provedor externo e valida se a API retorna erro 503.

### 7. Callback sem código

Valida se a API retorna erro 401 quando o código de autenticação não é informado.