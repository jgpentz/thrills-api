import socket
import json

from thrills_api.internals.msg_payload_types import MsgType

NODE_MANAGER_HOST = "127.0.0.1"  # localhost
NODE_MANAGER_PORT = 3050  # Port the server is listening on


def node_manager_client(msg_type: MsgType, data=None):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((NODE_MANAGER_HOST, NODE_MANAGER_PORT))
    print(f"connected to server {NODE_MANAGER_HOST}:{NODE_MANAGER_PORT}")

    message = {"type": msg_type.value, "data": data}
    client_socket.sendall(json.dumps(message).encode())

    # receive response from the server
    response = client_socket.recv(50000)
    print("Received response from server")

    if response:
        response_json = response.decode()

        # Parse JSON string into dictionary
        response = json.loads(response_json)

    print("closing connection")
    client_socket.close()

    return response
