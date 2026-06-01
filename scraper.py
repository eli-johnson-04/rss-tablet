import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone, timedelta
import json

# configurations for individual venues
VENUES = {
    'new_brookland_tavern': {
        'name': 'New Brookland Tavern',
        'url': 'https://www.newbrooklandtavern.com/',
        'website': 'https://www.newbrooklandtavern.com/',
        'maps': 'https://www.google.com/maps/place/New+Brookland+Tavern/@33.9983504,-81.0178011,1913m/data=!3m2!1e3!4b1!4m6!3m5!1s0x88f8bb462cc265d9:0x974ae781d0a085fa!8m2!3d33.998346!4d-81.0152262!16zL20vMGN5Y2xo?entry=ttu&g_ep=EgoyMDI2MDUyNy4wIKXMDSoASAFQAw%3D%3D',
        'list': {
            'title_hook': 'title',
            'date_hook': 'short-date',
        },
        'detail': {
            'full_date_hook': 'event-full-date',
            'image_hook': 'event-image',
        },
        'scraper': 'wix'
    },
    'art_bar': {
        'name': 'Art Bar',
        'url': 'https://www.artbarsc.com/events/',
        'website': 'https://www.artbarsc.com/events/',
        'maps': 'https://www.google.com/maps/place/Art+Bar/@34.0006994,-81.0400209,1913m/data=!3m2!1e3!4b1!4m6!3m5!1s0x88f8bb2c7a559d3b:0x633d2ae568b7f162!8m2!3d34.000695!4d-81.037446!16s%2Fm%2F0k56sry?entry=ttu&g_ep=EgoyMDI2MDUyNy4wIKXMDSoASAFQAw%3D%3D',
        'scraper': 'art_bar'
    },
    # 'the_spaze': {
    #     'name': 'The Spaze',
    #     'url': 'https://thelooneybinsc.bigcartel.com/',
    #     'website': 'https://thelooneybinsc.bigcartel.com/',
    #     'maps': 'https://www.google.com/maps/place/The+Spaze/@33.977909,-81.0157564,1913m/data=!3m1!1e3!4m6!3m5!1s0x88f8bbed58718737:0x4ff9d0c1de7350b!8m2!3d33.9802268!4d-81.0101548!16s%2Fg%2F11wv2m229q?entry=ttu&g_ep=EgoyMDI2MDUyNy4wIKXMDSoASAFQAw%3D%3D',
    #     'scraper': 'bigcartel'
    # },
    'cats_kettle': {
        'name': "Cat's Kettle",
        'url': 'https://www.catskettle.com/calendar',
        'website': 'https://www.catskettle.com/calendar',
        'base_url': 'https://www.catskettle.com',
        'maps': 'https://www.google.com/maps/place/Cat%E2%80%99s+Kettle-+Gourmet+Delicatessen/@33.9998131,-81.0377782,956m/data=!3m2!1e3!4b1!4m6!3m5!1s0x88f8bbe24f2403d5:0x21d540109388cd8!8m2!3d33.9998087!4d-81.0352033!16s%2Fg%2F11xn635b2p?entry=ttu&g_ep=EgoyMDI2MDUyNy4wIKXMDSoASAFQAw%3D%3D',
        'scraper': 'squarespace'
    },
    'colajazz': {
        'name': 'ColaJazz',
        'url': 'https://www.colajazz.com/events',
        'website': 'https://www.colajazz.com/events',
        'base_url': 'https://www.colajazz.com',
        'maps': 'https://www.google.com/maps/place/ColaJazz+Foundation/@34.0020403,-81.0165515,239m/data=!3m1!1e3!4m6!3m5!1s0x88f8bb7b1aa15de7:0xf140db18553f8908!8m2!3d34.0021127!4d-81.016152!16s%2Fg%2F11rr28ljw4?entry=ttu&g_ep=EgoyMDI2MDUyNy4wIKXMDSoASAFQAw%3D%3D',
        'scraper': 'squarespace'
    },
}

def get_next_weekday(weekday_name):
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    today = datetime.now(timezone.utc).date()
    target = days.index(weekday_name.lower())
    days_ahead = (target - today.weekday()) % 7
    next_date = today + timedelta(days=days_ahead)
    return next_date

ART_BAR_WEEKLY = [
    {
        'title': 'Improv Comedy',
        'url': 'https://www.artbarsc.com/event/improv-comedy/',
        'day': 'Tuesday',
        'time': '8:00 pm',
        'image_url': 'https://www.artbarsc.com/wp-content/uploads/AdobeStock_1293354954-1600x953.jpeg',
    },
    {
        'title': 'Karaoke',
        'url': 'https://www.artbarsc.com/event/karaoke/',
        'day': 'Wednesday',
        'time': '8:00 pm',
        'image_url': 'https://www.artbarsc.com/wp-content/uploads/karaoke.jpg',
    },
    {
        'title': 'Useless Trivia',
        'url': 'https://www.artbarsc.com/event/trivia/',
        'day': 'Thursday',
        'time': '7:00 pm',
        'image_url': 'https://www.artbarsc.com/wp-content/uploads/useless-trivia-e1748825794656.jpg',
    },
]

