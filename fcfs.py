import threading
import socket
import time
import sys
from datetime import datetime

class Process:
    def __init__(self, pid, burst_time):
        self.pid = pid
        self.burst_time = burst_time

    def print_details(self):
        print(f"({self.pid}, {self.burst_time}) ")
        

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

pause_flag = threading.Event()
pause_flag.clear()
process_queue = []
queue_lock = threading.Lock()


def scheduler(client_socket):

    isEnd = False;
    isPid = True;

    while True:
        data = client_socket.recv(1024).decode()

        pid_string = ""
        burst_string=""

        pid_list = []
        burst_list = []

        for char in data:
            #print(f"char {char} pid_string {pid_string} burst_string {burst_string}")
            if char == "E":
                isEnd = True;
                break;
            elif isPid:
                if char != " ":
                    pid_string += char
                else:
                    isPid = False
                    pid_list.append(int(pid_string))
                    pid_string = ""
            else:
                if char != " ":
                    burst_string += char
                else:
                    isPid = True
                    burst_list.append(int(burst_string))
                    burst_string = ""

        #pid, burst_time = data.rstrip().split(None, 1)
        #print(f"pid_list={pid_list} burst_list={burst_list}")
        # make new process objects and append to queue
        for i in range(len(pid_list)):
            process_queue.append(Process(int(pid_list[i]), int(burst_list[i])))

        for i in range(len(process_queue)):
            process_queue[i].print_details()

        if len(process_queue) > 0:
            front = process_queue.pop(0)
        elif isEnd == True:
            print("IT IS THE END.")
            break;
        else:
            print("Didn't detect END")
            break;

        print(f"PID = {front.pid}")
        print(f"Burst time = {front.burst_time}")
        print(f"Sleeping for = {front.burst_time}s")

        time.sleep(front.burst_time)

        print(f"Awoke.")

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