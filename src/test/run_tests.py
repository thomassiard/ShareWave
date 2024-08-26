import sys
import os

# Dodajte 'src' u sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from client import Client
from tracker import TrackerServer
from protocol import FIELDS, OPT_GET_LIST, OPT_GET_TORRENT, OPT_GET_PEERS, OPT_GET_PIECE, RET_SUCCESS, RET_NO_AVAILABLE_TORRENTS

def test_createServerRequest():
    ip = '127.0.0.2'
    port = '8080'
    cli = Client(ip, port)
    peer_id = cli.createPeerID()
    opc = OPT_GET_TORRENT
    tid = 0
    expectedPayload = {
        FIELDS['OPC']: opc,
        FIELDS['IP']: ip,
        FIELDS['PORT']: port,
        FIELDS['PID']: peer_id,
        FIELDS['TID']: tid
    }
    actualPayload = cli.createServerRequest(opc=opc, torrent_id=tid)
    assert actualPayload == expectedPayload

def test_handleServerRequest():
    tracker = TrackerServer()
    opc = OPT_GET_LIST
    ip = '127.0.0.2'
    port = '8080'
    peer_id = 'test'
    tid = 0
    requestPayload = {
        FIELDS['OPC']: opc,
        FIELDS['IP']: ip,
        FIELDS['PORT']: port,
        FIELDS['PID']: peer_id,
        FIELDS['TID']: tid
    }
    expectedPayload = {
        FIELDS['OPC']: opc,
        FIELDS['RET']: RET_NO_AVAILABLE_TORRENTS,
        FIELDS['TORRENT_LIST']: []  # Dodajte ovu liniju
    }
    actualPayload = tracker.handleRequest(requestPayload)
    assert actualPayload == expectedPayload

def test_createPeerRequest():
    ip = '127.0.0.2'
    port = '8080'
    cli = Client(ip, port)
    opc = OPT_GET_PIECE
    piece_idx = 0
    expectedPayload = {
        FIELDS['OPC']: opc,
        FIELDS['IP']: ip,
        FIELDS['PORT']: port,
        FIELDS['PIECE_IDX']: piece_idx
    }
    actualPayload = cli.createPeerRequest(opc=opc, piece_idx=piece_idx)
    assert actualPayload == expectedPayload

def test_handlePeerRequest():
    ip = '127.0.0.2'
    port = '8080'
    cli = Client(ip, port)
    opc = OPT_GET_PEERS
    requestPayload = {
        FIELDS['OPC']: opc,
        FIELDS['IP']: ip,
        FIELDS['PORT']: port,
    }
    expectedResponse = {
        FIELDS['OPC']: opc,
        FIELDS['IP']: ip,
        FIELDS['PORT']: port,
        FIELDS['PEER_LIST']: {},
        FIELDS['RET']: RET_SUCCESS
    }
    actualResponse = cli.handlePeerRequest(requestPayload)
    assert actualResponse == expectedResponse
