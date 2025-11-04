import socket
import json
import time

class TaskClient:
    def __init__(self, host='localhost', port=8888):
        # Dirección y puerto del servidor
        self.host = host
        self.port = port
    
    def send_message(self, message):
        # Envía un mensaje al servidor y recibe la respuesta
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.port))
            
            sock.send(json.dumps(message).encode('utf-8'))
            response = sock.recv(4096).decode('utf-8')
            sock.close()
            
            return json.loads(response)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def enviar_tarea(self, tipo, datos):
        # Envía una tarea nueva al servidor
        mensaje = {
            "type": "task",
            "task_type": tipo,
            "data": datos
        }
        return self.send_message(mensaje)
    
    def obtener_resultado(self, task_id):
        # Consulta el resultado de una tarea
        mensaje = {
            "type": "result", 
            "task_id": task_id
        }
        return self.send_message(mensaje)
    
    def esperar_resultado(self, task_id, timeout=30):
        # Espera la respuesta de una tarea por un tiempo determinado
        print(f"Esperando resultado para {task_id}...")
        
        inicio = time.time()
        while time.time() - inicio < timeout:
            resultado = self.obtener_resultado(task_id)
            
            if resultado.get('status') == 'completado':
                print("Tarea completada!")
                print(f"Resultado: {json.dumps(resultado, indent=2)}")
                return resultado
            elif resultado.get('status') == 'processing':
                print("Procesando...")
                time.sleep(2)
            else:
                print(f"Estado: {resultado}")
                time.sleep(2)
        
        print("Tiempo agotado.")
        return None

def main():
    # Menú principal del cliente
    cliente = TaskClient()
    
    while True:
        print("\nSISTEMA DISTRIBUIDO DE TAREAS")
        print("1. Procesar texto")
        print("2. Analizar números") 
        print("3. Tarea simple")
        print("4. Salir")
        
        opcion = input("\nElige una opción (1-4): ").strip()
        
        if opcion == '1':
            texto = input("Texto a procesar: ")
            respuesta = cliente.enviar_tarea('text_processing', {'text': texto})
            
        elif opcion == '2':
            numeros = input("Números separados por coma: ")
            lista_numeros = [int(x.strip()) for x in numeros.split(',')]
            respuesta = cliente.enviar_tarea('data_analysis', {'numbers': lista_numeros})
            
        elif opcion == '3':
            mensaje = input("Mensaje para tarea simple: ")
            respuesta = cliente.enviar_tarea('simple', {'message': mensaje})
            
        elif opcion == '4':
            print("Cerrando cliente...")
            break
        else:
            print("Opción no válida.")
            continue
        
        # Muestra la respuesta del servidor
        if respuesta.get('status') == 'success':
            task_id = respuesta.get('task_id')
            print(f"Tarea creada con ID: {task_id}")
            
            esperar = input("¿Esperar resultado? (s/n): ").lower()
            if esperar == 's':
                cliente.esperar_resultado(task_id)
        else:
            print(f"Error: {respuesta.get('message')}")

if __name__ == "__main__":
    main()
