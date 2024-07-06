import hashlib
import datetime 
import hmac
from hmac import compare_digest
import secrets

SECRET_KEY = b'SuperSecretKey'
pending_transactions=[]
challenge_bits = {}


class Donors:
    def __init__(self, id, name):
        self.donor_id = id
        self.name=name
        self.donations=[]
        
    def viewUser(self):

        if self.donations:
            print(f"Transactions for {self.name}:")
            for idx, donation in enumerate(self.donations, start=1):
                print(f"Transaction {idx}:")
                print("  Foundation ID:", donation.foundation_id)
                print("  Foundation Name: ", CharitableFoundations[donation.foundation_id].name)
                print("  Amount in $:", donation.amount)
                print("  Transaction Time:", donation.transaction_time)
                print("  Signature:", donation.signature)
                print()
        else:
            print("No transactions found for this foundation.")

class CharitableFoundation:
    def __init__(self, id, name):
        self.foundation_id = id
        self.donations = []
        self.name = name

    def get_transactions_details(self):

        if self.donations:
            print(f"Transactions for {self.name}:")
            for idx, donation in enumerate(self.donations, start=1):
                print(f"Transaction {idx}:")
                print("  Donor ID:", donation.donor_id)
                print("  donor Name: ", UserList[donation.donor_id-1].name)
                print("  Amount in $:", donation.amount)
                print("  Transaction Time:", donation.transaction_time)
                print("  Signature:", donation.signature)
                print()
        else:
            print("No transactions found for this foundation.")

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4 

    def create_genesis_block(self):
        return Block("0" * 64, [], datetime.datetime.now())

    def add_block(self, new_block):
        new_block.previous_hash = self.chain[-1].hash
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)

class Transactions:
    def __init__(self, foundation_id, donor_id, amount, transaction_time):
        self.foundation_id = foundation_id
        self.donor_id = donor_id
        self.amount = amount
        self.transaction_time = transaction_time
        self.signature = self.generate_signature()

    def generate_challenge(self):
        challenge = secrets.randbits(1)
        challenge_bits[self.signature] = challenge 
        return challenge

    def verifyTransaction(self, response):
        challenge = challenge_bits.get(self.signature)
        if challenge is None:
            return False 
        expected_response = str(challenge)
        return response == expected_response
    
    def generate_signature(self):
        data = f"{self.foundation_id},{self.donor_id},{self.amount},{self.transaction_time}"
        return hmac.new(SECRET_KEY, msg=data.encode(), digestmod=hashlib.sha256).hexdigest()
    
    def get_transaction_data(self):
        return f"{self.foundation_id},{self.donor_id},{self.amount},{self.transaction_time},{self.signature}"

class Block:
    def __init__(self, previous_hash, transactions, timestamp):
        self.timestamp = timestamp
        self.nonce = 0
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.merkle_root = self.calculate_merkle_root()
        self.hash = self.generate_hash()
        
    def calculate_merkle_root(self):
        merkle_tree = MerkleTree(self.transactions)
        return merkle_tree.get_merkle_root()

    def generate_hash(self): 
        sha = hashlib.sha256()
        sha.update(str(self.previous_hash).encode() + str(self.transactions).encode() + str(self.nonce).encode() + str(self.timestamp).encode())
        return sha.hexdigest()

    def mine_block(self, difficulty):
        while not self.hash.startswith('0' * difficulty):
            self.nonce += 1
            self.hash = self.generate_hash()

class MerkleTree:
    def __init__(self, array):
        self.array = array
        self.tree = self.build_tree()

    def build_tree(self):
        if not self.array:
            return []

        leaf_nodes = []
        for item in self.array:
            leaf_nodes.append(hashlib.sha256(item.get_transaction_data().encode()).hexdigest())

        tree = [leaf_nodes]

        while len(tree[0]) > 1:
            level = []

            for i in range(0, len(tree[0]), 2):
                left = tree[0][i]
                right = tree[0][i + 1] if i + 1 < len(tree[0]) else left 

                combined_hash = hashlib.sha256((left + right).encode()).hexdigest()
                level.append(combined_hash)

            tree.insert(0, level)

        return tree

    def get_merkle_root(self):
        if len(self.tree) > 0:
            tree = self.tree
            return tree[0][0]
        else:
            return None

