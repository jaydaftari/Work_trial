import socket
import time

host = "broker"
port = 9092

while True:
    try:
        with socket.create_connection((host, port), timeout=3):
            print("Kafka is available!")
            break
    except OSError:
        print("Waiting for Kafka...")
        time.sleep(3)
