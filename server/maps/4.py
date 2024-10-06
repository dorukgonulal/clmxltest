# Import the following libraries
import requests
import folium
import folium.plugins
from folium import Map, TileLayer 
from pystac_client import Client 
import branca 
import pandas as pd
import matplotlib.pyplot as plt
from tabulate import tabulate
import os
# Provide the STAC and RASTER API endpoints
# The endpoint is referring to a location within the API that executes a request on a data collection nesting on the server.
temizlenmis_satirlar = []

with open("server/maps/datas.txt", "r") as dosya:
    ilk_satir = dosya.readline().strip()  # Dosyanın ilk satırını okur ve boşlukları temizler
    print(ilk_satir)
tarih = str(ilk_satir).split(",")
print(tarih)
# The STAC API is a catalog of all the existing data collections that are stored in the GHG Center.
STAC_API_URL = "https://earth.gov/ghgcenter/api/stac"

# The RASTER API is used to fetch collections for visualization
RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster"

# The collection name is used to fetch the dataset from the STAC API. First, we define the collection name as a variable 
# Name of the collection for ECCO Darwin CO₂ flux monthly emissions
collection_name = "eccodarwin-co2flux-monthgrid-v5"

# Fetch the collection from the STAC API using the appropriate endpoint
# The 'requests' library allows a HTTP request possible
collection = requests.get(f"{STAC_API_URL}/collections/{collection_name}").json()

# Print the properties of the collection to the console

# Provide the STAC and RASTER API endpoints
# The endpoint refers to a location within the API that executes a request on a data collection nesting on the server.

# The STAC API is a catalog of all the existing data collections stored in the GHG Center.
STAC_API_URL = "https://earth.gov/ghgcenter/api/stac/"

# The RASTER API is used to fetch collections for visualization.
RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster/"

# The collection name is used to fetch the dataset from the STAC API. First, you must define the collection name as a variable. 
# The collection name in the STAC API
collection_name = "eccodarwin-co2flux-monthgrid-v5"

# Fetch the collection from the STAC API using the appropriate endpoint
# The 'requests' library allows a HTTP request possible
collection = requests.get(f"{STAC_API_URL}/collections/{collection_name}").json()

# Print the properties of the collection in a table
# Adjust display settings
pd.set_option('display.max_colwidth', None)  # Set maximum column width to "None" to prevent cutting off text

# Extract the relevant information about the collection
collection_info = {
    "Title": collection.get("title", "N/A"), # Extract the title of the collection 
    "Description": collection.get("description", "N/A"), # Extract the dataset description
    "Temporal Extent": collection.get("extent", {}).get("temporal", {}).get("interval", "N/A"), # Extract the temporal coverage of the collection
    "Spatial Extent": collection.get("extent", {}).get("spatial", {}).get("bbox", "N/A"), # Extract the spatial coverage of the collection
}

# Convert the derived information into a DataFrame format
properties_table = pd.DataFrame(list(collection_info.items()), columns=["Collection Summary", ""])

# Display the properties in a table
collection_summary = properties_table.style.set_properties(**{'text-align': 'left'}) \
                                           .set_table_styles([
    {
        'selector': 'th.col0, td.col0',    # Select the first column
        'props': [('min-width', '200px'),  # Set a minimum width
                  ('text-align', 'left')]  # Align text to the left
    },
    {
        'selector': 'td.col1',             # Select the second column
        'props': [('text-align', 'left')]  # Align text to the left
    }
])

# Print the collection summary table

# Create a function that would search for data collection in the US GHG Center STAC API

