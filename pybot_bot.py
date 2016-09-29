# -*- coding: utf-8 -*-

infile = None
def raw_input():
    global infile
    if(infile == None):
        infile = open("C:\\bot_input.txt", "r");
    return infile.readline()

#from copy import deepcopy, copy
#from collections import defaultdict, deque

import sys
import random

MAXSCORE = 48
INFINITY = MAXSCORE*100
MAXPLAYER = 2
MAXHOLES = 6
DEFAULTSTONES = 4

#playerid 
HoleToMove = [{0:6, 1:5, 2:4, 3:3, 4:2, 5:1}, {0:1, 1:2, 2:3, 3:4, 4:5, 5:6}]
MoveToHole = [{6:0, 5:1, 4:2, 3:3, 2:4, 1:5}, {1:0, 2:1, 3:2, 4:3, 5:4, 6:5}]
              
mainboard = None
logFile = None
def logMsg(msg):
    global logFile
    #return
    logFile.write(msg + "\n")
       
class Board:
    def __init__(self, playerId, other = None):
        self.holes = [[DEFAULTSTONES for x in xrange(MAXHOLES)] for y in xrange(MAXPLAYER)]
        self.stores = [0 for x in xrange(MAXPLAYER)]
        self.over = False        
        if other == None:
            self.movecnt = 0
            self.owner = playerId
            self.opponent = self.owner ^ 1
            msg = " ".join(["\n\nI am player", str(self.owner+1), "against", str(self.opponent+1)])
            logMsg(msg)
        else:
            for i in xrange(MAXPLAYER):
                for j in xrange(MAXHOLES):
                    self.holes[i][j] = other.holes[i][j]
            for i in xrange(MAXPLAYER):
                self.stores[i] = other.stores[i]
            self.owner = other.owner
            self.opponent = other.opponent
            self.movecnt = 0
            #msg = " ".join(["\nCopied new board for Player", str(self.owner+1), "against", str(self.opponent+1)])
            #logMsg(msg)
                
    def playOpponentMove(self, move):
        #msg = " ".join(["player", str(self.opponent +1), "plays", str(move)])
        #logMsg(msg)        
        return self.playMove(self.opponent, move)
        
    def playOwnMove(self, move):
        #msg = " ".join(["player", str(self.owner+1), "plays", str(move)])
        #logMsg(msg)
        return self.playMove(self.owner, move)
        
    def evalBoard(self, player):        
        score = self.stores[self.owner] - self.stores[self.opponent]
        #score += sum(self.holes[player])
        
        return score
        
    def getPossibleMoves(self, playerId):
        possibleMoves = []
        if self.movecnt == 0:
            possibleMoves.append(4)
            return possibleMoves
        
        holes = self.holes[playerId]
        for idx, x in enumerate(holes):
            if x != 0:
                possibleMoves.append(HoleToMove[playerId][idx])
        return possibleMoves
        
    def playMove(self, playerId, move): 
        self.movecnt += 1
        bonus = False
        pid = playerId
        holes = self.holes[pid]
        hole = MoveToHole[pid][move]
        seed = holes[hole]
        holes[hole] = 0 #empty the hole and distribute the seed in other holes
        
        while seed > 0:
            seed -= 1
            hole += 1
            if hole < MAXHOLES:
                holes[hole] += 1                
            elif hole >= MAXHOLES:
                if pid == playerId:
                    #pid is the player whose holes are being processed and 
                    #we hit store if it is the player who played the move then 
                    #increment store seed
                    self.stores[pid] += 1
                    if seed == 0:
                        bonus = True                                
                else:
                    seed += 1 #seed shouldn't decrement for non player pit
                #switch to other player holes
                pid ^= 1
                hole = -1
                holes = self.holes[pid]
        
        if  (-1 < hole < MAXHOLES) and holes[hole] == 1 and pid == playerId:
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
        
        
        if sum(self.holes[playerId]) == 0:
            #update homepit for other player with his remaining stones            
            pid = playerId ^ 1
            cnt = 0
            holes = self.holes[pid]
            for idx in xrange(MAXHOLES):
                cnt += holes[idx]
                holes[idx] = 0
            self.stores[pid] += cnt
            self.over = True            
            bonus = False
            #logMsg(" ".join(["Game Over by player", str(playerId+1)])) 
        return bonus
        
    def display(self):
        msg = "".join(["\n-----------------------------------\n", 
                 "\t",                 
                 " ".join([str(x) for x in reversed(self.holes[0])]),
                 "\nP1: ",
                 str(self.stores[0]),
                 "\t\t\tP2:",
                 str(self.stores[1]),
                 "\n\t",
                 " ".join([str(x) for x in self.holes[1]]),
                 "\n----------------------------------\n"])        
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


