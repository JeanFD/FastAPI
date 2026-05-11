import streamlit as st
import requests
import time
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIGURAÇÕES ---
API_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="FastFocus Pomodoro", page_icon="🍅")

# --- GERENCIAMENTO DE ESTADO (SESSION STATE) ---
# O Streamlit roda o script inteiro a cada clique. 
# Precisamos do Session State para "lembrar" das variáveis entre os cliques.
if 'current_session_id' not in st.session_state:
    st.session_state['current_session_id'] = None
if 'end_time' not in st.session_state:
    st.session_state['end_time'] = None
if 'is_running' not in st.session_state:
    st.session_state['is_running'] = False

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.title("🍅 Menu")
menu_choice = st.sidebar.radio("Navegação", ["Timer", "Histórico", "Configurações"])

# --- FUNÇÃO AUXILIAR: COMUNICAÇÃO COM API ---
def create_session(task_name, minutes):
    try:
        payload = {"task_name": task_name, "work_minutes": minutes}
        response = requests.post(f"{API_URL}/sessions/", json=payload)
        response.raise_for_status() # Lança erro se não for 200/201
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Erro: O Backend parece estar desligado.")
        return None

def start_timer_api(session_id):
    try:
        response = requests.post(f"{API_URL}/sessions/{session_id}/start")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro do Backend: {response.text}")
            return None
    except Exception as e:
        st.error(f"Erro de conexão: {e}")

# --- PÁGINA: TIMER ---
if menu_choice == "Timer":
    st.title("⏱️ Pomodoro Timer")

    # 1. Formulário de Criação (Só aparece se não tiver sessão ativa)
    if st.session_state['current_session_id'] is None:
        with st.container(border=True):
            st.subheader("Nova Tarefa")
            task_name = st.text_input("O que vamos focar hoje?", placeholder="Ex: Estudar FastApi")
            duration = st.slider("Tempo de foco (min)", 1, 60, 25)
            
            if st.button("Criar Sessão", use_container_width=True):
                if task_name:
                    data = create_session(task_name, duration)
                    if data:
                        st.session_state['current_session_id'] = data['id']
                        st.session_state['task_name'] = data['task_name']
                        st.session_state['work_minutes'] = data['work_minutes']
                        st.rerun() # Recarrega a página para atualizar o estado
                else:
                    st.warning("Dê um nome para a tarefa!")

    # 2. Área do Timer (Aparece quando a sessão existe)
    else:
        st.info(f"Tarefa Atual: **{st.session_state.get('task_name')}**")
        
        col1, col2 = st.columns(2)
        
        # Botão INICIAR
        if not st.session_state['is_running']:
            if col1.button("▶️ Iniciar Foco", type="primary", use_container_width=True):
                # Chama o backend para marcar a hora oficial de início
                resp = start_timer_api(st.session_state['current_session_id'])
                if resp:
                    # O Backend retorna quando deve acabar (ex: 18:55)
                    # Convertemos a string ISO para objeto datetime
                    end_time_str = resp['end_time'] 
                    st.session_state['end_time'] = datetime.fromisoformat(end_time_str)
                    st.session_state['is_running'] = True
                    st.rerun()

        # Botão CANCELAR/REINICIAR
        if col2.button("🔄 Cancelar / Nova Sessão"):
            # Limpa o estado para começar do zero
            st.session_state['current_session_id'] = None
            st.session_state['is_running'] = False
            st.session_state['end_time'] = None
            st.rerun()

        # 3. O LOOP VISUAL DO TIMER
        # Este é o "Front que conta", baseado na "Verdade do Back"
        if st.session_state['is_running'] and st.session_state['end_time']:
            timer_placeholder = st.empty() # Cria um espaço vazio para atualizar os números
            
            # Loop visual
            while True:
                now = datetime.now()
                # A diferença entre a HORA QUE O BACKEND DISSE PARA ACABAR e AGORA
                remaining = st.session_state['end_time'] - now
                
                if remaining.total_seconds() <= 0:
                    timer_placeholder.success("🎉 O tempo acabou! Bom trabalho!")
                    st.balloons()
                    # Aqui poderia ter um som ou notificação
                    break
                
                # Formatação MM:SS
                mins, secs = divmod(int(remaining.total_seconds()), 60)
                timer_text = f"{mins:02d}:{secs:02d}"
                
                # Atualiza o HTML do contador
                timer_placeholder.markdown(
                    f"<h1 style='text-align: center; font-size: 80px;'>{timer_text}</h1>", 
                    unsafe_allow_html=True
                )
                
                time.sleep(1) # Espera 1s antes de atualizar (não sobrecarrega CPU)

        # 4. Upload de Evidência (Formulário e Arquivo)
        if st.session_state['is_running'] == False and st.session_state['current_session_id']:
             st.write("---")
             st.write("Timer ainda não iniciado.")

# --- PÁGINA: HISTÓRICO ---
elif menu_choice == "Histórico":
    st.title("📜 Histórico de Sessões")
    
    if st.button("Atualizar Lista"):
        try:
            # Faz um GET na sua API
            response = requests.get(f"{API_URL}/sessions/")
            sessions = response.json()
            
            if sessions:
                df = pd.DataFrame(sessions)
                # Formata as colunas para ficar bonito
                st.dataframe(
                    df[["task_name", "work_minutes", "completed", "id"]],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.info("Nenhuma sessão encontrada.")
        except Exception as e:
            st.error(f"Erro ao buscar histórico: {e}")

# --- PÁGINA: CONFIGURAÇÕES ---
elif menu_choice == "Configurações":
    st.title("⚙️ Configurações")
    st.write(f"Conectado em: `{API_URL}`")
    st.write("Versão do Frontend: 1.0.0")