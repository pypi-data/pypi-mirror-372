import os
import copy
import json
import asyncio
import aiohttp
import logging
from core_engine.constants import ModuleName
from datetime import datetime, timedelta
from core_engine.bridges.integration import Integration
from core_engine.auth.services import AuthorizationService
authorization_service = AuthorizationService()

class NewObject:
    def __init__(self, tenant=None, access=None, module=None, returnings="id"):
        self.data = dict(tenant=tenant, access=access, module=module, query_params=dict(returnings=returnings))
        self.query_params = dict(returnings=returnings)

class ExternalIntegrationServices(object):
    def __init__(self, access, module, token):
        self.access = access
        self.token = token
        self.module = module
		
    def get_data(self, request, token, module, access, tenant=None):
        from core_engine.connection import ConnectionService
        authorization_service = AuthorizationService()
		
		# Get Access
        data_connection = authorization_service.get_access(token, module, access, tenant)

		# Get Parameter
        fields = request.get('fields', None)
		
        if data_connection.get("status") == 200:
            connection_service = ConnectionService(db_name=data_connection.get("detail").get('name'), db_host = data_connection.get("detail").get('host'), db_user = data_connection.get("detail").get('user'), db_password = data_connection.get("detail").get('password'), created_by = data_connection.get("detail").get('created_by'), token=token, module=module, access=access)
            values, integration_data = connection_service.get_datas(data_connection.get("detail").get('schema'), data_connection.get("detail").get('table_name'), data_connection.get("detail").get('tables'), request, None, fields)
            return values, integration_data
        return data_connection, None
		
    def create_data_integration(self, data, internal_first_action):
        request_integration_mapping = dict(internal_first_action=internal_first_action, internal_action_method="POST", order="id", is_active="true", is_delete="false", module_flag=self.module)
        integration_mappings, integration_data = self.get_data(request_integration_mapping, self.token, ModuleName.EBESHA_SETTING_GENERAL_INTEGRATION_MAPPING, "read", None)

        if integration_mappings.get('status') == 200:
            json_data = {}
            response_data = {}
            if integration_mappings.get('count') > 0:
                integration_datas = []
                integration = Integration(self.token, self.module, "read")
                module_access = authorization_service.get_access(self.token, self.module, self.access)
                if module_access.get('status') == 200:
                    for table in module_access.get('detail').get('tables'):
                        for field in table.get('fields'):
                            if field.get('integration') is not None:
                                integration_datas.append({"name":field.get('name'), "integration":field.get('integration')})
        
                copy_data = copy.copy(data)
                data_update = integration.check_integration({"data":[copy_data]}, integration_datas, self.module, None, data.get('tenant'))
                copy_data = data_update.get('data')[0]
                #for idx, value in enumerate(copy_data):
                #    if str(type(copy_data.get(value))) == "<class 'dict'>":
                #        if copy_data.get(value).get('name'):
                #            copy_data.update({value : copy_data.get(value).get('name')})

                for idx, value in enumerate(copy_data):
                    if value == "assigns":
                        characters_to_remove = "{} "
                        translation_table = str.maketrans("", "", characters_to_remove)
                        modified_string = copy_data.get(value).translate(translation_table)
                
                        users = integration.get_user_list("auth_user_list", modified_string)
                        try:
                            if users.get('status') == "400":
                                copy_data = copy_data
                        except:
                            copy_data.update({"assigns":users})

                for integration_mapping in integration_mappings.get('data'):
                    # Start check condition statement request data #
                    match_condition_statement = 0
                    for idx, key in enumerate(integration_mapping.get('condition_statement')):
                        if data.get(key) == integration_mapping.get('condition_statement').get(key):
                            match_condition_statement = match_condition_statement + 1
							
                    if match_condition_statement != len(integration_mapping.get('condition_statement')):
                        continue
                    # Start check condition statement request data #
						
                    # Start Get Integration Auth #
                    request_integration_auth = dict(order="id",sort="ASC",integration=str(integration_mapping.get('integrations').get('id')), is_active="true", is_delete="false", module_flag=ModuleName.EBESHA_SETTING_GENERAL_INTEGRATION_AUTHENTICATION)
                    integration_auths, integration_data = self.get_data(request_integration_auth, self.token, ModuleName.EBESHA_SETTING_GENERAL_INTEGRATION_AUTHENTICATION, "read", None)
					# Start Get Integration Auth #

					# Start Mapping Data Request #
                    if (integration_mapping.get('mapping_request_fields')):
                        for mapping_request_field in integration_mapping.get('mapping_request_fields'):
                            if len(mapping_request_field.get('internal_field')) == 1:
                                if len(mapping_request_field.get('integration_field')) == 1:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : copy_data[mapping_request_field.get('internal_field')[0]]})
                                elif len(mapping_request_field.get('integration_field')) == 2:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : {str(mapping_request_field.get('integration_field')[1]) : copy_data[mapping_request_field.get('internal_field')[0]]}})
                            elif len(mapping_request_field.get('internal_field')) == 2:
                                if len(mapping_request_field.get('integration_field')) == 1:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]]})
                                elif len(mapping_request_field.get('integration_field')) == 2:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : {str(mapping_request_field.get('integration_field')[1]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]]}})
                            elif len(mapping_request_field.get('internal_field')) == 3:
                                if len(mapping_request_field.get('integration_field')) == 1:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]]})
                                elif len(mapping_request_field.get('integration_field')) == 2:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : {str(mapping_request_field.get('integration_field')[1]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]]}})
                            elif len(mapping_request_field.get('internal_field')) == 4:
                                if len(mapping_request_field.get('integration_field')) == 1:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]]})
                                elif len(mapping_request_field.get('integration_field')) == 2:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : {str(mapping_request_field.get('integration_field')[1]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]]}})
                            elif len(mapping_request_field.get('internal_field')) == 5:
                                if len(mapping_request_field.get('integration_field')) == 1:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]][mapping_request_field.get('internal_field')[4]]})
                                if len(mapping_request_field.get('integration_field')) == 2:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : {str(mapping_request_field.get('integration_field')[1]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]][mapping_request_field.get('internal_field')[4]]}})
					# End Mapping Data Request  #
					
					# Start set variable request to integration apps #
                    request_data = json.loads(integration_mapping.get('integrations').get('body'))
                    header_data = integration_mapping.get('integrations').get('header')
                    url_data = integration_mapping.get('integrations').get('url')
                    method_data = integration_mapping.get('integrations').get('method')
                    # End set variable request to integration apps #
								
					# Start set auth integration apps #
                    if integration_auths.get('status') == 200:
                        if integration_auths.get('count') > 0:
                            for integration_auth in integration_auths.get('data'):
		        	    		# Start set variable request to integration auth apps #
                                request_auth_data = json.loads(integration_auth.get('body'))
                                header_auth_data = json.loads(integration_auth.get('header'))
                                url_auth_data = integration_auth.get('url')
                                method_auth_data = integration_auth.get('method')
                                auth_type = integration_auth.get('auth_type')
		        			    # End set variable request to integration auth apps #
											
		        			    # Start check auth type #
                                if auth_type == "Basic Auth":
									# Start action api to integration authorization apps #
                                    response_auth = asyncio.run(self._aiohttp_requests(method_auth_data, url_auth_data, header_auth_data, request_auth_data))
									# End action api to integration authorization apps #
									
                                    if response_auth.get('status_request_code') == 200 or response_auth.get('status_request_code') == 201:
                                        try:
                                            auth_mapping = json.loads(integration_auth.get('json'))
                                            if len(auth_mapping) == 1:
                                                parameter = "{"+str(auth_mapping[0])+"}"
                                                header_data = header_data.replace(parameter, response_auth[auth_mapping[0]])
                                                url_data = url_data.replace(parameter, response_auth[auth_mapping[0]])
                                            elif len(auth_mapping) == 2:
                                                parameter = "{"+str(auth_mapping[1])+"}"
                                                header_data = header_data.replace(parameter, response_auth[auth_mapping[0]][auth_mapping[1]])
                                                url_data = url_data.replace(parameter, response_auth[auth_mapping[0]][auth_mapping[1]])
                                            elif len(auth_mapping) == 3:
                                                parameter = "{"+str(auth_mapping[2])+"}"
                                                header_data = header_data.replace(parameter, response_auth[auth_mapping[0]][auth_mapping[1]][auth_mapping[2]])
                                                url_data = url_data.replace(parameter, response_auth[auth_mapping[0]][auth_mapping[1]][auth_mapping[2]])
                                        except:
                                            auth_mapping = None
                                    else:
                                        logging.error(response_auth)
		        			    # End check auth type #
					# End set auth integration apps #
											
					# Start set variable request to integration apps #
                    header_data = json.loads(header_data)
                    # End set variable request to integration apps #
					
					# Start modified request data to integration apps #
                    for json_modified in (json_data):
                        request_data.update({json_modified:json_data.get(json_modified)})
					# End modified request data to integration apps #
                    
					# Start action api to integration apps #
                    response = asyncio.run(self._aiohttp_requests(method_data, url_data, header_data, request_data))
                    #response = {"status_request_code": 200,"caseId": 27288,"caseTicketNo": "KEPOO006","old_case_ticket_no": None,"parentId": None,"caseSubject": "Test","description": "Test","solution": "","caseLatLong": "","caseAddress": "","casePriority": "Low","createdDate": "2023-11-24T18:05:11.518243","lastModifiedDate": "2023-11-24T18:05:11.527191","tenantId": {"tenantId": 46,"tenantName": "PT Kepoo Solusi Indonesia"},"accountId": None,"contactId": {"contactId": 58644,"contactName": "puji@gmail.com"},"originId": {"originId": 56,"originName": "Telephone"},"assignId": None,"statusId": {"statusId": 32,"statusName": "Open"},"categoryId": {"categoryId": 28,"categoryName": "Complaint"},"caseCategoryId": {"caseCategoryId": 1510,"caseCategoryName": "Gagal Transaksi/Pembelian/Pembayaran"},"createdBy": {"id": 1,"first_name": "Super","last_name": "User","username": "superuser","email": "support@lmd.co.id"},"lastModifiedBy": None,"notes": "","serviceDeskId": None,"isDelete": False,"isActive": True,"fcr": False,"is_public": False,"children": [],"statusClose": False,"remaining_sla": {"resolve_time": None,"due_by_time": "2023-11-30 00:11:00","use_holiday": None,"sla_times": None,"remaining_day": None},"caseCategoryTree": [{"id": 1510,"name": "Gagal Transaksi/Pembelian/Pembayaran","parent": 1390},{"id": 1390,"name": "ATM/Kartu Debit","parent": 1366},{"id": 1366,"name": "Sistem Pembayaran","parent": 1362},{"id": 1362,"name": "Pengaduan Nasabah","parent": None}],"to_close": False,"additional_field": []}
 					# Start action api to integration apps #
					
					# Start Mapping Data Response #
                    if response.get('status_request_code') == 200 or response.get('status_request_code') == 201:
                        if (integration_mapping.get('mapping_response_fields')):
                            for mapping_response_field in integration_mapping.get('mapping_response_fields'):
                                if len(mapping_response_field.get('internal_field')) == 1:
                                    if len(mapping_response_field.get('integration_field')) == 1:
                                        #response_data.update({str(mapping_response_field.get('internal_field')[0]) : response[mapping_response_field.get('integration_field')[0]]})
                                        data.update({str(mapping_response_field.get('internal_field')[0]) : response[mapping_response_field.get('integration_field')[0]]})
                                    elif len(mapping_response_field.get('integration_field')) == 2:
                                        #response_data.update({str(mapping_response_field.get('internal_field')[0]) : response[mapping_response_field.get('integration_field')[0]][mapping_response_field.get('integration_field')[1]]})
                                        data.update({str(mapping_response_field.get('internal_field')[0]) : response[mapping_response_field.get('integration_field')[0]][mapping_response_field.get('integration_field')[1]]})
                    else:
                        logging.error(response)
					# End Mapping Data Response #
        return data
					
    def update_data_integration(self, data, internal_first_action):
        request_integration_mapping = dict(internal_first_action=internal_first_action, internal_action_method="PATCH", order="id", is_active="true", is_delete="false", module_flag=self.module)
        integration_mappings, integration_data = self.get_data(request_integration_mapping, self.token, ModuleName.EBESHA_SETTING_GENERAL_INTEGRATION_MAPPING, "read", None)
        if integration_mappings.get('status') == 200:
            json_data = {}
            response_data = {}
            if integration_mappings.get('count') > 0:
                integration_datas = []
                integration = Integration(self.token, self.module, "read")
                module_access = authorization_service.get_access(self.token, self.module, self.access)
                if module_access.get('status') == 200:
                    for table in module_access.get('detail').get('tables'):
                        for field in table.get('fields'):
                            if field.get('integration') is not None:
                                integration_datas.append({"name":field.get('name'), "integration":field.get('integration')})
        
                copy_data = copy.copy(data)
                data_update = integration.check_integration({"data":[copy_data]}, integration_datas, self.module, None, data.get('tenant'))
                copy_data = data_update.get('data')[0]

                for idx, value in enumerate(copy_data):
                    if value == "assigns":
                        characters_to_remove = "{} "
                        translation_table = str.maketrans("", "", characters_to_remove)
                        modified_string = copy_data.get(value).translate(translation_table)
                
                        users = integration.get_user_list("auth_user_list", modified_string)
                        try:
                            if users.get('status') == "400":
                                copy_data = copy_data
                        except:
                            copy_data.update({"assigns":users})

                for integration_mapping in integration_mappings.get('data'):
                    # Start set refference id #
                    mapping_integration_id = None
                    # End set refference id #
					
                    # Start check condition statement request data #
                    match_condition_statement = 0
                    for idx, key in enumerate(integration_mapping.get('condition_statement')):
                        if data.get(key) == integration_mapping.get('condition_statement').get(key):
                            match_condition_statement = match_condition_statement + 1
							
                    if match_condition_statement != len(integration_mapping.get('condition_statement')):
                        continue
                    # Start check condition statement request data #
					
					# Start Get Integration Auth #
                    request_integration_auth = dict(order="id",sort="ASC",integration=str(integration_mapping.get('integrations').get('id')), is_active="true", is_delete="false", module_flag=ModuleName.EBESHA_SETTING_GENERAL_INTEGRATION_AUTHENTICATION)
                    integration_auths, integration_data = self.get_data(request_integration_auth, self.token, ModuleName.EBESHA_SETTING_GENERAL_INTEGRATION_AUTHENTICATION, "read", None)
					# Start Get Integration Auth #

					# Start Mapping Data Request #
                    if (integration_mapping.get('mapping_request_fields')):
                        for mapping_request_field in integration_mapping.get('mapping_request_fields'):
                            if len(mapping_request_field.get('internal_field')) == 1:
                                mapping_integration_id = self.check_data_refference(mapping_request_field.get('internal_field')[0], copy_data[mapping_request_field.get('internal_field')[0]])
                                if len(mapping_request_field.get('integration_field')) == 1:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : copy_data[mapping_request_field.get('internal_field')[0]]})
                                elif len(mapping_request_field.get('integration_field')) == 2:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : {str(mapping_request_field.get('integration_field')[1]) : copy_data[mapping_request_field.get('internal_field')[0]]}})
                            elif len(mapping_request_field.get('internal_field')) == 2:
                                mapping_integration_id = self.check_data_refference(mapping_request_field.get('internal_field')[1], copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]])
                                if len(mapping_request_field.get('integration_field')) == 1:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]]})
                                elif len(mapping_request_field.get('integration_field')) == 2:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : {str(mapping_request_field.get('integration_field')[1]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]]}})
                            elif len(mapping_request_field.get('internal_field')) == 3:
                                mapping_integration_id = self.check_data_refference(mapping_request_field.get('internal_field')[2], copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]])
                                if len(mapping_request_field.get('integration_field')) == 1:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]]})
                                elif len(mapping_request_field.get('integration_field')) == 2:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : {str(mapping_request_field.get('integration_field')[1]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]]}})
                            elif len(mapping_request_field.get('internal_field')) == 4:
                                mapping_integration_id = self.check_data_refference(mapping_request_field.get('internal_field')[3], copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]])
                                if len(mapping_request_field.get('integration_field')) == 1:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]]})
                                elif len(mapping_request_field.get('integration_field')) == 2:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : {str(mapping_request_field.get('integration_field')[1]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]]}})
                            elif len(mapping_request_field.get('internal_field')) == 5:
                                mapping_integration_id = self.check_data_refference(mapping_request_field.get('internal_field')[4], copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]][mapping_request_field.get('internal_field')[4]])
                                if len(mapping_request_field.get('integration_field')) == 1:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]][mapping_request_field.get('internal_field')[4]]})
                                if len(mapping_request_field.get('integration_field')) == 2:
                                    json_data.update({str(mapping_request_field.get('integration_field')[0]) : {str(mapping_request_field.get('integration_field')[1]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]][mapping_request_field.get('internal_field')[4]]}})
					# End Mapping Data Request  #
                    
					# Start set variable request to integration apps #
                    request_data = json.loads(integration_mapping.get('integrations').get('body'))
                    header_data = integration_mapping.get('integrations').get('header')
                    url_data = integration_mapping.get('integrations').get('url')
                    method_data = integration_mapping.get('integrations').get('method')
                    # End set variable request to integration apps #
								
					# Start set auth integration apps #
                    if integration_auths.get('status') == 200:
                        if integration_auths.get('count') > 0:
                            for integration_auth in integration_auths.get('data'):
		        	    		# Start set variable request to integration auth apps #
                                request_auth_data = json.loads(integration_auth.get('body'))
                                header_auth_data = json.loads(integration_auth.get('header'))
                                url_auth_data = integration_auth.get('url')
                                method_auth_data = integration_auth.get('method')
                                auth_type = integration_auth.get('auth_type')
		        			    # End set variable request to integration auth apps #
											
		        			    # Start check auth type #
                                if auth_type == "Basic Auth":
                                    response_auth = asyncio.run(self._aiohttp_requests(method_auth_data, url_auth_data, header_auth_data, request_auth_data))
                                    if response_auth.get('status_request_code') == 200 or response_auth.get('status_request_code') == 201:
                                        try:
                                            auth_mapping = json.loads(integration_auth.get('json'))
                                            if len(auth_mapping) == 1:
                                                parameter = "{"+str(auth_mapping[0])+"}"
                                                header_data = header_data.replace(parameter, response_auth[auth_mapping[0]])
                                                url_data = url_data.replace(parameter, response_auth[auth_mapping[0]])
                                            elif len(auth_mapping) == 2:
                                                parameter = "{"+str(auth_mapping[1])+"}"
                                                header_data = header_data.replace(parameter, response_auth[auth_mapping[0]][auth_mapping[1]])
                                                url_data = url_data.replace(parameter, response_auth[auth_mapping[0]][auth_mapping[1]])
                                            elif len(auth_mapping) == 3:
                                                parameter = "{"+str(auth_mapping[2])+"}"
                                                header_data = header_data.replace(parameter, response_auth[auth_mapping[0]][auth_mapping[1]][auth_mapping[2]])
                                                url_data = url_data.replace(parameter, response_auth[auth_mapping[0]][auth_mapping[1]][auth_mapping[2]])
                                        except:
                                            auth_mapping = None
                                    else:
                                        logging.error(response_auth)
		        			    # End check auth type #
					# End set auth integration apps #
											
					# Start set variable request to integration apps #
                    header_data = json.loads(header_data)
                    # End set variable request to integration apps #
					
					# Start modified request data to integration apps #
                    for json_modified in (json_data):
                        request_data.update({json_modified:json_data.get(json_modified)})
					# End modified request data to integration apps #
                    
					# Start update target id integration #
                    url_data = url_data.replace("{id}", mapping_integration_id)
					# End update target id integration #
					
					# Start check mapping integration id #
                    if mapping_integration_id is None:
                        continue
					# End check mapping integration id #
                    
					# Start action api to integration apps #
                    response = asyncio.run(self._aiohttp_requests(method_data, url_data, header_data, request_data))
                    #response = {"status_request_code": 200,"caseId": 27288,"caseTicketNo": "KEPOO006","old_case_ticket_no": None,"parentId": None,"caseSubject": "Test","description": "Test","solution": "","caseLatLong": "","caseAddress": "","casePriority": "Low","createdDate": "2023-11-24T18:05:11.518243","lastModifiedDate": "2023-11-24T18:05:11.527191","tenantId": {"tenantId": 46,"tenantName": "PT Kepoo Solusi Indonesia"},"accountId": None,"contactId": {"contactId": 58644,"contactName": "puji@gmail.com"},"originId": {"originId": 56,"originName": "Telephone"},"assignId": None,"statusId": {"statusId": 32,"statusName": "Open"},"categoryId": {"categoryId": 28,"categoryName": "Complaint"},"caseCategoryId": {"caseCategoryId": 1510,"caseCategoryName": "Gagal Transaksi/Pembelian/Pembayaran"},"createdBy": {"id": 1,"first_name": "Super","last_name": "User","username": "superuser","email": "support@lmd.co.id"},"lastModifiedBy": None,"notes": "","serviceDeskId": None,"isDelete": False,"isActive": True,"fcr": False,"is_public": False,"children": [],"statusClose": False,"remaining_sla": {"resolve_time": None,"due_by_time": "2023-11-30 00:11:00","use_holiday": None,"sla_times": None,"remaining_day": None},"caseCategoryTree": [{"id": 1510,"name": "Gagal Transaksi/Pembelian/Pembayaran","parent": 1390},{"id": 1390,"name": "ATM/Kartu Debit","parent": 1366},{"id": 1366,"name": "Sistem Pembayaran","parent": 1362},{"id": 1362,"name": "Pengaduan Nasabah","parent": None}],"to_close": False,"additional_field": []}
 					# Start action api to integration apps #
					
					# Start Mapping Data Response Set To Internal Data #
                    if response.get('status_request_code') == 200 or response.get('status_request_code') == 201:
                        if (integration_mapping.get('mapping_response_fields')):
                            for mapping_response_field in integration_mapping.get('mapping_response_fields'):
                                if len(mapping_response_field.get('internal_field')) == 1:
                                    if len(mapping_response_field.get('integration_field')) == 1:
                                        data.update({str(mapping_response_field.get('internal_field')[0]) : response[mapping_response_field.get('integration_field')[0]]})
                                    elif len(mapping_response_field.get('integration_field')) == 2:
                                        data.update({str(mapping_response_field.get('internal_field')[0]) : response[mapping_response_field.get('integration_field')[0]][mapping_response_field.get('integration_field')[1]]})
                    else:
                        logging.error(response)
					# End Mapping Data Response Set To Internal Data #
        return data

    def get_data_integration(self, internal_first_action, tenant=None):
        datas = {"status":200, "data":[]}
        start = datetime.now()
        request_integration_mapping = dict(internal_first_action=internal_first_action, internal_action_method="PATCH", integration_action_method="GET", order="id", is_active="true", is_delete="false", module_flag=self.module)
        integration_mappings, integration_data = self.get_data(request_integration_mapping, self.token, ModuleName.EBESHA_SETTING_GENERAL_INTEGRATION_MAPPING, "read", tenant)
        if integration_mappings.get('status') == 200:
            json_data = {}
            response_data = {}
            if integration_mappings.get('count') > 0:
                for integration_mapping in integration_mappings.get('data'):
					# Start get data internal module #
                    request_integration_mapping = integration_mapping.get("data_parameter")
                    response_data, integration_datas = self.get_data(request_integration_mapping, self.token, self.module, "read", tenant)
                    if response_data.get('status') == 200:
                        datas = response_data
                    else:
                        return response_data
					# End get data internal module #
					
					# Start Get Integration Auth #
                    request_integration_auth = dict(order="id",sort="ASC",integration=str(integration_mapping.get('integrations').get('id')), is_active="true", is_delete="false", module_flag=ModuleName.EBESHA_SETTING_GENERAL_INTEGRATION_AUTHENTICATION)
                    integration_auths, integration_data = self.get_data(request_integration_auth, self.token, ModuleName.EBESHA_SETTING_GENERAL_INTEGRATION_AUTHENTICATION, "read", tenant)
					# Start Get Integration Auth #
					
                    for data in datas.get('data'):
                        copy_data = copy.copy(data)
                        # Start set refference id #
                        condition_statement_field = []
                        mapping_integration_id = data.get('mapping_integration_id')
                        # End set refference id #
					
                        # Start check condition statement request data #
                        match_condition_statement = 0
                        for idx, key in enumerate(integration_mapping.get('condition_statement')):
                            if data.get(key) == integration_mapping.get('condition_statement').get(key):
                                match_condition_statement = match_condition_statement + 1
                                condition_statement_field.append(key)
							
                        if match_condition_statement != len(integration_mapping.get('condition_statement')):
                            continue
                        # Start check condition statement request data #
					
			    		# Start Mapping Data Request #
                        if (integration_mapping.get('mapping_request_fields')):
                            for mapping_request_field in integration_mapping.get('mapping_request_fields'):
                                if len(mapping_request_field.get('internal_field')) == 1:
                                    mapping_integration_id = self.check_data_refference(mapping_request_field.get('internal_field')[0], copy_data[mapping_request_field.get('internal_field')[0]])
                                    if len(mapping_request_field.get('integration_field')) == 1:
                                        json_data.update({str(mapping_request_field.get('integration_field')[0]) : copy_data[mapping_request_field.get('internal_field')[0]]})
                                    elif len(mapping_request_field.get('integration_field')) == 2:
                                        json_data.update({str(mapping_request_field.get('integration_field')[0]) : {str(mapping_request_field.get('integration_field')[1]) : copy_data[mapping_request_field.get('internal_field')[0]]}})
                                elif len(mapping_request_field.get('internal_field')) == 2:
                                    mapping_integration_id = self.check_data_refference(mapping_request_field.get('internal_field')[1], copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]])
                                    if len(mapping_request_field.get('integration_field')) == 1:
                                        json_data.update({str(mapping_request_field.get('integration_field')[0]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]]})
                                    elif len(mapping_request_field.get('integration_field')) == 2:
                                        json_data.update({str(mapping_request_field.get('integration_field')[0]) : {str(mapping_request_field.get('integration_field')[1]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]]}})
                                elif len(mapping_request_field.get('internal_field')) == 3:
                                    mapping_integration_id = self.check_data_refference(mapping_request_field.get('internal_field')[2], copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]])
                                    if len(mapping_request_field.get('integration_field')) == 1:
                                        json_data.update({str(mapping_request_field.get('integration_field')[0]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]]})
                                    elif len(mapping_request_field.get('integration_field')) == 2:
                                        json_data.update({str(mapping_request_field.get('integration_field')[0]) : {str(mapping_request_field.get('integration_field')[1]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]]}})
                                elif len(mapping_request_field.get('internal_field')) == 4:
                                    mapping_integration_id = self.check_data_refference(mapping_request_field.get('internal_field')[3], copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]])
                                    if len(mapping_request_field.get('integration_field')) == 1:
                                        json_data.update({str(mapping_request_field.get('integration_field')[0]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]]})
                                    elif len(mapping_request_field.get('integration_field')) == 2:
                                        json_data.update({str(mapping_request_field.get('integration_field')[0]) : {str(mapping_request_field.get('integration_field')[1]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]]}})
                                elif len(mapping_request_field.get('internal_field')) == 5:
                                    mapping_integration_id = self.check_data_refference(mapping_request_field.get('internal_field')[4], copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]][mapping_request_field.get('internal_field')[4]])
                                    if len(mapping_request_field.get('integration_field')) == 1:
                                        json_data.update({str(mapping_request_field.get('integration_field')[0]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]][mapping_request_field.get('internal_field')[4]]})
                                    if len(mapping_request_field.get('integration_field')) == 2:
                                        json_data.update({str(mapping_request_field.get('integration_field')[0]) : {str(mapping_request_field.get('integration_field')[1]) : copy_data[mapping_request_field.get('internal_field')[0]][mapping_request_field.get('internal_field')[1]][mapping_request_field.get('internal_field')[2]][mapping_request_field.get('internal_field')[3]][mapping_request_field.get('internal_field')[4]]}})
		    			# End Mapping Data Request  #
					
			    		# Start set variable request to integration apps #
                        request_data = json.loads(integration_mapping.get('integrations').get('body'))
                        header_data = integration_mapping.get('integrations').get('header')
                        url_data = integration_mapping.get('integrations').get('url')
                        method_data = integration_mapping.get('integrations').get('method')
                        # End set variable request to integration apps #
                    
		    			# Start set auth integration apps #
                        if integration_auths.get('status') == 200:
                            if integration_auths.get('count') > 0:
                                for integration_auth in integration_auths.get('data'):
		        	        		# Start set variable request to integration auth apps #
                                    request_auth_data = json.loads(integration_auth.get('body'))
                                    header_auth_data = json.loads(integration_auth.get('header'))
                                    url_auth_data = integration_auth.get('url')
                                    method_auth_data = integration_auth.get('method')
                                    auth_type = integration_auth.get('auth_type')
		            			    # End set variable request to integration auth apps #
											
		        	    		    # Start check auth type #
                                    if auth_type == "Basic Auth":
                                        response_auth = asyncio.run(self._aiohttp_requests(method_auth_data, url_auth_data, header_auth_data, request_auth_data))
                                        if response_auth.get('status_request_code') == 200 or response_auth.get('status_request_code') == 201:
                                            try:
                                                auth_mapping = json.loads(integration_auth.get('json'))
                                                if len(auth_mapping) == 1:
                                                    parameter = "{"+str(auth_mapping[0])+"}"
                                                    header_data = header_data.replace(parameter, response_auth[auth_mapping[0]])
                                                    url_data = url_data.replace(parameter, response_auth[auth_mapping[0]])
                                                elif len(auth_mapping) == 2:
                                                    parameter = "{"+str(auth_mapping[1])+"}"
                                                    header_data = header_data.replace(parameter, response_auth[auth_mapping[0]][auth_mapping[1]])
                                                    url_data = url_data.replace(parameter, response_auth[auth_mapping[0]][auth_mapping[1]])
                                                elif len(auth_mapping) == 3:
                                                    parameter = "{"+str(auth_mapping[2])+"}"
                                                    header_data = header_data.replace(parameter, response_auth[auth_mapping[0]][auth_mapping[1]][auth_mapping[2]])
                                                    url_data = url_data.replace(parameter, response_auth[auth_mapping[0]][auth_mapping[1]][auth_mapping[2]])
                                            except:
                                                auth_mapping = None
                                        else:
                                            logging.error(f"{start} : Can't connect or auth failed to {url_auth_data} : {start}")
		            			    # End check auth type #
                        else:
                            return integration_auths
    					# End set auth integration apps #
											
	    				# Start set variable request to integration apps #
                        header_data = json.loads(header_data)
                        # End set variable request to integration apps #
                    
				    	# Start modified request data to integration apps #
                        for json_modified in (json_data):
                            request_data.update({json_modified:json_data.get(json_modified)})
    					# End modified request data to integration apps #
                    
	    				# Start update target id integration #
                        url_data = url_data.replace("{id}", mapping_integration_id)
			    		# End update target id integration #
					
				    	# Start check mapping integration id #
                        if mapping_integration_id is None:
                            continue
	    				# End check mapping integration id #
					
		    			# Start action api to integration apps #
                        response = asyncio.run(self._aiohttp_requests(method_data, url_data, header_data, request_data))
                        #response = {"status_request_code": 200,"caseId": 27288,"caseTicketNo": "KEPOO006","old_case_ticket_no": None,"parentId": None,"caseSubject": "Test","description": "Test","solution": "","caseLatLong": "","caseAddress": "","casePriority": "Low","createdDate": "2023-11-24T18:05:11.518243","lastModifiedDate": "2023-11-24T18:05:11.527191","tenantId": {"tenantId": 46,"tenantName": "PT Kepoo Solusi Indonesia"},"accountId": None,"contactId": {"contactId": 58644,"contactName": "puji@gmail.com"},"originId": {"originId": 56,"originName": "Telephone"},"assignId": None,"statusId": {"statusId": 32,"statusName": "Open"},"categoryId": {"categoryId": 28,"categoryName": "Complaint"},"caseCategoryId": {"caseCategoryId": 1510,"caseCategoryName": "Gagal Transaksi/Pembelian/Pembayaran"},"createdBy": {"id": 1,"first_name": "Super","last_name": "User","username": "superuser","email": "support@lmd.co.id"},"lastModifiedBy": None,"notes": "","serviceDeskId": None,"isDelete": False,"isActive": True,"fcr": False,"is_public": False,"children": [],"statusClose": False,"remaining_sla": {"resolve_time": None,"due_by_time": "2023-11-30 00:11:00","use_holiday": None,"sla_times": None,"remaining_day": None},"caseCategoryTree": [{"id": 1510,"name": "Gagal Transaksi/Pembelian/Pembayaran","parent": 1390},{"id": 1390,"name": "ATM/Kartu Debit","parent": 1366},{"id": 1366,"name": "Sistem Pembayaran","parent": 1362},{"id": 1362,"name": "Pengaduan Nasabah","parent": None}],"to_close": False,"additional_field": []}
 					    # Start action api to integration apps #
					
    					# Start Mapping Data Response Set To Internal Data #
                        if response.get('status_request_code') == 200 or response.get('status_request_code') == 201:
                            if (integration_mapping.get('mapping_response_fields')):
                                for mapping_response_field in integration_mapping.get('mapping_response_fields'):
                                    if len(mapping_response_field.get('internal_field')) == 1:
                                        if len(mapping_response_field.get('integration_field')) == 1:
                                            data.update({str(mapping_response_field.get('internal_field')[0]) : response[mapping_response_field.get('integration_field')[0]]})
                                        elif len(mapping_response_field.get('integration_field')) == 2:
                                            data.update({str(mapping_response_field.get('internal_field')[0]) : response[mapping_response_field.get('integration_field')[0]][mapping_response_field.get('integration_field')[1]]})
                        else:
                            logging.error(f"{start} : Can't connect or hit to {url_auth_data} : {start}")
			    		# End Mapping Data Response Set To Internal Data #

                        for integration_data in integration_datas:
                            if integration_data.get("name") in data and integration_data.get("name") not in condition_statement_field:
                                request_integration_data = dict(fields="id",name=data.get(integration_data.get("name")), module_flag=self.module)
                                integration_module, data_relation = self.get_data(request_integration_data, self.token, integration_data.get("integration"), "read", tenant)
                                if integration_module.get("status") == 200:
                                    if integration_module.get("count") > 0:
                                        data.update({integration_data.get("name") : str(integration_module.get("data")[0].get('id'))})
                                else:
                                    return integration_module
        return datas

    def check_data_refference(self, target_field, copy_data):
        if target_field == "mapping_integration_id":
            return copy_data
        return None

    async def _aiohttp_requests(self, method, url, headers, body):
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            try:
                session = aiohttp.ClientSession()
                method_map = {
                    'GET': session.get,
                    'POST': session.post,
                    'PUT': session.put,
                    'PATCH': session.patch,
                    'DELETE': session.delete
                }
			
                responses = await method_map[method](url, headers=headers, json=body, ssl=False)
                response = await responses.json()
                response.update({"status_request_code":responses.status})
                await session.close()
                break
            except Exception as err:
                if attempt < max_retries:
                    logging.error(f"Retrying to connect {url}")
                else:
                    logging.error(f"Max retries reached to {url}")
                response = {"status_request_code":"500", "detail":str(err).split("\n")}
        return response