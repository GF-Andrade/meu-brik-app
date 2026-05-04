import streamlit as st
import pandas as pd
from datetime import datetime
import os
import ast

# 1. CONFIGURAÇÃO (Título e Ícone)
st.set_page_config(page_title="Brik PRO 9.7", layout="wide", page_icon="💎")

# 2. ARQUIVOS E PASTAS
ARQUIVO_ESTOQUE = "estoque.csv"
ARQUIVO_VENDAS = "vendas.csv"
PASTA_FOTOS = "fotos_produtos"
if not os.path.exists(PASTA_FOTOS): os.makedirs(PASTA_FOTOS)

# 3. CSS DARK & GOLD (COM AJUSTE PARA CELULAR)
st.markdown("""
    <style>
    .stApp { background-color: #0F1116 !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #E0E0E0 !important; }
    
    /* Box das Métricas */
    div[data-testid="stMetric"] { 
        background-color: #1C1F26 !important; 
        border-left: 5px solid #D4AF37 !important; 
        border-radius: 10px !important; 
        padding: 10px !important;
    }
    
    /* Ajuste de fonte para telas pequenas (Celular) */
    @media (max-width: 640px) {
        div[data-testid="stMetricValue"] > div { font-size: 1.5rem !important; }
        .stTable, .stDataFrame { font-size: 0.8rem !important; }
    }

    section[data-testid="stSidebar"] { background-color: #16191E !important; }
    .stButton>button { background-color: #D4AF37 !important; color: #0F1116 !important; font-weight: bold !important; width: 100%; }
    .destaque-gasto { color: #FF4B4B !important; font-weight: bold; font-size: 0.85em; }
    .destaque-lucro { color: #00FF7F !important; font-weight: bold; font-size: 1.1em; background-color: #1E2E26; padding: 5px 10px; border-radius: 5px; display: inline-block; }
    </style>
    """, unsafe_allow_html=True)

# 4. CARREGAMENTO E SALVAMENTO
def carregar_dados():
    if os.path.exists(ARQUIVO_ESTOQUE):
        estoque = pd.read_csv(ARQUIVO_ESTOQUE)
        if 'gastos_extras' not in estoque.columns: estoque['gastos_extras'] = "[]"
        estoque['gastos_extras'] = estoque['gastos_extras'].fillna("[]")
    else:
        estoque = pd.DataFrame(columns=["id", "produto", "qtd", "custo_compra", "venda_sugerida", "foto", "data_entrada", "gastos_extras"])
    
    vendas = pd.read_csv(ARQUIVO_VENDAS) if os.path.exists(ARQUIVO_VENDAS) else pd.DataFrame(columns=["data_venda", "produto_nome", "qtd_vendida", "valor_unitario", "lucro"])
    
    estoque['data_entrada'] = estoque['data_entrada'].fillna(datetime.now().strftime('%d/%m/%Y')).astype(str)
    
    if not vendas.empty:
        # Força a conversão para datetime garantindo que o dia vem primeiro
        vendas['data_venda'] = pd.to_datetime(vendas['data_venda'], dayfirst=True, errors='coerce')
        vendas = vendas.dropna(subset=['data_venda']) # Remove erros de conversão
        
    return estoque, vendas

# Recarrega os dados na sessão
st.session_state.estoque, st.session_state.vendas = carregar_dados()

if 'temp_gastos' not in st.session_state:
    st.session_state.temp_gastos = []

def salvar():
    st.session_state.estoque.to_csv(ARQUIVO_ESTOQUE, index=False)
    df_v_save = st.session_state.vendas.copy()
    if not df_v_save.empty:
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
        c = st.number_input("Custo Unitário (R$)", min_value=0.0, step=0.01, value=None)
        v = st.number_input("Preço Venda (R$)", min_value=0.0, step=0.01, value=None)
        
        st.write("➕ **Gastos Adicionais**")
        cg1, cg2 = st.columns(2)
        desc_g = cg1.text_input("Tipo")
        val_g = cg2.number_input("Valor", min_value=0.0)
        
        if st.button("Adicionar Gasto"):
            if desc_g and val_g > 0:
                st.session_state.temp_gastos.append({"tipo": desc_g, "valor": val_g})
                st.rerun()
        
        for g in st.session_state.temp_gastos: st.caption(f"✅ {g['tipo']}: R$ {g['valor']:.2f}")
        
        ft = st.file_uploader("Foto", type=['png', 'jpg', 'jpeg'])
        if st.button("🚀 FINALIZAR"):
            if n and q and c and v:
                id_p = int(datetime.now().timestamp())
                path = os.path.join(PASTA_FOTOS, f"{id_p}_{ft.name}") if ft else "Sem Foto"
                if ft:
                    with open(path, "wb") as f: f.write(ft.getbuffer())
                novo = pd.DataFrame([{"id": id_p, "produto": n, "qtd": q, "custo_compra": c, "venda_sugerida": v, "foto": path, "data_entrada": d_in.strftime('%d/%m/%Y'), "gastos_extras": str(st.session_state.temp_gastos)}])
                st.session_state.estoque = pd.concat([st.session_state.estoque, novo], ignore_index=True)
                st.session_state.temp_gastos = []
                salvar(); st.rerun()

