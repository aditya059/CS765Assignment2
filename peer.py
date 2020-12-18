import socket
import threading
import time
import hashlib 
import random
import numpy
from queue import Queue  

no_of_threads = 3                   # We have 3 threads one each for listen, liveness testing and mining
job_no = [1, 2, 3]                  # We will create 3 jobs in queue for running each thread  
queue = Queue()                     # Queue to store our jobs  

MY_IP = "0.0.0.0"                   # MY_IP will later contain IP Address for listening 
PORT = int(input("PORT No. = "))    # Port for listening 
seeds_addr = set()                  # To store seed address received from config.txt
connect_seed_addr = []              # To store seed address to which peer is connected
peer_set_from_seed = set()          # Set used to store different peers address received from seed 
peers_connected = []                # To store list of peer objects connected 
MessageList = []                    # To store hash of Block to prevent flooding
DataBase = []                       # To store Blockchain blocks in local database
PendingQueue = Queue()              # To store received block which need to be validated

# Class of Peer objects 
class Peer: 
    i = 0
    address = ""
    def __init__(self, addr): 
        self.address = addr 

# Data Base Entry Class
class DB_Entry():
    def __init__(self, block, block_hash, height):
        self.block = block
        self.block_hash = block_hash
        self.height = height

# Block Class
class Block:
    def __init__(self, prev_block_hash, merkel_root, time_stamp):
        self.prev_block_hash = prev_block_hash
        self.merkel_root = merkel_root
        self.time_stamp = time_stamp
        #self.transaction = []

    def hash(self):
        block = str(self.prev_block_hash) + ":" + str(self.merkel_root) + ":" + str(self.time_stamp)
        return hash_of_message(block)

    def __str__(self):
        return str(self.prev_block_hash) + ":" + str(self.merkel_root) + ":" + str(self.time_stamp)
 
# Blockchain Class
class Blockchain():
    def __init__(self):
        self.genesis_block = Block("0x0000", "0x14ac", timestamp())  
        self.genesis_hash = "0x9e1c"
        DataBase.append(DB_Entry(self.genesis_block, self.genesis_hash, 0))

# Write the outputs to the file
def write_output_to_file(output):
    try:
        file = open("outputpeer.txt", "a")  
        file.write(output + "\n") 
    except:
        print("Write Failed")
    finally:
        file.close()

# To generate merkel root hash of 16 bits
def merkel():
    return "0x14ac"

# To find self timestamp
def timestamp():
    return time.time()

# To calculate hash of Block
def hash_of_message(message):
    result = hashlib.sha3_256(message.encode('utf-8')).hexdigest() 
    return "0x" + result[-4:]

# Read address of seeds from config file
def read_addr_of_seeds():
    global seeds_address_list
    try:
        file = open("config.txt","r")
        seeds_address_list = file.read()
    except:
        print("Read from config failed")
    finally:
        file.close()

# To calculate n i.e. total no. of seeds and also to find set of all available seeds
def total_available_seeds():
    global seeds_address_list
    temp = seeds_address_list.split("\n")
    for addr in temp:
        if addr:
            addr = addr.split(":")
            addr = "0.0.0.0:" + str(addr[1])
            seeds_addr.add(addr)
    return len(seeds_addr)

# Generate k random numbers in a given range.  
def generate_k_random_numbers_in_range(lower, higher, k):
    random_numbers_set = set()
    while len(random_numbers_set) < k:
        random_numbers_set.add(random.randint(lower,higher))
    return random_numbers_set

