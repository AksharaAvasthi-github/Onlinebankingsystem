from pymongo import MongoClient

MONGO_URI = "mongodb+srv://22btrcn129_db_user:Ynmb4hnExkzEHpWk@cluster0.v0w7ew4.mongodb.net/?appName=Cluster0"

client = MongoClient(MONGO_URI)

db = client.get_database("bank")

customers = db.get_collection("customers")
accounts = db.get_collection("accounts")
transactions = db.get_collection("transactions")
requests = db.get_collection("requests")