from flask_ngrok import run_with_ngrok
from flask import Flask,jsonify,request
from blockchain import Blockchain
from uuid import uuid4

app = Flask(__name__) #__name__ indica el archivo actual
#no solo en local
#run_with_ngrok(app)#Mandamos nuestra a pp a al red
node_address = str(uuid4()).replace('-','') #Creamos una nueva dirreccion y eliminamos los guiones
# 4-5-6 cambio a 456
blockchain = Blockchain()


@app.route("/mine_block",methods = ["GET"])
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transaction(sender=node_address,receiver="Mati", amount=1)
    block = blockchain.create_block(proof,previous_hash)
    response={
        "message" : "Nuevo bloke activo",
        "index" : block["index"],
        "timestamp" : block["timestamp"],
        "proof" : block["proof"],
        "transaction" : block["transactions"]
    }
    return jsonify(response),200
#python3 .\api.py
#Obtenemos la cadena y su longitud
@app.route("/get_chain", methods =["GET"])
def get_chain():
    response ={ "chain":blockchain.chain,
                "length":len(blockchain.chain)
    }
    return jsonify(response),200

#Comprobamos que la cadena sea valida
@app.route("/is_valid", methods =["GET"])
def is_valid():
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    if is_valid:
        response = {"message" : "Todo Correcto"}
    else:
        response = { "message":"La cadena no es valida"}
        return jsonify(response),200
    #Funcion para mandar una transacción

@app.route("/add_transaction", methods =["POST"])
def add_transaction():
    json = request.get_json()
    transactions_keys = ["sender", "receiver", "amount"]
    if not all(key in json for key in transactions_keys):
        return "No han llegado todos los elementos",400
    index = blockchain.add_transaction(json["sender"],json["receiver"],json["amount"])
    response = {"message": f'La transaccion sera incluida en elbloque{index}'}
    return jsonify(response),201




#Funcion para incluir nodo
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
#Funcion para actualizar a la cadena mas larga
@app.route("/replace_chain", methods =["GET"])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced:
        response = {"message":"La cadena correcta ha sido actualizada" ,"new_chain":blockchain.chain}
    else:
        response = {"message":"Todo correcto,no hace falta actualizar" ,"new_chain":blockchain.chain}
    return jsonify(response),200


app.run(host='0.0.0.0',port=44446)