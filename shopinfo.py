import requests
import json
import math
import os
import apikey

keyid = apikey.keyid

class restrantSearchApi:
    '''レストラン検索APIリクエストのパラメータ作成'''
    def __init__(self):
        self._url = "https://api.gnavi.co.jp/RestSearchAPI/v3/"
        self._keyid = keyid
    
    @property
    def url(self):
        return self._url

    @property
    def keyid(self):
        return self._keyid
        
    def api_request(self, shop_id):
        parameter = {}
        parameter['keyid'] = self._keyid
        parameter['id'] = shop_id
        
        return parameter

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
    def set(self, latitude, longitude):
        geolocation = {}
        geolocation['latitude'] = latitude
        geolocation['longitude'] = longitude

        return geolocation   

class searchRange:
    '''検索範囲を指定 緯度/経度からの検索範囲(半径) 1:300m、2:500m、3:1000m、4:2000m、5:3000m'''
    def set(self, num):
        range = {}
        range['range'] = num

        return range
    
class apiRequestParameter:
    '''APIリクエストのパラメータとして使うために複数の辞書をマージする'''
    def merge(self, *args):
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

    def return_code(self):
        '''APIに正常終了のコードが存在しないためエラーコードが存在しない場合に正常と判断する(200を返す)'''
        '''異常終了時のコードは https://api.gnavi.co.jp/api/manual/photosearch/ 参照'''
        res = self.api_request()
        try:
            error_code = res['gnavi']['error'][0]['code']
            return error_code
        except KeyError: # エラーコードが存在しない場合
            return 200

    def hit_count(self):
        res = self.api_request()
        hitcount = res['response']['total_hit_count']

        return hitcount
        
    def total_page(self):
        res = self.api_request()
        total_page = math.ceil(res['response']['total_hit_count'] / res['response']['hit_per_page'])
        
        return total_page

class reputationInfo(apiRequest):
    '''口コミAPIのレスポンスを辞書へ格納する'''
    def __init__(self, url, param):
        super().__init__(url, param)

    def shop_kana(self, id):
        url = restrantSearchApi().url
        shop_id = restrantSearchApi().api_request(id)
        shop_kana = shopNameKana(url, shop_id).get_kana()

        return shop_kana
    
    def reputation_search(self):
        shop_data = self.api_request()['response']
        per_page = shop_data['hit_per_page']
        hit_count = self.hit_count()
        page = 1

        temp_reputation_info = {}
        index = 0
        while hit_count - (page * per_page) > 0:
            for i in range(per_page):
                temp_reputation_info.update({
                    shop_data[str(i)]['photo']['shop_name']: { 
                        "shop_id": shop_data[str(i)]['photo']['shop_id'],
                        "kana": self.shop_kana(shop_data[str(i)]['photo']['shop_id']),
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
                        "shop_id": shop_data[str(i)]['photo']['shop_id'],
                        "kana": self.shop_kana(shop_data[str(i)]['photo']['shop_id']),
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
                    "shop_id": j['shop_id'],
                    "kana": j['kana'],
                    "menu": j['menu'],
                    "comment": j['comment'],
                    "distance": j['distance'],
                    "url": j['url']
                    }
                }
            )
            index += 1
        return reputation_info

class shopNameKana(apiRequest):
    '''レストラン検索APIから店名の読みがなを取得する'''
    def __init__(self, url, param):
        super().__init__(url, param)

    def get_kana(self):
        shop_data = self.api_request()
        shop_kana = shop_data['rest'][0]['name_kana']
        return shop_kana
