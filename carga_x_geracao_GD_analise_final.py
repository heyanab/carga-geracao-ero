
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title='Carga x Geração', layout='wide')
st.title('📊 Carga x Geração – Análise de GD Injetada por Transformador (Mensal)')

st.markdown('Faça upload de um arquivo Excel com a aba **Dados**, contendo as colunas: Ano, Mês, Geração (kW), Trafo, POT DISPONÍVEL, CLIENTES.')

uploaded_file = st.file_uploader("📁 Upload da planilha (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, sheet_name="Dados")
        required_cols = {"Ano", "Mês", "Geração (kW)", "Trafo", "POT DISPONÍVEL ", "CLIENTES"}

        if not required_cols.issubset(df.columns):
            st.error(f"❌ A planilha deve conter as colunas: {required_cols}")
        else:
            df["Mês/Ano"] = df["Mês"].astype(str) + "/" + df["Ano"].astype(str)
            df["Capacidade (kW)"] = df["POT DISPONÍVEL "] * 0.92
            df["% Carregamento GD"] = (df["Geração (kW)"] / df["Capacidade (kW)"]) * 100

            def classificar(p):
                if p > 140:
                    return "Obra necessária"
                elif p > 120:
                    return "Atenção"
                else:
                    return "OK"

            df["Classificação"] = df["% Carregamento GD"].apply(classificar)

            trafos = df["Trafo"].unique()
            trafo_sel = st.selectbox("🔌 Selecione o transformador", trafos)

            df_trafo = df[df["Trafo"] == trafo_sel].sort_values("Ano")

            st.subheader(f"📈 Gráfico de GD Injetada - {trafo_sel}")
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.plot(df_trafo["Mês/Ano"], df_trafo["% Carregamento GD"], marker='o', linewidth=2, color='royalblue', label="% GD / Capacidade")
            ax.axhline(100, color='gray', linestyle='--', linewidth=1, label='Limite 100%')
            ax.axhline(120, color='orange', linestyle='--', linewidth=1, label='Atenção (120%)')
            ax.axhline(140, color='red', linestyle='--', linewidth=1, label='Limite Obra (140%)')
            ax.set_ylabel('% de Carregamento GD')
            ax.set_xlabel('Mês/Ano')
            ax.set_title(f'Carregamento GD - {trafo_sel}')
            ax.grid(True, linestyle='--', alpha=0.4)
            ax.legend()
            st.pyplot(fig)

            st.subheader("📋 Tabela de Resultados")
            st.dataframe(df_trafo[["Ano", "Mês", "Geração (kW)", "Capacidade (kW)", "% Carregamento GD", "Classificação", "CLIENTES"]])

            csv = df_trafo.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Baixar CSV da análise", csv, file_name=f"analise_{trafo_sel}.csv")

    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
