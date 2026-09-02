import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
from io import BytesIO

# Configuração da Página
st.set_page_config(
    page_title="Plataforma Edáfica Universal",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS para o Modo Escuro
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

# --- INTERFACE ---
st.title("🌱 Plataforma de Organização e Análise de Solo")
st.subheader("Cadastro Livre de Amostras e Comparação de Ambientes")
st.markdown("---")

# BARRA LATERAL: Cadastro e Atualização
st.sidebar.header("📥 Cadastrar ou Atualizar Amostra")
with st.sidebar.form(key="formulario_solo", clear_on_submit=True):
    novo_ambiente = st.text_input("Ambiente de Origem:", placeholder="Ex: PEMA, Flona...").strip().upper()
    nova_parcela = st.text_input("ID/Código da Parcela:", placeholder="Ex: R-01...").strip().upper()
    
    st.markdown("---")
    st.caption("Digite livremente usando ponto ou vírgula (Ex: 0.58 ou 0,99).")
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
                    nova_linha = pd.DataFrame([{
                        'Ambiente_Origem': novo_ambiente, 'ID_Parcela': nova_parcela, 
                        'pH': np.round(v_ph, 2), 'Condutividade (µS/cm)': np.round(v_cond, 2), 
                        'Argila (%)': np.round(v_arg, 2), 'Materia_Organica (%)': np.round(v_mo, 2), 'Altitude (m)': np.round(v_alt, 1)
                    }])
                    df = pd.concat([df, nova_linha], ignore_index=True)
                
                df.to_csv(ARQUIVO_BANCO, index=False)
                st.sidebar.success("Dados salvos com precisão!")
                st.rerun()
        except ValueError:
            st.sidebar.error("Erro: Preencha apenas números válidos!")

# BARRA LATERAL: Nova Seção de Exclusão Múltipla Avançada
st.sidebar.markdown("---")
st.sidebar.header("🗑️ Remover Múltiplas Amostras")

deletar_ambiente = st.sidebar.selectbox("1. Escolha o Ambiente:", [""] + list(df['Ambiente_Origem'].unique()))

if deletar_ambiente != "":
    # Filtra e lista apenas os códigos das parcelas que pertencem a esse ambiente escolhido
    parcelas_disponiveis = df[df['Ambiente_Origem'] == deletar_ambiente]['ID_Parcela'].unique()
    
    # Caixa de multisseleção onde você marca várias de uma só vez
    parcelas_selecionadas = st.sidebar.multiselect("2. Selecione as parcelas para deletar:", options=parcelas_disponiveis)
    
    if st.sidebar.button("❌ Excluir Selecionadas Permanentemente"):
        if not parcelas_selecionadas:
            st.sidebar.warning("Selecione pelo menos uma parcela!")
        else:
            # Filtra o banco de dados removendo todas as linhas marcadas de uma só vez
            df = df[~((df['Ambiente_Origem'] == deletar_ambiente) & (df['ID_Parcela'].isin(parcelas_selecionadas)))]
            df.to_csv(ARQUIVO_BANCO, index=False)
            st.sidebar.success(f"{len(parcelas_selecionadas)} parcela(s) removida(s) com sucesso!")
            st.rerun()

# Seção de Créditos ao Desenvolvedor
st.sidebar.markdown("---")
st.sidebar.markdown("""<div class="dev-box"><strong style='color: #00e676; font-size: 14px;'>💻 DESENVOLVEDOR DO SISTEMA</strong><br><span style='font-size: 16px; font-weight: bold;'>Thiago Araújo de Vasconcelos</span><br><span style='color: #a3a8b4; font-size: 12px;'>Plataforma Edáfica de Análise Ecológica</span></div>""", unsafe_allow_html=True)

# ABAS PRINCIPAIS
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
