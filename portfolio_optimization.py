# -*- coding: utf-8 -*-
"""portfolio_optimization.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1S5tQGg36fGeQQqCQaYoNVIt0_K_EmYYo
"""

pip install streamlit yfinance PyPortfolioOpt matplotlib

import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.expected_returns import mean_historical_return
from pypfopt.plotting import plot_weights

# Configuração do título da aplicação
st.title("Otimização de Portfólio - Índice de Sharpe")

# Entrada de tickers pelo usuário
st.sidebar.header("Configurações do Portfólio")
tickers = st.sidebar.text_area("Insira os tickers (separados por vírgula):", "AAPL,MSFT,GOOG,AMZN")
tickers = [ticker.strip().upper() for ticker in tickers.split(",")]

# Definir o horizonte de tempo
periodo = st.sidebar.selectbox("Horizonete de tempo para os dados históricos:", ["1y", "3y", "5y"])
st.sidebar.write("Você selecionou:", periodo)

if st.sidebar.button("Calcular Portfólio Ótimo"):
    try:
        # Baixar os dados históricos do Yahoo Finance
        st.write("Obtendo dados dos ativos...")
        dados = yf.download(tickers, period=periodo)["Adj Close"]

        # Verificar se há dados suficientes
        if dados.isnull().sum().sum() > 0:
            st.warning("Alguns ativos possuem dados incompletos. Eles serão ignorados.")

        # Calcular retornos esperados e matriz de covariância
        retornos_esperados = mean_historical_return(dados)
        matriz_covariancia = CovarianceShrinkage(dados).ledoit_wolf()

        # Otimização do portfólio para maximizar o Índice de Sharpe
        ef = EfficientFrontier(retornos_esperados, matriz_covariancia)
        pesos = ef.max_sharpe()
        ef.clean_weights()

        # Mostrar os pesos otimizados
        st.subheader("Pesos Ótimos do Portfólio:")
        st.write(pd.DataFrame.from_dict(pesos, orient="index", columns=["Peso"]).round(4))

        # Gráfico de composição do portfólio
        fig, ax = plt.subplots()
        plot_weights(pesos, ax=ax)
        st.pyplot(fig)

        # Mostrar métricas do portfólio otimizado
        desempenho = ef.portfolio_performance(verbose=True)
        st.subheader("Desempenho do Portfólio:")
        st.write(f"Retorno Esperado: {desempenho[0]:.2%}")
        st.write(f"Volatilidade: {desempenho[1]:.2%}")
        st.write(f"Índice de Sharpe: {desempenho[2]:.2f}")

    except Exception as e:
        st.error(f"Ocorreu um erro: {str(e)}")

streamlit run portfolio_optimization.py