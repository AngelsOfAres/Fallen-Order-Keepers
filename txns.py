import requests
import time
from algosdk import mnemonic
from algosdk.future import transaction
from algosdk.v2client import algod


graphql = 'DGRAPH ENDPOINT API'
dg_auth = 'DGRAPH AUTH KEY'
balance_list = [YOUR ASA IDS HERE]

algod_address = "https://mainnet-algorand.api.purestake.io/ps2"
alog_token = 'YOUR ALGOD YOKEN HERE'
headers2 = {"X-API-Key": alog_token}
algod_client = algod.AlgodClient(alog_token, algod_address, headers2)

base_url = "https://mainnet-idx.algonode.cloud/v2"
headersDG = {"DG-Auth": dg_auth}


async def add_games(address, won, lost, expwon, explost):
    addgame = """
    mutation addGame($address: String!, $won: Int!, $lost: Int!, $expwon: Int!, $explost: Int!) {
      updateDiscordWallets(input: {filter: {address: {eq: $address}}, set: {won: $won, , lost: $lost, expwon: $expwon, explost: $explost}}) {
            numUids
        }
    }
    """
    variables = {'address': address, 'won': won, 'lost': lost, 'expwon': expwon, 'explost': explost}
    request = requests.post(graphql, json={'query': addgame, 'variables': variables}, headers=headersDG)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Update Query failed to run by returning code of {}. {}".format(request.status_code, addgame))
    
async def add_boss_battle(address, weekly_points, total_points):
    addbossbattle = """
    mutation addBossbattle($address: String!, $bossbattles: Int!, $weekly_battles: Int!) {
      updateDiscordWallets(input: {filter: {address: {eq: $address}}, set: {bossbattles: $bossbattles, weekly_battles: $weekly_battles}}) {
            numUids
        }
    }
    """
    variables = {'address': address, 'weekly_battles': weekly_points, 'bossbattles': total_points}
    request = requests.post(graphql, json={'query': addbossbattle, 'variables': variables}, headers=headersDG)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Update Query failed to run by returning code of {}. {}".format(request.status_code, addbossbattle))

async def add_drip(address, current_time, new_exp):
    add_drip = """
    mutation addDrip($address: String!, $lastdrip: DateTime!, $new_exp: Int!) {
      updateDiscordWallets(input: {filter: {address: {eq: $address}}, set: {lastdrip: $lastdrip, drip_exp: $new_exp}}) {
            numUids
        }
    }
    """
    variables = {'address': address, 'lastdrip': current_time, 'new_exp': new_exp}
    request = requests.post(graphql, json={'query': add_drip, 'variables': variables}, headers=headersDG)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Update Query failed to run by returning code of {}. {}".format(request.status_code, add_drip))
    
async def update_wings(address, current_time, wingscount):
    update_wings = """
    mutation addWings($address: String!, $wings_staked: DateTime!, $wingscount: Int!) {
      updateDiscordWallets(input: {filter: {address: {eq: $address}}, set: {wings_staked: $wings_staked, wingscount: $wingscount}}) {
            numUids
        }
    }
    """
    variables = {'address': address, 'wings_staked': current_time, 'wingscount': wingscount}
    request = requests.post(graphql, json={'query': update_wings, 'variables': variables}, headers=headersDG)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Update Query failed to run by returning code of {}. {}".format(request.status_code, update_wings))
    

async def get_all_wallets():

    getallwallets = """
    query queryDiscordWallets {
        queryDiscordWallets {
            address
            name
            userid
        }
    }
    """
    request = requests.post(graphql, json={'query': getallwallets}, headers=headersDG)
    if request.status_code == 200:
        result = request.json()
        if result['data']['queryDiscordWallets'] == []:
            wallets = []
        else:
            wallets = result['data']['queryDiscordWallets']            
        return wallets

async def get_all_lumberjacks():

    getalllumberjacks = """
    query queryDiscordWallets {
        queryDiscordWallets {
            userid
            equipped_hatchet
        }
    }
    """
    request = requests.post(graphql, json={'query': getalllumberjacks}, headers=headersDG)
    if request.status_code == 200:
        result = request.json()
        if result['data']['queryDiscordWallets'] == []:
            equipped_hatchets = []
        else:
            equipped_hatchets = result['data']['queryDiscordWallets']
            
        return equipped_hatchets


