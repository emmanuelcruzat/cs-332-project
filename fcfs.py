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
        print(f"Received process info: PID={self.pid}, Burst Time={self.burst_time}")
        log_file.write(f"Received process info: PID={self.pid}, Burst Time={self.burst_time}")
        log_file.flush()
        

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

pause_flag = threading.Event()
pause_flag.set()
process_queue = []
queue_lock = threading.Lock()

def scheduler(client_socket, log_file):

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
                print("Simulator has stopped sending processes")
                log_file.write("Simulator has stopped sending processes")
                log_file.flush()
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
            newProcess = Process(int(pid_list[i]), int(burst_list[i]))
            newProcess.print_details(log_file);
            process_queue.append(newProcess)

        #print("-----\nCurrent queue:")
        #log_file.write(f"-----\nCurrent queue:\n")
        #log_file.flush()
        
        #for i in range(len(process_queue)):
            #process_queue[i].print_details(log_file)

        if len(process_queue) > 0:
            front = process_queue.pop(0)
        elif isEnd:
            print("All processes have been handled")
            log_file.write("All processes have been handled")
            log_file.flush()
            break;
        #else:
            #print("Didn't detect END")
            #log_file.write(f"Didn't detect END\n")
            #log_file.flush()
            #break;

        print(f"Process {front.pid} started with burst time: {front.burst_time}")
        log_file.write(f"Process {front.pid} started with burst time: {front.burst_time}")
        log_file.flush()

        time.sleep(front.burst_time)
        pause_flag.wait();

        print(f"Process {front.pid} completed in burst time: {front.burst_time}")
        log_file.write(f"Process {front.pid} completed in burst time: {front.burst_time}")
        log_file.flush()

        #print(f"Awoke.")
        #log_file.write(f"Awoke.\n")
        #log_file.flush()

# ...

def shell():

    while True:
        #command input
        command = input("Enter a command: ")
        
        if command == "pause":
            pause_flag.clear();
        if command == "continue":
            pause_flag.set();
        if command == "list":
            #display all active processes (not completed processes)
    
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

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"fcfs_log_{timestamp}.txt"
    log_file = open(log_filename, "w")


    scheduler_thread = threading.Thread(target=scheduler(client_socket, log_file))
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
