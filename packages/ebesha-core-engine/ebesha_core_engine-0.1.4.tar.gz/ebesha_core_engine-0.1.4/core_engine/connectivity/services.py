# Author : Puji Anugrah Pangestu #
# Created : 31 July 2025 #

from core_engine.bridges.integration import Integration

class LogicServices:
    def __init__(self, timezone='', search='', token=None, module=None, access=None):
        self.timezone=timezone
        self.search=search
        self.token=token
        self.module=module
        self.access=access

    def build_query(self, group_by, fields, table_schema, table_views):
        integration = Integration(self.token, self.module, self.access)
        integration_datas = []
        childrens = []
        select_field = ""
        where_integration = ""
        self_join_table = ""
        groups = None
        if group_by is not None:
            table_name = table_views[0].get('name')
            group_arr = group_by.split(",")
            groups = ""
            for group in group_arr:
                select_field += f"{table_name}.\"{group}\","
                groups += f"{table_name}.\"{group}\","
            groups = groups.rstrip(',').strip()
        else:
            if fields is not None:
                for field in fields.split(","):
                    for tables in table_views:
                        table_name = tables.get('name')
                        for table_view in tables.get('fields'):
                            if(table_view.get('name')==field):
                                if table_view.get('integration') is not None:
                                    integration_datas.append({"name":table_view.get('name'),"integration":table_view.get('integration')})

                                    where_difference_modules = integration.find_search_integration(table_view.get('integration'), self.search)
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

                                elif table_view.get('fk_to'):
                                    self_join_table += f" LEFT JOIN {table_schema}.\"{table_view.get('fk_to').get('table')}\" {table_name}_{table_view.get('name')} on {table_name}_{table_view.get('name')}.{table_view.get('fk_to').get('field')} = {table_name}.{table_view.get('name')} "
                                    select_field += f"to_json({table_name}_{table_view.get('name')}.*) as {table_view.get('name')},"
                                else:
                                    if "date" in table_view.get('name') or 'Timestamp' in table_view.get('type') or 'Interval' in table_view.get('type'):
                                        # Start set date with timezone tenant #
                                        if table_view.get('name') == "created_date" or table_view.get('name') == "last_modified_date":
                                            select_field += f"({table_name}.\"{field}\"::timestamp AT TIME ZONE '{self.timezone}')::timestamp as {field},"
                                        else:
                                            select_field += f"{table_name}.\"{field}\","
                                        # End set date with timezone tenant #
                                    else:
                                        select_field += f"{table_name}.\"{field}\","
            else:
                for tables in table_views:
                    for table_view in tables.get('fields'):
                        table_name = tables.get('name')
                        if table_view.get('view'):
                            if table_view.get('integration') is not None:
                                integration_datas.append({"name":table_view.get('name'),"integration":table_view.get('integration')})

                                where_difference_modules = integration.find_search_integration(table_view.get('integration'), self.search)
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

                            elif table_view.get('fk_to'):
                                self_join_table += f" LEFT JOIN {table_schema}.\"{table_view.get('fk_to').get('table')}\" {table_name}_{table_view.get('name')} on {table_name}_{table_view.get('name')}.{table_view.get('fk_to').get('field')} = {table_name}.{table_view.get('name')} "
                                select_field += f"to_json({table_name}_{table_view.get('name')}.*) as {table_view.get('name')},"
                            else:
                                if "date" in table_view.get('name') or 'Timestamp' in table_view.get('type') or 'Interval' in table_view.get('type'):
                                    # Start set date with timezone tenant #
                                    if table_view.get('name') == "created_date" or table_view.get('name') == "last_modified_date":
                                        select_field += f"({table_name}.\"{table_view.get('name')}\"::timestamp AT TIME ZONE '{self.timezone}')::timestamp as {table_view.get('name')},"
                                    else:
                                        select_field += f"{table_name}.\"{table_view.get('name')}\","
                                else:
                                    select_field += f"{table_name}.\"{table_view.get('name')}\","
        select_field = select_field.rstrip(',').strip()
        return integration_datas, childrens, select_field, where_integration, self_join_table, groups
		
    def children_query(self, open_cursor, tenant, childrens, datas, select_field, table_schema, table_name, self_join_table, integration_datas):
        integration = Integration(self.token, self.module, self.access)

        def fetch_children(parent_id, level):
            if level > 6:
                return []

            query = f"""
                SELECT {select_field}
                FROM {table_schema}."{table_name}" {table_name}
                {self_join_table}
                WHERE {table_name}.{child_field} = {parent_id}
                ORDER BY {table_name}.id
            """
            open_cursor.execute(query)
            children = open_cursor.fetchall()
            children = integration.check_integration({"data": children}, integration_datas, self.module, None, tenant).get("data")

            for child in children:
                child["users_detail"] = self.get_user_assign(integration, child)
                child["children"] = fetch_children(child.get("id"), level + 1)

            return children

        '''def fetch_parents_recursive(current_parent):
            if not current_parent or not current_parent.get("parent"):
                return None

            parent_id = current_parent["parent"].get("id")
            if not parent_id:
                return None

            try:
                query = f"""
                    SELECT "id", "name", "parent"
                    FROM {table_schema}."{table_name}" {table_name}
                    WHERE {table_name}."id" = {parent_id}
                """
                open_cursor.execute(query)
                parent_data = open_cursor.fetchone()
            except:
                connection.rollback()
                query = f"""
                    SELECT "id", "ticket_number", "parent"
                    FROM {table_schema}."{table_name}" {table_name}
                    WHERE {table_name}."id" = {parent_id}
                """
                open_cursor.execute(query)
                parent_data = open_cursor.fetchall()
				
            if parent_data:
                current_parent["parent"]["parent"] = parent_data
                current_parent["first_parent"] = parent_data
                fetch_parents_recursive(current_parent["parent"])'''

        if childrens:
            for child_field in childrens:
                for parent in datas:
                    parent["children"] = fetch_children(parent.get("id"), 1)
        
        '''for parent in datas:
            if parent.get("parent"):
                fetch_parents_recursive(parent)'''
				
        return datas
		
    def get_user_assign(self, integration, json_data):
        users = []
        if json_data.get('assigns'):
            users = integration.get_user_list("auth_user_list", ','.join(json_data.get('assigns')))
        elif json_data.get('users'):
            users = integration.get_user_list("auth_user_list", ','.join(json_data.get('users')))
        return users
		
    def build_insert_query(self, data, table_schema, table_name, returnings, cursor):
        fields = []
        values = []

        for key, val in data.items():
            if key == "additional_fields":
                continue

            fields.append(f'"{key}"')

            if isinstance(val, bytes):
                values.append(psycopg2.Binary(val))
            elif val in (None, "", "None") or str(val).lower() == "null":
                values.append("null")
            elif isinstance(val, bool):
                values.append(str(val))  # PostgreSQL accepts 'true'/'false' literals
            else:
                safe_val = str(val).replace("'", "''")
                values.append(f"'{safe_val}'")

        field_str = ", ".join(fields)
        value_str = ", ".join(map(str, values))
        created_by = f"'{self.created_by}'" if self.created_by else "null"

        query = f"""
            INSERT INTO {table_schema}.{table_name}
            ({field_str}, "created_by", "created_date")
            VALUES ({value_str}, {created_by}, NOW())
            RETURNING {returnings};
        """

        cursor.execute(query)
        return cursor.fetchone()
	
    '''def children_query(self, childrens, datas, select_field, table_schema, table_name, self_join_table, integration_datas):
        integration = Integration(self.token, self.module, self.access)
        if childrens:
			# Start check self foreign key if exist (6 level static)#
            for children in childrens:
                for parent in datas:
                    qry_child1 = f"""SELECT {select_field}
                    FROM {table_schema}."{table_name}" {table_name}
                    {self_join_table}
                    WHERE {table_name}.{children} = {parent.get('id')}
                    order by {table_name}.id"""
                    open_cursor.execute(qry_child1)
                    childs1 = open_cursor.fetchall()

                    childs1 = integration.check_integration({"data":childs1}, integration_datas, self.module, None, tenant)
                    for child1 in childs1.get('data'):
						# Start get detail user assigns #
                        child1.update({"users_detail": self.get_user_assign(integration, child1)})
						# Start get detail user assigns #

                        qry_child2 = f"""SELECT {select_field}
                        FROM {table_schema}."{table_name}" {table_name}
                        {self_join_table}
                        WHERE {table_name}.{children} = {child1.get('id')}
                        order by {table_name}.id"""

                        open_cursor.execute(qry_child2)
                        childs2 = open_cursor.fetchall()

                        childs2 = integration.check_integration({"data":childs2}, integration_datas, self.module, None, tenant)
                        for child2 in childs2.get('data'):
						    # Start get detail user assigns #
                            child2.update({"users_detail": self.get_user_assign(integration, child2)})
						    # Start get detail user assigns #

                            qry_child3 = f"""SELECT {select_field}
                            FROM {table_schema}."{table_name}" {table_name}
                            {self_join_table}
                            WHERE {table_name}.{children} = {child2.get('id')}
                            order by {table_name}.id"""

                            open_cursor.execute(qry_child3)
                            childs3 = open_cursor.fetchall()

                            childs3 = integration.check_integration({"data":childs3}, integration_datas, self.module, None, tenant)
                            for child3 in childs3.get('data'):
					    	    # Start get detail user assigns #
                                child3.update({"users_detail": self.get_user_assign(integration, child3)})
						        # Start get detail user assigns #

                                qry_child3 = f"""SELECT {select_field}
                                FROM {table_schema}."{table_name}" {table_name}
                                {self_join_table}
                                WHERE {table_name}.{children} = {child3.get('id')}
                                order by {table_name}.id"""

                                open_cursor.execute(qry_child3)
                                childs4 = open_cursor.fetchall()

                                childs4 = integration.check_integration({"data":childs4}, integration_datas, self.module, None, tenant)
                                for child4 in childs4.get('data'):
					    	        # Start get detail user assigns #
                                    child4.update({"users_detail": self.get_user_assign(integration, child4)})
						            # Start get detail user assigns #

                                    qry_child4 = f"""SELECT {select_field}
                                    FROM {table_schema}."{table_name}" {table_name}
                                    {self_join_table}
                                    WHERE {table_name}.{children} = {child4.get('id')}
                                    order by {table_name}.id"""

                                    open_cursor.execute(qry_child4)
                                    childs5 = open_cursor.fetchall()

                                    childs5 = integration.check_integration({"data":childs5}, integration_datas, self.module, None, tenant)
                                    for child5 in childs5.get('data'):
					        	        # Start get detail user assigns #
                                        child5.update({"users_detail": self.get_user_assign(integration, child5)})
						                # Start get detail user assigns #

                                        qry_child5 = f"""SELECT {select_field}
                                        FROM {table_schema}."{table_name}" {table_name}
                                        {self_join_table}
                                        WHERE {table_name}.{children} = {child5.get('id')}
                                        order by {table_name}.id"""

                                        open_cursor.execute(qry_child5)
                                        childs6 = open_cursor.fetchall()

                                        childs6 = integration.check_integration({"data":childs6}, integration_datas, self.module, None, tenant)

                                        child5.update({"children":childs6.get('data')})
                                    child4.update({"children":childs5.get('data')})
                                child3.update({"children":childs4.get('data')})
                            child2.update({"children":childs3.get('data')})
                        child1.update({"children":childs2.get('data')})
                    parent.update({"children":childs1.get('data')})
			# End check self foreign key if exist #
        return datas'''