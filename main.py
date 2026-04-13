from fastapi import FastAPI
from database import customers, accounts, transactions
import uuid
from datetime import datetime
from pydantic import BaseModel
from database import requests

app = FastAPI()

class ServiceRequest(BaseModel):
    customer_id: str
    type: str
    description: str

@app.get("/")
def home():
    return {"msg": "API running"}


# 🟢 Login (with token)
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


# 🔐 Auth helper
def get_user(token):
    return customers.find_one({"token": token})


# 🟢 Add Balance (FIXED)
@app.post("/add-balance")
def add_balance(data: dict):
    acc = accounts.find_one({"account_id": data["account_id"]})

    if not acc:
        return {"error": "Account not found"}

    accounts.update_one(
        {"account_id": data["account_id"]},
        {"$set": {"balance": data["amount"]}}
    )

    return {"msg": "Balance updated"}


# 🤖 AI Fraud Detection
def detect_anomaly(account_id, amount):
    user_txns = list(transactions.find({"from_account": account_id}))

    if len(user_txns) < 3:
        return 0

    avg = sum(t["amount"] for t in user_txns) / len(user_txns)

    if amount > avg * 3:
        return 1

    return 0


# 🟢 Transfer (FULL FIX)
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

    # 🔒 ensure user owns account
    if from_acc["customer_id"] != user["customer_id"]:
        return {"error": "Unauthorized access"}

    if amount <= 0:
        return {"error": "Invalid amount"}

    if amount > from_acc["balance"]:
        return {"error": "Insufficient balance"}

    if amount > from_acc.get("transaction_limit", 10000):
        return {"error": "Limit exceeded"}

    # 🤖 AI fraud detection
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
        "from_account": data["from_account"],
        "to_account": data["to_account"],
        "amount": amount,
        "status": "SUCCESS",
        "flagged": flagged,
        "timestamp": datetime.utcnow()
    })

    return {"msg": "Transfer successful", "flagged": flagged}


# 🟢 Set Limit (FIXED)
@app.post("/set-limit")
def set_limit(data: dict):
    accounts.update_one(
        {"account_id": data["account_id"]},
        {"$set": {"transaction_limit": data["limit"]}}
    )

    return {"msg": "Limit updated"}


# 🟢 Transaction History
@app.get("/transactions/{account_id}")
def get_transactions(account_id: str):
    txns = list(transactions.find({
        "$or": [
            {"from_account": account_id},
            {"to_account": account_id}
        ]
    }))

    for t in txns:
        t["_id"] = str(t["_id"])

    return txns


# 🤖 AI Insights
@app.get("/insights/{account_id}")
def insights(account_id: str):
    txns = list(transactions.find({"from_account": account_id}))

    total = sum(t["amount"] for t in txns)
    count = len(txns)
    avg = total / count if count else 0

    return {
        "total_spent": total,
        "avg_transaction": avg,
        "num_transactions": count
    }

@app.post("/request-service")
def request_service(data: ServiceRequest):
    requests.insert_one({
        "customer_id": data.customer_id,
        "type": data.type,
        "description": data.description,
        "status": "PENDING",
        "timestamp": datetime.utcnow()
    })

    return {"msg": "Service request submitted"}

@app.get("/requests/{customer_id}")
def get_requests(customer_id: str):
    reqs = list(requests.find({"customer_id": customer_id}))

    for r in reqs:
        r["_id"] = str(r["_id"])

    return reqs

@app.post("/update-request")
def update_request(data: dict):
    requests.update_one(
        {"_id": ObjectId(data["request_id"])},
        {"$set": {"status": data["status"]}}
    )

    return {"msg": "Request updated"}