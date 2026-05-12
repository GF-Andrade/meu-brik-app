import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. CONFIGURAÇÃO
st.set_page_config(page_title="Brik PRO 11.1", layout="wide", page_icon="💎")

# 2. ARQUIVOS E PASTAS
ARQUIVO_ESTOQUE = "estoque.csv"
ARQUIVO_VENDAS = "vendas.csv"
PASTA_FOTOS = "fotos_produtos"
if not os.path.exists(PASTA_FOTOS): os.makedirs(PASTA_FOTOS)

# 3. FUNÇÕES DE DADOS
def carregar_dados():
    if os.path.exists(ARQUIVO_ESTOQUE):
        try:
            estoque = pd.read_csv(ARQUIVO_ESTOQUE)
            estoque['gastos_extras'] = estoque.get('gastos_extras', "[]").fillna("[]")
        except:
            estoque = pd.DataFrame(columns=["id", "produto", "qtd", "custo_compra", "venda_sugerida", "foto", "data_entrada", "gastos_extras"])
    else:
        estoque = pd.DataFrame(columns=["id", "produto", "qtd", "custo_compra", "venda_sugerida", "foto", "data_entrada", "gastos_extras"])

    if os.path.exists(ARQUIVO_VENDAS):
        try:
            vendas = pd.read_csv(ARQUIVO_VENDAS)
            if not vendas.empty:
                vendas['data_venda'] = pd.to_datetime(vendas['data_venda'], dayfirst=True, errors='coerce')
        except:
            vendas = pd.DataFrame(columns=["data_venda", "produto_nome", "qtd_vendida", "valor_unitario", "lucro"])
    else:
        vendas = pd.DataFrame(columns=["data_venda", "produto_nome", "qtd_vendida", "valor_unitario", "lucro"])
    return estoque, vendas

def salvar():
    st.session_state.estoque.to_csv(ARQUIVO_ESTOQUE, index=False)
    v_save = st.session_state.vendas.copy()
    if not v_save.empty:
        v_save['data_venda'] = pd.to_datetime(v_save['data_venda'], errors='coerce')
        v_save['data_venda'] = v_save['data_venda'].dt.strftime('%d/%m/%Y %H:%M')
    v_save.to_csv(ARQUIVO_VENDAS, index=False)

# 4. INICIALIZAÇÃO
if 'estoque' not in st.session_state:
    st.session_state.estoque, st.session_state.vendas = carregar_dados()
if 'temp_gastos' not in st.session_state:
    st.session_state.temp_gastos = []
if 'form_id' not in st.session_state:
    st.session_state.form_id = 0
if 'editando_id' not in st.session_state:
    st.session_state.editando_id = None

# 5. SIDEBAR
meses_nome = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
with st.sidebar:
    st.title("🏆 Andrade Tech")
    filtro_mes_nome = st.selectbox("📅 Mês:", ["Todos os Meses"] + meses_nome)
    mes_num = meses_nome.index(filtro_mes_nome) + 1 if filtro_mes_nome != "Todos os Meses" else None
    
    st.divider()
    menu_selecionado = st.radio("Navegação:", ["📊 Dashboard", "⚡ Produtos", "📜 Vendas"])
    
    st.divider()
    
    # LÓGICA DE FORMULÁRIO
    is_edit = st.session_state.editando_id is not None
    st.subheader("📝 Editar Produto" if is_edit else "🆕 Novo Produto")
    
    with st.expander("Abrir Formulário", expanded=is_edit):
        f_id = st.session_state.form_id
        
        # Define valores base (Se não for edição, usa None para limpar o campo)
        val_n, val_q, val_c, val_v = "", None, None, None
        
        if is_edit:
            item_edit = st.session_state.estoque[st.session_state.estoque['id'] == st.session_state.editando_id].iloc[0]
            val_n = item_edit['produto']
            val_q = int(item_edit['qtd'])
            val_c = float(item_edit['custo_compra'])
            val_v = float(item_edit['venda_sugerida'])

        n = st.text_input("Nome", value=val_n, placeholder="Ex: iPhone 13", key=f"n_{f_id}")
        q = st.number_input("Qtd", min_value=1, value=val_q, placeholder="0", key=f"q_{f_id}")
        c = st.number_input("Custo Unit. (R$)", min_value=0.0, value=val_c, placeholder="0.00", key=f"c_{f_id}")
        v = st.number_input("Venda Sugerida (R$)", min_value=0.0, value=val_v, placeholder="0.00", key=f"v_{f_id}")
        
        st.write("🔧 Gastos Extras")
        col_g1, col_g2 = st.columns(2)
        tg = col_g1.text_input("Tipo", placeholder="Capa", key=f"tg_{f_id}")
        vg = col_g2.number_input("Valor", min_value=0.0, value=None, placeholder="0.00", key=f"vg_{f_id}")
        
        if st.button("➕ Add Gasto", key=f"btn_g_{f_id}"):
            if tg and vg:
                st.session_state.temp_gastos.append({"tipo": tg, "valor": vg})
                st.rerun()
        
        for g in st.session_state.temp_gastos:
            st.caption(f"📍 {g['tipo']}: R$ {g['valor']:.2f}")

        ft = st.file_uploader("Foto do Produto", type=['png', 'jpg', 'jpeg'], key=f"ft_{f_id}")
        
        # Botões de Ação
        c_btn1, c_btn2 = st.columns(2)
        if not is_edit:
            if c_btn1.button("🚀 CADASTRAR"):
                if n and q and c is not None and v is not None:
                    id_p = int(datetime.now().timestamp())
                    path = "Sem Foto"
                    if ft:
                        path = os.path.join(PASTA_FOTOS, f"{id_p}_{ft.name}")
                        with open(path, "wb") as f: f.write(ft.getbuffer())
                    
                    s_extras = sum(item['valor'] for item in st.session_state.temp_gastos)
                    c_final = c + (s_extras / q)
                    
                    novo = pd.DataFrame([{
                        "id": id_p, "produto": n.upper(), "qtd": q, "custo_compra": c_final,
                        "venda_sugerida": v, "foto": path, "data_entrada": datetime.now().strftime('%d/%m/%Y'),
                        "gastos_extras": str(st.session_state.temp_gastos)
                    }])
                    st.session_state.estoque = pd.concat([st.session_state.estoque, novo], ignore_index=True)
                    salvar()
                    st.session_state.temp_gastos = []; st.session_state.form_id += 1; st.rerun()
        else:
            if c_btn1.button("💾 SALVAR"):
                idx = st.session_state.estoque[st.session_state.estoque['id'] == st.session_state.editando_id].index[0]
                st.session_state.estoque.at[idx, 'produto'] = n.upper()
                st.session_state.estoque.at[idx, 'qtd'] = q
                st.session_state.estoque.at[idx, 'custo_compra'] = c
                st.session_state.estoque.at[idx, 'venda_sugerida'] = v
                if ft:
                    path = os.path.join(PASTA_FOTOS, f"{st.session_state.editando_id}_{ft.name}")
                    with open(path, "wb") as f: f.write(ft.getbuffer())
                    st.session_state.estoque.at[idx, 'foto'] = path
                salvar()
                st.session_state.editando_id = None; st.session_state.form_id += 1; st.rerun()
            
            if c_btn2.button("❌ CANCELAR"):
                st.session_state.editando_id = None; st.rerun()

