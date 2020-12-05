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
        '''APIリクエストのパラメータとして使うために複数の辞書をマージするクラス'''
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

    def hit_count2(self):
        res = self.api_request()
        hitcount = res['response']['total_hit_count']

        return hitcount
        
    def total_page2(self):
        res = self.api_request()
        total_page = math.ceil(res['response']['total_hit_count'] / res['response']['hit_per_page'])
        
        return total_page

    def current_page(self):
        current_page = {}
        current_page['offset_page'] = 1

        return current_page
    
    def range(self):
        range = {}
        range['range'] = 1

        return range        

class restrantInfo(apiRequest):
    def __init__(self, url, param):
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

class kuchikomiInfo(apiRequest):
    def __init__(self, url, param):
        super().__init__(url, param)
    
    def shop_info(self):
        shop_data2 = self.api_request()
        shop_data = shop_data2['response']
#        print(shop_data)
        per_page = shop_data['hit_per_page']
        total_page = self.total_page2()
        print('total page is ' + str(total_page))
        hit_count = self.hit_count2()
        print('hit count is ' + str(hit_count))
        page = 1

        kuchikomiinfo = {}
        nokori = hit_count - (per_page * page)

        while hit_count - (per_page * page) > 0:
            print('nokori is ' + str(nokori))
            print('全部表示する')
            for i in range(per_page):
                kuchikomiinfo[shop_data[str(i)]['photo']['shop_name']] = shop_data[str(i)]['photo']['comment']
                print(i)
                print(shop_data[str(i)]['photo']['shop_name'])
            page += 1
            param = self.param
            param['offset_page'] = page
            print(param)
            print(url)
            response = requests.get(self.url, params=param)
            shop_data3 = response.json()
            shop_data = shop_data3['response']
        else:
            nokori2 = hit_count - (per_page * (page-1))
            print('nokori2 is ' + str(nokori2))
            print('残りだけ表示する')
            for i in range(nokori2):
                print(i)
                print(shop_data[str(i)]['photo']['shop_name'])
            
        return kuchikomiinfo    

#param1 = restrantApi('RSFST08000', 'RSFST08008')
param1 = kuchikomiApi('ラーメン')
apibase = param1.baseinfo()

param2 = geoLocation("43.0555316", "141.3526345")
geolocation = param2.geolocation()

merge = mergeApiParameter()
param = merge.api_parameter(apibase, geolocation)

url = param1.url

#shop = restrantInfo(url, param)
shop = kuchikomiInfo(url, param)
shop2 = shop.shop_info()
#print(shop2)

#json = json.dumps(info, indent=4, ensure_ascii=False)
#print(json)

