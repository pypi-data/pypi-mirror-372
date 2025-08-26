# Author : Puji Anugrah Pangestu #
# Created : 01 Oct 2022 #

import json
import os
import psycopg2
import psycopg2.extras
import re
import logging
from datetime import datetime
from core_engine.connectivity.query_builder import QueryBuilder
from core_engine.connectivity.services import LogicServices
from core_engine.constants import Messages, ModuleName, GroupTypeData, CustomQuery
from core_engine.utilities.paginations import DinamicPagination
from core_engine.bridges.integration import Integration
from core_engine.utilities.utils import replace_last_character
from core_engine.caches.services import CacheServices
from core_engine.external_integration.services import ExternalIntegrationServices

class ConnectionService():
    def __init__(self, db_name=None, db_host = None, db_port=5432, db_user = None, db_password = None, created_by = None, token = None, module = None, access = None, role_type=None):
        self.access = access
        self.created_by = created_by
        self.db_name = db_name
        self.db_host = db_host
        self.db_port = db_port
        self.db_user = db_user
        self.db_password = db_password
        self.module = module
        self.token = token
        self.role_type = role_type
        self.cache_services = CacheServices()

    def get_columns(self, table_schema, table_name):
        connection = self._connection()
        where_dict = {"table_schema": table_schema, "table_name": table_name}
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute("""SELECT column_name, ordinal_position, is_nullable, data_type, character_maximum_length
                      FROM information_schema.columns
                      WHERE table_schema = %(table_schema)s
                      AND table_name = %(table_name)s
                      ORDER BY ordinal_position""",
                      where_dict)
        columns = cursor.fetchall()
        cursor.close()
        connection.close()
        return columns
		
    def custom_exception_query(self, table_name):
        custom_filter_query = ""
        if self.module == ModuleName.EBESHA_OMNICHANNEL_EMAIL_LIST:
            if self.role_type == "AGENT" or  self.role_type == "CUSTOMER":
                custom_filter_query = f" AND ('{self.created_by}'::int = ANY({table_name}.assign_to_specific_user::int[]) or  '{self.created_by}'::int = ANY({table_name}.assign_to_group_account::int[]) or '{self.created_by}'::int = ANY({table_name}.assign_to_group_department::int[]) or  '{self.created_by}'::int = ANY({table_name}.assign_to_group_routing::int[]))"
        return custom_filter_query
		
    def get_custom_datas(self, table_schema, table_name, table_views, request, url, fields, tenant=None, timezone='Etc/GMT-7'):
        dinamic_pagination = DinamicPagination()
        integration = Integration(self.token, self.module, self.access)
        connection = self._connection()
        try:
            integration_datas = []
            childrens = []
            select_field = ""
            where_integration = ""
            self_join_table = ""
            
			# Get parameter request #
            #start = request.get('start', 0) if request.get('start') != "" else 0
            limit = request.get('limit', 10) if request.get('limit') != "" else 10
            page = request.get('page', 1) if request.get('page') != "" else 1
            order = request.get('order', 'id') if request.get('order') != "" else "id"
            sort = request.get('sort', 'ASC') if request.get('sort') != "" else "ASC"
            search = request.get('search', '')
			# Get parameter request #

            open_cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

			# Start check field #
            if fields is not None:
                for field in fields.split(","):
                    for tables in table_views:
                        for table_view in tables.get('fields'):
                            if(table_view.get('name')==field):
                                if table_view.get('integration') is not None:
                                    integration_datas.append({"name":table_view.get('name'),"integration":table_view.get('integration')})

                                    where_difference_modules = integration.find_search_integration(table_view.get('integration'), search)
                                    for where_difference_module in where_difference_modules:
                                        where_integration += f" OR {table_name}.\"{table_view.get('name')}\" = '{where_difference_module}' "

                                if table_view.get('self_fk'):
                                    childrens.append(table_view.get('name'))
                                    self_join_table += f" LEFT JOIN {table_schema}.\"{table_name}\" {table_name}_{table_view.get('name')} on {table_name}_{table_view.get('name')}.id = {table_name}.{table_view.get('name')} "

						    		# Check show field element self_fk #
                                    selected = []
                                    if table_view.get('self_attributes'):
                                        for self_attribute in table_view.get('self_attributes'):
                                            selected.append(f"""{table_name}_{table_view.get('name')}.\"{self_attribute}\"""")
                                    else:
                                        selected.append(f"{table_name}_{table_view.get('name')}.*")
                                    select_field += f"case when {table_name}_{table_view.get('name')}.id is not null then to_json((SELECT d FROM (SELECT {','.join(selected)}) d)) end as {table_view.get('name')},"
                                    # Check show field element self_fk #

									# Remark Puji 20230920 #
                                    #select_field += f"to_json({table_name}_{table_view.get('name')}.*) as {table_view.get('name')},"
									# Remark Puji 20230920 #
                                elif table_view.get('fk_to'):
                                    self_join_table += f" LEFT JOIN {table_schema}.\"{table_view.get('fk_to').get('table')}\" {table_name}_{table_view.get('name')} on {table_name}_{table_view.get('name')}.{table_view.get('fk_to').get('field')} = {table_name}.{table_view.get('name')} "
                                    select_field += f"to_json({table_name}_{table_view.get('name')}.*) as {table_view.get('name')},"
                                else:
                                    if "date" in table_view.get('name') or 'Timestamp' in table_view.get('type') or 'Interval' in table_view.get('type'):
                                        # Start set date with timezone tenant #
                                        if table_view.get('name') == "created_date" or table_view.get('name') == "last_modified_date":
                                            #select_field += f"{table_name}.\"{field}\"::character varying as {field},"
                                            #select_field += f"to_char(({table_name}.\"{field}\"::timestamp AT TIME ZONE '{timezone}'), 'yyyy-mm-dd HH24:MI:SS')::character varying as {field},"
                                            select_field += f"({table_name}.\"{field}\"::timestamp AT TIME ZONE '{timezone}')::timestamp as {field},"
                                        else:
                                            select_field += f"{table_name}.\"{field}\","
                                        # End set date with timezone tenant #
                                    else:
                                        select_field += f"{table_name}.\"{field}\","
                                    #select_field += f"{table_name}.\"{field}\","
            else:
                for tables in table_views:
                    for table_view in tables.get('fields'):
                        if table_view.get('view'):
                            if table_view.get('integration') is not None:
                                integration_datas.append({"name":table_view.get('name'),"integration":table_view.get('integration')})

                                where_difference_modules = integration.find_search_integration(table_view.get('integration'), search)
                                for where_difference_module in where_difference_modules:
                                    where_integration += f" OR {table_name}.\"{table_view.get('name')}\" = '{where_difference_module}' "

                            if table_view.get('self_fk'):
                                childrens.append(table_view.get('name'))
                                self_join_table += f" LEFT JOIN {table_schema}.\"{table_name}\" {table_name}_{table_view.get('name')} on {table_name}_{table_view.get('name')}.id = {table_name}.{table_view.get('name')} "

								# Check show field element self_fk #
                                selected = []
                                if table_view.get('self_attributes'):
                                    for self_attribute in table_view.get('self_attributes'):
                                        selected.append(f"""{table_name}_{table_view.get('name')}.\"{self_attribute}\"""")
                                else:
                                    selected.append(f"{table_name}_{table_view.get('name')}.*")
                                select_field += f"case when {table_name}_{table_view.get('name')}.id is not null then to_json((SELECT d FROM (SELECT {','.join(selected)}) d)) end as {table_view.get('name')},"
                                # Check show field element self_fk #

								# Remark Puji 20230920 #
                                #select_field += f"to_json({table_name}_{table_view.get('name')}.*) as {table_view.get('name')},"
								# Remark Puji 20230920 #
                            elif table_view.get('fk_to'):
                                self_join_table += f" LEFT JOIN {table_schema}.\"{table_view.get('fk_to').get('table')}\" {table_name}_{table_view.get('name')} on {table_name}_{table_view.get('name')}.{table_view.get('fk_to').get('field')} = {table_name}.{table_view.get('name')} "
                                select_field += f"to_json({table_name}_{table_view.get('name')}.*) as {table_view.get('name')},"
                            else:
                                if "date" in table_view.get('name') or 'Timestamp' in table_view.get('type') or 'Interval' in table_view.get('type'):
                                    # Start set date with timezone tenant #
                                    if table_view.get('name') == "created_date" or table_view.get('name') == "last_modified_date":
                                        #select_field += f"{table_name}.\"{table_view.get('name')}\"::character varying as {table_view.get('name')},"
                                        select_field += f"({table_name}.\"{table_view.get('name')}\"::timestamp AT TIME ZONE '{timezone}')::timestamp as {table_view.get('name')},"
                                    else:
                                        select_field += f"{table_name}.\"{table_view.get('name')}\","
                                    # Start set date with timezone tenant #
                                else:
                                    select_field += f"{table_name}.\"{table_view.get('name')}\","
            select_field = replace_last_character(select_field, ",", "")
            # End check field #

			# Start check query custom #    
            file1 = open(f"{os.environ.get('QUERY_DIRECTORY')}/{CustomQuery.ModuleName[self.module]}", "r+") 
            basic_query = file1.read()
            basic_query = basic_query.replace("{params}", search).replace("{schema}", table_schema).replace("{table_name}", table_name)
			# End check query custom #
			
			# Start get where condition #
            where_dict = ""
            where_like = ""
			# End get where condition #

			# Start check order by & limitation data #
            order_by = f"ORDER BY {order} {sort}"
            limit_by = f"OFFSET {int(limit)*(int(page)-1)} LIMIT {limit}"
			# End check order by & limitation data #

			# Start check custom exception #
            additional_query = self.custom_exception_query(table_name)
			# End check custom exception #
            
			# Start generate query list #
            qry_data = f""" {basic_query}
                WHERE 1=1 {additional_query}
                {order_by} {limit_by}"""
			# End generate query list #

			# Start generate query counting #
            qry_count = f"""SELECT count(*) FROM(
                {basic_query}
                WHERE 1=1 {additional_query}
                ) {table_name}"""
			# End generate query counting #

			# Start execute query list #
            open_cursor.execute(qry_data)
            datas = open_cursor.fetchall()
			# End execute query list #

			# Start execute query counting #
            open_cursor.execute(qry_count)
            count = open_cursor.fetchall()
			# End execute query counting #

			# Start generate pagination url #
            previous = dinamic_pagination.generate_previous_page(url, request, count[0].get('count'))
            next = dinamic_pagination.generate_next_page(url, request, count[0].get('count'))
			# End generate pagination url #

			# Start generate response #
            responses = {"status":200, "page" : page, "count" : count[0].get("count") , "previous" : previous, "next" : next, "data" : datas}
			# End generate response #

			# Start close connection #
            open_cursor.close()
            connection.close()
			# End close connection #
            return responses, integration_datas
        except Exception as err:
            connection.rollback()
            connection.close()
            message = {"status":400, "detail":self.error_message(str(err))}
            return message, None

    def get_datas(self, table_schema, table_name, table_views, request, url, fields, tenant=None, timezone='Etc/GMT-7', group_by=None):
        dinamic_pagination = DinamicPagination()
        integration = Integration(self.token, self.module, self.access)
        connection = self._connection()
        try:
			# Get parameter request #
            limit = request.get('limit', 10) if request.get('limit') != "" else 10
            page = request.get('page', 1) if request.get('page') != "" else 1
            order = request.get('order', 'id') if request.get('order') != "" else "id"
            sort = request.get('sort', 'ASC') if request.get('sort') != "" else "ASC"
            search = request.get('search', '')
			# Get parameter request #

			# Start check field #
            logic_service = LogicServices(timezone, search, self.token, self.module, self.access)
            open_cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            integration_datas, childrens, select_field, where_integration, self_join_table, groups = logic_service.build_query(group_by, fields, table_schema, table_views)
            # End check field #

			# Start get where condition #
            where_dict = self._where_dict(table_schema, table_name, request)
            where_like = self._where_like(table_schema, table_name, search, where_integration)
			# End get where condition #

			# Start check order by & limitation data #
            order_by = f"ORDER BY {table_name}.{order} {sort}"
            limit_by = f"OFFSET {int(limit)*(int(page)-1)} LIMIT {limit}"
			# End check order by & limitation data #

			# Start check custom exception #
            additional_query = self.custom_exception_query(table_name)
			# End check custom exception #
            
			# Start build select #
            query_builder = QueryBuilder()
            query_data = (
                query_builder.select(select_field)
                    .from_table(table_schema, table_name)
                    .join(self_join_table)
                    .where(f"1=1 {where_like} {where_dict} {additional_query}")
                    .group_by(groups)
                    .order_by(f"{table_name}.{order}", sort)
                    .offset(int(limit)*(int(page)-1))
                    .limit(limit)
                    .build(False, False)
            )
			# End build select #
            
			# Start build counting #
            query_builder = QueryBuilder()
            query_count = (
                query_builder.select(select_field)
                    .from_table(table_schema, table_name)
                    .join(self_join_table)
                    .where(f"1=1 {where_like} {where_dict} {additional_query}")
                    .group_by(groups)
                    .build(True, True if groups else False)
            )
			# End build counting #
			
			# Start execute query list #
            open_cursor.execute(query_data)
            datas = open_cursor.fetchall()
			# End execute query list #

			# Start execute query counting #
            open_cursor.execute(query_count)
            count = open_cursor.fetchall()
			# End execute query counting #

			# Start check self foreign key if exist (6 level static) showing children and parent #
            datas = logic_service.children_query(open_cursor, tenant, childrens, datas, select_field, table_schema, table_name, self_join_table, integration_datas)
			# End check self foreign key if exist (6 level static) showing children and parent #

			# Start generate pagination url #
            previous = dinamic_pagination.generate_previous_page(url, request, count[0].get('count'))
            next = dinamic_pagination.generate_next_page(url, request, count[0].get('count'))
			# End generate pagination url #

			# Start generate response #
            responses = {"status":200, "page" : page, "count" : count[0].get("count") , "previous" : previous, "next" : next, "data" : datas}
			# End generate response #

			# Start close connection #
            open_cursor.close()
            connection.close()
			# End close connection #
            return responses, integration_datas
        except Exception as err:
            connection.rollback()
            connection.close()
            message = {"status":400, "detail":self.error_message(str(err))}
            return message, None

    def get_user_assign(self, integration, json_data):
        users = []
        if json_data.get('assigns'):
            users = integration.get_user_list("auth_user_list", ','.join(json_data.get('assigns')))
        elif json_data.get('users'):
            users = integration.get_user_list("auth_user_list", ','.join(json_data.get('users')))
        return users

    def post_datas(self, json_data, table_schema, table_name, returnings="id"):
        external_integration_services = ExternalIntegrationServices("create", self.module, self.token)

        connection = self._connection()
        try:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            array_datas = []
            set_additional_mappings = []

            for data in json_data.get('datas'):
                # Start check integration to another apps first action internal app true #
                data = external_integration_services.create_data_integration(data, "true")
                # Start check integration to another apps first action internal app true #

                values = ""
                fields = ""
				# Set field module
                for idx, key in enumerate(data):
                    if key != "additional_fields":
                        fields += f'"{key}",'
                        if str(type(data.get(key))) == "<class 'bytes'>":  # Handling for json_data['data']
                            values += f"{psycopg2.Binary(data.get(key))},"
                        elif data.get(key) is None or data.get(key) == "" or data.get(key) == "None" or str(data.get(key)).lower() == "null":
                            values += f"null,"
                        elif data.get(key) == True:
                            values += f"{data.get(key)},"
                        elif data.get(key) == False:
                            values += f"{data.get(key)},"
                        else:
                            val = str(data.get(key)).replace("'", "''")
                            #values += f"'{data.get(key)}',"
                            values += f"'{val}',"

                values = replace_last_character(values, ",", "")
                fields = replace_last_character(fields, ",", "")

                created_by = f""" '{self.created_by}'""" if self.created_by is not None else f""" null"""

                qry_data = f"""INSERT INTO {table_schema}.{table_name} ({fields}, "created_by", "created_date") VALUES ({values}, {created_by}, NOW()) RETURNING {returnings};"""
                cursor.execute(qry_data)
                id = cursor.fetchone()

				# Set value Additional Field Loop
                for idx, key in enumerate(data):
                    if key == "additional_fields":
                        for mapping in data.get(key):
                            json_mapping = {}
                            for idx, keys in enumerate(mapping):
                                if keys == "additional_field" or keys == "data":
                                    json_mapping.update({keys:mapping.get(keys)})
                            json_mapping.update({"tenant":data.get("tenant"), "refference_id":id.get('id')})
                            set_additional_mappings.append(json_mapping)
                array_datas.append(id)

				# Start create data cache #
                self.cache_services.create_data_caches(f"{self.module}_{data.get('tenant')}_{id.get('id')}", id.get('id'), data)
				# End create data cache #
				# Start trigger flag data update #
                self.cache_services.set_caches(f"{self.module}_STATUS_UPDATE_{data.get('tenant')}", {"status":True})
				# End trigger flag data update #

                # Start check integration to another apps #
                for idx, key in enumerate(id):
                    data.update({key:id[key]})
                # End check integration to another apps #

            connection.commit()
            cursor.close()
            connection.close()

            datas = {"status":200, "detail" : Messages.success_save_data, "data":array_datas}
            return datas, set_additional_mappings
        except Exception as err:
            logging.error(".................................................................")
            logging.error(err)
            logging.error(f"Json Request : {json_data}")
            logging.error(f"Table Schema : {table_schema}")
            logging.error(f"Table Name : {table_name}")
            logging.error(".................................................................")
            message = {"status":400, "detail":self.error_message(str(err))}
            connection.rollback()
            connection.close()
            return message, []

    def error_message(self, message):
        if message.find("duplicate key value") >= 0 and message.find("already exists") >= 0:
            return Messages.duplicate_data
        elif message.find("column") >= 0 and message.find("does not exist") >= 0:
            return Messages.column_not_exist
        elif message.find("relation") >= 0 and message.find("does not exist") >= 0:
            return Messages.table_not_exist
        elif message.find("relation") >= 0 and message.find("not-null constraint") >= 0:
            return Messages.field_not_null
        elif message.find("syntax error at or near") >= 0:
            return Messages.syntax_error
        else:
            return Messages.failed_process

    def patch_datas(self, json_data, table_schema, table_name, returnings="id"):
        external_integration_services = ExternalIntegrationServices("update", self.module, self.token)

        connection = self._connection()
        try:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            array_datas = []
            exist_additional_mappings = []
            not_exist_additional_mappings = []

            for data in json_data.get('datas'):
                # Start check integration to another apps first action internal app true #
                data = external_integration_services.update_data_integration(data, "true")
                # Start check integration to another apps first action internal app true #

                update_field = ""
                condition = ""
                for idx, key in enumerate(data):
                    if key != "additional_fields":
                        if key != "id":
                            if data.get(key) is None or data.get(key) == "" or data.get(key) == "None":
                                update_field += f""""{key}" = null,"""
                            elif data.get(key) == True:
                                update_field += f""""{key}" = {data.get(key)},"""
                            elif data.get(key) == False:
                                update_field += f""""{key}" = {data.get(key)},"""
                            else:
                                val = str(data.get(key)).replace("'", "''")
                                update_field += f""""{key}" = '{val}',"""
                        else:
                            condition += f""""{key}" = {data.get(key)}"""
                    else:
                        for mapping in data.get(key):
                            json_mapping = {}
                            for idx, keys in enumerate(mapping):
                                if keys == "id" or keys == "additional_field" or keys == "data":
                                    json_mapping.update({keys:mapping.get(keys)})

                            if json_mapping.get('id') is not None:
                                exist_additional_mappings.append(json_mapping)
                            else:
                                del json_mapping['id']
                                json_mapping.update({"refference_id":data.get('id'), "tenant":data.get('tenant')})
                                not_exist_additional_mappings.append(json_mapping)
                update_field = replace_last_character(update_field, ",", "")

                last_modified_by = f""" "last_modified_by"='{self.created_by}'""" if self.created_by is not None else f""" "last_modified_by"=null"""

                qry_data = f"""UPDATE {table_schema}.{table_name} SET {update_field}, {last_modified_by}, "last_modified_date"=NOW() WHERE {condition} RETURNING {returnings};"""
                
                cursor.execute(qry_data)

                id = cursor.fetchone()
                array_datas.append(id)

				# Start update/create data cache #
                self.cache_services.update_data_caches(f"{self.module}_{data.get('tenant')}_{id.get('id')}", data)
				# End update/create data cache #
				# Start trigger flag data update #
                self.cache_services.set_caches(f"{self.module}_STATUS_UPDATE_{data.get('tenant')}", {"status":True})
				# End trigger flag data update #

            connection.commit()
            cursor.close()
            connection.close()

            datas = {"status":200, "detail" : Messages.success_update_data, "data":array_datas}
            return datas, exist_additional_mappings, not_exist_additional_mappings
        except Exception as err:
            logging.error(".................................................................")
            logging.error(err)
            logging.error(f"Json Request : {json_data}")
            logging.error(f"Table Schema : {table_schema}")
            logging.error(f"Table Name : {table_name}")
            logging.error(".................................................................")
            message = {"status":400, "detail":self.error_message(str(err))}
            connection.rollback()
            connection.close()
            return message, [], []

    def bulk_patch_datas(self, json_data, table_schema, table_name, returnings="id"):
        connection = self._connection()
        try:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            array_datas = []
            exist_additional_mappings = []
            not_exist_additional_mappings = []

            for data in json_data.get('datas'):
                update_field = ""
                condition = ""
                for idx, key in enumerate(data):
                    if key != "additional_fields":
                        if key != "id":
                            if data.get(key) is None or data.get(key) == "" or data.get(key) == "None":
                                update_field += f""""{key}" = null,"""
                            elif data.get(key) == True:
                                update_field += f""""{key}" = {data.get(key)},"""
                            elif data.get(key) == False:
                                update_field += f""""{key}" = {data.get(key)},"""
                            else:
                                update_field += f""""{key}" = '{data.get(key)}',"""
                        else:
                            condition += f""""{key}" = {data.get(key)}"""
                    else:
                        for mapping in data.get(key):
                            json_mapping = {}
                            for idx, keys in enumerate(mapping):
                                if keys == "id" or keys == "additional_field" or keys == "data":
                                    json_mapping.update({keys:mapping.get(keys)})

                            if json_mapping.get('id') is not None:
                                exist_additional_mappings.append(json_mapping)
                            else:
                                del json_mapping['id']
                                json_mapping.update({"refference_id":data.get('id'), "tenant":data.get('tenant')})
                                not_exist_additional_mappings.append(json_mapping)
                update_field = replace_last_character(update_field, ",", "")

				# Start bulk update #
                if condition == "":
                    for idx, key in enumerate(json_data):
                        if key == "module":
                            condition += ""
                        elif key == "datas":
                            condition += ""
                        else:
                            condition += f""""{key}" = {json_data.get(key)} AND """
                    condition = replace_last_character(condition, "AND", "")
				# End bulk update #
                last_modified_by = f""" "last_modified_by"='{self.created_by}'""" if self.created_by is not None else f""" "last_modified_by"=null"""

                qry_data = f"""UPDATE {table_schema}.{table_name} SET {update_field}, {last_modified_by}, "last_modified_date"=NOW() WHERE {condition} RETURNING {returnings};"""
                cursor.execute(qry_data)

                id = cursor.fetchone()
                array_datas.append(id)

            cursor.close()
            connection.commit()
            connection.close()

            datas = {"status":200, "detail" : Messages.success_update_data, "data":array_datas}
            return datas, exist_additional_mappings, not_exist_additional_mappings
        except Exception as err:
            logging.error(".................................................................")
            logging.error(err)
            logging.error(f"Json Request : {json_data}")
            logging.error(f"Table Schema : {table_schema}")
            logging.error(f"Table Name : {table_name}")
            logging.error(".................................................................")
            message = {"status":400, "detail":self.error_message(str(err))}
            connection.rollback()
            connection.close()
            return message, [], []

    def custom_query(self, report_data, table_schema, table_name, table_views, request, url, fields, export=False):
        dinamic_pagination = DinamicPagination()
        connection = self._connection()
        try:
            select_field = f"{fields}"
            where_integration = ""
            self_join_table = ""
			
			# Get parameter request #
            #start = request.get('start', 0) if request.get('start') != "" else 0
            limit = 0 if export else (request.get('limit', 10) if request.get('limit') != "" else 10)
            page = request.get('page', 1) if request.get('page') != "" else 1
            order = request.get('order', 'id') if request.get('order') != "" else "id"
            sort = request.get('sort', 'ASC') if request.get('sort') != "" else "ASC"
            period_start = request.get('period_start', str(datetime.now().year)) if request.get('period_start') != "" else str(datetime.now().year)
            period_end = request.get('period_end', str(datetime.now().year)) if request.get('period_end') != "" else str(datetime.now().year)
            type = request.get('type', 'Revenue') if request.get('type') != "" else "Revenue"
            search = request.get('search', '')
			# Get parameter request #

            open_cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

			# Start get where condition #
            where_dict = self._where_custom_dict(report_data.get('description'), request)
            where_like = self._where_custom_like(report_data.get('description'), search, request)
			# End get where condition #

			# Functional query with filter #
            function = report_data.get('function').replace("{filter}", f"{where_dict} {where_like}")
            function = function.replace('{period_start}', period_start)
            function = function.replace('{period_end}', period_end)
            function = function.replace('{type}', type)
 			# Functional query with filter #

			# Start check order by & limitation data #
            order_by = f"ORDER BY {order} {sort}"
            limit_by = f"OFFSET {int(limit)*(int(page)-1)} LIMIT {limit}" if limit!=0 else ""
			# End check order by & limitation data #

			# Start generate query list #
            qry_data = f"SELECT {select_field} FROM ({function} {order_by} {limit_by}) a"
			# End generate query list #
            
			# Start generate query counting #
            qry_count = f"SELECT count(a.*) FROM ( {function} ) a"
			# End generate query counting #

			# Start execute query list #
            open_cursor.execute(qry_data)
            datas = open_cursor.fetchall()
			# End execute query list #

			# Start execute query counting #
            open_cursor.execute(qry_count)
            count = open_cursor.fetchall()
			# End execute query counting #

			# Start generate pagination url #
            previous = dinamic_pagination.generate_previous_page(url, request, count[0].get('count'))
            next = dinamic_pagination.generate_next_page(url, request, count[0].get('count'))
			# End generate pagination url #

			# Start generate response #
            responses = {"status":200, "page" : page, "count" : count[0].get("count") , "previous" : previous, "next" : next, "data" : datas}
			# End generate response #

			# Start close connection #
            open_cursor.close()
            connection.close()
			# End close connection #
            return responses
        except Exception as err:
            logging.error(".................................................................")
            logging.error(err)
            logging.error(f"Table Schema : {table_schema}")
            logging.error(f"Table Name : {table_name}")
            logging.error(".................................................................")
            message = {"status":400, "detail":self.error_message(str(err))}
            connection.rollback()
            connection.close()
            return message

    def custom_report_query(self, report_data, table_schema, table_name, table_views, request, url, fields, export=False):
        dinamic_pagination = DinamicPagination()
        connection = self._connection()
        try:
            select_field = f"{fields}"
            where_integration = ""
            self_join_table = ""

			# Get parameter request #
            #start = request.get('start', 0) if request.get('start') != "" else 0
            limit = 0 if export else (request.get('limit', 10) if request.get('limit') != "" else 10)
            page = request.get('page', 1) if request.get('page') != "" else 1
            order = request.get('order', 'id') if request.get('order') != "" else "id"
            sort = request.get('sort', 'ASC') if request.get('sort') != "" else "ASC"
            date_from = request.get('created_date__start', None) if request.get('created_date__start') != "" else None
            date_to = request.get('created_date__end', None) if request.get('created_date__end') != "" else None
            search = request.get('search', '')
			# Get parameter request #

            open_cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

			# Functional query with filter #
            function = report_data.get('function')
            function = function.replace("{params}", search)
            function = function.replace("{date_from}", date_from)
            function = function.replace("{date_to}", date_to)
 			# Functional query with filter #
            
			# Start check order by & limitation data #
            order_by = f"ORDER BY {order} {sort}"
            limit_by = f"OFFSET {int(limit)*(int(page)-1)} LIMIT {limit}" if limit!=0 else ""
			# End check order by & limitation data #

			# Start generate query list #
            qry_data = f"SELECT {select_field} FROM ({function} {order_by} {limit_by}) a"
			# End generate query list #
            
			# Start generate query counting #
            qry_count = f"SELECT count(a.*) FROM ( {function} ) a"
			# End generate query counting #

			# Start execute query list #
            open_cursor.execute(qry_data)
            datas = open_cursor.fetchall()
			# End execute query list #

			# Start execute query counting #
            open_cursor.execute(qry_count)
            count = open_cursor.fetchall()
			# End execute query counting #

			# Start generate pagination url #
            previous = dinamic_pagination.generate_previous_page(url, request, count[0].get('count'))
            next = dinamic_pagination.generate_next_page(url, request, count[0].get('count'))
			# End generate pagination url #

			# Start generate response #
            responses = {"status":200, "page" : page, "count" : count[0].get("count") , "previous" : previous, "next" : next, "data" : datas}
			# End generate response #

			# Start close connection #
            open_cursor.close()
            connection.close()
			# End close connection #
            return responses
        except Exception as err:
            logging.error(".................................................................")
            logging.error(err)
            logging.error(f"Table Schema : {table_schema}")
            logging.error(f"Table Name : {table_name}")
            logging.error(".................................................................")
            message = {"status":400, "detail":self.error_message(str(err))}
            connection.rollback()
            connection.close()
            message = {"status":400, "detail":str(err).strip().split("\n")}
            return message
			
    def _check_data_type(self, table_schema, table_name, attributes, value):
        columns = self.get_columns(table_schema, table_name)
        attribute, equals = self._check_equals(attributes.split("__"), value)
        value = value.replace("'", "''") if value else value

        def is_null(val):
            return val is None or val.lower() in ['null', 'notnull']

        for column in columns:
            col_name = column.get('column_name')
            if col_name != attribute:
                continue

            data_type = column.get('data_type')
            column_ref = f'{table_name}."{col_name}"'

            if data_type in GroupTypeData.character:
                if equals not in ["IN", "NOT IN"]:
                    if is_null(value):
                        return f" AND lower({column_ref}) {equals}"
                    return f" AND lower({column_ref}) {'is' if value.lower() == 'null' else equals} lower('{value}')"
                else:
                    val_list = "','".join(value.split(','))
                    return f" AND {column_ref} {equals} ('{val_list}')"

            elif data_type in GroupTypeData.date:
                convert_format = "::date" if len(attributes.split("__")) == 2 else ""
                if is_null(value):
                    return f" AND {column_ref} {equals}"
                return f" AND {column_ref}{convert_format} {'is' if value.lower() == 'null' else equals} '{value}'"

            elif data_type in GroupTypeData.array:
                if equals == "NOT IN":
                    return f" AND NOT ('{value}'::text = ANY({column_ref}::text[]))"
                return f" AND '{value}'::text = ANY({column_ref}::text[])"

            else:
                if equals not in ["IN", "NOT IN"]:
                    if is_null(value):
                        return f" AND {column_ref} {equals}"
                    return f" AND {column_ref} {'is' if value.lower() == 'null' else equals} {value}"
                else:
                    val_list = ",".join(value.split(','))
                    return f" AND {column_ref} {equals} ({val_list})"

        return ""
		
    def _check_equals(self, attribute, value):
        if value.lower() == "null":
            return attribute[0], "IS NULL"
        if value.lower() == "notnull":
            return attribute[0], "IS NOT NULL"
        else:
            if len(attribute) > 1:
                if attribute[1] == "start":
                    return attribute[0], ">="
                elif attribute[1] == "end":
                    return attribute[0], "<="
                elif attribute[1] == "in":
                    return attribute[0], "IN"
                elif attribute[1] == "notin":
                    return attribute[0], "NOT IN"
        return attribute[0], "="

    def _connection(self):
        #conn = psycopg2.connect("dbname=" + self.db_name + " host='"+self.db_host+"' user='"+ self.db_user +"' password='"+ self.db_password +"'")
        try:
            conn_str = f"dbname={self.db_name} host='{self.db_host}' port={self.db_port} user='{self.db_user}' password='{self.db_password}'"
            conn = psycopg2.connect(conn_str)
            return conn
        except:
            conn_str = f"dbname={self.db_name} host='{self.db_host}' port='5433' user='{self.db_user}' password='{self.db_password}'"
            conn = psycopg2.connect(conn_str)
            return conn

    def _where_dict(self, table_schema, table_name, request):
        where_dict = ""
        for idx, key in enumerate(dict(request)):
            if key != "search" and key != "limit" and key != "page" and key != "start" and key != "limit" and key != "sort" and key != "order" and request.get(key, '') != "":
                where_dict += self._check_data_type(table_schema, table_name, key, request.get(key, ''))

        return where_dict

    def _where_custom_dict(self, field_structure, request):
        columns = json.loads(field_structure)
        where_dict = ""
        for idx, key in enumerate(dict(request)):
            if key != "search" and key != "limit" and key != "page" and key != "start" and key != "limit" and key != "sort" and key != "order" and request.get(key, '') != "":
                where_dict += self._check_custom_data_type(field_structure, key, request.get(key, ''))
        return where_dict

    def _where_custom_like(self, field_structure, search, request):
        columns = json.loads(field_structure)
        where_like = ""
        for idx, key in enumerate(columns.get('filter')):
            val = search.replace("'", "''")
            if idx == 0:
                where_like += f" AND ({columns.get('initial_query')}.{self._custom_cast_data_type(key)} ILIKE '%{val}%'"
            else:
                where_like += f" OR {columns.get('initial_query')}.{self._custom_cast_data_type(key)} ILIKE '%{val}%'"
        where_like += f")"
        return where_like

    def _where_like(self, table_schema, table_name, search, where_integration):
        where_str = ""
        columns = self.get_columns(table_schema, table_name)
        for idx, column in enumerate(columns):
            val = search.replace("'", "''")
            if idx == 0:
                where_str += f" AND ({table_name}." + self._cast_data_type(column) + f" ILIKE '%{val}%' "
            else:
                where_str += f" OR {table_name}." + self._cast_data_type(column) + f" ILIKE '%{val}%' "
        where_str += f" {where_integration} ) "
        return where_str

    def _check_custom_data_type(self, field_structure, attribute, value):
        columns = json.loads(field_structure)
        attribute, equals = self._check_equals(attribute.split("__"), value)
        value = value.replace("'", "''")
        for column in columns.get('filter'):
            qry = ""
            if column == attribute:
                if columns.get('filter').get(column) in GroupTypeData.character:
                    if equals != "IN":
                        if value.lower() == 'null' or value is None or value.lower() == 'notnull':
                            qry = f" AND lower({columns.get('initial_query')}.\"{column}\") {equals}"
                        else:
                            qry = f" AND lower({columns.get('initial_query')}.\"{column}\") {'is' if value == 'null' else equals} lower('{value}')"
                    else:
                        val = "','".join(value.split(','))
                        val = f"('{val}')"
                        qry = f" AND {columns.get('initial_query')}.\"{column}\" {equals} {val}"
                    return qry
                elif columns.get('filter').get(column) in GroupTypeData.date:
                    qry = f" AND {columns.get('initial_query')}.\"{column}\"::date {'is' if value == 'null' else equals} '{value}'"
                    return qry
                elif columns.get('filter').get(column) in GroupTypeData.array:
                    qry = f" AND '{value}'::text = ANY({columns.get('initial_query')}.\"{column}\"::text[])"
                    return qry
                else:
                    qry = f" AND {columns.get('initial_query')}.\"{column}\" {'is' if value == 'null' else equals} {value}"
                    return qry
        return qry

    def _cast_data_type(self, column):
        return f"\"{column.get('column_name')}\"::text"

    def _custom_cast_data_type(self, column):
        return f"\"{column}\"::text"
