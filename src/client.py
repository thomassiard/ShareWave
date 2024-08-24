"""
Provides Client's functionalities and actions. See client_handler which is the main entry point for user interaction handling
"""
from src.protocol import *
import src.file_handler as fd
from socket import *
import json
import asyncio
import sys
import uuid
import hashlib
import logging
import os

# Define the size of the read buffer
READ_SIZE = 4096

# Define protocol-related constants
RET_FAIL = 0
RET_SUCCESS = 1
RET_ALREADY_SEEDING = 2
RET_NO_AVAILABLE_TORRENT = 3
RET_TORRENT_DOES_NOT_EXIST = 4
RET_FINISHED_DOWNLOAD = 5
RET_FINSH_SEEDING = 6

OPT_GET_LIST = 10
OPT_GET_TORRENT = 11
OPT_START_SEED = 12
OPT_STOP_SEED = 13
OPT_UPLOAD_FILE = 14
OPT_GET_PEERS = 15
OPT_GET_PIECE = 16

# Define other required constants
OPC = 'op_code'
RET = 'return_code'
TID = 'torrent_id'
FILE_NAME = 'file_name'
TOTAL_PIECES = 'total_pieces'
SEEDER_LIST = 'seeder_list'
TORRENT_LIST = 'torrent_list'
TORRENT = 'torrent'
PIECE_DATA = 'piece_data'
PIECE_IDX = 'piece_index'
PEER_LIST = 'peer_list'
IP = 'ip'
PORT = 'port'
PID = 'peer_id'

# Postavljanje osnovnog logger-a za zapisivanje u fajl
log_dir = 'src/logs'
log_file = 'client.log'
log_path = os.path.join(log_dir, log_file)

