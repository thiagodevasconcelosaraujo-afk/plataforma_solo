import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from io import BytesIO

st.set_page_config(page_title="Plataforma Edáfica Universal", page_icon="🌱", layout="wide", initial_sidebar_state="expanded")

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

def inicializar_banco():
    if not os.path.exists(ARQUIVO_BANCO):
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
df = pd.read_csv(ARQUIVO_BANCO)

st.title("🌱 Plataforma de Organização e Análise de Solo")
st.subheader("Cadastro Livre de Amostras e Comparação de Ambientes")
st.markdown("---")

st.sidebar.header("📥 Cadastrar ou Atualizar Amostra")

# Gerenciamento do estado dos inputs para os botões funcionarem de forma reativa
for chave, padrao in [('sb_ph', 4.50), ('sb_cond', 25.00), ('sb_arg', 15.00), ('sb_mo', 2.00), ('sb_alt', 150.0)]:
    if chave not in st.session_state:
        st.session_state[chave] = padrao

# Função auxiliar para recalcular e ajustar os valores decimais complexos (Ex: 0.99 -> 1.00)
def ajustar_valor(chave, incremento):
    try:
        atual = float(st.session_state[chave])
        st.session_state[chave] = np.round(max(0.0, atual + incremento), 2)
    except:
        pass

novo_ambiente = st.sidebar.text_input("Ambiente de Origem:", placeholder="Ex: PEMA, Flona...").strip().upper()
nova_parcela = st.sidebar.text_input("ID/Código da Parcela:", placeholder="Ex: R-01...").strip().upper()
st.sidebar.markdown("---")

# Interface de botões laterais acoplados para celular (+1 casa decimal e +10 rápidos)
st.sidebar.markdown("**pH do Solo**")
c1, c2, c3 = st.sidebar.columns([2, 1, 1])
input_ph = c1.text_input("pH:", value=f"{st.session_state['sb_ph']:.2f}", label_visibility="collapsed")
if c2.button("+0.01", key="b_ph1"): ajustar_valor('sb_ph', 0.01); st.rerun()
if c3.button("+10", key="b_ph10"): ajustar_valor('sb_ph', 10.0); st.rerun()

st.sidebar.markdown("**Condutividade (µS/cm)**")
c1, c2, c3 = st.sidebar.columns([2, 1, 1])
input_condutividade = c1.text_input("Cond:", value=f"{st.session_state['sb_cond']:.2f}", label_visibility="collapsed")
if c2.button("+0.01", key="b_co1"): ajustar_valor('sb_cond', 0.01); st.rerun()
if c3.button("+10", key="b_co10"): ajustar_valor('sb_cond', 10.0); st.rerun()

st.sidebar.markdown("**Teor de Argila (%)**")
c1, c2, c3 = st.sidebar.columns([2, 1, 1])
input_argila = c1.text_input("Arg:", value=f"{st.session_state['sb_arg']:.2f}", label_visibility="collapsed")
if c2.button("+0.01", key="b_ar1"): ajustar_valor('sb_arg', 0.01); st.rerun()
if c3.button("+10", key="b_ar10"): ajustar_valor('sb_arg', 10.0); st.rerun()

st.sidebar.markdown("**Matéria Orgânica (%)**")
c1, c2, c3 = st.sidebar.columns([2, 1, 1])
input_mo = c1.text_input("MO:", value=f"{st.session_state['sb_mo']:.2f}", label_visibility="collapsed")
if c2.button("+0.01", key="b_mo1"): ajustar_valor('sb_mo', 0.01); st.rerun()
if c3.button("+10", key="b_mo10"): ajustar_valor('sb_mo', 10.0); st.rerun()

st.sidebar.markdown("**Altitude (m)**")
c1, c2, c3 = st.sidebar.columns([2, 1, 1])
input_altitude = c1.text_input("Alt:", value=f"{st.session_state['sb_alt']:.1f}", label_visibility="collapsed")
if c2.button("+0.1", key="b_al1"): ajustar_valor('sb_alt', 0.1); st.rerun()
if c3.button("+10", key="b_al10"): ajustar_valor('sb_alt', 10.0); st.rerun()

