import os
import logging
import secrets
from dotenv import load_dotenv
from flask import Flask, render_template, request, send_from_directory

from classifier import classificar_email
from response import resposta_sugerida
from process_email import extract_text

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def processar_email_com_resposta(text: str) -> dict:
    categoria = classificar_email(text)
    resposta = resposta_sugerida(text, categoria)
    return {
        "categoria": categoria,
        "resposta": resposta
    }

def gerar_secret_key() -> str:
    sk = os.getenv("SECRET_KEY")
    if not sk:
        sk = secrets.token_hex(24)
        logger.info("SECRET_KEY gerada automaticamente.")
    return sk

app = Flask(__name__)
app.config["SECRET_KEY"] = gerar_secret_key()
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

def obter_conteudo_email(req) -> str:
    texto = req.form.get("email_text", "").strip()
    if texto:
        return texto

    if "email_file" in req.files:
        arquivo = req.files["email_file"]
        if not arquivo or not arquivo.filename:
            raise ValueError("Nenhum arquivo selecionado.")

        nome = arquivo.filename.lower()

        if nome.endswith(".txt"):
            return arquivo.read().decode("utf-8", errors="ignore").strip()

        if nome.endswith(".pdf"):
            return extract_text(arquivo).strip()

        raise ValueError("Formato não suportado (.txt ou .pdf).")

    raise ValueError("Nenhum conteúdo fornecido.")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            conteudo = obter_conteudo_email(request)
            resultado = processar_email_com_resposta(conteudo)

            preview = conteudo if len(conteudo) <= 1000 else conteudo[:1000] + "..."

            return render_template(
                "index.html",
                result={
                    "label": resultado["categoria"],
                    "score": "",
                    "text": preview,
                    "response": resultado["resposta"]
                }
            )
        except Exception as e:
            return render_template("index.html", error=str(e))

    return render_template("index.html")

@app.route("/favicon.ico")
def favicon():
    caminho_static = os.path.join(app.root_path, "static")
    return send_from_directory(
        caminho_static,
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon"
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
