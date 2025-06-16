
import yfinance as yf
import pandas as pd
import ta
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Robô de Investimentos - RSI", layout="wide")

st.title("🤖 Robô de Investimentos com RSI")
st.markdown("Simule operações automáticas com base no Índice de Força Relativa (RSI).")

# Entrada do usuário
ativo = st.text_input("Código do ativo (ex: PETR4.SA, BTC-USD, AAPL):", "PETR4.SA")
inicio = st.date_input("Data inicial", pd.to_datetime("2023-01-01"))
fim = st.date_input("Data final", pd.to_datetime("2025-01-01"))

if st.button("Executar Robô"):
    dados = yf.download(ativo, start=inicio, end=fim)
    if dados.empty:
        st.error("Não foi possível obter dados para esse ativo.")
    else:
        dados['RSI'] = ta.momentum.RSIIndicator(dados['Close'], window=14).rsi()
        dados['Sinal'] = 0
        dados.loc[dados['RSI'] < 30, 'Sinal'] = 1  # Compra
        dados.loc[dados['RSI'] > 70, 'Sinal'] = -1  # Venda

        # Simulação de operações
        capital_inicial = 10000
        posicao = 0
        capital = capital_inicial
        historico = []

        for i in range(1, len(dados)):
            preco = dados['Close'].iloc[i]
            sinal = dados['Sinal'].iloc[i]
            data = dados.index[i]

            if sinal == 1 and capital > 0:
                posicao = capital / preco
                capital = 0
                historico.append(("Compra", data, preco))
            elif sinal == -1 and posicao > 0:
                capital = posicao * preco
                posicao = 0
                historico.append(("Venda", data, preco))

        # Resultado final
        if posicao > 0:
            capital = posicao * dados['Close'].iloc[-1]

        lucro = capital - capital_inicial
        st.subheader(f"💰 Lucro final: R${lucro:,.2f}")

        # Gráfico
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(dados['Close'], label='Preço')
        for tipo, data, preco in historico:
            cor = 'g' if tipo == 'Compra' else 'r'
            ax.scatter(data, preco, color=cor, label=tipo)
        ax.set_title(f"{ativo} - Estratégia RSI")
        ax.legend()
        ax.grid()
        st.pyplot(fig)
