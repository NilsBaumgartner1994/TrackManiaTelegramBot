import urllib2
from bs4 import BeautifulSoup

def getLastUpdate(url):
    response = urllib2.urlopen(url)
    html_doc = response.read()
    soup = BeautifulSoup(html_doc, 'html.parser')

    playerTag = soup.findAll("small")
    print playerTag[0].getText()

url = "https://players.turbo.trackmania.com/ps4/rankings"
getLastUpdate(url)
