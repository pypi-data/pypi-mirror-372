import requests

S = requests.Session()

URL = "https://fa.wikipedia.org/w/api.php"

SEARCHPAGE = "روحانی"

PARAMS = {
    "action": "query",
    "format": "json",
    "list": "search",
    "srsearch": SEARCHPAGE
}

R = S.get(url=URL, params=PARAMS)
DATA = R.json()

for x in DATA['query']['search']:
    if SEARCHPAGE.lower() in x['title']:
      print(x['title'])
      print(x['snippet'])
      print('***************')

