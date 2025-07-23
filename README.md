# RailRover.org Scraper

This script scrapes all rail rover and ranger ticket information from http://www.railrover.org/.

## Usage

1. Install requirements:
   ```
   pip install -r requirements.txt
   ```
2. Run the script:
   ```
   python railrover_scraper.py
   ```
3. Output:
   - All ticket data is saved in `railrover_tickets.json` inside the `web_extraction/` folder.
   - All route map images are downloaded to the `railrover_maps/` folder inside `web_extraction/`.

## Notes
- The script extracts ticket name, description, any route map images, and valid stations found on each ticket's page.
- You may need to adapt the script if the website structure changes. 