# First, we need to define the function
# The name of the function is "get_item_count" 
# The argument that will be passed to the defined function is "collection_id"
def get_item_count(collection_id):

    # Set a counter for the number of items existing in the collection 
    count = 0 

    # Define the path to retrieve the granules (items) of the collection of interest in the STAC API
    items_url = f"{STAC_API_URL}/collections/{collection_id}/items" 

    # Run a while loop to make HTTP requests until there are no more URLs associated with the collection in the STAC API
    while True:

        # Retrieve information about the granules by sending a "get" request to the STAC API using the defined collection path 
        response = requests.get(items_url) 

        # If the items do not exist, print an error message and quit the loop
        if not response.ok:
            print("error getting items")
            exit()

        # Return the results of the HTTP response as JSON
        stac = response.json()

        # Increase the "count" by the number of items (granules) returned in the response
        count += int(stac["context"].get("returned", 0))

        # Retrieve information about the next URL associated with the collection in the STAC API (if applicable)
        next = [link for link in stac["links"] if link["rel"] == "next"]

        # Exit the loop if there are no other URLs
        if not next:
            break
        
        # Ensure the information gathered by other STAC API links associated with the collection are added to the original path
        # "href" is the identifier for each of the tiles stored in the STAC API
        items_url = next[0]["href"]

    # Return the information about the total number of granules found associated with the collection
    return count

# Apply the function created above "get_item_count" to the Air-Sea CO2 Flux ECCO-Darwin collection
number_of_items = get_item_count(collection_name)

# Get the information about the number of granules found in the collection
items = requests.get(f"{STAC_API_URL}/collections/{collection_name}/items?limit={number_of_items}").json()["features"]

# Print the total number of items (granules) found
print(f"Found {len(items)} observations")

# Sort the items based on their date-time attribute
items_sorted = sorted(items, key=lambda x: x["properties"]["start_datetime"])

# Create an empty list
table_data = []
# Extract the ID and date-time information for each granule and add them to the list
# By default, only the first 5 items in the collection are extracted to be displayed in the table. 
# To see the date-time of all existing granules in this collection, remove "5" from "item_sorted[:5]" in the line below. 
for item in items_sorted[:5]:
    table_data.append([item['id'], item['properties']['start_datetime']])

# Define the table headers
headers = ["Item ID", "Start Date-Time"]

print("Below you see the first 5 items in the collection, along with their item IDs and corresponding Start Date-Time.")

# Print the table using tabulate
print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))

# Once again, apply the function created above "get_item_count" to the collection
# This step allows retrieving the number of granules “observations” in the collection.
number_of_items = get_item_count(collection_name)
items = requests.get(f"{STAC_API_URL}/collections/{collection_name}/items?limit={number_of_items}").json()["features"]

# Now you need to create a dictionary where the start datetime values for each granule are queried more explicitly by year and month (e.g., 2020-02)
items = {item["properties"]["start_datetime"]: item for item in items}

# Next, you need to specify the asset name for this collection.
# The asset name refers to the raster band containing the pixel values for the parameter of interest.
# For the case of this collection, the parameter of interest is “co2”.
asset_name = "co2"

# Fetch the minimum and maximum values for the CO2 value range
rescale_values = {"max":0.0007, "min":-0.0007}

# Choose a color map for displaying the first observation (event)
# Please refer to matplotlib library if you'd prefer to choose a different color ramp.
# For more information on Colormaps in Matplotlib, please visit https://matplotlib.org/stable/users/explain/colors/colormaps.html
color_map = "magma"


# You can retrieve the first observation of interest by defining the last 6 digits of its Item ID. 
# The numbers indicate the year and month (YYYYMM) when the data was gathered.
# For example, the observation collected in December 2022 has the following item ID: eccodarwin-co2flux-monthgrid-v5-202212 
# To set the time, you will need to insert "202212" in the line below. 


# Set the time
# If you want to select another time, you can refer to the Data Browser on the U.S. Greenhouse Gas Center website  
# URL to the Air-Sea CO2 Flux ECCO-Darwin collection in the US GHG Center: https://dljsq618eotzp.cloudfront.net/browseui/#eccodarwin-co2flux-monthgrid-v5/
observation_date_1 = '202212'


