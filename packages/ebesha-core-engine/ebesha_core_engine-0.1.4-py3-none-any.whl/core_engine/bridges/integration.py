import json
import requests
import asyncio
import aiohttp
from datetime import datetime
from django.conf import settings
from core_engine.caches.services import CacheServices
from core_engine.constants import (
    MappingPathAPI,
    MappingMultiPathAPI,
    MappingRefferenceAPI,
    MappingDetailPathAPI,
    MappingSearchAPI,
    ModuleName,
    AdditionalType,
    RootAPI,
    UMModuleIntegration
)


class Integration(object):
    def __init__(self, token, module, access):
        self.token = token
        self.module = module
        self.access = access
        self.cache_services = CacheServices()

    async def _aiohttp_single_request(self, url, headers, body):
        session = aiohttp.ClientSession()
        responses = await session.get(url, headers=headers, data=body, ssl=False)
        value = await responses.json()
        await session.close()
        return value

    async def _aiohttp_request(self, url, headers, body):
        session = aiohttp.ClientSession()
        responses = await session.get(url, headers=headers, data=body, ssl=False)
        value = self._construct_response_aiohttp(responses, await responses.json())
        await session.close()
        return value

    async def _aiohttp_requests(self, url, headers, body):
        session = aiohttp.ClientSession()
        responses = await session.get(url, headers=headers, data=body, ssl=False)
        value = self._construct_response_aiohttps(responses, await responses.json())
        await session.close()
        return value

    async def _aiohttp_refference_requests(self, url, headers, body):
        session = aiohttp.ClientSession()
        responses = await session.post(url, headers=headers, data=body, ssl=False)
        value = self._construct_response_aiohttps(responses, await responses.json())
        await session.close()
        return value

    async def _aiohttp_patch(self, url, headers, body):
        session = aiohttp.ClientSession()
        responses = await session.patch(url, headers=headers, data=body, ssl=False)
        value = self._construct_response_aiohttps(responses, await responses.json())
        await session.close()
        return value

    def _construct_response(self, resp):
        if resp.status_code == 200:
            data = resp.json()
            if len(data.get('data')) > 0:
                return data.get('data')[0]
        else:
            return None

    def _construct_responses(self, resp):
        if resp.status_code == 200:
            data = resp.json()
            if len(data.get('data')) > 0:
                return data.get('data')
        else:
            return None

    def _construct_response_aiohttp(self, resp, data):
        if resp.status == 200:
            if len(data.get('data')) > 0:
                return data.get('data')[0]
        else:
            return None

    def _construct_response_aiohttps(self, resp, data):
        if resp.status == 200:
            if len(data.get('data')) > 0:
                return data.get('data')
        else:
            return None

    async def _check_additional_field(self, datas, module):
        tmp_data_additional_fields = []
        for data in datas:
            additional = []
            if len(tmp_data_additional_fields) > 0:
                for tmp_data_additional_field in tmp_data_additional_fields:
                    urls = {}
                    tasks = []
                    async with aiohttp.ClientSession() as session:
                        tmp_value = {}
                        for tmp_data_additional in tmp_data_additional_field.get('data'):
                            url, headers, body = self._check_additional_mapping(tmp_data_additional.get(
                                'id'), data.get('id'), tmp_data_additional_field.get('tenant'))
                            tasks.append(asyncio.create_task(session.get(
                                url, headers=headers, data=body, ssl=False)))
                            tmp_value.update({url: {"id": None, "additional_field": tmp_data_additional.get('id'), "name": tmp_data_additional.get(
                                'name'), "label": tmp_data_additional.get('label'), "data": None, "type": tmp_data_additional.get('type')}})

                        responses = await asyncio.gather(*tasks)
                        for response in responses:
                            value = self._construct_response_aiohttps(response, await response.json())
                            if value is not None:
                                tmp_value[f"{response.url}"].update(
                                    {"id": value[0].get("id")})
                                tmp_value[f"{response.url}"].update(
                                    {"data": value[0].get("data")})
                                if tmp_value[f"{response.url}"].get('type') == AdditionalType.Dropdown:
                                    tmp_value[f"{response.url}"].update({"refference_api": MappingRefferenceAPI.refference.get(
                                        ModuleName.EBESHA_CRM_SETTING_ADDITIONAL_DATA)})
                                additional.append(
                                    tmp_value.get(f"{response.url}"))
                            else:
                                if tmp_value[f"{response.url}"].get('type') == AdditionalType.Dropdown:
                                    tmp_value[f"{response.url}"].update({"refference_api": MappingRefferenceAPI.refference.get(
                                        ModuleName.EBESHA_CRM_SETTING_ADDITIONAL_DATA)})
                                additional.append(
                                    tmp_value.get(f"{response.url}"))
                        await session.close()
            else:
                url, headers, body = self._identify_module(
                    ModuleName.EBESHA_CRM_SETTING_ADDITIONAL_FIELD)
                res = requests.get(url=url.format(module),
                                   headers=headers, data=body)
                val = self._construct_responses(res)
                if val is not None:
                    tmp_data_additional_fields.append(
                        {"tenant": data.get('tenant').get('id'), "module": module, "data": val})
                else:
                    tmp_data_additional_fields.append(
                        {"tenant": data.get('tenant').get('id'), "module": module, "data": []})

                for tmp_data_additional_field in tmp_data_additional_fields:
                    urls = {}
                    tasks = []
                    async with aiohttp.ClientSession() as session:
                        tmp_value = {}

                        for tmp_data_additional in tmp_data_additional_field.get('data'):
                            url, headers, body = self._check_additional_mapping(tmp_data_additional.get(
                                'id'), data.get('id'), tmp_data_additional_field.get('tenant'))
                            tasks.append(asyncio.create_task(session.get(
                                url, headers=headers, data=body, ssl=False)))
                            tmp_value.update({url: {"id": None, "additional_field": tmp_data_additional.get('id'), "name": tmp_data_additional.get(
                                'name'), "label": tmp_data_additional.get('label'), "data": None, "type": tmp_data_additional.get('type')}})

                        responses = await asyncio.gather(*tasks)
                        for response in responses:
                            value = self._construct_response_aiohttps(response, await response.json())
                            if value is not None:
                                tmp_value[f"{response.url}"].update(
                                    {"id": value[0].get("id")})
                                tmp_value[f"{response.url}"].update(
                                    {"data": value[0].get("data")})
                                if tmp_value[f"{response.url}"].get('type') == AdditionalType.Dropdown:
                                    tmp_value[f"{response.url}"].update({"refference_api": MappingRefferenceAPI.refference.get(
                                        ModuleName.EBESHA_CRM_SETTING_ADDITIONAL_DATA)})
                                additional.append(
                                    tmp_value.get(f"{response.url}"))
                            else:
                                if tmp_value[f"{response.url}"].get('type') == AdditionalType.Dropdown:
                                    tmp_value[f"{response.url}"].update({"refference_api": MappingRefferenceAPI.refference.get(
                                        ModuleName.EBESHA_CRM_SETTING_ADDITIONAL_DATA)})
                                additional.append(
                                    tmp_value.get(f"{response.url}"))

                        await session.close()
            data.update({"additional_fields": additional})

    def _check_additional_mapping(self, additional_id, refference_id, tenant):
        url, headers, body = self._identify_module(
            ModuleName.EBESHA_CRM_SETTING_ADDITIONAL_MAPPING)
        return url.format(refference_id, additional_id), headers, body

    def _identify_body(self, body, module):
        if body is not None:
            for idx, key in enumerate(body):
                body[key] = (body[key].format(module))
            return body
        return None

    def _identify_header(self, headers):
        new_header = {}
        if headers is not None:
            for idx, key in enumerate(headers):
                if key == "Authorization":
                    new_header.update(
                        {f"{key}": headers[key].format(self.token)})
                else:
                    new_header.update({f"{key}": f"{headers[key]}"})
            return new_header
        return None

    def _identify_root_module(self, key):
        return RootAPI.path.get(f"{key}").get('url'), self._identify_header(RootAPI.path.get(f"{key}").get('headers')), RootAPI.path.get(f"{key}").get('body')

    def _identify_module(self, key):
        return MappingPathAPI.path.get(f"{key}").get('url'), self._identify_header(MappingPathAPI.path.get(f"{key}").get('headers')), self._identify_body(MappingPathAPI.path.get(f"{key}").get('body'), key)

    def _identify_module_multi_search(self, key):
        return MappingMultiPathAPI.path.get(f"{key}").get('url'), self._identify_header(MappingMultiPathAPI.path.get(f"{key}").get('headers')), self._identify_body(MappingMultiPathAPI.path.get(f"{key}").get('body'), key)

    def _identify_detail_module(self, key):
        return MappingDetailPathAPI.path.get(f"{key}").get('url'), self._identify_header(MappingDetailPathAPI.path.get(f"{key}").get('headers')), self._identify_body(MappingDetailPathAPI.path.get(f"{key}").get('body'), key)

    def _find_identify_module(self, key):
        return MappingSearchAPI.search.get(f"{key}").get('url'), self._identify_header(MappingSearchAPI.search.get(f"{key}").get('headers')), self._identify_body(MappingSearchAPI.search.get(f"{key}").get('body'), key)

    def _refference_identify_module(self, key):
        # Start check share setting with flag #
        if key == ModuleName.EBESHA_CRM_SETTING_STATUS or key == ModuleName.EBESHA_CRM_SETTING_PRIORITY or key == ModuleName.EBESHA_CRM_SETTING_ORIGIN:
            if self.module == ModuleName.EBESHA_CRM_SETTING_CASE_AUTO_GENERATE:
                return f"{MappingRefferenceAPI.refference.get(key).get('url')}&module_flag={ModuleName.EBESHA_CRM_TR_CASE}", self._identify_header(MappingRefferenceAPI.refference.get(f"{key}").get('headers')), self._identify_body(MappingRefferenceAPI.refference.get(f"{key}").get('body'), key)
            if key == ModuleName.EBESHA_CRM_SETTING_STATUS:
                if self.module == ModuleName.EBESHA_CRM_SETTING_SALES_SLA:
                    return f"{MappingRefferenceAPI.refference.get(key).get('url')}&module_flag={ModuleName.EBESHA_SALES_TR_DEAL}", self._identify_header(MappingRefferenceAPI.refference.get(f"{key}").get('headers')), self._identify_body(MappingRefferenceAPI.refference.get(f"{key}").get('body'), key)
                elif self.module == ModuleName.EBESHA_SETTING_GENERAL_NOTIFICATION:
                    return f"{MappingRefferenceAPI.refference.get(key).get('url')}&module_flag={ModuleName.EBESHA_CRM_TR_CASE}", self._identify_header(MappingRefferenceAPI.refference.get(f"{key}").get('headers')), self._identify_body(MappingRefferenceAPI.refference.get(f"{key}").get('body'), key)
            return f"{MappingRefferenceAPI.refference.get(key).get('url')}&module_flag={self.module}", self._identify_header(MappingRefferenceAPI.refference.get(f"{key}").get('headers')), self._identify_body(MappingRefferenceAPI.refference.get(f"{key}").get('body'), key)
        # End check share setting with flag #

        return MappingRefferenceAPI.refference.get(key).get("url"), self._identify_header(MappingRefferenceAPI.refference.get(f"{key}").get('headers')), self._identify_body(MappingRefferenceAPI.refference.get(f"{key}").get('body'), key)

    def check_integration(self, datas, integration_datas, module, additional_field, tenant=None):
        try:
            for integration_data in integration_datas:
                tmp_datas = {}
                for data in datas.get('data'):
                    if integration_data.get('name') in data:
                        if data[integration_data.get('name')] is not None:
                            id = str(data[integration_data.get('name')])
                            '''if len(tmp_datas) > 0:
                                if tmp_datas.get(f"{integration_data.get('name')}|{id}|{tenant}") is not None:
                                   data[integration_data.get('name')]= tmp_datas.get(f"{integration_data.get('name')}|{id}|{tenant}")
                                else:
                                    url, headers, body = self._identify_module(integration_data.get('integration'))
                                    res = (asyncio.run(self._aiohttp_request(url.format(data.get(integration_data.get('name'))), headers, body)))
                                    data[integration_data.get('name')] = res
                                    tmp_datas.update({f"{integration_data.get('name')}|{id}|{tenant}":data[integration_data.get('name')]})
                            else:
                                url, headers, body = self._identify_module(integration_data.get('integration'))
                                res = (asyncio.run(self._aiohttp_request(url.format(data.get(integration_data.get('name'))), headers, body)))
                                data[integration_data.get('name')] = res
                                tmp_datas.update({f"{integration_data.get('name')}|{id}|{tenant}":data[integration_data.get('name')]})'''
                            if id is not None and id.strip() != "":
                                if self.cache_services.get_caches(f"{integration_data.get('integration')}_{tenant}_{id}") is not None:
                                    data[integration_data.get('name')] = self.cache_services.get_caches(
                                        f"{integration_data.get('integration')}_{tenant}_{id}")
                                else:
                                    url, headers, body = self._identify_module(
                                        integration_data.get('integration'))
                                    res = (asyncio.run(self._aiohttp_request(url.format(
                                        data.get(integration_data.get('name'))), headers, body)))
                                    self.cache_services.set_caches(
                                        f"{integration_data.get('integration')}_{tenant}_{id}", res)
                                    data[integration_data.get('name')] = res
                            else:
                                data[integration_data.get('name')] = None
            if additional_field is not None:
                asyncio.run(self._check_additional_field(
                    datas.get('data'), module))
            return datas
        except Exception as err:
            message = {"status": "400", "detail": str(err).split("\n")}
            return message

    def meta_data_additional_field(self, module):
        url, headers, body = self._identify_module(
            ModuleName.EBESHA_CRM_SETTING_ADDITIONAL_FIELD)

        res = requests.get(url=url.format(module), headers=headers, data=body)
        vals = self._construct_responses(res)

        if vals is not None:
            for val in vals:
                if val.get('type') == AdditionalType.Dropdown:
                    url, headers, body = self._refference_identify_module(
                        ModuleName.EBESHA_CRM_SETTING_ADDITIONAL_DATA)
                    val.update(
                        {"refference_api": {"url": url, "headers": headers, "body": body}})
        return vals

    def find_search_integration(self, module, search):
        get_id = []
        try:
            if search != "":
                url, headers, body = self._find_identify_module(module)
                if module in UMModuleIntegration.get_data:
                    responses = (asyncio.run(self._aiohttp_requests(url.format(search), headers, body)))
                else:
                    responses = (asyncio.run(self._aiohttp_refference_requests(url.format(search), headers, body)))
                if responses is not None:
                    for response in responses:
                        get_id.append(response.get('id'))
            return get_id
        except Exception as err:
            message = {"status": "400", "detail": str(err).split("\n")}
            return message

    def user_online_status(self, module, id):
        try:
            url, headers, body = self._identify_root_module(module)
            res = (asyncio.run(self._aiohttp_single_request(
                url.format(id), headers, body)))
            return res
        except Exception as err:
            message = {"status": "400", "detail": str(err).split("\n")}
            return message

    def user_management_module(self, module, id):
        try:
            url, headers, body = self._identify_root_module(module)
            res = (asyncio.run(self._aiohttp_single_request(
                url.format(id), headers, body)))
            return res
        except Exception as err:
            message = {"status": "400", "detail": str(err).split("\n")}
            return message

    def user_list(self, module, tenant):
        try:
            url, headers, body = self._identify_root_module(module)
            body['tenant'] = tenant
            res = (asyncio.run(self._aiohttp_single_request(url, headers, body)))
            return res
        except Exception as err:
            message = {"status": "400", "detail": str(err).split("\n")}
            return message

    def get_user_list(self, module, id):
        try:
            url, headers, body = self._identify_root_module(module)
            if self.cache_services.get_caches(f"{url.format(id)}_{self.token}") is not None:
                res = self.cache_services.get_caches(
                    f"{url.format(id)}_{self.token}")
            else:
                res = (asyncio.run(self._aiohttp_requests(
                    url.format(id), headers, body)))
                self.cache_services.set_caches(
                    f"{url.format(id)}_{self.token}", res)
            return res
        except Exception as err:
            message = {"status": "400", "detail": str(err).split("\n")}
            return message

    def get_user_access_list(self, module, menu, tenant, create, read, update, delete, is_self_data):
        try:
            url, headers, body = self._identify_root_module(module)
            keys = f"{url}_{module}_{menu}_{create}_{read}_{update}_{delete}_{is_self_data}_{tenant}"
            body['module'] = menu
            body['tenant'] = tenant
            body['create'] = create
            body['read'] = read
            body['update'] = update
            body['delete'] = delete
            body['is_self_data'] = is_self_data
            if self.cache_services.get_caches(keys) is not None:
                res = self.cache_services.get_caches(keys)
            else:
                res = (asyncio.run(self._aiohttp_single_request(url, headers, body)))
                self.cache_services.set_caches(keys, res)
            return res
        except Exception as err:
            message = {"status": "400", "detail": str(err).split("\n")}
            return message

    def get_service_category_parent(self, module, tenant, id):
        try:
            url, headers, body = self._identify_module_multi_search(module)
            if self.cache_services.get_caches(f"{url.format(id)}_{module}_{tenant}_{self.token}") is not None:
                res = self.cache_services.get_caches(
                    f"{url.format(id)}_{module}_{tenant}_{self.token}")
            else:
                res = (asyncio.run(self._aiohttp_requests(
                    url.format(id), headers, body)))
                self.cache_services.set_caches(
                    f"{url.format(id)}_{module}_{tenant}_{self.token}", res)
            return res
        except Exception as err:
            message = {"status": "400", "detail": str(err).split("\n")}
            return message

    def get_member_list(self, base_url, module_target, module, id):
        try:
            url, headers, body = self._identify_root_module(module)
            body['module'] = module_target
            if self.cache_services.get_caches(f"{url.format(base_url, id)}_{self.token}") is not None:
                res = self.cache_services.get_caches(
                    f"{url.format(base_url, id)}_{self.token}")
            else:
                res = (asyncio.run(self._aiohttp_requests(
                    url.format(base_url, id), headers, body)))
                self.cache_services.set_caches(
                    f"{url.format(base_url, id)}_{self.token}", res)
            return res
        except Exception as err:
            message = {"status": "400", "detail": str(err).split("\n")}
            return message

    def get_role_user(self, module, type='', user_id=''):
        try:
            url, headers, body = self._identify_root_module(module)
            if self.cache_services.get_caches(f"{url.format(type,user_id)}_{self.token}") is not None:
                res = self.cache_services.get_caches(
                    f"{url.format(type,user_id)}_{self.token}")
            else:
                res = (asyncio.run(self._aiohttp_requests(
                    url.format(type, user_id), headers, body)))
                self.cache_services.set_caches(
                    f"{url.format(type,user_id)}_{self.token}", res)
            return res
        except Exception as err:
            message = {"status": "400", "detail": str(err).split("\n")}
            return message

    def update_bulk_menu(self, module, tenant_id, role_id, menu_name):
        try:
            url, headers, body = self._identify_root_module(module)
            body['tenant_id'] = tenant_id
            body['role_id'] = role_id
            body['menu_name'] = menu_name
            if menu_name is not None:
                res = (asyncio.run(self._aiohttp_patch(url, headers, body)))
            return {"status": 200, "data": res}
        except Exception as err:
            message = {"status": "400", "detail": str(err).split("\n")}
            return message

    def get_users_auth_tenant(self, module, tenant_id):
        try:
            url, headers, body = self._identify_root_module(module)
            if self.cache_services.get_caches(f"{url.format(tenant_id)}_{self.token}") is not None:
                res = self.cache_services.get_caches(
                    f"{url.format(tenant_id)}_{self.token}")
            else:
                res = (asyncio.run(self._aiohttp_requests(
                    url.format(tenant_id), headers, body)))
                self.cache_services.set_caches(
                    f"{url.format(tenant_id)}_{self.token}", res)
            return res
        except Exception as err:
            message = {"status": "400", "detail": str(err).split("\n")}

    def get_group_list(self, base_url, module_target, module, id):
        try:
            url, headers, body = self._identify_root_module(module)
            body['module'] = module_target
            if self.cache_services.get_caches(f"{url.format(base_url, id)}_{self.token}") is not None:
                res = self.cache_services.get_caches(
                    f"{url.format(base_url, id)}_{self.token}")
            else:
                res = (asyncio.run(self._aiohttp_requests(
                    url.format(base_url, id), headers, body)))
                self.cache_services.set_caches(
                    f"{url.format(base_url, id)}_{self.token}", res)
            return res
        except Exception as err:
            message = {"status": "400", "detail": str(err).split("\n")}
            return message

    def get_refference_data(self, base_url, module, id):
        try:
            url, headers, body = self._identify_root_module(module)
            key = f"{url.format(base_url, id)}_{module}_{self.token}"
            if self.cache_services.get_caches(key) is not None:
                res = self.cache_services.get_caches(key)
            else:
                res = (asyncio.run(self._aiohttp_requests(url.format(base_url, id), headers, body)))
                self.cache_services.set_caches(key, res)
            return res
        except Exception as err:
            message = {"status": "400", "detail": str(err).split("\n")}
            return message
