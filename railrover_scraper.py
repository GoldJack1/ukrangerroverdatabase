import requests
from bs4 import BeautifulSoup
import os
import json
from urllib.parse import urljoin, urlparse

BASE_URL = 'http://www.railrover.org/'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAPS_DIR = os.path.join(BASE_DIR, 'railrover_maps')
OUTPUT_JSON = os.path.join(BASE_DIR, 'railrover_tickets.json')

os.makedirs(MAPS_DIR, exist_ok=True)

def get_soup(url):
    resp = requests.get(url)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'html.parser')

def download_image(img_url, ticket_name):
    parsed = urlparse(img_url)
    filename = os.path.basename(parsed.path)
    safe_ticket = ticket_name.replace(' ', '_').replace('/', '_')
    local_path = os.path.join(MAPS_DIR, f"{safe_ticket}_{filename}")
    r = requests.get(img_url)
    with open(local_path, 'wb') as f:
        f.write(r.content)
    return local_path

def parse_ticket_page(ticket_url, ticket_name):
    soup = get_soup(ticket_url)
    data = {'name': ticket_name, 'url': ticket_url}
    # Description
    desc = soup.find('div', {'id': 'main'})
    if desc:
        data['description'] = desc.get_text(strip=True)
    # Find images (maps)
    images = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if src and ('map' in src.lower() or 'route' in src.lower()):
            img_url = urljoin(ticket_url, src)
            local_img = download_image(img_url, ticket_name)
            images.append(local_img)
    if images:
        data['maps'] = images
    # Extract stations (look for lists, tables, or comma-separated text)
    stations = set()
    # Look for lists
    for ul in soup.find_all(['ul', 'ol']):
        for li in ul.find_all('li'):
            text = li.get_text(strip=True)
            # Heuristic: station names are usually short and not full sentences
            if 2 < len(text) < 40 and (',' not in text or text.count(',') < 3):
                stations.add(text)
    # Look for tables
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            for cell in row.find_all(['td', 'th']):
                text = cell.get_text(strip=True)
                if 2 < len(text) < 40 and (',' not in text or text.count(',') < 3):
                    stations.add(text)
    # Look for comma-separated station lists in paragraphs
    for p in soup.find_all('p'):
        text = p.get_text(strip=True)
        if 'valid at' in text.lower() or 'stations:' in text.lower():
            parts = text.split(':', 1)
            if len(parts) > 1:
                for station in parts[1].split(','):
                    s = station.strip()
                    if 2 < len(s) < 40:
                        stations.add(s)
    if stations:
        data['stations'] = sorted(stations)
    # TODO: Extract more fields (price, validity, etc.) if available
    return data

def main():
    soup = get_soup(BASE_URL)
    tickets = []
    # Find all ticket links (from the main page)
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)
        if 'rover' in text.lower() or 'ranger' in text.lower():
            ticket_url = urljoin(BASE_URL, href)
            try:
                ticket_data = parse_ticket_page(ticket_url, text)
                tickets.append(ticket_data)
            except Exception as e:
                print(f"Failed to parse {ticket_url}: {e}")
    # Save to JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(tickets, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(tickets)} tickets to {OUTPUT_JSON}")

if __name__ == '__main__':
    main() 