async def get_balance(address, token):
    account_info = algod_client.account_info(address)
    assets = account_info.get("assets", [])
    
    for asset in assets:
        if asset["asset-id"] > 0 and asset["asset-id"] == token:
            balance = asset["amount"]
            break
    else:
        balance = -1

    return balance
    

async def get_wallet(userid):

    getwallet = f"""
    query queryDiscordWallets {{
        queryDiscordWallets(filter: {{userid: {{eq: "{userid}"}}}}) {{
            address
            name
            lost
            won
            expwon
            explost
            lastdrip
            drip_exp
        }}
    }}
    """
    variables = {'userid': userid}
    request = requests.post(graphql, json={'query': getwallet, 'variables': variables}, headers=headersDG)
    if request.status_code == 200:
        result = request.json()
        if result['data']['queryDiscordWallets'] == []:
            wallet = ''
            name = ''
            won = 0
            lost = 0
            expwon = 0
            explost = 0
            lastdrip = ''
            drip_exp = 0
        else:
            wallet = result['data']['queryDiscordWallets'][0]['address']
            name = result['data']['queryDiscordWallets'][0]['name']
            won = result['data']['queryDiscordWallets'][0]['won']
            lost = result['data']['queryDiscordWallets'][0]['lost']
            expwon = result['data']['queryDiscordWallets'][0]['expwon']
            explost = result['data']['queryDiscordWallets'][0]['explost']
            lastdrip = result['data']['queryDiscordWallets'][0]['lastdrip']
            drip_exp = result['data']['queryDiscordWallets'][0]['drip_exp']

        return wallet, name, won, lost, expwon, explost, lastdrip, drip_exp
    

async def get_main_char(userid):

    getmain = f"""
    query queryDiscordWallets {{
        queryDiscordWallets(filter: {{userid: {{eq: "{userid}"}}}}) {{
            address
            main_character
            equipped_hatchet
        }}
    }}
    """
    variables = {'userid': userid}
    request = requests.post(graphql, json={'query': getmain, 'variables': variables}, headers=headersDG)
    if request.status_code == 200:
        result = request.json()
        if result['data']['queryDiscordWallets'] == []:
            wallet = ''
            main_character = int(0)
            equipped_hatchet = int(0)
        else:
            wallet = result['data']['queryDiscordWallets'][0]['address']
            main_character = int(result['data']['queryDiscordWallets'][0]['main_character'])
            equipped_hatchet = int(result['data']['queryDiscordWallets'][0]['equipped_hatchet'])

        return wallet, main_character, equipped_hatchet
    
async def update_character(address, chosen_fallen):
    update_char = """
    mutation addWings($address: String!, $chosen_fallen: Int!) {
      updateDiscordWallets(input: {filter: {address: {eq: $address}}, set: {main_character: $chosen_fallen}}) {
            numUids
        }
    }
    """
    variables = {'address': address, 'chosen_fallen': chosen_fallen}
    request = requests.post(graphql, json={'query': update_char, 'variables': variables}, headers=headersDG)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Update Query failed to run by returning code of {}. {}".format(request.status_code, update_char))
    
async def equip_main_hatchet(address, chosen_hatchet):
    update_hatchet = """
    mutation addWings($address: String!, $chosen_hatchet: Int!) {
      updateDiscordWallets(input: {filter: {address: {eq: $address}}, set: {equipped_hatchet: $chosen_hatchet}}) {
            numUids
        }
    }
    """
    variables = {'address': address, 'chosen_hatchet': chosen_hatchet}
    request = requests.post(graphql, json={'query': update_hatchet, 'variables': variables}, headers=headersDG)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Update Query failed to run by returning code of {}. {}".format(request.status_code, update_hatchet))
    
async def get_bossbattles(userid):
    bossbattle_data = []
    get_bossbattles = f"""
    query queryDiscordWallets {{
        queryDiscordWallets(filter: {{userid: {{eq: "{userid}"}}}}) {{
            address
            name
            bossbattles
            weekly_battles
        }}
    }}
    """
    variables = {'userid': userid}
    request = requests.post(graphql, json={'query': get_bossbattles, 'variables': variables}, headers=headersDG)
    if request.status_code == 200:
        result = request.json()
        if result['data']['queryDiscordWallets'] == []:
            wallet = ''
            name = ''
            bossbattles = 0
            weekly_battles = 0
            bossbattle_data.append(wallet)
            bossbattle_data.append(name)
            bossbattle_data.append(bossbattles)
            bossbattle_data.append(weekly_battles)
        else:
            wallet = result['data']['queryDiscordWallets'][0]['address']
            name = result['data']['queryDiscordWallets'][0]['name']
            bossbattles = result['data']['queryDiscordWallets'][0]['bossbattles']
            weekly_battles = result['data']['queryDiscordWallets'][0]['weekly_battles']
            bossbattle_data.append(wallet)
            bossbattle_data.append(name)
            bossbattle_data.append(bossbattles)
            bossbattle_data.append(weekly_battles)

        return bossbattle_data
    
