import socket
from fg_net import FGNetFDM

def listen_and_parse_udp(host: str, port: int):
    """
    Listens to UDP packets on the specified host and port, parses them as FGNetFDM packets.
    
    Args:
        host (str): The IP address or hostname to listen on.
        port (int): The port number to listen on.
    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind the socket to the address and port
    sock.bind((host, port))
    print(f"Listening on {host}:{port}")

    while True:
        # Receive data from the socket
        data, addr = sock.recvfrom(4096)  # 4096 is the buffer size
        print(f"Received packet from {addr}")

        try:
            # Parse the data as FGNetFDM
            fg_packet = FGNetFDM(data)
            
            # Optionally, you can swap bytes if needed:
            # fg_packet.swap_bytes()

            # Now you can access fields of fg_packet
            print(f"Version: {fg_packet.version}")
            print(f"Latitude: {fg_packet.latitude}")
            print(f"Longitude: {fg_packet.longitude}")
            print(f"Num engines: {fg_packet.num_engines}")
            print(f"engine State: {fg_packet.eng_state}")
            print(f"RPM: {fg_packet.rpm}")
            print(f"weight on wheels: {fg_packet.wow}")
            # Add more fields to print or process as needed

        except Exception as e:
            print(f"Failed to parse FGNetFDM packet: {e}")

if __name__ == '__main__':
    # Replace '0.0.0.0' with the desired host IP address or 'localhost' for local testing.
    # Replace 5000 with the desired port number.
    listen_and_parse_udp('0.0.0.0', 5550)
