import requests
import json
import math
import os

class baseInfo:
    def __init__(self):
        self.url = "https://api.gnavi.co.jp/RestSearchAPI/v3/"
        self.keyid = "apikey"

    def baseinfo(self):
        baseinfo = {}
        baseinfo['keyid'] = self.keyid
        baseinfo['url'] = self.url

        return baseinfo

class category:
    def __init__(self, category1, category2):
        self.category1 = category1
        self.category2 = category2

    def category(self):
        category = {}
        category['category_l'] = self.category1
        category['category_s'] = self.category2
        
        return category

class geoLocation:
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def geolocation(self):
        geolocation = {}
        geolocation['latitude'] = self.latitude
        geolocation['longitude'] = self.longitude

        return geolocation    

class menu:
    def __init__(self, menu):
        self.menu = menu
    
#    def menu(self):
#        menu = {}
#        menu['menu_name'] = menu 

#        return menu

class mergeParam:
    def __init__(self):
        pass

    def api_parameter(self, *args):
        '''複数の辞書をマージする関数'''
        parameter = {}
        print(args)
        
        for i in args:
            parameter.update(**i)
        
        return parameter

param = baseInfo()
print(param.baseinfo())

param2 = geoLocation('50', '100')
print(param2.geolocation())


param3 = mergeParam()
mergeparam = param3.api_parameter(param.baseinfo(), param2.geolocation())
print(mergeparam)

'''
class apiResponse:
    def __init__(self, latitude, longitude, category1, category2):
        self.url = "https://api.gnavi.co.jp/RestSearchAPI/v3/"
        self.keyid = "apikey"
        self.latitude = latitude
        self.longitude = longitude
        self.category1 = category1
        self.category2 = category2

    def category(self):
        category = {}
        category['category_l'] = self.category1
        category['category_s'] = self.category2
        
        return category
    
    def geolocation(self):
        geolocation = {}
        geolocation['latitude'] = self.latitude
        geolocation['longitude'] = self.longitude

        return geolocation

    def current_page(self):
        current_page = {}
        current_page['offset_page'] = 1

        return current_page
    
    def range(self):
        range = {}
        range['range'] = 1

        return range

    def api_parameter(self):
        parameter = {
            "keyid": self.keyid,

        }
        
        parameter.update(
            **self.geolocation(), 
            **self.category(), 
            **self.current_page(), 
            **self.range()
            )
        
        return parameter

    def api_request(self):
        param = self.api_parameter()
        response = requests.get(self.url, params=param)
                
        return response.json()

    def hit_count(self):
        res = self.api_request()
        hitcount = res['total_hit_count']

        return hitcount
        
    def total_page(self):
        res = self.api_request()
        total_page = math.ceil(res['total_hit_count'] / res['hit_per_page'])
        
        return total_page

    def shop_info(self):
        shop_data = self.api_request()     
        total_page = self.total_page()
        page = 1

        shopinfo = {}
        while total_page >= page:
            for shop in shop_data['rest']:
                shopinfo[shop['name']] = shop['name_kana']
            page += 1
            param = self.api_parameter()
            param['offset_page'] = page
            response = requests.get(self.url, params=param)
            shop_data = response.json()

        return shopinfo

'''



#shopsearch = apiResponse("43.0555316", "141.3526345", 'RSFST08000', 'RSFST08008')

#hit_count = shopsearch.hit_count()
#total_page = shopsearch.total_page()
#shop_info = shopsearch.shop_info()

#print(hit_count)
#print(total_page)
#print(shop_info)
