from sys import argv
from socket import *
import struct

file_path = argv[1]
server_ip = argv[2]
server_port = int(argv[3])

# chunk_size = 1024 # 1KB per packet
chunk_size = 256
client_timeout = 1 # ACK Timeout

file_data = open(file_path, "rb").read()

sock = socket(AF_INET, SOCK_DGRAM)
sock.settimeout(client_timeout)

# Send File Name
seq_num = 0
while True:
    try:
        sock.sendto(f"{seq_num}:{file_path}".encode(), (server_ip, server_port))
        ack, addr = sock.recvfrom(1024)
        if ack.decode() == f"ACK{seq_num}":
            break
    except timeout:
        print(f"Retrying file name (seq {seq_num})...")
seq_num += 1

# Send File in Chunks
for i in range(0, len(file_data), chunk_size):
    chunk = file_data[i : i+chunk_size]
    while True:
        try:
            sock.sendto(f"{seq_num}:".encode() + chunk, (server_ip, server_port))
            ack, addr = sock.recvfrom(1024)
            if ack.decode() == f"ACK{seq_num}":
                break  # Move to next chunk
        except timeout:
            print(f"Retrying chunk {seq_num}...")
    seq_num += 1

# Send EoF Message
while True:
    try:
        sock.sendto(f"{seq_num}:EOF".encode(), (server_ip, server_port))
        ack, addr = sock.recvfrom(1024)
        if ack.decode() == f"ACK{seq_num}":
            break
    except timeout:
        print(f"Retrying EOF (seq {seq_num})...")

sock.close()
print("File transfer complete!")