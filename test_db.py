from database import customers

customers.insert_one({"name": "test", "balance": 1000})

print("Inserted!")