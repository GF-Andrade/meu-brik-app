import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Brik PRO 10.8", layout="wide", page_icon="💎")

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
    .botao-excluir>button { background-color: #FF4B4B !important; color: white !important; }
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

if 'estoque' not in st.session_state:
    st.session_state.estoque, st.session_state.vendas = carregar_dados()
if 'menu_aba' not in st.session_state:
    st.session_state.menu_aba = "📊 Dashboard"
if 'temp_gastos' not in st.session_state:
    st.session_state.temp_gastos = []

def salvar():
    st.session_state.estoque.to_csv(ARQUIVO_ESTOQUE, index=False)
    v_save = st.session_state.vendas.copy()
    if not v_save.empty:
        v_save['data_venda'] = pd.to_datetime(v_save['data_venda'], errors='coerce')
        v_save['data_venda'] = v_save['data_venda'].dt.strftime('%d/%m/%Y %H:%M')
    v_save.to_csv(ARQUIVO_VENDAS, index=False)

# 5. SIDEBAR
meses_nome = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
with st.sidebar:
    st.title("🏆 Andrade Tech")
    filtro_mes_nome = st.selectbox("📅 Mês:", ["Todos os Meses"] + meses_nome)
    mes_num = meses_nome.index(filtro_mes_nome) + 1 if filtro_mes_nome != "Todos os Meses" else None
    
    st.divider()
    # Trocado: "⚡ Vendas" -> "⚡ Produtos" | "📜 Esgotados" -> "📜 Vendas"
    st.session_state.menu_aba = st.radio("Navegação:", ["📊 Dashboard", "⚡ Produtos", "📜 Vendas"], 
                                       index=["📊 Dashboard", "⚡ Produtos", "📜 Vendas"].index(st.session_state.menu_aba))
    
    st.divider()
    st.subheader("🆕 Novo Produto")
    with st.expander("Abrir Formulário"):
        n = st.text_input("Nome", placeholder="Ex: iPhone 13")
        d_in = st.date_input("Data Entrada", format="DD/MM/YYYY")
        q = st.number_input("Qtd", min_value=1, step=1, value=None, placeholder="0")
        c = st.number_input("Custo (R$)", min_value=0.0, step=0.01, value=None, placeholder="0.00")
        v = st.number_input("Venda (R$)", min_value=0.0, step=0.01, value=None, placeholder="0.00")
        
        st.write("🔧 **Gastos Extras**")
        col_g1, col_g2 = st.columns(2)
        tipo_g = col_g1.text_input("Tipo", placeholder="Frete", key="tipo_g")
        val_g = col_g2.number_input("Valor", min_value=0.0, value=None, placeholder="0.00", key="val_g")
        
        if st.button("➕ Adicionar Gasto"):
            if tipo_g and val_g:
                st.session_state.temp_gastos.append({"tipo": tipo_g, "valor": val_g})
                st.rerun()
        
        for g in st.session_state.temp_gastos:
            st.caption(f"📍 {g['tipo']}: R$ {g['valor']:.2f}")

        ft = st.file_uploader("Foto", type=['png', 'jpg', 'jpeg'])
        
        if st.button("🚀 CADASTRAR"):
            if n and q and c is not None and v is not None:
                id_p = int(datetime.now().timestamp())
                path = os.path.join(PASTA_FOTOS, f"{id_p}_{ft.name}") if ft else "Sem Foto"
                if ft:
                    with open(path, "wb") as f: f.write(ft.getbuffer())
                
                s_extras = sum(item['valor'] for item in st.session_state.temp_gastos)
                c_final = c + (s_extras / q)
                
                novo = pd.DataFrame([{
                    "id": id_p, "produto": n.upper(), "qtd": q, 
                    "custo_compra": c_final, "venda_sugerida": v, 
                    "foto": path, "data_entrada": d_in.strftime('%d/%m/%Y'), 
                    "gastos_extras": str(st.session_state.temp_gastos)
                }])
                st.session_state.estoque = pd.concat([st.session_state.estoque, novo], ignore_index=True)
                st.session_state.temp_gastos = []
                salvar()
                st.session_state.menu_aba = "⚡ Produtos"
                st.rerun()

# 6. FUNÇÃO DE CARD
def exibir_card(item, modo_venda=True):
    with st.container():
        c1, c2 = st.columns([1, 2])
        with c1:
            if item['foto'] != "Sem Foto" and os.path.exists(item['foto']):
                st.image(item['foto'], width='stretch')
            else: st.write("🖼️ S/ Foto")
        with c2:
            st.subheader(item['produto'])
            if modo_venda:
                st.write(f"📦 Qtd: {int(item['qtd'])} | 💰 Preço: R$ {item['venda_sugerida']:.2f}")
                if st.button("🛒 Registrar Venda", key=f"v_{item['id']}"):
                    st.session_state.estoque.loc[st.session_state.estoque['id'] == item['id'], 'qtd'] -= 1
                    lucro = float(item['venda_sugerida']) - float(item['custo_compra'])
                    nova_venda = pd.DataFrame([{
                        "data_venda": datetime.now(), "produto_nome": item['produto'],
                        "qtd_vendida": 1, "valor_unitario": float(item['venda_sugerida']), "lucro": lucro
                    }])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, nova_venda], ignore_index=True)
                    salvar(); st.rerun()
            else:
                lucro_u = float(item['venda_sugerida']) - float(item['custo_compra'])
                st.write(f"✅ Status: Esgotado | Lucro: R$ {lucro_u:.2f}")
                st.markdown('<div class="botao-excluir">', unsafe_allow_html=True)
                if st.button("🗑️ Deletar Registro", key=f"del_{item['id']}"):
                    st.session_state.estoque = st.session_state.estoque[st.session_state.estoque['id'] != item['id']]
                    salvar(); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

# 7. TELAS
if st.session_state.menu_aba == "📊 Dashboard":
    st.header(f"📊 Desempenho: {filtro_mes_nome}")
    dv = st.session_state.vendas.copy()
    if mes_num and not dv.empty:
        dv = dv[dv['data_venda'].dt.month == mes_num]
    
    if not dv.empty:
        fat = (dv['qtd_vendida'].astype(float) * dv['valor_unitario'].astype(float)).sum()
        luc = dv['lucro'].astype(float).sum()
        qtd = dv['qtd_vendida'].sum()
    else: fat, luc, qtd = 0.0, 0.0, 0
        
    st.metric("Faturamento", f"R$ {fat:,.2f}")
    st.metric("Lucro Líquido", f"R$ {luc:,.2f}")
    st.metric("Total Vendido", int(qtd))

elif st.session_state.menu_aba == "⚡ Produtos":
    st.header("⚡ Estoque de Produtos")
    dispo = st.session_state.estoque[st.session_state.estoque['qtd'] > 0]
    if dispo.empty: st.info("Nenhum produto em estoque.")
    for _, row in dispo.iterrows(): exibir_card(row, True)

elif st.session_state.menu_aba == "📜 Vendas":
    st.header("📜 Histórico de Vendas (Esgotados)")
    esgo = st.session_state.estoque[st.session_state.estoque['qtd'] <= 0]
    if esgo.empty: st.info("Nenhuma venda registrada nos itens esgotados.")
    for _, row in esgo.iterrows(): exibir_card(row, False)