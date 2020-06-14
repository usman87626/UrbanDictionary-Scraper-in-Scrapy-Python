import scrapy
from scrapy import Request
import json 
import requests

class UrbanDictionary(scrapy.Spider):
    name = 'urban_scraper'
    start_urls = ["https://www.urbandictionary.com/popular.php?character="+chr(code) for code in range(ord('A'),ord('Z')+1)]   
    
    custom_settings = {
        'FEED_FORMAT' : 'json' , 
        'FEED_URI' : 'urban_dictionary.json'
    }
    
    def parse(self,response):
        links=[]

        #Xpath to get page links for all the words on the page
        #response.xpath("//li[@class='word']/a/@href").getall()
        #response.css("li.word a").css('::attr(href)').getall()
        # links = response.css("li.word a").css('::attr(href)').getall()
        for item in response.css("li.word"):
            word = item.css('a::text').get()
            short_description = requests.get(f'https://api.urbandictionary.com/v0/tooltip?term={word}').json()['string'].replace('</b>',' ').replace('<b>','').replace('\n','').replace('\r','')
            links.append({
                'word' : word ,
                'short_desc':  short_description ,
                'link':    item.css('a::attr(href)').get()
            })
            
        #Follow the link recursively    
        for link in links:
             yield response.follow(url=link['link'] ,meta={
                 'short_desription':link['short_desc'] , 
                 'word':link['word']
                 }, 
             callback=self.parse_links)
             

    def parse_links(self , response):
        # Word here
        word = response.meta.get('word')
        # Short Description
        short_description = response.meta.get('short_desription')
        # Full description
        full_description = " ".join(response.xpath("//div[@class='meaning']/descendant::text()").getall())
        
        items = {
            'word': word , 
            'short_description':short_description,
            'full_description':full_description
        }

        yield items

# if __name__ == '__main__':
#     res = ''
#     #read file
#     with open('urban.json','r') as f:
#         for line in f.read():
#             res += line
    
#     #Write file
#     with open('urban.json','w') as f:
#         f.write(json.dumps(json.loads(res),indent=2))