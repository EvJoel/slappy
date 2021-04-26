import json
import requests
import threading
import math
from datetime import *
from time import gmtime, strftime
import ast



global time_for_games 
time_for_games = False

global next_game_start
global check_score
global old_scores

global state 
state = 1






def getData():
    
    got_data = False
    
    
    #Try API request
    response = requests.get("https://nhl-score-api.herokuapp.com/api/scores/latest")
     
    #Check if request was successful
    if(response.status_code == 200):
        got_data = True
    else:
        
        print("error")
        
    #If request successful
    live_games = []
    upcoming_games = []
    final_games = []
    
    if(got_data):
        data = response.json()
        games = data.get('games')
        for game in games:
            #Create game id for tracking status
            team1 = game.get('teams').get('away').get('id')
            team2 = game.get('teams').get('home').get('id')
            game_id = str(team1)+"-"+str(team2)   
            game_state = game.get('status').get('state')
                
            if(game_state == "LIVE"):
                goals = str(game.get('goals'))
                live_games.append([game_id,goals])
                
            elif(game_state == "PREVIEW"):
                start_time = game.get('startTime')
                upcoming_games.append([game_id,start_time])
                    
            else:
                num_goals = len(game.get('goals'))
                start_time = game.get('startTime')
                final_games.append([game_id,num_goals,start_time])
                   
                
    print(live_games)
    return live_games,upcoming_games,final_games


def compareScores(curr_scores,old_scores):
    num_goals = []
    counter = 0
    #Iterate through current active games
    for score in curr_scores:
        #Check if # of active games has changed
       if(score[0] in [i[0] for i in old_scores]):
           #Check if scores has change in active game
           curr_goals_json =  ast.literal_eval(score[1])
           old_goals_json = ast.literal_eval(old_scores[counter][1])
           score_diff = len(curr_goals_json) - len(old_goals_json)
           if(score_diff > 0):
               #Add number of goals scored
               new_goals = curr_goals_json[-score_diff:]
               for goal in new_goals:
                   num_goals.append(goal.get('team'))
           
       else:
           pass
       counter += 1
    #Returns number of goals scores since last call
    return num_goals
           
        
           
def scoreGoal():
    #Activates goal scoring mechanism
    pass


def startup():
    global state
    global old_scores
    #Startup function, only runs once
    #Get current API data
    data = getData()
    scores  = data[0]
    upcoming = data[1]
    final = data[2]    
    old_scores = scores
    earliest_start = math.inf
    
   
    if(scores):
        #Check if any games are live
        #Switch to active game state
        state = 2
        print("Active Games")
        startGameTimer(120)
    elif(upcoming):
        #Check if any games are coming up
        current_time = datetime.now().isoformat()
        print("Upcoming games")
        #Find earliest starting game
        for game in upcoming:
            start_time = datetime.fromisoformat(game[1][:-1])
            difference = start_time - current_time
            if(difference < earliest_start):
                earliest_start = start_time
                
        #Start timer to activate once earliest game starts
        startWaitTimer(difference)
        print("Started wait timer, waiting for", difference, "seconds")
    else:
        print("No active games")
        
    
        
    

def startWaitTimer(interval):
    global wait_timer 
    wait_timer = threading.Timer(interval,checkStartTime)
    wait_timer.start()
    
def startGameTimer(interval):
    global game_timer 
    game_timer = threading.Timer(interval,checkScores)    
    game_timer.start()
    
def checkStartTime():
    global time_for_games
    time_for_games = True

def checkScores():
    global check_score
    check_score = True
    

    
           
    








if __name__ == "__main__":
    

    global next_game_start
    global check_score
    check_score = False
    global old_scores
    
    

    #Timer interval for idle state [s]
    wait_timer_interval = 3600
    #Timer interval for score updating [s]
    score_timer_interval = 120
    
    #Number of new goals scored
    new_goal_scored = 0
    
   #Run startup code 
    startup()
    
    while True:
        if(state == 1):
            #Idle state
            if(time_for_games):
                print("Games about to start...switching states")
                #Check if game has started
                state = 2
                startGameTimer(score_timer_interval)
            else:
                pass
                
                
            
            
        elif(state == 2):
            #Active games state, checking for scores
            
            if(check_score):
                print("Checking scores...")
                data = getData()
                curr_scores = data[0]
                if(curr_scores):
                    #Check if new goals have been scored
                    new_goal_scored = compareScores(curr_scores, old_scores)
                    print(new_goal_scored)
                    check_score = False
                    game_timer.cancel()
                    if(len(new_goal_scored) > 0):
                        print(new_goal_scored," goals scored...triggering mechanism")
                        state = 3
                    else:
                        print("No new goals scored...")
                    old_scores = curr_scores
                    startGameTimer(120)
                else:
                    state = 1
                
                
                
                
            
        
        
        elif(state == 3):
            for i in range(new_goal_scored):
                #Activate for each goal scored
                pass
            new_goal_scored = 0
            state = 2
           
        
        else:
            print("Invalid state")
        
    
   