UserList = []
Pending_transactions_list = []
BlockChain = Blockchain() 
CharitableFoundations = {}

def print_blockchain():
    print("Blockchain:")
    for idx, block in enumerate(BlockChain.chain):
        print(f"Block {idx}:")
        print("  Timestamp:", block.timestamp)
        print("  Previous Hash:", block.previous_hash)
        print("  Hash:", block.hash)
        print("  Merkle Tree Root: ", block.merkle_root)
        print("  Transactions:")
        for transaction in block.transactions:
            print("    Foundation ID:", transaction.foundation_id)
            print("    Donor ID:", transaction.donor_id)
            print("    Amount in $:", transaction.amount)
            print("    Transaction Time:", transaction.transaction_time)
            print("    Signature:", transaction.signature)
        print()

def createFoundation(id, name):
    foundation = CharitableFoundation(id, name)
    CharitableFoundations[id] = foundation
    print(f"Charitable foundation registered successfully. Please use the charity id {id} to make donations")
    return foundation

def createDonor(id, name):
    donor = Donors(id, name)
    UserList.append(donor)
    print(f"Donor registered successfully. Please remember the donorId {id} to make further donations")
    return donor

def donate(donor_id, foundation_id, amount):
    if foundation_id not in CharitableFoundations:
        print("Charitable foundation not found.")
        return
    transaction = Transactions(foundation_id, donor_id, amount, datetime.datetime.now())
    
    challenge = transaction.generate_challenge()
    print(f"Expected challenge Response: {challenge}")
    

    response = input("Enter response to verify transaction: ")
    if transaction.verifyTransaction(response):
        CharitableFoundations[foundation_id].donations.append(transaction)
        UserList[donor_id - 1].donations.append(transaction)
        pending_transactions.append(transaction)
        print("Transaction verified and added to the blockchain.")
        print("Donation added to the foundation.")
        if len(pending_transactions) > 2:
            createBlock(pending_transactions)
            pending_transactions.clear()
    else:
        print("Transaction verification failed. Transaction not added to the blockchain.")


def createBlock(verified_transactions):
    transactions=[]
    for t in verified_transactions:
        transactions.append(t)
                
    if len(verified_transactions) > 0:
        block = Block(BlockChain.chain[-1].hash, transactions, datetime.datetime.now())
        BlockChain.add_block(block)
        print("Donations added to the blockchain.")


def main():

    print("****Welcome to this Charity Donation Management System")
    while True:
        print("1: Register new Charity")
        print("2: Register new donor ")
        print("3: Donate to a charity")
        print("4: Get Charity's Donation History")
        print("5: Get donor's Donation History")
        print("6: Print Blockchain")
        print("7: Exit")

        action = input()
        if action == '1':
            name=input("Enter Charity name: ")
            createFoundation(len(CharitableFoundations)+1, name)
        elif action=='2':
            name=input("Enter donor Name: ")
            createDonor(len(UserList)+1, name)
        elif action=='3':
            id=int(input("Enter donor Id: "))
            amount=int( input("Enter Amount to be donated (in $): "))
            fid=int(input("Enter Charity Id: "))
            donate(id, fid, amount)
        elif action=='4':
            fid=int(input("Enter Charity Id: "))
            CharitableFoundations[fid].get_transactions_details()
        elif action=='5':
            fid=int(input("Enter donor Id: "))
            UserList[fid-1].viewUser()
        elif action == '6':
            print_blockchain()
        elif action == '7':
            break
        else:
            print("Invalid Entry")






if __name__ == "__main__":
    main()
