import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

# 🔐 Session token
if "token" not in st.session_state:
    st.session_state.token = None

st.title("🏦 Online Banking System")

st.sidebar.write("✅ Logged in" if st.session_state.token else "❌ Not logged in")

menu = st.sidebar.selectbox("Menu", [
    "Login",
    "Add Balance",
    "Transfer",
    "Set Limit",
    "Transactions",
    "Insights"
])


# 🔹 Login
if menu == "Login":
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(f"{BASE_URL}/login", json={
            "email": email,
            "password": password
        })

        data = res.json()

        if "token" in data:
            st.session_state.token = data["token"]
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error(data.get("error"))


# 🔹 Add Balance
elif menu == "Add Balance":
    acc_id = st.text_input("Account ID")
    amount = st.number_input("Amount")

    if st.button("Update Balance"):
        res = requests.post(f"{BASE_URL}/add-balance", json={
            "account_id": acc_id,
            "amount": amount
        })
        st.write(res.json())


# 🔹 Transfer
elif menu == "Transfer":
    from_acc = st.text_input("From Account ID")
    to_acc = st.text_input("To Account ID")
    amount = st.number_input("Amount")

    if st.button("Transfer"):
        if not st.session_state.token:
            st.error("Login first!")
        else:
            res = requests.post(f"{BASE_URL}/transfer", json={
                "token": st.session_state.token,
                "from_account": from_acc,
                "to_account": to_acc,
                "amount": amount
            })
            st.write(res.json())


# 🔹 Set Limit
elif menu == "Set Limit":
    acc_id = st.text_input("Account ID")
    limit = st.number_input("New Limit")

    if st.button("Set Limit"):
        res = requests.post(f"{BASE_URL}/set-limit", json={
            "account_id": acc_id,
            "limit": limit
        })
        st.write(res.json())


# 🔹 Transactions
elif menu == "Transactions":
    acc_id = st.text_input("Account ID")

    if st.button("Get Transactions"):
        res = requests.get(f"{BASE_URL}/transactions/{acc_id}")
        st.write(res.json())


# 🔹 Insights (AI 🔥)
elif menu == "Insights":
    acc_id = st.text_input("Account ID")

    if st.button("Get Insights"):
        res = requests.get(f"{BASE_URL}/insights/{acc_id}")
        st.write(res.json())