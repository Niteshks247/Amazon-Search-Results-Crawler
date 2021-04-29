import requests
import bs4
import dateparser
import csv
import sys

startUrl,numResults,fname = sys.argv[1:]

def searchCrawler(startUrl,numResults,fname):
    
    headers = {'ACCEPT-LANGUAGE':'en-US,en;q=0.9',
          'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'}
    
    def writeCSV(fname,data):
        keys = data[0].keys()
        with open(fname, 'w', newline='',encoding='utf-8')  as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(DATA)
        return fname
    
    def fixUrl(url,domain):
        temp = url.split('/')
        if len(temp)<3 or temp[2]!=domain.split('/')[2]:
            return domain+url
        
    def scrapePage(url,numRows):
        page = requests.get(url, headers=headers)


        parsed = bs4.BeautifulSoup(page.content,'lxml')
        domain = "/".join(page.url.split('/')[:3])

        indexs = parsed.find_all('div',attrs={'data-component-type':'s-search-result'})

        Data = []
        for i in range(1,len(indexs)):
            data = {}
            box = indexs[i]

            # Product Name
            prod = box.find("h2")
            prodName = prod.text.strip()
            data['Product Name'] = prodName

            # Product URL
            prodUrl = prod.find('a').attrs['href']
            data['Product URL'] = fixUrl(prodUrl,domain)

             # Image URL
            imgUrl = box.find("img",attrs={'data-image-index':i}).attrs['src']
            data['Image URL'] = imgUrl

            # Old Price
            oldPriceBox = box.find('span',attrs={'class':'a-price','data-a-color':'secondary'})
            if oldPriceBox:
                oldPriceBox = oldPriceBox.findChild()
                oldPrice = oldPriceBox.text
            else:
                oldPrice = None
            data['Old Price'] = oldPrice

            # Deal Price
            pricebox = box.find('span',attrs={'class':'a-price','data-a-color':'price'}).findChild()
            price = pricebox.text
            data['Deal Price'] = price

            # Rating
            ratingText = box.find('i',class_='a-icon')
            if ratingText and ratingText.text:
                rating = ratingText.text.split()[0]
            else:
                rating = None
            data['Rating'] = rating

            # Number of Ratings
            if rating:
                ratingbox = box.find('span',attrs={'aria-label':ratingText.text})
                numRatings = ratingbox.next_sibling.attrs['aria-label']
            else:
                numRatingText = None
            data['Number of Ratings'] = numRatings

            # Delivery Date
            dateText = box.find('span',class_='a-text-bold')
            if dateText:
                dateText = dateText.text.split(',')
                dateText = dateText[-1]
                date = dateparser.parse(dateText).date()
                date = "/".join(reversed(date.isoformat().split('-')))
            else:
                date = None
            data['Delivery Date'] = date

            Data.append(data)
            if len(Data)>=numRows:
                break

        searchPages = parsed.find('ul',class_='a-pagination')
        nextUrl = searchPages.find('li',class_='a-last').findChild()
        nextUrl = fixUrl(nextUrl.attrs['href'],domain)

        return Data,nextUrl
    
    DATA = []
    
    nextUrl = startUrl
    while(len(DATA)<numResults):
        numRows = numResults-len(DATA)
        data,nextUrl = scrapePage(nextUrl,numRows)
        DATA.extend(data)
    	
        print(f"{numResults-len(DATA)} results remaining...")

    writeCSV(fname,DATA)
    
    return fname

print("Crawling...")
searchCrawler(startUrl,int(numResults),fname)
print("Operation Complete...")
print(f"Results saved at {fname}")