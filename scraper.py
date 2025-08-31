#import selenium yay
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

#Website URL
CHROMEDRIVER_PATH = r"C:\Users\kevin\OneDrive\Desktop\chromedriver\chromedriver-win64\chromedriver.exe"
URL = "https://guide.michelin.com/us/en/restaurants"


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
#ahhhhhhhhhhhhhhhhhhhhhhhhh
all_restaurants = []
driver.get(URL)
time.sleep(3)
restaurants_page1 = get_restaurant_links()
all_restaurants += restaurants_page1
for i in range(2, 5):
	time.sleep(3)
	driver.get("http://guide.michelin.com/us/en/restaurants/page/" + str(i))
	restaurants_page2 = get_restaurant_links()
	all_restaurants += restaurants_page2
#driver.get("https://guide.michelin.com/us/en/restaurants/page/2")
#time.sleep(5)
#all_restaurants = restaurants_page1 + restaurants_page2

results = []
for name, href in all_restaurants:
	driver.get(href)
	time.sleep(3)
	address = get_address()
	cuisine = get_cuisine()
	results.append((name, address, cuisine))
	print(f"{name}: {address} / {cuisine}")

driver.quit()
