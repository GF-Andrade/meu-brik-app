import streamlit as st
import pandas as pd
from datetime import datetime
import os
import ast

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Brik PRO 9.8", layout="wide", page_icon="💎")

# 2. ARQUIVOS
ARQUIVO_ESTOQUE = "estoque.csv"
ARQUIVO_VENDAS = "vendas.csv"
PASTA_FOTOS = "fotos_produtos"
if not os.path.exists(PASTA_FOTOS): os.makedirs(PASTA_FOTOS)

# 3. CSS (Ajuste de visibilidade)
st.markdown("""
    <style>
    .stApp { background-color: #0F1116 !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #E0E0E0 !important; }
    div[data-testid="stMetric"] { background-color: #1C1F26 !important; border-left: 5px solid #D4AF37 !important; border-radius: 10px !important; padding: 15px !important; margin-bottom: 10px; }
    section[data-testid="stSidebar"] { background-color: #16191E !important; }
    .stButton>button { background-color: #D4AF37 !important; color: #0F1116 !important; font-weight: bold !important; width: 100%; }
    .destaque-lucro { color: #00FF7F !important; font-weight: bold; font-size: 1.1em; background-color: #1E2E26; padding: 5px 10px; border-radius: 5px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# 4. LÓGICA DE DADOS REFORÇADA
def carregar_dados():
    # --- ESTOQUE ---
    if os.path.exists(ARQUIVO_ESTOQUE):
        estoque = pd.read_csv(ARQUIVO_ESTOQUE)
        estoque['gastos_extras'] = estoque.get('gastos_extras', "[]").fillna("[]")
    else:
        estoque = pd.DataFrame(columns=["id", "produto", "qtd", "custo_compra", "venda_sugerida", "foto", "data_entrada", "gastos_extras"])

    # --- VENDAS (Onde costuma dar o bug no Dashboard) ---
    if os.path.exists(ARQUIVO_VENDAS):
        vendas = pd.read_csv(ARQUIVO_VENDAS)
        if not vendas.empty:
            # BUG FIX: Converte para string primeiro para limpar, depois para data forçando o padrão BR
            vendas['data_venda'] = vendas['data_venda'].astype(str)
            vendas['data_venda'] = pd.to_datetime(vendas['data_venda'], dayfirst=True, errors='coerce')
            # Remove qualquer linha que não conseguiu converter (evita travar o dashboard)
            vendas = vendas.dropna(subset=['data_venda'])
    else:
        vendas = pd.DataFrame(columns=["data_venda", "produto_nome", "qtd_vendida", "valor_unitario", "lucro"])
    
    return estoque, vendas

st.session_state.estoque, st.session_state.vendas = carregar_dados()

if 'temp_gastos' not in st.session_state:
    st.session_state.temp_gastos = []

def salvar():
    st.session_state.estoque.to_csv(ARQUIVO_ESTOQUE, index=False)
    df_v_save = st.session_state.vendas.copy()
    if not df_v_save.empty:
        # Garante que no arquivo físico a data sempre será gravada como DIA/MES/ANO
        df_v_save['data_venda'] = df_v_save['data_venda'].dt.strftime('%d/%m/%Y %H:%M')
    df_v_save.to_csv(ARQUIVO_VENDAS, index=False)

# 5. SIDEBAR
meses_nome = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
with st.sidebar:
    st.title("🏆 Andrade Tech")
    filtro_mes_nome = st.selectbox("📅 Mês de Referência:", ["Todos os Meses"] + meses_nome)
    mes_num = meses_nome.index(filtro_mes_nome) + 1 if filtro_mes_nome != "Todos os Meses" else None
    
    st.divider()
    menu = st.radio("Navegação:", ["📊 Dashboard", "⚡ Vendas", "📜 Esgotados"])
    
    st.divider()
    with st.expander("🆕 Novo Produto"):
        n = st.text_input("Nome").upper()
        d_in = st.date_input("Data de Entrada", value=datetime.now(), format="DD/MM/YYYY")
        q = st.number_input("Qtd", min_value=1, value=None)
        c = st.number_input("Custo Unitário", min_value=0.0)
        v = st.number_input("Preço Venda", min_value=0.0)
        
        st.write("➕ **Gasto Extra**")
        cg1, cg2 = st.columns(2)
        dg = cg1.text_input("Tipo")
        vg = cg2.number_input("R$", min_value=0.0)
        if st.button("Add Gasto"):
            if dg and vg > 0:
                st.session_state.temp_gastos.append({"tipo": dg, "valor": vg})
                st.rerun()
        
        ft = st.file_uploader("Foto", type=['png', 'jpg', 'jpeg'])
        if st.button("🚀 FINALIZAR"):
            if n and q and v:
                id_p = int(datetime.now().timestamp())
                path = os.path.join(PASTA_FOTOS, f"{id_p}_{ft.name}") if ft else "Sem Foto"
                if ft:
                    with open(path, "wb") as f: f.write(ft.getbuffer())
                novo = pd.DataFrame([{"id": id_p, "produto": n, "qtd": q, "custo_compra": c, "venda_sugerida": v, "foto": path, "data_entrada": d_in.strftime('%d/%m/%Y'), "gastos_extras": str(st.session_state.temp_gastos)}])
                st.session_state.estoque = pd.concat([st.session_state.estoque, novo], ignore_index=True)
                st.session_state.temp_gastos = []
                salvar(); st.rerun()

# 6. FILTRAGEM (O CORAÇÃO DO PROBLEMA)
df_vendas_f = st.session_state.vendas.copy()
df_estoque_f = st.session_state.estoque.copy()

if mes_num:
    if not df_vendas_f.empty:
        # Filtra comparando o número do mês da coluna datetime
        df_vendas_f = df_vendas_f[df_vendas_f['data_venda'].dt.month == mes_num]
    
    def extrair_mes(x):
        try: return int(str(x).split('/')[1])
        except: return 0
    df_estoque_f['mes_entrada'] = df_estoque_f['data_entrada'].apply(extrair_mes)
    df_estoque_f = df_estoque_f[df_estoque_f['mes_entrada'] == mes_num]

# 7. FUNÇÃO DE CARD
def exibir_card_produto(item, modo_venda=True):
    with st.container():
        c1, c2 = st.columns([1, 3])
        with c1:
            if item['foto'] != "Sem Foto" and os.path.exists(item['foto']): st.image(item['foto'], use_container_width=True)
        with c2:
            st.subheader(item['produto'])
            st.write(f"📅 {item['data_entrada']}")
            
            # Gastos
            try: gastos = ast.literal_eval(item.get('gastos_extras', "[]"))
            except: gastos = []
            if gastos:
                with st.expander("🔍 Gastos"):
                    for g in gastos: st.caption(f"• {g['tipo']}: R$ {g['valor']:.2f}")
            
            if modo_venda:
                st.write(f"📦 Qtd: {int(item['qtd'])} | R$ {item['venda_sugerida']:.2f}")
                if st.button("Vender", key=f"v_{item['id']}"):
                    st.session_state.estoque.loc[st.session_state.estoque['id'] == item['id'], 'qtd'] -= 1
                    lv = (item['venda_sugerida'] - item['custo_compra'])
                    nv = pd.DataFrame([{"data_venda": datetime.now(), "produto_nome": item['produto'], "qtd_vendida": 1, "valor_unitario": item['venda_sugerida'], "lucro": lv}])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, nv], ignore_index=True)
                    salvar(); st.rerun()
            else:
                lucro = item['venda_sugerida'] - item['custo_compra']
                st.markdown(f"<span class='destaque-lucro'>LUCRO: R$ {lucro:.2f}</span>", unsafe_allow_html=True)
    st.divider()

# 8. TELAS
if menu == "📊 Dashboard":
    st.header(f"📊 {filtro_mes_nome}")
    
    # Verificação de depuração: se estiver vazio no celular, ele avisará
    if df_vendas_f.empty:
        st.warning("Nenhuma venda encontrada para este mês. Verifique se as vendas foram registradas corretamente.")
    else:
        # Cálculo garantido
        faturamento = (df_vendas_f['qtd_vendida'] * df_vendas_f['valor_unitario']).sum()
        lucro_total = df_vendas_f['lucro'].sum()
        total_itens = df_vendas_f['qtd_vendida'].sum()
        
        # Exibição simples (sem colunas para evitar bug mobile)
        st.metric("FATURAMENTO TOTAL", f"R$ {faturamento:,.2f}")
        st.metric("LUCRO LÍQUIDO", f"R$ {lucro_total:,.2f}")
        st.metric("ITENS VENDIDOS", int(total_itens))
        
        st.divider()
        df_exibir = df_vendas_f.copy()
        df_exibir['data_venda'] = df_exibir['data_venda'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_exibir[['data_venda', 'produto_nome', 'lucro']], use_container_width=True)

elif menu == "⚡ Vendas":
    st.header("⚡ Estoque")
    dispo = df_estoque_f[df_estoque_f['qtd'] > 0]
    for _, item in dispo.iterrows(): exibir_card_produto(item, modo_venda=True)

elif menu == "📜 Esgotados":
    st.header("📜 Histórico")
    esg = df_estoque_f[df_estoque_f['qtd'] <= 0]
    for _, item in esg.iterrows(): exibir_card_produto(item, modo_venda=False)