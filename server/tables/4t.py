# Import the following libraries
import requests
import folium
import folium.plugins
from folium import Map, TileLayer 
from pystac_client import Client 
import branca 
import pandas as pd
import matplotlib.pyplot as plt
import tabulate
import time
import openai
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
# Name of the collection for ECCO Darwin CO₂ flux monthly emissions
collection_name = "eccodarwin-co2flux-monthgrid-v5"

collection = requests.get(f"{STAC_API_URL}/collections/{collection_name}").json()

# Provide the STAC and RASTER API endpoints
# The endpoint refers to a location within the API that executes a request on a data collection nesting on the server.

# The STAC API is a catalog of all the existing data collections stored in the GHG Center.
STAC_API_URL = "https://earth.gov/ghgcenter/api/stac/"

# The RASTER API is used to fetch collections for visualization.
RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster/"

asset_name = "co2"

# Create a polygon for the area of interest (aoi)
california_coast_aoi = {
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
aoi_map = Map(
    
    # Base map is set to OpenStreetMap
    tiles="OpenStreetMap", 

    # Define the spatial properties for the map
    location=[
        
    # Set the center of the map
        35, -120 
    ],
    
    # Set the zoom value
    zoom_start=7, 
)

# Insert the Coastal California polygon to the map
folium.GeoJson(california_coast_aoi, name="Coastal California").add_to(aoi_map)

# Visualize the map

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
    }# Check the total number of items available within the collection
items = requests.get(
    f"{STAC_API_URL}/collections/{collection_name}/items?limit=600"
).json()["features"]

# Print the total number of items (granules) found
print(f"Found {len(items)} items")

# Generate a for loop that iterates over all the existing items in the collection 
for item in items:

    # The loop will then retrieve the information for the start datetime of each item in the list
    print(item["properties"]["start_datetime"])

    # Exit the loop after printing the start datetime for the first item in the collection
    break

start_time = time.time()

# Fonksiyon çalıştırma ve istatistikleri toplama
stats = [generate_stats(item, california_coast_aoi) for item in items]

# Zaman ölçümünü bitir ve sonucu göster
end_time = time.time()
print(f"Execution time: {end_time - start_time:.2f} seconds")

# Create a function that converts statistics in JSON format into a pandas DataFrame
def clean_stats(stats_json) -> pd.DataFrame:
    pd.set_option('display.float_format', '{:.20f}'.format)
    stats_json_ = [stats_json[datetime] for datetime in stats_json] 
    # Normalize the JSON data 
    df = pd.json_normalize(stats_json_)

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

# Sort the DataFrame by the datetime column so the plot displays the values from left to right (2020 -> 2022)
df_sorted = df.sort_values(by="datetime")

# Plot the timeseries analysis of the monthly air-sea CO₂ flux changes along the coast of California
# Figure size: 20 representing the width, 10 representing the height
fig = plt.figure(figsize=(20, 10))
plt.plot(
    df_sorted["datetime"],    # X-axis: sorted datetime
    df_sorted["max"],         # Y-axis: maximum CO₂ value
    color="purple",           # Line color
    linestyle="-",            # Line style
    linewidth=1,              # Line width
    label="CO2 Emissions",    # Legend label
)

# Display legend
plt.legend()

# Insert label for the X-axis
plt.xlabel("Years")

# Insert label for the Y-axis
plt.ylabel("CO2 Emissions mmol m²/s")

# Insert title for the plot
plt.title(f"CO2 Emission Values for {bolge[0]}")

# Rotate x-axis labels to avoid cramping
plt.xticks(rotation=90)

# Add data citation
plt.text(
    df_sorted["datetime"].iloc[0],           # X-coordinate of the text (first datetime value)
    df_sorted["max"].min(),                  # Y-coordinate of the text (minimum CO2 value)

    # Text to be displayed
    "Source: NASA Air-Sea CO₂ Flux, ECCO-Darwin Model v5",                   
    fontsize=12,                             # Font size
    horizontalalignment="left",              # Horizontal alignment
    verticalalignment="bottom",              # Vertical alignment
    color="blue",                            # Text color
)

# Plot the time series
plt.savefig("./server/static/assets/table.png")
#plt.show()

