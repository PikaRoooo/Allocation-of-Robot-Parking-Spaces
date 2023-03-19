#Created on 20 May 2021 - Author Roopika Ravikanna - University of Lincoln, England
#This script contains 5 diffrent ranking techniques to allocate parking spaces to Autonomous Agri Robots waiting on Pickers

import itertools
import random
import numpy as np
import statistics
import math
#import thread
import time
import simpy
import pygame as pg


#Random Rank function
def random_rank():
    for picker in pickers: #for each of the picker repeat this

        x = pickers.index(picker) #picker indices stored in a local variable
	#print(x)
        random_row_number = random.randint(1,n_rows) #a row is randomly allocated to a picker
        
        current_row_picker = random_row_number
        picker_rows.append(current_row_picker)

        #print(picker + ' has been alloted with row %d' %current_row_picker) #print row number of the picker
        
        global median_row
    median_row = random.randint(1,n_rows)
    #print('randomly alloted parking row is ',median_row)
	

#Cumulative Rank function
def cumulative_rank():

    for picker in pickers: #for each of the picker repeat this

        x = pickers.index(picker) #picker indices stored in a local variable
	#print(x)
        random_row_number = random.randint(1,n_rows) #a row is randomly allocated to a picker
        
        current_row_picker = random_row_number
        picker_rows.append(current_row_picker)

        #print(picker + ' has been alloted with row %d' %current_row_picker) #print row number of the picker

	#calculate row-wise ranking priority of the picker

        current_pick_row = current_row_picker - 1

        rank[current_pick_row,x] = 1 #first rank given to the current row of the picker

        right_rows = n_rows - current_row_picker #number of rows to the right of the current row
	
	#rankings given for the rows to the right of the current row
        for i in range(1,right_rows+1):
               
            rank[current_pick_row+i,x] = i+1
               
        left_rows = current_row_picker - 1 #number of rows to the left of the current row

	#rankings given for the rows to the left of the current row
        for i in range(1, left_rows+1):
           
            rank[current_pick_row-i,x] = i+1
    
       
        #print(picker)
        #print(rank)
        sum_of_rank = np.sum(rank, axis = 1)
        #print("Sum of rank : ",sum_of_rank)
        min_rank = min(sum_of_rank)
        sum_of_rank_2 = sum_of_rank[sum_of_rank != min_rank]
        min_rank_2 = min(sum_of_rank_2)
        sum_of_rank_3 = sum_of_rank_2[sum_of_rank_2 != min_rank_2]
        min_rank_3 = min(sum_of_rank_3)

        min_rank_list = np.where(sum_of_rank == min_rank)
        min_rank_list_2 = np.where(sum_of_rank_2 == min_rank_2)
        min_rank_list_3 = np.where(sum_of_rank_3 == min_rank_3)

        median_rank = statistics.median(min_rank_list[0])
        median_rank_2 = statistics.median(min_rank_list_2[0])
        median_rank_3 = statistics.median(min_rank_list_3[0])
        global median_row
        
    median_row = math.floor(median_rank)+1 #best spot
    median_row_2 = math.floor(median_rank_2)+1 #2nd best spot
    median_row_3 = math.floor(median_rank_3)+1 #3rd best spot

    #global ps 
    ps = [median_row, median_row_2, median_row_3]
    return ps
    #print('parking spot preference 1 is ',ps[0])
    #print('parking spot preference 2 is ',ps[1])
    #print('parking spot preference 3 is ',ps[2])

#The below function simulates picking action of the pickers along with the service provided by the robots for transportation
def picking(name, row, picking_time, env, robot):
    
    for i in range(1,len(pick_points)+1):
        #print('%s arriving at %.1f' % (name, env.now))
        #print('%s is in row%d pick point%d at %.1f' %(name, row, i, env.now))
        
        yield env.timeout(picking_time)

        if i%5 == 0:
            #print('%s requesting robot' %name)
            with robot.request() as req:
                start = env.now
                yield req            
                random_num = random.randint(0,2)
                #ranks = cumulative_rank()

                #robot_row = int(ranks[random_num])
                robot_row = int(random.randint(1,n_rows)) #--- standard parking (hash out above two lines)
                #robot_row = int(ps[random_num])
                row_diff = abs(robot_row - row)
                spaces_to_move = (row_diff+i)*2
                yield env.timeout(spaces_to_move*robot_speed)
                
                #print('%s has been served by the robot in %.1f seconds.' % (name, env.now - start))

