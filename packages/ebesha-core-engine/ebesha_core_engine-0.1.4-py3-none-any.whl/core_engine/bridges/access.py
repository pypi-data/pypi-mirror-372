import json
import requests
from core_engine.constants import (
    MappingPathAPI
)

class UserManagement(object):
    def __init__(self, token, module, access, tenant=None):
        self.token = token
        self.module = module
        self.access = access
        self.tenant = tenant

    def _construct_response(self, resp):
        if resp.status_code==200:
            response = dict(
                status=resp.status_code,
                data=resp.json()
            )
            return response
        else:
            response = dict(
                status=resp.status_code,
                detail=resp.json()
            )
            return response
		
    def _construct_responses(self, status, resp):
        response = dict(
            status=status,
            data=resp
        )
        return response

    def check_token(self):
        try:
            headers = dict(
                Authorization=self.token
            )
            body = dict(module=self.module, access=self.access, tenant=self.tenant)
            res = requests.post(url=f"{MappingPathAPI.path.get('valid_token')}", headers=headers, data=body)
        
            response = self._construct_response(res)
            return response
        except Exception as err:
            message = {"status":"400", "detail":str(err).split("\n")}
            return message