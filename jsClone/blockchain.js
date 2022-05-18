const axios = require('axios');


var sha256 = require('sha256')
module.exports = class Blockchain{
    
    constructor(){
        //this.hash = sha256.create()
        this.cadena = []
        this.transacciones = []
        this.crearBloque(1,"Genesis")
        this.nodos = new Set()
    } 

    crearBloque(pruebaTrabajo, hashAnterior){
        let bloque = {
            'indice' : this.cadena.length + 1,
            'fecha' : new Date().getTime(),
            'pruebaTrabajo' : pruebaTrabajo,
            'hashAnterior' : hashAnterior,
            'transacciones' : this.transacciones
        }
        this.transacciones= []
        this.cadena.push(bloque)
        return bloque
    }
    bloqueAnteriorF(){
        return this.cadena[this.cadena.length-1]
    }
    prueba_trabajo(pruebaAnterior){
        let nuevaPrueba=1
        let checkPrueba = false
        while(!checkPrueba){
            //this.hash=sha256.create()
            let hashUpdate = sha256((Math.pow(nuevaPrueba,2)-Math.pow(pruebaAnterior,2)).toString())
            console.log(`Prueba: ${nuevaPrueba} hashUpdate ${hashUpdate}`)
            let operacionHash = hashUpdate
            if(operacionHash.substring(0,2) == "00"){
                checkPrueba=true
            }
            else{
                nuevaPrueba++
            }
        }
        return nuevaPrueba
    }

    hashF(bloque){
        console.log(`Bloque --> ${JSON.stringify(bloque)}`)
        let hash_block = sha256(JSON.stringify(bloque))
        return hash_block
    }

    cadenaEsValida(){
        let bloqueAnterior = this.cadena[0]
        let indice_bloque = 1
        while(indice_bloque < this.cadena.length){
            let bloque = this.cadena[indice_bloque]
            //Check cadena modificada
            console.log(`Hash anterior --> ${bloque.hashAnterior}`)
            if(bloque.hashAnterior != this.hashF(bloqueAnterior)){
                console.log('hash anterior es distinto a la funcion hashF')
                return false
            }
            let pruebaAnterior = bloqueAnterior.pruebaTrabajo
            let pruebaActual = bloque.pruebaTrabajo
            let operacionHash = sha256((Math.pow(pruebaActual,2)-Math.pow(pruebaAnterior,2)).toString())
            if(operacionHash.substring(0,2) != "00"){
                console.log('hash no contiene substring 00')
                return false
            }
            bloqueAnterior = bloque
            indice_bloque=indice_bloque+1
        }
        return true
    }

    anadirTransaccion(emisor, receptor, moneymoney){
        this.transacciones.push({'emisor': emisor, 'receptor': receptor, 'cantidad': moneymoney})
        let bloqueAnterior = this.bloqueAnteriorF()
        return bloqueAnterior.indice+1
    }
    
    
    anadirNodo(direccion){
        this.nodos.add(direccion)
    }

    async reemplazarCadena(){
        let red = this.nodos
        let cadenaMasLarga = undefined
        let longiMax = this.cadena.length
        for(let nodo of red){
            const response = await axios.get(`${nodo}/obtenerCadena`) // formatear
            let tamanio = response.data.longitud // Comprobar
            console.log(`Tamaño cadena: ${tamanio}`)
            
            let cadena = response.data.cadena
            console.log('Cadena mas larga -- '+longiMax)
            console.log(this.cadenaEsValida(cadena)) 
            if(tamanio > longiMax && this.cadenaEsValida(cadena)){
                longiMax = tamanio
                cadenaMasLarga=cadena
            }
        }
           
        if(cadenaMasLarga != undefined){
            this.cadena = cadenaMasLarga
            return true
        }
        return false
    }
}
