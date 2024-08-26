"""
Klasa za rukovanje korisničkim unosima i povezivanje s trackerom.
"""

from client import *
from protocol import RET_FINISHED_SEEDING, RET_FINISHED_DOWNLOAD, RET_SUCCESS, RET_FAIL, RET_ALREADY_SEEDING, RET_NO_AVAILABLE_TORRENTS, RET_TORRENT_DOES_NOT_EXIST
import asyncio
import sys

def handleUserChoice():
    """
    Rukuje korisničkim izborom putem konzole.
    
    :return: Lista s odabranom opcijom, torrent ID-om i imenom datoteke
    """
    while True:
        print("\nOdaberite opciju: ")
        print("[1] Prikaži popis torrent-a")
        print("[2] Preuzmi Torrent")
        print("[3] Postavi novu datoteku")
        print("[4] Pomoć")
        print("[5] Izlaz")
        userInput = input("[p2py client]: ")

        try:
            userInput = int(userInput)

            if userInput in range(1, 6):
                if userInput == 1:
                    # Prikaži popis torrent-a
                    return [OPT_GET_LIST, None, None]

                elif userInput == 2:
                    # Preuzmi torrent
                    torrent_id = int(input("[p2py client] Unesite ID torrent-a: "))
                    return [OPT_GET_TORRENT, torrent_id, None]

                elif userInput == 3:
                    # Postavi novu datoteku
                    filename = str(input("[p2py client] Unesite ime datoteke s ekstenzijom: "))
                    return [OPT_UPLOAD_FILE, None, filename]

                elif userInput == 4:
                    # Pomoć
                    print("\n///////////////////////////////////////////////////////////////////////////////////////////////////\n")
                    print("[1] Prikaži popis torrent-a:")
                    print("\t - Ova opcija omogućuje vam da dobijete popis torrent-a i njihove ID-eve (TID)\n")

                    print("[2] Preuzmi Torrent:")
                    print("\t - Odaberite ID torrent-a (TID) s popisa [1] da biste započeli preuzimanje datoteke\n")

                    print("[3] Postavi novu datoteku:")
                    print("\t - Odaberite datoteku u formatu: [ime_datoteke].[ekstenzija], da biste je dodali na popis torrent-a.")
                    print("\t - Počet ćete dijeliti ovu datoteku")
                    print("\n///////////////////////////////////////////////////////////////////////////////////////////////////\n")
                    input("Pritisnite enter za nastavak...")
                    return [0, None, None]

                elif userInput == 5:
                    # Izlaz
                    return [-1, None, None]

            else:
                print("Nevažeći unos. Molimo pokušajte ponovo.")
        except ValueError:
            print("Nevažeći unos, dopuštene su samo cijele brojeve.")

def parseCommandLine():
    """
    Parsira argumente naredbenog retka za IP adrese i portove.
    
    :return: Izvorni IP, izvorni port, odredišni IP i odredišni port
    """
    src_ip = None
    src_port = None
    dest_ip = None
    dest_port = None
    args = len(sys.argv) - 1

    if args == 4:
        src_ip = sys.argv[1]
        src_port = sys.argv[2]
        dest_ip = sys.argv[3]
        dest_port = sys.argv[4]

        try:
            asyncio.streams.socket.inet_aton(src_ip)
            asyncio.streams.socket.inet_aton(dest_ip)
        except asyncio.streams.socket.error:
            print("Neispravan format za IP adresu izvora ili trackera, molimo pokušajte ponovo.")
            return None, None, None, None

        try:
            if int(src_port) not in range(0, 65536) or int(dest_port) not in range(0, 65536):
                print("Raspon portova mora biti [0, 65535], molimo pokušajte ponovo.")
                return None, None, None, None
        except ValueError:
            print("Neispravan format za port izvora ili trackera, molimo pokušajte ponovo.")

    elif args == 2:
        src_ip = sys.argv[1]
        src_port = sys.argv[2]

        try:
            asyncio.streams.socket.inet_aton(src_ip)
        except asyncio.streams.socket.error:
            print("Neispravan format za IP adresu izvora ili trackera, molimo pokušajte ponovo.")
            return None, None, None, None

        try:
            if int(src_port) not in range(0, 65536):
                print("Raspon portova mora biti [0, 65535], molimo pokušajte ponovo.")
                return None, None, None, None
        except ValueError:
            print("Neispravan format za port izvora, molimo pokušajte ponovo.")
        
    else:
        print("Molimo provjerite argumente:")
        print("client_handler.py [izvorni IP] [izvorni port] [tracker IP] [tracker port]")

    return src_ip, src_port, dest_ip, dest_port

async def main():
    """
    Glavna funkcija za pokretanje klijenta, povezivanje s trackerom i rukovanje korisničkim unosima.
    """
    src_ip, src_port, dest_ip, dest_port = parseCommandLine()

    if src_ip is not None and src_port is not None:
        cli = Client(src_ip, src_port)

        if dest_ip is None and dest_port is None:
            # Koristi zadani IP i port ako nisu navedeni
            dest_ip = "127.0.0.1"
            dest_port = "8888"

        print("Povezivanje s trackerom na " + dest_ip + ":" + dest_port + " ...")
        print("Povezivanje kao klijent: " + src_ip + ":" + src_port + " ...")

        while True:
            reader, writer = await cli.connectToTracker(dest_ip, dest_port)

            argList = handleUserChoice()

            if argList[0] > 0:
                # Stvaranje zahtjeva za server
                payload = cli.createServerRequest(opc=argList[0], torrent_id=argList[1], filename=argList[2])

                # Provjera valjanosti payload-a
                if not payload:
                    continue

                # Slanje poruke serveru
                await cli.send(writer, payload)

                # Primanje odgovora od servera
                result = await cli.receive(reader)

                if result == RET_FINISHED_DOWNLOAD:
                    writer.close()  # Zatvori trenutnu sesiju, zatim pokreni novu
                    reader, writer = await cli.connectToTracker(dest_ip, dest_port)
                    payload = cli.createServerRequest(opc=OPT_START_SEED, torrent_id=argList[1])
                    await cli.send(writer, payload)
                    result = await cli.receive(reader)
                    writer.close()
                    
                if result == RET_FINISHED_SEEDING:
                    writer.close()  # Zatvori trenutnu sesiju, zatim pokreni novu
                    reader, writer = await cli.connectToTracker(dest_ip, dest_port)
                    payload = cli.createServerRequest(opc=OPT_STOP_SEED, torrent_id=cli.tid)
                    await cli.send(writer, payload)  # Pošalji poruku trackeru
                    result = await cli.receive(reader)
                    writer.close()
                    break

                if result != RET_SUCCESS:
                    writer.close()

            elif argList[0] == 0:
                # Pomoć
                writer.close()

            else:
                # Izlaz
                writer.close()
                sys.exit(0)

        writer.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Izlaz iz programa.")
