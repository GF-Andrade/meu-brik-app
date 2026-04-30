import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Brik PRO",
    layout="wide",
    page_icon="📦",
    initial_sidebar_state="collapsed"
)

# 2. CONFIGURAÇÃO DE ARQUIVOS
ARQUIVO_ESTOQUE = "estoque.csv"
ARQUIVO_VENDAS = "vendas.csv"
PASTA_FOTOS = "fotos_produtos"
if not os.path.exists(PASTA_FOTOS): os.makedirs(PASTA_FOTOS)

# 3. ESTILIZAÇÃO CSS (CORREÇÃO DE VISIBILIDADE)
st.markdown("""
    <style>
    /* FUNDO DA PÁGINA */
    .stApp { background-color: #F0F2F6 !important; }
    
    /* BOTÃO DO MENU (FIXO E AZUL ESCURO) */
    button[data-testid="sidebar-button"] {
        background-color: #002D5B !important;
        color: #FFFFFF !important;
        border-radius: 12px !important;
        width: 55px !important;
        height: 55px !important;
        position: fixed !important;
        top: 10px !important;
        left: 10px !important;
        z-index: 9999 !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3) !important;
    }

    /* SIDEBAR (ESCURA PARA CONTRASTE) */
    section[data-testid="stSidebar"] {
        background-color: #111B21 !important;
        border-right: 1px solid #202C33;
    }
    section[data-testid="stSidebar"] * { color: white !important; }

    /* CARDS DO DASHBOARD (BRANCOS COM TEXTO PRETO) */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 2px solid #DEE2E6 !important;
        border-radius: 15px !important;
        padding: 20px !important;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05) !important;
    }
    div[data-testid="stMetricLabel"] > div { 
        color: #495057 !important; 
        font-weight: bold !important;
        font-size: 16px !important;
    }
    div[data-testid="stMetricValue"] > div { 
        color: #000000 !important; 
        font-weight: 800 !important;
    }

    /* TÍTULOS E TEXTOS DA PÁGINA */
    h1, h2, h3, h4, span, label, p { 
        color: #000000 !important; 
        opacity: 1 !important;
    }

    /* BOTÕES (CORES QUE SE DESTACAM NO FUNDO CLARO) */
    .stButton > button {
        background-color: #0056B3 !important;
        color: white !important;
        border-radius: 10px !important;
        height: 50px !important;
        font-weight: bold !important;
        border: none !important;
    }
    
    /* BOTÃO DE EXCLUIR */
    div.stButton > button[key^="del_"] {
        background-color: #C82333 !important;
    }

    /* CONTAINERS DE PRODUTOS */
    [data-testid="stVerticalBlock"] > div > div[style*="border"] {
        background-color: #FFFFFF !important;
        border: 1px solid #CED4DA !important;
        border-radius: 15px !important;
        padding: 20px !important;
    }

    .assinatura { 
        font-size: 14px; color: #6C757D !important; text-align: center; margin-top: 40px; 
    }
    </style>
    """, unsafe_allow_html=True)

# 4. GESTÃO DE DADOS
def carregar_dados():
    if os.path.exists(ARQUIVO_ESTOQUE):
        st.session_state.estoque = pd.read_csv(ARQUIVO_ESTOQUE)
    else:
        st.session_state.estoque = pd.DataFrame(columns=["id", "produto", "qtd", "custo_compra", "gastos_extras", "venda_sugerida", "foto", "data_entrada"])
    
    if os.path.exists(ARQUIVO_VENDAS):
        df_v = pd.read_csv(ARQUIVO_VENDAS)
        if "id_venda" not in df_v.columns:
            df_v["id_venda"] = [int(datetime.now().timestamp()) + i for i in range(len(df_v))]
        st.session_state.vendas = df_v
    else:
        st.session_state.vendas = pd.DataFrame(columns=["id_venda", "data_venda", "produto_id", "produto_nome", "qtd_vendida", "valor_unitario_real", "lucro_da_venda", "status"])

