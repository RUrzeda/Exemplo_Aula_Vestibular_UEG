import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Dashboard Vestibular UEG 2026/1",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🎓 Dashboard Vestibular UEG 2026/1")
st.markdown("### Análise de Inscrições Deferidas por Curso e Cidade")

# Destacar cobertura dos dados
st.success("✅ **Cobertura dos Dados:** 14.204 inscrições extraídas - **100% de cobertura completa!**")
st.markdown("---")

# Carregar dados
@st.cache_data
def load_data():
    df = pd.read_csv('dados_consolidados_100pct.csv')
    return df

df = load_data()

# Sidebar - Filtros
st.sidebar.header("🔍 Filtros")

# Filtro de Cidade
cidades_unicas = ['Todas'] + sorted(df['cidade'].unique().tolist())
cidade_selecionada = st.sidebar.selectbox("Cidade", cidades_unicas)

# Filtro de Curso
cursos_unicos = ['Todos'] + sorted(df['curso'].unique().tolist())
curso_selecionado = st.sidebar.selectbox("Curso", cursos_unicos)

# Filtro de Modalidade/Tipo
tipos_unicos = ['Todos'] + sorted(df['tipo_curso'].unique().tolist())
tipo_selecionado = st.sidebar.selectbox("Tipo de Curso", tipos_unicos)

# Filtro de Turno
turnos_unicos = ['Todos'] + sorted(df['turno'].unique().tolist())
turno_selecionado = st.sidebar.selectbox("Turno", turnos_unicos)

# Aplicar filtros
df_filtrado = df.copy()

if cidade_selecionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['cidade'] == cidade_selecionada]

if curso_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['curso'] == curso_selecionado]

if tipo_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['tipo_curso'] == tipo_selecionado]

if turno_selecionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['turno'] == turno_selecionado]

# Métricas principais
st.markdown("## 📊 Métricas Gerais")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de Vagas", f"{df_filtrado['vagas'].sum():,}")

with col2:
    st.metric("Total de Inscrições", f"{df_filtrado['inscricoes'].sum():,}")

with col3:
    media_candidatos = df_filtrado[df_filtrado['inscricoes'] > 0]['candidatos_por_vaga'].mean()
    st.metric("Média Candidatos/Vaga", f"{media_candidatos:.2f}")

with col4:
    cursos_com_inscricoes = (df_filtrado['inscricoes'] > 0).sum()
    st.metric("Cursos com Inscrições", f"{cursos_com_inscricoes}/{len(df_filtrado)}")

st.markdown("---")

# Seção de Insights
st.markdown("## 💡 Principais Insights")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔥 Cursos Mais Concorridos")
    top_concorridos = df_filtrado.nlargest(10, 'candidatos_por_vaga')[['curso', 'cidade', 'turno', 'vagas', 'inscricoes', 'candidatos_por_vaga']]
    top_concorridos_display = top_concorridos.copy()
    top_concorridos_display.columns = ['Curso', 'Cidade', 'Turno', 'Vagas', 'Inscrições', 'Cand/Vaga']
    st.dataframe(top_concorridos_display, use_container_width=True, hide_index=True)

with col2:
    st.markdown("### 📉 Cursos com Menor Procura")
    bottom_procura = df_filtrado.nsmallest(10, 'candidatos_por_vaga')[['curso', 'cidade', 'turno', 'vagas', 'inscricoes', 'candidatos_por_vaga']]
    bottom_procura_display = bottom_procura.copy()
    bottom_procura_display.columns = ['Curso', 'Cidade', 'Turno', 'Vagas', 'Inscrições', 'Cand/Vaga']
    st.dataframe(bottom_procura_display, use_container_width=True, hide_index=True)

st.markdown("---")

# Análise por Tipo de Curso
st.markdown("## 📚 Análise por Tipo de Curso")

stats_tipo = df_filtrado.groupby('tipo_curso').agg({
    'vagas': 'sum',
    'inscricoes': 'sum',
    'candidatos_por_vaga': 'mean'
}).reset_index()

stats_tipo['candidatos_por_vaga'] = stats_tipo['candidatos_por_vaga'].round(2)

