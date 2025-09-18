import streamlit as st
st.set_page_config(page_title="Calculator", page_icon="🧮")
st.title("🧮 Simple Calculator")

a = st.number_input("First number (a)", value=0.0)
b = st.number_input("Second number (b)", value=0.0)

op = st.selectbox("Operation", ["+", "-", "×", "÷"])

if st.button("Calculate"):
    try:
        if op == "+":
            res = a + b
        elif op == "-":
            res = a - b
        elif op == "×":
            res = a * b
        else:  # ÷
            if b == 0:
                st.error("Cannot divide by zero.")
                st.stop()
            res = a / b

        st.success(f"Result: {a} {op} {b} = {res}")
    except Exception as e:
        st.error(str(e))       

