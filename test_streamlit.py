"""
Teste simples do Streamlit
"""

import streamlit as st

st.set_page_config(page_title="Teste", page_icon="🧪")

st.title("🧪 Teste Streamlit")
st.write("Se você vê esta mensagem, o Streamlit está funcionando!")

if st.button("Clique aqui"):
    st.success("✅ Funcionando perfeitamente!")
    st.balloons()

st.sidebar.write("Menu lateral funcionando")
