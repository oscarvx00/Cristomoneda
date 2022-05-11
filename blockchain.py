import datetime
import hashlib
import json
import requests
from uuid import uuid4
from flask import Flask,jsonify,request
from urllib.parse import urlparse
from flask_ngrok import run_with_ngrok

class Blockchain:

	def __init__(self):
		self.chain = [] #La cadena de bloques
		self.transactions = [] #Las transacciones ejecutada en la cadena
		self.create_block(proof = 1 , previous_hash = "genesisis")
		#El primer bloque creado
		self.nodes = set() # Set no permite nodos repetidos

	def create_block(self,proof,previous_hash):

		block = {
			'index' : len(self.chain) + 1,
			'timestamp' : str(datetime.datetime.now),
			'proof' : proof,
			'previous_hash' : previous_hash,
			'transactions' : self.transactions
		}

		self.transactions = []
		self.chain.append(block)
		return block

	def get_previous_block(self):
		
		return self.chain[-1]


	def proof_of_work(self,previous_proof):
		#Utilizamos este algorortimo para confirmar el minado de los bloques
		new_proof = 1
		check_proof = False
		while check_proof is False:
			hash_operation = hashlib.sha256(str(new_proof**2 -previous_proof**2).encode()).hexdigest()
		if hash_operation[:4] == "0000":
				check_proof = True
		else:
			new_proof =+ 1
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
			if block["previous_hash"] != self.hash(previous_block):
				#Significa que las cadena ha sido alterada
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
		return previous_block["index"] + 1 #En que bloque sera incluida la transaccion

	def add_node(self,address):
		parsed_url =urlparse(address)
		self.nodes.add(parsed_url.netloc) #incluimos la url como nuevo nodo

	def replace_chain(self):
		#Reemplza al blockchain por la cadena mas larga
		network = self.nodes
		longest_chain = None
		max_length = len(self.chain)
		for node in network:
			response = requests.get(f'http://{node}/get_chain')
			if response.status_code == 200:#200 indica que es correcto
				length = response.json()["length"]
				chain = response.json()["chain"]
				#Si el tamaño de la cadena es mayor y es valida
				if length > max_length and self.is_chain_valid(chain):
					max_length = length
					longest_chain = chain
		if longest_chain :
			self.chain = longest_chain
			return True
		return False
