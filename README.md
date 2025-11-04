 Sistema Distribuido de Tareas

Este proyecto implementa un sistema distribuido que permite procesar tareas de forma paralela mediante sockets y RabbitMQ.  
Los clientes se conectan al servidor, envían tareas y reciben los resultados una vez que los *workers* las procesan.


## Objetivo

Diseñar una arquitectura distribuida donde los procesos se comuniquen entre sí a través de sockets y una cola de mensajes.  
El sistema busca distribuir la carga de trabajo y permitir la ejecución de tareas en paralelo para mejorar la eficiencia.


## Componentes

### Cliente (`cliente.py`)
- Se conecta al servidor por socket TCP.  
- Envía tareas y consulta sus resultados.  
- Permite simular distintos tipos de clientes (por ejemplo, web o móvil).  
- Tipos de tareas:
  - Procesamiento de texto: cuenta palabras, invierte el texto y lo convierte en mayúsculas.  
  - Análisis de números: calcula suma, promedio, mínimo y máximo.  
  - Tareas simples de prueba.

### Servidor (`servidor.py`)
- Escucha conexiones de los clientes.  
- Recibe las tareas y las envía a RabbitMQ (cola `task_queue`).  
- Escucha los resultados de los *workers* desde la cola `result_queue`.  
- Devuelve los resultados al cliente.

### Workers (`worker.py`)
- Procesan las tareas recibidas desde RabbitMQ.  
- Cada worker puede ejecutar distintos tipos de tareas.  
- Envían los resultados al servidor mediante la cola `result_queue`.  
- Es posible ejecutar varios workers en paralelo.

### RabbitMQ
- Funciona como sistema de mensajería entre el servidor y los *workers*.  
- Cola `task_queue`: recibe tareas del servidor.  
- Cola `result_queue`: recibe los resultados procesados por los workers.

### Almacenamiento distribuido (conceptual)
El sistema está preparado para integrarse con:
- **PostgreSQL**, para guardar información o registros de tareas.  
- **Amazon S3**, para almacenar archivos o resultados más grandes.

### Balanceador de carga (conceptual)
Se podría incorporar **Nginx** o **HAProxy** para distribuir las solicitudes entre varios servidores, lo que aumentaría la disponibilidad y escalabilidad del sistema.


## Ejecución del sistema

### 1. Iniciar RabbitMQ con Docker
Desde la carpeta del proyecto:
```bash
docker compose up
```

Esto levanta RabbitMQ y habilita el panel de administración en  
[http://localhost:15672](http://localhost:15672)  
Usuario y contraseña por defecto: `guest / guest`

### 2. Ejecutar el servidor
En otra terminal:
```bash
python servidor.py
```

Debería mostrar:
```
Conectado a RabbitMQ
Servidor iniciado
Escuchando en localhost:8888
```

### 3. Ejecutar los workers
En otras terminales (una por worker):
```bash
python worker.py worker1
python worker.py worker2
```

### 4. Ejecutar el cliente
En otra terminal:
```bash
python cliente.py
```

## Requerimientos

Instalar las dependencias con:
```bash
pip install -r requirements.txt
```

Librerías utilizadas:
- `pika`: conexión con RabbitMQ.  
- `socket` y `threading`: comunicación entre cliente y servidor.  
- `json`: manejo de datos estructurados.  
- `time`, `hashlib` y `random`: control de tiempos y simulación de tareas.

