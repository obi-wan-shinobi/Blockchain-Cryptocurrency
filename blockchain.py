from time import time, sleep
from datetime import datetime
from Crypto.PublicKey import RSA
from Crypto.Signature import *
import json
import hashlib

class Blockchain(object):
    def __init__(self):
        self.chain = [self.addGenesisBlock()]
        self.pendingTransactions = []
        self.difficulty = 7
        self.minerRewards = 50
        self.blockSize = 10

    def addTransaction(self, sender, receiver, amt, keyString, senderKey):
        keyByte = keyString.encode("ASCII")
        senderKeyByte = senderKey.encode("ASCII")

        key = RSA.import_key(keyByte)
        senderKey = RSA.import_key(senderKeyByte)

        if(not sender or not receiver or not amt):
            print("transaction error 1")
            return False

        transaction = Transaction(sender, receiver, amt)

        transaction.signTransaction(key, senderKey)

        if(not transaction.isValidTransaction()):
            print("transaction error 2")
            return False
        self.pendingTransactions.append(transaction)
        return (len(self.chain) + 1)

    def generateKeys(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        file_out = open("private.pem", "wb")
        file_out.write(private_key)

        public_key = key.publickey().export_key()
        file_out = open("receiver.pem", "wb")
        file_out.write(public_key)

        return(key.publickey().export_key().decode('ASCII'))

    def minePendingTransactions(self, miner):
        lenPT = len(self.pendingTransactions)
        # if(lenPT <= 1):
        # 	print("Not enough transactions to mine! (Must be > 1)")
        # 	return False;
        # else:
        for i in range(0, lenPT, self.blockSize):
        	end = i + self.blockSize
        	if i >= lenPT:
        		end = lenPT

        	transactionSlice = self.pendingTransactions[i:end]

        	newBlock = Block(transactionSlice, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), len(self.chain))
        	#print(type(self.getLastBlock()));

        	hashVal = self.getLastBlock().hash
        	newBlock.prev = hashVal
        	newBlock.mineBlock(self.difficulty)
        	self.chain.append(newBlock)
        print("Mining Transactions Success!")

        payMiner = Transaction("Miner Rewards", miner, self.minerRewards)
        self.pendingTransactions = [payMiner]
        return True

    def getLastBlock(self):
        return self.chain[-1]

    def addBlock(self, block):
        if(len(self.chain) > 0):
            block.prev = self.getLastBlock().hash
        else:
            block.prev = "none"
        self.chain.append(block)

    def addGenesisBlock(self):
        tArr = []
        #tArr.append(Transaction("me", "you", 10))
        genesis = Block(tArr, time(), 0)
        genesis.prev = "None"
        return genesis

    def chainJSONencode(self):
        blockArrJSON = []
        for block in self.chain:
            blockJSON = {}
            blockJSON['hash'] = block.hash
            blockJSON['index'] = block.index
            blockJSON['prev'] = block.prev
            blockJSON['time'] = block.time
            blockJSON['nonse'] = block.nonse

            transactionsJSON = []
            tJSON = {};
            for transaction in block.transactions:
                tJSON['time'] = transaction.time
                tJSON['sender'] = transaction.sender
                tJSON['receiver'] = transaction.receiver
                tJSON['amt'] = transaction.amt
                tJSON['hash'] = transaction.hash
                transactionsJSON.append(tJSON)

            blockJSON['transactions'] = transactionsJSON

            blockArrJSON.append(blockJSON)

        return blockArrJSON;

class Block(object):
    def __init__(self, transactions, time, index):
        self.index = index  #Block number
        self.time = time
        self.nonse = 0
        self.transactions = transactions         #Transaction data
        self.prev = ''     #Hash of previous block
        self.hash = self.calculateHash()    #Hash of block

    def mineBlock(self, difficulty):
        arr = []
        for i in range(0, difficulty):
            arr.append(i)

        #compute until the beginning of the hash = 0123...difficulty
        arrStr = map(str, arr)
        hashPuzzle = ''.join(arrStr)
        #print(len(hashPuzzle))
        while(self.hash[0:difficulty] != hashPuzzle):
            self.nonse += 1
            self.hash = self.calculateHash()
            print(f'Nonse: {self.nonse} Hash Attempt: {self.hash} Hash we want: {hashPuzzle}...')
        print(f'Block Mined! Nonse to solve Proof of Work: {self.nonse}')
        return True

    def calculateHash(self):
        hashTransaction = ""
        for transaction in self.transactions:
            hashTransaction +=transaction.hash

        hashString = str(self.time) + hashTransaction + self.prev + str(self.nonse)
        hashEncoded = json.dumps(hashString, sort_keys=True).encode()

        return hashlib.sha256(hashEncoded).hexdigest()      #SHA256 hash encoding

class Transaction(object):
    def __init__(self, sender, receiver, amt):
        self.sender = sender
        self.receiver = receiver
        self.amt = amt
        self.time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        self.hash = self.calculateHash()

    def signTransaction(self, key, senderKey):
        if(self.hash != self.calculateHash()):
            print("transaction tampered error")
            return False
        if(str(key.publickey().export_key()) != str(senderKey.publickey().export_key())):
            print("Transaction attempt to be signed from another wallet")
            return False
        pkcs1_15.new(key)

        self.signature = "made"
        print("Made Signature!")
        return True

    def calculateHash(self):
        hashString = self.sender + self.receiver + str(self.amt) + str(self.time)
        hashEncoded = json.dumps(hashString, sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()

    def isValidTransaction(self):
        if(self.hash != self.calculateHash()):
            return False
        if(self.sender == self.receiver):
            return False
        if(self.sender == "Miner Rewards"):
            return True
        if(not self.signature or len(self.signature) == 0):
            print("No Signature!")
            return False
        return True
