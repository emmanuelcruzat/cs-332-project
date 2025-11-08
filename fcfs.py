import threading
import socket
import time
import sys
from datetime import datetime

class Process:
    def __init__(self, pid, burst_time):
        self.pid = pid
        self.burst_time = burst_time

    def print_details(self, log_file):
        #print(f"Received process info: PID={self.pid}, Burst Time={self.burst_time}")
        log_file.write(f"Received process info: PID={self.pid}, Burst Time={self.burst_time}\n")
        log_file.flush()
        
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

pause_flag = threading.Event()
pause_flag.set()
process_queue = []
queue_lock = threading.Lock()

def scheduler(client_socket, log_file):
    while True:
        #print("-----\nCurrent queue:")
        #log_file.write(f"-----\nCurrent queue:\n")
        #log_file.flush()
        
        #for i in range(len(process_queue)):
            #process_queue[i].print_details(log_file)

        if len(process_queue) > 0:
            with queue_lock:
                front = process_queue.pop(0)
        elif isEnd:
            print("All processes have been handled")
            log_file.write("All processes have been handled\n")
            log_file.flush()
            break
        else:
            continue

        #print(f"Process {front.pid} started with burst time: {front.burst_time}")
        log_file.write(f"Process {front.pid} started with burst time: {front.burst_time}\n")
        log_file.flush()

        time.sleep(front.burst_time)

        #print(f"Process {front.pid} completed in burst time: {front.burst_time}")
        log_file.write(f"Process {front.pid} completed in burst time: {front.burst_time}\n")
        log_file.flush()

        pause_flag.wait()

        #print(f"Awoke.")
        #log_file.write(f"Awoke.\n")
        #log_file.flush()
# ...
def shell():
    while True:
        #command input
        command = input("fcfs-shell> ")
        
        if command == "pause":
            pause_flag.clear()
        if command == "continue":
            pause_flag.set()
        if command == "list":
            for i in range(len(process_queue)):
                print(f"{i}: PID={process_queue[i].pid}, Burst Time={process_queue[i].burst_time}")
# ...

def receiver(client_socket, log_file):
    isPid = True
    
    while True:
        data = client_socket.recv(1024).decode()

        pid_string = ""
        burst_string = ""

        pid_list = []
        burst_list = []

        for char in data:
            #print(f"char {char} pid_string {pid_string} burst_string {burst_string}")
            if char == "E":
                isEnd = True
                #print("Simulator has stopped sending processes")
                log_file.write("Simulator has stopped sending processes\n")
                log_file.flush()
                break
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
            newProcess = Process(int(pid_list[i]), int(burst_list[i]))
            newProcess.print_details(log_file)
            with queue_lock:
                process_queue.append(newProcess)
#...

def main():
    global client_socket, isEnd
    isEnd = False
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
    except socket.error as e:
        print("Connection failed:", e)
        exit(1)

    print("Connected to the server")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"fcfs_log_{timestamp}.txt"
    log_file = open(log_filename, "w")


    scheduler_thread = threading.Thread(target=scheduler, args=(client_socket, log_file))
    shell_thread = threading.Thread(target=shell)
    receiver_thread = threading.Thread(target=receiver, args=(client_socket, log_file))
    scheduler_thread.start()
    shell_thread.start()
    receiver_thread.start()

    # ...

    shell_thread.join()
    scheduler_thread.join()
    receiver_thread.join()
    client_socket.close()
    log_file.close()

if __name__ == "__main__":
    main()