from .pod import Pod
from .command import Command, Option
from .gamemaster import SequentialGameMaster

class EchoGame :
    def __init__(self, numberOfPlayer=1, numberOfTics=3):
        self._nbPlayer= numberOfPlayer
        self._nbTics= numberOfTics
    
    # Game interface :
    def initialize(self):
        self._msg= [ Pod("Hello player", [i]) for i in range(self._nbPlayer+1) ]
        self._tic= 0
        return Pod("EchoGame", [self._nbPlayer, self._nbTics])
    
    def playerHand( self, iPlayer ):
        return self._msg[iPlayer]

    def applyAction( self, action, iPlayer ):
        self._msg[iPlayer]= action
        return True

    def tic( self ):
        self._tic+= 1

    def isEnded( self ):
        return self._tic >= self._nbTics

    def playerScore( self, iPlayer ):
        return 1.0

# serve :
def serve():
    # Commands:
    cmd= Command(
            "start-server",
            [
                Option( "port", "p", default=1400 ),
                Option( "number", "n", 2, "number of games" )
            ],
            (
                "star a server fo EchoGame on your machine. "
                "ARGUMENTS the Hello msg"
            )
        )

    cmd.process()
    if cmd.ready() :
        game= EchoGame()
    else :
        print( cmd.help() )
        exit()

    # start:
    master= SequentialGameMaster( game )
    master.launchOnNet( cmd.option("number"), cmd.option("port") )

if __name__ == '__main__' :
    serve()