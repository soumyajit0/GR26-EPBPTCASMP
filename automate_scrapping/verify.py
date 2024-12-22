from app import start_server
import csv

import socket
import json
import time

#main()

def get_next_row(file_path,start_num):
    """
    A generator to yield the next row's number, FB link, and personality from a CSV file.

    :param file_path: Path to the CSV file.
    :yields: A tuple of (row_number, FB link, personality) for each row.
    """
    with open(file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)  # Read CSV as dictionaries
        for idx, row in enumerate(reader, start=1):  # Enumerate with 1-based index
            yield idx, row["FB Link"], row["Personality"]

file_path = r'D:\Final Year Project\Final-Year-Project-Shared\clean_data.csv'


import collections
import socket

d=collections.defaultdict(int)
Per=None

def check_stop():
    count=0
    mxv=0
    mxk=None
    global d
    for key,val in d.items():
        print(f"{key}: {val}")
        if val>mxv:
            mxv=val
            mxk=key
        count+=val
    return (mxk==Per and count>=10) or count>=25

def start_server2(host='127.0.0.1', port=65431):
    global Row,d
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Server listening on {host}:{port}...")
        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")
                data = conn.recv(1024)  # Receive up to 1024 bytes
                if not data:
                    break
                message = data.decode('utf-8')  # Decode received bytes
                print(f"Received: {message}")
                d[message]=d.get(message,0)+1
                if check_stop():
                    store_details()
                    Row+=1
                    d.clear()
                    time.sleep(2)
                    send_next()

                
file_path=r'D:\Final Year Project\Final-Year-Project-Shared\clean_data.csv'
Row=1

def store_details(column_number=5):
    global Row,d
    row_number=Row
    data=d
    """
    Writes a dictionary's key-value pairs into a specific cell of a CSV file.

    :param file_path: Path to the CSV file.
    :param row_number: Row number (1-indexed) where the data should be written.
    :param column_number: Column number (1-indexed) where the data should be written.
    :param data: Dictionary containing key-value pairs to write.
    """
    # Format the dictionary into a string
    formatted_data = ', '.join(f"{key}={value}" for key, value in data.items())
    
    # Read the existing content of the CSV
    rows = []
    with open(file_path, 'r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        rows = list(reader)
    
    # Ensure the file has enough rows
    while len(rows) < row_number:
        rows.append([])
    
    # Ensure the row has enough columns
    while len(rows[row_number]) < column_number:
        rows[row_number].append('')
    
    # Write the formatted dictionary into the specific cell
    rows[row_number][column_number - 1] = formatted_data
    
    # Write back the modified rows to the CSV
    with open(file_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def send_data(host='127.0.0.1', port=65432, message="Hello, Server!"):
    """
    Sends data to a server.

    :param host: IP address of the server.
    :param port: Port the server is listening on.
    :param message: The message to send.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print(f"Connected to server {host}:{port}")
        client_socket.sendall(message.encode('utf-8'))  # Send message
        return

All=[ row for row in get_next_row(file_path,start_num=1)]
start_num=24             # starts at 1, indexing at 0
def send_next():
    global Per,Row
    row_number, fb_link, personality=All[Row-1]
    if row_number<start_num:
        Row+=1
        send_next()
        return
    Per=personality
    print(f"Row: {row_number}, FB Link: {fb_link}, Personality: {personality}")
    send_data(message=fb_link)
    

import threading
threading.Thread(target=start_server,args=()).start()
threading.Thread(target=start_server2,args=()).start()
time.sleep(5)
send_next()

