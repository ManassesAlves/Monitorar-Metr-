import requests
import json
import os
import sys

# --- CONFIGURAÇÕES VIA VARIÁVEIS DE AMBIENTE ---
# O GitHub vai injetar esses valores na hora de rodar
TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL_API = "https://www.diretodostrens.com.br/api/status"
ARQUIVO_ESTADO = "estado_metro.json"

def enviar_telegram(mensagem):
    if not TOKEN or not CHAT_ID:
        print("ERRO: Tokens não configurados.")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def carregar_estado_anterior():
    """Lê o arquivo JSON salvo no repositório."""
    if os.path.exists(ARQUIVO_ESTADO):
        with open(ARQUIVO_ESTADO, 'r') as f:
            return json.load(f)
    return {}

def salvar_estado_atual(estado):
    """Salva o estado atual no arquivo JSON."""
    with open(ARQUIVO_ESTADO, 'w') as f:
        json.dump(estado, f, indent=4)

def main():
    print("--- Iniciando Verificação ---")
    
    # 1. Carrega o passado
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
                descricao = linha.get('descricao')
                
                # Se a linha é nova ou mudou de status
                if nome not in estado_anterior or estado_anterior[nome] != status_atual:
                    # Se não é a primeira vez que rodamos (tem histórico), avisa
                    if estado_anterior: 
                        emoji = "✅" if "Normal" in status_atual else "⚠️"
                        msg = (
                            f"{emoji} **Atualização {nome}**\n"
                            f"De: {estado_anterior.get(nome, 'Desconhecido')}\n"
                            f"Para: **{status_atual}**"
                        )
                        if descricao and "Normal" not in status_atual:
                            msg += f"\nObs: _{descricao}_"
                        
                        print(f"Mudança: {nome}")
                        enviar_telegram(msg)
                        houve_mudanca = True
                    
                    # Atualiza o estado na memória
                    novo_estado[nome] = status_atual
            
            # 2. Salva o futuro (se houve mudança, atualiza o JSON)
            if houve_mudanca or not estado_anterior:
                salvar_estado_atual(novo_estado)
                print("Estado atualizado salvo no JSON.")
            else:
                print("Nenhuma mudança detectada.")
                
        else:
            print(f"Erro na API: {response.status_code}")
            sys.exit(1) # Força erro para o GitHub avisar
            
    except Exception as e:
        print(f"Erro crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
