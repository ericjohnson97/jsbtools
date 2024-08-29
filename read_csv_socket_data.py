import json
import socket
import xml.etree.ElementTree as ET
import csv
from typing import Dict, Any, List

def parse_xml_config(file_path: str) -> Dict[str, Any]:
    """
    Parse the XML file to extract the UDP socket configuration, output file name, and property labels.

    Args:
        file_path (str): Path to the XML configuration file.

    Returns:
        Dict[str, Any]: A dictionary containing the port, protocol, and a list of property labels.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    output_config = {'properties': []}
    
    for output in root.findall('output'):
        if output.attrib['type'].upper() == "SOCKET" and output.attrib['protocol'].upper() == "UDP":
            output_config['port'] = int(output.attrib['port'])
            for property_tag in output.findall('property'):
                label = property_tag.get('caption')
                if label is None:
                    label = property_tag.text.strip()
                output_config['properties'].append(label)
            break
    
    return output_config

def receive_udp_data(port: int, property_labels: List[str]) -> None:
    """
    Create a UDP socket to receive CSV data, parse it, and print the data as a dictionary.

    Args:
        port (int): The port to listen for incoming UDP packets.
        property_labels (List[str]): List of property labels extracted from the XML configuration.
    """
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("localhost", port))

    print(f"Listening for UDP packets on port {port}...")

    # Create a UDP socket to send to plotjuggler
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


    while True:
        data, _ = udp_socket.recvfrom(4096)
        decoded_data = data.decode('utf-8')
        # print(decoded_data)
        csv_reader = csv.reader(decoded_data.splitlines(), delimiter=',')

        for row in csv_reader:
            data_dict = {'timestamp': row[0]}
            for i, label in enumerate(property_labels, start=1):
                data_dict[label] = float(row[i])

        send_udp_data(data_dict, send_socket)

def send_udp_data(data: dict, udp_socket, ip: str = "127.0.0.1", port: int = 6000) -> None:
    """
    Send a dictionary as JSON via UDP to the specified IP and port.

    Args:
        data (dict): The dictionary to send.
        ip (str): The IP address to send the data to. Defaults to 127.0.0.1.
        port (int): The port to send the data to. Defaults to 6000.
    """
    # Convert the dictionary to a JSON string
    json_data = json.dumps(data)    
    # print(json_data)

    udp_socket.sendto(f"{json_data}\n".encode('utf-8'), (ip, port))
    print(f"Data sent to {ip}:{port}")


if __name__ == "__main__":
    config_file = "/home/eric/PX4-Autopilot/Tools/simulation/jsbsim/jsbsim_bridge/models/F450/F450.xml"  # Replace with the actual file path
    output_config = parse_xml_config(config_file)
    
    if 'port' in output_config:
        receive_udp_data(output_config['port'], output_config['properties'])
    else:
        print("No valid UDP output configuration found in the XML file.")
