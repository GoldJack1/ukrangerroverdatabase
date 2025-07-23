import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin

BASE_URL = 'http://www.railrover.org/'
MAIN_PAGE = BASE_URL


def get_ticket_links():
    resp = requests.get(MAIN_PAGE)
    soup = BeautifulSoup(resp.text, 'html.parser')
    ticket_map = {}
    for ul in soup.find_all('ul', class_='subcategoryitems'):
        for li in ul.find_all('li'):
            a = li.find('a', href=True)
            if not a:
                continue
            name = a.get_text(strip=True)
            # If there is a <small> subtitle, append it in parentheses
            small = a.find('small')
            if small:
                subtitle = small.get_text(strip=True)
                # Remove subtitle from name if duplicated
                name = name.replace(subtitle, '').strip()
                name = f"{name} {subtitle}" if subtitle else name
            url = urljoin(BASE_URL, a['href'])
            ticket_map[name] = url
    return ticket_map

def main():
    ticket_map = get_ticket_links()
    with open('ticket_url_map.json', 'w') as f:
        json.dump(ticket_map, f, indent=2)
    print(f"Extracted {len(ticket_map)} tickets. Saved to ticket_url_map.json")

if __name__ == '__main__':
    main() 