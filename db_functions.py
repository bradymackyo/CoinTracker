# script for setting up db for testing purposes
from db import Database
import random

addresses = ['3E8ociqZa9mZUSwGdSmAEMAoAxBK3FNDcd', 'bc1q0sg9rdst255gtldsmcf8rk0764avqy2h2ksqs5', 'bc1qm34lsc65zpw79lxes69zkqmk6ee3ewf0j77s3h', '12xQ9k5ousS8MqNsMBqHKtjAtCuKezm2Ju']

users = ['Brady', 'Katy', 'Ella', 'Thomas', 'Luke', 'Levi', 'Jake', 'Marie', 'Ashlynn']

def initialize_empty_tables(db):
    # users
    db.create_table(
        "users",
        """
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        addresses TEXT NOT NULL DEFAULT '[]'
        """
    )

    # txns
    db.create_table(
        "transactions",
        """
        hash TEXT PRIMARY KEY,
        address TEXT NOT NULL,
        balance INTEGER,
        block_height INTEGER,
        block_index INTEGER,
        double_spend INTEGER DEFAULT 0,
        fee INTEGER,
        result INTEGER,
        size INTEGER,
        time INTEGER,
        tx_index INTEGER
        """
    )



# test func to add random users
def create_random_user(db):
    import json

    name = random.choice(users)

    num_addresses = random.randint(0, 4)
    selected_addresses = random.sample(addresses, num_addresses)

    addresses_json = json.dumps(selected_addresses)

    db.execute(
        "INSERT INTO users (name, addresses) VALUES (?, ?)",
        (name, addresses_json)
    )
    db.commit()

    return db.cursor.lastrowid


