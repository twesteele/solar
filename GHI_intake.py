#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#Used to extract raw GHI point data for the inter county and intra county GHI heatmaps and filter to only points in VA
INPUT: raw GHI csvs in GHIs folder and va_coords.txt
OUTPUT: GHIsums_all.csv and GHImeans_all.csv
"""

import pandas as pd
import os
from shapely.geometry import Point, Polygon
import ast
import numpy as np

#%%

GHI_sum_list = []
GHI_mean_list = []
directory = "GHIs"
for root,dirs,files in os.walk(directory):
    for file in files:
        if file.endswith("2020.csv"):
            df = pd.read_csv(directory+"/"+file)
            locID = df['Location ID'][0]
            lat = float(df['Latitude'][0])
            lon = float(df['Longitude'][0])
            df1 = df.iloc[2:,0:6].reset_index(drop=True)
            df1 = df1.apply(pd.to_numeric)
            df1.columns = ['year', 'month', 'day', 'hour', 'minute', 'GHI']
            df1['GHI'] = df1['GHI'].replace(0, np.NaN)
            df1sum = df1.groupby(["month", "day"]).sum()
            df1mean = df1.groupby(["month", "day"]).mean()
            sumGsum = sum(df1sum['GHI'])
            sumGmean = sum(df1mean['GHI'])
            GHI_sum_dict = {'locID':locID, 'lat': lat, 'lon': lon, 'data': sumGsum}
            GHI_mean_dict = {'locID':locID, 'lat': lat, 'lon': lon, 'data': sumGmean}
            GHI_sum_list.append(GHI_sum_dict)
            GHI_mean_list.append(GHI_mean_dict)



#%%

with open("va_coords.txt", 'r') as f:
    mylist = ast.literal_eval(f.read())
f.close()
mylist2 = list(mylist[0])
mylist3 = [[i[1], i[0]] for i in mylist2]
mylist4 = [tuple(i) for i in mylist3]

poly = Polygon(mylist4)
###

#Used to find se and nw corners for the app
coord_df = pd.DataFrame(mylist4)
sw = coord_df[[1 , 0]].min().values.tolist() # [-83.6753949997662, 36.5408560001517]
ne = coord_df[[1 , 0]].max().values.tolist() # [-75.1664349995895, 39.4660119998373]

#%%
GHIsums = []
for i in GHI_sum_list:
    p = Point(i['lat'], i['lon'])
    if p.within(poly):
        GHIsums.append(i)
        
GHImeans = []
for i in GHI_mean_list:
    p = Point(i['lat'], i['lon'])
    if p.within(poly):
        GHImeans.append(i)


#%%

GHIsums_df = pd.DataFrame(GHIsums)
GHImeans_df = pd.DataFrame(GHImeans)

#%%
GHIsums_df.to_csv("GHIsums_all.csv", )
GHImeans_df.to_csv("GHImeans_all.csv", )


