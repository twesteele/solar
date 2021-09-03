# Solar Capstone Streamlit App

The intention of this project was to create a webapp that intergrates data on 
solar irradiance, solar installation costs, and housing prices (current and
projected) to provide a tool for prospective home buyers that are interested in 
installing solar panels on their new home. The motivatation for doing this concurrently
with buying a new home is that these costs can often be rolled into the mortgage 
when buying the home. Currently the app is only focused on the state of Virginia 
at the county level. 

## Data

NREL's NSRDB data was downloaded using the Data Viewer at https://maps.nrel.gov/nsrdb-viewer . 
The 2020 PSM v3 data comes as modelled prediction of GHI in half hour intervals over the course
of a year for points on a 0.02*0.02 lat/long grid. Since the viewer selector is a rectangle,
grid points outside the boundaries of VA were filtered out using shapely. This is done
in  `GHI_intake.py`. GHI was then summed and averaged at the month/day grouping. 
The mean value of GHI for grid point location were subsequently filtered/assigned to 
the counties within which they are located, and averaged together to give a daily
average of GHI for each county across the entire state (`GHI_statewide.py`). The sum 
for each grid point within a county are used as a relative measure of which points
had a higher cumulative GHI over the course of the year. 

Zillow housing prices and appreciation forecasts come in from the Zillow Home Value Index metric
 which is a measure associated with the "typical house price" for a single 
 Family Residence (https://www.zillow.com/research/data/). Historical county prices
 come filtered to counties in VA, and the most recent ZHVI price was used ('housing_prices_intake.py`).
 Projected year over year appreciation was grouped by counties in VA and averaged and some
 missing counties were filled in ( 'housing_prices_projected_intake.py'). 
 Solar installation costs were scraped manually from EnergySage.com (`install_costs.csv`).


## App
The app uses streamlit to show the county differences in GHI for the entire state of VA.
By selecting a county from the dropdown, one can see the relative differences in GHI between gridpoints
in each county, the current housing prices, projected appreciation, and average cost of installing a 5kW system
in each county. Going forward, additional years of GHI data will be added, as well as predictions of 
future GHI for each county. 


