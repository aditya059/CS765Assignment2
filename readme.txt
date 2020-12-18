Description of the code:

  	SEED:
		1. Create socket, Bind socket and then listening for request/messages from peers
		2. Once it receives the connect request from peer, it create separate thread to handle that peer
		3. If it receives a connection request from peer, then it send its peer list to that peer
		4. If it receives a dead node message from peer, it will remove dead peer info from its peer list

  	PEER:
	    1. Read seed address from "config.txt" file
		2. Send request to seeds 
		3. Receive peer list and connect to atmost 4 random peers
		4. It create 3 separate thread one for listening, another for mining, and last one for liveness testing
		5. It mines block, forward received block and also generate liveness request 
		6. If a peer is down it sends dead node message to seed node

	Adversary:
	    1. Read seed address from "config.txt" file
		2. Send request to seeds 
		3. Receive peer list and connect to atmost 4 random peers
		4. It create 4 separate thread one for listening, another for mining, another for flooding and last one for liveness testing
		5. It mines block, forward received block and also generate liveness request 
		6. It also send invalid blocks to some selected peers at regular interval of time(flood them)
		7. If a peer is down it sends dead node message to seed node

Details steps for compile and run:

1. Open the project folder:
	1. Open the file "config.txt" and put the System IP and any Port no. in the format of "IP:PORT"
	2. Based on the no. of seed we want to have, we have to put all Seed Address manually like above

2. Go to the directory where seed.py and peer.py file is available using terminal
  
To compile and run seed:
	3. Run the code using "python3 seed.py"
	4. Based on no. of entries in config file, run different seeds with different port no. given in config file. Enter port no. only
	5. Now run one or more instance of terminal using same step 3 and 4

To compile and run peer:
	6. Run the code using "python3 peer.py"
	7. Give the port no. as you wish. Enter distinct port no. for each peer. Enter other values asked by program 
	8. Now run one or more instance of terminal using same step 6 and 7 to generate more peers. 

To compile and run adversary:
	9. Run the code using "python3 adversary.py"
	10. Give the port no. as you wish. Enter distinct port no. for each adversary. Enter other values asked by program 
	11. Now run one or more instance of terminal using same step 9 and 10 to generate more adversary. 

A sample of config file is already given and our output files