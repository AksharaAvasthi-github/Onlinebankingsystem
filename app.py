import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

# Background CSS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0e1117;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

#  Session token
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
    "Insights",
    "Service Request"
])


#  Login
if menu == "Login":
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
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error(data.get("error"))
        except:
            st.error(res.text)


#  Add Balance
elif menu == "Add Balance":
    acc_id = st.text_input("Account ID")
    amount = st.number_input("Amount")

    if st.button("Update Balance"):
        res = requests.post(f"{BASE_URL}/add-balance", json={
            "account_id": acc_id,
            "amount": amount
        })

        try:
            st.write(res.json())
        except:
            st.error(res.text)


#  Transfer
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

            try:
                st.write(res.json())
            except:
                st.error(res.text)


#  Set Limit
elif menu == "Set Limit":
    acc_id = st.text_input("Account ID")
    limit = st.number_input("New Limit")

    if st.button("Set Limit"):
        res = requests.post(f"{BASE_URL}/set-limit", json={
            "account_id": acc_id,
            "limit": limit
        })

        try:
            st.write(res.json())
        except:
            st.error(res.text)


#  Transactions
elif menu == "Transactions":
    acc_id = st.text_input("Account ID")

    if st.button("Get Transactions"):
        res = requests.get(f"{BASE_URL}/transactions/{acc_id}")

        try:
            st.write(res.json())
        except:
            st.error(res.text)


<<<<<<< HEAD
# 🔹 Insights
=======
#  Insights 
>>>>>>> df914f74c3162233035d0a577680582a75f14388
elif menu == "Insights":
    acc_id = st.text_input("Account ID")

    if st.button("Get Insights"):
        res = requests.get(f"{BASE_URL}/insights/{acc_id}")

        try:
            st.write(res.json())
        except:
            st.error(res.text)


# 🔹 Service Request
elif menu == "Service Request":

    st.subheader("Raise Service Request")

    customer_id = st.text_input("Customer ID")

    req_type = st.selectbox("Request Type", [
        "Card Block",
        "Complaint",
        "Account Issue",
        "Other"
    ])

    description = st.text_area("Description")

    if st.button("Submit Request"):
        res = requests.post(f"{BASE_URL}/request-service", json={
            "customer_id": customer_id,
            "type": req_type,
            "description": description
        })

        try:
            data = res.json()
            st.write(data)   # 🔥 DEBUG SHOW
            if "msg" in data:
                st.success(data["msg"])
            else:
                st.error(data)
        except:
            st.error(res.text)

    st.subheader("View Requests")

    if st.button("Load My Requests"):
        res = requests.get(f"{BASE_URL}/requests/{customer_id}")

        try:
            data = res.json()
            for r in data:
                st.write(f"📌 Type: {r['type']}")
                st.write(f"📊 Status: {r['status']}")
                st.write(f"📝 {r['description']}")
                st.write("---")
        except:
            st.error(res.text)