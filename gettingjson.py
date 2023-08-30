import requests
import json
import time

#Input your ballchasing API token
TOKEN = "BWsWZPP2dFC4bl4EYPMqyiyroJKeuhH9NubD32a0"
AUTH = {"Authorization": TOKEN}

#Input uploader
uploader = "76561199225615730" 
requestLink = "https://ballchasing.com/api/replays?uploader=" + uploader

corename = 'C:\\RocketLeagueReplays\\ID_JSON_new\\' + uploader



noMoreRequestLinks = False


for i in range (0,1000):
    
    isResponseCallValid = False
    
    
    while isResponseCallValid == False and noMoreRequestLinks == False:
        
        filename = corename + "_" + str(i)
    
        newname = filename + ".json"
        
        replayids = requests.get(requestLink,headers=AUTH)
            
        jsonreplayids = replayids.json()
        
        jsonresponse_string = json.dumps(jsonreplayids)
        
        if replayids.status_code == 200:
            
            isResponseCallValid = True

            print("Downloaded file " + newname)
            
            if "next" in jsonreplayids:
                requestLink = jsonreplayids['next']
            
            else:
                print("No more request links!")
                noMoreRequestLinks = True
        
            with open(newname, "+w") as outfile:
                outfile.write(jsonresponse_string)
            
        else:
            print("Invalid response code... Waiting")
            time.sleep(0.1)