#Import the required libraries
import altair as alt
import pandas as pd
import streamlit as st
import folium 
from streamlit_folium import folium_static 
from shapely.geometry import Point, Polygon
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import json
from urllib.request import urlopen


#%%
# Load the county polygons
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

l = [v for v in counties['features'] if v['properties']['STATE']=='51']

#Change the county names to include either county or city (some cities are themselves counties in VA)
for i in l:
    if i['properties']['LSAD']=='city':
        i['properties']['NAME']=i['properties']['NAME']+" City"
    if i['properties']['LSAD']=='County':
        i['properties']['NAME']=i['properties']['NAME']+" County"
l = sorted(l, key = lambda i: i['properties']['NAME'])

# dictionary of the polygons and other features
va_polygons = {"type": "FeatureCollection", "features": l}

#get the list of county names
county_names = [i['properties']['NAME'] for i in va_polygons['features']]
county_names.insert(0, "Commonwealth of Virginia")

#fix Accomack county - it has small islands which confuses folium
va_polygons['features'][0]['geometry']['coordinates']=va_polygons['features'][0]['geometry']['coordinates'][0]
va_polygons['features'][0]['geometry']['type'] = 'Polygon'

#%%
# Load the pre-processed data

house_prices = pd.read_csv("va_county_house_prices.csv")
ghi_df = pd.read_csv("GHIsums_all.csv")
install_costs = pd.read_csv("install_costs.csv")
forecasted_prices = pd.read_csv("forecasted_housing_prices.csv")
ghi_statewide = pd.read_csv("county_ghi_means.csv")


with open("intro.txt", "r") as intro:
    intro_ = intro.read()
    intro.close()
    
with open("ghi_explainer.txt", "r") as ghi_explainer:
    ghi_explainer_ = ghi_explainer.read()
    ghi_explainer.close()



#%% 
# Streamlit Sidebar and Title 
st.set_page_config(layout="wide")
st.title("New Solar Installation Planning")
st.markdown("Select A County from the Dropdown Menu")
expander = st.expander("Explanation of GHI")
expander.write(ghi_explainer_)

st.sidebar.header('Select A County')
county_input = st.sidebar.selectbox(
                    "Select a County",
                    county_names
                    )


city = st.sidebar.text_input("Enter a City", "Input a City")
st.sidebar.header('Data Sources')
st.sidebar.markdown(intro_)

#%%

