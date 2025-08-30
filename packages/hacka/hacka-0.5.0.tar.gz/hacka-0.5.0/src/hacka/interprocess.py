import sys, zmq
from .pod import Pod

context = zmq.Context()

def verbose( aString ):
    pass

class AbsTabletop() :
    # Engine process :
    def waitForPlayers(self, numberOfPlayers):
        # lets the players connect the game
        pass
    
    # Player Managment :
    def changePlayerOrder(self):
        # change the order of the players
        pass
    
    def stopPlayer(self, iPlayer):
        pass
    
    def wakeUpPlayers( self, gamelConf ):
        pass
    
    def activatePlayer( self, iPlayer, aPodable ):
        pass
    
    def sleepPlayer( self, iPlayer, aPodable, result ):
        pass

class TabletopNet() :
    # HackaGame Server:
    def __init__(self, port=1400):
        # initialize the server
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        verbose( f'HackaGame: Start a server on {port}' )
        self.socket.bind( 'tcp://*:'+str(port) )
    
    # Engine process :
    def waitForPlayers(self, numberOfPlayers):
        self.players= [0]
        iPlayer= 1
        nbReady= 0
        while nbReady < numberOfPlayers :
            sockid, none, msg = self.socket.recv_multipart()
            if msg == b'player' and sockid not in self.players :
                self.players.append( sockid )
                self.send( iPlayer, 'yes' )
                iPlayer+= 1
            elif msg == b'ready' and sockid in self.players :
                verbose( f'HackaGame: player-{ self.players.index(sockid) } ready' )
                nbReady+= 1
            else :
                self.socket.send_multipart( [sockid, b'', b'nop'] )
        return True

    # Player Managment :
    def changePlayerOrder(self):
        first= self.players.pop(1) # 0 is the game itself.
        first= self.players.append(first)

    def stopPlayer(self, iPlayer):
        self.send( iPlayer, 'stop' )
    
    def wakeUpPlayers( self, gameConfiguration ):
        gc256= gameConfiguration.asPod()
        numberOfPlayers= len(self.players)-1
        for i in range(1, numberOfPlayers+1) :
            self.send( i, f'wake-up\nplayer {i} on {numberOfPlayers}\n' + gc256.dump() )
        nbReady= 0
        ready= []
        while nbReady < numberOfPlayers :
            sockid, none, msg = self.socket.recv_multipart()
            if msg == b'ready' and sockid in self.players and sockid not in ready :
                verbose( f'HackaGame: player-{ self.players.index(sockid) } ready' )
                ready.append(sockid)
                nbReady+= 1
            else :
                self.socket.send_multipart( [sockid, b'', b'stop\nerror protocol'] )
    
    def activatePlayer( self, iPlayer, playerHand ):
        # Perception :
        ph256= playerHand.asPod()
        assert( 0 < iPlayer and iPlayer < len(self.players) )
        playerSockId= self.players[iPlayer]
        msg= f'perception\n'+ ph256.dump()
        self.socket.send_multipart( [playerSockId, b'', bytes(msg, 'utf8')] )
        # Perception :
        playerSockId= self.players[iPlayer]
        while True :
            sockid, none, msg = self.socket.recv_multipart()
            if sockid == playerSockId :
                actionStr= msg.decode('utf8')
                verbose( f'HackaGame: player-{ self.players.index(sockid) } action : {actionStr}' )
                return Pod().load(actionStr)
            else :
                self.socket.send_multipart( [sockid, b'', b'stop\nerror protocol'] )
    
    def sleepPlayer( self, iPlayer, playerHand, result ):
        ph256= playerHand.asPod()
        assert( 0 < iPlayer and iPlayer < len(self.players) )
        playerSock= self.players[iPlayer]
        msg= f'sleep\nresult {result}\n{ ph256.asPod().dump() }'
        self.socket.send_multipart( [playerSock, b'', bytes(msg, "utf-8")] )
        while True :
            sockid, none, msg = self.socket.recv_multipart()
            if sockid == playerSock and msg == b'ready' :
                verbose( f'HackaGame: player-{ self.players.index(sockid) } sleep' )
                return True
            else :
                self.socket.send_multipart( [sockid, b'', b'stop\nerror protocol'] )
    
    # Communication :
    def send( self, iPlayer, msg ):
        assert( 0 < iPlayer and iPlayer < len(self.players) )
        self.socket.send_multipart( [self.players[iPlayer], b'', bytes(msg, "utf-8")] )

