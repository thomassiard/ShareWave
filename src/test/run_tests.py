import sys
import os

# Dodavanje putanje do direktorija izvan trenutnog direktorija
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# Uvoz potrebnih modula
from client import Client
from tracker import TrackerServer
from protocol import *

def test_createServerRequest():
    ip = '127.0.0.2'
    port = '8080'
    cli = Client(ip, port) # Kreiranje instancije Client klase
    peer_id = cli.createPeerID() # Generiranje jedinstvenog ID-a za peer
    opc = OPT_GET_TORRENT # Definiranje opcije i ID-a torrenta za testiranje
    tid = 0
    
    # Očekivani payload za zahtjev
    expectedPayload = {
        FIELDS['OPC']: opc,             # Opcija zahtjeva
        FIELDS['IP']: ip,               # IP adresa
        FIELDS['PORT']: port,           # Port
        FIELDS['PID']: peer_id,         # ID peera
        FIELDS['TID']: tid              # ID torrenta
    }
    
    actualPayload = cli.createServerRequest(opc=opc, torrent_id=tid) # Kreiranje stvarnog payloada pomoću metode iz Client klase
    assert actualPayload == expectedPayload # Provjera da li stvarni payload odgovara očekivanom

def test_handleServerRequest():
    tracker = TrackerServer()
    
    # Definiranje opcije i podataka za zahtjev
    opc = OPT_GET_LIST
    ip = '127.0.0.2'
    port = '8080'
    peer_id = 'test'
    tid = 0
    
    # Payload zahtjeva za TrackerServer
    requestPayload = {
        FIELDS['OPC']: opc,      
        FIELDS['IP']: ip,      
        FIELDS['PORT']: port,    
        FIELDS['PID']: peer_id,     
        FIELDS['TID']: tid         
    }
    
    # Očekivani payload za odgovor
    expectedPayload = {
        FIELDS['OPC']: opc,                     # Opcija zahtjeva
        FIELDS['RET']: RET_NO_AVAILABLE_TORRENTS, # Povratni kod za nedostupne torrente
        FIELDS['TORRENT_LIST']: []              # Lista torrenta (prazan)
    }
    
    actualPayload = tracker.handleRequest(requestPayload) # Dobivanje stvarnog odgovora pomoću metode iz TrackerServer klase
    assert actualPayload == expectedPayload # Provjera da li stvarni odgovor odgovara očekivanom

def test_createPeerRequest():
    ip = '127.0.0.2'
    port = '8080'
    cli = Client(ip, port)
    
    # Definiranje opcije i indeksa dijela za zahtjev
    opc = OPT_GET_PIECE
    piece_idx = 0
    
    # Očekivani payload za zahtjev
    expectedPayload = {
        FIELDS['OPC']: opc,             # Opcija zahtjeva
        FIELDS['IP']: ip,               # IP adresa
        FIELDS['PORT']: port,           # Port
        FIELDS['PIECE_IDX']: piece_idx  # Indeks dijela
    }
    
    actualPayload = cli.createPeerRequest(opc=opc, piece_idx=piece_idx) # Kreiranje stvarnog payloada pomoću metode iz Client klase
    assert actualPayload == expectedPayload # Provjera da li stvarni payload odgovara očekivanom

def test_handlePeerRequest():
    ip = '127.0.0.2'
    port = '8080'
    cli = Client(ip, port)
    
    # Definiranje opcije za zahtjev
    opc = OPT_GET_PEERS
    
    # Payload zahtjeva za Client
    requestPayload = {
        FIELDS['OPC']: opc,          
        FIELDS['IP']: ip,           
        FIELDS['PORT']: port       
    }
    
    # Očekivani odgovor
    expectedResponse = {
        FIELDS['OPC']: opc,             # Opcija zahtjeva
        FIELDS['IP']: ip,               # IP adresa
        FIELDS['PORT']: port,           # Port
        FIELDS['PEER_LIST']: {},        # Lista peera (prazna)
        FIELDS['RET']: RET_SUCCESS      # Povratni kod za uspjeh
    }
    
    actualResponse = cli.handlePeerRequest(requestPayload) # Dobivanje stvarnog odgovora pomoću metode iz Client klase
    assert actualResponse == expectedResponse # Provjera da li stvarni odgovor odgovara očekivanom