async def update_kinsubs(address, amount):
    update_kinsubs = """
    mutation addKinsubs($address: String!, $amount: Int!) {
      updateDiscordWallets(input: {filter: {address: {eq: $address}}, set: {kinship_subs: $amount}}) {
            numUids
        }
    }
    """
    variables = {'address': address, 'amount': amount}
    request = requests.post(graphql, json={'query': update_kinsubs, 'variables': variables}, headers=headersDG)
    if request.status_code == 200:
        return request.json()
    else:
        raise Exception("Update Query failed to run by returning code of {}. {}".format(request.status_code, update_kinsubs))
    
async def get_kinship_subs(userid):
    get_kinsubs = f"""
    query queryDiscordWallets {{
        queryDiscordWallets(filter: {{userid: {{eq: "{userid}"}}}}) {{
            address
            name
            kinship_subs
        }}
    }}
    """
    variables = {'userid': userid}
    request = requests.post(graphql, json={'query': get_kinsubs, 'variables': variables}, headers=headersDG)
    if request.status_code == 200:
        result = request.json()
        if result['data']['queryDiscordWallets'] == []:
            wallet = ''
            name = ''
            kinsubs = 0
        else:
            wallet = result['data']['queryDiscordWallets'][0]['address']
            name = result['data']['queryDiscordWallets'][0]['name']
            kinsubs = result['data']['queryDiscordWallets'][0]['kinship_subs']
        wallet_kinship = [name, wallet, kinsubs]

        return wallet_kinship


async def send_assets(sender, sender_address, receiver_address, token, token_name, amount):
    decimals = algod_client.asset_info(token).get("params").get("decimals")
    note = "Fallen Order. " + sender + " sent you " + str(amount) + " $" + token_name + " via the AoA Discord."

    params = algod_client.suggested_params()
    txn = transaction.AssetTransferTxn(
        clawback_address,
        params,
        receiver_address,
        amt=amount * (10 ** decimals),
        index=token,
        revocation_target=sender_address,
        note=note
    )

    signed_txn = txn.sign(sender_key)
    tx_id = algod_client.send_transaction(signed_txn)

    return tx_id

async def clawback_character(wallet, character_id):
    note = "Fallen Order. FUSION COMPLETE! Your Fallen Order character has been sent back to the reserve wallet and your new character is waiting for you to claim! DM angel.algo to claim."

    params = algod_client.suggested_params()
    txn = transaction.AssetTransferTxn(
        fallen_order_manager,
        params,
        fallen_order_manager,
        amt=1,
        index=character_id,
        revocation_target=wallet,
        note=note
    )

    signed_txn = txn.sign(sender_key)
    tx_id = algod_client.send_transaction(signed_txn)

    return tx_id

async def send_logs(receiver_address, logs_id):
    note = "Fallen Order. Congrats! You successfully chopped some wood!"

    params = algod_client.suggested_params()
    txn = transaction.AssetTransferTxn(
        fallen_order_accessories,
        params,
        receiver_address,
        amt=1,
        index=logs_id,
        revocation_target=fallen_order_accessories,
        note=note
    )

    signed_txn = txn.sign(sender_key_accessories)
    max_attempts = 3
    attempt = 1
    while attempt <= max_attempts:
        try:
            tx_id = algod_client.send_transaction(signed_txn)
            transaction.wait_for_confirmation(algod_client, tx_id)
            break
        except Exception as e:
            print(f"Transaction failed: {str(e)}")
            attempt += 1
            if attempt > max_attempts:
                print("Edit Metadata Txn failed 3 times!")
                break

    return tx_id

