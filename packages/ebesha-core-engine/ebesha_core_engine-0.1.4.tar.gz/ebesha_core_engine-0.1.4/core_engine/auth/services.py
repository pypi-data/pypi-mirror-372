import os
import jwt
from core_engine.caches.services import CacheServices
from datetime import datetime, timedelta

from core_engine.bridges.access import UserManagement

caches = {}

class AuthorizationService(object):
    def __init__(self):
        self.cache_services = CacheServices()

    def get_access(self, token, module, access, tenant=None):
        datas = self._caching_autorization(token, module, access, tenant)
        return self._decode_access(datas)

    def _decode_access(self, datas):
        if datas.get('status') == 200:
            jwt_token = bytes(datas.get('data').get('detail'), 'utf-8')
            results = {"status":datas.get('status'), "detail":jwt.decode(jwt_token, os.environ.get("JWT_TOKEN"), algorithms=['HS256'])}
            return results
        return datas

    def _caching_autorization(self, token, module, access, tenant=None):
        '''if caches.get(f"{token}|{module}|{access}{tenant}"):
            if caches.get(f"{token}|{module}|{access}{tenant}").get('detail').get('status') == 200:
                if (datetime.now() - caches.get(f"{token}|{module}|{access}{tenant}").get('last_date')) > (timedelta(0, int(os.environ.get("CACHE_IDLE")) * 60, 0)):
                    del caches[f"{token}|{module}|{access}{tenant}"]
                    return self._request_access(token, module, access, tenant)
            else:
                return self._request_access(token, module, access, tenant)
            return caches.get(f"{token}|{module}|{access}{tenant}").get('detail')
        else:
            return self._request_access(token, module, access, tenant)'''
        data_cache = self.cache_services.get_idle_caches(f"{module}_{tenant}_{token}_{access}")
        if data_cache:
            if data_cache.get('detail').get('status') == 200:
                return data_cache.get('detail')
            else:
                return self._request_access(token, module, access, tenant)
        else:
            return self._request_access(token, module, access, tenant)

    def _request_access(self, token, module, access, tenant=None):
        user_management_client = UserManagement(token, module, access, tenant)
        datas = user_management_client.check_token()
        #caches.update({f"{token}|{module}|{access}{tenant}":{"module":module, "access":access, "last_date":datetime.now(), "detail":datas}})
        self.cache_services.set_idle_caches(f"{module}_{tenant}_{token}_{access}", {"module":module, "access":access, "detail":datas})
        return datas
