import cloudscraper # Biblioteca antibloqueio
import json
import csv
import os
import sys
from datetime import datetime, timedelta, timezone
import requests # Fallback caso precise

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_API = "https://www.diretodostrens.com.br/api/status"
ARQUIVO_ESTADO = "estado_metro.json"
ARQUIVO_HISTORICO = "historico_metro.csv"

LINHAS_COR = {
    "1": "Azul", "2": "Verde", "3": "Vermelha", "4": "Amarela", "5": "Lilás",
    "7": "Rubi", "8": "Diamante", "9": "Esmeralda", "10": "Turquesa",
    "11": "Coral", "12": "Safira", "13": "Jade", "15": "Prata"
}

def get_horario_sp():
    fuso_sp = timezone(timedelta(hours=-3))
    return datetime.now(fuso_sp)

def enviar_telegram(mensagem):
    if not TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data, timeout=10)
    except Exception as e:
        print(f"Erro Telegram: {e}")

def carregar_estado_anterior():
    if os.path.exists(ARQUIVO_ESTADO):
        try:
            with open(ARQUIVO_ESTADO, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def salvar_estado_atual(estado):
    with open(ARQUIVO_ESTADO, 'w') as f:
        json.dump(estado, f, indent=4)

def salvar_historico(nome_linha, status_novo, status_antigo, descricao):
    arquivo_existe = os.path.exists(ARQUIVO_HISTORICO)
    agora = get_horario_sp()
    try:
        with open(ARQUIVO_HISTORICO, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not arquivo_existe:
                writer.writerow(["Data", "Hora", "Dia_Semana", "Linha", "Status_Novo", "Status_Anterior", "Descricao"])
            writer.writerow([
                agora.strftime("%Y-%m-%d"), agora.strftime("%H:%M:%S"), agora.strftime("%A"),
                nome_linha, status_novo, status_antigo, descricao
            ])
    except Exception as e:
        print(f"Erro CSV: {e}")

def main():
    print("--- Iniciando Verificação (Modo Cloudscraper) ---")
    estado_anterior = carregar_estado_anterior()
    novo_estado = estado_anterior.copy()
    houve_mudanca = False
    
    # Cria um scraper especializado em passar por Cloudflare/WAF
    scraper = cloudscraper.create_scraper()

    try:
        # Tenta conectar usando o scraper em vez do requests puro
        response = scraper.get(URL_API, timeout=30)
        
        if response.status_code == 200:
            linhas = response.json()
            
            for linha in linhas:
                codigo = str(linha.get('codigo'))
                cor = LINHAS_COR.get(codigo, "")
                nome_formatado = f"Linha {codigo} - {cor}" if cor else f"Linha {codigo}"
                
                status_atual = linha.get('situacao')
                descricao = linha.get('descricao')
                
                chave_estado = f"L{codigo}"
                status_salvo = estado_anterior.get(chave_estado)
                
                if status_salvo and status_salvo != status_atual:
                    print(f"Mudança: {nome_formatado}")
                    emoji = "✅" if "Normal" in status_atual else "⚠️"
                    msg = (
                        f"{emoji} **{nome_formatado}**\n"
                        f"🔄 De: {status_salvo}\n"
                        f"➡️ Para: **{status_atual}**"
                    )
                    
                    if descricao and len(str(descricao).strip()) > 0:
                        msg += f"\n\n📢 **Detalhes:**\n_{descricao}_"
                    
                    enviar_telegram(msg)
                    salvar_historico(nome_formatado, status_atual, status_salvo, descricao)
                    houve_mudanca = True
                
                novo_estado[chave_estado] = status_atual
            
            if houve_mudanca or not estado_anterior:
                salvar_estado_atual(novo_estado)
            else:
                print("Tudo normal.")

        else:
            print(f"Erro API: {response.status_code}")
            print(f"Conteúdo: {response.text[:200]}") # Mostra o erro para debug
            sys.exit(1)

    except Exception as e:
        print(f"Erro Crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
