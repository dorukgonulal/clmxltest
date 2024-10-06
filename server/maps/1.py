# Import the following libraries
import requests
import folium
import folium.plugins
from folium import Map, TileLayer
from pystac_client import Client
import branca
import pandas as pd
import matplotlib.pyplot as plt
import os
temizlenmis_satirlar = []

# Dosya yolunu belirtin
with open("server/maps/datas.txt", "r") as dosya:
    ilk_satir = dosya.readline().strip()  # Dosyanın ilk satırını okur ve boşlukları temizler
    print(ilk_satir)
tarih = str(ilk_satir).split(",")
print(tarih)
# tarih = str(tarih).replace("[]", "")
# tarih = tarih.replace(" ", "")
# tarih = tarih.split(",")
# print(tarih)
# Provide the STAC and RASTER API endpoints
# The endpoint is referring to a location within the API that executes a request on a data collection nesting on the server.

# The STAC API is a catalog of all the existing data collections that are stored in the GHG Center.
STAC_API_URL = "https://earth.gov/ghgcenter/api/stac"

# The RASTER API is used to fetch collections for visualization
RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster"

# The collection name is used to fetch the dataset from the STAC API. First, we define the collection name as a variable
# Name of the collection for ODIAC dataset 
collection_name = "odiac-ffco2-monthgrid-v2023"

# Fetch the collection from the STAC API using the appropriate endpoint
# The 'requests' library allows a HTTP request possible
collection = requests.get(f"{STAC_API_URL}/collections/{collection_name}").json()

# Print the properties of the collection to the console
print(collection)

# Create a function that would search for a data collection in the US GHG Center STAC API

# First, we need to define the function
# The name of the function = "get_item_count"
# The argument that will be passed through the defined function = "collection_id"
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

# Apply the function created above "get_item_count" to the data collection
number_of_items = get_item_count(collection_name)

# Get the information about the number of granules found in the collection
items = requests.get(f"{STAC_API_URL}/collections/{collection_name}/items?limit={number_of_items}").json()["features"]

# Print the total number of items (granules) found
print(f"Found {len(items)} items")
available_dates = []

# Her bir öğeyi dolaşarak tarihleri çekin
for item in items:
    # "properties" altındaki "start_datetime" alanını yıl ve ay olarak alın
    date = item["properties"]["start_datetime"][:7]
    available_dates.append(date)

# Tekrarları kaldırmak için 'set' kullanarak listeyi güncelleyin
unique_dates = sorted(set(available_dates))

# Mevcut tarihleri yazdırın
print("Mevcut yıllar ve aylar:")
for date in unique_dates:
    print(date)
# Now we create a dictionary where the start datetime values for each granule is queried more explicitly by year and month (e.g., 2020-02)
items = {item["properties"]["start_datetime"][:7]: item for item in items} 

# Next, we need to specify the asset name for this collection
# The asset name is referring to the raster band containing the pixel values for the parameter of interest
# For the case of the ODIAC Fossil Fuel CO₂ Emissions collection, the parameter of interest is “co2-emissions”
asset_name = "co2-emissions"

# Fetching the min and max values for a specific item
rescale_values = {"max":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["max"], "min":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["min"]}


# Choose a color map for displaying the first observation (event)
# Please refer to matplotlib library if you'd prefer choosing a different color ramp.
# For more information on Colormaps in Matplotlib, please visit https://matplotlib.org/stable/users/explain/colors/colormaps.html
color_map = "rainbow" 

# Make a GET request to retrieve information for the 2020 tile
# 2020
january_2020_tile = requests.get(

    # Pass the collection name, the item number in the list, and its ID
    f"{RASTER_API_URL}/collections/{items[tarih[1]]['collection']}/items/{items[tarih[1]]['id']}/tilejson.json?"

    # Pass the asset name
    f"&assets={asset_name}"

    # Pass the color formula and colormap for custom visualization
    f"&color_formula=gamma+r+1.05&colormap_name={color_map}"

    # Pass the minimum and maximum values for rescaling
    f"&rescale={rescale_values['min']},{rescale_values['max']}", 

# Return the response in JSON format
).json()

# Print the properties of the retrieved granule to the console
print(january_2020_tile)

# Make a GET request to retrieve information for the 2000 tile
# 2000
january_2000_tile = requests.get(

    # Pass the collection name, the item number in the list, and its ID
    f"{RASTER_API_URL}/collections/{items[tarih[2]]['collection']}/items/{items[tarih[2]]['id']}/tilejson.json?"

    # Pass the asset name
    f"&assets={asset_name}"

    # Pass the color formula and colormap for custom visualization
    f"&color_formula=gamma+r+1.05&colormap_name={color_map}"

    # Pass the minimum and maximum values for rescaling
    f"&rescale={rescale_values['min']},{rescale_values['max']}", 

# Return the response in JSON format
).json()

# Print the properties of the retrieved granule to the console
print(january_2000_tile)

# To change the location, you can simply insert the latitude and longitude of the area of your interest in the "location=(LAT, LONG)" statement

# Set the initial zoom level and center of map for both tiles
# 'folium.plugins' allows mapping side-by-side
map_ = folium.plugins.DualMap(location=(34, -118), zoom_start=6)

# Define the first map layer (January 2020)
map_layer_2020 = TileLayer(
    tiles=january_2020_tile["tiles"][0], # Path to retrieve the tile
    attr="GHG", # Set the attribution
    opacity=0.8, # Adjust the transparency of the layer
)

# Add the first layer to the Dual Map
map_layer_2020.add_to(map_.m1)

# Define the second map layer (January 2000)
map_layer_2000 = TileLayer(
    tiles=january_2000_tile["tiles"][0], # Path to retrieve the tile
    attr="GHG", # Set the attribution
    opacity=0.8, # Adjust the transparency of the layer
)

# Add the second layer to the Dual Map
map_layer_2000.add_to(map_.m2)
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
#with open("anasayfa.html", "w", encoding="utf-8") as file:
 #   file.write(html_content)

#print("Ana sayfa oluşturuldu: anasayfa.html")