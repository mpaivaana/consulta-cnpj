import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import time
import csv
import os

from styles import apply_styles

st.set_page_config(
    page_title="Registro de Leads",
    page_icon="assets/favicon.ico",  
    layout="centered",
    initial_sidebar_state="expanded"
)

apply_styles()

if "informacoes" not in st.session_state:
    st.session_state.informacoes = {}
if "salvo" not in st.session_state:
    st.session_state.salvo = False

def buscar_cnpj(nome_empresa):
    query = f"{nome_empresa} CNPJ"
    url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    cnpj_pattern = r'\b\d{2}\.\d{3}\.\d{3}\/\d{4}-\d{2}\b'
    text_content = soup.get_text()  
    
    match = re.search(cnpj_pattern, text_content)
    if match:
        return match.group(0)
    return None


def buscar_informacoes_cnpj(cnpj):
    cnpj_cleaned = cnpj.replace('.', '').replace('/', '').replace('-', '')
    url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj_cleaned}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.RequestException:
        return None
    data = response.json()
    if "status" in data and data["status"] == "ERROR":
        return None
    return {
        'E-mail': data.get('email', 'Não encontrado'),
        'Telefone': data.get('telefone', 'Não encontrado'),
    }

csv_file_path = 'dados_leads.csv'

def salvar_dados_csv(dados):
    colunas = ['Lead', 'Nome da Empresa', 'E-mail', 'Telefone', 'CNPJ', 'Número de Cobranças', 'Mensagem']
    if not os.path.isfile(csv_file_path):
        with open(csv_file_path, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=',')
            writer.writerow(colunas)
    with open(csv_file_path, mode='a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file, delimiter=',')
        writer.writerow(dados)

st.image("assets/header.png", use_column_width=True)
st.title("Registro de Leads para contato")

mensagem_sucesso = st.empty()

lead = st.text_input("Insira o Lead:", value=st.session_state.get('lead', ''))
nome_empresa = st.text_input("Insira o nome da empresa:", value=st.session_state.get('nome_empresa', ''))

if st.button("Buscar Informações"):
    if nome_empresa:
        with st.spinner("Buscando informações..."):
            cnpj = buscar_cnpj(nome_empresa)
            if cnpj:
                st.session_state.cnpj = cnpj
                informacoes = buscar_informacoes_cnpj(cnpj)
                st.session_state.informacoes = informacoes if informacoes else {}
                if informacoes:
                    with st.container(border=True):
                        st.write("CNPJ encontrado:", cnpj)
                        st.write("E-mail:", informacoes.get('E-mail', 'Não encontrado'))
                        st.write("Telefone:", informacoes.get('Telefone', 'Não encontrado'))
                else:
                    st.write("Não foi possível obter informações adicionais.")
            else:
                st.write("CNPJ não encontrado.")
    else:
        st.write("Por favor, insira um nome de empresa.")

if st.session_state.informacoes:
    novo_email = st.text_input("Alterar Email:", value=st.session_state.informacoes.get('E-mail', ''))
    novo_telefone = st.text_input("Alterar Telefone:", value=st.session_state.informacoes.get('Telefone', ''))
    novo_cnpj = st.text_input("Alterar CNPJ:", value=st.session_state.get('cnpj', ''))
    numero_cobrancas = st.text_input("Número de cobranças emitidas por mês:", value=st.session_state.get('numero_cobrancas', ''))
    mensagem = st.text_area("Mensagem:", value=st.session_state.get('mensagem', ''))

    if st.button("Salvar"):
        st.session_state.lead = lead
        st.session_state.nome_empresa = nome_empresa
        st.session_state.numero_cobrancas = numero_cobrancas
        st.session_state.mensagem = mensagem
        st.session_state.cnpj = novo_cnpj
        st.session_state.salvo = True

        dados = [
            lead,
            nome_empresa,
            novo_email,
            novo_telefone,
            novo_cnpj,
            numero_cobrancas,
            mensagem
        ]
        
        salvar_dados_csv(dados)

        sucesso_msg = (
            "*✔️ Dados salvos com sucesso!*\n"
            f"- *Lead:* {lead}\n"
            f"- *Nome da Empresa:* {nome_empresa}\n"
            f"- *E-mail:* {novo_email}\n"
            f"- *Telefone:* {novo_telefone}\n"
            f"- *CNPJ:* {novo_cnpj}\n"
            f"- *Número de Cobranças:* {numero_cobrancas}\n"
            f"- *Mensagem:* {mensagem}"
        )
        mensagem_sucesso.success(sucesso_msg)
        
        st.session_state.lead = " "
        st.session_state.nome_empresa = " "
        st.session_state.numero_cobrancas = " "
        st.session_state.mensagem = " "
        st.session_state.informacoes = {}
        st.session_state.cnpj = " "
        st.session_state.salvo = False 

        time.sleep(3)
        st.rerun()

st.image("assets/footer.png", use_column_width=True)