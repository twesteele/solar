#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# Used to extract the ZHVI forecasted prices
# INPUT: "ZHVI_counties_projected.csv.csv"
# OUTPUT: "forecasted_housing_prices.csv""
"""

import pandas as pd


df = pd.read_csv("ZHVI_counties_projected.csv")
dfVA= df[df['StateName']=='VA'].reset_index()
dfVAcounties = dfVA[12:]
#%%
dfVAcounties_other = dfVA[:12]
dfVAcounties_other['county'] = dfVAcounties_other['RegionName'].map(lambda x: x.rstrip(', VA'))
dfVAcounties_other['county'] = dfVAcounties_other['county'].astype(str) + ' City' 
dfVAcounties_other = dfVAcounties_other[['county', 'index', 'ForecastYoYPctChange' ]]
dfVAcounties_other.columns = ['county', 'ind', 'forecast']
#%%
dfVAcounties = dfVAcounties[['CountyName', 'index', 'ForecastYoYPctChange' ]]
dfVAcounties.columns = ['county', 'ind', 'forecast']
#%%

VA_forecast = pd.concat([dfVAcounties, dfVAcounties_other ]).reset_index(drop = True)
#%%
VA_forecast = VA_forecast.groupby(by="county" ).mean().reset_index()
VA_forecast = VA_forecast.round(1)
#%%
df2 = pd.DataFrame({'county':["Commonwealth of Virginia", "Bedford City", "Covington City", "Emporia City", "Fairfax City", "Falls Chruch City", "Galax City", "Lexington City", "Manassas City", "Fredericksburg City", "Williamsburg City"],
                    'ind'   :[0,0,0,0,0,0,0,0,0,0,0],
                    'forecast':["Not Available", "Not Available", "Not Available", "Not Available","Not Available", "Not Available","Not Available", "Not Available","Not Available", "Not Available", "Not Available"]})
                              
#%%                         
VA_forecast = pd.concat([df2,VA_forecast]).reset_index(drop = True)
#%%

VA_forecast = VA_forecast.sort_values(by = 'county').reset_index(drop = True)
VA_forecast = VA_forecast.drop([12,13]).reset_index(drop = True)


VA_forecast.to_csv("forecasted_housing_prices.csv", )
