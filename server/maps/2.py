# Import the following libraries
import requests
import folium
import folium.plugins
from folium import Map, TileLayer
from pystac_client import Client
import branca
import pandas as pd
import matplotlib.pyplot as plt
import time
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
    <iframe src="2.html" title="Harita"></iframe>
</body>
</html>
"""

# Dosya olarak kaydetme
# with open("maps.html", "w", encoding="utf-8") as file:
 #    file.write(html_content)

print("Ana sayfa oluşturuldu: maps.html")

# # Texas, USA
# texas_aoi = {
#     "type": "Feature", # Create a feature object
#     "properties": {},
#     "geometry": { # Set the bounding coordinates for the polygon
#         "coordinates": [
#             [
#                 # [13.686159004559698, -21.700046934333145],
#                 # [13.686159004559698, -23.241974326585833],
#                 # [14.753560168039911, -23.241974326585833],
#                 # [14.753560168039911, -21.700046934333145],
#                 # [13.686159004559698, -21.700046934333145],
#                 [-95, 29], # South-east bounding coordinate
#                 [-95, 33], # North-east bounding coordinate
#                 [-104,33], # North-west bounding coordinate
#                 [-104,29], # South-west bounding coordinate
#                 [-95, 29]  # South-east bounding coordinate (closing the polygon)
#             ]
#         ],
#         "type": "Polygon",
#     },
# }

# # Create a new map to display the generated polygon
# # We'll plug in the coordinates for a location
# # central to the study area and a reasonable zoom level
# aoi_map = Map(

#     # Base map is set to OpenStreetMap
#     tiles="OpenStreetMap",

#     # Define the spatial properties for the map
#     location=[
#         30,-100
#     ],

#     # Set the zoom value
#     zoom_start=6,
# )

# # Insert the polygon to the map
# folium.GeoJson(texas_aoi, name="Texas, USA").add_to(aoi_map)

# # Visualize the map

# # Check total number of items available within the collection
# items = requests.get(
#     f"{STAC_API_URL}/collections/{collection_name}/items?limit=300"
# ).json()["features"]

# # Print the total number of items (granules) found
# print(f"Found {len(items)} items")

# # The bounding box should be passed to the geojson param as a geojson Feature or FeatureCollection
# # Create a function that retrieves information regarding a specific granule using its asset name and raster identifier and generates the statistics for it

# # The function takes an item (granule) and a JSON (polygon) as input parameters
# def generate_stats(item, geojson):

#     # A POST request is made to submit the data associated with the item of interest (specific observation) within the boundaries of the polygon to compute its statistics
#     result = requests.post(

#         # Raster API Endpoint for computing statistics
#         f"{RASTER_API_URL}/cog/statistics",

#         # Pass the URL to the item, asset name, and raster identifier as parameters
#         params={"url": item["assets"][asset_name]["href"]},

#         # Send the GeoJSON object (polygon) along with the request
#         json=geojson,

#     # Return the response in JSON format
#     ).json()

#     # Return a dictionary containing the computed statistics along with the item's datetime information.
#     return {
#         **result["properties"],
#         "start_datetime": item["properties"]["start_datetime"][:7],
#     }



# # Zaman ölçümünü başlat
# start_time = time.time()

# # Fonksiyon çalıştırma ve istatistikleri toplama
# stats = [generate_stats(item, texas_aoi) for item in items[:50]]

# # Zaman ölçümünü bitir ve sonucu göster
# end_time = time.time()
# print(f"Execution time: {end_time - start_time:.2f} seconds")

# # Create a function that converts statistics in JSON format into a pandas DataFrame
# def clean_stats(stats_json) -> pd.DataFrame:

#     # Normalize the JSON data
#     df = pd.json_normalize(stats_json)

#     # Replace the naming "statistics.b1" in the columns
#     df.columns = [col.replace("statistics.b1.", "") for col in df.columns]

#     # Set the datetime format
#     df["date"] = pd.to_datetime(df["start_datetime"])

#     # Return the cleaned format
#     return df

# # Apply the generated function on the stats data
# df = clean_stats(stats)

# # Display the stats for the first 5 granules in the collection in the table
# # Change the value in the parenthesis to show more or a smaller number of rows in the table

# # Figure size: 20 representing the width, 10 representing the height
# fig = plt.figure(figsize=(20, 10))


# plt.plot(
#     df["date"], # X-axis: sorted datetime
#     df["max"], # Y-axis: maximum CO₂ level
#     color="red", # Line color
#     linestyle="-", # Line style
#     linewidth=0.5, # Line width
#     label="Max monthly CO₂ emissions", # Legend label
# )

# # Display legend
# plt.legend()

# # Insert label for the X-axis
# plt.xlabel("Years")

# # Insert label for the Y-axis
# plt.ylabel("CO2 emissions gC/m2/d")

# # Insert title for the plot
# plt.title("CO2 emission Values for Texas, Dallas (2000-2022)")

# ###
# # Add data citation
# plt.text(
#     df["date"].iloc[0],           # X-coordinate of the text
#     df["max"].min(),              # Y-coordinate of the text




#     # Text to be displayed
#     "Source: NASA ODIAC Fossil Fuel CO₂ Emissions",                  
#     fontsize=12,                             # Font size
#     horizontalalignment="right",             # Horizontal alignment
#     verticalalignment="top",                 # Vertical alignment
#     color="blue",                            # Text color
# )

# # Plot the time series
# plt.show()