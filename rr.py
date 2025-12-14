import threading
import socket
import time
import sys
from datetime import datetime

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

class Process:
    def __init__(self, pid, burst_time):
        self.pid = pid
        self.burst_time = burst_time
        self.remaining_time = burst_time

    def print_details(self, log_file):
        log_file.write(f"Received process info: PID={self.pid}, Burst Time={self.burst_time}\n")
        log_file.flush()

pause_flag = threading.Event()
pause_flag.clear()
process_queue = []
queue_lock = threading.Lock()

def scheduler(client_socket, log_file):
    global isEnd
    isPid = True

    while True:
        data = client_socket.recv(1024).decode()

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

        log_file.write(f"Process {front.pid} started with remaining time: {front.remaining_time}\n")
        log_file.flush()

        if front.remaining_time <= time_quantum: #if time left is shorter than time slice
            time.sleep(front.remaining_time)
        else:                                   #if there is time left over
            time.sleep(time_quantum)
            front.remaining_time -= time_quantum
            with queue_lock:
                process_queue.append(front)
            log_file.write(f"Process {front.pid} exceeded time quantum ({time_quantum}) and will be requeued with remaining time: {front.remaining_time}s\n")
            log_file.flush()

        log_file.write(f"Process {front.pid} completed in burst time: {front.burst_time}\n")
        log_file.flush()

        pause_flag.wait()

def shell():
    global time_quantum
    time_quantum = int(input("How long do you want the time quantum to be: "))
    print(f"Time quantum is set to: {time_quantum}\n")
    print("\nShell interface ready. Commands: pause | continue | list\n")
    while True:
        command = input("rr-shell> ").strip().lower() 
        if command == "pause":
            pause_flag.clear()
        if command == "continue":
            pause_flag.set()
        if command == "list":
            for i in range(len(process_queue)):
                print(f"{i}: PID={process_queue[i].pid}, Burst Time={process_queue[i].burst_time}, Remaining Time={process_queue[i].remaining_time}")

def main():
    global client_socket, isEnd, time_quantum
    time_quantum = 1
    isEnd = False

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((SERVER_IP, SERVER_PORT))
    except socket.error as e:
        print("Connection failed:", e)
        exit(1)

    print("Connected to the server")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"rr_log_{timestamp}.txt"
    log_file = open(log_filename, "w")


    scheduler_thread = threading.Thread(target=scheduler, args=(client_socket, log_file))
    shell_thread = threading.Thread(target=shell)
    scheduler_thread.start()
    shell_thread.start()

    # ...

    shell_thread.join()
    scheduler_thread.join()
    client_socket.close()
    log_file.close()

if __name__ == "__main__":
    main()