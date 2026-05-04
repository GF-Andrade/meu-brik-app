import streamlit as st
import pandas as pd
from datetime import datetime
import os
import ast

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Brik PRO 10.3", layout="wide", page_icon="💎")

# 2. ARQUIVOS E PASTAS
ARQUIVO_ESTOQUE = "estoque.csv"
ARQUIVO_VENDAS = "vendas.csv"
PASTA_FOTOS = "fotos_produtos"
if not os.path.exists(PASTA_FOTOS): os.makedirs(PASTA_FOTOS)

# 3. CSS
st.markdown("""
    <style>
    .stApp { background-color: #0F1116 !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #E0E0E0 !important; }
    div[data-testid="stMetric"] { background-color: #1C1F26 !important; border-left: 5px solid #D4AF37 !important; border-radius: 10px !important; padding: 15px !important; }
    section[data-testid="stSidebar"] { background-color: #16191E !important; }
    .stButton>button { background-color: #D4AF37 !important; color: #0F1116 !important; font-weight: bold !important; width: 100%; border-radius: 8px !important; }
    /* Ajuste para inputs ficarem limpos */
    input { background-color: #262730 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. FUNÇÕES DE DADOS
def carregar_dados():
    if os.path.exists(ARQUIVO_ESTOQUE):
        estoque = pd.read_csv(ARQUIVO_ESTOQUE)
        estoque['gastos_extras'] = estoque.get('gastos_extras', "[]").fillna("[]")
    else:
        estoque = pd.DataFrame(columns=["id", "produto", "qtd", "custo_compra", "venda_sugerida", "foto", "data_entrada", "gastos_extras"])
    
    if os.path.exists(ARQUIVO_VENDAS):
        vendas = pd.read_csv(ARQUIVO_VENDAS)
        if not vendas.empty:
            vendas['data_venda'] = pd.to_datetime(vendas['data_venda'], dayfirst=True, errors='coerce')
            vendas = vendas.dropna(subset=['data_venda'])
    else:
        vendas = pd.DataFrame(columns=["data_venda", "produto_nome", "qtd_vendida", "valor_unitario", "lucro"])
    return estoque, vendas

st.session_state.estoque, st.session_state.vendas = carregar_dados()
if 'temp_gastos' not in st.session_state: st.session_state.temp_gastos = []

def salvar():
    st.session_state.estoque.to_csv(ARQUIVO_ESTOQUE, index=False)
    v_save = st.session_state.vendas.copy()
    if not v_save.empty: v_save['data_venda'] = v_save['data_venda'].dt.strftime('%d/%m/%Y %H:%M')
    v_save.to_csv(ARQUIVO_VENDAS, index=False)

# 5. SIDEBAR COM CADASTRO "LIMPO"
meses_nome = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
with st.sidebar:
    st.title("🏆 Andrade Tech")
    filtro_mes_nome = st.selectbox("📅 Mês:", ["Todos os Meses"] + meses_nome)
    mes_num = meses_nome.index(filtro_mes_nome) + 1 if filtro_mes_nome != "Todos os Meses" else None
    
    st.divider()
    menu = st.radio("Navegação:", ["📊 Dashboard", "⚡ Vendas", "📜 Esgotados"])
    
    st.divider()
    st.subheader("🆕 Novo Produto")
    with st.expander("Abrir Formulário"):
        n = st.text_input("Nome do Produto", placeholder="Ex: iPhone 13")
        d_in = st.date_input("Data de Entrada", format="DD/MM/YYYY")
        
        # Campos com valor inicial None mostram o placeholder vazio
        q = st.number_input("Quantidade", min_value=1, step=1, value=None, placeholder="0")
        c = st.number_input("Custo Unitário (R$)", min_value=0.0, step=0.01, value=None, placeholder="0.00")
        v = st.number_input("Venda Sugerida (R$)", min_value=0.0, step=0.01, value=None, placeholder="0.00")
        
        st.write("➕ **Gastos Extras**")
        col1, col2 = st.columns(2)
        dg = col1.text_input("Tipo", placeholder="Ex: Frete", key="tg_tipo")
        vg = col2.number_input("Valor", min_value=0.0, value=None, placeholder="0.00", key="tg_val")
        
        if st.button("Adicionar Gasto"):
            if dg and vg:
                st.session_state.temp_gastos.append({"tipo": dg, "valor": vg})
                st.rerun()
        
        for g in st.session_state.temp_gastos:
            st.caption(f"✅ {g['tipo']}: R$ {g['valor']:.2f}")

        ft = st.file_uploader("Foto", type=['png', 'jpg', 'jpeg'])
        
        if st.button("🚀 CADASTRAR PRODUTO"):
            if n and q and c is not None and v is not None:
                id_p = int(datetime.now().timestamp())
                path = os.path.join(PASTA_FOTOS, f"{id_p}_{ft.name}") if ft else "Sem Foto"
                if ft:
                    with open(path, "wb") as f: f.write(ft.getbuffer())
                
                novo = pd.DataFrame([{
                    "id": id_p, "produto": n.upper(), "qtd": q, 
                    "custo_compra": c, "venda_sugerida": v, 
                    "foto": path, "data_entrada": d_in.strftime('%d/%m/%Y'), 
                    "gastos_extras": str(st.session_state.temp_gastos)
                }])
                st.session_state.estoque = pd.concat([st.session_state.estoque, novo], ignore_index=True)
                st.session_state.temp_gastos = []
                salvar()
                st.success("Cadastrado!")
                st.rerun()
            else:
                st.error("Preencha Nome, Qtd, Custo e Venda!")

# 6. FUNÇÃO DE CARD
def exibir_card(item, venda_ativa=True):
    with st.container():
        c1, c2 = st.columns([1, 2])
        with c1:
            if item['foto'] != "Sem Foto" and os.path.exists(item['foto']):
                st.image(item['foto'], use_container_width=True)
            else: st.write("🖼️ S/ Foto")
        with c2:
            st.subheader(item['produto'])
            if venda_ativa:
                st.write(f"📦 Qtd: {int(item['qtd'])} | 💰 R$ {item['venda_sugerida']:.2f}")
                if st.button("🛒 Vender", key=f"v_{item['id']}"):
                    st.session_state.estoque.loc[st.session_state.estoque['id'] == item['id'], 'qtd'] -= 1
                    lucro = item['venda_sugerida'] - item['custo_compra']
                    nova_venda = pd.DataFrame([{
                        "data_venda": datetime.now(), "produto_nome": item['produto'],
                        "qtd_vendida": 1, "valor_unitario": item['venda_sugerida'], "lucro": lucro
                    }])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, nova_venda], ignore_index=True)
                    salvar(); st.rerun()
            else:
                lucro_u = item['venda_sugerida'] - item['custo_compra']
                st.write(f"✅ Esgotado | Lucro Unit: R$ {lucro_u:.2f}")
    st.divider()

# 7. TELAS
if menu == "📊 Dashboard":
    st.header(f"Resultados: {filtro_mes_nome}")
    
    dv = st.session_state.vendas.copy()
    if mes_num and not dv.empty:
        dv = dv[dv['data_venda'].dt.month == mes_num]
    
    if not dv.empty:
        # Forçamos a conversão para garantir que a soma não resulte em 0 por erro de tipo
        faturamento = (dv['qtd_vendida'].astype(float) * dv['valor_unitario'].astype(float)).sum()
        lucro_total = dv['lucro'].astype(float).sum()
        qtd_total = dv['qtd_vendida'].sum()
    else:
        faturamento, lucro_total, qtd_total = 0.0, 0.0, 0
        
    st.metric("Faturamento", f"R$ {faturamento:,.2f}")
    st.metric("Lucro Líquido", f"R$ {lucro_total:,.2f}")
    st.metric("Itens Vendidos", int(qtd_total))

elif menu == "⚡ Vendas":
    df_e = st.session_state.estoque.copy()
    dispo = df_e[df_e['qtd'] > 0]
    for _, row in dispo.iterrows(): exibir_card(row, True)

elif menu == "📜 Esgotados":
    df_e = st.session_state.estoque.copy()
    esgo = df_e[df_e['qtd'] <= 0]
    for _, row in esgo.iterrows(): exibir_card(row, False)