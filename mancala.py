#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 23:26:10 2020

@author: adamwasserman
"""

import numpy as np
import copy

class Board:
    def __init__(self,board = 4 * np.ones((2,6),dtype='int8'), bucket = np.zeros(2,dtype='int8'), player = 0):
        self.bucket = bucket
        self.board = board
        self.player = player
        
    def move(self, start):
        count,self.board[start] = self.board[start],0
        row = start[0]
        col = start[1]
        gain = 0
        
        while count > 0:
            
            if row == 0:
                col -= 1
                count -= 1
                if col < 0:
                    if self.player == 0:
                        self.bucket[0] += 1
                        gain += 1
                        
                        #Post-adding to bucket logic
                        if count == 0:
                            return True, gain#New turn; start from anywhere
                        count -= 1 #If added to bucket, subtract 1 again!
                    row = 1
                    col = 0
            else:
                #row = 1
                col += 1
                count -= 1
                if col > 5:
                    if self.player == 1:
                        self.bucket[1] += 1
                        gain += 1
                        
                        if count == 0:
                            return True, gain
                        count -= 1
                    row = 0
                    col = 5
            
            self.board[row,col] += 1
            if count == 0 and self.board[row,col] > 1:
                count = self.board[row,col]
                self.board[row,col] = 0
        
        self.player = 1 if self.player == 0 else 0
        return False,gain
    
    def simulate(self):
        res = []
        row = self.player
        for col in range(6):#6 is the number of columns
            path = [col]
            next_move = Board(copy.copy(self.board),bucket = np.zeros(2,dtype = 'int8'),player = self.player)
            again,gained = next_move.move((row,col))
            if again:
                add_path, add_gain = next_move.simulate() # recursive call
                path += add_path
                gained += add_gain
            
            res.append([path,gained])
        
        return max(res, key = lambda x: x[1])

    def printBoard(self):
        print("Board representation: ")
        print(" ".join([str(num) for num in self.board[0]]))
        print(" ".join([str(num) for num in self.board[1]]))
    

if __name__ == '__main__':
    game = Board()
    print("Let's play Mancala!")
    while sum(game.board[0,:]) != 0 and sum(game.board[0,:]):
        usr_input = input(f"""
   It's player {game.player+1} turn.
   Type the column you wish to move
   Type 'b' to see a repsentation of the board.
   Type 'sim' to see how you can win the most points.
   To see the score, type 'score'.
   To quit, type 'q'.
   Your input: """)
        if usr_input == 'q':
            break
        elif usr_input == 'b':
            game.printBoard()
        elif usr_input == 'sim':
            path,points = game.simulate()
            print(f"Gain {points} point(s) by moving along the following columns:")
            print(", ".join([str(num+1) for num in path]))
        elif usr_input == 'score':
            print(f"\nPlayer 1: {game.bucket[0]}")
            print(f"Player 2: {game.bucket[1]}")
        elif 0 < int(usr_input) <= 6:
            col = int(usr_input) - 1
            move_again, gain = game.move((game.player,col))
            print(f"Player {game.player+1} gained {gain} points!")
            print(game.board)
        else:
            print("Column out of bounds")
    
            
            
        
