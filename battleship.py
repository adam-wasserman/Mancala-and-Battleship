#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 16:26:32 2021

@author: adamwasserman
"""

import numpy as np
import time
import os
import random

ships = {"Submarine":('*',3), "Carrier":('#',5), 'Destroyer':('@',4), 'Scout':('+',2), 'Escort':('o',3)}
let_to_number = {'A':0, 'B':1, "C":2, "D":3, 'E':4, 'F':5, 'G':6, 'H':7, 'I':8, 'J':9}

class Game:
    def __init__(self,multi = True):
        self.board = np.zeros((10,10,2),dtype = 'object') #2 10 by 10 boards
        self.guesses = np.full((10,10,2), fill_value = 'O', dtype = 'str')
        self.player = 0
        self.multi = multi
            
        
        
    def togglePlayer(self):
        if self.player == 0:
            return 1
        return 0
            
    def placeShips(self):
        l_ships = list(ships.keys())
        while len(l_ships) > 0:
            s_type = input("Choose a ship to place (" + str(l_ships) + "):")
            if s_type == '':
                break
            if not(s_type in l_ships):
                print("Ship selection not found / available")
                continue
            print("You chose a ship of size " + str(ships[s_type][1]))
            spos = self.genCoords(input("Choose one endpoint: "))
            if spos == False:
                print("Invalid coords!")
                continue
            epos = self.genCoords(input("Choose your second endpoint: "))
            if epos == False:
                print("Invalid coords!")
                continue
            x_diff = spos[1] - epos[1]
            y_diff = spos[0] - epos[0]
            size = ships[s_type][1]
            if not((abs(x_diff)+1 == size and y_diff == 0) or (x_diff == 0 and abs(y_diff)+1 == size)):
                print("Endpoints do not form valid ship placement")
                continue
            ship = Ship(s_type,self.player)
            if x_diff != 0:
                direction = x_diff // (size-1)
                to_slice = slice(spos[1],epos[1]-direction,-direction)
                if any((self.board[spos[0],to_slice,spos[2]] != 0)):
                    print("Overlapping with another ship!")
                    continue
                self.board[spos[0],to_slice,spos[2]] = ship
            if y_diff != 0:
                direction = y_diff // (size-1)
                to_slice = slice(spos[0],epos[0]-direction,-direction)
                if any((self.board[to_slice,spos[1],spos[2]] != 0)):
                    print("Overlapping with anotoher ship!")
                    continue
                self.board[to_slice,spos[1],spos[2]] = ship
            l_ships.remove(s_type)
            self.printBoard()
    
    def fireShots(self):
        while (not (np.all(self.board[:,:,0] == 0) or np.all(self.board[:,:,1] == 0))):
            print("Hello, Player {player}. Here are your previous guesses:".format(player = self.player+1))
            self.printGuesses()
            user_input = input("Choose a square to fire:")
            to_fire = self.genCoords(user_input)
            if to_fire == False:
                print("Invalid coordinates!")
                continue
            if self.guesses[to_fire[0],to_fire[1],self.player] != 'O':
                print("Already guessed this spot!")
                continue
            opp_piece = self.board[to_fire[0],to_fire[1],self.togglePlayer()]
            if opp_piece != 0:
                opp_piece.decHealth()
                if opp_piece.getHealth() == 0:
                    filt = (self.board == opp_piece) # is there a way to do this with 'is'?
                    self.board[filt] = 0
                    self.guesses[filt[:,:,::-1]] = 'x' #clever trick with slicing
                    print("\nHIT! SHIP SUNK: "+ opp_piece.getType() + "\n")
                    self.printGuesses()
                else:
                    self.guesses[to_fire[0],to_fire[1],self.player] = '*'
                    print("\nHIT!\n")
                    self.printGuesses()
            else:
                self.guesses[to_fire[0],to_fire[1],self.player] = '-'
                print("\nMISS")
            time.sleep(3)
            print("\n"*20)
            self.player = self.togglePlayer()
        winning_player = 1 if np.all(self.board[:,:,1] == 0) else 2
        print("GAME OVER! Player {winner} wins!".format(winner=winning_player))
            
                               

    def genCoords(self,string):
            if len(string) != 2:
                return False
            if not(string[0] in let_to_number.keys()):
                return False
            if int(string[1]) > 9 or int(string[1]) < 0:
                return False
            row = let_to_number[string[0]]
            col = int(string[1])-1 if int(string[1]) != 0 else 9
            return row,col,self.player
        
    def printBoard(self):
        print("  1 2 3 4 5 6 7 8 9 0")
        for i,j in let_to_number.items():
            print(i,end = ' ')
            for k in self.board[j,:,self.player]:
                sym = "0" if k == 0 else k.symbol
                print(sym, end = ' ')
            print() # for new line
    
    def printGuesses(self):
        print("  1 2 3 4 5 6 7 8 9 0")
        for i,j in let_to_number.items():
            print(i, end=' ')
            for k in self.guesses[j,:,self.player]:
                print(k, end = ' ')
            print()
            
    def randomBoard(self):
        for vessel in ships.keys():
            while True:
                start = np.array([int(random.random()*10),int(random.random()*10)],dtype='int8')
                direction = np.array([0,1] if random.random() > 0.5 else [1,0]) * (-1 if random.random() > 0.5 else 1)
                end = start + ((ships[vessel][1]-1) * direction)
                params = np.concatenate((start,end))
                if np.any(params < 0) or np.any(params > 9):
                    continue
                row_slice = slice(min(start[0],end[0]),max(end[0],start[0])+1)
                col_slice = slice(min(start[1],end[1]),max(end[1],start[1])+1)
                total_slice = np.s_[row_slice,col_slice,self.player]
                if np.any(self.board[total_slice] != 0):
                    continue
                self.board[total_slice] = Ship(vessel,self.player)
                break
        
        

class Ship:
    def __init__(self, s_type, player):
        self.player = player
        self.type = s_type
        self.symbol = ships[s_type][0]
        self.health = ships[s_type][1]
        
    def decHealth(self):
        self.health -= 1
    
    def getHealth(self):
        return self.health
    
    def getType(self):
        return self.type

def clear():
    os.system('cls' if os.name=='nt' else 'clear')
    
#The following code should go into the main method, when created
if __name__ = '__main__':
    clear()
    print("Hello. Welcome to Battleship!\nBienvenido a Battleship!")
    
    print("""                    ()
                    ||q',,'
                    ||d,~
         (,---------------------,)
          ',       q888p       ,'
            \       986       /
             \  8p, d8b ,q8  /
              ) 888a888a888 (
             /  8b` q8p `d8  \              O
            /       689       \             |','
           /       d888b       \      (,---------,)
         ,'_____________________',     \   ,8,   /
         (`__________L|_________`)      ) a888a (    _,_
         [___________|___________]     /___`8`___\   }*{
           }:::|:::::}::|::::::{      (,=========,)  -=-
   Samwise  '|::::}::|:::::{:|'  .,.    \:::|:::/    ~`~=
 --=~(@)~=-- '|}:::::|::{:::|'          ~".,."~`~
               '|:}::|::::|'~`~".,."
           ~`~".,."~`~".,                 "~`~".,."~
                          ".,."~`~""")
    print("Would you like to play a game?")
    response = input("Type anything into the console to continue. Type 'q' to quit: ")
    if response != 'q':
        game = Game()
        print("\n\nHello player 1!\n\n")
        random_or_place = None
        while not(random_or_place == 'r' or random_or_place == 'm'):
            random_or_place = input("Would you like a random ship arrangment ('r')\nor would you like to place ships manually('m'): ")
        if random_or_place == 'r':
            game.randomBoard()
            print("Here is your board: \n")
            game.printBoard()
            input("Type anything to the console to continue")
        else:
            game.printBoard()
            game.placeShips()
        if game.multi:
            game.player = game.togglePlayer()
            clear()
            time.sleep(0.3)
            print("Player 2, you're up!")
            random_or_place = None
            while not(random_or_place == 'r' or random_or_place == 'm'):
                random_or_place = input("Would you like a random ship arrangment ('r')\nor would you like to place ships manually('m'): ")
            if random_or_place == 'r':
                game.randomBoard()
                print("Here is your board: \n")
                game.printBoard()
                input("Type anything to the console to continue")
            else:
                game.printBoard()
                game.placeShips()
            clear()
            game.player = game.togglePlayer()
            game.fireShots()
        else:
            pass #AI not implemented
    