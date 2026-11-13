# Cafeteria Gourmet Digital

Aplicação acadêmica de e-commerce desenvolvida com Python, Flask, SQLite, HTML, CSS e JavaScript, organizada em padrão MVC.

## Requisitos
- Python 3.10 ou superior
- pip

## Instalação (Linux/macOS)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
No Windows:
```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
py app.py
```
Acesse http://127.0.0.1:5000

O banco `database/cafeteria.db` e os produtos de demonstração são criados automaticamente na primeira execução.

## Acesso administrativo de demonstração
- E-mail: `admin@cafeteria.local`
- Senha: `Admin123!`

Altere a senha e a `SECRET_KEY` antes de qualquer implantação pública. A senha administrativa inicial é apenas para demonstração acadêmica.

## Funcionalidades
- Cadastro e login com hash de senha
- Catálogo de produtos
- Carrinho de compras em sessão
- Registro de pedido e itens
- Consulta de pedidos do cliente
- Painel administrativo para cadastrar/desativar produtos e atualizar status de pedidos

## Pagamento
O checkout registra o pedido com pagamento `Pendente`. Não há cobrança real nem armazenamento de dados de cartão. Para pagamento real, integrar um gateway homologado usando ambiente de testes e credenciais protegidas.

## Estrutura MVC
- `models/`: acesso ao banco SQLite
- `views/`: templates HTML (pasta `templates/`)
- `controllers/`: rotas e regras de fluxo
- `static/`: CSS e JavaScript
- `app.py`: inicialização e registro dos controllers

## Limitações e melhorias futuras
Para uma publicação real, adicionar proteção CSRF, limitação de tentativas de login, recuperação de senha, política de privacidade/LGPD, logs, testes automatizados, configuração segura de produção e integração com gateway de pagamento. Este projeto é uma base funcional para demonstração acadêmica, não uma loja pronta para receber pagamentos reais.
