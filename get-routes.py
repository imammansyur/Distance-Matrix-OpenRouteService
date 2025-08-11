import os
import time
from time import sleep
import datetime
import json
import requests
import pandas as pd

def latitude(n):
    return df['latitude'].values[n]
    
def longitude(n):
    return df['longitude'].values[n]

def coordinate(x):
    strcoordinate = [str(latitude(x)), str(longitude(x))]
    return ','.join((strcoordinate))
    
def save_csv(arr):
    df_distance = pd.DataFrame(arr)
    df_distance.to_csv('distance-matrix.csv', header=False, index=False)
    
def check_counter(count):
    #to deal with limited api quota
    # if count%39==0 and count>0:
        # print("Maximum quota every minute has reached, waiting for 1 minute.")
        # sleep(60)
    if count%1995==0 and count>0:
        print("Maximum daily quota has reached, waiting for 1 day.")
        sleep(86400)
        
def counter_add(count):
    count+=1
    return count

def route(a, b, count):
    url = 'https://api.openrouteservice.org/v2/directions/driving-car?api_key={}&start={}&end={}'.format(os.getenv('ors_key'),coordinate(a),coordinate(b))
    
    status = None
    sleep_time = 3
    # print(a,b, count)
    
    while status != 200:
    # for i in range(5):
        try:
            check_counter(count)
            counter = counter_add(count)
            
            response = requests.get(url)
            status = response.status_code
            print(a, b, response)
        except Exception as e:
            print(e)
        if status != 200:
            print(a, b, response, response.content)
            sleep(sleep_time)
            sleep_time *= 2
            
    with open("response/response_{}-{}_{}.json".format(a,b,datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")), "wb") as f:
        f.write(response.content)
    
    response = response.json()
    distance[a][b] = response['features'][0]['properties']['summary']['distance']

def main():
    global df
    df = pd.read_csv('coordinates.csv')
    
    global distance
    distance = pd.read_csv('distance.csv', header=None, index_col=False).to_numpy()
    
    global counter
    counter = 0

    os.makedirs("response", exist_ok=True)

    for n, row in df.iterrows():
        for m, row in df.iterrows():        
            if n==m:
                distance[n][m] = 999999
                save_csv(distance)
            elif distance[n][m]==0:
                route(n, m, counter)
                save_csv(distance)
                
if __name__ == "__main__":
    main()
