from protocol import *
import file_handler as fd
import asyncio
import hashlib
import json
import sys

class Client:
    def __init__(self, src_ip, src_port):
        self.src_ip = src_ip
        self.src_port = src_port
        self.peer_id = self.createPeerID()
        self.tid = -1
        self.peer_choked = True
        self.peer_interested = False
        self.peer_am_seeding = False
        self.peer_am_leeching = False
        self.seeders_list = {}
        self.piece_buffer = PieceBuffer()

    ########### CONNECTION HANDLING ###########

    async def connectToTracker(self, ip="127.0.0.1", port=8888):
        try:
            return await asyncio.open_connection(ip, int(port))
        except ConnectionError:
            print("Connection Error: unable to connect to tracker.")
            sys.exit(-1)

    async def connectToPeer(self, ip, port, request):
        try:
            print(f"Connecting to seeder at {ip}:{port} ...")
            reader, writer = await asyncio.open_connection(ip, int(port))
            print(f"Connected as leecher: {self.src_ip}:{self.src_port}.")
            await self.send(writer, request)
            response = await self.receive(reader)
            writer.close()
            return response
        except ConnectionError:
            print("Connection Error: unable to connect to peer.")
            sys.exit(-1)

    async def receiveRequest(self, reader, writer):
        try:
            data = await reader.read(READ_SIZE)
            peer_request = json.loads(data.decode())
            addr = writer.get_extra_info('peername')
            print(f"\n[PEER] Debug received {peer_request!r} from {addr!r}.")
            response = self.handlePeerRequest(peer_request)
            payload = json.dumps(response)
            print("[PEER] Debug send payload:", payload)
            writer.write(payload.encode())
            await writer.drain()
            print("[PEER] Closing the connection for", addr)
        except:
            print("[PEER] Peer", writer.get_extra_info('peername'), "has disconnected.")
        finally:
            writer.close()

    async def startSeeding(self):
        server = await asyncio.start_server(self.receiveRequest, self.src_ip, self.src_port)
        if server:
            addr = server.sockets[0].getsockname()
            print(f'[PEER] SEEDING !!! ... Serving on {addr}\n')
            async with server:
                try:
                    await server.serve_forever()
                except:
                    pass
                finally:
                    server.close()
                    await server.wait_closed()

    async def receive(self, reader):
        data = await reader.read(READ_SIZE)
        payload = json.loads(data.decode())
        print(f'[PEER] Received decoded message: {payload!r}\n')
        opc = payload.get(FIELDS['OPC'])
        return await self.handleServerResponse(payload) if opc > 9 else self.handlePeerResponse(payload)

    async def send(self, writer, payload):
        json_payload = json.dumps(payload)
        print("[PEER] Sending encoded request message:", json_payload)
        writer.write(json_payload.encode())

    ########### REQUEST & RESPONSE HANDLING ###########

    async def handleServerResponse(self, response):
        ret = response[FIELDS['RET']]
        opc = response[FIELDS['OPC']]
        if ret == RET_FAIL:
            print("[PEER] RESPONSE: returned failed")
            return -1
        if ret == RET_ALREADY_SEEDING:
            print("[PEER] UPLOAD FAIL: You are already currently seeding a file.")
            return -1
        if ret == RET_NO_AVAILABLE_TORRENTS:
            print("[PEER] GET TORRENT LIST FAIL: There are no available torrents right now.")
            return -1
        if ret == RET_TORRENT_DOES_NOT_EXIST:
            print("[PEER] GET TORRENT FAIL: The torrent ID does not exist")
            return -1

        if opc == OPT_GET_LIST:
            self.displayTorrentList(response[FIELDS['TORRENT_LIST']])
            return RET_SUCCESS
        if opc == OPT_GET_TORRENT:
            torrent = response[FIELDS['TORRENT']]
            self.peer_am_leeching = True
            self.seeders_list = torrent[FIELDS['SEEDER_LIST']]
            self.piece_buffer.setBuffer(torrent[FIELDS['TOTAL_PIECES']])
            await self.downloadFile(torrent[FIELDS['TOTAL_PIECES']], torrent[FIELDS['FILE_NAME']])
            return RET_FINISHED_DOWNLOAD
        if opc in (OPT_START_SEED, OPT_UPLOAD_FILE):
            self.peer_am_leeching = False
            self.peer_am_seeding = True
            self.tid = response[FIELDS['TID']]
            await self.startSeeding()
            return RET_FINISHED_SEEDING
        if opc == OPT_STOP_SEED:
            self.peer_am_seeding = False
            return RET_FINISHED_SEEDING

        return 1

    def displayTorrentList(self, torrent_list):
        print("\n///////////////////////////////////////////////////////////////////////////////////////////////////\n")
        print("TID \t FILE_NAME \t TOTAL_PIECES \t SEEDERS \t")
        print("--- \t -------- \t ------------ \t ------- \t")
        for torrent in torrent_list:
            print(f"{torrent[FIELDS['TID']]} \t {torrent[FIELDS['FILE_NAME']]} \t {torrent[FIELDS['TOTAL_PIECES']]} \t\t {torrent[FIELDS['SEEDER_LIST']]}")
        print("\n///////////////////////////////////////////////////////////////////////////////////////////////////\n")

    def createServerRequest(self, opc, torrent_id=None, filename=None):
        payload = {
            FIELDS['OPC']: opc,
            FIELDS['IP']: self.src_ip,
            FIELDS['PORT']: self.src_port,
            FIELDS['PID']: self.peer_id
        }
        if opc in (OPT_GET_TORRENT, OPT_START_SEED, OPT_STOP_SEED):
            payload[FIELDS['TID']] = torrent_id
        elif opc == OPT_UPLOAD_FILE:
            num_pieces = self.uploadFile(filename)
            if num_pieces == 0:
                return {}
            payload.update({
                FIELDS['FILE_NAME']: self.fileStrip(filename),
                FIELDS['TOTAL_PIECES']: num_pieces
            })
        return payload

    def handlePeerResponse(self, response):
        ret = response[FIELDS['RET']]
        opc = response[FIELDS['OPC']]
        if ret in (RET_FAIL, RET_SUCCESS):
            if opc == OPT_GET_PEERS:
                self.seeders_list = response[FIELDS['PEER_LIST']]
            elif opc == OPT_GET_PIECE:
                data = response[FIELDS['PIECE_DATA']]
                idx = response[FIELDS['PIECE_IDX']]
                self.piece_buffer.addData(Piece(idx, data))
            return 1
        return -1

    def handlePeerRequest(self, request):
        opc = request[FIELDS['OPC']]
        response = {
            FIELDS['OPC']: opc,
            FIELDS['IP']: self.src_ip,
            FIELDS['PORT']: self.src_port
        }
        if opc == OPT_GET_PEERS:
            response.update({FIELDS['PEER_LIST']: self.seeders_list, FIELDS['RET']: RET_SUCCESS})
        elif opc == OPT_GET_PIECE:
            piece_idx = request[FIELDS['PIECE_IDX']]
            if self.piece_buffer.checkIfHavePiece(piece_idx):
                response.update({
                    FIELDS['PIECE_DATA']: self.piece_buffer.getData(piece_idx),
                    FIELDS['PIECE_IDX']: piece_idx,
                    FIELDS['RET']: RET_SUCCESS
                })
            else:
                response[FIELDS['RET']] = RET_FAIL
        return response

    def createPeerRequest(self, opc, piece_idx=None):
        payload = {
            FIELDS['OPC']: opc,
            FIELDS['IP']: self.src_ip,
            FIELDS['PORT']: self.src_port
        }
        if opc == OPT_GET_PIECE:
            payload[FIELDS['PIECE_IDX']] = piece_idx
        return payload

    ########### HELPER FUNCTIONS ###########

    async def downloadFile(self, num_pieces, filename):
        await self.evenPeerSelection(num_pieces)
        while not self.piece_buffer.checkIfHaveAllPieces():
            await asyncio.sleep(1)  # Avoid a tight loop
        
        pieces_to_file = [self.piece_buffer.getData(i) for i in range(self.piece_buffer.getSize())]
        output_dir = f'output/{self.peer_id}_{filename}'
        try:
            fd.decodeToFile(pieces_to_file, output_dir)
            print(f"[PEER] Successfully downloaded file: {output_dir}")
        except Exception as e:
            print(f"Exception occurred in downloadFile() with filename: {filename}. Error: {e}")

    def uploadFile(self, filename):
        try:
            pieces, num_pieces = fd.encodeToBytes(filename)
            self.piece_buffer.setBuffer(num_pieces)
            for idx, piece in enumerate(pieces):
                self.piece_buffer.addData(Piece(idx, piece))
            return num_pieces
        except Exception as e:
            print(f"Exception occurred in uploadFile() with filename: '{filename}', please check your filename or directory. Error: {e}")
            return 0

    def createPeerID(self):
        return hashlib.md5(f"{self.src_ip}{self.src_port}".encode()).hexdigest()

    def fileStrip(self, filename):
        return filename.split('/')[-1]  # Simplified stripping of the filename
    
    async def evenPeerSelection(self, num_pieces):
        # Prikupite listu nedostajućih delova
        missing_pieces = self.piece_buffer.getMissingPieces()
        
        # Povežite se sa peer-ovima za svaki nedostajući deo
        for piece_idx in missing_pieces:
            # Ako je broj nedostajućih delova veliki, možda želite ograničiti broj paralelnih veza
            for peer_id, peer_info in self.seeders_list.items():
                ip = peer_info['IP_ADDRESS']
                port = peer_info['PORT']
                
                # Kreirajte zahtev za preuzimanje delova
                request = self.createPeerRequest(OPT_GET_PIECE, piece_idx)
                
                try:
                    response = await self.connectToPeer(ip, port, request)
                    if response[FIELDS['RET']] == RET_SUCCESS:
                        print(f"Piece {piece_idx} successfully received from {ip}:{port}")
                    else:
                        print(f"Failed to receive piece {piece_idx} from {ip}:{port}")
                except Exception as e:
                    print(f"Exception occurred while receiving piece {piece_idx} from {ip}:{port}. Error: {e}")

class Piece:
    def __init__(self, index, data):
        self.index = index
        self.data = data

class PieceBuffer:
    def __init__(self):
        self.buffer = []
        self.size = 0
        self.have_pieces = []

    def setBuffer(self, length):
        self.buffer = [0] * length
        self.size = length
        self.have_pieces = [False] * length

    def addData(self, piece):
        idx = piece.index
        if 0 <= idx < self.size:
            self.buffer[idx] = piece.data
            self.have_pieces[idx] = True
            return 1
        return -1

    def getData(self, idx):
        if 0 <= idx < self.size and self.buffer[idx] != 0:
            return self.buffer[idx]
        return -1

    def getSize(self):
        return self.size

    def getMissingPieces(self):
        return [idx for idx, have in enumerate(self.have_pieces) if not have]

    def checkIfHavePiece(self, idx):
        return self.have_pieces[idx]

    def checkIfHaveAllPieces(self):
        return all(self.have_pieces)