class TabletopLocal() :
    def __init__(self, players):
        # initialize the server
        self.players = [0] + players
        self.idResults= { id(p): [] for p in players }
        
    # Engine process :
    def waitForPlayers(self, numberOfPlayers):
        return True
    
    # Player Managment :
    def changePlayerOrder(self):
        # change the order of the players
        first= self.players.pop(1) # 0 is the game itself.
        first= self.players.append(first)
    
    def stopPlayer(self, iPlayer):
        return True
    
    def wakeUpPlayers( self, gameConfiguration ):
        gc256= gameConfiguration.asPod()
        numberOfPlayers= len(self.players)-1
        iPlayer= 1
        gameDump= gc256.dump()
        for player in self.players[1:] :
            verbose( f"\n> W A K E - U P   P L A Y E R - {iPlayer}" )
            #player.wakeUp( iPlayer, numberOfPlayers, gameConf )
            player.wakeUp( iPlayer, numberOfPlayers, Pod().load(gameDump) )
            iPlayer+= 1
        verbose( f"\n> G A M E   P R O C E S S" )
    
    def activatePlayer( self, iPlayer, playerHand ):
        ph256= playerHand.asPod()
        verbose( f"\n> A C T I V A T E   P L A Y E R - {iPlayer}" )
        self.players[iPlayer].perceive( Pod().load( ph256.dump() ) )
        action= self.players[iPlayer].decide()
        verbose( f"\n> G A M E   P R O C E S S" )
        return action
     
    def sleepPlayer( self, iPlayer, playerHand, result ):
        ph256= playerHand.asPod()
        self.idResults[ id(self.players[iPlayer]) ].append(result)
        verbose( f"\n> P U T   T O   S L E E P   P L A Y E R - {iPlayer}" )
        self.players[iPlayer].perceive( Pod().load( ph256.dump() ) )
        self.players[iPlayer].sleep(result)
        verbose( f"\n> G A M E   P R O C E S S" )

    # results :
    def results(self):
        return [ self.idResults[p] for p in self.idResults ]

class SeatClient() :
    # HackaGame Client:
    def __init__(self, player):
        self.player= player
    
    # HackaGame Client:
    def takeASeat(self, host='localhost', port=1400 ):
        #  Socket to talk to server
        verbose( f'HackaGames: connect to game on {host}:{port}' )
        self.connectToGame(host, port)
        msg= 'go'
        results= []
        while msg[0] != 'stop' :
            msg= self.receive().split('\n')
            if msg[0] == 'perception' :
                self.player.perceive( Pod().load( msg[1:] ) )
                action= self.player.decide()
                self.send( action.dump() )
            elif msg[0] == 'wake-up' :
                playerMsg= msg[1].split(' ')
                gameConfigurationMsg= ''
                if len(msg) > 2 : 
                    gameConfigurationMsg= msg[2:]
                self.player.wakeUp( 
                    int( playerMsg[1] ), int( playerMsg[3] ), Pod().load( gameConfigurationMsg )
                )
                self.send( "ready" )
            elif msg[0] == 'sleep' :
                self.player.perceive( Pod().load( msg[2:] ) )
                results.append( float( msg[1].split(' ')[1] ) )
                self.player.sleep( results[-1] )
                self.send( "ready" )
        return results
    
    def connectToGame(self, host, port):
        self.socket = context.socket(zmq.REQ)
        self.socket.connect( f'tcp://{host}:{port}' )
        self.send("player")
        #  Get the reply.
        message = self.receive()
        if message != 'yes' :
            verbose('HackaGames: didn\'t reach the game')
            exit()
        self.send( "ready" )

    def send(self, msg):
        self.socket.send( bytes(msg, 'utf8') )

    def receive(self):
        bytesMsg= self.socket.recv()
        print( f"> receive: {type(bytesMsg)}" )
        return bytesMsg.decode('utf8')

