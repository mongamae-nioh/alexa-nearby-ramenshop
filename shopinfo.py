import requests
import json
import math
import os

keyid = "apikey"

class restrantApi:
    '''レストラン検索APIリクエストのパラメータ作成'''
    def __init__(self, category1, category2):
        self._url = "https://api.gnavi.co.jp/RestSearchAPI/v3/"
        self._keyid = keyid
        self.category1 = category1
        self.category2 = category2
    
    @property
    def url(self):
        return self._url

    @property
    def keyid(self):
        return self._keyid
        
    def baseinfo(self):
        baseinfo = {}
        baseinfo['keyid'] = self._keyid
        baseinfo['category_l'] = self.category1
        baseinfo['category_s'] = self.category2
        
        return baseinfo

class reputationApi:
    '''口コミAPIリクエストのパラメータ作成'''
    def __init__(self, menu):
        self._url = "https://api.gnavi.co.jp/PhotoSearchAPI/v3/"
        self._keyid = keyid
        self.menu = menu

    @property
    def url(self):
        return self._url

    @property
    def keyid(self):
        return self._keyid

    def baseinfo(self):
        baseinfo = {}
        baseinfo['keyid'] = self._keyid
        baseinfo['menu_name'] = self.menu

        return baseinfo

class geoLocation:
    '''位置情報のパラメータを作成'''
    def __init__(self, latitude, longitude):
        self.latitude = latitude
        self.longitude = longitude

    def geolocation(self):
        geolocation = {}
        geolocation['latitude'] = self.latitude
        geolocation['longitude'] = self.longitude

        return geolocation    

class searchRange:
    '''検索範囲を指定'''
    def current_page(self, int):
        current_page = {}
        current_page['offset_page'] = self.int

        return current_page
    
    def range(self, int):
        range = {}
        range['range'] = self.int

        return range        

class mergeApiParameter:
    '''APIリクエストのパラメータとして使うために複数の辞書をマージする'''
    def api_parameter(self, *args):
        parameter = {}

        for i in args:
            parameter.update(**i)
        
        return parameter

class apiRequest:
    '''APIリクエストとレスポンスを返す'''
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

class restrantInfo(apiRequest):
    '''レストラン検索APIのレスポンスを辞書へ格納する'''
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
    '''口コミAPIのレスポンスを辞書へ格納する'''
    def __init__(self, url, param):
        super().__init__(url, param)
    
    def reputation_search(self):
        shop_data = self.api_request()['response']
        per_page = shop_data['hit_per_page']
        hit_count = self.hit_count2()
        page = 1

        temp_reputation_info = {}
        index = 0
        while hit_count - (page * per_page) > 0:
            for i in range(per_page):
                temp_reputation_info.update({
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
                temp_reputation_info.update({
                    shop_data[str(i)]['photo']['shop_name']: { 
                        "menu": shop_data[str(i)]['photo']['menu_name'],
                        "comment": shop_data[str(i)]['photo']['comment'].replace('\r\n', ''),
                        "score": shop_data[str(i)]['photo']['total_score'],
                        "distance": shop_data[str(i)]['photo']['distance'],
                        "url": shop_data[str(i)]['photo']['shop_url']
                    }
                })
                
        reputation_info = {}
        index = 0
        for i,j in temp_reputation_info.items():
            reputation_info.update({
                index: {
                    "name": i,
                    "menu": j['menu'],
                    "comment": j['comment'],
                    "distance": j['distance'],
                    "url": j['url']
                    }
                }
            )
            index += 1
        
        return reputation_info
