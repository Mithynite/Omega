import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
import re

# Constants
BASE_URL = "https://www.helveti.cz"
PAGE_URL_TEMPLATE = "https://www.helveti.cz/znacky?strana={}"
CSV_FILE = "wristwatch_data.csv"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_max_pages():
    """Finds the highest page number from pagination."""
    response = requests.get(PAGE_URL_TEMPLATE.format(1), headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    page_links = soup.find_all("a", attrs={"data-page": True})
    max_page = 1
    for link in page_links:
        page_number = link.get("data-page")
        if page_number and page_number.isdigit():
            max_page = max(max_page, int(page_number))

    return max_page

def get_watch_links(page):
    """Gets all watch links from a given page."""
    url = PAGE_URL_TEMPLATE.format(page)
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    watch_links = []
    watch_containers = soup.find_all("div", class_="boxik column has-compare")

    for container in watch_containers:
        a_tag = container.find("a", href=True)
        if a_tag:
            watch_links.append(BASE_URL + a_tag["href"])

    return watch_links

def clean_watch_title(full_title):
    """Removes unnecessary prefixes like 'Pánské hodinky' from the title."""
    prefixes = ["Pánské hodinky", "Dámské hodinky", "Unisex hodinky", "Dětské hodinky"]

    for prefix in prefixes:
        if full_title.startswith(prefix):
            full_title = full_title.replace(prefix, "").strip()
            break

    return re.sub(r'\s+', ' ', full_title)


def scrape_watch(url):
    """Extracts details of a single watch."""
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")

    h1_tag = soup.find("h1")
    if not h1_tag:
        return None

    product_title = clean_watch_title(h1_tag.get_text(strip=True))

    # Extract price
    price_tag = soup.find("strong", class_="js_cena dark-red fs-26")
    price = price_tag.get_text(strip=True) if price_tag else "N/A"

    # Extract specifications dynamically
    specs = {}
    headers = {"Název", "URL", "Cena"}
    tables = soup.find_all("table")

    for table in tables:
        for row in table.find_all("tr"):
            columns = row.find_all("td")
            if len(columns) == 2:
                param_name = columns[0].get_text(strip=True)
                param_value = columns[1].get_text(strip=True)
                specs[param_name] = param_value
                headers.add(param_name)

    watch_data = {"Název": product_title, "URL": url, "Cena": price, **specs}
    return watch_data, headers


# Get max pages
max_pages = get_max_pages()
print(f"Total pages found: {max_pages}")

# Ask user for start page
while True:
    try:
        start_page = int(input(f"Enter the page number to start from (1-{max_pages}): "))
        if 1 <= start_page <= max_pages:
            break
        else:
            print(f"Please enter a number between 1 and {max_pages}.")
    except ValueError:
        print("Invalid input. Please enter a number.")

# Start scraping
all_watches = []
all_headers = set()

for page in range(start_page, max_pages + 1):
    print(f"Scraping page {page}/{max_pages}...")

    watch_links = get_watch_links(page)
    if not watch_links:
        print("No watches found, stopping early.")
        break

    for idx, watch_url in enumerate(watch_links, start=1):
        print(f"  Scraping watch {idx}/{len(watch_links)} on page {page}...")
        watch_data, headers = scrape_watch(watch_url)

        if watch_data:
            all_watches.append(watch_data)
            all_headers.update(headers)
        time.sleep(1)

# Convert to DataFrame with dynamic headers
all_headers = sorted(all_headers)
df = pd.DataFrame(all_watches, columns=all_headers)

# Save to CSV
if os.path.exists(CSV_FILE):
    df.to_csv(CSV_FILE, mode="a", header=False, index=False, encoding="utf-8")
else:
    df.to_csv(CSV_FILE, index=False, encoding="utf-8")

print("\nScraping complete! Data saved to 'wristwatch_data.csv'.")
