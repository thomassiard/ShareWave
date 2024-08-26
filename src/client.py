from protocol import *
import file_handler as fd
import asyncio
import hashlib
import json
import sys

class Client:
    def __init__(self, src_ip, src_port):
        self.src_ip = src_ip  # IP adresa klijenta
        self.src_port = src_port  # Port klijenta
        self.peer_id = self.createPeerID()  # Jedinstveni identifikator klijenta
        self.tid = -1  # ID torrent-a (postavljen na -1 kao početna vrijednost)
        self.peer_choked = True  # Status klijenta (da li je "choked")
        self.peer_interested = False  # Status klijenta (da li je zainteresiran za torrent)
        self.peer_am_seeding = False  # Status klijenta (da li dijeli torrent)
        self.peer_am_leeching = False  # Status klijenta (da li preuzima torrent)
        self.seeders_list = {}  # Rječnik sa popisom seedera
        self.piece_buffer = PieceBuffer()  # Instanca za pohranu dijelova torrent-a

    ########### CONNECTION HANDLING ###########

    async def connectToTracker(self, ip="127.0.0.1", port=8888):
        try:
            return await asyncio.open_connection(ip, int(port))  # Povezivanje na tracker
        except ConnectionError:
            print("Connection Error: unable to connect to tracker.")  # Greška pri povezivanju
            sys.exit(-1)  # Izlazak iz programa

    async def connectToPeer(self, ip, port, request):
        try:
            print(f"Connecting to seeder at {ip}:{port} ...")  # Povezivanje na peer
            reader, writer = await asyncio.open_connection(ip, int(port))
            print(f"Connected as leecher: {self.src_ip}:{self.src_port}.")  # Povezivanje kao leech-er
            await self.send(writer, request)  # Slanje zahtjeva
            response = await self.receive(reader)  # Primanje odgovora
            writer.close()  # Zatvaranje veze
            return response
        except ConnectionError:
            print("Connection Error: unable to connect to peer.")  # Greška pri povezivanju s peer-om
            sys.exit(-1)  # Izlazak iz programa

    async def receiveRequest(self, reader, writer):
        try:
            data = await reader.read(READ_SIZE)  # Čitanje podataka
            peer_request = json.loads(data.decode())  # Dekodiranje podataka
            addr = writer.get_extra_info('peername')  # Dobivanje informacija o peer-u
            print(f"\n[PEER] Debug received {peer_request!r} from {addr!r}.")
            response = self.handlePeerRequest(peer_request)  # Obrada zahtjeva
            payload = json.dumps(response)  # Kodiranje odgovora
            print("[PEER] Debug send payload:", payload)
            writer.write(payload.encode())  # Slanje odgovora
            await writer.drain()  # Očekivanje da se svi podaci pošalju
            print("[PEER] Closing the connection for", addr)
        except:
            print("[PEER] Peer", writer.get_extra_info('peername'), "has disconnected.")  # Peer se isključio
        finally:
            writer.close()  # Zatvaranje veze

    async def startSeeding(self):
        server = await asyncio.start_server(self.receiveRequest, self.src_ip, self.src_port)  # Pokretanje servera za seeding
        if server:
            addr = server.sockets[0].getsockname()  # Dobivanje adrese servera
            print(f'[PEER] SEEDING !!! ... Serving on {addr}\n')
            async with server:
                try:
                    await server.serve_forever()  # Održavanje servera u funkciji
                except:
                    pass
                finally:
                    server.close()  # Zatvaranje servera
                    await server.wait_closed()  # Čekanje da se server zatvori

    async def receive(self, reader):
        data = await reader.read(READ_SIZE)  # Čitanje podataka
        payload = json.loads(data.decode())  # Dekodiranje podataka
        print(f'[PEER] Received decoded message: {payload!r}\n')
        opc = payload.get(FIELDS['OPC'])
        return await self.handleServerResponse(payload) if opc > 9 else self.handlePeerResponse(payload)  # Obrada odgovora

    async def send(self, writer, payload):
        json_payload = json.dumps(payload)  # Kodiranje podataka
        print("[PEER] Sending encoded request message:", json_payload)
        writer.write(json_payload.encode())  # Slanje podataka

    ########### REQUEST & RESPONSE HANDLING ###########

    async def handleServerResponse(self, response):
        ret = response[FIELDS['RET']]
        opc = response[FIELDS['OPC']]
        if ret == RET_FAIL:
            print("[PEER] RESPONSE: returned failed")  # Neuspješan odgovor
            return -1
        if ret == RET_ALREADY_SEEDING:
            print("[PEER] UPLOAD FAIL: You are already currently seeding a file.")  # Već dijelite datoteku
            return -1
        if ret == RET_NO_AVAILABLE_TORRENTS:
            print("[PEER] GET TORRENT LIST FAIL: There are no available torrents right now.")  # Nema dostupnih torrent-a
            return -1
        if ret == RET_TORRENT_DOES_NOT_EXIST:
            print("[PEER] GET TORRENT FAIL: The torrent ID does not exist")  # Torrent ID ne postoji
            return -1

        if opc == OPT_GET_LIST:
            self.displayTorrentList(response[FIELDS['TORRENT_LIST']])  # Prikaz popisa torrent-a
            return RET_SUCCESS
        if opc == OPT_GET_TORRENT:
            torrent = response[FIELDS['TORRENT']]
            self.peer_am_leeching = True  # Postavka klijenta kao leech-er
            self.seeders_list = torrent[FIELDS['SEEDER_LIST']]  # Ažuriranje popisa seedera
            self.piece_buffer.setBuffer(torrent[FIELDS['TOTAL_PIECES']])  # Postavka bafera za dijelove
            await self.downloadFile(torrent[FIELDS['TOTAL_PIECES']], torrent[FIELDS['FILE_NAME']])  # Preuzimanje datoteke
            return RET_FINISHED_DOWNLOAD
        if opc in (OPT_START_SEED, OPT_UPLOAD_FILE):
            self.peer_am_leeching = False  # Postavka klijenta kao seeder
            self.peer_am_seeding = True
            self.tid = response[FIELDS['TID']]  # Postavka ID-a torrent-a
            await self.startSeeding()  # Pokretanje dijeljenja
            return RET_FINISHED_SEEDING
        if opc == OPT_STOP_SEED:
            self.peer_am_seeding = False  # Zaustavljanje dijeljenja
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
            payload[FIELDS['TID']] = torrent_id  # Dodavanje ID-a torrent-a
        elif opc == OPT_UPLOAD_FILE:
            num_pieces = self.uploadFile(filename)  # Preuzimanje broja dijelova
            if num_pieces == 0:
                return {}
            payload.update({
                FIELDS['FILE_NAME']: self.fileStrip(filename),  # Dodavanje imena datoteke
                FIELDS['TOTAL_PIECES']: num_pieces  # Dodavanje ukupnog broja dijelova
            })
        return payload

    def handlePeerResponse(self, response):
        ret = response[FIELDS['RET']]
        opc = response[FIELDS['OPC']]
        if ret in (RET_FAIL, RET_SUCCESS):
            if opc == OPT_GET_PEERS:
                self.seeders_list = response[FIELDS['PEER_LIST']]  # Ažuriranje popisa seedera
            elif opc == OPT_GET_PIECE:
                data = response[FIELDS['PIECE_DATA']]
                idx = response[FIELDS['PIECE_IDX']]
                self.piece_buffer.addData(Piece(idx, data))  # Dodavanje podataka o dijelu u bafer
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
            payload[FIELDS['PIECE_IDX']] = piece_idx  # Dodavanje indeksa dijela
        return payload

    ########### HELPER FUNCTIONS ###########

    async def downloadFile(self, num_pieces, filename):
        await self.evenPeerSelection(num_pieces)  # Odabir peer-ova
        while not self.piece_buffer.checkIfHaveAllPieces():  # Provjera da li su svi dijelovi preuzeti
            await asyncio.sleep(1)  # Izbjegavanje preopterećenja

        pieces_to_file = [self.piece_buffer.getData(i) for i in range(self.piece_buffer.getSize())]  # Prikupljanje svih dijelova
        output_dir = f'output/{self.peer_id}_{filename}'  # Određivanje izlazne putanje
        try:
            fd.decodeToFile(pieces_to_file, output_dir)  # Dekodiranje u datoteku
            print(f"[PEER] Successfully downloaded file: {output_dir}")
        except Exception as e:
            print(f"Exception occurred in downloadFile() with filename: {filename}. Error: {e}")  # Greška pri preuzimanju datoteke

    def uploadFile(self, filename):
        try:
            pieces, num_pieces = fd.encodeToBytes(filename)  # Kodiranje datoteke u dijelove
            self.piece_buffer.setBuffer(num_pieces)  # Postavka bafera za dijelove
            for idx, piece in enumerate(pieces):
                self.piece_buffer.addData(Piece(idx, piece))  # Dodavanje dijelova u bafer
            return num_pieces
        except Exception as e:
            print(f"Exception occurred in uploadFile() with filename: '{filename}', please check your filename or directory. Error: {e}")  # Greška pri uploadu datoteke
            return 0

    def createPeerID(self):
        return hashlib.md5(f"{self.src_ip}{self.src_port}".encode()).hexdigest()  # Kreiranje jedinstvenog identifikatora klijenta

    def fileStrip(self, filename):
        return filename.split('/')[-1]  # Uklanjanje putanje iz imena datoteke
    
    async def evenPeerSelection(self, num_pieces):
        # Prikupite listu nedostajućih dijelova
        missing_pieces = self.piece_buffer.getMissingPieces()
        
        # Povežite se s peer-ovima za svaki nedostajući dio
        for piece_idx in missing_pieces:
            # Ako je broj nedostajućih dijelova veliki, možda želite ograničiti broj paralelnih veza
            for peer_id, peer_info in self.seeders_list.items():
                ip = peer_info['IP_ADDRESS']
                port = peer_info['PORT']
                
                # Kreirajte zahtjev za preuzimanje dijelova
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
        self.index = index  # Indeks dijela
        self.data = data  # Podaci dijela

class PieceBuffer:
    def __init__(self):
        self.buffer = []  # Bafer za dijelove
        self.size = 0  # Veličina bafera
        self.have_pieces = []  # Popis koji označava koje dijelove imamo

    def setBuffer(self, length):
        self.buffer = [0] * length  # Inicijalizacija bafera
        self.size = length
        self.have_pieces = [False] * length  # Inicijalizacija popisa dostupnih dijelova

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
        return [idx for idx, have in enumerate(self.have_pieces) if not have]  # Povratak popisa nedostajućih dijelova

    def checkIfHavePiece(self, idx):
        return self.have_pieces[idx]  # Provjera da li imamo dio s određenim indeksom

    def checkIfHaveAllPieces(self):
        return all(self.have_pieces)  # Provjera da li imamo sve dijelove
