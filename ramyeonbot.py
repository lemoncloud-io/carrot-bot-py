################################################################
## Sync-pull ramyeon info via lemon bot api and item-pools-api##
## Author: tony@lemoncloud.io ##################################
## First commit: 17.May.2018 ###################################
################################################################

import requests
from requests.exceptions import HTTPError
import time

#dev_server = "http://idev.lemoncloud.io"
local_server = "http://localhost"
botAPI = ":8080/bots/"
poolsAPI = ":8084/item-pools/"

server = local_server

# 1) Get horse list from remote and save into csv
def getListfromRemote(nv_mid):
    # Ex. http://localhost:8080/bots/60
    url = server+botAPI
    page = 0

    ramyeon_list = []

    while True:
    #while page < 1:
        page = page + 1
        data = {"mid":nv_mid,"page":page,"max_page":page}

        try:
            r = requests.post(url + "60",json = data)
            r.raise_for_status()

            result = r.json()['result']
            # If node doesn't exist, stop looping.
            if 'nodes' not in result:
                
                break
            else:
                nodes = result['nodes']
                for index,node in enumerate(nodes):
                    if 'rank' in node:
                        ramyeon_list.append(node['id'])
                        print("Info: index:",index,"/page:",page)

        except HTTPError:
            print("Error: getListfromRemote() failed (Status Code:",r.status_code,")")
            raise HTTPError
        print("Info: extracting page",page)

        # Sleep 1 sec to avoid heavy load on the website
        time.sleep(1)

    return ramyeon_list

# 2) Get detail ramyeon info from bot
def getDetailInfo(id):
    # Ex. http://localhost:8080/bots/54
    url = server+botAPI
    
    detail_info = {}

    data = {"mid":id}
    
    try:
        r = requests.post(url + "54",json = data)
        r.raise_for_status()

        result = r.json()['result']
        detail_info = result
    except HTTPError:
        print("Error: getListfromRemote() failed (Status Code:",r.status_code,")")
        raise HTTPError
    
    return detail_info

# 3) create item using ramyeon info
def doCreateItem(detailInfo):
    ns_mid = "NS" + str(detailInfo['mid'])
    # Ex. http://localhost:8084/item-pools/NS13851053793
    url = server+poolsAPI+ns_mid

    data = detailInfo

    try:
        r = requests.post(url, json = data)
        r.raise_for_status()
    except HTTPError:
        print("Error: doCreateItem() failed (Status Code:",r.status_code,")")
        raise HTTPError

    print("Info: doCreateItem ns_mid",ns_mid)

    # Sleep 1 sec to avoid heavy load on the website
    time.sleep(1)

def main():
    try:
        # 1) Get ramyeon from remote and save it into array
        nv_mid = 5640980426
        mall_list = getListfromRemote(nv_mid) # 5640980426: 진라면 매운맛
        print(mall_list)
        
        # For Test
        #mall_list = ['13851053793']
    
        # 2) Get detail ramyeon info from bot
        for ns_id in mall_list:
            detailInfo = getDetailInfo(ns_id)
            
            # !important! Link nv_mid(item mid) to detail info
            detailInfo['nv_mid'] = nv_mid
            
            print(detailInfo)
    
            # 3) Create item using ramyeon info
            doCreateItem(detailInfo)

    except HTTPError:
        print("Error: Terminated abnormally by HTTPError")

    print("Info: Create is completed successfully")

if __name__ == "__main__":
    main()