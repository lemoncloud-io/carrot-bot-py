################################################################
## Sycn index from ES5 to ES6 ##################################
## Author: tony@lemoncloud.io ##################################
## First commit: 24.May.2018 ###################################
################################################################

import requests
from requests.exceptions import HTTPError
import time
import csv
import time
import json


micro_server = "http://micro.lemoncloud.io"
local_server = "http://localhost"
poolsAPI = ":8084/item-pools/"
elasticAPI = ":8081/elastic/"
elastic6API = ":8081/elastic6/"

# 1) Get ES5 index which NS's val equals 'SG'
def getES5IndexfromRemote(ns,_type,_page):
    # Ex. http://micro.lemoncloud.io:8081/elastic/bot-v1?ns=SG
    url = micro_server+elasticAPI

    _limit =1

    try:
        
        r = requests.get(url + "bot-v1?ns="+ns+"&type="+_type+"&$limit="+str(_limit)+"&$page="+str(_page))
        r.raise_for_status()

        hits = r.json()['result']['hits']['hits']
        
        #return result
        if len(hits) == 0: 
            return {}

        source = hits[0]['_source']
        return source

    except HTTPError:
        print("Error: getListfromRemote() failed (Status Code:",r.status_code,")")
        raise HTTPError

    return {}

# 2) Set ES6 index
def setES6Index(data,_id,_type):
    # Ex. echo '{"A":"a"}' | http POST 'http://localhost:8081/elastic6/bot-v1/0/push?$type=item-pool'
    url = micro_server+elastic6API + "bot-v1/"+_id+"/push?$type="+_type
    print ("url:",url)

    try:
        r = requests.post(url, json = data)
        r.raise_for_status()

    except HTTPError:
        print("Error: setES6Index() failed (Status Code:",r.status_code,")")
        raise HTTPError


def main():
    page = -1
    while True:
        page = page +1
        try:
            # 1) Get ES5 index where ns='SG' and type='ONED'
            sg_data = getES5IndexfromRemote('SG','ONED',page)

            if len(sg_data) == 0:
                break

            print(sg_data)
            print(page)
            
            # 2) Set ES6 index
            _id = sg_data['id']
            setES6Index(sg_data,_id,'item-pool')

        except HTTPError:
            print("Error: Terminated abnormally by HTTPError")
        
        # Sleep 1 sec to avoid heavy load on the website
        time.sleep(1)


if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))