if 'estoque' not in st.session_state: carregar_dados()

def salvar():
    st.session_state.estoque.to_csv(ARQUIVO_ESTOQUE, index=False)
    st.session_state.vendas.to_csv(ARQUIVO_VENDAS, index=False)

# 5. CONFIGURAÇÃO DE TEMPO
LISTA_MESES = ["Janeiro/2026", "Fevereiro/2026", "Março/2026", "Abril/2026", "Maio/2026", "Junho/2026", "Julho/2026", "Agosto/2026", "Setembro/2026", "Outubro/2026", "Novembro/2026", "Dezembro/2026"]
MAPA_MESES = {m: f"{i+1:02d}/2026" for i, m in enumerate(LISTA_MESES)}

# 6. MENU LATERAL
with st.sidebar:
    st.markdown("## 🏢 Andrade Tech")
    menu = st.radio("Selecione:", ["📊 Dashboard", "⚡ Produtos", "📜 Vendas"])
    st.divider()
    
    with st.expander("➕ Adicionar Novo"):
        with st.form("cad_form", clear_on_submit=True):
            n = st.text_input("Nome").upper()
            q = st.number_input("Estoque", min_value=0, value=1)
            c = st.number_input("Custo Unit (R$)", min_value=0.0)
            e = st.number_input("Extras (R$)", min_value=0.0)
            v = st.number_input("Preço Venda (R$)", min_value=0.0)
            ft = st.file_uploader("Foto", type=['jpg','png','jpeg'])
            if st.form_submit_button("Salvar"):
                if n:
                    id_p = int(datetime.now().timestamp())
                    path = "Sem Foto"
                    if ft:
                        path = os.path.join(PASTA_FOTOS, f"{id_p}_{ft.name}")
                        with open(path, "wb") as f: f.write(ft.getbuffer())
                    nova = {"id": id_p, "produto": n, "qtd": q, "custo_compra": c, "gastos_extras": e, "venda_sugerida": v, "foto": path, "data_entrada": datetime.now().strftime("%d/%m/%Y")}
                    st.session_state.estoque = pd.concat([st.session_state.estoque, pd.DataFrame([nova])], ignore_index=True)
                    salvar(); st.rerun()
    st.markdown('<p style="color:white !important;">Brik Gabriel Andrade</p>', unsafe_allow_html=True)

# 7. TELAS
if menu == "📊 Dashboard":
    st.title("📊 Desempenho Financeiro")
    mes_txt = st.selectbox("Escolha o Mês:", LISTA_MESES, index=datetime.now().month - 1)
    mes_f = MAPA_MESES[mes_txt]
    
    df_v_mes = st.session_state.vendas.copy()
    if not df_v_mes.empty:
        df_v_mes = df_v_mes[pd.to_datetime(df_v_mes['data_venda'], dayfirst=True).dt.strftime('%m/%Y') == mes_f]

    # BLOCO 1: REALIZADO
    st.markdown("### ✅ Realizado no Mês")
    c1, c2 = st.columns(2)
    c1.metric("Faturamento Mensal", f"R$ {df_v_mes['qtd_vendida'].mul(df_v_mes['valor_unitario_real']).sum():,.2f}" if not df_v_mes.empty else "R$ 0,00")
    c2.metric("Lucro Mensal", f"R$ {df_v_mes['lucro_da_venda'].sum():,.2f}" if not df_v_mes.empty else "R$ 0,00")

    st.divider()
    
    # BLOCO 2: PROJEÇÃO
    st.markdown("### 🔮 Projeção de Estoque")
    df_e = st.session_state.estoque[st.session_state.estoque['qtd'] > 0].copy()
    c3, c4, c5 = st.columns(3)
    c3.metric("Total Investido", f"R$ {(df_e['qtd'] * (df_e['custo_compra'] + df_e['gastos_extras'])).sum():,.2f}")
    c4.metric("Previsão Retorno", f"R$ {(df_e['qtd'] * df_e['venda_sugerida']).sum():,.2f}")
    c5.metric("Lucro Pendente", f"R$ {((df_e['qtd'] * df_e['venda_sugerida']).sum() - (df_e['qtd'] * (df_e['custo_compra'] + df_e['gastos_extras'])).sum()):,.2f}")

