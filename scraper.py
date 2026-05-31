import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone
import json

# configurations for individual venues
VENUES = {
    'new_brookland_tavern': {
        'name': 'New Brookland Tavern',
        'url': 'https://www.newbrooklandtavern.com/',
        'list': {
            'title_hook': 'title',
            'date_hook': 'short-date',
        },
        'detail': {
            'full_date_hook': 'event-full-date',
            'image_hook': 'event-image',
        }
    }
}

# scrape a particular venue according to its config
def scrape_venue(venue):
    r = requests.get(venue['url'])
    soup = BeautifulSoup(r.text, 'html.parser')

    titles = soup.find_all(attrs={'data-hook': venue['list']['title_hook']})
    events = []

    # get the event url, the full date, the image if needed, and create an event for it
    for title in titles:
        event_url = title['href']
        detail_r = requests.get(event_url)
        detail_soup = BeautifulSoup(detail_r.text, 'html.parser')

        full_date = detail_soup.find(attrs={'data-hook': venue['detail']['full_date_hook']})
        image_div = detail_soup.find(attrs={'data-hook': venue['detail']['image_hook']})
        wow_image = image_div.find(attrs={'data-resize': 'cover'}).find('wow-image')
        image_info = json.loads(wow_image['data-image-info'])
        uri = image_info['imageData']['uri']
        image_url = f'https://static.wixstatic.com/media/{uri}'

        events.append({
            'title': title.text,
            'url': event_url,
            'date': full_date.text if full_date else '',
            'image_url': image_url,
        })

    return events

# create the feed
fg = FeedGenerator()
fg.id('https://eli-johnson-04.github.io/rss-tablet/feed.xml')
fg.title('Local Events Feed')
fg.link(href='https://eli-johnson-04.github.io/rss-tablet/feed.xml', rel='self')
fg.description('Upcoming local events')

# run through all venues and add their events to the feed
for venue_key, venue in VENUES.items():
    for event in scrape_venue(venue):
        fe = fg.add_entry()
        fe.id(event['url'])
        fe.title(f"[{venue['name']}] {event['title']}")
        fe.link(href=event['url'])
        fe.description(event['date'])
        fe.published(datetime.now(timezone.utc))
        if event['image_url']:
            fe.enclosure(event['image_url'], 0, 'image/jpeg')

# create the rss file
fg.rss_file('feed.xml')
print(f"Feed generated successfully")