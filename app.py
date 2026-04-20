import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Brik PRO - Gestão 360",
    layout="wide",
    page_icon="📱",
    initial_sidebar_state="collapsed"
)

# 2. CONFIGURAÇÃO DE ARQUIVOS
ARQUIVO_ESTOQUE = "estoque.csv"
ARQUIVO_VENDAS = "vendas.csv"
PASTA_FOTOS = "fotos_produtos"

if not os.path.exists(PASTA_FOTOS):
    os.makedirs(PASTA_FOTOS)

# 3. ESTILIZAÇÃO CSS (CORREÇÃO DE CORES E MOBILE)
st.markdown("""
    <style>
    /* Força visibilidade das métricas no Dashboard */
    [data-testid="stMetricValue"] {
        color: #01C18D !important;
        font-weight: bold !important;
        font-size: 28px !important;
    }
    [data-testid="stMetricLabel"] {
        color: #31333F !important;
        font-size: 14px !important;
    }
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        padding: 15px !important;
        border-radius: 10px !important;
        border: 1px solid #e6e9ef !important;
    }
    /* Botões grandes para Touch */
    .stButton > button {
        width: 100%;
        height: 50px;
        background-color: #01C18D !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 10px !important;
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
        st.session_state.vendas = pd.read_csv(ARQUIVO_VENDAS)
        # Garante colunas de status/obs para versões antigas do CSV
        if 'status' not in st.session_state.vendas.columns:
            st.session_state.vendas['status'] = "Concluída"
        if 'observacao' not in st.session_state.vendas.columns:
            st.session_state.vendas['observacao'] = ""
    else:
        st.session_state.vendas = pd.DataFrame(columns=["data_venda", "produto_id", "produto_nome", "qtd_vendida", "valor_unitario_real", "lucro_da_venda", "status", "observacao"])

if 'estoque' not in st.session_state: carregar_dados()

def salvar():
    st.session_state.estoque.to_csv(ARQUIVO_ESTOQUE, index=False)
    st.session_state.vendas.to_csv(ARQUIVO_VENDAS, index=False)

# 5. LÓGICA DE NEGÓCIO
def registrar_devolucao(index_venda, nova_obs):
    venda = st.session_state.vendas.loc[index_venda]
    if venda['status'] != "Devolvido":
        # Devolve ao estoque
        idx_p = st.session_state.estoque[st.session_state.estoque['id'] == venda['produto_id']].index
        if not idx_p.empty:
            st.session_state.estoque.at[idx_p[0], 'qtd'] += venda['qtd_vendida']
        
        st.session_state.vendas.at[index_venda, 'status'] = "Devolvido"
        st.session_state.vendas.at[index_venda, 'observacao'] = nova_obs
        salvar()
        return True
    return False

# 6. MENU LATERAL
with st.sidebar:
    st.title("🏢 Brik PRO")
    menu = st.radio("Menu Principal", ["📊 Dashboard", "🛒 Vender", "📦 Estoque", "📜 Histórico/Pós-Venda"])
    st.divider()
    st.caption("v2.5 - Mobile Ready")

# 7. TELAS
if menu == "📊 Dashboard":
    st.title("📊 Indicadores")
    df_v = st.session_state.vendas[st.session_state.vendas['status'] == "Concluída"]
    df_e = st.session_state.estoque
    
    faturamento = (df_v['qtd_vendida'] * df_v['valor_unitario_real']).sum()
    lucro = df_v['lucro_da_venda'].sum()
    invest_preso = (df_e['qtd'] * (df_e['custo_compra'] + df_e['gastos_extras'])).sum()

    c1, c2 = st.columns(2)
    c1.metric("Faturamento", f"R$ {faturamento:,.2f}")
    c2.metric("Lucro Líquido", f"R$ {lucro:,.2f}")
    st.metric("Investimento em Estoque", f"R$ {invest_preso:,.2f}")
    
    st.divider()
    meta = st.number_input("Meta Mensal (R$)", value=5000.0)
    prog = min(faturamento/meta, 1.0) if meta > 0 else 0
    st.progress(prog)
    st.write(f"**{prog*100:.1f}%** da meta atingida.")

elif menu == "🛒 Vender":
    st.title("🛒 Nova Venda")
    prods = st.session_state.estoque[st.session_state.estoque['qtd'] > 0]
    
    if prods.empty:
        st.warning("Sem estoque disponível.")
    else:
        escolha = st.selectbox("Selecione o Produto", prods['produto'])
        item = prods[prods['produto'] == escolha].iloc[0]
        
        if item['foto'] != "Sem Foto": st.image(item['foto'], width=150)
        
        c1, c2 = st.columns(2)
        qtd_v = c1.number_input("Qtd", 1, max_value=int(item['qtd']))
        v_real = c2.number_input("Preço Fechado", value=float(item['venda_sugerida']))
        
        total = qtd_v * v_real
        st.subheader(f"Total: R$ {total:,.2f}")
        
        if st.button("🚀 FINALIZAR VENDA"):
            idx = st.session_state.estoque[st.session_state.estoque['id'] == item['id']].index[0]
            st.session_state.estoque.at[idx, 'qtd'] -= qtd_v
            
            custo_un = item['custo_compra'] + item['gastos_extras']
            lucro_v = (v_real - custo_un) * qtd_v
            
            nova_v = {
                "data_venda": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "produto_id": item['id'], "produto_nome": item['produto'],
                "qtd_vendida": qtd_v, "valor_unitario_real": v_real,
                "lucro_da_venda": lucro_v, "status": "Concluída", "observacao": ""
            }
            st.session_state.vendas = pd.concat([st.session_state.vendas, pd.DataFrame([nova_v])], ignore_index=True)
            salvar()
            st.balloons()
            st.success("Venda salva!")

elif menu == "📦 Estoque":
    st.title("📦 Gestão de Estoque")
    t1, t2 = st.tabs(["Lista", "Novo"])
    
    with t1:
        for i, r in st.session_state.estoque.iterrows():
            with st.expander(f"{r['produto']} ({r['qtd']} un)"):
                if r['foto'] != "Sem Foto": st.image(r['foto'], width=100)
                st.write(f"Custo: R$ {r['custo_compra']+r['gastos_extras']:.2f}")
                if st.button("🗑️ Excluir", key=f"del_{r['id']}"):
                    st.session_state.estoque = st.session_state.estoque.drop(i)
                    salvar()
                    st.rerun()
    
    with t2:
        with st.form("cad"):
            n = st.text_input("Nome")
            c1, c2 = st.columns(2)
            q = c1.number_input("Qtd", 1)
            comp = c2.number_input("Custo", 0.0)
            ext = st.number_input("Extras", 0.0)
            vend = st.number_input("Sugerido", 0.0)
            img = st.file_uploader("Foto")
            if st.form_submit_button("CADASTRAR"):
                id_p = int(datetime.now().timestamp())
                path = "Sem Foto"
                if img:
                    path = os.path.join(PASTA_FOTOS, f"{id_p}_{img.name}")
                    with open(path, "wb") as f: f.write(img.getbuffer())
                nova = {"id": id_p, "produto": n, "qtd": q, "custo_compra": comp, "gastos_extras": ext, "venda_sugerida": vend, "foto": path, "data_entrada": datetime.now().strftime("%d/%m/%Y")}
                st.session_state.estoque = pd.concat([st.session_state.estoque, pd.DataFrame([nova])], ignore_index=True)
                salvar()
                st.success("Salvo!")

elif menu == "📜 Histórico/Pós-Venda":
    st.title("📜 Histórico de Vendas")
    if st.session_state.vendas.empty:
        st.write("Sem registros.")
    else:
        for i, row in st.session_state.vendas.iloc[::-1].iterrows():
            with st.expander(f"Venda: {row['produto_nome']} - {row['status']}"):
                st.write(f"Data: {row['data_venda']} | Total: R$ {row['qtd_vendida']*row['valor_unitario_real']:.2f}")
                if row['observacao']: st.info(f"Obs: {row['observacao']}")
                
                st.divider()
                st_sel = st.selectbox("Alterar para:", ["Concluída", "Devolvido", "Manutenção"], key=f"sel_{i}")
                obs_v = st.text_input("Observação", key=f"in_{i}")
                
                if st.button("Atualizar", key=f"up_{i}"):
                    if st_sel == "Devolvido":
                        registrar_devolucao(i, obs_v)
                    else:
                        st.session_state.vendas.at[i, 'status'] = st_sel
                        st.session_state.vendas.at[i, 'observacao'] = obs_v
                        salvar()
                    st.rerun()