import threading
import socket
import time
import sys
from datetime import datetime

class Process:
    def __init__(self, pid, burst_time):
        self.pid = pid
        self.burst_time = burst_time
        

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

pause_flag = threading.Event()
pause_flag.clear()
process_queue = []
queue_lock = threading.Lock()


def scheduler(client_socket):
    while True:
        data = client_socket.recv(1024).decode()

        if data == "END":
            break;
        
        #convert data in process objects
        #put process objects in the queue
        #simulates running the processes??

        print(f"Collected data={data}")

# ...

#def shell():
# ...

def main():
    global client_socket

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
    except socket.error as e:
        print("Connection failed:", e)
        exit(1)

    print("Connected to the server")

    scheduler_thread = threading.Thread(target=scheduler(client_socket))
    #shell_thread = threading.Thread(target=shell)
    scheduler_thread.start()
    #shell_thread.start()

    # ...

    #shell_thread.join()
    scheduler_thread.join()
    client_socket.close()
    # log_file.close()

if __name__ == "__main__":
    main()