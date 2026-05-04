import streamlit as st
import pandas as pd
from datetime import datetime
import os
import ast

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Brik PRO 9.6", layout="wide", page_icon="💎")

# 2. ARQUIVOS E PASTAS
ARQUIVO_ESTOQUE = "estoque.csv"
ARQUIVO_VENDAS = "vendas.csv"
PASTA_FOTOS = "fotos_produtos"
if not os.path.exists(PASTA_FOTOS): os.makedirs(PASTA_FOTOS)

# 3. CSS DARK & GOLD
st.markdown("""
    <style>
    .stApp { background-color: #0F1116 !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #E0E0E0 !important; }
    div[data-testid="stMetric"] { background-color: #1C1F26 !important; border-left: 5px solid #D4AF37 !important; border-radius: 10px !important; }
    section[data-testid="stSidebar"] { background-color: #16191E !important; }
    .stButton>button { background-color: #D4AF37 !important; color: #0F1116 !important; font-weight: bold !important; border-radius: 8px !important; }
    .destaque-gasto { color: #FF4B4B !important; font-weight: bold; font-size: 0.9em; }
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
        vendas['data_venda'] = pd.to_datetime(vendas['data_venda'], dayfirst=True, errors='coerce')
    return estoque, vendas

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
    st.subheader("🆕 Novo Produto")
    with st.expander("Formulário de Cadastro"):
        n = st.text_input("Nome").upper()
        d_in = st.date_input("Data de Entrada", value=datetime.now(), format="DD/MM/YYYY")
        q = st.number_input("Qtd", min_value=1, value=None)
        c = st.number_input("Custo Unitário (R$)", min_value=0.0, step=0.01, value=None)
        v = st.number_input("Preço Venda (R$)", min_value=0.0, step=0.01, value=None)
        st.markdown("---")
        st.write("➕ **Gastos Adicionais**")
        col_g1, col_g2 = st.columns([2, 1])
        desc_gasto = col_g1.text_input("Tipo", key="desc_g")
        val_gasto = col_g2.number_input("Valor", min_value=0.0, step=0.01, key="val_g")
        if st.button("➕ Adicionar"):
            if desc_gasto and val_gasto > 0:
                st.session_state.temp_gastos.append({"tipo": desc_gasto, "valor": val_gasto})
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

# 6. FILTRAGEM
df_vendas_f = st.session_state.vendas.copy()
df_estoque_f = st.session_state.estoque.copy()
if mes_num:
    if not df_vendas_f.empty: df_vendas_f = df_vendas_f[df_vendas_f['data_venda'].dt.month == mes_num]
    def extrair_mes(x):
        try: return int(str(x).split('/')[1])
        except: return 0
    df_estoque_f['mes_entrada'] = df_estoque_f['data_entrada'].apply(extrair_mes)
    df_estoque_f = df_estoque_f[df_estoque_f['mes_entrada'] == mes_num]

# 7. FUNÇÃO DE EXIBIÇÃO (FIX DO ERRO FLOAT)
def exibir_card_produto(item, modo_venda=True):
    with st.container():
        c1, c2 = st.columns([1, 4])
        with c1:
            if item['foto'] != "Sem Foto" and os.path.exists(item['foto']): st.image(item['foto'], width=130)
            else: st.info("Sem Foto")
        with c2:
            st.subheader(item['produto'])
            st.write(f"📅 **Entrada:** {item['data_entrada']}")
            
            # --- TRATAMENTO ULTRA SEGURO DOS GASTOS ---
            gastos_lista = []
            raw_g = item.get('gastos_extras', "[]")
            
            # Se for texto, tenta converter. Se for qualquer outra coisa (float, NaN), vira lista vazia.
            if isinstance(raw_g, str) and raw_g.strip():
                try:
                    gastos_lista = ast.literal_eval(raw_g)
                    if not isinstance(gastos_lista, list): gastos_lista = []
                except:
                    gastos_lista = []
            
            if gastos_lista:
                with st.expander("🔍 Ver Gastos Adicionais"):
                    total_extra = 0
                    for g in gastos_lista:
                        st.markdown(f"<span class='destaque-gasto'>• {g['tipo']}: R$ {g['valor']:.2f}</span>", unsafe_allow_html=True)
                        total_extra += g['valor']
                    st.write(f"**Total Extra: R$ {total_extra:.2f}**")
            # ------------------------------------------

            if modo_venda:
                st.write(f"📦 **Disponível:** {int(item['qtd'])} | 💰 **Preço:** R$ {item['venda_sugerida']:.2f}")
                with st.expander("💸 Vender"):
                    qv = st.number_input("Qtd", 1, max_value=int(item['qtd']), key=f"v_{item['id']}")
                    if st.button("Confirmar", key=f"b_{item['id']}"):
                        st.session_state.estoque.loc[st.session_state.estoque['id'] == item['id'], 'qtd'] -= qv
                        lv = (item['venda_sugerida'] - item['custo_compra']) * qv
                        nv = pd.DataFrame([{"data_venda": datetime.now(), "produto_nome": item['produto'], "qtd_vendida": qv, "valor_unitario": item['venda_sugerida'], "lucro": lv}])
                        st.session_state.vendas = pd.concat([st.session_state.vendas, nv], ignore_index=True)
                        salvar(); st.rerun()
            else:
                lucro_unitario = item['venda_sugerida'] - item['custo_compra']
                st.write("❌ **STATUS: ESGOTADO**")
                st.markdown(f"💰 **Lucro Unitário Gerado:** <span class='destaque-lucro'>R$ {lucro_unitario:.2f}</span>", unsafe_allow_html=True)
                if st.button("🗑️ Remover Registro", key=f"del_{item['id']}"):
                    st.session_state.estoque = st.session_state.estoque[st.session_state.estoque['id'] != item['id']]
                    salvar(); st.rerun()
    st.divider()

# 8. TELAS
if menu == "📊 Dashboard":
    st.header(f"📊 Relatório - {filtro_mes_nome}")
    if not df_vendas_f.empty:
        fat = (df_vendas_f['qtd_vendida'] * df_vendas_f['valor_unitario']).sum()
        luc = df_vendas_f['lucro'].sum()
        c1, c2, c3 = st.columns(3)
        c1.metric("FATURAMENTO", f"R$ {fat:,.2f}")
        c2.metric("LUCRO", f"R$ {luc:,.2f}")
        c3.metric("VENDAS", int(df_vendas_f['qtd_vendida'].sum()))
        df_v = df_vendas_f.copy()
        df_v['data_venda'] = df_v['data_venda'].dt.strftime('%d/%m/%Y %H:%M')
        st.dataframe(df_v[['data_venda', 'produto_nome', 'qtd_vendida', 'lucro']], use_container_width=True)
    else: st.info("Sem movimentação.")

elif menu == "⚡ Vendas":
    st.header(f"⚡ Estoque Ativo - {filtro_mes_nome}")
    dispo = df_estoque_f[df_estoque_f['qtd'] > 0]
    for _, item in dispo.iterrows(): exibir_card_produto(item, modo_venda=True)

elif menu == "📜 Esgotados":
    st.header(f"📜 Histórico de Esgotados - {filtro_mes_nome}")
    esgotados = df_estoque_f[df_estoque_f['qtd'] <= 0]
    for _, item in esgotados.iterrows(): exibir_card_produto(item, modo_venda=False)