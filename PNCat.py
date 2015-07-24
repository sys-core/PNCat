import sys
import socket
import getopt
import threading
import subprocess


# définire quelque variables globales
ecouter     = False
commande    = False
charger     = False
executer    = ""
charger_destination = ""
port        = 0
cible       = ""


def usage():
    print "PNCat outil réseau"
    print
    print "Usage: PNCat.py -t hôte_cible -p port"
    
    print "-l --ecouter        -ecouter sur l\'[hôte]:[port] pour les connections entrantes"
    print "-e --exécuter=fichier_à_exécuter   - exécuter le fichier offert lors de la réception d'une connexion"
    print "-c --commande        _initialise le Shell de commandes"
    print "- --charger=déstination   -sur une connexion réçue, charge un fichier et écrit dans la déstination"
    print
    print
    print "Exemples"
    print "PNCat.py -t 192.168.1.1 -p 5555 -l -c"
    print "PNCat.py -t 192.168.1.1 -p 5555 -l -u=c:\\cible.exe"
    print "PNCat.py -t 192.168.1.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./PNCat.py -t 192.168.11.12 -p 135"
    sys.exit(0)
    
    def client_sender(tampon):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            #se connecterà notre hôte cible
            client.connect((cible,port))
            if len(tampon):
                client.send(tampon)
                
                while True:
                    #maintenant attendre l'arrivée des données
                    recv_len = 1
                    reponse = ""
                    
                    while recv_len:
                        donnee = client.recv(4096)
                        recv_len = len(donnee)
                        reponse+= donnee
                        if recv_len < 4096:
                            break
                    print reponse,
                    
                    #attendre pour plus d'entrée
                    tampon = raw_input("")
                    tampon+= "\n"
                    
                    client.send(tampon)
                
        except:
              print "[*] Exception! Sortir."
                    #démanteler la connexion
              client.close()
    def server_loop():
        global cible
        #si aucune cible n'est définie, nous écoutons sur toute les interfaces
        if not len(cible):
            cible = "0.0.0.0"
        
        serveur = socket.socket(socket.AF_NET, socket.SOCK_STREAM)
        serveur.bind((cible,port))
        serveur.listen(5)
        
        while True:
            client_socket, addr = server.accept()
            
            #séparer un thread pour gérer un nouveau client
            client_thread = threading.Thread(cible=client_handler,args=(client_socket,))
            client_thread.start()
    def run_command(commande):
        #réduire la nouvelle ligne
        commande = command.rstrip()
        
        #éxecuter la commande et obtenir la sortie de retour
        try:
            sortie = sybprocess.check_output(commande,stderr=subprocess.STDOUT, shell=True)
        except:
                sortie = "Echec d'exécuter la commande.\r\n"
            
            #envoie du retour de la sortie au client
        return sortie
        
    def client_handler(client_socket):
        global charger
        global executer
        global commande
        #vérifier le chargement
        if len(charger_destination):
            #lire dans tous les octets et écrire dans notre déstination
            fichier_tampon = ""
            #conserver les données de lecture jusqu'à ce qu'aucune ne soit disponible
            
            while True:
                donnee = client_socket.recv(1024)
                
                if not donnee:
                    break
                else:
                    fichier_tampon += donnee
                
                #maintenant nous disposons de ces octets et essayons de les écrire dehors
                try:
                    fichier_descripteur = open(charger_destination,"wb")
                    fichier_descripteur.write(fichier_tampon)
                    fichier_descripteur.close()
                    
                    #reconnaitre que nous écrivons le fichier dehors
                    client_socket.send("Fichier enregistré avec succès dans %\r\n" % charger_destination)
                
                except:
                    client_socket.send("Echec d'enregistrer le fichier dans %\r\n" % charger_destination)
                
                # vérifier l'exécution de la commande
                
                if len(commande):
                    #exécuter la commande
                    sortie = run_command(executer)
                    client_socket.send(sortie)
                
                # maintenant nous allons dans une autre loop si le Shell de commandes est demandé
                if commande:
                    while True:
                        #afficher un prompt simple
                        client_socket.send("<PNC:#>")
                            
                            #maintenant nous recevons avant de voir le saut de ligne (touche Enter)
                        cmd_buffer = ""
                        while "\n" not in cmd_buffer:
                                cmd_tampon += client_socket.recv(1024)
                                
                            
                            #envoie du retour de la sortie de commande
                            
                        reponse = run_command(cmd_buffer)
                            
                            #envoie du retour de la réponse
                        client_socket.send(reponse)
                            
                    
            
        
    
    def main():
        global ecouter
        global port
        global commande
        global executer
        global charger_destination
        global cible
        if not len(sys.argv[1:]):
            usage()
            # read the commandline options
        try:
            opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:",["help","listen","execute","target","port","command","upload"])
        except getopt.GetoptError as err:
                    print str(err)
                    usage()
                    
        for o,a in opts:
                if o in ("-h","--help"):
                        usage()
                elif o in ("-l","--listen"):
                        ecouter = True
                elif o in ("-e","--execute"):
                        executer = a
                elif o in ("-c","--command"):
                        commande = True
                elif o in ("-h","--charger"):
                        charger_destination = a
                elif o in ("-t","--target"):
                        cible = a 
                elif o in ("-p","port"):
                        port = int(a)
                else:
                    assert False,"Unhandled Option"
        # allons-nous écouter ou seulement envoyer des données depuis stdin?
        if not ecouter and len(cible) and port > 0:
                    
            #lire dans le tampon depuis la ligne de commande
            #ceci bloque, alors envoie CTRL-D s'il n'ya pas d'envoi d'entrée à stdin
            tampon = sys.stdin.read()
                    
            #envoyer des données
            client_sender(tampon)
                    
                #nous allons écouter et potentiellement 
                #charger des choses, exécuter des commandes, et annuler le retour shell en fonction de notre option de ligne de commandes
            if ecouter:
                        server_loop()
            
    main()
