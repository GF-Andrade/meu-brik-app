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

# 3. ESTILIZAÇÃO CSS (DARK MODE & MOBILE)
st.markdown("""
    <style>
    .stApp { background-color: #0E1117 !important; }
    section[data-testid="stSidebar"] { background-color: #0E1117 !important; border-right: 1px solid #30363D; }
    section[data-testid="stSidebar"] .st-emotion-cache-6qob1r { background-color: #0E1117 !important; }
    h1, h2, h3, h4, p, span, label, .stMarkdown { color: #FFFFFF !important; opacity: 1 !important; }
    
    div[data-testid="stMetric"] {
        background-color: #1A1C23 !important;
        border: 1px solid #30363D !important;
        border-radius: 12px !important;
    }
    
    .stButton > button { 
        background-color: #01C18D !important; 
        color: white !important; 
        font-weight: bold; 
        border-radius: 8px;
        height: 45px;
        width: 100%;
    }
    
    div.stButton > button[key^="del_"] {
        background-color: #FF4B4B !important;
    }

    .assinatura { 
        font-size: 14px; color: #888 !important; text-align: center; margin-top: 30px; 
        font-style: italic; border-top: 1px solid #30363D; padding-top: 15px; 
    }
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

# 5. LISTA DE MESES
LISTA_MESES = ["Janeiro/2026", "Fevereiro/2026", "Março/2026", "Abril/2026", "Maio/2026", "Junho/2026", "Julho/2026", "Agosto/2026", "Setembro/2026", "Outubro/2026", "Novembro/2026", "Dezembro/2026"]
MAPA_MESES = {m: f"{i+1:02d}/2026" for i, m in enumerate(LISTA_MESES)}

# 6. MENU LATERAL (NOMES ATUALIZADOS)
with st.sidebar:
    st.markdown("## 🏢 Brik PRO")
    menu = st.radio("Navegação:", ["📊 Dashboard", "⚡ Produtos", "📜 Vendas"])
    st.divider()
    
    with st.expander("➕ Novo Item"):
        with st.form("cad_form", clear_on_submit=True):
            n = st.text_input("Produto").upper()
            q = st.number_input("Qtd", min_value=1, value=1)
            c = st.number_input("Custo (R$)", min_value=0.0, step=0.01)
            v = st.number_input("Preço Sugerido (R$)", min_value=0.0, step=0.01)
            e = st.number_input("Extras (R$)", min_value=0.0, step=0.01, value=0.0)
            ft = st.file_uploader("Foto", type=['jpg','png','jpeg'])
            if st.form_submit_button("Cadastrar"):
                if n and c > 0 and v > 0:
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
    
    col1, col2 = st.columns(2)
    col1.metric("FATURAMENTO MENSAL", f"R$ {df_v_mes['qtd_vendida'].mul(df_v_mes['valor_unitario_real']).sum():,.2f}")
    col2.metric("LUCRO MENSAL", f"R$ {df_v_mes['lucro_da_venda'].sum():,.2f}")
    
    st.divider()
    df_e = st.session_state.estoque[st.session_state.estoque['qtd'] > 0].copy()
    col3, col4, col5 = st.columns(3)
    col3.metric("INVESTIDO", f"R$ {(df_e['qtd'] * (df_e['custo_compra'] + df_e['gastos_extras'])).sum():,.2f}")
    col4.metric("RETORNO", f"R$ {(df_e['qtd'] * df_e['venda_sugerida']).sum():,.2f}")
    col5.metric("PENDENTE", f"R$ {((df_e['qtd'] * df_e['venda_sugerida']).sum() - (df_e['qtd'] * (df_e['custo_compra'] + df_e['gastos_extras'])).sum()):,.2f}")

elif menu == "⚡ Produtos":
    st.title("⚡ Gestão de Produtos")
    busca = st.text_input("🔍 Buscar no estoque...").upper()
    df_res = st.session_state.estoque.copy()
    if busca: df_res = df_res[df_res['produto'].str.contains(busca, case=False)]

    for i, r in df_res.iterrows():
        custo_u = r['custo_compra'] + r['gastos_extras']
        with st.container():
            c_img, c_txt = st.columns([1, 2])
            with c_img:
                if r['foto'] != "Sem Foto" and os.path.exists(r['foto']): st.image(r['foto'], use_container_width=True)
                else: st.write("🖼️")
            with c_txt:
                st.markdown(f"### {r['produto']}")
                st.markdown(f"📅 **Entrada:** {r['data_entrada']} | 📦 **Estoque:** {int(r['qtd'])} un")
                st.markdown(f"💵 **Custo Unit:** R$ {custo_u:.2f} | 📈 **Lucro Unit:** R$ {(r['venda_sugerida'] - custo_u):.2f}")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if r['qtd'] > 0:
                        with st.expander("💰 Vender"):
                            qv = st.number_input("Qtd", 1, max_value=int(r['qtd']), key=f"q_{r['id']}")
                            vv = st.number_input("Preço Final", value=float(r['venda_sugerida']), key=f"v_{r['id']}")
                            if st.button("Confirmar Venda", key=f"bt_v_{r['id']}"):
                                st.session_state.estoque.loc[st.session_state.estoque['id'] == r['id'], 'qtd'] -= qv
                                nova_v = {"data_venda": datetime.now().strftime("%d/%m/%Y %H:%M"), "produto_id": r['id'], "produto_nome": r['produto'], "qtd_vendida": qv, "valor_unitario_real": vv, "lucro_da_venda": (vv - custo_u) * qv, "status": "Concluída", "observacao": ""}
                                st.session_state.vendas = pd.concat([st.session_state.vendas, pd.DataFrame([nova_v])], ignore_index=True)
                                salvar(); st.rerun()
                    else:
                        st.warning("Esgotado")
                with col_btn2:
                    with st.expander("⚙️ Ajustar"):
                        ed_nome = st.text_input("Nome", r['produto'], key=f"ed_n_{r['id']}")
                        ed_qtd = st.number_input("Estoque", value=int(r['qtd']), key=f"ed_q_{r['id']}")
                        ed_custo = st.number_input("Custo", value=float(r['custo_compra']), key=f"ed_c_{r['id']}")
                        ed_sug = st.number_input("Preço Sug", value=float(r['venda_sugerida']), key=f"ed_s_{r['id']}")
                        ed_ext = st.number_input("Extras", value=float(r['gastos_extras']), key=f"ed_e_{r['id']}")
                        if st.button("💾 Salvar", key=f"ed_sv_{r['id']}"):
                            idx = st.session_state.estoque[st.session_state.estoque['id'] == r['id']].index
                            st.session_state.estoque.loc[idx, ['produto', 'qtd', 'custo_compra', 'venda_sugerida', 'gastos_extras']] = [ed_nome.upper(), ed_qtd, ed_custo, ed_sug, ed_ext]
                            salvar(); st.rerun()
                        if st.button("🗑️ Excluir", key=f"del_{r['id']}"):
                            st.session_state.estoque = st.session_state.estoque[st.session_state.estoque['id'] != r['id']]
                            salvar(); st.rerun()
        st.divider()

elif menu == "📜 Vendas":
    st.title("📜 Histórico de Vendas")
    mes_h_txt = st.selectbox("📅 Selecione o Mês:", LISTA_MESES, index=datetime.now().month - 1)
    mes_h_filtro = MAPA_MESES[mes_h_txt]
    df_h = st.session_state.vendas.copy()
    df_h = df_h[pd.to_datetime(df_h['data_venda'], dayfirst=True).dt.strftime('%m/%Y') == mes_h_filtro]

    if df_h.empty: st.info("Nenhuma venda registrada neste mês.")
    else:
        for i, row in df_h.iloc[::-1].iterrows():
            p_info = st.session_state.estoque[st.session_state.estoque['id'] == row['produto_id']]
            foto = p_info['foto'].values[0] if not p_info.empty else "Sem Foto"
            with st.container():
                c1, c2 = st.columns([1, 2])
                with c1:
                    if foto != "Sem Foto" and os.path.exists(foto): st.image(foto, use_container_width=True)
                    else: st.write("🖼️")
                with c2:
                    st.markdown(f"#### {row['produto_nome']}")
                    st.markdown(f"📅 **Vendido em:** {row['data_venda']}")
                    st.markdown(f"🔢 {row['qtd_vendida']} un | 💰 Total: R$ {(row['qtd_vendida'] * row['valor_unitario_real']):.2f}")
                    st.markdown(f"📈 Lucro: <span style='color:#01C18D; font-weight:bold;'>R$ {row['lucro_da_venda']:.2f}</span>", unsafe_allow_html=True)
            st.divider()