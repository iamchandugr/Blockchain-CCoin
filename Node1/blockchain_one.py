# -*- coding: utf-8 -*-
"""
Created on Tue Aug 20 21:32:38 2019

@author: Chandu
"""
import datetime
import hashlib
import json
import pickle, os, glob
from pathlib import Path
from flask import Flask, jsonify, render_template, request, redirect
class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.genesis_block()
    
    def previous_block(self):
        #print(" Chain length is %",len(self.chain))
        return self.chain[len(self.chain)-1]
    
    def mine_block(self):
        nounce = 0
        hash_value = ""
        found_golden_hash = False
        prev_block = self.previous_block()
        prev_nounce = prev_block["nounce"]
        while found_golden_hash is False:
            hash_value = hashlib.sha512(str(nounce**2 - prev_nounce**2).encode()).hexdigest()
            if hash_value[:4] == '0000':
                found_golden_hash = True
            else:
                nounce += 1
        prev_block_hash = self.hash_block(prev_block)
        self.add_block_to_chain(nounce,prev_block_hash)
        
    def hash_block(self,transaction_block):
        encoded_block = json.dumps(transaction_block, sort_keys = True).encode()
        return hashlib.sha512(encoded_block).hexdigest()
    
    def check_chain_length(self):
        return len(self.chain)
    
    def genesis_block(self):
        global blockchain
        if self.check_chain_length() == 0:
            block = {
                    "Block_number" : 0,
                    "nounce" : 0,
                     "time_stamp" : str(datetime.datetime.now()),
                     "transactions" : "Genesis Block",
                     "previous_hash" : 0
                    }
            self.chain.append(block);
            
    def add_block_to_chain(self, golden_nounce, previous_hash):
        block = {
                "Block_number" : blockchain.check_chain_length(),
                "nounce" : golden_nounce,
                "time_stamp" : str(datetime.datetime.now()),
                "transactions" : blockchain.transactions,
                "previous_hash" : previous_hash,
                }
        self.transactions = []
        self.chain.append(block);
    
    def replace_with_long_chain(self):
        global blockchain
        blockchain_local = Blockchain()
        for filename in Path('../../').glob('**/*.obj'):
            if os.path.getsize(filename) > 0:
                filename = open(filename, 'rb')
                blockchain_local = pickle.load(filename)
                filename.close()
            if blockchain.valid_chain() == "Valid chain":
                print("Valid chain so checking...")
                if blockchain_local.check_chain_length() > blockchain.check_chain_length()-1:
                    print(" length is %",blockchain_local.check_chain_length())
                    if blockchain_local.valid_chain() == "Valid chain":
                        blockchain = blockchain_local
                        file_local = open('transaction.obj', 'wb')
                        pickle.dump(blockchain, file_local)
                        file_local.close()
            else:
                blockchain = Blockchain()
    
    def valid_chain(self):
        length = 1
        chain_len = len(self.chain)
        current_block = self.chain[0]
        while(length < chain_len) :
            next_block = self.chain[length]
            current_block_hash = self.hash_block(current_block)
            if(current_block_hash != next_block["previous_hash"]) :
                return "Not matching previous hash. So Not valid chain"
            prev_nounce = current_block["nounce"]
            nounce = next_block["nounce"]
            hash_value = hashlib.sha512(str(nounce**2 - prev_nounce**2).encode()).hexdigest()
            if hash_value[:4] != '0000':
                return "Not valid chain"
            current_block = next_block
            length+=1
        return "Valid chain"
    
    def add_transactions_print(self,transaction_message):
        self.transactions.append(transaction_message)
        self.mine_block()
        self.print_chain()
        
    def print_chain(self):
        print(self.chain)
            
app = Flask(__name__, template_folder="../templates", static_folder="../static")

blockchain = Blockchain()

#@app.route('/add_block_to_chain')         


#@app.route('/valid_chain')


#@app.route('/check_chain_length')

    
#@app.route('/print_chain')
#def print_chain():
 #   print(blockchain.chain)
        
@app.route('/print', methods = ['GET','POST'])
def start():
    global blockchain
    file = open('transaction.obj', 'rb')
    trans_message = ""
    if request.method == "POST":
        if os.path.getsize('transaction.obj') > 0:
            blockchain = pickle.load(file)
        trans_message = "You gave "+request.form['amt']+" CCoin to "+request.form['to']
        blockchain.add_transactions_print(trans_message)
        file = open('transaction.obj', 'wb')
        pickle.dump(blockchain, file)
    else:
        response = {}
        blockchain.replace_with_long_chain()
        file = open('transaction.obj', 'rb')
        if os.path.getsize('transaction.obj') > 0:
            blockchain = pickle.load(file)
        for i in range(len(blockchain.chain)):
            response['Block '+str(i)] = blockchain.chain[i]
        #return """<h3>{}</h3><button onclick="location.href = 'http://localhost:5000/;" id="myButton" >Click to do Transactions</button>""".format(jsonify(response))
        return render_template('print_blocks.html', result=response, port=5001)
    #return redirect("http://localhost:5000/", code=200)
    file.close()
    return render_template('transaction_form.html', port=5001)

@app.route('/')
def start_form():
    global blockchain
    file = ""
    try:
        file = open('transaction.obj', 'rb')
        if os.path.getsize('transaction.obj') > 0:
            blockchain = pickle.load(file)
            blockchain.replace_with_long_chain()
        else:
            pickle.dump(blockchain,file)
    except:
        print("No file found. So creating one...")
        file = open('transaction.obj', 'wb+')
    file.close()
    return render_template('transaction_form.html', port=5001)
    
app.run(host='0.0.0.0', port= 5001)
#blockchain.add_block_to_chain("RAKE gave back 1560 dollars to TENNY")
#blockchain.add_block_to_chain("Checky gave back 100 dollars to dummy")
#blockchain.add_block_to_chain("Dummy gave 100 dollars to checky")
#print(blockchain.valid_chain())
#blockchain.print_chain()