# 6. FUNÇÃO DE CARD
def exibir_card(item, modo_venda=True):
    with st.container():
        c1, c2 = st.columns([1, 2])
        with c1:
            if item['foto'] != "Sem Foto" and os.path.exists(item['foto']):
                st.image(item['foto'], use_container_width=True)
            else: st.write("🖼️ S/ Foto")
        with c2:
            st.subheader(item['produto'])
            if modo_venda:
                st.write(f"📦 Qtd: {int(item['qtd'])} | 💰 R$ {item['venda_sugerida']:.2f}")
                col1, col2 = st.columns(2)
                if col1.button("🛒 Vender", key=f"v_{item['id']}"):
                    st.session_state.estoque.loc[st.session_state.estoque['id'] == item['id'], 'qtd'] -= 1
                    lucro = float(item['venda_sugerida']) - float(item['custo_compra'])
                    nv = pd.DataFrame([{"data_venda": datetime.now(), "produto_nome": item['produto'], "qtd_vendida": 1, "valor_unitario": float(item['venda_sugerida']), "lucro": lucro}])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, nv], ignore_index=True)
                    salvar(); st.rerun()
                if col2.button("📝 Editar", key=f"ed_{item['id']}"):
                    st.session_state.editando_id = item['id']
                    st.rerun()
            else:
                st.write(f"✅ Esgotado | Lucro Unit: R$ {(float(item['venda_sugerida']) - float(item['custo_compra'])):.2f}")
                if st.button("🗑️ Excluir Definitivo", key=f"del_{item['id']}"):
                    nome_p = item['produto']
                    st.session_state.estoque = st.session_state.estoque[st.session_state.estoque['id'] != item['id']]
                    st.session_state.vendas = st.session_state.vendas[st.session_state.vendas['produto_nome'] != nome_p]
                    salvar(); st.rerun()
    st.divider()

# 7. TELAS
if menu_selecionado == "📊 Dashboard":
    st.header(f"📊 Desempenho: {filtro_mes_nome}")
    dv = st.session_state.vendas.copy()
    if not dv.empty:
        dv['data_venda'] = pd.to_datetime(dv['data_venda'])
        if mes_num: dv = dv[dv['data_venda'].dt.month == mes_num]
        fat = (dv['qtd_vendida'] * dv['valor_unitario']).sum()
        luc = dv['lucro'].sum()
        qtd = dv['qtd_vendida'].sum()
    else: fat, luc, qtd = 0.0, 0.0, 0
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Faturamento", f"R$ {fat:,.2f}")
    col2.metric("Lucro Líquido", f"R$ {luc:,.2f}")
    col3.metric("Itens Vendidos", int(qtd))

elif menu_selecionado == "⚡ Produtos":
    st.header("⚡ Estoque Disponível")
    busca = st.text_input("🔍 Pesquisar...")
    dispo = st.session_state.estoque[st.session_state.estoque['qtd'] > 0]
    if busca: dispo = dispo[dispo['produto'].str.contains(busca, case=False, na=False)]
    for _, row in dispo.iterrows(): exibir_card(row, True)

elif menu_selecionado == "📜 Vendas":
    st.header("📜 Histórico e Esgotados")
    esgo = st.session_state.estoque[st.session_state.estoque['qtd'] <= 0]
    for _, row in esgo.iterrows(): exibir_card(row, False)