'''
01 function minimax(node, depth, maximizingPlayer)
02     if depth = 0 or node is a terminal node
03         return the heuristic value of node

04     if maximizingPlayer
05         bestValue := −∞
06         for each child of node
07             v := minimax(child, depth − 1, FALSE)
08             bestValue := max(bestValue, v)
09         return bestValue

10     else    (* minimizing player *)
11         bestValue := +∞
12         for each child of node
13             v := minimax(child, depth − 1, TRUE)
14             bestValue := min(bestValue, v)
15         return bestValue
(* Initial call for maximizing player *)
minimax(origin, depth, TRUE)
'''
def getHeuristicValue(board, maximizingPlayer):    
    if maximizingPlayer:
        return board.evalBoard(board.owner)
    else:
        return board.evalBoard(board.opponent)
    

def minimax(board, depth, maximizingPlayer):
    bestvalue = 0
    bestmove = -1
    
    if depth == 0 or board.over == True:
        return (getHeuristicValue(board, maximizingPlayer), bestmove)
    
    if maximizingPlayer:        
        bestvalue = -INFINITY
        moves = board.getPossibleMoves(board.owner)
        if len(moves) == 0:
            return (getHeuristicValue(board, maximizingPlayer), bestmove)
        for move in moves:
            #Fixme: account for bonus move as well.
            newboard = Board(0, board)
            bonus = newboard.playOwnMove(move)            
            v, m = minimax(newboard, depth -1, bonus)
            if v > bestvalue:                
                bestvalue = v
                bestmove = move
        return (bestvalue, bestmove)
    else:  #minimizing player
        bestvalue = INFINITY
        moves = board.getPossibleMoves(board.opponent)
        if len(moves) == 0:
            return (getHeuristicValue(board, maximizingPlayer), bestmove)
        for move in moves:
            newboard = Board(0, board) #Allocate a new board for each branching
            bonus = newboard.playOpponentMove(move)
            v, m = minimax(newboard, depth -1, (not bonus))
            if v < bestvalue:
                bestvalue = v
                bestmove = move
        return (bestvalue, bestmove)

def update_opponent_move(board, move):
    board.playOpponentMove(move)
    board.display()
    return

def get_next_move(board):        
    #nextmove = random.choice(board.getPossibleMoves(board.owner))
    #nextmove = 1
    v, nextmove = minimax(board, 5, True)
    board.playOwnMove(nextmove)
    board.display()
    
    return nextmove
    
def commandis(instr, cmd):
    if instr.find(cmd) == -1:
        return False
    else:
        return True

'''-----------------------------------
	8 8 2 3 2 0
 P1: 3			P2:3
	0 1 1 7 2 8
----------------------------------
''' 
def setBoard(playerId):
    b = Board(playerId)
    p1str = "8 8 2 3 2 0"
    p1holes = [int(x) for x in p1str.split(" ")]  
    for idx, x in enumerate(reversed(p1holes)):
        b.holes[0][idx] = x
    p2str = "0 1 1 7 2 8"
    p2holes = [int(x) for x in p2str.split(" ")]  
    for idx, x in enumerate(p2holes):
        b.holes[1][idx] = x
    b.stores[0] = 3 #p1 score
    b.stores[1] = 3 # p2 score
    return b
        
if __name__ == "__main__":        
    playerId = 0;
    respstr = "";    
    if ( len(sys.argv) >= 2 ):
        logFile = open(sys.argv[1], "w");       
    else:
       logFile = open("mybot.log", "w+");
   
    done = False
    while not done:        
        incmd = sys.stdin.readline()      
        #incmd = raw_input().strip()
        if (commandis(incmd, "START")):
            #START:X
            playerId = int(incmd[6])
            #player id for internal use is 0 or 1
            mainboard = Board(playerId - 1)
            #mainboard = setBoard(playerId-1)
            mainboard.display()
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
    if infile:
        infile.close()
    if logFile:
        logFile.close()