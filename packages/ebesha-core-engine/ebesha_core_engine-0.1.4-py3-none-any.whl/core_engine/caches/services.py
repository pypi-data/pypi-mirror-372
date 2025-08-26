import os
import redis
import json
import logging
from datetime import datetime,timedelta

class CacheServices(object):
    def __init__(self):
        self.conn = redis.Redis(host=os.environ.get("REDIS_HOST"), port=os.environ.get("REDIS_PORT"))
		
    def set_caches_trust_device(self, key, data):
        try:
            self.conn.psetex(key, (timedelta(seconds=int(os.environ.get("CACHE_IDLE"))*60*60*12*60)), json.dumps(data))
            return json.loads(self.conn.get(key))
        except:
            logging.error(f"can't create data cache {key}")
            return None
		
    def set_caches(self, key, data):
        try:
            self.conn.psetex(key, (timedelta(seconds=int(os.environ.get("CACHE_IDLE"))*60)), json.dumps(data))
            return json.loads(self.conn.get(key))
        except:
            logging.error(f"can't create data cache {key}")
            return None
		
    def get_caches(self, key):
        try:
            return json.loads(self.conn.get(key))
        except:
            return None
			
    def set_idle_caches(self, key, data):
        try:
            self.conn.psetex(key, (timedelta(seconds=60*60)), json.dumps(data))
            return json.loads(self.conn.get(key))
        except:
            logging.error(f"can't create data cache {key}")
            return None
		
    def get_idle_caches(self, key):
        try:
            return json.loads(self.conn.get(key))
        except:
            return None
			
    def create_data_caches(self, key, id, data):
        try:
            if data.get('name'):
                data = {"id":id, "name":data.get('name')}
                self.set_caches(key, data)
        except:
            return None
			
    def update_data_caches(self, key, data):
        try:
            if data.get('name') and data.get('color'):
                data = {"id":data.get('id'), "name":data.get('name'), "color":data.get('color')}
                self.set_caches(key, data)
            elif data.get('name'):
                data = {"id":data.get('id'), "name":data.get('name')}
                self.set_caches(key, data)
        except:
            return None

    def change_format_datetime(self, datas):
        for data in datas:
            for key, value in enumerate(data):
                if isinstance(data[value], datetime): 
                    data.update({value:data[value].strftime("%Y-%m-%dT%H:%M:%S.%f")})
        return datas

    def set_list_caches(self, key, data, module, tenant):
        if data.get('data'):
            self.change_format_datetime(data.get('data'))
			
        try:
            key = f"{key}{module}"
            self.conn.psetex(key, (timedelta(seconds=60*60)), json.dumps(data))
            #self.set_caches(f"{module}_STATUS_UPDATE_{tenant}", {"status":False})
            self.conn.delete(f"{module}_STATUS_UPDATE_{tenant}")
            return json.loads(self.conn.get(key))
        except:
            logging.error(f"Cant create cache {key}")
            return None
		
    def get_list_caches(self, key, module, tenant):
        try:
            key = f"{key}{module}"
            if self.conn.get(f"{module}_STATUS_UPDATE_{tenant}"):
                update_status = json.loads(self.conn.get(f"{module}_STATUS_UPDATE_{tenant}"))
                if (update_status.get("status")):
                    return None
            #    return json.loads(self.conn.get(key))
            #else:
            #    return json.loads(self.conn.get(key))
            #return json.loads(self.conn.get(key))
            return None
        except:
            return None
			
    def delete_caches(self, key):
        try:
            #if self.conn.get(f"{module}_STATUS_UPDATE_{tenant}"):
            #    self.conn.delete(key)
            self.conn.delete(key)
            return None
        except:
            return None
		