# Don't change anything here
observation_1 = f'eccodarwin-co2flux-monthgrid-v5-{observation_date_1}'


# Make a GET request to retrieve information for the December 2022 tile
# A GET request is made for the December 2022 tile.
december_2022_tile = requests.get(

    # Pass the collection name, the item number in the list, and its ID
    f"{RASTER_API_URL}/collections/{items[list(items.keys())[0]]['collection']}/items/{items[list(items.keys())[0]]['id']}/tilejson.json?"

    # Pass the asset name
    f"&assets={asset_name}"
    
    # Pass the color formula and colormap for custom visualization
    f"&color_formula=gamma+r+1.05&colormap_name={color_map}"
    
    # Pass the minimum and maximum values for rescaling 
    f"&rescale={rescale_values['min']},{rescale_values['max']}"),# Choose a color map for displaying the first observation (event)
# Please refer to matplotlib library if you'd prefer to choose a different color ramp.
# For more information on Colormaps in Matplotlib, please visit https://matplotlib.org/stable/users/explain/colors/colormaps.html
color_map = "magma"


# You can retrieve the first observation of interest by defining the last 6 digits of its Item ID. 
# The numbers indicate the year and month (YYYYMM) when the data was gathered.
# For example, the observation collected in December 2022 has the following item ID: eccodarwin-co2flux-monthgrid-v5-202212 
# To set the time, you will need to insert "202212" in the line below. 


# Set the time
# If you want to select another time, you can refer to the Data Browser on the U.S. Greenhouse Gas Center website  
# URL to the Air-Sea CO2 Flux ECCO-Darwin collection in the US GHG Center: https://dljsq618eotzp.cloudfront.net/browseui/#eccodarwin-co2flux-monthgrid-v5/
observation_date_1 = '202212'


# Don't change anything here
observation_1 = f'eccodarwin-co2flux-monthgrid-v5-{observation_date_1}'


# Make a GET request to retrieve information for the December 2022 tile
# A GET request is made for the December 2022 tile.
december_2022_tile = requests.get(
    # Pass the collection name, the item number in the list, and its ID
    f"{RASTER_API_URL}/collections/{items[list(items.keys())[0]]['collection']}/items/{items[list(items.keys())[0]]['id']}/tilejson.json?"
    # Pass the asset name
    f"&assets={asset_name}"
    # Pass the color formula and colormap for custom visualization
    f"&color_formula=gamma+r+1.05&colormap_name={color_map}"
    # Pass the minimum and maximum values for rescaling 
    f"&rescale={rescale_values['min']},{rescale_values['max']}"
).json()  # Move .json() here


# Print the properties of the retrieved granule to the console
print(december_2022_tile)
    
    # Return the response in JSON format
    # 
# You will repeat the same approach used in the previous step to retrieve the second observation of interest
observation_date_2 = '202104'


# Don't change anything here
observation_2 = f'eccodarwin-co2flux-monthgrid-v5-{observation_date_2}'


# Make a GET request to retrieve information for the December 2022 tile
# A GET request is made for the April 2021 tile.
april_2021_tile = requests.get(

    # Pass the collection name, the item number in the list, and its ID
    f"{RASTER_API_URL}/collections/{items[list(items.keys())[20]]['collection']}/items/{items[list(items.keys())[20]]['id']}/tilejson.json?"

    # Pass the asset name
    f"&assets={asset_name}"
    
    # Pass the color formula and colormap for custom visualization
    f"&color_formula=gamma+r+1.05&colormap_name={color_map}"
    
    # Pass the minimum and maximum values for rescaling 
    f"&rescale={rescale_values['min']},{rescale_values['max']}").json()


# Print the properties of the retrieved granule to the console
print(april_2021_tile)

# To change the location, you can simply insert the latitude and longitude of the area of your interest in the "location=(LAT, LONG)" statement

# Set the initial zoom level and center of map for both tiles
# 'folium.plugins' allows mapping side-by-side
map_ = folium.plugins.DualMap(location=(34, -118), zoom_start=7)


