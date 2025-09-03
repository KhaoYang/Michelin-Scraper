#import selenium yay
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import requests
import os
from dotenv import load_dotenv
import csv
import pandas as pd
import json

load_dotenv()

#Website URL
CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_P")
URL = "https://guide.michelin.com/us/en/restaurants"
ACCESS_TOKEN = os.getenv("MAPBOX_TOKEN")

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)
driver.get(URL)
time.sleep(5)
def get_restaurant_links():
	last_height = driver.execute_script("return document.body.scrollHeight")
	scroll_attempts = 0
	max_attempts = 10
	while scroll_attempts < max_attempts:
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(2)
		new_height = driver.execute_script("return document.body.scrollHeight")
		if new_height == last_height:
			scroll_attempts += 1
		else:
			scroll_attempts = 0
			last_height = new_height
	links = driver.find_elements(By.CSS_SELECTOR, "a.link[aria-label][href]")
	restaurant_data = []
	base_url = "https://guide.michelin.com"
	for link in links:
		aria_label = link.get_attribute("aria-label")
		href = link.get_attribute("href")
		if aria_label and aria_label.startswith("Open ") and href:
			name = aria_label.replace("Open ", "").strip()
			full_url = href if href.startswith("http") else base_url + href
			restaurant_data.append((name, full_url))
	return restaurant_data

def get_address():
	try:
		elems = driver.find_elements(By.CSS_SELECTOR, "div.data-sheet__block--text")
		for elem in elems:
			text = elem.text.strip()
			if "," in text and any(city in text for city in ["Chicago", "New York", "Los Angeles", "San Francisco", "USA"]):
				return text
		return "ADDRESS WHERE????????????????"
	except Exception:
		return "ADDRESS WHERE????????"
	
def get_cuisine():
	try:
		elems = driver.find_elements(By.CSS_SELECTOR, "div.data-sheet__block--text")
		for elem in elems:
			text = elem.text.strip()
			if "$" in text or "€" in text or "£" in text:
				return text
		return "CUISINE WHERE!!!!!!!!!!!!!!!!"
	except Exception:
		return "CUISINE WHERE!!!!!!!!"
	
def get_coordinates(address):
	try:
		url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json?access_token={ACCESS_TOKEN}"
		response = requests.get(url)
		data = response.json()
		if data['features']:
			lon, lat = data['features'][0]['center']
			return lat, lon
		else:
			return None, None
	except Exception:
		return None, None
#ahhhhhhhhhhhhhhhhhhhhhhhhh
all_restaurants = []
for i in range(1, 2):
	driver.get("http://guide.michelin.com/us/en/restaurants/page/" + str(i))
	time.sleep(3)
	restaurants_page1 = get_restaurant_links()
	all_restaurants += restaurants_page1

results = []
result_dict = []

for name, href in all_restaurants[:4]:
	driver.get(href)
	time.sleep(3)
	address = get_address()
	cuisine = get_cuisine()
	coordinates = get_coordinates(address)
	dic = {"name": name, "address": address, "cuisine": cuisine, "coordinates": coordinates}
	result_dict.append(dic)
	print(dic)
	#results.append((name, address, cuisine))
	#print(result_dict)

filename = "michelin_restaurants.csv"
fieldnames = ["name", "address", "cuisine", "latitude", "longitude"]
with open(filename, mode = 'w', newline = '', encoding = "utf-8") as file:
	writer = csv.DictWriter(file, fieldnames=fieldnames)
	writer.writeheader()
	for entry in result_dict:
		lat, lon = entry["coordinates"] if entry["coordinates"] else (None, None)
		writer.writerow({
			"name": entry["name"],
			"address": entry["address"],
			"cuisine": entry["cuisine"],
			"latitude": lat,
			"longitude": lon
		})
df = pd.read_csv(filename)
df.to_json("michelin_restaurants.json", orient="records", indent = 2)

with open('michelin_restaurants.json') as f:
    data = json.load(f)

features = []
for restaurant in data:
    coords_str = restaurant.get('coordinates', '')
    # Split into lat/lon
    parts = coords_str.split(' ')
    if len(parts) == 2:
        lat = parts[0]
        lon = parts[1]
        if lat is not None and lon is not None:
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {k: v for k, v in restaurant.items() if k != 'coordinates'}
            }
            features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features
}

with open('michelin_restaurants.geojson', 'w') as f:
    json.dump(geojson, f, indent=2)


driver.quit()
