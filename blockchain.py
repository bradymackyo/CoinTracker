import requests
import db
import os
from dotenv import load_dotenv

# load how many transactions we want stored in our local
load_dotenv()

TXNS_TO_STORE = int(os.getenv('TXNS_TO_STORE', 5))
if not isinstance(TXNS_TO_STORE, int):
    TXNS_TO_STORE = 5



# def get_bitcoin_data(address):
#     url = 'https://api.blockchair.com/bitcoin/stats/dashboard/address'
#     response = requests.get(url)
#     data = response.json()
#     return data
    
# def get_address_data(address):
#     try: # try to retrieve all data for the walltet
#         url = f'https://api.blockchair.com/bitcoin/dashboards/address/{address}'
#         response = requests.get(url)
#         data = response.json()
#         return data
#     except Exception as e:
#         return e



# hit the blockchair api limit lol
def get_address_data_blockchain_com(address, db, raw=False):
    try:
        # use the other api
        url = f'https://blockchain.info/rawaddr/{address}'
        response = requests.get(url)

        # check status
        if response.status_code != 200:
            return {
                'error': f'API returned status code {response.status_code}',
                'address': address
            }
        data = response.json()        

        if raw:
            return data
        
        update_txns(db, address, data.get('txs', [])[:TXNS_TO_STORE])


        # brief description of the wallet - no txns
        return {
            'success': True,
            'address': address,
            'final_balance': data.get('final_balance', None),
            'n_tx': data.get('n_tx', None),
            'total_received': data.get('total_received', None),
            'hash_160': data.get('hash_160', None),
            'n_unredeemed': data.get('n_unredeemed', None),
            'total_sent': data.get('total_sent', None)
        }

    except Exception as e:
        return {
            'error': f'Unexpected error: {str(e)}',
            'address': address
        }
    

# after making the query update the local txns with the "5" latest - this can be changed to store more just for the sake of simplicity for this exercise
def update_txns(db, address, txns):
    try:

        # get txns associated with address
        db.execute(
            "SELECT hash, time FROM transactions WHERE address = ? ORDER BY time DESC",
            (address,)
        )
        existing_txns = db.fetchall()
        existing_hashes = {txn['hash']: txn['time'] for txn in existing_txns}

        # extract the hash and time from the 5 most recent txns
        hashes = {txn['hash']: txn['time'] for txn in txns}
        # check what hashes are different
        hashes_to_add = set(hashes.keys()) - set(existing_hashes.keys())
        hashes_to_remove = set(existing_hashes.keys()) - set(hashes.keys())

        transactions_added = 0
        transactions_removed = 0

        # Rdrop txn not in 5 most recent
        if hashes_to_remove:
            for tx_hash in hashes_to_remove:
                db.execute(
                    "DELETE FROM transactions WHERE hash = ? AND address = ?",
                    (tx_hash, address)
                )
                transactions_removed += 1

        # add the new transactions
        for txn in txns:
            if txn['hash'] in hashes_to_add:
                txn_hash = txn.get('hash')
                balance = txn.get('balance', 0)
                block_height = txn.get('block_height')
                block_index = txn.get('block_index')
                double_spend = 1 if txn.get('double_spend', False) else 0
                fee = txn.get('fee', 0)
                result = txn.get('result', 0)
                size = txn.get('size', 0)
                time = txn.get('time', 0)
                txn_index = txn.get('tx_index')

                db.execute("""
                    INSERT OR REPLACE INTO transactions
                    (hash, address, balance, block_height, block_index, double_spend, fee, result, size, time, tx_index)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (txn_hash, address, balance, block_height, block_index, double_spend, fee, result, size, time, txn_index))

                transactions_added += 1

        db.commit()

        return {
            'success': True,
            'address': address,
            'transactions_added': transactions_added,
            'transactions_removed': transactions_removed,
            'total_stored': len(txns)
        }

    except Exception as e:
        db.rollback()
        return {
            'success': False,
            'error': str(e),
            'address': address
        }
