import streamlit as st
import os

ARQUIVO_CREDENCIAIS = ".env_admin.csv"

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

def gerenciar_login():
    # Inicializa variáveis na sessão
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if "nome_usuario" not in st.session_state:
        st.session_state.nome_usuario = ""

    st.sidebar.header("🔑 Controle de Acesso")
    est_bloqueado = True

    admin_nome_salvo, admin_senha_salva = ler_credenciais()

    # Fluxo de exibição na barra lateral
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

    return est_bloqueado