# This function is used to register the peer to (floor(n / 2) + 1) random seeds
def register_with_k_seeds():   # where k = floor(n / 2) + 1
    global seeds_addr
    seeds_addr = list(seeds_addr)
    seed_nodes_index = generate_k_random_numbers_in_range(0, n - 1, n // 2 + 1)
    seed_nodes_index = list(seed_nodes_index)
    for i in seed_nodes_index:
        connect_seed_addr.append(seeds_addr[i])
    connect_seeds()

# This function takes complete list of peers and find a random no. of peers to connect to b/w 1 and 4 and then connect to them and receive k-th block   
def join_atmost_4_peers(complete_peer_list):
    i = 0
    limit = random.randint(1, 4)
    print("Peers Connected List : ")
    for peer in complete_peer_list:
        try:
            if i < limit:
                sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                peer_addr = peer.split(":")
                ADDRESS = (str(peer_addr[0]), int(peer_addr[1]))
                sock.connect(ADDRESS)
                peers_connected.append( Peer(complete_peer_list[i]) )
                print(peer)
                i += 1
                message = "New Connect Request From:"+str(MY_IP)+":"+str(PORT)
                sock.send(message.encode('utf-8'))       
                print(sock.recv(20).decode('utf-8'))                       # Connect Accepted Message Received here                       
                received_block_k = sock.recv(128).decode('utf-8')          # Received Block k
                print("Received Block_K", received_block_k)
                thread = threading.Thread(target = put_block_in_pending_queue, args = [received_block_k])
                thread.start()
                sock.close()
            else:
                break
        except:
            print("Peer Connection Error. Trying another peer")

# It take complete peer list separated by comma from each seed and union them all
def union_peer_lists(complete_peer_list):
    global MY_IP
    complete_peer_list = complete_peer_list.split(",")
    complete_peer_list.pop()
    temp = complete_peer_list.pop()
    temp = temp.split(":")
    MY_IP = temp[0]
    for i in complete_peer_list:
        if i:
            peer_set_from_seed.add(i)
    complete_peer_list = list(peer_set_from_seed)
    return complete_peer_list

# This function is used to connect to seed and send our IP address and port info to seed and then receives a list of peers connected to that seed separated by comma
# After finding union it calls join_atmost_4_peers to connect to atmost peers
def connect_seeds():
    for i in range(0, len(connect_seed_addr)):
        try:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            seed_addr = connect_seed_addr[i].split(":")
            ADDRESS = (str(seed_addr[0]), int(seed_addr[1]))
            sock.connect(ADDRESS)
            MY_ADDRESS = str(MY_IP)+":"+str(PORT)
            sock.send(MY_ADDRESS.encode('utf-8'))
            message = sock.recv(10240).decode('utf-8')
            complete_peer_list = union_peer_lists(message)
            sock.close()
        except:
            print("Seed Connection Error")
    for peer in complete_peer_list:
        print(peer)
        write_output_to_file(peer)
    join_atmost_4_peers(complete_peer_list)

# Create socket to connect 2 computers
def create_socket():
    global sock
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
   
# To Bind Socket
def bind_socket():
    global sock
    ADDRESS = (MY_IP, PORT)
    sock.bind(ADDRESS)
    
# To handle different connected peers in different thread.It recieves messages from peer.
# According to the type of message received take appropriate actions
def handle_peer(conn, addr):
    global block_k
    global block_k_index
    while True:
        try:
            message = conn.recv(128).decode('utf-8')
            received_data = message
            if message:
                message = message.split(":")
                if "New Connect Request From" in message[0]:                # If it is new connection request then check if already 4 peers are not connected then accept the connection
                    if(len(peers_connected) < 4):
                        conn.send("New Connect Accepted".encode('utf-8'))      
                        peers_connected.append( Peer(str(addr[0])+":"+str(message[2])) )
                        block_k = DataBase[-1].block
                        block_k_index = len(DataBase) - 1
                        conn.send(str(block_k).encode('utf-8'))             # Send Block k 
                elif "Liveness Request" in message[0]:                      # If its liveness request then give back liveness reply              
                    liveness_reply = "Liveness Reply:" + str(message[1]) + ":" + str(message[2]) + ":" + str(MY_IP)
                    conn.send(liveness_reply.encode('utf-8'))
                elif "Send Previous Blocks" in received_data:               # If we get this message we sent all block from Block 0 to Block (k-1) to the requesting peer
                    conn.send(str(block_k_index).encode('utf-8'))
                    for i in range(block_k_index):
                        time.sleep(0.1)
                        conn.send(str(DataBase[i].block).encode('utf-8'))
                else:                                             
                    thread = threading.Thread(target = put_block_in_pending_queue, args = [received_data])  # If its new block then put it in Pending Queue if its not in ML list
                    thread.start()
        except:
            break
    conn.close()

# To listen at a particular port and create thread for each peer                 
def begin():
    sock.listen(100)
    print("Peer is Listening")
    while True:
        conn, addr = sock.accept()
        sock.setblocking(5)
        thread = threading.Thread(target = handle_peer, args = (conn,addr))
        thread.start()


# This function takes address of peer which is down. Generate dead node message and send it to all connected seeds
def report_dead(peer):
    dead_message = "Dead Node:" + peer + ":" + str(timestamp()) + ":" + str(MY_IP)
    print(dead_message)
    write_output_to_file(dead_message)
    for seed in connect_seed_addr:        
        try:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            seed_address = seed.split(":")
            ADDRESS = (str(seed_address[0]), int(seed_address[1]))
            sock.connect(ADDRESS)
            sock.send(dead_message.encode('utf-8'))
            sock.close()
        except:
            print("Seed Down ", seed)

# This function generates liveness request and send it to all connected peers at interval of 13 sec
# If three consecutive replies are not received then call report_dead()
def liveness_testing():    
    while True:
        liveness_request = "Liveness Request:" + str(timestamp()) + ":" + str(MY_IP)
        #print(liveness_request)                       
        for peer in peers_connected:
            try:                
                sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                peer_addr = peer.address.split(":")
                ADDRESS = (str(peer_addr[0]), int(peer_addr[1]))
                sock.connect(ADDRESS)
                sock.send(liveness_request.encode('utf-8'))
                #print(sock.recv(1024).decode('utf-8'))       
                sock.close()  
                peer.i = 0           # If it is able to send liveness req and get reply then start from 0 again so that we check for 3 consecutive failure
            except:                     # This happens when connection fails so count for 3 consecutive failures for given peer
                peer.i = peer.i + 1   
                if(peer.i == 3):                # If three failures then report this peer as dead node and remove from connected peer list
                    report_dead(peer.address)
                    peers_connected.remove(peer)
        time.sleep(13)

# Add valid blocks to local database    
def add_block_to_database(block, block_hash, height):
    DataBase.append(DB_Entry(block, block_hash, height))   

start = 1                               # Mine when start = 1

# Put received block in Pending Queue if its hash is not in Message List to avoid flooding/looping 
def put_block_in_pending_queue(received_block):
    global start
    hash = hash_of_message(received_block) 
    if hash in MessageList:             # If hash of received block is already in Message List then dont store in Pending Queue
        pass
    else:
        MessageList.append(str(hash))   # If it is received for 1st time then append it to its ML list
        PendingQueue.put(received_block)                
        print("Block Received = ", received_block)
        start = 0                       # Stop Mining

# To validate received block and add it to database or Blockchain if valid
def validate(received_block):
    message = received_block.split(":")
    if str(message[0]) == "0x0000" and str(message[2]) >= str(timestamp() - 3600) and str(message[2]) <= str(timestamp() + 3600):
        print("Adding Genesis to db ", received_block)
        DataBase[0] = DB_Entry(received_block, '0x9e1c', 0)  
        write_output_to_file(received_block)
        return True
    for db_entry in DataBase:
        if str(message[0]) == str(db_entry.block_hash) and str(message[2]) >= str(timestamp() - 3600) and str(message[2]) <= str(timestamp() + 3600):
            print("Adding to db ", received_block)
            add_block_to_database(received_block, hash_of_message(received_block), db_entry.height + 1)
            write_output_to_file(received_block)
            return True
    return False

# To synchronise with current blockchain height
def sync_with_current_blockchain_height():
    print("Sync")
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    peer_addr = peers_connected[0].address.split(":")
    ADDRESS = (str(peer_addr[0]), int(peer_addr[1]))
    sock.connect(ADDRESS)
    print("Send")
    message = "Send Previous Blocks"
    sock.send(message.encode('utf-8'))  
    no_of_prev_block = int(sock.recv(5).decode('utf-8'))
    print(no_of_prev_block)           
    for i in range(no_of_prev_block):
        received_block = sock.recv(40).decode('utf-8')
        validate(received_block)
    sock.close()
    print("sync done")
    

# Generate block and send it to connected peers
def generate_and_send_block():

    longest_chain_length = DataBase[-1].height
    parent = DataBase[-1]
    for db_entry in DataBase:
        if db_entry.height == longest_chain_length:
            parent = db_entry
            break
    
    block = Block(parent.block_hash, merkel(), timestamp())  
    print("------------------------------------") 
    print("Block Height = ", parent.height + 1)
    print("My block = ", block) 
    print("My Block Hash = ", hash_of_message(str(block)))
    print("------------------------------------")
    add_block_to_database(block, block.hash(), parent.height + 1)
 
    MessageList.append(block.hash())  # Add hash of mined block to ML list
    for peer in peers_connected:
        try:
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            peer_addr = peer.address.split(":")
            ADDRESS = (str(peer_addr[0]), int(peer_addr[1]))
            sock.connect(ADDRESS)
            sock.send(str(block).encode('utf-8'))   
            sock.close() 
        except:
            continue

nodeHashpower = float(input("Node Hash Power = "))  

# To generate exponential waiting time  
def generateWaitingTime(interarrivaltime):
    globalLambda = 1.0 / interarrivaltime                                   # Overall block generation rate
    lamda = nodeHashpower * globalLambda / 100.0                            # Scale individual miners lambda parameter based on the percentage of hash power it has         
    waitingTime = numpy.random.exponential(scale = 1.0 / lamda, size=None)  # Appropriately scale the the exponential waiting time
    return waitingTime

# To validate blocks in pending queue and send it to connected peers if valid
def handle_pending_queue():
    while PendingQueue.empty() == False:
        received_block = PendingQueue.get()
        if validate(received_block):
            for peer in peers_connected:     # Forward gossip message to all connected peers
                try:
                    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    peer_addr = peer.address.split(":")
                    ADDRESS = (str(peer_addr[0]), int(peer_addr[1]))
                    sock.connect(ADDRESS)
                    sock.send(str(received_block).encode('utf-8'))  
                    sock.close()
                except:
                    continue

# Calculate and print MPU and other values
def calculate_MPU(start_time, end_time):
    MPU = (DataBase[-1].height + 1) / len(DataBase)
    write_output_to_file("-----------------------------------")
    write_output_to_file("Start Time = " + str(start_time))
    write_output_to_file("End Time = " + str(end_time))
    write_output_to_file("No. of Block in longest chain = " + str(DataBase[-1].height))
    write_output_to_file("No. of blocks in blockchain = " + str(len(DataBase)))
    write_output_to_file("MPU = " + str(MPU))
    write_output_to_file("----------------------------")
    print("-----------------------------------")
    print("Start Time = " , str(start_time))
    print("End Time = " , str(end_time))
    print("No. of Block in longest chain = " , str(DataBase[-1].height))
    print("No. of blocks in blockchain = " , str(len(DataBase)))
    print("MPU = " , str(MPU))
    print("-----------------------------------")

# Block Mining
def mining():
    global start
    start_time = time.time()                     # Start time of peer
    end_time = start_time + 600                  # We want to calculate MPU for 10 min
    Flag = True

    if len(peers_connected) > 0:
        sync_with_current_blockchain_height()
    else:
        MessageList.append(hash_of_message(str(DataBase[-1].block)))

    print("Start Mining")

    while(True):
        current_longest_chain_length = DataBase[-1].height
        thread = threading.Thread(target = handle_pending_queue)
        thread.start()
        if DataBase[-1].height >= current_longest_chain_length and PendingQueue.empty():
            start = 1
        if start == 1:
            t = timestamp()                         # Time at which it start mining
            tow = generateWaitingTime(2)                                 
            print("Next Block will be created after ", tow)
            while(timestamp() <= t + tow):
                if start == 0:
                    break
            if start == 1:
                generate_and_send_block()  
        if Flag and timestamp() >= end_time:
            print(calculate_MPU(start_time, end_time))
            Flag = False 
            
# Create Worker Threads
def create_workers():
   for _ in range(no_of_threads):
       thread = threading.Thread(target = work)
       thread.daemon = True
       thread.start()

# Do next job that is in the queue (listen, liveness testing, mining)
def work():
   while True:
       x = queue.get()
       if x == 1:
           create_socket()
           bind_socket()
           begin()
       elif x == 2:
           liveness_testing()
       elif x == 3:
           mining() 
       queue.task_done()

# Create jobs in queue
def create_jobs():
    for i in job_no:
        queue.put(i)
    queue.join()


read_addr_of_seeds()
n = total_available_seeds()
register_with_k_seeds()                        # Where k = floor(n / 2) + 1

blockchain = Blockchain()

create_workers()
create_jobs()