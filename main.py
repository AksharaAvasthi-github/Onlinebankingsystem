from fastapi import FastAPI
from database import customers, accounts, transactions, requests
import uuid
from datetime import datetime
from pydantic import BaseModel
from bson import ObjectId

app = FastAPI()

# =========================
# 🔐 MODELS
# =========================
class ServiceRequest(BaseModel):
    type: str
    description: str


# =========================
# 🔐 AUTH HELPER
# =========================
def get_user(token):
    return customers.find_one({"token": token})


# =========================
# 🏠 HOME
# =========================
@app.get("/")
def home():
    return {"msg": "API running"}


# =========================
# 🔑 LOGIN
# =========================
@app.post("/login")
def login(user: dict):
    existing = customers.find_one({
        "email": user["email"],
        "password": user["password"]
    })

    if not existing:
        return {"error": "Invalid credentials"}

    token = str(uuid.uuid4())

    customers.update_one(
        {"email": user["email"]},
        {"$set": {"token": token}}
    )

    return {"msg": "Login successful", "token": token}


# =========================
# 💰 ADD BALANCE (SECURE)
# =========================
@app.post("/add-balance")
def add_balance(data: dict):
    user = get_user(data.get("token"))

    if not user:
        return {"error": "Unauthorized"}

    acc = accounts.find_one({"account_id": data["account_id"]})

    if not acc:
        return {"error": "Account not found"}

    if acc["customer_id"] != user["customer_id"]:
        return {"error": "Unauthorized access"}

    accounts.update_one(
        {"account_id": data["account_id"]},
        {"$set": {"balance": data["amount"]}}
    )

    return {"msg": "Balance updated"}


# =========================
# 🤖 FRAUD DETECTION
# =========================
def detect_anomaly(account_id, amount):
    user_txns = list(transactions.find({"from_account": account_id}))

    if len(user_txns) < 3:
        return 0

    avg = sum(t["amount"] for t in user_txns) / len(user_txns)

    return 1 if amount > avg * 3 else 0


# =========================
# 🔁 TRANSFER (SECURE)
# =========================
@app.post("/transfer")
def transfer(data: dict):
    user = get_user(data.get("token"))

    if not user:
        return {"error": "Unauthorized"}

    from_acc = accounts.find_one({"account_id": data["from_account"]})
    to_acc = accounts.find_one({"account_id": data["to_account"]})
    amount = data["amount"]

    if not from_acc or not to_acc:
        return {"error": "Invalid account"}

    if from_acc["customer_id"] != user["customer_id"]:
        return {"error": "Unauthorized access"}

    if amount <= 0:
        return {"error": "Invalid amount"}

    if amount > from_acc["balance"]:
        return {"error": "Insufficient balance"}

    if amount > from_acc.get("transaction_limit", 10000):
        return {"error": "Limit exceeded"}

    flagged = detect_anomaly(data["from_account"], amount)

    # update balances
    accounts.update_one(
        {"account_id": data["from_account"]},
        {"$set": {"balance": from_acc["balance"] - amount}}
    )

    accounts.update_one(
        {"account_id": data["to_account"]},
        {"$set": {"balance": to_acc["balance"] + amount}}
    )

    # save transaction
    transactions.insert_one({
        "transaction_id": str(uuid.uuid4()),
        "from_account": data["from_account"],
        "to_account": data["to_account"],
        "amount": amount,
        "type": "transfer",
        "status": "SUCCESS",
        "flagged": flagged,
        "date": datetime.utcnow().strftime("%Y-%m-%d")
    })

    return {"msg": "Transfer successful", "flagged": flagged}


# =========================
# ⚙️ SET LIMIT (SECURE)
# =========================
@app.post("/set-limit")
def set_limit(data: dict):
    user = get_user(data.get("token"))

    if not user:
        return {"error": "Unauthorized"}

    acc = accounts.find_one({"account_id": data["account_id"]})

    if not acc:
        return {"error": "Account not found"}

    if acc["customer_id"] != user["customer_id"]:
        return {"error": "Unauthorized access"}

    accounts.update_one(
        {"account_id": data["account_id"]},
        {"$set": {"transaction_limit": data["limit"]}}
    )

    return {"msg": "Limit updated"}


# =========================
# 📄 TRANSACTIONS (SECURE)
# =========================
@app.get("/transactions/{account_id}")
def get_transactions(account_id: str, token: str):
    user = get_user(token)

    if not user:
        return {"error": "Unauthorized"}

    acc = accounts.find_one({"account_id": account_id})

    if not acc:
        return {"error": "Account not found"}

    if acc["customer_id"] != user["customer_id"]:
        return {"error": "Unauthorized access"}

    txns = list(transactions.find({
        "$or": [
            {"from_account": account_id},
            {"to_account": account_id}
        ]
    }))

    for t in txns:
        t["_id"] = str(t["_id"])

    return txns


# =========================
# 🤖 INSIGHTS (SECURE)
# =========================
@app.get("/insights/{account_id}")
def insights(account_id: str, token: str):
    user = get_user(token)

    if not user:
        return {"error": "Unauthorized"}

    acc = accounts.find_one({"account_id": account_id})

    if not acc:
        return {"error": "Account not found"}

    if acc["customer_id"] != user["customer_id"]:
        return {"error": "Unauthorized access"}

    txns = list(transactions.find({"from_account": account_id}))

    total = sum(t["amount"] for t in txns)
    count = len(txns)
    avg = total / count if count else 0

    return {
        "total_spent": total,
        "avg_transaction": avg,
        "num_transactions": count
    }


# =========================
# 🛠 SERVICE REQUEST (FIXED)
# =========================
@app.post("/request-service")
def request_service(data: ServiceRequest, token: str):
    user = get_user(token)

    if not user:
        return {"error": "Unauthorized"}

    requests.insert_one({
        "customer_id": user["customer_id"],   # 🔥 AUTO
        "type": data.type,
        "description": data.description,
        "status": "PENDING",
        "timestamp": datetime.utcnow()
    })

    return {"msg": "Service request submitted"}


# =========================
# 📋 GET MY REQUESTS (FIXED)
# =========================
@app.get("/requests/me")
def get_requests(token: str):
    user = get_user(token)

    if not user:
        return {"error": "Unauthorized"}

    reqs = list(requests.find({"customer_id": user["customer_id"]}))

    for r in reqs:
        r["_id"] = str(r["_id"])

    return reqs


# =========================
# 🔧 UPDATE REQUEST
# =========================
@app.post("/update-request")
def update_request(data: dict, token: str):
    user = get_user(token)

    if not user:
        return {"error": "Unauthorized"}

    requests.update_one(
        {"_id": ObjectId(data["request_id"])},
        {"$set": {"status": data["status"]}}
    )

    return {"msg": "Request updated"}