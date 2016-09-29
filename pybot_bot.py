# -*- coding: utf-8 -*-

file = None
def raw_input():
    global file
    if(file == None):
        file = open("C:\\bot_input.txt", "r");
    return file.readline()

#from copy import deepcopy, copy
#from collections import defaultdict, deque

import sys
import random


MAXPLAYER = 2
MAXHOLES = 6
DEFAULTSTONES = 4

#playerid 
HoleToMove = [{0:1, 1:2, 2:3, 3:4, 4:5, 5:6},
              {0:6, 1:5, 2:4, 3:3, 4:2, 5:1}]
MoveToHole = [{1:0, 2:1, 3:2, 4:3, 5:4, 6:5},
              {6:0, 5:1, 4:2, 3:3, 2:4, 1:5}]
              
mainboard = None
logFile = None
def logMsg(msg):
    logFile.write(msg)
       
class Board:
    def __init__(self, playerId):
        self.holes = [[DEFAULTSTONES for x in xrange(MAXHOLES)] for y in xrange(MAXPLAYER)]
        self.stores = [0 for x in xrange(MAXPLAYER)]
        self.owner = playerId
        self.opponent = self.owner ^ 1
        msg = ["I am player", self.owner, "against", self.opponent].join(" ")
        logMsg(msg)        
    
    def playOpponentMove(self, move):
        msg = ["player", str(self.opponent), "plays", str(move)].join(" ")
        logMsg(msg)        
        self.playMove(self.opponent, move)
        
    def playOwnMove(self, move):
        msg = ["player", str(self.owner), "plays", str(move)].join(" ")
        logMsg(msg)
        self.playMove(self.owner)
        
    def evalBoard(self):
        return self.stores[self.owner] - self.stores[self.opponent]
        
    def playMove(self, playerId, move):        
        pid = playerId
        holes = self.holes[pid]
        hole = MoveToHole[pid][move]
        seed = holes[hole]
        holes[pid][hole] = 0 #empty the hole and distribute the seed in other holes
        
        while seed > 0:            
            hole += 1
            seed -= 1
            if hole < MAXHOLES:
                holes[hole] += 1
            elif hole == MAXHOLES:
                if pid == playerId:
                    #pid is the player whose holes are being processed and 
                    #we hit store if it is the player who played the move then 
                    #increment store seed
                    self.stores[pid] += 1
                    seed -= 1                    
                else:
                    #skip the store and switch to other player holes
                    pid ^= 1
                    hole = 0
                    holes = self.holes[pid]
        if holes[hole] == 1 and pid == playerId:
            #player dropped the last seed in empty hole on his side
            holes[hole] = 0
            #pMove = HoleToMove[pid][hole]
            opid = pid ^ 1
            oholes = self.holes[opid]
            #ohole1 = MoveToHole[opid][pMove]
            ohole = abs(5-hole)
            cnt = oholes[ohole] + 1
            oholes[ohole] = 0
            self.stores[pid] += cnt
        
    def display(self):
        msg = [ "-----------------------------------\n", 
                 "\t",
                 self.holes[1],
                 "\nP2: ",
                 self.stores[1],
                 "\t\t\tP1:",
                 self.stores[0],
                 "\n\t",
                 self.holes[0],
                "----------------------------------\n"].join("")        
        logMsg(msg)
'''
        logMsg("-----------------------------------\n")
        logMsg("\t")
        logMsg(self.holes[1])
        logMsg("\nP2: ")
        logMsg(self.stores[1])
        logMsg("\t\t\tP1:")
        logMsg(self.stores[0])
        logMsg("\n\t")
        logMsg(self.holes[0])
        logMsg("----------------------------------\n")
'''        
        

def update_opponent_move(board, move):
    board.playOpponentMove(move)
    board.display()
    return

def get_next_move(board):
    nextmove = random.randint(1,6)
    board.playOwnMove(nextmove)
    board.display()
    return nextmove
    

def commandis(instr, cmd):
    if instr.find(cmd) == -1:
        return False
    else:
        return True
    
if __name__ == "__main__":    
   playerId = 0;
   respstr = "";
   if ( len(sys.argv) >= 2 ):
       log = open(sys.argv[1], "w+");       
   
   done = False
   while not done:
      #incmd = sys.stdin.readline()      
      incmd = raw_input().strip()
      if (commandis(incmd, "START")):
           #START:X
          playerId = int(incmd[6])
          #player id for internal use is 0 or 1
          mainboard = Board(playerId - 1)
          respstr = "READY"
      elif (commandis(incmd,"STOP")):
         respstr = "STOPPED"
         done = True
      elif (commandis(incmd,"YOUR_MOVE")):
         move = get_next_move(mainboard) #however you implement it
         respstr = str(move) 
      elif (commandis(incmd, "OTHER_MOVED")):
         # fixme: update you board state         
         move = int(incmd[12])
         update_opponent_move(mainboard, move)
         respstr = "ACK"
      sys.stdout.write(respstr)
      sys.stdout.write("\n")
      sys.stdout.flush() 
      if file:
          file.close()