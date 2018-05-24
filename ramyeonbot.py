################################################################
## Sync-pull ramyeon info via lemon bot api and item-pools-api##
## Author: tony@lemoncloud.io ##################################
## First commit: 17.May.2018 ###################################
################################################################

import requests
from requests.exceptions import HTTPError
import time
import csv
import time

#dev_server = "http://idev.lemoncloud.io"
local_server = "http://localhost"
botAPI = ":8080/bots/"
poolsAPI = ":8084/item-pools/"

server = local_server

# 1) Get list from remote and save into csv
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
                        # Append id to list
                        ramyeon_list.append(node)
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
        print("Error: getDetailInfo() failed (Status Code:",r.status_code,")")
        raise HTTPError
    
    return detail_info

# 3) create item using ramyeon info
def doCreateItem(detailInfo,nv_mid):
    ns_mid = "NS" + str(detailInfo['mid'])
    
    # !important! Link nv_mid(item mid) to detail info
    detailInfo['nv_mid'] = nv_mid
    
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

# save Node to CSV
# file name: nv_mid{nv_mid}.csv
def saveNodeToCSV(nv_mid,nodes):
    filename = "nv_mid:" + str(nv_mid) + ".csv"

    f = open(filename, 'w', encoding='utf-8', newline='')
    wr = csv.writer(f)
    wr.writerow(["id", "name", "mall", "price", "delivery"])
    for node in nodes:
            wr.writerow([node["id"],node["name"],node["mall"],node["price"],node["delivery"]])

    f.close()

def main():
    nv_mids = [
        5640980426, #오뚜기 진라면 매운맛 120g //600
        5640996976, #오뚜기 진라면 순한맛 120g //427
        6359445024, #오뚜기 진라면 매운맛 110g //499
        5716182795, #오뚜기 진라면컵 순한맛 65g //365
        5716181948, #오뚜기 진라면컵 매운맛 65g //334
        6344210326, #삼양 불닭볶음면 140g     //259
        5639964597, #농심 신라면 120g        //934
        5757233945, #농심 신라면블랙 130g     //155
        5648380638, #농심 신라면 65g         //595
        5648381071, #농심 신라면 큰사발면 114g //464

        # 8583124560, #오뚜기 진라면 순한맛 110g //39
        # 1185307259, #삼양라면 120g          //??
        # 13046260762, #삼양 까르보 불닭볶음면 130g //26
        # 13753480413, #삼양 짜장 불닭볶음면 140g //42
    ]

    for index, nv_mid in enumerate(nv_mids):
        # Print progress
        print(nv_mid,"(",index +1 ,"/",len(nv_mids),")")

        try:
            # 1) Get ramyeon from remote and save it into array
            mall_list = getListfromRemote(nv_mid)
            #print(mall_list)
            

            # 1-1) save mall_list to csv
            # Save node to csv
            saveNodeToCSV(nv_mid,mall_list)   

            # For Test
            #mall_list = ['13851053793']
        
            # 2) Get detail ramyeon info from bot
            for mall in mall_list:
                ns_id = mall['id']
                detailInfo = getDetailInfo(ns_id)
                
                # 3) Create item using ramyeon info
                doCreateItem(detailInfo,nv_mid)

        except HTTPError:
            print("Error: Terminated abnormally by HTTPError")

        print("Info: Create with niv_md",nv_mid," is completed successfully")
    
    print("Info: All completed successfully")

if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))