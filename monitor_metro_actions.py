import requests
import json
import csv
import os
import sys
from datetime import datetime, timedelta, timezone

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_API = "https://www.diretodostrens.com.br/api/status"
ARQUIVO_ESTADO = "estado_metro.json"
ARQUIVO_HISTORICO = "historico_metro.csv"

def get_horario_sp():
    """Retorna data/hora ajustada para São Paulo (UTC-3)"""
    fuso_sp = timezone(timedelta(hours=-3))
    return datetime.now(fuso_sp)

def enviar_telegram(mensagem):
    if not TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def carregar_estado_anterior():
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, 'r') as f:
            return json.load(f)
    return {}

def salvar_estado_atual(estado):
    with open(ARQUIVO_ESTADO, 'w') as f:
        json.dump(estado, f, indent=4)

def salvar_historico(nome_linha, status_novo, status_antigo, descricao):
    arquivo_existe = os.path.exists(ARQUIVO_HISTORICO)
    agora = get_horario_sp()
    
    with open(ARQUIVO_HISTORICO, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not arquivo_existe:
            writer.writerow(["Data", "Hora", "Dia_Semana", "Linha", "Status_Novo", "Status_Anterior", "Descricao"])
            
        writer.writerow([
            agora.strftime("%Y-%m-%d"),
            agora.strftime("%H:%M:%S"),
            agora.strftime("%A"),
            nome_linha,
            status_novo,
            status_antigo,
            descricao
        ])

def main():
    print("--- Iniciando Verificação ---")
    estado_anterior = carregar_estado_anterior()
    novo_estado = estado_anterior.copy()
    houve_mudanca = False
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (MonitorMetroGitHub/1.0)'}
        response = requests.get(URL_API, headers=headers, timeout=15)
        
        if response.status_code == 200:
            linhas = response.json()
            
            for linha in linhas:
                nome = f"Linha {linha.get('codigo')} - {linha.get('nome')}"
                status_atual = linha.get('situacao')
                descricao = linha.get('descricao') # Captura a descrição do problema
                
                # Se mudou de status
                if nome in estado_anterior and estado_anterior[nome] != status_atual:
                    status_antigo = estado_anterior[nome]
                    
                    # --- MONTAGEM DA MENSAGEM COM DESCRIÇÃO ---
                    emoji = "✅" if "Normal" in status_atual else "⚠️"
                    msg = (
                        f"{emoji} **{nome}**\n"
                        f"🔄 De: {status_antigo}\n"
                        f"➡️ Para: **{status_atual}**"
                    )
                    
                    # Verifica se existe descrição e se não está vazia
                    if descricao and len(str(descricao).strip()) > 0:
                        msg += f"\n\n📢 **Detalhes:**\n_{descricao}_"
                    # -------------------------------------------
                    
                    enviar_telegram(msg)
                    salvar_historico(nome, status_atual, status_antigo, descricao)
                    
                    print(f"Registrado: {nome} mudou para {status_atual}")
                    houve_mudanca = True
                
                # Atualiza memória
                novo_estado[nome] = status_atual
            
            if houve_mudanca or not estado_anterior:
                salvar_estado_atual(novo_estado)
            else:
                print("Sem mudanças.")
                
        else:
            print(f"Erro API: {response.status_code}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Erro crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
