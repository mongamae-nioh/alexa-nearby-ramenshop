import requests
import json
import math
import os

keyid = "apikey"

class restrantApi:
    def __init__(self, category1, category2):
        self.url = "https://api.gnavi.co.jp/RestSearchAPI/v3/"
        self.keyid = keyid
        self.category1 = category1
        self.category2 = category2
        
    def baseinfo(self):
        baseinfo = {}
        baseinfo['keyid'] = self.keyid
        baseinfo['category_l'] = self.category1
        baseinfo['category_s'] = self.category2
        
        return baseinfo

class reputationApi:
    def __init__(self, menu):
        self.url = "https://api.gnavi.co.jp/PhotoSearchAPI/v3/"
        self.keyid = keyid
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
    '''APIリクエストのパラメータとして使うために複数の辞書をマージするクラス'''
#    def __init__(self):
#        pass

    def api_parameter(self, *args):
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

class removeUnnecessaryCharactor:
    def __init__(self, object):
        self.object = object
    
    def remove_linefeed(self):
        return self.object.replace('\r\n', '')

class restrantInfo(apiRequest):
    def __init__(self, url, param):
        super().__init__(url, param)
    
    def restrant_search(self):
        shop_data = self.api_request()     
        total_page = self.total_page()
        page = 1

        restrant_info = {}
        while total_page >= page:
            for shop in shop_data['rest']:
                restrant_info[shop['name']] = shop['name_kana']
            page += 1
            param = self.param
            param['offset_page'] = page
            response = requests.get(self.url, params=param)
            shop_data = response.json()

        return restrant_info    

class reputationInfo(apiRequest):
    def __init__(self, url, param):
        super().__init__(url, param)
    
    def reputation_search(self):
        shop_data = self.api_request()['response']
        per_page = shop_data['hit_per_page']
        hit_count = self.hit_count2()
        page = 1

        reputation_info = {}
        index = 0
        while hit_count - (page * per_page) > 0:
            for i in range(per_page):
#                reputation_info.update({
#                    index: {
#                        shop_data[str(i)]['photo']['shop_name']: { 
#                            "menu": shop_data[str(i)]['photo']['menu_name'],
#                            "comment": shop_data[str(i)]['photo']['comment'].replace('\r\n', ''),
#                            "score": shop_data[str(i)]['photo']['total_score'],
#                            "distance": shop_data[str(i)]['photo']['distance'],
#                            "url": shop_data[str(i)]['photo']['shop_url']
#                        }
#                    }})
#                index += 1
                reputation_info.update({
                    shop_data[str(i)]['photo']['shop_name']: { 
                        "menu": shop_data[str(i)]['photo']['menu_name'],
                        "comment": shop_data[str(i)]['photo']['comment'].replace('\r\n', ''),
                        "score": shop_data[str(i)]['photo']['total_score'],
                        "distance": shop_data[str(i)]['photo']['distance'],
                        "url": shop_data[str(i)]['photo']['shop_url']
                    }
                })
            page += 1
            param = self.param
            param['offset_page'] = page
            response = requests.get(self.url, params=param)
            shop_data = response.json()['response']
        else:
            remaining = hit_count - ((page-1) * per_page)
            for i in range(remaining):
                reputation_info.update({
                    shop_data[str(i)]['photo']['shop_name']: { 
                        "menu": shop_data[str(i)]['photo']['menu_name'],
                        "comment": shop_data[str(i)]['photo']['comment'].replace('\r\n', ''),
                        "score": shop_data[str(i)]['photo']['total_score'],
                        "distance": shop_data[str(i)]['photo']['distance'],
                        "url": shop_data[str(i)]['photo']['shop_url']
                    }
                })
        
        last_dict = {}
        index = 0
        for i,j in reputation_info.items():
            last_dict.update({
                index: {
                    i : {
                        "menu": reputation_info[i]['menu'],
                        "comment": reputation_info[i]['comment'],
                        "distance": reputation_info[i]['distance'],
                        "url": reputation_info[i]['url']
                    }
                }
            })
            index += 1
        
        last = json.dumps(last_dict, indent=4, ensure_ascii=False)
        print(last)
                
        return reputation_info

#param1 = restrantApi('RSFST08000', 'RSFST08008')
param1 = reputationApi('ラーメン')
apibase = param1.baseinfo()

param2 = geoLocation("43.0555316", "141.3526345")
geolocation = param2.geolocation()

merge = mergeApiParameter()
param = merge.api_parameter(apibase, geolocation)

url = param1.url

#shop = restrantInfo(url, param)
shop = reputationInfo(url, param)
#shop2 = shop.restrant_search()
shop2 = shop.reputation_search()
#hitcount = shop.hit_count2()
#print(shop2)

#for i,j in shop2.items():
#    mojiretsu = i + 'の口コミです。'
#    mojiretsu += j['comment'] + '現在地からの距離はおおよそ' + str(j['distance']) + 'メートルです。'
#    print(mojiretsu)

#print(hitcount)
#json = json.dumps(shop2, indent=4, ensure_ascii=False)
#print(json)
