import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Brik PRO - Gestão 360",
    layout="wide",
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)

# 2. CONFIGURAÇÃO DE ARQUIVOS
ARQUIVO_ESTOQUE = "estoque.csv"
ARQUIVO_VENDAS = "vendas.csv"
PASTA_FOTOS = "fotos_produtos"
if not os.path.exists(PASTA_FOTOS): os.makedirs(PASTA_FOTOS)

# 3. ESTILIZAÇÃO CSS (DARK MODE)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; }
    h1, h2, h3, h4, p, span, label, .stMarkdown { color: #FFFFFF !important; opacity: 1 !important; }
    
    div[data-testid="stMetric"] {
        background-color: #1A1C23 !important;
        border: 1px solid #30363D !important;
        border-radius: 12px !important;
    }
    
    [data-testid="stMetricLabel"] p { color: #FFFFFF !important; font-weight: 700 !important; }
    div[data-testid="stMetricValue"] div { color: #01C18D !important; font-weight: bold !important; }
    
    .stButton > button { background-color: #01C18D !important; color: white !important; font-weight: bold; border-radius: 8px; }
    .assinatura { font-size: 14px; color: #888 !important; text-align: center; margin-top: 50px; font-style: italic; border-top: 1px solid #30363D; padding-top: 15px; }
    
    hr { border-color: #30363D !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. GESTÃO DE DADOS
def carregar_dados():
    if os.path.exists(ARQUIVO_ESTOQUE):
        st.session_state.estoque = pd.read_csv(ARQUIVO_ESTOQUE)
    else:
        st.session_state.estoque = pd.DataFrame(columns=["id", "produto", "qtd", "custo_compra", "gastos_extras", "venda_sugerida", "foto", "data_entrada"])
    
    if os.path.exists(ARQUIVO_VENDAS):
        st.session_state.vendas = pd.read_csv(ARQUIVO_VENDAS)
    else:
        st.session_state.vendas = pd.DataFrame(columns=["data_venda", "produto_id", "produto_nome", "qtd_vendida", "valor_unitario_real", "lucro_da_venda", "status", "observacao"])

if 'estoque' not in st.session_state: carregar_dados()

def salvar():
    st.session_state.estoque.to_csv(ARQUIVO_ESTOQUE, index=False)
    st.session_state.vendas.to_csv(ARQUIVO_VENDAS, index=False)

# 5. LISTA DE MESES (2026)
LISTA_MESES = ["Janeiro/2026", "Fevereiro/2026", "Março/2026", "Abril/2026", "Maio/2026", "Junho/2026", "Julho/2026", "Agosto/2026", "Setembro/2026", "Outubro/2026", "Novembro/2026", "Dezembro/2026"]
MAPA_MESES = {m: f"{i+1:02d}/2026" for i, m in enumerate(LISTA_MESES)}

# 6. MENU LATERAL
with st.sidebar:
    st.title("🏢 Brik PRO")
    menu = st.radio("Navegação:", ["📊 Dashboard", "⚡ Vendas", "📜 Histórico"])
    st.divider()
    
    with st.expander("➕ Novo Item"):
        with st.form("cad_form", clear_on_submit=True):
            n = st.text_input("Produto").upper()
            q = st.number_input("Qtd", min_value=1, value=1)
            c = st.number_input("Custo (R$)", min_value=0.0, step=0.01, value=None)
            e = st.number_input("Extras (R$)", min_value=0.0, step=0.01, value=0.0)
            v = st.number_input("Venda Sugerida (R$)", min_value=0.0, step=0.01, value=None)
            ft = st.file_uploader("Foto", type=['jpg','png','jpeg'])
            if st.form_submit_button("Cadastrar"):
                if n and c is not None and v is not None:
                    id_p = int(datetime.now().timestamp())
                    path = "Sem Foto"
                    if ft:
                        path = os.path.join(PASTA_FOTOS, f"{id_p}_{ft.name}")
                        with open(path, "wb") as f: f.write(ft.getbuffer())
                    nova = {"id": id_p, "produto": n, "qtd": q, "custo_compra": c, "gastos_extras": e, "venda_sugerida": v, "foto": path, "data_entrada": datetime.now().strftime("%d/%m/%Y")}
                    st.session_state.estoque = pd.concat([st.session_state.estoque, pd.DataFrame([nova])], ignore_index=True)
                    salvar(); st.rerun()

    st.markdown(f'<p class="assinatura">Sistema Brik Gabriel Andrade</p>', unsafe_allow_html=True)

# 7. TELAS
if menu == "📊 Dashboard":
    st.title("📊 Painel de Controle")
    mes_txt = st.selectbox("📅 Mês:", LISTA_MESES, index=datetime.now().month - 1)
    mes_filtro = MAPA_MESES[mes_txt]
    
    df_v_mes = st.session_state.vendas[st.session_state.vendas['status'] == "Concluída"].copy()
    df_v_mes = df_v_mes[pd.to_datetime(df_v_mes['data_venda'], dayfirst=True).dt.strftime('%m/%Y') == mes_filtro]
    fat_mes = (df_v_mes['qtd_vendida'] * df_v_mes['valor_unitario_real']).sum()
    luc_mes = df_v_mes['lucro_da_venda'].sum()

    df_e = st.session_state.estoque[st.session_state.estoque['qtd'] > 0].copy()
    invest_total = (df_e['qtd'] * (df_e['custo_compra'] + df_e['gastos_extras'])).sum()
    retorno_total = (df_e['qtd'] * df_e['venda_sugerida']).sum()

    st.markdown(f"### 💵 Realizado: {mes_txt}")
    col1, col2 = st.columns(2)
    col1.metric("FATURAMENTO MENSAL", f"R$ {fat_mes:,.2f}")
    col2.metric("LUCRO MENSAL", f"R$ {luc_mes:,.2f}")
    
    st.divider()
    st.markdown("### 🔮 Projeção Geral")
    col3, col4, col5 = st.columns(3)
    col3.metric("TOTAL INVESTIDO", f"R$ {invest_total:,.2f}")
    col4.metric("PREVISÃO RETORNO", f"R$ {retorno_total:,.2f}")
    col5.metric("LUCRO PENDENTE", f"R$ {(retorno_total - invest_total):,.2f}")

elif menu == "⚡ Vendas":
    st.title("⚡ Venda Rápida")
    busca = st.text_input("🔍 Buscar no estoque...").upper()
    df_res = st.session_state.estoque[st.session_state.estoque['qtd'] > 0]
    if busca: df_res = df_res[df_res['produto'].str.contains(busca, case=False)]

    for i, r in df_res.iterrows():
        custo_total_u = r['custo_compra'] + r['gastos_extras']
        lucro_previsto_u = r['venda_sugerida'] - custo_total_u
        
        with st.container():
            c_img, c_txt = st.columns([1, 2])
            with c_img:
                if r['foto'] != "Sem Foto" and os.path.exists(r['foto']): st.image(r['foto'], use_container_width=True)
                else: st.write("🖼️")
            with c_txt:
                st.markdown(f"### {r['produto']}")
                # DESCRIÇÃO DETALHADA IGUAL AO HISTÓRICO
                st.markdown(f"📅 **Data Entrada:** {r['data_entrada']}")
                st.markdown(f"📦 **Estoque:** {int(r['qtd'])} un")
                st.markdown(f"💵 **Preço Pago (Custo):** R$ {custo_total_u:.2f}")
                st.markdown(f"📈 **Lucro Previsto:** <span style='color:#01C18D; font-weight:bold;'>R$ {lucro_previsto_u:.2f}</span>", unsafe_allow_html=True)
                
                with st.expander(f"💰 Vender {r['produto']}"):
                    qv = st.number_input("Qtd", 1, max_value=int(r['qtd']), key=f"q_{r['id']}")
                    vv = st.number_input("Preço Final de Venda", value=float(r['venda_sugerida']), key=f"v_{r['id']}")
                    if st.button("Confirmar Negócio", key=f"bt_{r['id']}"):
                        st.session_state.estoque.at[i, 'qtd'] -= qv
                        lucro_venda_final = (vv - custo_total_u) * qv
                        nova_v = {"data_venda": datetime.now().strftime("%d/%m/%Y %H:%M"), "produto_id": r['id'], "produto_nome": r['produto'], "qtd_vendida": qv, "valor_unitario_real": vv, "lucro_da_venda": lucro_venda_final, "status": "Concluída", "observacao": ""}
                        st.session_state.vendas = pd.concat([st.session_state.vendas, pd.DataFrame([nova_v])], ignore_index=True)
                        salvar(); st.rerun()
        st.divider()

elif menu == "📜 Histórico":
    st.title("📜 Histórico")
    mes_h_txt = st.selectbox("📅 Selecione o Mês:", LISTA_MESES, index=datetime.now().month - 1)
    mes_h_filtro = MAPA_MESES[mes_h_txt]
    df_h = st.session_state.vendas.copy()
    df_h = df_h[pd.to_datetime(df_h['data_venda'], dayfirst=True).dt.strftime('%m/%Y') == mes_h_filtro]

    if df_h.empty: st.info("Sem transações registradas.")
    else:
        for i, row in df_h.iloc[::-1].iterrows():
            produto_info = st.session_state.estoque[st.session_state.estoque['id'] == row['produto_id']]
            foto_path = produto_info['foto'].values[0] if not produto_info.empty else "Sem Foto"
            
            with st.container():
                col_foto, col_info = st.columns([1, 2])
                with col_foto:
                    if foto_path != "Sem Foto" and os.path.exists(foto_path): st.image(foto_path, use_container_width=True)
                    else: st.write("🖼️")
                with col_info:
                    st.markdown(f"#### {row['produto_nome']}")
                    st.markdown(f"📅 **Data Venda:** {row['data_venda']}")
                    st.markdown(f"🔢 **Quantidade:** {row['qtd_vendida']} un")
                    st.markdown(f"💰 **Total:** R$ {(row['qtd_vendida'] * row['valor_unitario_real']):.2f}")
                    st.markdown(f"📈 **Lucro Líquido:** <span style='color:#01C18D; font-weight:bold;'>R$ {row['lucro_da_venda']:.2f}</span>", unsafe_allow_html=True)
            st.divider()