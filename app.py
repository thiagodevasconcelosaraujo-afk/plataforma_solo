import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from io import BytesIO

st.set_page_config(page_title="Plataforma Edáfica", page_icon="🌱", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stTabs [data-baseweb="tab"] { font-size: 18px; font-weight: bold; color: #a3a8b4; }
    .stTabs [data-baseweb="tab"]:hover { color: #00e676; }
    .stTabs [aria-selected="true"] { color: #00e676 !important; border-bottom-color: #00e676 !important; }
    .dev-box { background-color: #1e222b; padding: 15px; border-radius: 8px; border-left: 4px solid #00e676; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

ARQUIVO_BANCO = "banco_solo.csv"
ARQUIVO_CREDENCIAIS = ".env_admin.csv"
COLUNAS_ESPERADAS = ['Ambiente_Origem', 'ID_Parcela', 'pH', 'Condutividade (µS/cm)', 'Argila (%)', 'Materia_Organica (%)', 'Altitude (m)']

def inicializar_banco(forcar=False):
    if forcar or not os.path.exists(ARQUIVO_BANCO):
        np.random.seed(42)
        dados = {
            'Ambiente_Origem': ['ÁREA A (SAVANA)'] * 20 + ['ÁREA B (FLORESTA)'] * 20,
            'ID_Parcela': [f"P-{i:02d}" for i in range(1, 21)] * 2,
            'pH': np.round(np.concatenate([np.random.uniform(4.2, 5.5, 20), np.random.uniform(3.8, 4.8, 20)]), 2),
            'Condutividade (µS/cm)': np.round(np.concatenate([np.random.uniform(10, 50, 20), np.random.uniform(40, 120, 20)]), 2),
            'Argila (%)': np.round(np.concatenate([np.random.uniform(5, 25, 20), np.random.uniform(30, 65, 20)]), 2),
            'Materia_Organica (%)': np.round(np.concatenate([np.random.uniform(1.2, 3.0, 20), np.random.uniform(3.5, 7.0, 20)]), 2),
            'Altitude (m)': np.round(np.concatenate([np.random.uniform(120, 350, 20), np.random.uniform(80, 200, 20)]), 1)
        }
        pd.DataFrame(dados).to_csv(ARQUIVO_BANCO, index=False)

inicializar_banco()

try:
    df = pd.read_csv(ARQUIVO_BANCO)
    if not all(col in df.columns for col in COLUNAS_ESPERADAS) or df.empty:
        raise ValueError()
except:
    inicializar_banco(forcar=True)
    df = pd.read_csv(ARQUIVO_BANCO)

# ==========================================
# 🔑 FUNÇÕES AUXILIARES DE TEXTO PARA CREDENCIAIS
# ==========================================
def salvar_credenciais(nome, senha):
    with open(ARQUIVO_CREDENCIAIS, "w", encoding="utf-8") as f:
        f.write(f"{nome},{senha}")

def ler_credenciais():
    if os.path.exists(ARQUIVO_CREDENCIAIS):
        try:
            with open(ARQUIVO_CREDENCIAIS, "r", encoding="utf-8") as f:
                linha = f.read().strip()
                if "," in linha:
                    partes = linha.split(",")
                    return partes[0], partes[1]
        except:
            return None, None
    return None, None

# ==========================================
# 🔑 GERENCIAMENTO DE SESSÃO PERSISTENTE
# ==========================================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "nome_usuario" not in st.session_state:
    st.session_state.nome_usuario = ""

st.sidebar.header("🔑 Controle de Acesso")
est_bloqueado = True

admin_nome_salvo, admin_senha_salva = ler_credenciais()

if st.session_state.autenticado:
    st.sidebar.success(f"🟢 Seja bem-vindo, {st.session_state.nome_usuario}!")
    if st.sidebar.button("🚪 Sair do Modo Admin"):
        st.session_state.autenticado = False
        st.session_state.nome_usuario = ""
        st.rerun()
    est_bloqueado = False
else:
    modo_acesso = st.sidebar.selectbox("Tipo de Usuário:", ["👁️ Convidado (Leitura)", "⚡ Administrador (Editor)"])
    
    if modo_acesso == "⚡ Administrador (Editor)":
        if admin_nome_salvo is None:
            st.sidebar.warning("🚨 Nenhum administrador cadastrado!")
            st.sidebar.subheader("Cadastro do Administrador")
            novo_nome = st.sidebar.text_input("Seu Nome:", key="reg_nome").strip()
            nova_senha = st.sidebar.text_input("Senha (4 dígitos):", type="password", max_chars=4, key="reg_senha").strip()
            
            if st.sidebar.button("💾 Efetuar Primeiro Cadastro"):
                if not novo_nome or len(nova_senha) != 4 or not nova_senha.isdigit():
                    st.sidebar.error("Insira um nome e uma senha válida de 4 números!")
                else:
                    salvar_credenciais(novo_nome, nova_senha)
                    st.session_state.autenticado = True
                    st.session_state.nome_usuario = novo_nome
                    st.rerun()
        else:
            nome_input = st.sidebar.text_input("Nome de Usuário:", key="login_nome").strip()
            senha_input = st.sidebar.text_input("Senha de 4 dígitos:", type="password", max_chars=4, key="login_senha").strip()
            
            if st.sidebar.button("🔓 Efetuar Login"):
                if nome_input.lower() == admin_nome_salvo.lower() and senha_input == admin_senha_salva:
                    st.session_state.autenticado = True
                    st.session_state.nome_usuario = admin_nome_salvo
                    st.rerun()
                else:
                    st.sidebar.error("Usuário ou Senha incorretos!")
    else:
        st.sidebar.info("Modo Convidado ativo.")

st.sidebar.markdown("---")

# ==========================================
# 📥 CADASTRO E ATUALIZAÇÃO (COMPORTAMENTO CONDICIONAL)
# ==========================================
st.sidebar.header("📥 Cadastrar ou Atualizar Amostra")
with st.sidebar.form(key="formulario_solo", clear_on_submit=True):
    novo_ambiente = st.text_input("Ambiente de Origem:", placeholder="Ex: PEMA, Flona...", disabled=est_bloqueado).strip().upper()
    nova_parcela = st.text_input("ID/Código da Parcela:", placeholder="Ex: R-01...", disabled=est_bloqueado).strip().upper()
    st.markdown("---")
    input_ph = st.text_input("pH do Solo:", value="4.50", disabled=est_bloqueado).strip()
    input_condutividade = st.text_input("Condutividade (µS/cm):", value="25.00", disabled=est_bloqueado).strip()
    input_argila = st.text_input("Teor de Argila (%):", value="15.00", disabled=est_bloqueado).strip()
    input_mo = st.text_input("Matéria Orgânica (%):", value="2.00", disabled=est_bloqueado).strip()
    input_altitude = st.text_input("Altitude do Ponto (m):", value="150", disabled=est_bloqueado).strip()
    botao_salvar = st.form_submit_button(label="💾 Salvar / Atualizar Dados", disabled=est_bloqueado)

if botao_salvar and not est_bloqueado:
    if not novo_ambiente or not nova_parcela:
        st.sidebar.error("Preencha o Ambiente de Origem e o ID da Parcela!")
    else:
        try:
            v_ph = float(input_ph.replace(',', '.'))
            v_cond = float(input_condutividade.replace(',', '.'))
            v_arg = float(input_argila.replace(',', '.'))
            v_mo = float(input_mo.replace(',', '.'))
            v_alt = float(input_altitude.replace(',', '.'))
            if not (0 <= v_ph <= 14) or not (0 <= v_arg <= 100) or not (0 <= v_mo <= 100):
                st.sidebar.error("Erro: Valores fora dos limites permitidos!")
            else:
                existe_registro = ((df['Ambiente_Origem'] == novo_ambiente) & (df['ID_Parcela'] == nova_parcela)).any()
                if existe_registro:
                    idx = df[(df['Ambiente_Origem'] == novo_ambiente) & (df['ID_Parcela'] == nova_parcela)].index
                    df.loc[idx, 'pH'] = np.round(v_ph, 2)
                    df.loc[idx, 'Condutividade (µS/cm)'] = np.round(v_cond, 2)
                    df.loc[idx, 'Argila (%)'] = np.round(v_arg, 2)
                    df.loc[idx, 'Materia_Organica (%)'] = np.round(v_mo, 2)
                    df.loc[idx, 'Altitude (m)'] = np.round(v_alt, 1)
                else:
                    nova_linha = pd.DataFrame([{'Ambiente_Origem': novo_ambiente, 'ID_Parcela': nova_parcela, 'pH': np.round(v_ph, 2), 'Condutividade (µS/cm)': np.round(v_cond, 2), 'Argila (%)': np.round(v_arg, 2), 'Materia_Organica (%)': np.round(v_mo, 2), 'Altitude (m)': np.round(v_alt, 1)}])
                    df = pd.concat([df, nova_linha], ignore_index=True)
                df.to_csv(ARQUIVO_BANCO, index=False)
                st.sidebar.success("Dados salvos!")
                st.rerun()
        except ValueError:
            st.sidebar.error("Erro: Preencha apenas números válidos!")

st.sidebar.markdown("---")

# ==========================================
# 🗑️ REMOVER AMOSTRAS (COMPORTAMENTO CONDICIONAL)
# ==========================================
st.sidebar.header("🗑️ Remover Múltiplas Amostras")
deletar_ambiente = st.sidebar.selectbox("1. Escolha o Ambiente:", [""] + list(df['Ambiente_Origem'].unique()), disabled=est_bloqueado)

if deletar_ambiente != "" and not est_bloqueado:
    parcelas_disponiveis = df[df['Ambiente_Origem'] == deletar_ambiente]['ID_Parcela'].unique()
    parcelas_selecionadas = st.sidebar.multiselect("2. Selecione as parcelas:", options=parcelas_disponiveis)
    if st.sidebar.button("❌ Excluir Selecionadas"):
        if not parcelas_selecionadas:
            st.sidebar.warning("Selecione pelo menos uma parcela!")
        else:
            df = df[~((df['Ambiente_Origem'] == deletar_ambiente) & (df['ID_Parcela'].isin(parcelas_selecionadas)))]
            df.to_csv(ARQUIVO_BANCO, index=False)
            st.sidebar.success("Removidas com sucesso!")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("""<div class="dev-box"><strong style='color: #00e676; font-size: 14px;'>💻 DESENVOLVEDOR DO SISTEMA</strong><br><span style='font-size: 16px; font-weight: bold;'>Thiago Araújo de Vasconcelos</span><br><span style='color: #a3a8b4; font-size: 12px;'>Plataforma Edáfica de Análise Ecológica</span></div>""", unsafe_allow_html=True)

# ==========================================
# 📊 CONTEÚDO PRINCIPAL (EXIBIÇÃO INCONDICIONAL)
# ==========================================
