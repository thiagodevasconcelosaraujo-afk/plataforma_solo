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
with st.sidebar.form(key="formulario_solo", clear_on_submit=True):
    novo_ambiente = st.text_input("Ambiente de Origem (Ex: PEMA, Flona):", placeholder="Digite o local...").strip().upper()
    nova_parcela = st.text_input("ID/Código da Parcela (Ex: R-01):", placeholder="Código identificador...").strip().upper()
    st.markdown("---")
    input_ph = st.text_input("pH do Solo:", value="4.50").strip()
    input_condutividade = st.text_input("Condutividade (µS/cm):", value="25.00").strip()
    input_argila = st.text_input("Teor de Argila (%):", value="15.00").strip()
    input_mo = st.text_input("Matéria Orgânica (%):", value="2.00").strip()
    input_altitude = st.text_input("Altitude do Ponto (m):", value="150").strip()
    botao_salvar = st.form_submit_button(label="💾 Salvar / Atualizar Dados")

if botao_salvar:
    if not novo_ambiente or not nova_parcela:
        st.sidebar.error("Preencha o Ambiente de Origem e o ID da Parcela!")
    else:
        try:
            novo_ph = float(input_ph.replace(',', '.'))
            nova_condutividade = float(input_condutividade.replace(',', '.'))
            nova_argila = float(input_argila.replace(',', '.'))
            nova_mo = float(input_mo.replace(',', '.'))
            nova_altitude = float(input_altitude.replace(',', '.'))
            if not (0 <= novo_ph <= 14) or not (0 <= nova_argila <= 100) or not (0 <= nova_mo <= 100):
                st.sidebar.error("Erro: Valores fora dos limites permitidos!")
            else:
                existe_registro = ((df['Ambiente_Origem'] == novo_ambiente) & (df['ID_Parcela'] == nova_parcela)).any()
                if existe_registro:
                    idx = df[(df['Ambiente_Origem'] == novo_ambiente) & (df['ID_Parcela'] == nova_parcela)].index
                    df.loc[idx, 'pH'] = np.round(novo_ph, 2)
                    df.loc[idx, 'Condutividade (µS/cm)'] = np.round(nova_condutividade, 2)
                    df.loc[idx, 'Argila (%)'] = np.round(nova_argila, 2)
                    df.loc[idx, 'Materia_Organica (%)'] = np.round(nova_mo, 2)
                    df.loc[idx, 'Altitude (m)'] = np.round(nova_altitude, 1)
                else:
                    nova_linha = pd.DataFrame([{'Ambiente_Origem': novo_ambiente, 'ID_Parcela': nova_parcela, 'pH': np.round(novo_ph, 2), 'Condutividade (µS/cm)': np.round(nova_condutividade, 2), 'Argila (%)': np.round(nova_argila, 2), 'Materia_Organica (%)': np.round(nova_mo, 2), 'Altitude (m)': np.round(nova_altitude, 1)}])
                    df = pd.concat([df, nova_linha], ignore_index=True)
                df.to_csv(ARQUIVO_BANCO, index=False)
                st.sidebar.success("Dados processados com sucesso!")
                st.rerun()
        except ValueError:
            st.sidebar.error("Erro: Preencha apenas números válidos nos campos!")

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
    col2.metric(label="Média de Condutividade", value=f"{df_filtrado['Condutividade (µS/cm)'].mean():.2f} µS/cm")
    col3.metric(label="Teor Médio de Argila", value=f"{df_filtrado['Argila (%)'].mean():.2f}%")
    col4.metric(label="Matéria Orgânica Média", value=f"{df_filtrado['Materia_Organica (%)'].mean():.2f}%")
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados_Solo')
    st.download_button(label="📥 Baixar Banco de Dados Completo (.Excel)", data=output.getvalue(), file_name="banco_solo.xlsx")
    st.dataframe(df, use_container_width=True)

with aba_comparativo:
    st.write("### Análise Multivariada Comparativa de Propriedades")
    st.caption("Gráfico integrado de colunas agrupadas avaliando múltiplas assinaturas do solo simultaneamente.")
    atributos_selecionados = st.multiselect("Selecione as propriedades do solo para comparar simultaneamente:", ['pH', 'Condutividade (µS/cm)', 'Argila (%)', 'Materia_Organica (%)', 'Altitude (m)'], default=['pH', 'Materia_Organica (%)', 'Argila (%)'])
    if not atributos_selecionados:
        st.warning("Selecione pelo menos um atributo.")
    else:
        df_melt = df.groupby('Ambiente_Origem')[atributos_selecionados].mean().reset_index()
        df_melt = pd.melt(df_melt, id_vars=['Ambiente_Origem'], value_vars=atributos_selecionados, var_name='Propriedade', value_name='Valor_Medio')
        df_melt['Valor_Medio'] = np.round(df_melt['Valor_Medio'], 2)
        fig_colunas = px.bar(df_melt, x='Propriedade', y='Valor_Medio', color='Ambiente_Origem', barmode='group', text='Valor_Medio', template="plotly_dark", height=500)
        fig_colunas.update_traces(textposition='outside', textfont_size=12, cliponaxis=False)
        st.plotly_chart(fig_colunas, use_container_width=True)
