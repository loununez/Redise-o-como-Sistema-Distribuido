import socket
import threading
import json
import time
import hashlib
import pika

class TaskServer:
    def __init__(self, host='localhost', port=8888):
        # Dirección y puerto del servidor
        self.host = host
        self.port = port
        # Guarda las tareas y sus resultados
        self.tasks = {}
        # Conexión con RabbitMQ
        self.setup_rabbitmq()
        print("Servidor iniciado")
        
    def setup_rabbitmq(self):
        try:
            # Conexión con RabbitMQ
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost')
            )
            self.channel = self.connection.channel()
            
            # Crea las colas necesarias
            self.channel.queue_declare(queue='task_queue', durable=False)
            self.channel.queue_declare(queue='result_queue', durable=False)
            
            # Se ejecuta cuando llega un resultado
            def result_callback(ch, method, properties, body):
                try:
                    result = json.loads(body.decode())
                    task_id = result['task_id']
                    self.tasks[task_id] = result
                    print(f"Resultado recibido: {task_id}")
                except Exception as e:
                    print(f"Error al recibir resultado: {e}")
            
            # Escucha la cola de resultados
            self.channel.basic_consume(
                queue='result_queue',
                on_message_callback=result_callback,
                auto_ack=True
            )
            
            # Hilo para recibir mensajes de RabbitMQ sin bloquear el servidor
            threading.Thread(target=self.channel.start_consuming, daemon=True).start()
            print("Conectado a RabbitMQ")
            
        except Exception as e:
            print(f"RabbitMQ no disponible: {e}")
            self.rabbitmq = False

    def handle_client(self, client_socket, address):
        # Atiende la conexión de un cliente
        print(f"Cliente conectado: {address}")
        
        try:
            # Recibe el mensaje del cliente
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                return
                
            message = json.loads(data)
            # Procesa el mensaje y arma una respuesta
            response = self.process_message(message)
            client_socket.send(json.dumps(response).encode('utf-8'))
            
        except Exception as e:
            print(f"Error al procesar cliente: {e}")
            error_msg = {"status": "error", "message": str(e)}
            client_socket.send(json.dumps(error_msg).encode('utf-8'))
        finally:
            client_socket.close()

    def process_message(self, message):
        # Decide qué hacer según el tipo de mensaje
        msg_type = message.get('type')
        
        if msg_type == 'task':
            return self.create_task(message)
        elif msg_type == 'result':
            return self.get_result(message)
        elif msg_type == 'test':
            return {"status": "success", "message": "Servidor activo"}
        else:
            return {"status": "error", "message": "Tipo de mensaje desconocido"}

    def create_task(self, message):
        # Crea una nueva tarea y la envía al worker
        task_type = message.get('task_type', 'process')
        data = message.get('data', {})
        
        # Genera un ID único
        task_id = hashlib.md5(f"{time.time()}".encode()).hexdigest()[:8]
        
        # Arma el mensaje que se manda al worker
        task_msg = {
            'task_id': task_id,
            'task_type': task_type,
            'data': data
        }
        
        try:
            # Envía la tarea a la cola de RabbitMQ
            self.channel.basic_publish(
                exchange='',
                routing_key='task_queue',
                body=json.dumps(task_msg)
            )
            
            self.tasks[task_id] = {'status': 'processing'}
            print(f"Tarea enviada: {task_id}")
            
            return {
                "status": "success", 
                "task_id": task_id, 
                "message": "Tarea en proceso"
            }
        except Exception as e:
            return {"status": "error", "message": f"Error al enviar tarea: {str(e)}"}

    def get_result(self, message):
        # Devuelve el resultado de una tarea si está disponible
        task_id = message.get('task_id')
        result = self.tasks.get(task_id, {'status': 'no_encontrado'})
        return result

    def start(self):
        # Inicia el servidor principal
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        
        print(f"Escuchando en {self.host}:{self.port}")
        
        try:
            # Acepta varios clientes al mismo tiempo
            while True:
                client_socket, address = server.accept()
                thread = threading.Thread(
                    target=self.handle_client, 
                    args=(client_socket, address)
                )
                thread.start()
        except KeyboardInterrupt:
            print("Servidor detenido")
        finally:
            server.close()

if __name__ == "__main__":
    TaskServer().start()
