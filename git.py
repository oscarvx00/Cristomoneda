import datetime
import hashlib
import json
import requests
from uuid         import uuid4
from flask        import Flask, jsonify, request
from urllib.parse import urlparse
from flask_ngrok  import run_with_ngrok

class Blockchain:
    def __init__(self):

        self.chain = [] #La cadena de bloques
        self.transactions = []  #Las transacciones ejecutada en la cadena
        self.create_block(proof = 1 , previous_hash = "genesisis")  #El primer bloque creado
        self.nodes = set() # No puede haber nodos repetidos

    def create_block(self,proof,previous_hash):

        block = {
            'index' : len(self.chain) + 1,
            'timestamp' : str(datetime.datetime.now),
            'proof' : proof,
            'previous_hash' : previous_hash,
            'transactions' : self.transactions
        }

        self.transactions = [] #Vaciamos las transacciones por que ya se incluyeron en el bloque
        #Solo se meteran las transacciones a la blockchain cuando se minen bloques
        self.chain.append(block) #Metemos el nuevo bloque a la cadena
        return block
    def get_previous_block(self):

        return self.chain[-1]
    

    def proof_of_work(self, previous_proof):     
        new_proof = 1
        check_proof = False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else: 
                new_proof += 1
        return new_proof
    
    def hash(self,block):
        encoded_block = json.dumps(block,sort_keys =True).encode()
        hash_block = hashlib.sha256(encoded_block).hexdigest()
        return hash_block
    def is_chain_valid(self,chain):

        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block["previous_hash"] != self.hash(previous_block):#Signifca que las cadena ha sido alterada
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != "0000":
                return False
            previous_block = block
            block_index += 1 
        return True
    def add_transaction(self,sender,receiver,amount):
        self.transactions.append({"sender":sender,"receiver":receiver,"amount":amount})
        previous_block = self.get_previous_block()
        return previous_block["index"] + 1 #EN que bloque sera incluida la transaccion

    def add_node(self,address):
        parsed_url =urlparse(address)
        self.nodes.add(parsed_url.netloc) #incluimos la url como nuevo nodo
    def replace_chain(self):
        #Reemplza al blockchaain por la cadena mas larga
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        print('Longitud de la propia cadena -->'+str(max_length))
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()["length"]
                print('Longitud -->'+str(length)+' Nodo -->'+str(node))
                chain = response.json()["chain"]
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        
        if longest_chain :
            self.chain = longest_chain
            return True
        return False

#SEGUNDA PARTE-----------------------------------------------------------------------------------------

app = Flask(__name__) #__name__ indica el archivo actual
run_with_ngrok(app)
#no solo en local
node_address = str(uuid4()).replace('-','') #Creamos una nueva dirreccion y eliminamos los guiones
# 4-5-6 cambio  a 456
blockchain = Blockchain()

@app.route("/mine_block", methods = ["GET"])
def mine_block():

    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender = node_address, receiver = "Ismael Ruiz Ranz", amount = 10)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message'       : '¡Enhorabuena, nuevo bloque minado!', 
              'index'         : block['index'],
              'timestamp'     : block['timestamp'],
              'proof'         : block['proof'],
              'previous_hash' : block['previous_hash'],
              'transactions'  : block['transactions']}
    return jsonify(response),200

@app.route("/get_chain", methods =["GET"])
def get_chain():
    response ={"chain":blockchain.chain,
                "length":len(blockchain.chain)
    }
    return jsonify(response),200

@app.route("/is_valid", methods =["GET"])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {"message" : "Todo Correcto"}
    else:
        response = { "message":"La cadena no es valida"}
    return jsonify(response),200

@app.route("/add_transaction", methods =["POST"])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    if not all(key in json for key in transaction_keys):
        return 'Faltan algunos elementos de la transacción', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'La transacción será añadida al bloque {index}'}
    return jsonify(response), 201

@app.route("/connect_node", methods =["POST"])
def connect_node():
    json = request.get_json()
    nodes = json.get("nodes")
    if nodes is None:
        return "No hay nodos en tu blockchain a incluir",400
    for node in nodes:
        blockchain.add_node(node)
    response = {"message":"Todos los nodos conectados","Total_Nodes":list(blockchain.nodes)}
    return jsonify(response),200

@app.route("/replace_chain", methods =["GET"])
def replace_chain():

    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {"message":"La cadena correcta ha sido actualizada" , 
        "new_chain":blockchain.chain}
    else:
        response = {"message":"Todo correcto,no hace falta actualizar" , 
        "new_chain":blockchain.chain}
    return jsonify(response),200

#app.run(host = '0.0.0.0', port = 44446)
app.run()
#http://1a20-83-54-105-62.ngrok.io-- MATI
#http://90da-83-54-105-62.ngrok.io -- ÁNGEL