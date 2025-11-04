import pika
import json
import time
import random

class TaskWorker:
    def __init__(self, worker_id):
        # Nombre o identificador del worker
        self.worker_id = worker_id
        # Conecta con RabbitMQ
        self.setup_rabbitmq()
        print(f"Worker {worker_id} listo")
    
    def setup_rabbitmq(self):
        try:
            # Conexión con el servidor RabbitMQ
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost')
            )
            self.channel = self.connection.channel()
            
            # Crea las colas necesarias
            self.channel.queue_declare(queue='task_queue', durable=False)
            self.channel.queue_declare(queue='result_queue', durable=False)
            
        except Exception as e:
            print(f"Error al conectar con RabbitMQ: {e}")
            raise

    def process_task(self, task_data):
        # Datos básicos de la tarea
        task_id = task_data['task_id']
        task_type = task_data['task_type']
        data = task_data['data']
        
        print(f"{self.worker_id} procesando tarea: {task_id}")
        
        # Simula el tiempo de ejecución
        time.sleep(random.randint(1, 3))
        
        # Procesamiento según el tipo de tarea
        if task_type == 'text_processing':
            text = data.get('text', '')
            result = {
                'palabras': len(text.split()),
                'caracteres': len(text),
                'mayusculas': text.upper(),
                'reverso': text[::-1]
            }
        elif task_type == 'data_analysis':
            numbers = data.get('numbers', [])
            result = {
                'suma': sum(numbers),
                'promedio': sum(numbers) / len(numbers) if numbers else 0,
                'minimo': min(numbers) if numbers else 0,
                'maximo': max(numbers) if numbers else 0
            }
        else:
            result = {'mensaje': f'Procesado por {self.worker_id}', 'datos': data}
        
        return result

    def start(self):
        # Se ejecuta cuando llega una tarea nueva
        def callback(ch, method, properties, body):
            try:
                task_data = json.loads(body.decode())
                
                result = self.process_task(task_data)
                
                # Envía el resultado al servidor
                result_msg = {
                    'task_id': task_data['task_id'],
                    'worker_id': self.worker_id,
                    'result': result,
                    'status': 'completado'
                }
                
                self.channel.basic_publish(
                    exchange='',
                    routing_key='result_queue',
                    body=json.dumps(result_msg)
                )
                
                print(f"{self.worker_id} completó tarea: {task_data['task_id']}")
                
            except Exception as e:
                print(f"Error en {self.worker_id}: {e}")

        # Escucha tareas nuevas en la cola
        self.channel.basic_consume(
            queue='task_queue',
            on_message_callback=callback,
            auto_ack=True
        )

        print(f"{self.worker_id} esperando tareas...")
        self.channel.start_consuming()

if __name__ == "__main__":
    import sys
    # Permite asignar el nombre del worker al iniciarlo
    worker_id = sys.argv[1] if len(sys.argv) > 1 else "worker1"
    
    try:
        TaskWorker(worker_id).start()
    except KeyboardInterrupt:
        print(f"Worker {worker_id} detenido")
    except Exception as e:
        print(f"Error en worker: {e}")
