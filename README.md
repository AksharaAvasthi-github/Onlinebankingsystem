Online Banking – Customer Account & Transaction Management System
A basic online banking platform that allows customers to manage accounts, perform transactions, and raise service requests through a digital interface without visiting a physical bank branch.
This project demonstrates backend API development, database management, and UI integration using Python technologies.
📌 Technology Stack
Backend Framework: FastAPI (Python)
Database: MongoDB Atlas
Frontend / UI: Streamlit 
API Architecture: REST APIs
Language: Python
📖 Problem Statement
Modern banks require a secure and user-friendly digital platform where customers can:
Manage their bank accounts
Perform fund transfers
Check balances and account details
Raise service requests
Traditional banking often requires visiting a branch, which is inefficient. This system provides a digital banking solution that simplifies customer operations.
🎯 Project Goals
The main objectives of the system are:
Build REST APIs for:
Customer onboarding
Account management
Transactions
Service requests
Store and manage data for:
Customers
Accounts
Transactions
Service requests
Develop a simple UI interface that interacts with backend APIs.
✅ Success Criteria
The project is considered successful if:
Customers can log in and view account details
Customers can check account balance
Fund transfers update balances correctly
The UI communicates successfully with backend APIs
🗂 System Architecture

User (Frontend UI)
        │
        ▼
    Streamlit UI
        │
        ▼
     FastAPI Backend
        │
        ▼
      Database
Flow:
User interacts with the UI
UI sends requests to FastAPI backend APIs
Backend processes the request
Data is stored/retrieved from the database
Response is returned to the UI