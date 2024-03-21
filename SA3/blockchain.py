import hashlib
import json
from time import time
import random

def generateHash(input_string):
    hashObject = hashlib.sha256()
    hashObject.update(input_string.encode('utf-8'))
    hashValue = hashObject.hexdigest()
    return hashValue

class BlockChain():
    def __init__(self):
        self.chain = []
        self.pendingTransactions = []
        self.miners = []
        self.peerBlocks = []

    def length(self):
        return len(self.chain)
        
    def addBlock(self, currentBlock):
        if(len(self.chain) == 0):
            self.createGenesisBlock()  
        currentBlock.previousHash = self.chain[-1].currentHash        
        isBlockMined = currentBlock.mineBlock()
        if(isBlockMined):
            self.chain.append(currentBlock)
            return True
        return False       
    
    def createGenesisBlock(self):
        genesisBlock = Block(0, time(), "No Previous Hash")
        self.chain.append(genesisBlock)
    
    def printChain(self):
        for block in self.chain:
            print("Block Index", block.index)
            print("Timestamp", block.timestamp)
            print("Transactions", block.transactions)
            print( "Previous Hash",block.previousHash)
            print( "Current Hash",block.currentHash)
            print( "Is Valid Block",block.isValid)

            print("*" * 100 , "\n")

    def validateBlock(self, currentBlock):
        previousBlock = self.chain[currentBlock.index - 1]
        if(currentBlock.index != previousBlock.index + 1):
            return False
        previousBlockHash = previousBlock.calculateHash()
        if(previousBlockHash != currentBlock.previousHash):
            return False
        validationHash = currentBlock.calculateHash()
        if(validationHash[0:currentBlock.difficulty] != "0" * currentBlock.difficulty):
            return False
        return True
    
    def addToMiningPool(self, transaction):
        self.pendingTransactions.append(transaction)

    def addMiner(self, miner):
        self.miners.append(miner)

    def minePendingTransactions(self, minerAddress):
        if(len(self.peerBlocks)>0):
            return ("PeerBlocksPending", None)
        for miner in self.miners:
            if miner.address == minerAddress:
                currentBlock = miner.createBlock(len(self.chain), self.pendingTransactions)
                
                isBlockAdded = self.addBlock(currentBlock) 
                if(isBlockAdded):  
                    isValid = self.validateBlock(currentBlock)
                    currentBlock.isValid = isValid

                    self.pendingTransactions = self.pendingTransactions[1:]
                    miner.reward(currentBlock)
                    return ("Mined", currentBlock)
        return ("NotMined", None)


    def addPeerBlock(self, peerBlock):
        self.peerBlocks.append(peerBlock)
        print("Pending Peer Blocks", self.peerBlocks)

    # Define validatePeerBlocks method
    def validatePeerBlocks(self):
        # Loop over each peerBlock in peerBlocks
        for peerBlock in self.peerBlocks:
            # Check if it is 0th i.e genesis block
            if(peerBlock.index == 0 and len(self.chain) == 0):
                # Add block to chain
                self.chain.append(peerBlock)
                # continue the loop
                continue
            # Check if the block is valid and store result in isvalid variable
            isValid = self.ValidateBlock(peerBlock)
            # If isvalid then
            if(isValid):
                # Add peerBlock to chain
                self.chain.append(peerBlock)
        # Set peerBlocks to empty    
        self.peerBlocks=[]
        
class Block:
    def __init__(self, index, timestamp, previousHash):
        self.index = index
        self.transactions = []
        self.timestamp = timestamp
        self.previousHash = previousHash
        self.isValid = None
        self.difficulty = 3
        self.nonce = 0
        self.currentHash = self.calculateHash()
    
    def calculateHash(self, timestamp=None):
        if(timestamp == None):
            timestamp = self.timestamp
        blockString = str(self.index) + str(timestamp) + str(self.previousHash) + json.dumps(self.transactions, default=str) + str(self.nonce)
        return generateHash(blockString)
    
    def mineBlock(self):
        target = "0" * self.difficulty
        nonceLimit = 40000
        
        while self.currentHash[:self.difficulty] != target:
            self.nonce += 1
            self.timestamp = time()    
            self.currentHash = self.calculateHash()        
            
            if(self.nonce >= nonceLimit):
                print("All nonce exhaust")
                self.nonce = 0
        return True

    def addTransaction(self, transaction):
        if transaction:
            self.transactions.append(transaction)
            if len(self.transactions) == 3:
                return "Ready"
            return "Add more transactions"


class Miner():
    def __init__(self, address):
        self.address= address
        self.walletBalance = 0    
   
    def createBlock(self, index, transactions):
        if(len(transactions) >=1 ):
            transactions = transactions[:1]

            if index==0:
                index = 1
            blockData = {
                    'index': index,
                    'timestamp': time(),
                    'previousHash': "No Previous Hash.",
            }    

            currentBlock = Block(
                                blockData["index"], 
                                blockData["timestamp"], 
                                blockData["previousHash"])
             
            currentBlock.transactions = transactions
            return currentBlock
        return False
    
    def reward(self, currentBlock):
        blockReward = 5 
        transactionFee = 0
        for transaction in currentBlock.transactions:
            transactionFee += transaction['transactionFeeEther']      
        minerReward = blockReward + transactionFee
        self.walletBalance += minerReward

class Node():
    def __init__(self, id):
        self.id = id
        self.blockchain = BlockChain()
        self.currentBlock = None
        self.failedBlocks = []


