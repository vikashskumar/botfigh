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
from StringIO import StringIO

MAXSCORE = 48
INFINITY = MAXSCORE*100
MAXPLAYER = 2
MAXHOLES = 6
DEFAULTSTONES = 4
MAX_DEPTH = 3

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
        self.storeincr = [0 for x in xrange(MAXPLAYER)]
        self.loot = [0 for x in xrange(MAXPLAYER)]
        self.overflow = [0 for x in xrange(MAXPLAYER)]
        self.bonus = [0 for x in xrange(MAXPLAYER)]
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
                self.storeincr[i] = other.storeincr[i]
                self.loot[i] = other.loot[i]
                self.overflow[i] = other.overflow[i]
                self.bonus[i] = other.bonus[i]
            self.owner = other.owner
            self.opponent = other.opponent
            self.movecnt = other.movecnt
            
            #msg = " ".join(["\nCopied new board for Player", str(self.owner+1), "against", str(self.opponent+1)])
            #logMsg(msg)
    def resetStats(self):
        for i in xrange(MAXPLAYER):
            self.storeincr[i] = 0
            self.loot[i] = 0
            self.overflow[i] = 0
            self.bonus[i] = 0
        
    def playOpponentMove(self, move):
        #msg = " ".join(["player", str(self.opponent +1), "plays", str(move)])
        #logMsg(msg)        
        return self.playMove(self.opponent, move)        
    
    def playOwnMove(self, move):
        #msg = " ".join(["player", str(self.owner+1), "plays", str(move)])
        #logMsg(msg)
        self.movecnt += 1
        return self.playMove(self.owner, move)
        
    def evalBoard(self, player):
        os = StringIO()
        p1 = self.owner
        p2 = self.opponent    
        storeval = self.stores[p1] - self.stores[p2]
        if self.over == True:
            if storeval > 0:  #Owner wins max value
                return INFINITY
            elif storeval < 0:
                return -INFINITY  #opponent wins
            else:
                return 0  #draw
        stones = sum(self.holes[p1]) - sum(self.holes[p2])
        loot = self.loot[p1] - self.loot[p2]
        #overflow= (self.overflow[p1]*0.3)**2 - (self.overflow[p2]*0.3)**2
        #overflow= self.overflow[p1] - self.overflow[p2]
        storeincr = self.storeincr[p1] - self.storeincr[p2]
        bonus = self.bonus[p1] - self.bonus[p2]
        #zerocnt = (self.holes[p1].count(0)*0.8)**2 -  (self.holes[p2].count(0)*0.8)**2
        zerocnt = self.holes[p1].count(0) - self.holes[p2].count(0)        
        
        #score = storeval + bonus + loot + storeincr - zerocnt
        '''
        '''
        finalscore = storeval + (loot*0.3)**2 + storeincr + bonus*2
        '''
        playerscore = (self.bonus[player]*2 + self.storeincr[player])*2        
        if (storeincr + bonus) == 0 and playerscore  > 0:
            if player == self.owner:
                finalscore += playerscore
            else:
                finalscore -= playerscore
    
        if loot == 0 and self.loot[player] > 0:
            if player == self.owner:
                finalscore += (self.loot[player]*0.3)**2
            else:
                finalscore -= (self.loot[player]*0.3)**2
                
        if (abs(zerocnt) > 3): 
             finalscore -= zerocnt*2
        elif(self.holes[player^1].count(0) > 4):
            if player == self.owner:
                finalscore += 5
            else:
                finalscore -= 5
            #score = score - self.stores[player^1]
        '''                
        print >> os, "\nP",player,":", "str",storeval, "stn", stones, "lt", loot, "incr", storeincr, "b", bonus, "-z", zerocnt, "F:", finalscore
        logMsg(os.getvalue())
        return finalscore
        
    def getPossibleMoves(self, playerId):
        possibleMoves = []        
        holes = self.holes[playerId]
        if self.movecnt < 2:
            for idx, x in enumerate(holes):
                if (idx + x) == MAXHOLES:
                    possibleMoves.append(HoleToMove[playerId][idx])
            if len(possibleMoves) > 0:
                return possibleMoves
        
        for idx, x in enumerate(holes):
            if x != 0:
                possibleMoves.append(HoleToMove[playerId][idx])
        return possibleMoves
        
    def playMove(self, playerId, move):   
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
                if pid != playerId:
                    self.overflow[playerId] += 1                
                    
            elif hole >= MAXHOLES:
                if pid == playerId:
                    #pid is the player whose holes are being processed and 
                    #we hit store if it is the player who played the move then 
                    #increment store seed
                    self.stores[pid] += 1                                        
                    if seed == 0:
                        bonus = True                                
                        self.bonus[pid] += 1
                    else:
                        self.storeincr[pid] += 1                        
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
            self.loot[pid] += oholes[ohole]
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

def getHeuristicValue(board, maximizingPlayer):    
    if maximizingPlayer:
        return board.evalBoard(board.owner)
    else:
        return board.evalBoard(board.opponent)
    

def minimax(board, depth, maximizingPlayer):
    bestvalue = 0
    bestmove = -1
#    os = StringIO()
    
    if depth == 0 or board.over == True:        
        return (getHeuristicValue(board, maximizingPlayer), bestmove)
    
    #dpthstr = " ".join([str(i) for i in xrange(depth)])
    if maximizingPlayer:
        bestvalue = -INFINITY
        moves = board.getPossibleMoves(board.owner)
        if len(moves) == 0:
            #print >> os, dpthstr, "Return", getHeuristicValue(board, maximizingPlayer), bestmove, "MAX", maximizingPlayer, "Depth:", depth
            #logMsg(os.getvalue())            
            return (getHeuristicValue(board, maximizingPlayer), bestmove)
        for move in moves:            
            newboard = Board(0, board)
            bonus = newboard.playOwnMove(move)
            v, m = minimax(newboard, depth -1, bonus)
            if v >= bestvalue:
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
            if v <= bestvalue:
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
    v, nextmove = minimax(board, MAX_DEPTH, True)
    logMsg("Playing Move: " + str(nextmove))
    board.playOwnMove(nextmove)
    board.resetStats()
    board.display()    
    return nextmove
    
def commandis(instr, cmd):
    if instr.find(cmd) == -1:
        return False
    else:
        return True

'''-----------------------------------
   1   5 5 6 6 0 5
       4 4 0 5 5 0 2
----------------------------------
''' 
def setBoard(playerId):
    b = Board(playerId)
    p1str = "5 5 6 6 0 5"
    p1holes = [int(x) for x in p1str.split(" ")]  
    for idx, x in enumerate(reversed(p1holes)):
        b.holes[0][idx] = x
    p2str = "4 4 0 5 5 0"
    p2holes = [int(x) for x in p2str.split(" ")]  
    for idx, x in enumerate(p2holes):
        b.holes[1][idx] = x
    b.stores[0] = 1 #p1 score
    b.stores[1] = 2 # p2 score
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