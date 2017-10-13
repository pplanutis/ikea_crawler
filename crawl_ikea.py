# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib
from utils_mailer import send_file
from datetime import datetime
import psycopg2
import traceback
import re
import sys
from prompt_toolkit.layout import dimension

class crawl(object):
    def __init__(self, query, min_price, max_price):
        self.main_url = "http://www.ikea.com"
        self.query = query
        self.min_price = min_price
        self.max_price = max_price
        self.parse_html2()
        
    def get_html(self, url, params=None):
        if params:
            return urllib.urlopen(url % params).read()
        else:
            return urllib.urlopen(url).read()
        
    def parse_html2(self):
        _url = "http://www.ikea.com/webapp/wcs/stores/servlet/IrwStockSearch?%s"
        _params = {'category': 'products', 
                   'storeId':19, 'langId':-27,
                   'ikeaStoreNumber1':203}
        _params['query'] = self.query
        _params['min_price'] = self.min_price
        _params['max_price'] = self.max_price
        page = 1
        while True:
            _params['pageNumber'] = page
            _uenc_params = urllib.urlencode(_params)
            soup = BeautifulSoup(self.get_html(_url, _uenc_params), 
                                 "html.parser")
            body = soup.body
            items, item = None, None
            try:
                list = body.find("div", {"id": "productsContainer"})
                items = list.find_all("div", {"class": "productContainer "})
            except:
                try:
                    list = body.find("div", {"class": "sc_product_container"})
                    img_div = list.find("div", {"class": "sc_product_img_container"})
                    item = list.find("div", {"class": "sc_product_text_container"})
                except:
                    print 'no products found'
                    break
            if items:
                items_len = len(items) / 2 if len(items) > 0 else 0
                if items_len > 0:
                    page += 1
                    i = 1
                    for item in items:
                        desc = []
                        dims = []
                        name, href, img, pr_code = None, None, None, None
                        name_span = item.find_all("span", {"id": 'txtNameProduct%s' % i})
                        desc_span = item.find_all("span", {"id": 'txtDescrProduct%s' % i})
                        name = re.sub(r"\s+", " ", name_span[0].text)+\
                            ', '+re.sub(r"\s+", " ", desc_span[0].text)
                        i += 1
                        for a in item.find_all("a", href=True):
                            if 'products' in a['href']:
                                href = a['href']
                        if href:
                            s2 = BeautifulSoup(self.get_html(self.main_url+href), 
                                 "html.parser")
                            b2 = s2.body
                            i2 = b2.find("div", {"class", "itemNumber"})
                            _pr_code = i2.find("div", {"id": "itemNumber"})
                            pr_code = _pr_code.text
                        img = item.find("img")
                        price_span = item.find("span", {"class": "prodPrice"})
                        ps = re.sub(r"\s+", "", item.select("span.prodPrice")[0].text)
                        desc.append([name if name else None, 
                                     self.main_url+img['src'] if img else self.main_url, 
                                     self.main_url+href if href else self.main_url,
                                     ps if ps else None,
                                     pr_code])
                        dim_div = item.find("div", {"class": "cartContainer moreInfo"})
                        dimensions = dim_div.find_all("span", {"class": "prodDimension"})
                        for x in xrange(0,len(dimensions)):
                            ds = re.sub(r"\s+", "", dim_div.select("span#txtDim1Product%s"%x)[0].text)
                            dims.append(ds)
                        print desc, dims
                else:
                    break
            elif item:
                name, href, img, price = None, None, None, None
                pr_code = None
                desc = []
                dims = []
                name_span = item.find("span", {"class": 'prodName'})
                desc_span = item.find("span", {"class": 'prodDesc'})
                name = re.sub(r"\s+", " ", name_span.text)+\
                    ', '+re.sub(r"\s+", " ", desc_span.text)
                _href = item.find("a", href=True)
                href = self.main_url+_href['href'] if 'products' in _href['href'] else self.main_url
                if href:
                    s2 = BeautifulSoup(self.get_html(href), 
                         "html.parser")
                    b2 = s2.body
                    i2 = b2.find("div", {"class", "itemNumber"})
                    _pr_code = i2.find("div", {"id": "itemNumber"})
                    pr_code = _pr_code.text
                _img = img_div.find("img", {"id": "productImg"})
                img = self.main_url+_img['src'] if _img else self.main_url 
                price_span = item.find("span", {"id": "price1"})
                price_cnt_span = item.find("span", {"class": "perProduct"})
                price = re.sub(r"\s+", "", price_span.text)+\
                    ''+re.sub(r"\s+", "", price_cnt_span.text) if price_cnt_span\
                    else re.sub(r"\s+", "", price_span.text)  
                desc.append([name, img, href, price, pr_code])
                dim_div = item.find("div", {"class": "prodDimension", "id": "metric"})
                _dim = re.sub(r"\s+", " ", dim_div.text.strip())
                dims = _dim.replace("cm", "cm,").split(",")
                print desc, dims
                break
                
if __name__ == "__main__":
    '''
    query:
        if exact name or product number given, script returns complete info about the precise product
        if normal search word given, like for example "szafka", script returns complete info about all the products that were found
    '''
    #query = 'trones'
    #query = '100.319.87'
    #query = '802.567.04'
    query = 'szafka'
    min_price = 1
    max_price = 5000
    crawl(query, min_price, max_price)
