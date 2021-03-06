#!/usr/bin/python3
import os
import socket
import subprocess

HOST = ''
PORT = 40000
TAM_MSG = 3000
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv = (HOST, PORT)
sock.bind(serv)
sock.listen(50)
while True:
    try:
        con, cliente = sock.accept()
    except: break
    pid = os.fork()
    if pid == 0:
        print('Cliente conectado', cliente)
        while True:
            msg = con.recv(TAM_MSG)
            if not msg: break
            msg = msg.decode().split()
            print(msg)
            if msg[0].lower() == 'connection':
                domain = ''.join(msg[2:])
                local_ip_address = '127.0.0.1'

                # Utilizando da biblioteca os para verificar informações de nome e sistema operacional do servidor, e utilizando a biblioteca subprocess para verificar informações do endereçamento IP do servidor
                server_data = os.uname()
                name_server = server_data.nodename
                operational_system = server_data.sysname
                ip_server_address = subprocess.run(['hostname', '-I'], stdout=subprocess.PIPE)
                ip_server_address = ip_server_address.stdout.decode('utf-8')

                
                if msg[1].lower() == '-p':
                    # Utilizando da biblioteca subprocess para fazer verificar as conexões estabelecidas do servidor
                    active_connections = subprocess.run(['netstat','-nt'], stdout=subprocess.PIPE)
                    active_connections = active_connections.stdout.decode('utf-8')
                    data_to_transfer = name_server + " " + operational_system + " " + ip_server_address + active_connections
                    # Encaminhando mensagem ao cliente
                    con.send(str.encode(data_to_transfer))
                
                
                elif msg[1].lower() == '-c': 
                    # Usando utilitário de dns para tradução de endereço IP
                    dns = subprocess.run(['host', domain], stdout=subprocess.PIPE) 
                    dns = dns.stdout.decode('utf-8')
                    dns = dns.split()
                    # Encontrar endereço ip do servidor
                    for i in range(len(dns)): 
                        if dns[i] == "address":
                            domain_ip_address = dns[i+1]
                            break
                    # Utilizando da biblioteca subprocess para fazer o teste de conexão e fazendo teste de conectividade com o utilitário de icmp com o endereço ip do dns passado como argumento
                    testing_connectivity = subprocess.run(['ping','-c', '4', domain_ip_address], stdout=subprocess.PIPE) 
                    testing_connectivity = testing_connectivity.stdout.decode('utf-8')
                    testing_connectivity = testing_connectivity.split()
                    # Verificando se há pacotes recebidos do ping, caso tenha significa que o servidor local tem conexões externas
                    if int(testing_connectivity[48]) > 0:  
                        status = "Server with external connection"
                    else:
                        status = "Server without external connection"
                    # Mensagem que será enviada para o cliente sendo guardada em uma variável    
                    data_to_transfer = '{} packets transmitted and {} packets received. {} to DNS {}'.format(testing_connectivity[45], testing_connectivity[48], status, domain)
                    data_to_transfer = name_server + " " + operational_system + " " + ip_server_address + data_to_transfer
                    # Mensagem enviada ao cliente
                    con.send(str.encode(data_to_transfer)) 

                
                elif msg[1].lower() == '-a':
                    # Utilizando da biblioteca subprocess para verificar as portas abertas no servidor
                    open_doors = subprocess.run(['nmap', local_ip_address], stdout=subprocess.PIPE)
                    open_doors = open_doors.stdout.decode('utf-8')
                    data_to_transfer = name_server + " " + operational_system + " " + ip_server_address + open_doors
                    # Encaminhando mensagem ao cliente
                    con.send(str.encode(data_to_transfer))
                
                
                else:
                    domain = ''.join(msg[1:])
                    dns = subprocess.run(['host', domain], stdout=subprocess.PIPE) # Usando utilitário de dns para tradução de endereço IP
                    dns = dns.stdout.decode('utf-8')
                    dns = dns.split()
                    for i in range(len(dns)): # Encontrar endereço ip do servidor
                        if dns[i] == "address":
                            domain_ip_address = dns[i+1]
                            break
                    testing_connectivity = subprocess.run(['ping','-c', '4', domain_ip_address], stdout=subprocess.PIPE)
                    testing_connectivity = testing_connectivity.stdout.decode('utf-8')
                    active_connections = subprocess.run(['netstat','-nt'], stdout=subprocess.PIPE)
                    active_connections = active_connections.stdout.decode('utf-8')                       
                    open_doors = subprocess.run(['nmap', local_ip_address], stdout=subprocess.PIPE)
                    open_doors = open_doors.stdout.decode('utf-8') 
                    data_to_transfer = name_server + " " + operational_system + " " + ip_server_address + open_doors + testing_connectivity + active_connections + domain
                    con.send(str.encode(data_to_transfer))
                        
            # QUIT
            elif msg[0].lower() == 'quit':
                break
            else:
                con.send(str.encode('Invalid Command'))

        print('Cliente desconectado', cliente)
        con.close()
        break
    else:
        con.close()
sock.close()

