# Microserviço de Autenticação Social OAuth

## Descrição do Projeto

Este projeto consiste em um microsserviço desenvolvido com FastAPI para simular um fluxo de autenticação social OAuth2 utilizando provedores como Google e GitHub.

O objetivo principal é demonstrar o funcionamento de uma API com autenticação simulada, testes de integração, uso de banco de testes em memória, mock de API externa, tratamento de falhas e execução automática dos testes por meio de CI com GitHub Actions.

## Tecnologias Utilizadas

- Python
- FastAPI
- Uvicorn
- Pytest
- HTTPX
- RESPX
- GitHub Actions

## Estrutura do Projeto

```txt
microservico-oauth/
├── main.py
├── test_main.py
├── requirements.txt
├── README.md
└── .github/
    └── workflows/
        └── ci.yml

Como rodar o projeto:

Clone o repositório:

git clone https://github.com/VitorAndrade5/Microservi-o-de-Autentica-o-Social-OAuth-.git

Entre na pasta do projeto:

cd Microservi-o-de-Autentica-o-Social-OAuth-

Instale as dependências:

python -m pip install -r requirements.txt

Caso esteja usando o lançador do Windows:

py -m pip install -r requirements.txt
Como executar a API

Rode o servidor com Uvicorn:

uvicorn main:app --reload

Acesse a documentação automática da API:

http://127.0.0.1:8000/docs
Rotas da API
Rota raiz
GET /

Verifica se a API está ativa.

Resposta esperada:

{
  "message": "Microserviço de Autenticação Social Ativo"
}
Login com provedor social
GET /auth/login/{provider}

Provedores aceitos:

google
github

Exemplo:

GET /auth/login/google

Caso o provedor seja válido, a API retorna uma URL simulada de autenticação.

Caso o provedor não seja suportado, a API retorna erro 400 Bad Request.

Callback de autenticação
GET /auth/callback?code=valid_code_123&provider=google

Essa rota simula o retorno do provedor OAuth após o login.

Ela recebe um código de autenticação, faz uma chamada simulada para uma API externa usando HTTPX e salva o usuário autenticado em um banco de dados em memória.

Banco de Testes

O projeto utiliza um banco de dados em memória representado por um dicionário Python.

Esse banco é usado para simular o armazenamento dos usuários autenticados durante os testes.

Antes de cada teste, o banco é limpo automaticamente para garantir isolamento entre os cenários.

Mock de API Externa

O projeto usa a biblioteca RESPX para simular chamadas externas feitas com HTTPX.

Isso permite testar o comportamento da API sem depender de serviços reais como Google ou GitHub.

Com isso, é possível simular:

Resposta de sucesso da API externa.
Código expirado ou inválido.
Falha de conexão com o serviço externo.
Testes de Integração

Os testes foram desenvolvidos com Pytest e FastAPI TestClient.

Para executar os testes:

python -m pytest -v

Ou, no Windows:

py -m pytest -v
Cenários de Teste Implementados
1. Rota raiz

Verifica se a API está online e respondendo corretamente.

2. Login com provedor válido

Testa se um provedor aceito, como Google, retorna uma URL simulada de autenticação.

3. Login com provedor inválido

Testa se a API bloqueia provedores não suportados, como Facebook, retornando erro 400 Bad Request.

4. Callback com sucesso

Simula uma resposta positiva da API externa OAuth usando mock com RESPX.

A API recebe os dados do usuário e salva essas informações no banco em memória.

5. Callback com código expirado

Simula uma resposta negativa da API externa, validando se a aplicação retorna erro 400 Bad Request quando o código OAuth é inválido ou expirado.

6. Callback com serviço externo indisponível

Simula uma falha de conexão com o provedor externo e valida se a API retorna erro 503 Service Unavailable.

7. Callback sem código

Valida se a API retorna erro 401 Unauthorized quando o código de autenticação não é informado.

Integração Contínua com GitHub Actions

O projeto possui uma pipeline de CI configurada com GitHub Actions.

A cada push ou pull request para a branch main, o GitHub executa automaticamente os testes do projeto.

Etapas da pipeline:

Baixar o código do repositório.
Configurar o Python.
Instalar as dependências.
Rodar os testes automatizados com Pytest.

Arquivo da pipeline:

.github/workflows/ci.yml
Entregáveis Atendidos
Testes de integração implementados.
Banco de testes em memória.
Mock de API externa com RESPX.
Tratamento de falhas.
Testes para cenários de erro.
Pipeline de CI com execução automática dos testes.
Documentação dos cenários testados.

Observabilidade e Quality Gates (Aula 4)

Implementamos mecanismos de monitoramento contínuo e validação rigorosa de qualidade:

- Endpoint `/health`: Retorna o status de saúde da aplicação, conexões simuladas e expõe métricas em tempo real.
- Logs Estruturados: Uso da biblioteca nativa `logging` mapeando eventos cruciais (`INFO`, `WARNING`, `ERROR`, `CRITICAL`).
- Métricas Simples: Contadores dinâmicos controlando requisições de sucesso e falha no ecossistema.
- Quality Gate Definição: Configuração de barreira de qualidade no GitHub Actions através do `pytest-cov`, exigindo cobertura de teste mínima de 80% para aceitar commits na branch principal.

Relatório de Prevenção de Bugs

O teste de integração/E2E implementado tenta evitar dois bugs críticos no microsserviço:

1. Degradação Silenciosa por Instabilidade Externa (Timeout/Queda): Evita que uma queda ou lentidão nas APIs do Google ou GitHub trave o nosso servidor Python esperando uma resposta da rede. O teste garante que o sistema capture a falha instantaneamente e responda com `503 Service Unavailable`, mantendo a aplicação de pé.
2. Vazamento de Requisições Malformadas: Impede que requisições sem códigos de autenticação válidos ou com provedores não suportados burlem a segurança, poluindo a memória ou o banco de dados do sistema com acessos inválidos.

Autores: 
Vito Andrade
Guilherme Abreu