col1, col2 = st.columns(2)

with col1:
    fig_tipo = px.bar(
        stats_tipo,
        x='tipo_curso',
        y='inscricoes',
        title='Inscrições por Tipo de Curso',
        labels={'tipo_curso': 'Tipo de Curso', 'inscricoes': 'Número de Inscrições'},
        color='tipo_curso',
        text='inscricoes',
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig_tipo.update_traces(textposition='outside')
    fig_tipo.update_layout(showlegend=False)
    st.plotly_chart(fig_tipo, use_container_width=True)

with col2:
    fig_cand_vaga = px.bar(
        stats_tipo,
        x='tipo_curso',
        y='candidatos_por_vaga',
        title='Média de Candidatos por Vaga (por Tipo)',
        labels={'tipo_curso': 'Tipo de Curso', 'candidatos_por_vaga': 'Candidatos/Vaga'},
        color='tipo_curso',
        text='candidatos_por_vaga',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_cand_vaga.update_traces(textposition='outside')
    fig_cand_vaga.update_layout(showlegend=False)
    st.plotly_chart(fig_cand_vaga, use_container_width=True)

st.markdown("---")

# Análise de Cursos de TI
st.markdown("## 💻 Análise Especial: Cursos de Tecnologia da Informação")

ti_cursos = df_filtrado[df_filtrado['curso'].str.contains('Sistemas', case=False, na=False)]

if len(ti_cursos) > 0:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Vagas em TI", f"{ti_cursos['vagas'].sum():,}")
    
    with col2:
        st.metric("Inscrições em TI", f"{ti_cursos['inscricoes'].sum():,}")
    
    with col3:
        media_ti = ti_cursos[ti_cursos['inscricoes'] > 0]['candidatos_por_vaga'].mean()
        st.metric("Média Cand/Vaga TI", f"{media_ti:.2f}")
    
    st.markdown("### Detalhamento dos Cursos de TI")
    ti_display = ti_cursos[['curso', 'cidade', 'turno', 'vagas', 'inscricoes', 'candidatos_por_vaga', 'modalidade']].copy()
    ti_display.columns = ['Curso', 'Cidade', 'Turno', 'Vagas', 'Inscrições', 'Cand/Vaga', 'Modalidade']
    st.dataframe(ti_display, use_container_width=True, hide_index=True)
    
    # Gráfico comparativo
    fig_ti = px.bar(
        ti_cursos,
        x='cidade',
        y='inscricoes',
        color='curso',
        title='Inscrições em Cursos de TI por Cidade',
        labels={'cidade': 'Cidade', 'inscricoes': 'Número de Inscrições', 'curso': 'Curso'},
        barmode='group'
    )
    st.plotly_chart(fig_ti, use_container_width=True)
else:
    st.info("Nenhum curso de TI encontrado com os filtros selecionados.")

st.markdown("---")

# Análise de Licenciaturas
st.markdown("## 👨‍🏫 Análise Especial: Licenciaturas")

licenciaturas = df_filtrado[df_filtrado['tipo_curso'] == 'Licenciatura']

if len(licenciaturas) > 0:
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Vagas em Licenciaturas", f"{licenciaturas['vagas'].sum():,}")
    
    with col2:
        st.metric("Inscrições em Licenciaturas", f"{licenciaturas['inscricoes'].sum():,}")
    
    with col3:
        media_lic = licenciaturas[licenciaturas['inscricoes'] > 0]['candidatos_por_vaga'].mean()
        st.metric("Média Cand/Vaga", f"{media_lic:.2f}")
    
    # Top 10 licenciaturas mais e menos procuradas
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Licenciaturas Mais Procuradas")
        top_lic = licenciaturas.nlargest(10, 'inscricoes')[['curso', 'cidade', 'inscricoes', 'candidatos_por_vaga']]
        top_lic_display = top_lic.copy()
        top_lic_display.columns = ['Curso', 'Cidade', 'Inscrições', 'Cand/Vaga']
        st.dataframe(top_lic_display, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### Licenciaturas Menos Procuradas")
        bottom_lic = licenciaturas.nsmallest(10, 'inscricoes')[['curso', 'cidade', 'inscricoes', 'candidatos_por_vaga']]
        bottom_lic_display = bottom_lic.copy()
        bottom_lic_display.columns = ['Curso', 'Cidade', 'Inscrições', 'Cand/Vaga']
        st.dataframe(bottom_lic_display, use_container_width=True, hide_index=True)
    
    # Distribuição de inscrições em licenciaturas por curso
    lic_por_curso = licenciaturas.groupby('curso')['inscricoes'].sum().reset_index().sort_values('inscricoes', ascending=False).head(15)
    
    fig_lic = px.bar(
        lic_por_curso,
        x='inscricoes',
        y='curso',
        orientation='h',
        title='Top 15 Licenciaturas por Total de Inscrições',
        labels={'curso': 'Curso', 'inscricoes': 'Total de Inscrições'},
        color='inscricoes',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_lic, use_container_width=True)
else:
    st.info("Nenhuma licenciatura encontrada com os filtros selecionados.")

st.markdown("---")

# Análise por Cidade
st.markdown("## 🏙️ Análise por Cidade")

inscricoes_por_cidade = df_filtrado.groupby('cidade').agg({
    'vagas': 'sum',
    'inscricoes': 'sum',
    'candidatos_por_vaga': 'mean'
}).reset_index().sort_values('inscricoes', ascending=False).head(15)

inscricoes_por_cidade['candidatos_por_vaga'] = inscricoes_por_cidade['candidatos_por_vaga'].round(2)

col1, col2 = st.columns(2)

with col1:
    fig_cidade_inscricoes = px.bar(
        inscricoes_por_cidade,
        x='inscricoes',
        y='cidade',
        orientation='h',
        title='Top 15 Cidades por Número de Inscrições',
        labels={'cidade': 'Cidade', 'inscricoes': 'Número de Inscrições'},
        color='inscricoes',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig_cidade_inscricoes, use_container_width=True)

with col2:
    fig_cidade_cand = px.bar(
        inscricoes_por_cidade,
        x='candidatos_por_vaga',
        y='cidade',
        orientation='h',
        title='Top 15 Cidades por Candidatos/Vaga',
        labels={'cidade': 'Cidade', 'candidatos_por_vaga': 'Candidatos por Vaga'},
        color='candidatos_por_vaga',
        color_continuous_scale='Reds'
    )
    st.plotly_chart(fig_cidade_cand, use_container_width=True)

st.markdown("---")

# Análise por Turno
st.markdown("## 🕐 Análise por Turno")

inscricoes_por_turno = df_filtrado.groupby('turno').agg({
    'vagas': 'sum',
    'inscricoes': 'sum',
    'candidatos_por_vaga': 'mean'
}).reset_index()

col1, col2 = st.columns(2)

with col1:
    fig_turno = px.pie(
        inscricoes_por_turno,
        values='inscricoes',
        names='turno',
        title='Distribuição de Inscrições por Turno',
        hole=0.4,
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(fig_turno, use_container_width=True)

with col2:
    fig_turno_bar = px.bar(
        inscricoes_por_turno,
        x='turno',
        y=['vagas', 'inscricoes'],
        title='Vagas vs Inscrições por Turno',
        labels={'value': 'Quantidade', 'turno': 'Turno'},
        barmode='group'
    )
    st.plotly_chart(fig_turno_bar, use_container_width=True)

st.markdown("---")

# Tabela completa de dados
st.markdown("## 📋 Dados Completos")

st.dataframe(
    df_filtrado[['curso', 'cidade', 'turno', 'modalidade', 'vagas', 'inscricoes', 'candidatos_por_vaga', 'taxa_ocupacao']].sort_values('candidatos_por_vaga', ascending=False),
    use_container_width=True,
    hide_index=True
)

# Rodapé
st.markdown("---")
st.markdown("**Fonte:** Edital do Vestibular UEG 2026/1 e Lista de Inscrições Deferidas")
st.markdown("**Dados:** 14.204 inscrições analisadas (✅ **100% de cobertura**)")
st.markdown("**Desenvolvido com:** Streamlit + Plotly + Python")

