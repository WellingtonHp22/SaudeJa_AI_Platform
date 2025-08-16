import streamlit as st

st.set_page_config(page_title="Teste SaudeJá", page_icon="🏥")

st.title("🏥 SaudeJá - Teste")
st.write("Se você vê esta mensagem, o Streamlit está funcionando!")

if st.button("Clique aqui"):
    st.success("✅ Funcionando perfeitamente!")
    st.balloons()
