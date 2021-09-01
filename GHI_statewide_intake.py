#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# Used to get the average GHI per county
#INPUT: va polygons('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') 
        and GHImeans_all.csv
        
#Output: "county_ghi_means.csv"

"""
import pandas as pd
from shapely.geometry import Point, Polygon
from urllib.request import urlopen
import json

ghi_df = pd.read_csv("GHImeans_all.csv")

with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

l = [v for v in counties['features'] if v['properties']['STATE']=='51']

for i in l:
    if i['properties']['LSAD']=='city':
        i['properties']['NAME']=i['properties']['NAME']+" City"
    if i['properties']['LSAD']=='County':
        i['properties']['NAME']=i['properties']['NAME']+" County"
        
l = sorted(l, key = lambda i: i['properties']['NAME'])

county_names = [i['properties']['NAME'] for i in l]
county_names.insert(0, "Commonwealth of Virginia")

va = {"type": "FeatureCollection", "features": l}
va['features'][0]['geometry']['coordinates']=va['features'][0]['geometry']['coordinates'][0]

#%%

ind_list = []
for i in range(0,len(va['features'])):
    NAME = va['features'][i]['properties']['NAME']
    ID = va['features'][i]['id']
    COORDS = va['features'][i]['geometry']['coordinates']
    COORDS = COORDS[0]
    COORDS = [(i[1], i[0]) for i in COORDS]
    poly = Polygon(COORDS)
    plist =[]
    for index, point in ghi_df.iterrows():
        p = Point([point['lat'], point['lon']])
        if p.within(poly):
            plist.append(index)
    ind_list.append({NAME:plist,"id": ID})
#%%
county_ghi_all = []
for i in range(0, len(ind_list)):
    inds = list(ind_list[i].values())
    county_ghi = ghi_df.iloc[inds[0], : ]
    county_mean = county_ghi['data'].mean()
    county_ghi_all.append({'county':list(ind_list[i].keys())[0], 'ghi':county_mean, 'fips': list(ind_list[i].values())[1]})
    
#%%
county_ghi_df = pd.DataFrame(county_ghi_all)
#%%
county_ghi_df.to_csv("county_ghi_means.csv", )

#%%


        
    