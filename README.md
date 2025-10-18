# Overview
The goal of this project is to showcase my skillset while creating a lightweight clone of CoinTrackers with a few key features.
Required:
- Add/Remove bitcoin addresses
- Synchronize bitcoin wallet transactions for the addresses
- Retrieve the current balances and transactions for each bitcoin address

Optional Ideas:
- User Interface - a way for a human user to interact with this project
- Server component with API and API specification/documentation
- Background wallet synchronization
- Data storage

# Approach
Make a small flask API for users to access directly. Then connect a simple frontend for simpler use cases. Finally add some sort of db solution.

## Requirements

- Python 3.9+
- pip (Python package manager)

## Quick Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd CoinTracker-Prototype
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   # In-memory database (for testing)
   python3 main.py

   # Persistent database (saved to file)
   python3 main.py test.db
   ```

4. **Access the test interface**
   - Open browser to: `http://localhost:5000`
   - Or use API endpoints directly at `http://localhost:5000/<endpoint>`

5. **Run tests** (optional)
   ```bash
   python3 test_endpoints.py
   ```

## Features

- Add/Remove Bitcoin addresses
- Synchronize wallet transactions from blockchain.com
- Retrieve current balances and transaction history
- RESTful API with 11 endpoints
- Interactive web testing interface
- Configurable transaction storage limits (TXNS_TO_STORE in .env)

# API Endpoints
## User Management

### Add User
**POST** `/add_user`

Create a new user with optional Bitcoin addresses

**Body:**
```json
{
  "name": "Alice",
  "addresses": ["addr1", "addr2"]
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "name": "Alice",
  "addresses": ["addr1", "addr2"]
}
```

---

### Generate Random User
**POST** `/generate_random_user`

Generate a random test user with 0-4 random Bitcoin addresses

**Body:**
```json
{}
```

**Response:**
```json
{
  "success": true,
  "user_id": 5,
  "name": "Brady",
  "addresses": ["3E8ociqZa9mZUSwGdSmAEMAoAxBK3FNDcd"],
  "message": "Random user \"Brady\" created with 1 address(es)"
}
```

---

### Retrieve User Data
**GET** `/retrieve_user_data?user_id=1`

Get user details and their Bitcoin addresses

**Body:**
```
None
```

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "name": "Alice",
  "addresses": ["addr1", "addr2"]
}
```

---

### Get All Users
**GET** `/get_all_users`

Retrieve all users from the database

**Body:**
```
None
```

**Response:**
```json
[
  {
    "user_id": 1,
    "name": "Alice",
    "addresses": ["addr1", "addr2"]
  }
]
```

---

## Address Management

### Add Addresses
**POST** `/add_addresses`

Add Bitcoin addresses to an existing user (avoids duplicates)

**Body:**
```json
{
  "user_id": 1,
  "addresses": ["addr1", "addr2"]
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "name": "Alice",
  "addresses": ["addr1", "addr2", "addr3", "addr4"]
}
```

---

### Remove Addresses
**POST** `/remove_addresses`

Remove Bitcoin addresses from a user

**Body:**
```json
{
  "user_id": 1,
  "addresses": ["addr2", "addr3"]
}
```

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "name": "Alice",
  "addresses": ["addr1", "addr4"],
  "removed_count": 2
}
```

---

## Blockchain Data

### Get Address Data
**POST** `/get_address_data`

Fetch live blockchain data for multiple addresses and update transaction database

**Body:**
```json
{
  "addresses": ["3E8ociqZa9mZUSwGdSmAEMAoAxBK3FNDcd"]
}
```

**Response:**
```json
{
  "success": true,
  "results": {
    "3E8ociqZa9mZUSwGdSmAEMAoAxBK3FNDcd": {
      "success": true,
      "data": {}
    }
  }
}
```

---

### Get Raw Address Data
**GET** `/get_raw_address_data?address=3E8ociqZa9mZUSwGdSmAEMAoAxBK3FNDcd`

Get raw blockchain data for a specific Bitcoin address

**Body:**
```
None
```

**Response:**
```json
{
  "success": true,
  "address": "3E8ociqZa9mZUSwGdSmAEMAoAxBK3FNDcd",
  "data": {...}
}
```

---

## Transactions

### Get Transactions by User
**GET** `/get_txns_by_user?user_id=1`

Get all stored transactions for all addresses belonging to a user

**Body:**
```
None
```

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "name": "Alice",
  "addresses": {
    "3E8ociqZa9mZUSwGdSmAEMAoAxBK3FNDcd": []
  },
  "total_transactions": 0
}
```

---

### Get Transactions by Address
**GET** `/get_txns_by_address?address=3E8ociqZa9mZUSwGdSmAEMAoAxBK3FNDcd`

Get all stored transactions for a specific Bitcoin address

**Body:**
```
None
```

**Response:**
```json
{
  "success": true,
  "address": "3E8ociqZa9mZUSwGdSmAEMAoAxBK3FNDcd",
  "transactions": [],
  "count": 0
}
```

---

### Get All Transactions
**GET** `/get_all_txns`

Retrieve all transactions from the database

**Body:**
```
None
```

**Response:**
```json
[
  {
    "hash": "779d71a447...",
    "address": "3E8ociqZa9mZUSwGdSmAEMAoAxBK3FNDcd",
    "balance": 26169,
    "block_height": 916828,
    "fee": 288,
    "result": 1000,
    "time": 1759091990
  }
]
```


# Database
- sqlite3 for simple filed loaded or in memory db for testing proof of concept (included demo db or from memory)

# Project Structure

- templates/test.html (html/js for the api tester)
.env (environment file to change the amount of transactions saved (blockchain api maxes at 100))
- blockchain.py (handles all the interaction with the blockchain api)
- db_functions.py (functions called to setup the database)
- db.py (wrapper to interact with the database and make queries)
- main.py (driver of the app includes the api and all of the endpoints)
- README.md (this file)
- requirements.txt (required libraries for the project to run)
- response_example.json (sample response from the blockchain api)
- test_endpoints.py (simple testing file)
- test.db (a sample db)

# Architecture
The project consists of a web api using python and flask, a sqlite3 db and a lightweight frontend to interact with the api. Also for our data we are using the blockchain.com api.
**Motivations for each tool**
- Flask: Lightweight framerwork I am familiar with and easy to get a prototype for a demo up and running quickly
- SQLite3: Does not require configuration or a server which is also excellent for a lightweight db with minimal setup requirements
- HTML/JS Frontend: I am traditionally a backend engineer and although I am not closed to frontend development, I wanted to showcase backend development and this was the easiet way to get it done.
- Blockchain.com API: In my limited use with both tools, blockchain.com had less limiting than blockchair
- Testing Suite: Uses all built in methods for little overhead and validation of our endpoints

# Error handling
- basic error handling included with http errors
- logging is sprinkled throughout to help with debugging

# Errors/issues to look out for
- rate limiting from the blockchain apis we are using
- large datasets could cause slow load times

# Improvements
- Could add multithreading in the future
- More robust testing infrastructure
- In a live environment have an actual token system for authentication