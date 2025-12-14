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
        log_file.write(f"Received process info: PID={self.pid}, Burst Time={self.burst_time}\n")
        log_file.flush()
        
SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

pause_flag = threading.Event()
pause_flag.set()
process_queue = []
queue_lock = threading.Lock()

def scheduler(client_socket, log_file):    
    global isEnd
    isPid = True

    while True:
        data = client_socket.recv(1024).decode()

        '''
        rec(v) creates the blocking issue because it blocks the scheduler thread
        until new data arrives from task generator

        settimeout() turns rec(v) from a blocking call into a periodic check for data

        after we try( rec(v) ), we except.socket.timeout: pass so that if no new data arrives
        within the timeout period, the program does nothing and keeps scheduling
        '''

        pid_string = ""
        burst_string = ""
        pid_list = []
        burst_list = []

        for char in data:
            if char == "E":
                isEnd = True
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

        for i in range(len(pid_list)):
            newProcess = Process(int(pid_list[i]), int(burst_list[i]))
            newProcess.print_details(log_file)
            with queue_lock:
                process_queue.append(newProcess)
    
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

        pause_flag.wait()

        log_file.write(f"Process {front.pid} started with burst time: {front.burst_time}\n")
        log_file.flush()

        time.sleep(front.burst_time)

        log_file.write(f"Process {front.pid} completed in burst time: {front.burst_time}\n")
        log_file.flush()

def shell():
    print("\nShell interface ready. Commands: pause | continue | list\n")
    while True:
        command = input("fcfs-shell> ").strip().lower() 
        if command == "pause":
            pause_flag.clear()
        if command == "continue":
            pause_flag.set()
        if command == "list":
            for i in range(len(process_queue)):
                print(f"{i}: PID={process_queue[i].pid}, Burst Time={process_queue[i].burst_time}")

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
    scheduler_thread.start()
    shell_thread.start()

    shell_thread.join()
    scheduler_thread.join()
    client_socket.close()
    log_file.close()

if __name__ == "__main__":
    main()