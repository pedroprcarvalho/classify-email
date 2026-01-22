import re
import os
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HF_API_TOKEN")
if not HF_TOKEN:
    raise ValueError("Defina HF_TOKEN ou HF_API_TOKEN no .env")

client = InferenceClient(api_key=HF_TOKEN)

def limpar_raciocinio_interno(texto: str) -> str:
    padroes = [
        r"(?i)(let me|i should|they want|maybe|so i|alright|let's|okay,|então vou|preciso|vou pensar|deixa eu).*",
        r"(?i)(analisando|pensando|raciocínio|planejando).*"
    ]

    for padrao in padroes:
        texto = re.sub(padrao, "", texto).strip()
    return texto

def extrair_resposta_final(texto: str) -> str:
    texto = limpar_raciocinio_interno(texto)

    padrao = r"(?:Prezado|Prezada|Prezados|Olá|Caro|Cara|Bom dia|Boa tarde|Boa noite)[\s\S]+"
    match = re.search(padrao, texto, flags=re.IGNORECASE)
    if match:
        return match.group(0).strip()

    partes = texto.strip().split("\n\n")
    if len(partes) > 1:
        return limpar_raciocinio_interno(partes[-1].strip())

    return texto.strip()

def gerar_resposta_chat(texto_email: str, categoria: str) -> str:
    if categoria == "Produtivo": 
        prompt = (
            "Você é um assistente de uma empresa no ramo financeiro."
            "IMPORTANTE: Sua tarefa é responder APENAS com a mensagem final pronta para envio. "
            "PROIBIDO explicar raciocínio, planejar a resposta ou dar justificativas. "
            "NÃO escreva nada sobre o que você vai fazer, NEM descreva seus pensamentos. "
            "Responda SOMENTE em português, com uma mensagem clara, educada, profissional que atenda a necessidade do email.\n\n"
            f"Email recebido:\n{texto_email}\n\n"
            "Mensagem final:"
        )
    else: 
        prompt = (
            "Você é um assistente de uma empresa no ramo financeiro."
            "IMPORTANTE: Sua tarefa é responder APENAS com a mensagem final pronta para envio. "
            "PROIBIDO explicar raciocínio, planejar a resposta ou dar justificativas. "
            "NÃO escreva nada sobre o que você vai fazer, NEM descreva seus pensamentos. "
            "Responda SOMENTE em português, com uma mensagem curta, amigável e educada.\n\n"
            f"Email recebido:\n{texto_email}\n\n"
            "Mensagem final:"
        )

    try:
        completion = client.chat.completions.create(
            model="HuggingFaceTB/SmolLM3-3B",
            messages=[{"role": "user", "content": prompt}],
        )

        resposta = completion.choices[0].message["content"].strip() 

        resposta_final = extrair_resposta_final(resposta)

        print(f"[LOG] Resposta final:\n{resposta_final}\n")
        return resposta_final

    except Exception as e:
        print(f"[LOG] Erro ao gerar resposta via Hugging Face: {e}")
        return texto_fallback(categoria)

def texto_fallback(categoria: str) -> str:
    if categoria == "Produtivo":
        return "Obrigado pelo contato. Nossa equipe analisará sua solicitação em breve."
    else:
        return "Obrigado pelo seu email. Desejamos um ótimo dia!"

def resposta_sugerida(texto_email: str, categoria: str) -> str:
    return gerar_resposta_chat(texto_email, categoria)

gerar_resposta = gerar_resposta_chat