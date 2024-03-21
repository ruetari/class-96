from flask import Flask, render_template, request
import os
from time import time
from blockchain import BlockChain, Miner, Node
from conversion import getGasPrices

STATIC_DIR = os.path.abspath('static')

app = Flask(__name__, static_folder=STATIC_DIR)
app.use_static_for_root = True

allNodes = {}

@app.route("/", methods= ["GET", "POST"])
def home():
    global blockData, currentBlock, chain, failedBlocks

    global allNodes
    nodeId =request.args.get("node")

    if(nodeId == None or nodeId == ""):
        return render_template('badRequest.html')
    
    if(nodeId not in allNodes):
        node = Node(nodeId)
        miner1 = Miner('Miner 1')
        miner2 = Miner('Miner 2')
        miner3 = Miner('Miner 3')

        node.blockchain.addMiner(miner1)
        node.blockchain.addMiner(miner2)
        node.blockchain.addMiner(miner3)
        
        allNodes[nodeId] = node
    
    currentNode = allNodes[nodeId]
     
    allPrices = getGasPrices()
    
    chain = currentNode.blockchain
    currentBlock = currentNode.currentBlock
    failedBlocks = currentNode.failedBlocks

    if request.method == "GET":
        return render_template('index.html', allPrices = allPrices, nodeId = nodeId)
    else:
        sender = request.form.get("sender")
        receiver = request.form.get("receiver")
        artId = request.form.get("artId")
        amount = request.form.get("amount")
        mode = request.form.get("mode")

        gasPrices, gweiPrices, etherPrices, dollarPrices = allPrices
        
        gasPriceGwei = gweiPrices[mode]
        gasPriceEther = etherPrices[mode]
        transactionFeeEther = etherPrices[mode] * 21000
        transactionFeeDollar = dollarPrices[mode] * 21000
        
        transaction = { 
                "sender": sender, 
                "receiver": receiver, 
                "amount": amount,
                "artId": artId,            
                "gasPriceGwei" : gasPriceGwei,
                "gasPriceEther" : gasPriceEther, 
                "transactionFeeEther" : transactionFeeEther,
                "transactionFeeDollar" : transactionFeeDollar
            }  

        chain.addToMiningPool(transaction)
    
    return render_template('index.html', blockChain = chain, allPrices = allPrices, nodeId = nodeId)


@app.route("/blockchain", methods= ["GET", "POST"])
def show():
    global chain, currentBlock, failedBlocks, allNodes

    nodeId =request.args.get("node")
    if(nodeId == None or nodeId == ""):
            return render_template('badRequest.html')
        
    if(nodeId not in allNodes):
            return render_template('notExits.html')
            
    currentNode = allNodes[nodeId]
    chain =currentNode.blockchain

    currentBlockLength  = 0
    if currentNode.currentBlock:
            currentBlockLength = len(currentNode.currentBlock.transactions)
    
    # Check if post request i.e synchronize button is pressed
    if(request.method == "POST"):
        # Call validatePeerBlocks() method
        currentNode.blockchain.validatePeerBlocks()
    

    return render_template('blockchain.html', blockChain = chain.chain, currentBlockLength = currentBlockLength, failedBlocks= failedBlocks, nodeId = nodeId)
    

@app.route("/miningPool", methods= ["GET", "POST"])
def miningPool():
    global chain, allNodes
    nodeId =request.args.get("node")
    if(nodeId == None or nodeId == ""):
            return render_template('badRequest.html')
        
    if(nodeId not in allNodes):
            return render_template('notExits.html')
            
    currentNode = allNodes[nodeId]
    chain =currentNode.blockchain
    
    if request.method == "POST":
        minerAddress = request.form.get("miner")

        status = False
        status, minedBlock = chain.minePendingTransactions(minerAddress)
        
        if(status== "Mined"):
            for peerNode in allNodes:  
                if(peerNode != nodeId):
                    if(minedBlock.index == 1):
                        allNodes[peerNode].blockchain.addPeerBlock(currentNode.blockchain.chain[0])
                    allNodes[peerNode].blockchain.addPeerBlock(minedBlock)
        return render_template('miningPool.html', pendingTransactions = chain.pendingTransactions, miners = chain.miners, nodeId = nodeId, status = status)
    
    return render_template('miningPool.html', pendingTransactions = chain.pendingTransactions, miners = chain.miners, nodeId = nodeId)
    
if __name__ == '__main__':
    app.run(debug = True, port=4001)