elif menu == "⚡ Produtos":
    st.title("⚡ Gestão de Produtos")
    busca = st.text_input("🔍 Buscar Produto...").upper()
    df_res = st.session_state.estoque.copy()
    if busca: df_res = df_res[df_res['produto'].str.contains(busca, case=False)]

    for i, r in df_res.iterrows():
        custo_tot = r['custo_compra'] + r['gastos_extras']
        with st.container():
            col_img, col_info = st.columns([1, 2])
            with col_img:
                if r['foto'] != "Sem Foto" and os.path.exists(r['foto']): st.image(r['foto'], use_container_width=True)
                else: st.write("📸 Sem Foto")
            with col_info:
                st.subheader(r['produto'])
                st.write(f"📦 Unidades: **{int(r['qtd'])}** | 💵 Preço: **R$ {r['venda_sugerida']:.2f}**")
                
                c_v, c_e = st.columns(2)
                with c_v:
                    with st.expander("💸 Venda Rápida"):
                        qv = st.number_input("Qtd", 1, max_value=max(1, int(r['qtd'])), key=f"v_{r['id']}")
                        if st.button("Confirmar", key=f"bt_v_{r['id']}"):
                            st.session_state.estoque.loc[st.session_state.estoque['id'] == r['id'], 'qtd'] -= qv
                            id_v = int(datetime.now().timestamp())
                            nova_v = {"id_venda": id_v, "data_venda": datetime.now().strftime("%d/%m/%Y %H:%M"), "produto_id": r['id'], "produto_nome": r['produto'], "qtd_vendida": qv, "valor_unitario_real": r['venda_sugerida'], "lucro_da_venda": (r['venda_sugerida'] - custo_tot) * qv, "status": "Concluída"}
                            st.session_state.vendas = pd.concat([st.session_state.vendas, pd.DataFrame([nova_v])], ignore_index=True)
                            salvar(); st.rerun()
                with c_e:
                    with st.expander("⚙️ Opções"):
                        ed_n = st.text_input("Nome", r['produto'], key=f"en_{r['id']}")
                        ed_q = st.number_input("Estoque", value=int(r['qtd']), key=f"eq_{r['id']}")
                        ed_s = st.number_input("Preço", value=float(r['venda_sugerida']), key=f"es_{r['id']}")
                        if st.button("💾 Salvar", key=f"esv_{r['id']}"):
                            idx = st.session_state.estoque[st.session_state.estoque['id'] == r['id']].index
                            st.session_state.estoque.loc[idx, ['produto', 'qtd', 'venda_sugerida']] = [ed_n.upper(), ed_q, ed_s]
                            salvar(); st.rerun()
                        if st.button("🗑️ Excluir TUDO", key=f"del_total_{r['id']}"):
                            st.session_state.estoque = st.session_state.estoque[st.session_state.estoque['id'] != r['id']]
                            st.session_state.vendas = st.session_state.vendas[st.session_state.vendas['produto_id'] != r['id']]
                            salvar(); st.rerun()
        st.divider()

elif menu == "📜 Vendas":
    st.title("📜 Histórico")
    if not st.session_state.vendas.empty:
        for i, row in st.session_state.vendas.iloc[::-1].iterrows():
            with st.container():
                st.write(f"**{row['produto_nome']}**")
                st.write(f"📅 {row['data_venda']} | {int(row['qtd_vendida'])} un | Lucro: **R$ {row['lucro_da_venda']:.2f}**")
                if st.button(f"🗑️ Estornar", key=f"del_v_h_{row['id_venda']}"):
                    st.session_state.vendas = st.session_state.vendas[st.session_state.vendas['id_venda'] != row['id_venda']]
                    salvar(); st.rerun()
            st.divider()
    else:
        st.info("Nenhuma venda registrada.")