async def trade_logs(sender, sender_wallet, receiver_address, logs_id, amount):
    note = "Fallen Order. " + sender + " sent you " + str(amount) + " Oak Logs via the AoA Discord."
    params = algod_client.suggested_params()
    txn = transaction.AssetTransferTxn(
        fallen_order_accessories,
        params,
        receiver_address,
        amt=amount,
        index=logs_id,
        revocation_target=sender_wallet,
        note=note
    )

    signed_txn = txn.sign(sender_key_accessories)
    max_attempts = 3
    attempt = 1
    while attempt <= max_attempts:
        try:
            tx_id = algod_client.send_transaction(signed_txn)
            break
        except Exception as e:
            print(f"Transaction failed: {str(e)}")
            attempt += 1
            if attempt > max_attempts:
                print("Trade Logs Txn failed 3 times!")
                break

    return tx_id

async def logs_payment(wallet, logs_id, amount):
    note = "Fallen Order. Congrats! You successfully purchased a Kinship Potion!"

    params = algod_client.suggested_params()
    txn = transaction.AssetTransferTxn(
        fallen_order_accessories,
        params,
        fallen_order_accessories,
        amt=amount,
        index=logs_id,
        revocation_target=wallet,
        note=note
    )

    signed_txn = txn.sign(sender_key_accessories)
    max_attempts = 3
    attempt = 1
    while attempt <= max_attempts:
        try:
            tx_id = algod_client.send_transaction(signed_txn)
            transaction.wait_for_confirmation(algod_client, tx_id)
            break
        except Exception as e:
            print(f"Transaction failed: {str(e)}")
            attempt += 1
            if attempt > max_attempts:
                print("Edit Metadata Txn failed 3 times!")
                break

    return tx_id

async def send_potion(wallet, potion_id):
    note = "Fallen Order. Congrats! You successfully purchased a Kinship Potion!"

    params = algod_client.suggested_params()
    txn = transaction.AssetTransferTxn(
        fallen_order_accessories,
        params,
        wallet,
        amt=1,
        index=potion_id,
        revocation_target=fallen_order_accessories,
        note=note
    )

    signed_txn = txn.sign(sender_key_accessories)
    max_attempts = 3
    attempt = 1
    while attempt <= max_attempts:
        try:
            tx_id = algod_client.send_transaction(signed_txn)
            transaction.wait_for_confirmation(algod_client, tx_id)
            break
        except Exception as e:
            print(f"Transaction failed: {str(e)}")
            attempt += 1
            if attempt > max_attempts:
                print("Edit Metadata Txn failed 3 times!")
                break

    return tx_id

async def freeze_asset(type, address_to_freeze, asset_to_freeze):
    if type == "freeze":
        freeze = True
    else:
        freeze = False

    params = algod_client.suggested_params()
    txn = transaction.AssetFreezeTxn(
        fallen_order_accessories,
        params,
        index=asset_to_freeze,
        target=address_to_freeze,
        new_freeze_state=freeze,
    )

    signed_txn = txn.sign(sender_key_accessories)
    max_attempts = 3
    attempt = 1
    while attempt <= max_attempts:
        try:
            tx_id = algod_client.send_transaction(signed_txn)
            transaction.wait_for_confirmation(algod_client, tx_id)
            break
        except Exception as e:
            print(f"Transaction failed: {str(e)}")
            attempt += 1
            if attempt > max_attempts:
                print("Edit Metadata Txn failed 3 times!")
                break

    return tx_id


async def edit_metadata(index, metadata):
    params = algod_client.suggested_params()
    edit_metadata_txn = transaction.AssetConfigTxn(
        sender=fallen_order_manager,
        sp=params,
        index= index,
        manager=fallen_order_manager,
        reserve=fallen_order_manager,
        freeze=fallen_order_manager,
        clawback=fallen_order_manager,
        note=metadata
    )
    signed_txn = edit_metadata_txn.sign(sender_key_fallen)
    max_attempts = 3
    attempt = 1
    while attempt <= max_attempts:
        try:
            txid = algod_client.send_transaction(signed_txn)
            break
        except Exception as e:
            print(f"Transaction failed: {str(e)}")
            attempt += 1
            if attempt > max_attempts:
                print("Edit Metadata Txn failed 3 times!")
                break
    
    return txid

