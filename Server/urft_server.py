from sys import argv
from socket import *

server_ip = argv[1]
server_port = int(argv[2])

sock = socket(AF_INET, SOCK_DGRAM)
sock.bind((server_ip, server_port))

expected_seq = 0
file = None

print("waiting...")

while True:
    data, addr = sock.recvfrom(1030) # 1024 + 6 bytes for header

    try:
        header, content = data.split(b":", 1) # structure : "seq_num:file_path" | 1 split maximum
        seq_num = int(header.decode())
    except ValueError: # <-------- shit packet I guess
        continue  # It works lmfao

    if seq_num < expected_seq:
        # Duplicated packet
        sock.sendto(f"ACK{seq_num}".encode(), addr)
        continue

    if seq_num == expected_seq:
        if file is None:
            file = open(content.decode(), "w")  # Handle First Packet (file path)
        elif content.decode() == "EOF":
            print("File transfer completed.")
            file.close()
            sock.sendto(f"ACK{seq_num}".encode(), addr)
            break
        else:
            file.write(content.decode())  # Write File

        # Send ACK
        sock.sendto(f"ACK{seq_num}".encode(), addr)
        expected_seq += 1

sock.close()