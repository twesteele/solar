#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# This used to take the ZHVI typical house prices at the County level for the whole US,
filter it down to just the counties in VA, and find the most recent typical house price
in each county. Additionally the FIPS code for each county is added. 

#INPUT: "ZHVI_counties.csv"
#OUTPUT: "va_county_house_prices.csv"

"""

import pandas as pd

# Filter to VA counties and get latest ZHVI price
df = pd.read_csv("ZHVI_counties.csv")
dfVA= df[df['StateName']=='VA'].reset_index() 
dfVAprice = dfVA.iloc[:,-1]                    
dfVA = dfVA.iloc[:,0:10]

# Wrangle together the FIPS code
dfVA['StateCodeFIPS'] = dfVA['StateCodeFIPS'].astype(str)
dfVA['MunicipalCodeFIPS'] = dfVA['MunicipalCodeFIPS'].astype(str).str.zfill(3)  
dfVA['fips']= dfVA['StateCodeFIPS']+dfVA['MunicipalCodeFIPS']

# Get the needed columns
dfVA_prices = pd.concat([dfVA, dfVAprice], axis=1)
dfVA_prices = dfVA_prices[['RegionName', 'fips', '2021-06-30']] 
dfVA_prices.columns = ['county', 'fips', 'ZHVI']

# Add data for Bedford City (missing)
dfVA_prices.loc[133] = ["Bedford City", "51515", "No Data Available" ] 

# Save to CSV file
dfVA_prices.to_csv("va_county_house_prices.csv", )