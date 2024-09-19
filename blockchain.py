import hashlib
import json
import os
import base64
class Blockchain:
    def __init__(self, username):
        self.username = username
        self.chain = []
        self.blockchain_filename = f"{self.username}_blockchain.json"
        self.load_blockchain()

    def load_blockchain(self):
        if os.path.exists(self.blockchain_filename):
            with open(self.blockchain_filename, 'r') as file:
                data = json.load(file)
                self.chain = data['chain']

    def save_blockchain(self):
        data = {'chain': self.chain}
        with open(self.blockchain_filename, 'w') as file:
            json.dump(data, file)

    def add_file(self, file_info):
        self.chain.append(file_info)
        self.save_blockchain()

    def get_files(self):
        return self.chain

    def get_file_data(self, filename):
        for file_info in self.chain:
            if file_info['name'] == filename:
                return file_info.get('data', None)
        return None

    def calculate_hash(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block.encode()).hexdigest()
    

    def get_file_type(self, file_name):
        return os.path.splitext(file_name)[1]

    def get_num_characters(self, file_data):
        try:
            return len(file_data.decode('utf-8'))
        except UnicodeDecodeError:
            return 0
        
    def add_file_with_contract(self, file_info):
        # Define the smart contract conditions
        file_name = file_info.get('name')
        file_data = file_info.get('data')

        # Condition 1: File must be a .txt file
        if self.get_file_type(file_name) != '.py':
            raise ValueError("File must be a .py file.")


        # If conditions are met, add the file to the blockchain
        self.add_file(file_info)




