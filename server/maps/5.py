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

with open("server/maps/datas.txt", "r") as dosya:
    ilk_satir = dosya.readline().strip()  # Dosyanın ilk satırını okur ve boşlukları temizler
    print(ilk_satir)
tarih = str(ilk_satir).split(",")
print(tarih)
# Provide STAC and RASTER API endpoints
STAC_API_URL = "https://earth.gov/ghgcenter/api/stac"
RASTER_API_URL = "https://earth.gov/ghgcenter/api/raster"

# Please use the collection name similar to the one used in STAC collection.

# Name of the collection for gosat budget methane. 
collection_name = "gosat-based-ch4budget-yeargrid-v1"

# Fetching the collection from STAC collections using appropriate endpoint.
collection = requests.get(f"{STAC_API_URL}/collections/{collection_name}").json()

def get_item_count(collection_id):
    count = 0
    items_url = f"{STAC_API_URL}/collections/{collection_id}/items"

    while True:
        response = requests.get(items_url)

        if not response.ok:
            print("error getting items")
            exit()

        stac = response.json()
        count += int(stac["context"].get("returned", 0))
        next = [link for link in stac["links"] if link["rel"] == "next"]

        if not next:
            break
        items_url = next[0]["href"]

    return count

# Check total number of items available
number_of_items = get_item_count(collection_name)
items = requests.get(f"{STAC_API_URL}/collections/{collection_name}/items?limit={number_of_items}").json()["features"]
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
# To access the year value from each item more easily, this will let us query more explicity by year and month (e.g., 2020-02)
items = {item["properties"]["start_datetime"][:10]: item for item in items} 
asset_name = "prior-total"

# Fetching the min and max values for a specific item
rescale_values = {"max":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["max"], "min":items[list(items.keys())[0]]["assets"][asset_name]["raster:bands"][0]["histogram"]["min"]}

items.keys()

color_map = "rainbow" # please select the color ramp from matplotlib library.
january_2019_tile = requests.get(
    f"{RASTER_API_URL}/collections/{items[tarih[1]]['collection']}/items/{items[tarih[1]]['id']}/tilejson.json?"
    f"&assets={asset_name}"
    f"&color_formula=gamma+r+1.05&colormap_name={color_map}"
    f"&rescale={rescale_values['min']},{rescale_values['max']}", 
).json()

# Set initial zoom and center of map for CH₄ Layer
# Centre of map [latitude,longitude]
map_ = folium.Map(location=(34, -118), zoom_start=6)

# January 2019
map_layer_2019 = TileLayer(
    tiles=january_2019_tile["tiles"][0],
    attr="GHG",
    opacity=0.7,
)
map_layer_2019.add_to(map_)

# # January 2012
# map_layer_2012 = TileLayer(
#     tiles=january_2012_tile["tiles"][0],
#     attr="GHG",
#     opacity=0.7,
# )
# map_layer_2012.add_to(map_.m2)
os.remove("server/templates/1.html")
# visualising the map
map_layer_2019.save("server/templates/1.html")


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
    <iframe src="5.html" title="Harita"></iframe>
</body>
</html>
"""

# Dosya olarak kaydetme
# with open("anasayfa.html", "w", encoding="utf-8") as file:
   #  file.write(html_content)

# print("Ana sayfa oluşturuldu: anasayfa.html")