def county_display(county_input , city_input ):
    
    geolocator = Nominatim(user_agent="GTA Lookup")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    
    if city_input == "NA":
        COUNTYind = county_names.index(county_input) - 1
        county_name_ = county_input
    if county_input == "NA":
        location = geolocator.geocode(city_input+ ", Virginia, United States")
        geo_detail = geolocator.reverse((location.latitude, location.longitude))
        county_name = [i for i in geo_detail.address.split(",") if "County" in i]
        
        if len(county_name) == 1:
            county_name_ = county_name[0].lstrip()
            if county_name_ in county_names:
                COUNTYind = county_names.index(county_name_) - 1
            if county_name_ not in county_names:
                return st.markdown("Sorry, that's not a valid Entry")
            
        if len(county_name) !=1:
            county_name_ = city_input+" City"
            if county_name_ in county_names:
               COUNTYind = county_names.index(county_name_) - 1
            if county_name_ not in county_names:
               return st.markdown("Sorry, that's not a valid Entry")
            
    COORDS = va_polygons['features'][COUNTYind]['geometry']['coordinates']
    COORDS = COORDS[0]
    COORDS = [(i[1], i[0]) for i in COORDS]
    poly = Polygon(COORDS)
    c_point = poly.centroid
    center_point = [c_point.x, c_point.y]

    COUNTY = va_polygons['features'][COUNTYind]
    m = folium.Map(location = center_point, 
                   tiles='OpenStreetMap', 
                   width= 350, 
                   height=350,
                   zoom_start=10.0)

    county_lines = folium.GeoJson(COUNTY, style_function = lambda x: {'color': 'black','weight': 1.0,'fillOpacity': 0},
    	name='counties').add_to(m)

    # Add hover functionality.
    style_function = lambda x: {'fillColor': '#ffffff', 
                                'color':'#000000', 
                                'fillOpacity': 0.1, 
                                'weight': 0.1}
    highlight_function = lambda x: {'fillColor': '#000000', 
                                    'color':'#000000', 
                                    'fillOpacity': 0.50, 
                                    'weight': 0.1}

    county_lines.add_child(folium.features.GeoJsonTooltip(['NAME'], labels=False))
    

    ind_list = []
    for index, point in ghi_df.iterrows():
        p = Point([point['lat'], point['lon']])
        if p.within(poly):
            ind_list.append(index)
            
    df2 = ghi_df.loc[ind_list, :] 
    df2['colorM'] = pd.cut(df2['data'], bins = 4, labels=[ "#FFCC00", "#FF9900", "#FF0000", "#990000"])
    
    for index, point in df2.iterrows():
        folium.CircleMarker([point['lat'], point['lon']], fill = True, color = point['colorM'], radius=6).add_to(m)

    coord_df = pd.DataFrame(va_polygons['features'][COUNTYind]['geometry']['coordinates'][0])
    sw = coord_df[[1 , 0]].min().values.tolist()
    ne = coord_df[[1 , 0]].max().values.tolist()
    m.fit_bounds(([sw,ne]))
    
    legend_df = {'a':["a","a","a","a"],
                 'b':[ 0.25, 0.25,0.25, 0.25], 
                 'c' : ["#FFCC00", "#FF9900", "#FF0000", "#990000"]
                 }
    
    
    legend_df = pd.DataFrame(legend_df)
    alt.renderers.set_embed_options(actions=False)
    
    chart = alt.Chart(legend_df).mark_bar(size=10).encode( alt.X('a', axis=None), 
                                                   alt.Y('b',axis = alt.Axis(tickCount=0, 
                        title="Lower                                                                    Higher")), 
                                                   color = alt.Color('c', scale = None),
                                                   
                                                   )
    
    
    
    county_price = house_prices[house_prices['county']==county_name_]
    price = county_price.iloc[:,-1].item()
    if price != "No Data Available":
        price = str(int(float(price)))
        price = "$" + price
    
    increase = forecasted_prices[forecasted_prices ['county']==county_name_]
    increase_pct = increase.iloc[:,-1].item()
    if increase_pct != "Not Available":
        increase_pct = increase_pct + "%"
    
    county_install_price = install_costs[install_costs['county']==county_name_]
    install_price = str(county_install_price.iloc[:,-1].item())
    if install_price != "No Estimate":
        install_price = "$" + install_price
    
    st.markdown("""<style>.big-font {font-size:50px !important;}</style>""",
                unsafe_allow_html=True)


    try:
        col1, col2, col3 = st.columns((2,1,2))
        col1.header(county_name_ +" Relative GHI")
        with col1: folium_static(m) 
        col2.header("GHI Legend")
        with col2: st.altair_chart(chart) 
        col3.header(county_name_ + " Typical House Price")
        with col3: st.markdown('<p class="big-font">{price}</p>'.format(price=price), 
                           unsafe_allow_html=True), st.header(county_name_ + " Projected Annual Appreciation"), st.markdown(
                               '<p class="big-font">{price}</p>'.format(price=increase_pct), 
                           unsafe_allow_html=True), st.header(county_name_ + " Average System Cost (5kW)"), st.markdown(
                               '<p class="big-font">{price}</p>'.format(price=install_price), unsafe_allow_html=True)
        
        
    except:
        pass
 
#%%
if county_input == "Commonwealth of Virginia" and city == "Input a City":
    
    
    point = [38.003, -79.42]
    m = folium.Map(location = point, tiles='OpenStreetMap', zoom_start=7.0)
    county_lines = folium.GeoJson(va_polygons, style_function = lambda x: {'color': 'black','weight': 1.0,'fillOpacity': 0},
	name='counties').add_to(m)
    
    
    
    ghi_statewide['fips'] = ghi_statewide['fips'].astype(str)
    ghi_statewide['ghi'] = ghi_statewide['ghi']/365*2
    
    choro = folium.features.Choropleth(va_polygons,
                           data = ghi_statewide,
                           columns = ["fips", "ghi"], 
                           key_on ='feature.id', 
                           fill_color='YlOrRd',
                           legend_name = "Average GHI (kWh/m^2)",
                           highlight = True,
                           name = "AvgGHI",
         
                           ).add_to(m)
    
    choro.geojson.add_child(folium.features.GeoJsonTooltip(['NAME'], labels=False))
    
    folium_static(m)


if county_input != "Commonwealth of Virginia"  and city == "Input a City":
    county_display(county_input, "NA")

if  city != "Input a City" and county_input == "Commonwealth of Virginia":
    county_display("NA", city)



        
    
    
    
    