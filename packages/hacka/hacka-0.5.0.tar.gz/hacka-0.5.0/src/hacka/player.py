#!env python3
"""
HackaGame player interface 
"""
import re

# Local HackaGame:
from . import pod, interprocess

class Player() :
    # Player interface :
    def wakeUp(self, playerId, numberOfPlayers, gameConf):
        pass

    def perceive(self, gameState):
        pass
    
    def decide(self):
        return "sleep"
    
    def sleep(self, result):
        pass

    # Player interface :
    def takeASeat(self, host='localhost', port=1400 ):
        client= interprocess.SeatClient(self)
        return client.takeASeat( host, port )

class PlayerShell(Player) :
    # Player interface :
    def wakeUp(self, playerId, numberOfPlayers, gameConf):
        print( f'---\nwake-up player-{playerId} ({numberOfPlayers} players)')
        print( gameConf )

    def perceive(self, gameState):
        print( f'---\ngame state\n' + str(gameState) )
    
    def decide(self):
        ok= 3
        action = input('Enter your action: ')
        return pod.Pod().decode(action)
        
    def sleep(self, result):
        print( f'---\ngame end\nresult: {result}')


# connect a game :
def connect():
    # Commands:
    player= PlayerShell()
    player.takeASeat()

if __name__ == '__main__' :
    connect()
