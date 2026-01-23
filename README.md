# Projeto Classificador de Emails
### Autor: Pedro Paulo Ramos de Carvalho

## Como Rodar:

Passo 1: Clonar Repositorio

git clone https://github.com/pedroprcarvalho/classify-email.git
cd classify-email

Passo 2: Criar ambiente virtual
python -m venv venv

Passo 3: Ativar ambiente virtual 
venv\Scripts\activate

Passo 4: Instalar dependências
pip install -r requirements.txt

Passo 5: Configurar variáveis de ambiente
Crie um arquivo .env
adicione no arquivo:
API_KEY=seu_token_do_hugging_face
Link para gerar token:
https://huggingface.co/settings/tokens

Passo 6: mudar a main para 

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True, use_reloader=False)

## Executar a Aplicação:
python app.py

http://127.0.0.1:8080


Link para aplicação online:
https://classify-email.onrender.com/

