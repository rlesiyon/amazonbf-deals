from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import argparse

#Comment out these 3 lines and change the searchterm variable, if you do not wish to use argparse version
my_parser = argparse.ArgumentParser(description='Return BF Amazon Deals')
my_parser.add_argument('searchterm', metavar='searchterm', type=str, help='The item to be searched for. Use + for spaces')
args = my_parser.parse_args()

searchterm = args.searchterm

s = HTMLSession()
dealslist = []

url = f'https://www.amazon.com/s?k={searchterm}'

def getdata(url):
    r = s.get(url)
    r.html.render(sleep=1)
    soup = BeautifulSoup(r.html.html, 'html.parser')
    return soup

def getdeals(soup):
    products = soup.find_all('div', {'data-component-type': 's-search-result'})
    for item in products:
        title_item = item.find('a', {'class': 
        'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
    
        title = title_item.text.strip()
        short_title = title[:25]
        link = title_item.get('href')
        saleprice, oldprice = getProductsPrices(item)
        try:
            reviews = float(item.find('span', {'class': 'a-size-base'}).text.strip())
        except:
            reviews = 0

        saleitem = {
            'title': title,
            'short_title': short_title,
            'link': link,
            'saleprice': saleprice,
            'oldprice': oldprice,
            'reviews': reviews            
            }
        print(saleitem)
        dealslist.append(saleitem)
    return

def getnextpage(soup): 
    url = soup.find('a', {'class': 's-pagination-next'})
    if url:
        return f'https://www.amazon.com{url.get("href")}'
    return 

def getProductsPrices(item):
    saleprices = item.find_all("span", {'class':'a-offscreen'})
    saleprice, oldprice = 0, 0
    try:
        saleprice = float(saleprices[0].text.replace('$','').replace(',','').strip())
        oldprice = float(saleprices[1].text.replace('$','').replace(',','').strip())
    except:
        try:
            saleprice = float(saleprices[0].text.replace('$','').replace(',','').strip())
            oldprice = saleprice
        except:
            pass
    return saleprice, oldprice

def main(url):
    while True:
        soup = getdata(url)
        getdeals(soup)
        url = getnextpage(soup)
        if not url:
            break
        else:
            print(url)
            print(len(dealslist))  

    df = pd.DataFrame(dealslist)
    df['percentoff'] = 100 - ((df.saleprice / df.oldprice) * 100)
    df = df.sort_values(by=['percentoff'], ascending=False)
    df.to_csv(searchterm + '-bfdeals.csv', index=False)
    print('Fin.')
    
if __name__ == "__main__":
    main(url)
      
