import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re

TICKET_MAP_FILE = 'ticket_url_map.json'
TICKETS_DIR = 'tickets'
MAPS_DIR = 'ticket_maps'

os.makedirs(TICKETS_DIR, exist_ok=True)
os.makedirs(MAPS_DIR, exist_ok=True)

def safe_filename(name):
    return re.sub(r'[^a-zA-Z0-9_\- ]+', '', name).replace(' ', '_')

def download_image(img_url, ticket_name):
    parsed = urlparse(img_url)
    filename = os.path.basename(parsed.path)
    safe_ticket = safe_filename(ticket_name)
    local_path = os.path.join(MAPS_DIR, f"{safe_ticket}_{filename}")
    try:
        r = requests.get(img_url)
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            f.write(r.content)
        return local_path
    except Exception as e:
        print(f"Failed to download image {img_url}: {e}")
        return None

def extract_stations(soup):
    stations = []
    p = soup.find('p', class_='stations')
    if p:
        text = p.get_text(separator=' ', strip=True)
        # Remove leading description
        if ':' in text:
            text = text.split(':', 1)[1]
        # Split by semicolon or linebreak
        for part in re.split(r';|\n', text):
            s = part.strip()
            if s:
                # Remove trailing periods, etc.
                s = s.rstrip('.').strip()
                if s:
                    stations.append(s)
    return stations

def extract_images(soup, ticket_url, ticket_name):
    images = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if src and ('map' in src.lower() or 'route' in src.lower()):
            img_url = urljoin(ticket_url, src)
            local_img = download_image(img_url, ticket_name)
            if local_img:
                images.append(local_img)
    return images

def extract_description(soup):
    desc_div = soup.find('div', class_='description')
    if desc_div:
        return desc_div.get_text(separator=' ', strip=True)
    return None

def extract_fares_and_restrictions(soup):
    fares = {}
    fares_div = soup.find('div', class_='fares')
    if fares_div:
        fares['raw'] = fares_div.get_text(separator=' ', strip=True)
    return fares

def parse_ticket_page(ticket_name, ticket_url):
    try:
        resp = requests.get(ticket_url)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
    except Exception as e:
        print(f"Failed to fetch {ticket_url}: {e}")
        return None
    data = {
        'name': ticket_name,
        'url': ticket_url,
        'description': extract_description(soup),
        'fares_and_restrictions': extract_fares_and_restrictions(soup),
        'stations': extract_stations(soup),
        'route_map_images': extract_images(soup, ticket_url, ticket_name)
    }
    return data

def main():
    with open(TICKET_MAP_FILE, 'r') as f:
        ticket_map = json.load(f)
    for ticket_name, ticket_url in ticket_map.items():
        print(f"Processing: {ticket_name}")
        data = parse_ticket_page(ticket_name, ticket_url)
        if data:
            filename = os.path.join(TICKETS_DIR, f"{safe_filename(ticket_name)}.json")
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
        else:
            print(f"Failed to process {ticket_name}")

if __name__ == '__main__':
    main() 