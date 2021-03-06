#!/usr/bin/python3

import time
import sys
import copy

# match_size - number of teams to play each match. default of 2 - pairs.

def all_matchups_checks(teams,costs,match_size=2):
    if match_size < 2:
        print('Match size must be 2 or more')
        return None
    if len(teams)%match_size != 0:
        print('Number of teams must be a multiple of match_size - add a "bye" team if needed')
        return None
    
    return all_matchups(teams,costs,match_size)

def calc_cost(current_match_t,new_team,costs):
    cost = 0.0
    # for each team already in match:
    for ts in current_match_t:
        cost += costs[ts][new_team]
    return cost

# Function overview:
# 
# in: teams
# in: current match
# 
# for each remaining team:
#   add to current match, calculate new score
#   if score greater than max, go back up
#   if match has match_size teams, save score, continue down
#   otherwise, continue down

def all_matchups(teams,costs,match_size=2,score=0.0,current_match=[0.0]):
    global state_level,current_state
    
    # go 'down' the tree search one level:
    state_level += 1
    ws = ' '*state_level*4
    
    print(ws,'Calling all_matchups, new state_level: ',state_level)
    print(ws,'Teams left: ',len(teams))

    # if there aren't any teams left, go back up
    if len(teams) == 0:
        yield teams
        state_level += -1
        return
    
    # if no current match, start with first team in list:
    if len(current_match)<2:
        current_match.append([teams[0]])
        starting_index = 1
    else:
        starting_index = 0
        
    print(ws,'Current match: ',current_match)
    
    # for every other team in team list:
    for i in range(starting_index,len(teams)):
        # cost of current adding team to current match
        new_score = calc_cost(current_match[1],teams[i],costs)
        
        print(ws,'Cost to add team',teams[i],' to match:',new_score,current_match)
        print(ws,'score',score)
        # if total cost so far is less than global_max, keep going (otherwise no point in continuing)
        # global_max is updated in parent function when generator is called
        if new_score+score<global_max: # and s<50.0:
            # update score2 with total score so far
            score2 = new_score+score
                
            # add new team to the match
            current_match[0] += new_score
            current_match[1].append(teams[i])
            
            print(ws,'Accepted. Total score now: ',score2)
            print(ws,'Current match now: ',current_match)
            
            #if current match is incomplete:
            if len(current_match[1]) < match_size:
                # continue down the tree with remaining teams
                for rest in all_matchups(teams[starting_index:i]+teams[i+1:],costs,match_size,score2,current_match):
                    # if no teams left to try, go back up
                    if rest==None:
                        print(ws,'No teams left to try or global max reached.')
                        yield None
                    
                    # else, combine pairs from lower down, and go back up
                    else:
                        print(ws,'Passing only this up: ',rest)
                        yield rest
            else:
                # continue down with new match:
                print(ws,'New match')
                for rest in all_matchups(teams[starting_index:i]+teams[i+1:],costs,match_size,score2,[0.0]):
                    # if no teams left to try, go back up
                    if rest==None:
                        print(ws,'No teams left to try or global max reached.')
                        yield None
                    
                    # else, combine pairs from lower down, and go back up
                    else:
                        print(ws,'Passing this up: ',rest)
                        yield [current_match] + rest
                        
            # remove team from current_match?
            current_match[0] += -new_score
            current_match[1].pop()
            
        # else stop searching this branch and go back up
        else:
            print(ws,'Going back up, total score too high:',new_score+score )
            yield None
            
        #print 'SL',state_level,current_state,len(teams)
           
    # set current_state ??????
    current_state[state_level]=1
    
    # going back up a level so reduce state_level by 1
    state_level += -1
    print(ws,'End of function - going back up to state_level: ',state_level)




# Function that searches for set of pairings with lowest total cost
# ** NOTE ** this is recursive!
# ** NOTE ** the 'yield' command is tricky - later calls to this function will return to this spot!
# Inputs:
# teams - list of teams that haven't been paired yet - initially len n, but gets shorter
# costs - list of len n of list of len n (n x n marix of costs)
# score - total score so far
#
# Global variables:
# state_level - the "level" of the tree search. top level is 0, should go to n/2
# current_state - ??
#
# Function variables:
# ta - team number of first team in list - try to pair with every other team
# ml - ??
# s - cost of current pair match
# score2 - update this with score of current pair


# prepare list of teams before sending to all_matchups
# return best round

def best_matchups(teams,costs,reset_state,best_cost,best_state,match_size):
    # badness must be list of lists
    starttime = time.time()
    
    global global_max, current_state, state_level
    global_max = best_cost+1.0
    best_score = global_max
    state_level = -1
    current_state = [1 for i in range(0,len(teams))]
    best_match = None
    if reset_state!=None:
        current_state = reset_state
        if best_state!=None:
            best_match = best_state
        else:
            best_match = current_state
    
    print ('CURRENT STATE')
    print (len(current_state),len(teams))
    print (current_state)
    print ('  BEST STATE SO FAR ')
    print (best_state)
    
    # Create the generator function, that will be called later:
    #match_gen = all_pairs(teams,costs)
    match_gen = all_matchups(teams,costs,match_size)
    
    ct = 0
    ctn = 0
    better_found = False
    
    print ('Calling pair generator')
    
    for match in match_gen:
        print ('TEST',current_state,'Best so far?',match!=None)
        if match != None:
            print (match)
            ct+=1
            score = 0.0
            for gme in match:
                score+=gme[0]
            if score<best_score:
                best_score = score
                best_match = copy.deepcopy(match)
                best_state = [c for c in current_state]
                global_max = best_score
                better_found = True
        else:
            ctn+=1
        
        # ???? not sure why this is here
        if ctn%1000000==0:
            if ctn>0 and ctn%1000000==0:
                print ("<p>",'STATUS:',ct,ctn,best_score,round(time.time()-starttime,1),'s',"</p>")
        
        # this bit was to exit if it took too long to calculate? more than 240.0 seconds?
        
        #if ctn%10000==0 and round(time.time()-starttime)>240.0:
        #    print ("<p>",'STATUS:',ct,ctn,best_score,round(time.time()-starttime,1),'s',"</p>")
        #    print ("<p>",'STATUS:',best_match,'s',"</p>")
        #    print ("<p>",'TAKING TOO LONG - JSON-EXITING',"</p>")
        #    return [best_state,current_state]
        #    break

    print ('Time taken: ',round(time.time()-starttime,1))

    return [best_state,best_match]


if __name__ == '__main__':
    # Testing:
    import random
    
    teams = [0,1,2,3,4,5]
    
    random.seed(2)
    
    costs = []
    for i in range(len(teams)):
        costs.append([])
        for j in range(len(teams)):
            #costs[i].append(random.randint(0,10))
            costs[i].append(10.0-abs(i-j))

    best_state = None
    current_state = None
    best_cost = 99999.0
    match_size = 3

    print ('DEBUG ')
    print (teams)
    for i in range(len(costs)):
        print (costs[i])
    print (best_state)
    print (current_state)
    print (best_cost)

    results = best_matchups(teams,costs,current_state,best_cost,best_state,match_size)

    print ('AFTER RUNNING ')
    print (best_state)
    print (current_state)
    print (best_cost)
    print (results)