st.sidebar.markdown("---")
botao_salvar = st.sidebar.button("💾 Salvar / Atualizar Dados")

if botao_salvar:
    if not novo_ambiente or not nova_parcela:
        st.sidebar.error("Preencha o Ambiente de Origem e o ID da Parcela!")
    else:
        try:
            v_ph = np.round(float(input_ph.replace(',', '.')), 2)
            v_cond = np.round(float(input_condutividade.replace(',', '.')), 2)
            v_arg = np.round(float(input_argila.replace(',', '.')), 2)
            v_mo = np.round(float(input_mo.replace(',', '.')), 2)
            v_alt = np.round(float(input_altitude.replace(',', '.')), 1)
            
            if not (0 <= v_ph <= 14) or not (0 <= v_arg <= 100) or not (0 <= v_mo <= 100):
                st.sidebar.error("Erro: Valores fora dos limites permitidos!")
            else:
                existe_registro = ((df['Ambiente_Origem'] == novo_ambiente) & (df['ID_Parcela'] == nova_parcela)).any()
                if existe_registro:
                    idx = df[(df['Ambiente_Origem'] == novo_ambiente) & (df['ID_Parcela'] == nova_parcela)].index
                    df.loc[idx, 'pH'] = v_ph
                    df.loc[idx, 'Condutividade (µS/cm)'] = v_cond
                    df.loc[idx, 'Argila (%)'] = v_arg
                    df.loc[idx, 'Materia_Organica (%)'] = v_mo
                    df.loc[idx, 'Altitude (m)'] = v_alt
                else:
                    nova_linha = pd.DataFrame([{'Ambiente_Origem': novo_ambiente, 'ID_Parcela': nova_parcela, 'pH': v_ph, 'Condutividade (µS/cm)': v_cond, 'Argila (%)': v_arg, 'Materia_Organica (%)': v_mo, 'Altitude (m)': v_alt}])
                    df = pd.concat([df, nova_linha], ignore_index=True)
                
                df.to_csv(ARQUIVO_BANCO, index=False)
                st.sidebar.success("Dados salvos perfeitamente!")
                st.rerun()
        except ValueError:
            st.sidebar.error("Erro: Verifique os números digitados!")

st.sidebar.markdown("---")
st.sidebar.header("🗑️ Remover Amostra do Sistema")
with st.sidebar.form(key="formulario_deletar", clear_on_submit=True):
    deletar_ambiente = st.selectbox("Ambiente da amostra:", [""] + list(df['Ambiente_Origem'].unique()))
    deletar_parcela = st.text_input("ID da Parcela:").strip().upper()
    botao_deletar = st.form_submit_button(label="❌ Excluir Permanentemente")

if botao_deletar:
    if deletar_ambiente == "" or not deletar_parcela:
        st.sidebar.error("Selecione o Ambiente e preencha o ID!")
    else:
        alvo = df[(df['Ambiente_Origem'] == deletar_ambiente) & (df['ID_Parcela'] == deletar_parcela)]
        if alvo.empty:
            st.sidebar.error("Nenhuma amostra encontrada.")
        else:
            df = df.drop(alvo.index)
            df.to_csv(ARQUIVO_BANCO, index=False)
            st.sidebar.success("Amostra excluída!")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("""<div class="dev-box"><strong style='color: #00e676; font-size: 14px;'>💻 DESENVOLVEDOR DO SISTEMA</strong><br><span style='font-size: 16px; font-weight: bold;'>Thiago Araújo de Vasconcelos</span><br><span style='color: #a3a8b4; font-size: 12px;'>Plataforma Edáfica de Análise Ecológica</span></div>""", unsafe_allow_html=True)

aba_geral, aba_comparativo = st.tabs(["📊 Visão Geral dos Dados", "📊 Painel de Comparação Gráfica"])

with aba_geral:
    st.write("### Painel Geral de Atributos do Solo")
    ambiente_sel = st.selectbox("Escolha o Ambiente:", df['Ambiente_Origem'].unique())
    df_filtrado = df[df['Ambiente_Origem'] == ambiente_sel]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric(label="Média de pH", value=f"{df_filtrado['pH'].mean():.2f}")