# Konfiguracija osnovnog logovanja
logging.basicConfig(filename=log_path,
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')



class Client:
    def __init__(self, src_ip, src_port):
        self.src_ip = src_ip
        self.src_port = src_port
        self.peer_id = self.create_peer_id()
        self.tid = -1
        # Peer States
        self.peer_choked = True
        self.peer_interested = False
        self.peer_am_seeding = False
        self.peer_am_leeching = False

        # List of seeders & piece buffer associated to the current download 
        self.seeders_list = {}
        self.piece_buffer = PieceBuffer()

    ########### CONNECTION HANDLING ###########

    async def connect_to_tracker(self, ip=None, port=None):
        """
        Handles connecting to the tracker and returns the reader and writer.
        """
        ip = ip or "127.0.0.1"
        port = port or 8888

        try:
            reader, writer = await asyncio.open_connection(ip, int(port))
            logging.info(f"Connected to tracker at {ip}:{port}")
            return reader, writer

        except ConnectionError as e:
            logging.error(f"Connection Error: unable to connect to tracker. Error: {e}")
            sys.exit(-1)

    async def connect_to_peer(self, ip, port, requests):
        """
        This function handles both sending the payload request, and receiving the expected response.
        """
        try:
            logging.info(f"Connecting to seeder at {ip}:{port} ...")
            reader, writer = await asyncio.open_connection(ip, int(port))
            logging.info(f"Connected as leecher: {self.src_ip}:{self.src_port}")

            await self.send(writer, requests)
            res = await self.receive(reader)
            writer.close()
            return res

        except ConnectionError as e:
            logging.error(f"Connection Error: unable to connect to peer. Error: {e}")
            sys.exit(-1)
            

    async def receive_request(self, reader, writer):
        """
        Handle incoming PEER requests and returns the appropriate response object.
        """
        try:
            data = await reader.read(READ_SIZE)
            peer_request = json.loads(data.decode())
            addr = writer.get_extra_info('peername')

            logging.info(f"Received request {peer_request!r} from {addr!r}.")
            response = self.handle_peer_request(peer_request)
            payload = json.dumps(response)
            logging.info(f"Sending payload: {payload}")
            writer.write(payload.encode())
            await writer.drain()
            logging.info(f"Closing the connection for {addr}")
        except Exception as e:
            logging.error(f"Exception occurred: {e}")
        
        writer.close()

    async def start_seeding(self):
        """
        Once a client begins seeding, we need to open and host a connection as a 'server'.
        """
        server = await asyncio.start_server(self.receive_request, self.src_ip, self.src_port)
        if not server:
            logging.error("Failed to start seeding server.")
            return
        addr = server.sockets[0].getsockname()
        logging.info(f'SEEDING !!! ... Serving on {addr}')
        async with server:
            try:
                await server.serve_forever()
            except Exception as e:
                logging.error(f"Server error: {e}")
            finally:
                server.close()
                await server.wait_closed()

    async def receive(self, reader):
        """
        Handle incoming RESPONSE messages and decode to the JSON object.
        Pass the JSON object to handle_request() that will handle the request appropriately.
        """
        data = await reader.read(READ_SIZE)
        payload = json.loads(data.decode())
        logging.info(f"Received decoded message: {payload!r}")
        opc = payload[OPC]
        if opc > 9:
            res = await self.handle_server_response(payload)
        else:
            res = self.handle_peer_response(payload)
        
        return res

    async def send(self, writer, payload: dict):
        """
        Encode the payload to an encoded JSON object and send to the appropriate client/server.
        """
        json_payload = json.dumps(payload)
        logging.info(f"Sending encoded request message: {json_payload}")
        writer.write(json_payload.encode())

    ########### REQUEST & RESPONSE HANDLING ###########
    
    async def handle_server_response(self, response) -> int:
        """
        Handle the response from a server, presumably a python dict has been loaded from the JSON object.
        Returns the appropriate RET code to client_handler.
        """
        ret = response[RET]
        opc = response[OPC]

        if ret == RET_FAIL:
            logging.info("RESPONSE: returned failed")
            return -1
        elif ret == RET_ALREADY_SEEDING:
            logging.info("UPLOAD FAIL: You are already currently seeding a file.")
            return -1
        elif ret == RET_NO_AVAILABLE_TORRENTS:
            logging.info("GET TORRENT LIST FAIL: There are no available torrents right now.")
            return -1
        elif ret == RET_TORRENT_DOES_NOT_EXIST:
            logging.info("GET TORRENT FAIL: The torrent ID does not exist")
            return -1

        if opc == OPT_GET_LIST:
            torrent_list = response[TORRENT_LIST]
            logging.info("Torrent List:")
            logging.info("TID \t FILE_NAME \t TOTAL_PIECES \t SEEDERS")
            logging.info("--- \t -------- \t ------------ \t -------")
            for idx, curr_torrent in enumerate(torrent_list):
                logging.info(f"{curr_torrent[TID]} \t {curr_torrent[FILE_NAME]} \t {curr_torrent[TOTAL_PIECES]} \t\t {curr_torrent[SEEDER_LIST]}")
            return RET_SUCCESS
        elif opc == OPT_GET_TORRENT:
            torrent = response[TORRENT]
            self.peer_am_leeching = True
            self.seeders_list = torrent[SEEDER_LIST]
            self.piece_buffer.set_buffer(torrent[TOTAL_PIECES])
            await self.download_file(torrent[TOTAL_PIECES], torrent[FILE_NAME])
            return RET_FINISHED_DOWNLOAD    
        elif opc == OPT_START_SEED or opc == OPT_UPLOAD_FILE:
            self.peer_am_leeching = False
            self.peer_am_seeding = True
            self.tid = response[TID]
            await self.start_seeding()
            return RET_FINSH_SEEDING
        elif opc == OPT_STOP_SEED:
            self.peer_am_seeding = False
            return RET_FINSH_SEEDING

        return 1

    def create_server_request(self, opc: int, torrent_id=None, filename=None) -> dict:
        """
        Called from client_handler.py to create the appropriate server request given the op code.
        Returns a dictionary of our payload.
        """
        payload = {OPC: opc, IP: self.src_ip, PORT: self.src_port, PID: self.peer_id}
        if opc in (OPT_GET_TORRENT, OPT_START_SEED, OPT_STOP_SEED):
            payload[TID] = torrent_id
        elif opc == OPT_UPLOAD_FILE:
            num_pieces = self.upload_file(filename)
            if num_pieces == 0:
                return {}
            payload[FILE_NAME] = self.file_strip(filename)
            payload[TOTAL_PIECES] = num_pieces

        return payload

    def handle_peer_response(self, response) -> int:
        """
        Handle the response from a peer. Returns 1 if successful.
        """
        ret = response[RET]
        opc = response[OPC]

        if ret == RET_FAIL or ret != RET_SUCCESS:
            return -1
        
        if opc == OPT_GET_PEERS:
            self.seeders_list = response[PEER_LIST]
        elif opc == OPT_GET_PIECE:
            data = response[PIECE_DATA]
            idx = response[PIECE_IDX]
            new_piece = Piece(idx, data)
            self.piece_buffer.add_data(new_piece)
        
        return 1

    def handle_peer_request(self, request) -> dict:
        """
        Handle the incoming request (this applies to peers only). Returns a response dictionary object.
        """
        opc = request[OPC]
        response = {OPC: opc, IP: self.src_ip, PORT: self.src_port}

        if opc == OPT_GET_PEERS:
            response[PEER_LIST] = self.seeders_list
            response[RET] = RET_SUCCESS
        elif opc == OPT_GET_PIECE:
            piece_idx = request[PIECE_IDX]
            if self.piece_buffer.check_if_have_piece(piece_idx):
                response[PIECE_DATA] = self.piece_buffer.get_data(piece_idx)
                response[PIECE_IDX] = request[PIECE_IDX]
                response[RET] = RET_SUCCESS
            else:
                response[RET] = RET_FAIL
        return response

    def create_peer_request(self, opc: int, piece_idx=None) -> dict:
        """
        Create the appropriate peer request.
        """
        payload = {OPC: opc, IP: self.src_ip, PORT: self.src_port}

        if opc == OPT_GET_PIECE:
            payload[PIECE_IDX] = piece_idx
        
        return payload

    ########### HELPER FUNCTIONS ###########

    async def simple_peer_selection(self, num_pieces: int):
        """
        A simple peer selection that downloads an entire file from the first peer in list.
        """
        pid = next(iter(self.seeders_list))
        initial_peer_ip = self.seeders_list[pid][IP]
        initial_peer_port = self.seeders_list[pid][PORT]
        
        for idx in range(num_pieces):
            request = self.create_peer_request(OPT_GET_PIECE, idx)
            await self.connect_to_peer(initial_peer_ip, initial_peer_port, request)
        
    async def even_peer_selection(self, num_pieces: int):
        """
        Evenly distributes the piece requests among available peers.
        """
        num_peers = len(self.seeders_list)

        peer_list = list(self.seeders_list.values())
        requests_list = [self.create_peer_request(OPT_GET_PIECE, i) for i in range(num_pieces)]
        
        curr_piece = 0
        while curr_piece < num_pieces:
            curr_peer = curr_piece % num_peers
            await self.connect_to_peer(peer_list[curr_peer][IP], peer_list[curr_peer][PORT], requests_list[curr_piece])
            curr_piece += 1   

    async def download_file(self, num_pieces: int, filename: str):
        """
        Method for starting the download of a file by calling the peer selection method to download pieces.
        Once done, output it to the output directory with peer_id appended to the filename.
        """
        await self.even_peer_selection(num_pieces)

        while not self.piece_buffer.check_if_have_all_pieces():
            await asyncio.sleep(1)  # Avoid tight loop

        pieces_to_file = [self.piece_buffer.get_data(i) for i in range(self.piece_buffer.get_size())]
        output_dir = f'output/{self.peer_id}_{filename}'
        try:
            fd.decode_to_file(pieces_to_file, output_dir)
            logging.info(f"Successfully downloaded file: {output_dir}")
        except Exception as e:
            logging.error(f"Exception occurred in download_file() with filename: {filename}. Error: {e}")

    def upload_file(self, filename: str) -> int:
        """
        Called when the user begins to be the initial seeder (upload a file). The piece buffer will be
        populated and initialized.
        Returns the number of pieces in the created piece buffer.
        """
        try:
            pieces, num_pieces = fd.encode_to_bytes(filename)
            self.piece_buffer.set_buffer(num_pieces)
            for idx, piece_data in enumerate(pieces):
                self.piece_buffer.add_data(Piece(idx, piece_data))
            return num_pieces
        except Exception as e:
            logging.error(f"Exception occurred in upload_file() with filename: '{filename}'. Error: {e}")
            return 0

    def create_peer_id(self) -> str:
        """
        Ideally, create a unique peer ID.
        Uses src_ip + src_port and MD5 hash -> hexadecimal string as an ID.
        """
        hash_string = self.src_ip + str(self.src_port)
        return hashlib.md5(hash_string.encode()).hexdigest()

    def file_strip(self, filename: str) -> str:
        """
        Strips the filename from directory path and escape characters.
        """
        return os.path.basename(filename)
        
class Piece:
    """
    Files are split into pieces.
    index -> piece's index in the expected buffer.
    """
    def __init__(self, index: int, data):
        self.index = index
        self.data = data

class PieceBuffer:
    """
    A piece manager that handles the current piece buffer for the requested file.
    """

    def __init__(self):
        self.__buffer = []
        self.__size = 0
        self.__have_pieces = []
    
    def get_buffer(self):
        return self.__buffer

    def set_buffer(self, length: int):
        """
        Initialize the piece buffer given the total number of pieces for the expected file.
        """
        self.__buffer = [0] * length
        self.__size = length
        self.__have_pieces = [False] * length

    def add_data(self, piece: Piece) -> int:
        idx = piece.index
        data = piece.data
        if 0 <= idx < self.__size:
            self.__buffer[idx] = data
            self.__have_pieces[idx] = True
            return 1
        return -1

    def get_data(self, idx: int):
        """
        Returns the piece bytes at the specified index.
        """
        if 0 <= idx < self.__size and self.__buffer[idx] != 0:
            return self.__buffer[idx]
        return -1
    
    def get_size(self) -> int:
        return self.__size

    def get_missing_pieces(self) -> list[int]:
        return [idx for idx, has_piece in enumerate(self.__have_pieces) if not has_piece]
    
    def check_if_have_piece(self, idx: int) -> bool:
        return self.__have_pieces[idx]
    
    def check_if_have_all_pieces(self) -> bool:
        return all(self.__have_pieces)
