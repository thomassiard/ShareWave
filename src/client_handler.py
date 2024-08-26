# Klasa za rukovanje korisničkim unosima i povezivanje s trackerom.
from client import *
from protocol import RET_FINISHED_SEEDING, RET_FINISHED_DOWNLOAD, RET_SUCCESS
import asyncio
import sys

def handleUserChoice(): # Funkcija za rukovanje korisničkim unosima
    while True:
        print("\nChoose an option: ")
        print("[1] Show torrent list")
        print("[2] Download Torrent")
        print("[3] Upload a new file")
        print("[4] Help")
        print("[5] Exit")
        userInput = input("[ShareWave client]: ")

        try:
            userInput = int(userInput)

            if userInput in range(1, 6):
                if userInput == 1:
                    # Prikaži popis torrent-a
                    return [OPT_GET_LIST, None, None]  # Vraća opciju za prikaz popisa torrent-a

                elif userInput == 2:
                    # Preuzmi torrent
                    torrent_id = int(input("[ShareWave client] Enter torrent ID: "))  # Unos ID-a torrenta
                    return [OPT_GET_TORRENT, torrent_id, None]  # Vraća opciju za preuzimanje torrenta

                elif userInput == 3:
                    # Postavi novu datoteku
                    filename = str(input("[ShareWave client] Enter filename with extension: "))  # Unos imena datoteke
                    return [OPT_UPLOAD_FILE, None, filename]  # Vraća opciju za upload nove datoteke

                elif userInput == 4:
                    # Pomoć
                    print("\n///////////////////////////////////////////////////////////////////////////////////////////////////\n")
                    print("[1] Show torrent list:")
                    print("\t - This option allows you to get a list of torrents and their IDs (TID)\n")

                    print("[2] Download Torrent:")
                    print("\t - Choose a torrent ID (TID) from the list [1] to start downloading the file\n")

                    print("[3] Upload a new file:")
                    print("\t - Choose a file in the format: [filename].[extension], to add it to the list of torrents.")
                    print("\t - You will start sharing this file")
                    print("\n///////////////////////////////////////////////////////////////////////////////////////////////////\n")
                    input("Press enter to continue...")
                    return [0, None, None]  # Vraća opciju za pomoć, bez promjena

                elif userInput == 5:
                    # Izlaz
                    return [-1, None, None]  # Vraća opciju za izlaz iz programa

            else:
                print("Invalid input. Please try again.")  # Nevažeći unos

        except ValueError:
            print("Invalid input, only integers are allowed.")  # Greška u unosu

def parseCommandLine(): # Funkcija za parsiranje argumenata naredbenog retka

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
            asyncio.streams.socket.inet_aton(src_ip)  # Provjera ispravnosti IP adrese
            asyncio.streams.socket.inet_aton(dest_ip)
        except asyncio.streams.socket.error:
            print("Invalid format for source or tracker IP address, please try again.")  # Greška u formatu IP adrese
            return None, None, None, None

        try:
            if int(src_port) not in range(0, 65536) or int(dest_port) not in range(0, 65536):
                print("Port range must be [0, 65535], please try again.")  # Greška u rasponu portova
                return None, None, None, None
        except ValueError:
            print("Invalid format for source or tracker port, please try again.")  # Greška u formatu porta

    elif args == 2:
        src_ip = sys.argv[1]
        src_port = sys.argv[2]

        try:
            asyncio.streams.socket.inet_aton(src_ip)  # Provjera ispravnosti IP adrese
        except asyncio.streams.socket.error:
            print("Invalid format for source or tracker IP address, please try again.")  # Greška u formatu IP adrese
            return None, None, None, None

        try:
            if int(src_port) not in range(0, 65536):
                print("Port range must be [0, 65535], please try again.")  # Greška u rasponu portova
                return None, None, None, None
        except ValueError:
            print("Invalid format for source port, please try again.")  # Greška u formatu porta
        
    else:
        print("Please check your arguments:")  # Upute za ispravan unos argumenata
        print("client_handler.py [source IP] [source port] [tracker IP] [tracker port]")

    return src_ip, src_port, dest_ip, dest_port

async def main(): # Glavna funkcija za pokretanje klijenta, povezivanje s trackerom i rukovanje korisničkim unosima.
    src_ip, src_port, dest_ip, dest_port = parseCommandLine()

    if src_ip is not None and src_port is not None:
        cli = Client(src_ip, src_port)  # Kreiranje instance klijenta

        if dest_ip is None and dest_port is None:
            # Koristi zadani IP i port ako nisu navedeni
            dest_ip = "127.0.0.1"
            dest_port = "8888"

        print("Connecting to tracker at " + dest_ip + ":" + dest_port + " ...")
        print("Connecting as client: " + src_ip + ":" + src_port + " ...")

        while True:
            reader, writer = await cli.connectToTracker(dest_ip, dest_port)  # Povezivanje s trackerom

            argList = handleUserChoice()  # Dobivanje korisničkog izbora

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
        asyncio.run(main())  # Pokretanje glavne funkcije
    except KeyboardInterrupt:
        print("Exiting the program.")
