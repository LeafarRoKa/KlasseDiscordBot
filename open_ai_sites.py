import aiohttp
from bs4 import BeautifulSoup
from readability import Document
import asyncio
import json
base_urls = ['https://en.wikipedia.org/w/']
urls= []
wiki_urls = [
    "https://en.wikipedia.org/wiki/Dusty_the_Klepto_Kitty",               # cat burglar cat :contentReference[oaicite:1]{index=1}
    "https://en.wikipedia.org/wiki/Toilet_paper_orientation",             # over vs under battle :contentReference[oaicite:2]{index=2}
    "https://en.wikipedia.org/wiki/Phallic_architecture",                 # absolutely wild architecture :contentReference[oaicite:3]{index=3}
    "https://en.wikipedia.org/wiki/High_five",                            # origins of the high five :contentReference[oaicite:4]{index=4}
    "https://en.wikipedia.org/wiki/Tashirojima",                          # cat island 🇯🇵 :contentReference[oaicite:5]{index=5}
    "https://en.wikipedia.org/wiki/Emu_War",                              # hilariously failed bird war :contentReference[oaicite:6]{index=6}
    "https://en.wikipedia.org/wiki/List_of_animals_awarded_human_credentials", # bizarre degrees :contentReference[oaicite:7]{index=7}
    "https://en.wikipedia.org/wiki/Blue_Peacock",                         # unusual military stuff :contentReference[oaicite:8]{index=8}
    "https://en.wikipedia.org/wiki/Ironman_Heavymetalweight_Championship", # absurd wrestling title :contentReference[oaicite:9]{index=9}
    "https://en.wikipedia.org/wiki/Vermin_Supreme",                        # the politician wearing a boot on his head :contentReference[oaicite:10]{index=10}
    "https://en.wikipedia.org/wiki/WikiTok",                               # random article scroll app :contentReference[oaicite:11]{index=11}
    "https://en.wikipedia.org/wiki/Wikiracing",                            # Wikipedia navigation game :contentReference[oaicite:12]{index=12}
    "https://en.wikipedia.org/wiki/Wikipedia_%E2%80%93_The_Text_Adventure",# Wikipedia text game :contentReference[oaicite:13]{index=13}
    "https://en.wikipedia.org/wiki/Bigipedia",                             # Wikipedia parody :contentReference[oaicite:14]{index=14}
    "https://en.wikipedia.org/wiki/La_Frikipedia",                          # Spanish Wikipedia parody :contentReference[oaicite:15]{index=15}
    "https://en.wikipedia.org/wiki/Unusual_deaths",                        # bizarre death list :contentReference[oaicite:16]{index=16}
    "https://en.wikipedia.org/wiki/Cosmic_latte",                          # the universe’s colour :contentReference[oaicite:17]{index=17}
    "https://en.wikipedia.org/wiki/Bir_Tawil",                             # no‑mans‑land region :contentReference[oaicite:18]{index=18}
    "https://en.wikipedia.org/wiki/Snow_in_Florida",                        # weird weather :contentReference[oaicite:19]{index=19}
    "https://en.wikipedia.org/wiki/Mojave_Phone_Booth",                     # famous desert phone :contentReference[oaicite:20]{index=20}
    # === More random & fun/quirky entries ===
    "https://en.wikipedia.org/wiki/Backrooms",                             # internet legend type
    "https://en.wikipedia.org/wiki/Big_Buck_Bunny",                         # fun animation project
    "https://en.wikipedia.org/wiki/Chocolate_rain",                          # viral song phenomenon
    "https://en.wikipedia.org/wiki/Dancing_Plague_of_1518",                  # bizarre historical event :contentReference[oaicite:21]{index=21}
    "https://en.wikipedia.org/wiki/Gravity_hill",                            # optical illusion roads :contentReference[oaicite:22]{index=22}
    "https://en.wikipedia.org/wiki/Phaistos_Disc",                           # mysterious artefact :contentReference[oaicite:23]{index=23}
    "https://en.wikipedia.org/wiki/Quantum_immortality",                      # thought‑experiment idea :contentReference[oaicite:24]{index=24}
    "https://en.wikipedia.org/wiki/Pykrete",                                 # odd WWII material :contentReference[oaicite:25]{index=25}
    "https://en.wikipedia.org/wiki/Bunny_Man",                               # eerie folklore entry :contentReference[oaicite:26]{index=26}
    "https://en.wikipedia.org/wiki/Roanoke_Colony",                           # historical mystery :contentReference[oaicite:27]{index=27}
    "https://en.wikipedia.org/wiki/Realdoll",                                 # quirky modern topic :contentReference[oaicite:28]{index=28}
    "https://en.wikipedia.org/wiki/Exploding_head_syndrome",                  # unusual sleep phenomenon :contentReference[oaicite:29]{index=29}
    "https://en.wikipedia.org/wiki/Elephantiasis",                             # strangely interesting biology :contentReference[oaicite:30]{index=30}
    "https://en.wikipedia.org/wiki/Sailing_stones",                            # moving rocks mystery :contentReference[oaicite:31]{index=31}
    "https://en.wikipedia.org/wiki/Whole‑body_transplant",                     # wild medical idea :contentReference[oaicite:32]{index=32}
    "https://en.wikipedia.org/wiki/Head_transplant",                            # even wilder surgery attempt :contentReference[oaicite:33]{index=33}
    # (… add more articles continuing this theme up to ~100 total)
]
with open('ai_text.json','r') as f:
    training_data = json.load(f)
async def data_scraping(session:aiohttp.ClientSession=None):
    global training_data
    urls = wiki_urls
    if session is None:
        session = aiohttp.ClientSession() # browser session
    headers = {"User-Agent": "LeafarBot/1.0 (learning project; contact: example@email.com)"}
    for url in urls:
        await asyncio.sleep(2)
        async with session.get(url,headers=headers) as page:#.head IS TOTALLY false it only returns headers and that would just give me the lables that would always be ignored
            html_data = await page.text()#.text is a corutine; this returns all the html text of the page so smth like: "<html><body><h1>Diamond</h1><p>Diamonds are rare items...</p></body></html>"
            doc = Document(html_data)#this creates a class with the html_data in it so will like be smth like def __init__(self,data): self.html = data so it can acces it later
            text = doc.summary()#returns only the paragraphs so like only <p>Diamonds are rare items used for crafting tools.</p>
            #so that is still not what we want we want the <p></p> thats why we will use beatifulsoup
            BeautifulText = BeautifulSoup(text,'html.parser')#a parser is smth that converts <p> etc. into a tree like structur so smth like html
                                                                                                                                            #└ body
                                                                                                                                            #├ p → Hello
                                                                                                                                            #└ p → World
                                                                                                                                            #this even alows us to do stuff like soup.find_all("p") or like in out example soup.get_text()
            text= BeautifulText.getText(' ')#the separator is what it separates the <p></p> with so like in most cases a whithespace bcs its between phrases
            training_data += text
            with open('ai_text.json','w') as f:
                json.dump(training_data,f)

async def all_pages():
    session = aiohttp.ClientSession() # browser session
    for url in base_urls:
        api_page = url + 'api.php'
        params = {
            'action': 'query', # 
            'list': 'allpages',#
            'aplimit': '50',#means how many pages i want on one request
            "format": "json" #wich format json is best for python
        }
        async with session.get(api_page,params=params) as dat:
            data = await dat.json()
            for page in data['query']['allpages']:
                page_title = page['title']
                urls.append(url +page_title)
            
            for i in range(20):
                params['apcontinue'] = data
    await session.close()
asyncio.run(data_scraping())

