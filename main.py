from flask import Flask, request, jsonify, render_template
import blockchain as bc
import sys
from db import Database
import json
import db_functions as dbf
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

# check if a db is passed if not create in memory
# note: will create a db if it does not exist
memory = False
if len(sys.argv) == 2: 
    logger.info('Loading db from file: ' + sys.argv[1])
    db_file = sys.argv[1]
    logger.info('db file opened')
else:
    logger.info('Starting in memory...')
    db_file = ':memory:'
    memory = True
    logger.info('database in memory initialized')

db = Database(db_file)
# Initialize empty tables if using memory
if memory:
    logger.info('Initializing empty tables...')
    dbf.initialize_empty_tables(db)
    logger.info('Tables initialized')

# template testing page with all endppoints
@app.route('/')
def index():
    return render_template('test.html')

# USER AND ADDRESS MANAGEMENT

@app.route('/add_user', methods=['POST'])
def add_user():
    try:

        data = request.get_json()

        # check for name
        if not data or 'name' not in data:
            return jsonify({'error': 'name is required'}), 400

        name = data['name']
        addresses = data.get('addresses', [])

        logger.info('adding user: ' + name)

        # make list
        addresses_json = json.dumps(addresses)


        # update txns when a new address is added
        # considered skipping existing wallets but updates can happen between people following the wallet
        #Unlikely but possible
        if not addresses_json == None:
            for address in addresses:
                bc.get_address_data_blockchain_com(address, db)


        # insert
        db.execute(
            "INSERT INTO users (name, addresses) VALUES (?, ?)",
            (name, addresses_json)
        )
        db.commit()

        # Get the newly created user_id
        user_id = db.cursor.lastrowid

        logger.info('user added: ' + name + ' with id: ' + str(user_id))

        return jsonify({
            'success': True,
            'user_id': user_id,
            'name': name,
            'addresses': addresses
        }), 201

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    
@app.route('/add_addresses', methods=['POST'])
def add_addresses():
    try:
        data = request.get_json()

        # validate
        if not data or 'user_id' not in data or 'addresses' not in data:
            return jsonify({'error': 'user_id and addresses are required'}), 400

        user_id = data['user_id']
        new_addresses = data['addresses']

        logger.info('adding addresses to user: ' + str(user_id) + ' with addresses: ' + str(new_addresses))

        # Validate that addresses is a list
        if not isinstance(new_addresses, list):
            return jsonify({'error': 'addresses must be a list'}), 400

        if not new_addresses == None:
            for address in new_addresses:
                bc.get_address_data_blockchain_com(address, db)

        # retrieve 
        db.execute("SELECT user_id, name, addresses FROM users WHERE user_id = ?", (user_id,))
        user = db.fetchone()

        if not user:
            return jsonify({'error': f'User with user_id {user_id} not found'}), 404

        existing_addresses = json.loads(user['addresses'])

        # add new addres (checks for dupes)
        for addr in new_addresses:
            if addr not in existing_addresses:
                existing_addresses.append(addr)

        # Convert back to JSON and update database
        updated_addresses_json = json.dumps(existing_addresses)
        db.execute(
            "UPDATE users SET addresses = ? WHERE user_id = ?",
            (updated_addresses_json, user_id)
        )
        db.commit()

        logger.info('added addresses to user: ' + str(user_id) + ' with addresses: ' + str(new_addresses))

        return jsonify({
            'success': True,
            'user_id': user_id,
            'name': user['name'],
            'addresses': existing_addresses
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/remove_addresses', methods=['POST'])
def remove_addresses():
    try:
        data = request.get_json()

        # validate
        if not data or 'user_id' not in data or 'addresses' not in data:
            return jsonify({'error': 'user_id and addresses are required'}), 400

        user_id = data['user_id']
        addresses_to_remove = data['addresses']

        logger.info('removing addresses from user: ' + str(user_id) + ' with addresses: ' + str(addresses_to_remove))

        # validate type
        if not isinstance(addresses_to_remove, list):
            return jsonify({'error': 'addresses must be a list'}), 400

        # get useer
        db.execute("SELECT user_id, name, addresses FROM users WHERE user_id = ?", (user_id,))
        user = db.fetchone()

        if not user:
            return jsonify({'error': f'User with user_id {user_id} not found'}), 404

        # pull curr addresses
        existing_addresses = json.loads(user['addresses'])

        # rremove addresses if they exist
        updated_addresses = [addr for addr in existing_addresses if addr not in addresses_to_remove]

        # store as json
        updated_addresses_json = json.dumps(updated_addresses)
        db.execute(
            "UPDATE users SET addresses = ? WHERE user_id = ?",
            (updated_addresses_json, user_id)
        )
        db.commit()

        logger.info('removed user with id: ' + str(user_id) + ' and addresses: ' + str(addresses_to_remove))

        return jsonify({
            'success': True,
            'user_id': user_id,
            'name': user['name'],
            'addresses': updated_addresses,
            'removed_count': len(existing_addresses) - len(updated_addresses)
        }), 200

    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/retrieve_user_data', methods=['GET'])
def retrieve_user_data():
    try:
        user_id = request.args.get('user_id')

        # validate
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        logger.info('retrieving user data for user: ' + str(user_id))

        # query db
        db.execute("SELECT user_id, name, addresses FROM users WHERE user_id = ?", (user_id,))
        user = db.fetchone()

        # validate
        if not user:
            return jsonify({'error': f'User with user_id {user_id} not found'}), 404

        addresses = json.loads(user['addresses'])

        # Return user data
        return jsonify({
            'success': True,
            'user_id': user['user_id'],
            'name': user['name'],
            'addresses': addresses
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/get_address_data', methods=['POST'])
def get_address_data():
    try:
        data = request.get_json()

        # check fields
        if not data or 'addresses' not in data:
            return jsonify({'error': 'addresses array is required'}), 400

        addresses = data['addresses']

        logger.info('retrieving address data for addresses: ' + str(addresses))


        # validate list
        if not isinstance(addresses, list):
            return jsonify({'error': 'addresses must be a list'}), 400

        # make sure it's a list
        if len(addresses) == 0:
            return jsonify({'error': 'addresses array cannot be empty'}), 400

        # iterate through addresse using blockchain.py func
        results = {}
        for address in addresses:
            try:
                address_data = bc.get_address_data_blockchain_com(address, db)
                results[address] = {
                    'success': True,
                    'data': address_data
                }
            except Exception as e:
                results[address] = {
                    'success': False,
                    'error': str(e)
                }

        return jsonify({
            'success': True,
            'results': results
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/get_txns_by_user', methods=['GET'])
def get_txns_by_user():
    try:
        
        user_id = request.args.get('user_id')

        # validation
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        logger.info('retrieving txns for user: ' + str(user_id))

        # retrieve adresses
        db.execute("SELECT user_id, name, addresses FROM users WHERE user_id = ?", (user_id,))
        user = db.fetchone()

        # check user exists
        if not user:
            return jsonify({'error': f'User with user_id {user_id} not found'}), 404
        
        user_addresses = json.loads(user['addresses'])

        # if no addresses exit early
        if len(user_addresses) == 0:
            return jsonify({
                'success': True,
                'user_id': user['user_id'],
                'name': user['name'],
                'addresses': {},
                'total_transactions': 0
            }), 200

        # get transaction per address per user
        transactions_by_address = {}
        total_transactions = 0

        for address in user_addresses:
            txn_list = retrieve_txns(address)
            transactions_by_address[address] = txn_list
            total_transactions += len(txn_list)

        return jsonify({
            'success': True,
            'user_id': user['user_id'],
            'name': user['name'],
            'addresses': transactions_by_address,
            'total_transactions': total_transactions
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_txns_by_address', methods=['GET'])
def get_txns_by_address():
    try:
        address = request.args.get('address')

        # validate
        if not address:
            return jsonify({'error': 'address is required'}), 400

        logger.info('retrieving txns for address: ' + str(address))

        bc.get_address_data_blockchain_com(address, db)

        # get txns using helper
        txn_list = retrieve_txns(address)

        return jsonify({
            'success': True,
            'address': address,
            'transactions': txn_list,
            'count': len(txn_list)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500    
    
@app.route('/get_raw_address_data', methods=['GET'])
def get_raw_address_data():
    try:
        address = request.args.get('address')
        # validate
        if not address:
            return jsonify({'error': 'address is required'}), 400
        
        logger.info('retrieving raw data for address: ' + str(address))

        # get raw data data for address: ' + str(address))

        raw_data = bc.get_address_data_blockchain_com(address, db, True)

        return jsonify({
            'success': True,
            'address': address,
            'data': raw_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500 

# test function 
@app.route('/get_all_users', methods=['GET'])
def get_all_users():
    # retrieve users
    logger.info('retrieving all users')

    db.execute("SELECT user_id, name, addresses FROM users")
    users_raw = db.fetchall()

    users_list = []
    for user in users_raw:
        users_list.append({
            'user_id': user['user_id'],
            'name': user['name'],
            'addresses': json.loads(user['addresses'])
        })

    return users_list

# test function 
@app.route('/get_all_txns', methods=['GET'])
def get_all_txns():
    logger.info('retrieving all txns')

    # retrieve txns
    db.execute("SELECT * FROM transactions")
    txns_raw = db.fetchall()

    txns_list = []
    for txn in txns_raw:
        txns_list.append({
            'hash': txn['hash'],
            'address': txn['address'],
            'balance': txn['balance'],
            'block_height': txn['block_height'],
            'block_index': txn['block_index'],
            'double_spend': txn['double_spend'],
            'fee': txn['fee'],
            'result': txn['result'],
            'size': txn['size'],
            'time': txn['time'],
            'tx_index': txn['tx_index']
        })

    return txns_list

# test function calls dbf to make arandom user
@app.route('/generate_random_user', methods=['POST'])
def generate_random_user():
    try:
        logger.info('generating random user')
        # random user func
        user_id = dbf.create_random_user(db)

        # grab what we just made
        db.execute("SELECT user_id, name, addresses FROM users WHERE user_id = ?", (user_id,))
        user = db.fetchone()

        if not user:
            return jsonify({'error': 'Failed to create user'}), 500

        addresses = json.loads(user['addresses'])

        if not addresses == None:
            for address in addresses:
                bc.get_address_data_blockchain_com(address, db)

        logger.info('random user created: ' + user['name'] + ' with addresses: ' + str(addresses) + 'and id: ' + str(user['user_id']))


        return jsonify({
            'success': True,
            'user_id': user['user_id'],
            'name': user['name'],
            'addresses': addresses,
            'message': f'Random user "{user["name"]}" created with {len(addresses)} address(es)'
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# helper function for getting txns by address
def retrieve_txns(address):
    db.execute(
            "SELECT * FROM transactions WHERE address = ? ORDER BY time DESC",
            (address,)
        )
    txns = db.fetchall()

    # convert to list
    txn_list = []
    for txn in txns:
        txn_list.append({
            'hash': txn['hash'],
            'balance': txn['balance'],
            'block_height': txn['block_height'],
            'block_index': txn['block_index'],
            'double_spend': bool(txn['double_spend']),
            'fee': txn['fee'],
            'result': txn['result'],
            'size': txn['size'],
            'time': txn['time'],
            'tx_index': txn['tx_index']
        })
    return txn_list

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        # close connection 
        db.close()