# 6. FILTRAGEM DE DADOS (CRÍTICO PARA CELULAR)
df_vendas_f = st.session_state.vendas.copy()
df_estoque_f = st.session_state.estoque.copy()

if mes_num:
    if not df_vendas_f.empty:
        # Garante que a comparação do mês seja numérica
        df_vendas_f = df_vendas_f[df_vendas_f['data_venda'].dt.month == mes_num]
    
    def extrair_mes(x):
        try: return int(str(x).split('/')[1])
        except: return 0
    df_estoque_f['mes_entrada'] = df_estoque_f['data_entrada'].apply(extrair_mes)
    df_estoque_f = df_estoque_f[df_estoque_f['mes_entrada'] == mes_num]

# 7. FUNÇÃO DE CARD (ADAPTADA PARA CELULAR)
def exibir_card_produto(item, modo_venda=True):
    with st.container():
        # No celular, essas colunas ficam uma em cima da outra automaticamente
        c1, c2 = st.columns([1, 3])
        with c1:
            if item['foto'] != "Sem Foto" and os.path.exists(item['foto']): 
                st.image(item['foto'], use_container_width=True)
            else: st.caption("Sem Foto")
        with c2:
            st.subheader(item['produto'])
            st.write(f"📅 {item['data_entrada']}")
            
            # Gastos Adicionais
            try: gastos = ast.literal_eval(item.get('gastos_extras', "[]"))
            except: gastos = []
            
            if gastos:
                with st.expander("🔍 Gastos Extras"):
                    for g in gastos: st.markdown(f"<span class='destaque-gasto'>• {g['tipo']}: R$ {g['valor']:.2f}</span>", unsafe_allow_html=True)
            
            if modo_venda:
                st.write(f"📦 Qtd: {int(item['qtd'])} | 💰 R$ {item['venda_sugerida']:.2f}")
                with st.expander("💸 Vender"):
                    qv = st.number_input("Qtd", 1, max_value=int(item['qtd']), key=f"v_{item['id']}")
                    if st.button("Vender", key=f"b_{item['id']}"):
                        st.session_state.estoque.loc[st.session_state.estoque['id'] == item['id'], 'qtd'] -= qv
                        lv = (item['venda_sugerida'] - item['custo_compra']) * qv
                        nv = pd.DataFrame([{"data_venda": datetime.now(), "produto_nome": item['produto'], "qtd_vendida": qv, "valor_unitario": item['venda_sugerida'], "lucro": lv}])
                        st.session_state.vendas = pd.concat([st.session_state.vendas, nv], ignore_index=True)
                        salvar(); st.rerun()
            else:
                lucro_u = item['venda_sugerida'] - item['custo_compra']
                st.markdown(f"<span class='destaque-lucro'>LUCRO: R$ {lucro_u:.2f}</span>", unsafe_allow_html=True)
                if st.button("🗑️ Excluir", key=f"del_{item['id']}"):
                    st.session_state.estoque = st.session_state.estoque[st.session_state.estoque['id'] != item['id']]
                    salvar(); st.rerun()
    st.divider()

# 8. TELAS (DASHBOARD FIX)
if menu == "📊 Dashboard":
    st.header(f"📊 {filtro_mes_nome}")
    
    if not df_vendas_f.empty:
        fat = (df_vendas_f['qtd_vendida'] * df_vendas_f['valor_unitario']).sum()
        luc = df_vendas_f['lucro'].sum()
        qtd_v = int(df_vendas_f['qtd_vendida'].sum())
        
        # Exibe métricas (No celular elas vão uma abaixo da outra)
        st.metric("FATURAMENTO", f"R$ {fat:,.2f}")
        st.metric("LUCRO", f"R$ {luc:,.2f}")
        st.metric("PRODUTOS VENDIDOS", qtd_v)
        
        st.divider()
        st.subheader("Lista de Vendas")
        df_view = df_vendas_f.copy()
        df_view['data_venda'] = df_view['data_venda'].dt.strftime('%d/%m/%Y')
        st.dataframe(df_view[['data_venda', 'produto_nome', 'qtd_vendida', 'lucro']], use_container_width=True)
    else:
        st.warning("Sem dados para este período no Dashboard.")

elif menu == "⚡ Vendas":
    st.header(f"⚡ Estoque")
    dispo = df_estoque_f[df_estoque_f['qtd'] > 0]
    if dispo.empty: st.info("Nada para mostrar.")
    for _, item in dispo.iterrows(): exibir_card_produto(item, modo_venda=True)

elif menu == "📜 Esgotados":
    st.header(f"📜 Histórico")
    esg = df_estoque_f[df_estoque_f['qtd'] <= 0]
    if esg.empty: st.info("Nada esgotado.")
    for _, item in esg.iterrows(): exibir_card_produto(item, modo_venda=False)