def scrape_art_bar(venue):
    events = []
    for e in ART_BAR_WEEKLY:
        next_date = get_next_weekday(e['day'])
        events.append({
            'title': e['title'],
            'url': e['url'],
            'date': f"{e['time']} {e['day']}s (weekly)",
            'image_url': e['image_url'],
            'parsed_date': datetime.combine(next_date, datetime.min.time()).replace(tzinfo=timezone.utc),
        })
    return events
                     
def scrape_wix_venue(venue):
    r = requests.get(venue['url'])
    soup = BeautifulSoup(r.text, 'html.parser')
    titles = soup.find_all(attrs={'data-hook': venue['list']['title_hook']})
    events = []
    for title in titles:
        event_url = title['href']
        detail_r = requests.get(event_url)
        detail_soup = BeautifulSoup(detail_r.text, 'html.parser')
        full_date = detail_soup.find(attrs={'data-hook': venue['detail']['full_date_hook']})
        image_div = detail_soup.find(attrs={'data-hook': venue['detail']['image_hook']})
        wow_image = image_div.find(attrs={'data-resize': 'cover'}).find('wow-image')
        image_info = json.loads(wow_image['data-image-info'])
        uri = image_info['imageData']['uri']
        events.append({
            'title': title.text,
            'url': event_url,
            'date': full_date.text if full_date else '',
            'image_url': f'https://static.wixstatic.com/media/{uri}',
            'parsed_date': datetime.strptime(full_date.text, "%b %d, %Y, %I:%M %p").replace(tzinfo=timezone.utc) if full_date else datetime.now(timezone.utc),
        })
    return events

def scrape_bigcartel_venue(venue):
    r = requests.get(venue['url'])
    soup = BeautifulSoup(r.text, 'html.parser')
    events = []
    for product in soup.select('div.product-list-thumb:not(.sold)'):
        link = product.find('a', class_='product-list-link')
        if not link:
            continue
        title = product.select_one('.product-list-thumb-name')
        img = product.select_one('img.product-list-image')
        image_url = img['data-srcset'].split(',')[0].strip().split(' ')[0] if img and img.get('data-srcset') else None
        events.append({
            'title': title.text.strip() if title else link['title'],
            'url': f"https://thelooneybinsc.bigcartel.com{link['href']}", # TODO: inaccurate if there's another bigcartel site
            'date': title.text.strip() if title else '',
            'image_url': image_url,
            'parsed_date': datetime.now(timezone.utc),
        })
    return events

def scrape_squarespace_venue(venue):
    r = requests.get(venue['url'])
    soup = BeautifulSoup(r.text, 'html.parser')
    events = []

    for article in soup.select('article.eventlist-event--upcoming'):
        title_el = article.select_one('.eventlist-title-link')
        date_el = article.select_one('time.event-date')
        time_el = article.select_one('time.event-time-localized-start')
        img_el = article.select_one('img')

        if not title_el or not date_el:
            continue

        date_str = date_el.get('datetime')
        time_str = time_el.text.strip() if time_el else ''
        full_date = f"{date_el.text.strip()} {time_str}".strip()

        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            parsed_date = datetime.now(timezone.utc)

        image_url = None
        if img_el and img_el.get('src'):
            image_url = img_el['src'].split('?')[0]

        events.append({
            'title': title_el.text.strip(),
            'url': venue['base_url'] + title_el['href'],
            'date': full_date,
            'image_url': image_url,
            'parsed_date': parsed_date,
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
    match venue.get('scraper'):
        case 'art_bar':
            events = scrape_art_bar(venue)
        case 'bigcartel':
            events = scrape_bigcartel_venue(venue)
        case 'wix':
            events = scrape_wix_venue(venue)
        case 'squarespace':
            events = scrape_squarespace_venue(venue)

    for event in events:
        fe = fg.add_entry()
        fe.id(event['url'])
        fe.title(f"[{venue['name']}] {event['title']}")
        fe.link(href=event['url'])
        fe.description(
            f"{event['date']}<br>"
            f"<a href=\"{venue['website']}\">Venue Website</a><br>"
            f"<a href=\"{venue['maps']}\">Google Maps</a>"
        )
        fe.published(event['parsed_date'])
        if event['image_url']:
            fe.enclosure(event['image_url'], 0, 'image/jpeg')

# create the rss file
fg.rss_file('feed.xml', pretty=True)
print(f"Feed generated successfully")