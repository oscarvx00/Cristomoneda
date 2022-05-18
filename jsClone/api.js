var express = require('express')
var bodyParser = require('body-parser')
var cors = require('cors')
var Blockchain = require('./blockchain.js')
const uuid = require('uuid')
const router = express.Router()
const PORT = 50001
const ngrok = require('ngrok')

let blockchain = new Blockchain()

const app = express()
let nodeUrl = undefined

app.use(cors())

app.use(bodyParser.json())
app.use(bodyParser.urlencoded({ extended: true }));


app.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', '*');
    res.header('Access-Control-Allow-Headers', 'Authorization, X-API-KEY, Origin, X-Requested-With, Content-Type, Accept, Access-Control-Allow-Request-Method');
    res.header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE');
    res.header('Allow', 'GET, POST, OPTIONS, PUT, DELETE');
    next();
});

app.get('/minarBloque', (req, res) => {
    let bloqueAnterior = blockchain.bloqueAnteriorF()
    let pruebaAnterior = bloqueAnterior.pruebaTrabajo
    let pruebaTrabajo = blockchain.prueba_trabajo(pruebaAnterior)
    let hashAnterior = blockchain.hashF(bloqueAnterior)
    blockchain.anadirTransaccion(nodeUrl, "YO", 10)
    bloque = blockchain.crearBloque(pruebaTrabajo, hashAnterior)
    res.json({
        mensaje: "Nuevo bloque",
        indice: bloque.indice,
        fecha: bloque.fecha,
        pruebaTrabajo: bloque.pruebaTrabajo,
        transacciones: bloque.transacciones
    })
})


app.get('/obtenerCadena', (req, res) => {
    res.json({
        cadena: blockchain.cadena,
        longitud: blockchain.cadena.length
    })
})

app.get('/validar', (req, res) => {
    let valida = blockchain.cadenaEsValida(blockchain.cadena)
    if(valida){
        res.json({mensaje: "Todo gucci"})
    } else {
        res.statusCode = 400
        res.json({mensaje: "Cadena no valida"})
    }
})

app.post('/anadirTransaccion', (req, res) => {
    let transaccion = req.body
    if(transaccion.emisor == undefined || transaccion.receptor == undefined || transaccion.cantidad == undefined){
        res.statusCode = 400
        res.json({mensaje: "Bad body"})
    }
    let indice = blockchain.anadirTransaccion(transaccion.emisor, transaccion.receptor, transaccion.cantidad)
    res.json({
        mensaje : `Transaccion añadida al bloque ${indice}`
    })
})

app.post('/conectarNodo', (req, res) => {
    let nodos = req.body.nodos
    if(nodos == undefined || nodos.length == 0){
        res.statusCode = 400
        res.json("Nodos vacios")
    }
    nodos.forEach(el => {
        blockchain.anadirNodo(el)
    });
    res.json({
        mensaje: "Todos los nodos conectados",
        lista: Array.from(blockchain.nodos)
    })
})

app.get('/reemplazarCadena', (req, res) => {
    let cadena_cambiada = blockchain.reemplazarCadena()
    if(cadena_cambiada){
        res.json({
            mensaje: "Cadena reemplazada con éxito",
            cadena: blockchain.cadena
        })
    }
    else {
        res.json({
            mensaje: "No es necesario reemplazar la cadena",
            cadena: blockchain.cadena
        })
    }
})

app.listen(PORT)



async function run(){
    const url = await ngrok.connect(50001)
    nodeUrl = url
    console.log(url)
}

console.log(`Running in ${PORT}`)
run()