# Define the first map layer with the CO2 Flux data for December 2022
map_layer_1 = TileLayer(
    tiles=december_2022_tile["tiles"][0], # Path to retrieve the tile
    attr="GHG", # Set the attribution 
    name='December 2022 CO2 Flux', # Title for the layer
    overlay=True, # The layer can be overlaid on the map
    opacity=0.8, # Adjust the transparency of the layer
)
# Add the first layer to the Dual Map 
map_layer_1.add_to(map_.m1)


# Define the second map layer with the CO2 Flux data for April 2021
map_layer_2 = TileLayer(
    tiles=april_2021_tile["tiles"][0], # Path to retrieve the tile
    attr="GHG", # Set the attribution 
    name='April 2021 CO2 Flux', # Title for the layer
    overlay=True, # The layer can be overlaid on the map
    opacity=0.8, # Adjust the transparency of the layer
)
# Add the second layer to the Dual Map 
map_layer_2.add_to(map_.m2)


# Display data markers (titles) on both maps
folium.Marker((40, 5.0), tooltip="both").add_to(map_)

# Add a layer control to switch between map layers
folium.LayerControl(collapsed=False).add_to(map_)

# Add a legend to the dual map using the 'branca' library
# Note: the inserted legend is representing the minimum and maximum values for both tiles
# Minimum value = -0.0007, maximum value = 0.0007
colormap = branca.colormap.LinearColormap(colors=["#0000FF", "#3399FF", "#66CCFF", "#FFFFFF", "#FF66CC", "#FF3399", "#FF0000"], vmin=-0.0007, vmax=0.0007) 

# Add the data unit as caption 
colormap.caption = 'Millimoles per meter squared per second (mmol m²/s)'

# Define custom tick values for the legend bar
tick_val = [-0.0007, -0.00035, 0, 0.00035, 0.0007]

# Create a HTML representation
legend_html = colormap._repr_html_()

# Create a customized HTML structure for the legend
legend_html = f'''
<div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; width: 400px; height: auto; background-color: rgba(255, 255, 255, 0.8);
             border-radius: 5px; border: 1px solid grey; padding: 10px; font-size: 14px; color: black;">
    <b>{colormap.caption}</b><br>
    <div style="display: flex; justify-content: space-between;">
        <div>{tick_val[0]}</div> 
        <div>{tick_val[1]}</div> 
        <div>{tick_val[2]}</div> 
        <div>{tick_val[3]}</div> 
        <div>{tick_val[4]}</div> 
    </div>
    <div style="background: linear-gradient(to right,
                {'#0000FF'}, {'#3399FF'} {20}%,
                {'#3399FF'} {20}%, {'#66CCFF'} {40}%,
                {'#66CCFF'} {40}%, {'#FFFFFF'} {50}%,
                {'#FFFFFF'} {50}%, {'#FF66CC'} {80}%,
                {'#FF66CC'} {80}%, {'#FF3399'}); height: 10px;"></div>
</div>
'''

# Display the legend and caption on the map
map_.get_root().html.add_child(folium.Element(legend_html))
os.remove("server/templates/1.html")
# Visualize the Dual Map
map_.save("server/templates/1.html")


html_content = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>Ana Sayfa</title>
    <style>
        body {
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .content {
            display: flex;
            justify-content: space-between;
            width: 100%;
        }
        h2 {
            flex: 1;
            text-align: center;
        }
        iframe {
            width: 600px;
            height: 400px;
            border: none;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="content">
        <h2>1. bölge</h2>
        <h2>2. bölge</h2>
    </div>
    <iframe src="1.html" title="Harita"></iframe>
</body>
</html>
"""

# Dosya olarak kaydetme
# with open("anasayfa.html", "w", encoding="utf-8") as file:
#     file.write(html_content)

# print("Ana sayfa oluşturuldu: anasayfa.html")
