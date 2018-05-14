#########################################################
## Sync pull horse info via lemon bot api and horse api##
## Author: tony@lemoncloud.io ###########################
## First commit: 14.May.2018 ############################
#########################################################

import requests
from requests.exceptions import HTTPError
import time

#dev_server = "http://idev.lemoncloud.io"
local_server = "http://localhost"
botAPI = ":8080/bots/"
horseAPI = ":8087/horse/"

server = local_server

# 1) Get horse list from remote and save into csv
def saveListfromRemote():
    # Ex. http://localhost:8080/bots/4135
    url = server+botAPI
    page = 0

    while True:
        page = page + 1
        data = {"pg":page}
        try:
            r = requests.post(url + "4135",json = data)
            r.raise_for_status()
        except HTTPError:
            if page ==1: # Error from the beginning
                print("Error: saveListfromRemote() failed (Status Code:",r.status_code,")")
                raise HTTPError
            else: # Task done
                print("Info: total page =",page-1)
                break
        
        print("Info: extracting page",page)

        # Sleep 1 sec to avoid heavy load on the website
        time.sleep(1)
        


# 2) Get mabun list from csv file
def getListfromCSV():
    # Ex. http://localhost:8080/bots/4129
    url = server+botAPI
    data = {"type":"racehorse"}
    
    try:
        r = requests.post(url + "4129",json = data)
        r.raise_for_status()
    except HTTPError:
        print("Error: getListfromCSV() failed (Status Code:",r.status_code,")")
        raise HTTPError

    # Original data is formatted like 
    # {"result":{"horses":{"name":"가나도라","mabun":"037283"}}}
    # We want only "mabun" data!
    horse_list = r.json()["result"]["horses"]
    return list(map(lambda x: x["mabun"],horse_list))

# 3) Sync pull horse info using mabun list
def doSyncpull(mabun):
    kr_mabun = "KR" + mabun
    # Ex. http://localhost:8087/horse/KR037283/sync-pull
    url = server+horseAPI+kr_mabun+"/sync-pull"

    try:
        r = requests.get(url)
        r.raise_for_status()
    except HTTPError:
        print("Error: doSyncpull() failed (Status Code:",r.status_code,")")
        raise HTTPError

    print("Info: sync-pull mabun",mabun)
    # Sleep 1 sec to avoid heavy load on the website
    time.sleep(1)

def main():
    try:
        # 1) Get horse list from remote and save into csv
        saveListfromRemote()

        # 2) Get mabun list from csv file
        mabun_list = getListfromCSV()
        
        # 3) Sync pull horse info using mabun list
        for index, mabun in enumerate(mabun_list):
            print("(",index +1 ,"/",len(mabun_list),")",end=" ")
            doSyncpull(mabun)

    except HTTPError:
        print("Error: Terminated abnormally by HTTPError")

    print("Info: Sync-pull is completed successfully")

if __name__ == "__main__":
    main()