#The below function generates pickers according to the pre-defined parameters
def picker_generator(env, robot):

    for i in pickers:
        picker_number = i[-1]
        picker_number = int(picker_number)
        row = picker_rows[picker_number-1]
        picking_time = time_of_picker[picker_number-1]
        yield env.timeout(0)
    
        #print('picker%d generated and is in row%d has a picking time of %d' %(picker_number, row, picking_time))
        env.process(picking('picker%d' % picker_number, row, picking_time, env, robot))


# Setup and start the simulation
print('Allocation of Parking Spaces to Robots and their performance')


rows = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20] #Add as many rows as needed
n_rows = len(rows) #number of rows

pickers = ['picker1','picker2','picker3','picker4','picker5'] #Add as many pickers as needed
n_pickers = len(pickers)#number of pickers stored

time_of_picker = [2,2,2,2,2]#time taken by each of the pickers to move form one node to another - can be different from one another (could use random.randint)
pick_points = [1,2,3,4,5,6,7,8,9,10]#Add as many WayPoints in each row
n_pick_points = len(pick_points)#number of WayPoints in each row

picker_rows = []#Empty list to store the randomly allocated rows to pickers
rank = np.zeros(((n_rows), len(pickers)))#Empty list to store rank allocations to all rows by each of the pickers

list_sum_of_rank=[] #Empty list to store rank aggregate values
robot_speed = 0.5 #Specify time taken for robot movement from one WayPoint to another

n_exp = 10 #Specify Number of test simulations in the experiment
tt = 0 #Variable to store Total Time of Experiments

make_video = False

median_row = 0 #storage variable of parking space
#Choose one of the ranking functions and comment out the rest

rank_type = 2 #choose rank_type = 1 for random_rank function (Randomly allocates header of one of the rows as the parking space)
#rank_type = 2 #choose rank_type = 2 for middle_rank function (Allocates the header of the middle row or centre row amongst a given series of rows as the parking space)
#rank_type = 3 #choose rank_type = 3 for distance_rank function (The distance in between the pickers is considered and parking space is alloted as the header of the centre row amidst the largest gap found #between them)
#rank_type = 4 #choose rank_type = 4 for cumulative_rank function (Each of the pickers gives out its preferred ranking of parking spaces to each of the rows, parking space is alloted to the row haeder #with the best rank (lowest aggregate rank)
#rank_type = 5 #choose rank_type = 3 for speed_based_cumulative_rank function (Similar to the cumulative rank but the faster pickers are prioritised over the slower pickers while aggregating the #cumulative rank)

#Simulations carried out for the specified number of times with the pre-defined picker and farm parameters using the chosen ranking algorithm

print('Parking Spaces are allocated according to Ranking Type ', rank_type)
print('1 - Standard Parking, 2 - Smart Parking')

for n in range(n_exp):
    if rank_type == 1:
        random_rank()
        # Create environment and start processes
        env = simpy.Environment()
        robot = simpy.Resource(env, 2)
        very_start = env.now
        env.process(picker_generator(env, robot))
        # Execute!
        env.run()
        
        print("Total task completion time: {}".format(env.now))
        tt = tt + env.now
        picker_rows = []
        
    elif rank_type == 2 :
        cumulative_rank()
        # Create environment and start processes
        env = simpy.Environment()
        robot = simpy.Resource(env, 2)
        very_start = env.now
        env.process(picker_generator(env, robot))
        # Execute!
        #do_animation()


        env.run()
        
        print("Total task completion time: {}".format(env.now))
        tt = tt + env.now
        picker_rows = []

    else:
        print("Enter Admissible Rank Type")

at = tt/n_exp #Average Task Completion Time
#print(tt)
print('Average Task Completion Time is %d' %at)

    
