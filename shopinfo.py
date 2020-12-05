import requests
import json
import math
import os

class restrantApi:
    def __init__(self, category1, category2):
        self.url = "https://api.gnavi.co.jp/RestSearchAPI/v3/"
        self.keyid = "apikey"
        self.category1 = category1
        self.category2 = category2
        
    def baseinfo(self):
        baseinfo = {}
        baseinfo['keyid'] = self.keyid
        baseinfo['category_l'] = self.category1
        baseinfo['category_s'] = self.category2
        
        return baseinfo

class kuchikomiApi:
    def __init__(self, menu):
        self.url = "https://api.gnavi.co.jp/PhotoSearchAPI/v3/"
        self.keyid = "apikey"
        self.menu = menu
    
    def baseinfo(self):
        baseinfo = {}
        baseinfo['keyid'] = self.keyid
        baseinfo['menu_name'] = self.menu

        return baseinfo

class geoLocation:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def geolocation(self):
        geolocation = {}
        geolocation['latitude'] = self.latitude
        geolocation['longitude'] = self.longitude

        return geolocation    

class mergeApiParameter:
    def __init__(self):
        pass

    def api_parameter(self, *args):
        '''複数の辞書をマージするクラス'''
        parameter = {}

        for i in args:
            parameter.update(**i)
        
        return parameter

class apiRequest:
    def __init__(self, url, param):
        self.url = url
        self.param = param
    
    def api_request(self):
        response = requests.get(self.url, params=self.param)

        return response.json()

    def hit_count(self):
        res = self.api_request()
        hitcount = res['total_hit_count']

        return hitcount
        
    def total_page(self):
        res = self.api_request()
        total_page = math.ceil(res['total_hit_count'] / res['hit_per_page'])
        
        return total_page

    def current_page(self):
        current_page = {}
        current_page['offset_page'] = 1

        return current_page
    
    def range(self):
        range = {}
        range['range'] = 1

        return range        

class shopInfo(apiRequest):
    def __init__(self):
        super().__init__(url, param)
    
    def shop_info(self):
        shop_data = self.api_request()     
        total_page = self.total_page()
        page = 1

        shopinfo = {}
        while total_page >= page:
            for shop in shop_data['rest']:
                shopinfo[shop['name']] = shop['name_kana']
            page += 1
            param = self.param
            param['offset_page'] = page
            response = requests.get(self.url, params=param)
            shop_data = response.json()

        return shopinfo    


param1 = restrantApi('RSFST08000', 'RSFST08008')
#print(param.baseinfo())

url = param1.url
param2 = geoLocation("43.0555316", "141.3526345")
#print(param2.geolocation())


param3 = mergeApiParameter()
param = param3.api_parameter(param1.baseinfo(), param2.geolocation())
#print(mergeparam)

res1 = apiRequest(url, param)
res2 = res1.api_request()
#print(res2)

hit_count = res1.hit_count()
#print(hit_count)

total_page = res1.total_page()
#print(total_page)

shop = shopInfo()

#print('url is ' + shop.url)
#print(shop.param)

shopinfo = shop.shop_info()
print(shopinfo)
