import requests
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
from datetime import datetime, timezone

# set up the request and beautifulsoup to parse brookland tavern's html
r = requests.get('https://www.newbrooklandtavern.com/')
soup = BeautifulSoup(r.text, 'html.parser')

# find all the event titles and their dates
titles = soup.find_all(attrs={'data-hook': 'title'})
dates = soup.find_all(attrs={'data-hook': 'short-date'})

# set up a new RSS feed generator
fg = FeedGenerator()
fg.id('https://eli-johnson-04.github.io/rss-tablet/feed.xml')
fg.link(href='https://eli-johnson-04.github.io/rss-tablet/feed.xml', rel='self')
fg.description('Upcoming events at New Brookland Tavern')

# associated each title and date together and create an XML entry for it
for title, date in zip(titles, dates):
    fe = fg.add_entry()
    fe.id(title['href'])
    fe.title(title.text)
    fe.link(href=title['href'])
    fe.description(date.text)
    fe.published(datetime.now(timezone.utc))

# write the rss file as xml
fg.rss_file('feed.xml')
print(f"Feed generated with {len(titles)} events")