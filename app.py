import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

# 🌌 Background CSS (purple gradient)
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    color: white;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29, #302b63);
}

/* Cards */
.card {
    background-color: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 15px;
    border: 1px solid rgba(255,255,255,0.1);
}

/* Buttons */
.stButton>button {
    border-radius: 10px;
    background: linear-gradient(90deg, #8e2de2, #4a00e0);
    color: white;
    font-weight: bold;
    box-shadow: 0px 0px 10px rgba(142, 45, 226, 0.7);
}

/* Inputs */
.stTextInput input, .stNumberInput input {
    border-radius: 8px;
    background-color: rgba(255,255,255,0.05);
    color: white;
}

/* Title glow */
h1 {
    text-align: center;
    text-shadow: 0px 0px 15px #8e2de2;
}
</style>
""", unsafe_allow_html=True)


# 🔐 Session
if "token" not in st.session_state:
    st.session_state.token = None

st.title("🏦 Online Banking System")

# Sidebar
st.sidebar.markdown("### 🔐 Status")
st.sidebar.write("✅ Logged in" if st.session_state.token else "❌ Not logged in")

menu_options = ["Login"]
if st.session_state.token:
    menu_options += [
        "Add Balance", "Transfer", "Set Limit",
        "Transactions", "Insights", "Service Request"
    ]

menu = st.sidebar.selectbox("Menu", menu_options)


# 🔹 LOGIN
if menu == "Login":
    st.markdown("### 🔑 Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.post(f"{BASE_URL}/login", json={
            "email": email,
            "password": password
        })

        try:
            data = res.json()
            if "token" in data:
                st.session_state.token = data["token"]
                st.success("✅ Logged in successfully!")
                st.rerun()
            else:
                st.error(data.get("error", "Login failed"))
        except:
            st.error(res.text)


# 🔹 ADD BALANCE
elif menu == "Add Balance":
    st.markdown("### 💰 Add Balance")

    acc_id = st.text_input("Account ID")
    amount = st.number_input("Amount")

    if st.button("Update Balance"):
        res = requests.post(f"{BASE_URL}/add-balance", json={
            "token": st.session_state.token,
            "account_id": acc_id,
            "amount": amount
        })

        try:
            data = res.json()
            st.success(data.get("msg", "Balance updated"))
        except:
            st.error(res.text)


# 🔹 TRANSFER
elif menu == "Transfer":
    st.markdown("### 🔁 Transfer Money")

    from_acc = st.text_input("From Account")
    to_acc = st.text_input("To Account")
    amount = st.number_input("Amount")

    if st.button("Transfer"):
        res = requests.post(f"{BASE_URL}/transfer", json={
            "token": st.session_state.token,
            "from_account": from_acc,
            "to_account": to_acc,
            "amount": amount
        })

        try:
            data = res.json()
            if "msg" in data:
                st.success(f"✅ {data['msg']}")
            else:
                st.error(data)
        except:
            st.error(res.text)


# 🔹 SET LIMIT
elif menu == "Set Limit":
    st.markdown("### ⚙️ Set Transaction Limit")

    acc_id = st.text_input("Account ID")
    limit = st.number_input("New Limit")

    if st.button("Update Limit"):
        res = requests.post(f"{BASE_URL}/set-limit", json={
            "token": st.session_state.token,
            "account_id": acc_id,
            "limit": limit
        })

        try:
            data = res.json()
            st.success(data.get("msg", "Limit updated"))
        except:
            st.error(res.text)


# 🔹 TRANSACTIONS
elif menu == "Transactions":
    st.markdown("### 📄 Transaction History")

    acc_id = st.text_input("Account ID")

    if st.button("Load Transactions"):
        res = requests.get(
            f"{BASE_URL}/transactions/{acc_id}?token={st.session_state.token}"
        )

        try:
            data = res.json()
            for t in data:
                st.markdown(f"""
                <div class="card">
                💸 <b>Amount:</b> {t['amount']} <br>
                🔁 {t['from_account']} → {t['to_account']} <br>
                📊 Status: {t['status']}
                </div>
                """, unsafe_allow_html=True)
        except:
            st.error(res.text)


# 🔹 INSIGHTS
elif menu == "Insights":
    st.markdown("### 🤖 Spending Insights")

    acc_id = st.text_input("Account ID")

    if st.button("Get Insights"):
        res = requests.get(
            f"{BASE_URL}/insights/{acc_id}?token={st.session_state.token}"
        )

        try:
            data = res.json()
            st.metric("Total Spent", data["total_spent"])
            st.metric("Average Transaction", data["avg_transaction"])
            st.metric("Transactions", data["num_transactions"])
        except:
            st.error(res.text)


# 🔹 SERVICE REQUEST
elif menu == "Service Request":
    st.markdown("### 🛠 Service Request")

    req_type = st.selectbox("Request Type", [
        "Card Block", "Complaint", "Account Issue", "Other"
    ])

    description = st.text_area("Description")

    # ✅ Submit request (NO customer_id)
    if st.button("Submit Request"):
        res = requests.post(
            f"{BASE_URL}/request-service?token={st.session_state.token}",
            json={
                "type": req_type,
                "description": description
            }
        )

        try:
            data = res.json()
            if "msg" in data:
                st.success(data["msg"])
            else:
                st.error(data)
        except:
            st.error(res.text)

    st.markdown("### 📋 My Requests")

    # ✅ Load requests (NO customer_id)
    if st.button("Load Requests"):
        res = requests.get(
            f"{BASE_URL}/requests/me?token={st.session_state.token}"
        )

        try:
            data = res.json()

            if isinstance(data, dict) and "error" in data:
                st.error(data["error"])
            else:
                if not data:
                    st.info("No requests found")
                else:
                    for r in data:
                        st.markdown(f"""
                        <div class="card">
                        📌 <b>{r['type']}</b><br>
                        📝 {r['description']}<br>
                        📊 Status: {r['status']}
                        </div>
                        """, unsafe_allow_html=True)

        except:
            st.error(res.text)