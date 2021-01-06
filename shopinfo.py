import requests
import json
import math
import os
import apikey

keyid = apikey.keyid

class RestrantSearchApi:
    """レストラン検索APIリクエストのパラメータ作成"""
    def __init__(self):
        self._url = "https://api.gnavi.co.jp/RestSearchAPI/v3/"
        self._keyid = keyid
    
    @property
    def url(self):
        return self._url

    @property
    def keyid(self):
        return self._keyid
        
    def search_by_shop_id(self, shop_id):
        parameter = {}
        parameter['keyid'] = self._keyid
        parameter['id'] = shop_id
        
        return parameter

class ReputationSearchApi:
    """口コミAPIリクエストのパラメータ作成"""
    def __init__(self):
        self._url = "https://api.gnavi.co.jp/PhotoSearchAPI/v3/"
        self._keyid = keyid

    @property
    def url(self):
        return self._url

    @property
    def keyid(self):
        return self._keyid

    def search_by_menu(self, menu_name):
        parameter = {}
        parameter['keyid'] = self._keyid
        parameter['menu_name'] = menu_name

        return parameter

class GeoLocation:
    """位置情報のパラメータを作成"""
    @classmethod
    def set(self, latitude, longitude):
        geolocation = {}
        geolocation['latitude'] = latitude
        geolocation['longitude'] = longitude

        return geolocation   

class SearchRange:
    """検索範囲を指定 緯度/経度からの検索範囲(半径) 1:300m、2:500m、3:1000m、4:2000m、5:3000m"""
    @classmethod
    def set(self, num):
        range = {}
        range['range'] = num

        return range
    
class ApiRequestParameter:
    """APIリクエストのパラメータとして使うために複数の辞書をマージする"""
    @classmethod
    def merge(self, *args):
        parameter = {}

        for i in args:
            parameter.update(**i)
        
        return parameter

class ApiRequest:
    """APIリクエストとレスポンスを返す"""
    def __init__(self, url, param):
        self.url = url
        self.param = param
    
    def api_response(self):
        response = requests.get(self.url, params=self.param)

        return response.json()

    def return_code(self):
        """APIに正常終了のコードが存在しないためエラーコードが存在しない場合に正常と判断する(200を返す)"""
        """異常終了時のコードは https://api.gnavi.co.jp/api/manual/photosearch/ 参照"""
        res = self.api_response()
        try:
            error_code = res['gnavi']['error'][0]['code']
            return error_code
        except KeyError: # エラーコードが存在しない場合
            return 200
    
    def total_hits(self):
        res = self.api_response()
        total_hits = res['response']['total_hit_count']

        return total_hits

class ShopName(ApiRequest):
    """店名が漢字だと正しく発話されないのでレストラン検索APIから正しい店名をカタカナで取得する"""
    def __init__(self, url, param):
        super().__init__(url, param)
        
    def official_name(self):
        shop_data = self.api_response()
        official_name = shop_data['rest'][0]['name_kana']

        return official_name

class ReputationInfo(ApiRequest):
    """口コミAPIのレスポンスを辞書へ格納する"""
    def __init__(self, url, param):
        super().__init__(url, param)

    def official_shop_name(self, shop_id):
        url = RestrantSearchApi().url
        shop_id = RestrantSearchApi().search_by_shop_id(shop_id)
        official_shop_name = ShopName(url, shop_id).official_name()

        return official_shop_name

    def reputation_search(self):
        shop_data = self.api_response()['response']
        per_page = shop_data['hit_per_page']
        total_hits = self.total_hits()
        page = 1

        temp_reputation_info = {}
        index = 0
        while total_hits - (page * per_page) > 0:
            for i in range(per_page):
                temp_reputation_info.update({
                    shop_data[str(i)]['photo']['shop_name']: { 
                        "shop_id": shop_data[str(i)]['photo']['shop_id'],
                        "kana": self.official_shop_name(shop_data[str(i)]['photo']['shop_id']),
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
            remaining = total_hits - ((page-1) * per_page)
            for i in range(remaining):
                temp_reputation_info.update({
                    shop_data[str(i)]['photo']['shop_name']: { 
                        "menu": shop_data[str(i)]['photo']['menu_name'],
                        "shop_id": shop_data[str(i)]['photo']['shop_id'],
                        "kana": self.official_shop_name(shop_data[str(i)]['photo']['shop_id']),
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
