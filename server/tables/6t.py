import requests
import folium
import folium.plugins
from folium import Map, TileLayer
from pystac_client import Client
import pandas as pd
import matplotlib.pyplot as plt
import time
import openai
import requests
import ast

openai.api_key = "sk-6qcxsNFps32b65Mk30Rozfg_Q_oCyTArWbd-VpY6VgT3BlbkFJmeOVl2IctpXAfskxdZewTqp_rPNFoIJPxGFt1ieLkA"

with open("server/tables/datas.txt", "r") as dosya:
    ilk_satir = dosya.readline().strip()  # Dosyanın ilk satırını okur ve boşlukları temizler
    print(ilk_satir)
bolge = str(ilk_satir).split(",")
print(bolge)

completion = openai.ChatCompletion.create(
    model="gpt-4-turbo",
    messages=[
        {"role": "system", "content": """
                Şimdi sana bazı şehirler ülke veya bölgeler yazacağım. Örneğin İstanbul:
[
    [29.5, 40.7],
    [29.5, 41.3],
    [28.5, 41.3],
    [28.5, 40.7],
    [29.5, 40.7]
]
Çıktılar bu formmatta ver yazı yazmadan sadece değerleri ver.
        """},
        {"role": "user", "content": str(bolge[0])}
    ]
)
        # Yanıtı al
result = completion.choices[0].message['content']


print(result)


list_data = ast.literal_eval(result)






# Provide the STAC and RASTER API endpoints
# The endpoint is referring to a location within the API that executes a request on a data collection nesting on the server.

# The STAC API is a catalog of all the existing data collections that are stored in the GHG Center.
STAC_API_URL = "https://earth.gov/ghgcenter/api/stac"

# The RASTER API is used to fetch collections for visualization
RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster"

# The collection name is used to fetch the dataset from the STAC API. First, we define the collection name as a variable
# Name of the collection for CEOS National Top-Down CO₂ Budgets dataset 
collection_name = "oco2-mip-co2budget-yeargrid-v1"

collection = requests.get(f"{STAC_API_URL}/collections/{collection_name}").json()

asset_name = "ff" #fossil fuel

# Create a polygon for the area of interest (aoi)
texas_aoi = {
    "type": "Feature", # Create a feature object
    "properties": {},
    "geometry": { # Set the bounding coordinates for the polygon
        "coordinates": [
            list_data
        ],
        "type": "Polygon",
    },
}

# Create a new map to display the generated polygon
# We'll plug in the coordinates for a location
# central to the study area and a reasonable zoom level
aoi_map = Map(

    # Base map is set to OpenStreetMap
    tiles="OpenStreetMap",

    # Define the spatial properties for the map
    location=[
        30,-100
    ],

    # Set the zoom value
    zoom_start=6,
)

# Insert the polygon to the map
folium.GeoJson(texas_aoi, name="Texas, USA").add_to(aoi_map)

# Visualize the map

# Check total number of items available within the collection
items = requests.get(
    f"{STAC_API_URL}/collections/{collection_name}/items?limit=600"
).json()["features"]

# Print the total number of items (granules) found
print(f"Found {len(items)} items")

# The bounding box should be passed to the geojson param as a geojson Feature or FeatureCollection
# Create a function that retrieves information regarding a specific granule using its asset name and raster identifier and generates the statistics for it

# The function takes an item (granule) and a JSON (polygon) as input parameters
def generate_stats(item, geojson):

    # A POST request is made to submit the data associated with the item of interest (specific observation) within the boundaries of the polygon to compute its statistics
    result = requests.post(

        # Raster API Endpoint for computing statistics
        f"{RASTER_API_URL}/cog/statistics",

        # Pass the URL to the item, asset name, and raster identifier as parameters
        params={"url": item["assets"][asset_name]["href"]},

        # Send the GeoJSON object (polygon) along with the request
        json=geojson,

    # Return the response in JSON format
    ).json()

    # Print the result
    print(result)

    # Return a dictionary containing the computed statistics along with the item's datetime information.
    return {
        **result["properties"],
        "datetime": item["properties"]["start_datetime"],
    }

# Generate a for loop that iterates over all the existing items in the collection
for item in items:

    # The loop will then retrieve the information for the start datetime of each item in the list
    print(item["properties"]["start_datetime"])

    # Exit the loop after printing the start datetime for the first item in the collection
    break

start_time = time.time()

# Fonksiyon çalıştırma ve istatistikleri toplama
stats = [generate_stats(item, texas_aoi) for item in items[:25]]

# Zaman ölçümünü bitir ve sonucu göster
end_time = time.time()
print(f"Execution time: {end_time - start_time:.2f} seconds")

# Create a function that converts statistics in JSON format into a pandas DataFrame
def clean_stats(stats_json) -> pd.DataFrame:

    # Normalize the JSON data
    df = pd.json_normalize(stats_json)

    # Replace the naming "statistics.b1" in the columns
    df.columns = [col.replace("statistics.b1.", "") for col in df.columns]

    # Set the datetime format
    df["date"] = pd.to_datetime(df["datetime"])

    # Return the cleaned format
    return df

# Apply the generated function on the stats data
df = clean_stats(stats)

# Display the stats for the first 5 granules in the collection in the table
# Change the value in the parenthesis to show more or a smaller number of rows in the table

# Figure size: 20 representing the width, 10 representing the height
fig = plt.figure(figsize=(20, 10))

plt.plot(
    df["datetime"], # X-axis: sorted datetime
    df["max"], # Y-axis: maximum CO₂ emission
    color="red", # Line color
    linestyle="-", # Line style
    linewidth=0.5, # Line width
    label="CO2 emissions", # Legend label
)

# Display legend
plt.legend()

# Insert label for the X-axis
plt.xlabel("Years")

# Insert label for the Y-axis
plt.ylabel("CO2 emissions gC/m2/year1")

# Insert title for the plot
plt.title(f"CO2 emission Values for {bolge[0]}")

# Add data citation
plt.text(
    df["datetime"].iloc[0],           # X-coordinate of the text 
    df["max"].min(),                  # Y-coordinate of the text 


    # Text to be displayed
    "Source: NASA/NOAA OCO-2 MIP Top-Down CO₂ Budgets",                  
    fontsize=12,                             # Font size
    horizontalalignment="left",              # Horizontal alignment
    verticalalignment="top",                 # Vertical alignment
    color="blue",                            # Text color
)

# Plot the time series
plt.savefig("./server/static/assets/table.png")
