import streamlit as st
import pandas as pd
from datetime import datetime
import os
import ast

# 1. CONFIGURAÇÃO BÁSICA
st.set_page_config(page_title="Brik PRO 9.9", layout="wide", page_icon="💎")

# 2. DIRETÓRIOS E ARQUIVOS
ARQUIVO_ESTOQUE = "estoque.csv"
ARQUIVO_VENDAS = "vendas.csv"
PASTA_FOTOS = "fotos_produtos"
if not os.path.exists(PASTA_FOTOS): os.makedirs(PASTA_FOTOS)

# 3. CSS OTIMIZADO PARA MOBILE (Evita que elementos sumam)
st.markdown("""
    <style>
    .stApp { background-color: #0F1116 !important; }
    h1, h2, h3, p, span, label, .stMarkdown { color: #E0E0E0 !important; }
    
    /* Container de métricas robusto */
    [data-testid="stMetric"] {
        background-color: #1C1F26 !important;
        border: 1px solid #333 !important;
        border-left: 5px solid #D4AF37 !important;
        padding: 20px !important;
        border-radius: 10px !important;
        margin: 10px 0px !important;
        display: block !important;
    }
    
    section[data-testid="stSidebar"] { background-color: #16191E !important; }
    .stButton>button { background-color: #D4AF37 !important; color: #0F1116 !important; font-weight: bold !important; width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

# 4. CARREGAMENTO DE DADOS (COM TRATAMENTO DE ERROS)
@st.cache_data(ttl=2) # Atualiza rápido, mas evita travamentos de leitura
def ler_arquivos():
    try:
        estoque = pd.read_csv(ARQUIVO_ESTOQUE) if os.path.exists(ARQUIVO_ESTOQUE) else pd.DataFrame(columns=["id", "produto", "qtd", "custo_compra", "venda_sugerida", "foto", "data_entrada", "gastos_extras"])
        vendas = pd.read_csv(ARQUIVO_VENDAS) if os.path.exists(ARQUIVO_VENDAS) else pd.DataFrame(columns=["data_venda", "produto_nome", "qtd_vendida", "valor_unitario", "lucro"])
        
        # Correção de tipos
        if not vendas.empty:
            vendas['data_venda'] = pd.to_datetime(vendas['data_venda'], dayfirst=True, errors='coerce')
            vendas = vendas.dropna(subset=['data_venda'])
            
        return estoque, vendas
    except Exception as e:
        st.error(f"Erro ao ler banco de dados: {e}")
        return pd.DataFrame(), pd.DataFrame()

# 5. INICIALIZAÇÃO
st.session_state.estoque, st.session_state.vendas = ler_arquivos()

# 6. SIDEBAR E FILTROS
meses_nome = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
with st.sidebar:
    st.title("🏆 Andrade Tech")
    filtro_mes_nome = st.selectbox("📅 Mês:", ["Todos os Meses"] + meses_nome)
    mes_num = meses_nome.index(filtro_mes_nome) + 1 if filtro_mes_nome != "Todos os Meses" else None
    
    st.divider()
    menu = st.radio("Navegação:", ["📊 Dashboard", "⚡ Vendas", "📜 Esgotados"])

# 7. FUNÇÃO DE SALVAMENTO
def salvar_dados():
    st.session_state.estoque.to_csv(ARQUIVO_ESTOQUE, index=False)
    vendas_save = st.session_state.vendas.copy()
    if not vendas_save.empty:
        vendas_save['data_venda'] = vendas_save['data_venda'].dt.strftime('%d/%m/%Y %H:%M')
    vendas_save.to_csv(ARQUIVO_VENDAS, index=False)

# 8. TELA: DASHBOARD (REESCRITA PARA MÁXIMA COMPATIBILIDADE)
if menu == "📊 Dashboard":
    st.header(f"Estatísticas - {filtro_mes_nome}")
    
    try:
        # Filtragem Local
        df_v = st.session_state.vendas.copy()
        if mes_num and not df_v.empty:
            df_v = df_v[df_v['data_venda'].dt.month == mes_num]
        
        # Variáveis de cálculo com valores padrão (Garante que nunca seja 'Nada')
        faturamento = 0.0
        lucro_total = 0.0
        itens_vendidos = 0
        
        if not df_v.empty:
            faturamento = (df_v['qtd_vendida'] * df_v['valor_unitario']).sum()
            lucro_total = df_v['lucro'].sum()
            itens_vendidos = int(df_v['qtd_vendida'].sum())

        # EXIBIÇÃO FORÇADA (Uma por uma para evitar erro de layout)
        st.metric(label="FATURAMENTO BRUTO", value=f"R$ {faturamento:,.2f}")
        st.metric(label="LUCRO LÍQUIDO", value=f"R$ {lucro_total:,.2f}")
        st.metric(label="QUANTIDADE VENDIDA", value=str(itens_vendidos))
        
        st.divider()
        if not df_v.empty:
            st.subheader("Histórico Recente")
            st.dataframe(df_v[['produto_nome', 'lucro']].tail(10), use_container_width=True)
        else:
            st.info("Nenhuma venda registrada para este filtro.")
            
    except Exception as e:
        st.error(f"Ocorreu um erro ao carregar o Dashboard: {e}")

# 9. TELA: VENDAS
elif menu == "⚡ Vendas":
    st.header("Estoque Disponível")
    df_e = st.session_state.estoque.copy()
    
    # Filtro de mês no estoque (por data de entrada)
    if mes_num:
        def get_mes(x):
            try: return int(str(x).split('/')[1])
            except: return 0
        df_e['m'] = df_e['data_entrada'].apply(get_mes)
        df_e = df_e[df_e['m'] == mes_num]

    disponiveis = df_e[df_e['qtd'] > 0]
    
    if disponiveis.empty:
        st.warning("Nenhum produto em estoque para este mês.")
    else:
        for _, prod in disponiveis.iterrows():
            with st.expander(f"📦 {prod['produto']} - R$ {prod['venda_sugerida']:.2f}"):
                if prod['foto'] != "Sem Foto" and os.path.exists(prod['foto']):
                    st.image(prod['foto'], width=200)
                
                st.write(f"Quantidade: {int(prod['qtd'])}")
                if st.button("Confirmar Venda de 1 Unid.", key=f"btn_{prod['id']}"):
                    # Lógica de Venda
                    st.session_state.estoque.loc[st.session_state.estoque['id'] == prod['id'], 'qtd'] -= 1
                    novo_lucro = prod['venda_sugerida'] - prod['custo_compra']
                    nova_venda = pd.DataFrame([{
                        "data_venda": datetime.now(),
                        "produto_nome": prod['produto'],
                        "qtd_vendida": 1,
                        "valor_unitario": prod['venda_sugerida'],
                        "lucro": novo_lucro
                    }])
                    st.session_state.vendas = pd.concat([st.session_state.vendas, nova_venda], ignore_index=True)
                    salvar_dados()
                    st.success("Venda realizada!")
                    st.rerun()

# 10. TELA: ESGOTADOS
elif menu == "📜 Esgotados":
    st.header("Produtos Esgotados")
    esgotados = st.session_state.estoque[st.session_state.estoque['qtd'] <= 0]
    if esgotados.empty:
        st.info("Nenhum produto esgotado.")
    else:
        st.table(esgotados[['produto', 'data_entrada']])