async def edit_hatchet(index, metadata):
    params = algod_client.suggested_params()
    edit_metadata_txn = transaction.AssetConfigTxn(
        sender=fallen_order_accessories,
        sp=params,
        index= index,
        manager=fallen_order_accessories,
        reserve=fallen_order_accessories,
        freeze=fallen_order_accessories,
        clawback=fallen_order_accessories,
        note=metadata
    )
    signed_txn = edit_metadata_txn.sign(sender_key_accessories)
    max_attempts = 3
    attempt = 1
    while attempt <= max_attempts:
        try:
            txid = algod_client.send_transaction(signed_txn)
            transaction.wait_for_confirmation(algod_client, txid)
            break
        except Exception as e:
            print(f"Transaction failed: {str(e)}")
            attempt += 1
            if attempt > max_attempts:
                print("Edit Metadata Txn failed 3 times!")
                break
    
    return txid


async def staking_rewards(send_data):
    txids = []
    params = algod_client.suggested_params()
    max_attempts = 3

    for item in send_data:
        wallet = item[0]
        count = item[1]
        ghostcount = item[2]
        order = item[3]
        exp = item[4]
        note1 = "Fallen Order Staking. You Received " + str(order) + " $ORDER for holding " + str(count) + " Characters. Thank You for the continued support!"
        note2 = "Fallen Order Staking. You Received " + str(exp) + " $EXP for holding " + str(count) + " Characters and " + str(ghostcount) + " Ghosts. Thank You for the continued support!"
        if wallet != "AOAZMP5WTCCHOPKZZICV5KEZ7IH6BRFIDI47ONQU42QNOTTAW4ACZVXDHA":
            txn1 = transaction.AssetTransferTxn(
                clawback_address,
                params,
                wallet,
                amt=order,
                index=811718424,
                revocation_target=fallen_order_main,
                note=note1
            )
            txn2 = transaction.AssetTransferTxn(
                clawback_address,
                params,
                wallet,
                amt=exp,
                index=811721471,
                revocation_target=fallen_order_main,
                note=note2
            )

            signed_txn1 = txn1.sign(sender_key)
            signed_txn2 = txn2.sign(sender_key)
            attempt = 1
            while attempt <= max_attempts:
                try:
                    if count != 0:
                        tx_id1 = algod_client.send_transaction(signed_txn1)
                    tx_id2 = algod_client.send_transaction(signed_txn2)
                    break
                except Exception as e:
                    print(f"Transaction failed: {str(e)}")
                    attempt += 1
                    if attempt > max_attempts:
                        print("Send Staking Rewards Txn failed 3 times!")
                        break

            txids.append([tx_id1, tx_id2])


async def deathmatch_clawback(user_address):
    decimals = algod_client.asset_info(811721471).get("params").get("decimals")
    note = "Fallen Order - Death Match! You successfully sign up for 50 $EXP. Good Luck!"

    params = algod_client.suggested_params()

    txn = transaction.AssetTransferTxn(
        clawback_address,
        params,
        fallen_order_main,
        amt=50 * (10 ** decimals),
        index=811721471,
        revocation_target=user_address,
        note=note.encode()
    )

    signed_txn = txn.sign(sender_key)

    tx_id = algod_client.send_transaction(signed_txn)

    return tx_id   

async def clawback_exp(user_address, amount, type):
    decimals = algod_client.asset_info(811721471).get("params").get("decimals")
    noteLoss = "Fallen Order - House Of Hermes. You lost " + str(amount) + " $EXP. Better luck next time!"
    noteTie = "Fallen Order - House Of Hermes. You tied and won " + str(amount) + " $EXP. DEATH TO HERMES! LETS GOOOOO!!!"
    noteWin = "Fallen Order - House Of Hermes. You won " + str(amount) + " $EXP. Hermes got knocked out!"

    params = algod_client.suggested_params()

    if type == "loss":
        txn = transaction.AssetTransferTxn(
            clawback_address,
            params,
            fallen_order_main,
            amt=amount * (10 ** decimals),
            index=811721471,
            revocation_target=user_address,
            note=noteLoss.encode()
        )
    elif type == "tie":
        txn = transaction.AssetTransferTxn(
            clawback_address,
            params,
            user_address,
            amt=amount*2 * (10 ** decimals),
            index=811721471,
            revocation_target=fallen_order_main,
            note=noteTie.encode()
        )
    elif type == "win":
        txn = transaction.AssetTransferTxn(
            clawback_address,
            params,
            user_address,
            amt=amount * (10 ** decimals),
            index=811721471,
            revocation_target=fallen_order_main,
            note=noteWin.encode()
        )

    signed_txn = txn.sign(sender_key)

    tx_id = algod_client.send_transaction(signed_txn)

    return tx_id