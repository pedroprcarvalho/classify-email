import os
import requests
from dotenv import load_dotenv
import time
import re

load_dotenv()
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
if not HF_API_TOKEN:
    raise ValueError("Defina HF_API_TOKEN no .env")

HF_MODEL = "facebook/bart-base-mnli"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

CANDIDATE_LABELS = [
    "email sobre trabalho, tarefas ou reuniões (produtivo)",
    "email solicitando informações, orçamento ou documentos profissionais (produtivo)",
    "email solicitando resolução de problemas (produtivo)",
    "email de propaganda ou marketing legítimo (improdutivo)",
    "email de golpe, phishing, fraude ou scam (improdutivo)",
    "email pessoal, cumprimentos, conversa informal, correntes ou brincadeiras (improdutivo)",
    "email de saudações, datas comemorativas ou felicitações (improdutivo)"
]

LABEL_MAP = {
    "email sobre trabalho, projetos, tarefas, reuniões ou negócios (produtivo)": "Produtivo",
    "email solicitando informações, orçamento ou documentos profissionais (produtivo)": "Produtivo",
    "email solicitando suporte técnico ou resolução de problemas (produtivo)": "Produtivo",
    "email de propaganda ou marketing legítimo (improdutivo)": "Improdutivo",
    "email de golpe, phishing, fraude ou scam (improdutivo)": "Improdutivo",
    "email pessoal, cumprimentos, conversa informal, correntes ou brincadeiras (improdutivo)": "Improdutivo",
    "email de saudações, datas comemorativas ou felicitações (improdutivo)": "Improdutivo"
}

CONFIDENCE_THRESHOLD = 0.70
CONFIDENCE_MARGIN = 0.15

KEYWORDS_PRODUTIVO = [
    "proposta", "orçamento", "reunião", "documento", "contrato", "pedido",
    "suporte", "assistência", "urgente", "problema", "bloqueio", "relatório",
    "projeto", "implementação", "análise", "negócio", "parceria", "pagamento"
]

KEYWORDS_GOLPE = [
    "parabéns", "contemplado", "benefício exclusivo", "últimos dígitos do cpf",
    "clique no link", "carro zero", "pix imediato", "ganhou", "prêmio", "sorteio",
    "transferência imediata", "oferta imperdível", "bônus garantido", "resgate seu benefício"
]

KEYWORDS_MARKETING = [
    "desconto", "promoção", "ganhe", "oferta", "cupom", "publicidade",
    "cashback", "black friday", "frete grátis", "oferta relâmpago"
]


def classificar_email(email_content: str) -> str:

    email_content = re.sub(r"\s+", " ", email_content).strip()

    if not email_content or len(email_content.split()) < 3:
        print("[LOG] Email muito curto → 'Improdutivo'")
        return "Improdutivo"

    lower_content = email_content.lower()

    if any(k in lower_content for k in KEYWORDS_GOLPE):
        print("[LOG] Palavra-chave de golpe detectada → 'Improdutivo'")
        return "Improdutivo"

    if any(k in lower_content for k in KEYWORDS_MARKETING):
        print("[LOG] Palavra-chave de marketing detectada → 'Improdutivo'")
        return "Improdutivo"

    heuristica_produtivo = any(k in lower_content for k in KEYWORDS_PRODUTIVO)

    payload = {
        "inputs": email_content,
        "parameters": {
            "candidate_labels": CANDIDATE_LABELS,
            "multi_label": False
        },
        "options": {"wait_for_model": True}
    }

    for attempt in range(2):
        try:
            response = requests.post(
                HF_API_URL, headers=HEADERS, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()

            if "labels" in result and "scores" in result:
                labels = result["labels"]
                scores = result["scores"]

                print("\n[LOG] --- RESULTADO IA ---")
                for label, score in zip(labels, scores):
                    print(f"[LOG] {label}: {score:.4f}")
                print("[LOG] ----------------------")

                top_score = scores[0]
                second_score = scores[1] if len(scores) > 1 else 0
                top_label = labels[0]
                final_label = LABEL_MAP.get(top_label, "Improdutivo")

                if top_score < CONFIDENCE_THRESHOLD or (top_score - second_score) < CONFIDENCE_MARGIN:
                    print(
                        f"[LOG] Confiança baixa ({top_score:.2f}) → fallback")
                    return fallback_classificacao(email_content, heuristica_produtivo)

                print(
                    f"[LOG] Escolhido: '{final_label}' (confiança: {top_score:.2f})")
                return final_label

            print("[LOG] Resposta inesperada da IA → fallback")
            return fallback_classificacao(email_content, heuristica_produtivo)

        except requests.exceptions.Timeout:
            print(f"[LOG] Timeout na API, tentativa {attempt+1}/3...")
            time.sleep(2)
        except Exception as e:
            print(f"[LOG] Erro na API: {e}")
            time.sleep(2)

    print("[LOG] Todas as tentativas falharam → fallback")
    return fallback_classificacao(email_content, heuristica_produtivo)


def fallback_classificacao(email_content: str, heuristica_produtivo: bool) -> str:
    lower_content = email_content.lower()
    if any(k in lower_content for k in KEYWORDS_GOLPE):
        return "Improdutivo"
    if any(k in lower_content for k in KEYWORDS_MARKETING):
        return "Improdutivo"
    if heuristica_produtivo:
        return "Produtivo"
    return "Improdutivo"