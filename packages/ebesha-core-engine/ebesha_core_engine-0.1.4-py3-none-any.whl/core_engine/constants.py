import os

class RootAPI:
    path = {
        "users":  {"url": os.environ.get('AUTHORIZATION_URL') + "/v2/users/status?id={}", "headers": {"Authorization": "{}"}},
        "user_lists": {"url": os.environ.get('AUTHORIZATION_URL') + "/v2/users/list", "headers": {"Authorization": "{}"}, "body": {"tenant": "{}"}},
        "user_access_lists": {"url": os.environ.get('AUTHORIZATION_URL') + "/v2/users/check-access-list", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "tenant": "{}", "create": "{}", "read": "{}",  "update": "{}", "delete": "{}", "is_self_data": "{}"}},
        "auth_user_list": {"url": os.environ.get('AUTHORIZATION_URL') + "/v3/um-auth-user-tenant/?view=true&user__in={}", "headers": {"Authorization": "Token {}"}},
        "user_list_root":  {"url": os.environ.get('AUTHORIZATION_URL') + "/v2/users/root-list?id={}", "headers": {"Authorization": "{}"}},
        "users_auth_tenant": {"url": os.environ.get('AUTHORIZATION_URL') + "/v3/um-auth-user-tenant/?view=true&tenant={}", "headers": {"Authorization": "Token {}"}},
        "role_users":  {"url": os.environ.get('AUTHORIZATION_URL') + "/v3/um-role-users/?role_type={}&user_id={}", "headers": {"Authorization": "Token {}"}},
        "update_bulk_menu":  {"url": os.environ.get('AUTHORIZATION_URL') + "/v3/um-role-menus/bulk/updates-menu", "headers": {"Authorization": "Token {}"}, "body": {"tenant_id": "{}", "role_id": "{}", "menu_name": "{}"}},
        "member_live_chat_list": {"url": "{}/dinamic-module/data-lists?fields=id,user_id,username,profile&id__in={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "tenant_configurations":  {"url": os.environ.get('AUTHORIZATION_URL') + "/v3/um-tenant-configurations/configurations?tenant={}", "headers": {"Authorization": "{}"}},
        "group_list": {"url": "{}/dinamic-module/data-lists?fields=id,name&id__in={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_ORIGIN": {"url": "{}/dinamic-module/data-lists?fields=id,name&id__in={}", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_ORIGIN", "access": "read"}},
        "EBESHA_CRM_TR_ACCOUNT": {"url": "{}/dinamic-module/data-lists?fields=id,name&id__in={}", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_TR_ACCOUNT", "access": "read"}},
        "EBESHA_CRM_TR_CONTACT": {"url": "{}/dinamic-module/data-lists?fields=id,name&id__in={}", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_TR_CONTACT", "access": "read"}},
        "EBESHA_CRM_SETTING_STATUS": {"url": "{}/dinamic-module/data-lists?fields=id,name,color&id__in={}", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_STATUS", "access": "read"}},
        "EBESHA_CRM_SETTING_CATEGORY": {"url": "{}/dinamic-module/data-lists?fields=id,name,color&id__in={}", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_CATEGORY", "access": "read"}},
        "EBESHA_SALES_TR_DEAL": {"url": "{}/dinamic-module/data-lists?fields=id,name&id__in={}", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SALES_TR_DEAL", "access": "read"}},
        "EBESHA_CRM_SETTING_SALES_SLA": {"url": "{}/dinamic-module/data-lists?fields=id,name&id__in={}", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_SALES_SLA", "access": "read"}}
    }

class MappingMultiPathAPI:
    path = {
        "EBESHA_CRM_SETTING_SERVICE_CATEGORY": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id__in={}&fields=id,name,parent&is_active=true&is_delete=false", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}}
    }

class MappingPathAPI:
    path = {
        "valid_token": f"{os.environ.get('AUTHORIZATION_URL')}/v2/users/valid-tokens", "tenants": {"url": os.environ.get('AUTHORIZATION_URL') + "/v3/um-tenants/?id={}&view=true", "headers": {"Authorization": "Token {}"}},
        "users": {"url": os.environ.get('AUTHORIZATION_URL') + "/v2/users/?id={}&view=true", "headers": {"Authorization": "Token {}"}},
        "departments": {"url": os.environ.get('AUTHORIZATION_URL') + "/v3/um-departments/?id={}&view=true", "headers": {"Authorization": "Token {}"}},
        "EBESHA_CRM_TR_ACCOUNT": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_ACCOUNT_OWNER": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_TR_CONTACT": {"url": os.environ.get('EBESHA_CRM_TR_CONTACT') + "/dinamic-module/data-lists?id={}&fields=id,name,email,priority", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_TR_CASE": {"url": os.environ.get('EBESHA_CRM_TR_CASE') + "/dinamic-module/data-lists?id={}&fields=id,ticket_number", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_ADDITIONAL_FIELD": {"url": os.environ.get('EBESHA_CRM_SETTING_ADDITIONAL_FIELD') + "/dinamic-module/data-lists?module_flag={}&fields=id,name,label,type,module_flag&is_active=true&is_delete=false", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_ADDITIONAL_MAPPING": {"url": os.environ.get('EBESHA_CRM_SETTING_ADDITIONAL_MAPPING') + "/dinamic-module/data-lists?refference_id={}&additional_field={}&is_active=true&is_delete=false", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_ADDITIONAL_DATA": {"url": os.environ.get('EBESHA_CRM_SETTING_ADDITIONAL_DATA') + "/dinamic-module/data-lists?additional_field={}&is_active=true&is_delete=false", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_ORIGIN": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}&fields=id,name&is_active=true&is_delete=false", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_PRIORITY": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}&fields=id,name&is_active=true&is_delete=false", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_STATUS": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}&fields=id,name,color,sequence,lock,percentage,color,icon&is_active=true&is_delete=false", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_CATEGORY": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}&fields=id,name&is_active=true&is_delete=false", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_SERVICE_CATEGORY": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}&fields=id,name&is_active=true&is_delete=false", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_CASE": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,format_ticket,counting_ticket,sequential", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_OMNICHANNEL_SETTING_TEMPLATE_BROADCAST": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?fields=id,name&is_active=true&is_delete=false", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_KNOWLEDGE_MANAGEMENT_APPROVAL": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}&fields=id,users&is_active=true&is_delete=false", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_OMNICHANNEL_CONFIGURATION_WHATSAPP": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?fields=id,username&is_active=true&is_delete=false", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_OMNICHANNEL_SETTING_CHATBOT_INTENT": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_EX_SETTING_POLICY": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_EX_SETTING_STATUS": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_EX_SETTING_WORKING_DAY": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_EX_SETTING_PERMIT_TYPE": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_EX_SETTING_LEAVE_TYPE": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_EX_SETTING_LEAVE_RULES": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_EX_SETTING_APPROVAL": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_PROBLEM_TYPE": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_IMPACT": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_CHANGE_TYPE": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_RISK": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_INDUSTRY": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SETTING_GENERAL_CITY": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SETTING_GENERAL_CURRENCY": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SETTING_GENERAL_CITY": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SETTING_GENERAL_PROVINCE": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SETTING_GENERAL_POSTAL_CODE": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,postal_code", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SETTING_GENERAL_GROUP": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SETTING_GENERAL_REASON": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SALES_TR_ACCOUNT": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SALES_TR_CONTACT": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SALES_TR_DEAL": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_MARKETING_TR_LEAD": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SETTING_GENERAL_BUSINESS_HOUR": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_EX_SETTING_CATEGORY": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CX_PRODUCT": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_EX_SETTING_EMPLOYEE_TYPE": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_GENERAL_TR_DISCUSSION": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,title", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_SALES": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_SALES_SLA": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}}
    }


class MappingDetailPathAPI:
    path = {
        "EBESHA_CRM_TR_ACCOUNT": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&additional_field_flag=true", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_TR_CONTACT": {"url": os.environ.get('EBESHA_CRM_TR_CONTACT') + "/dinamic-module/data-lists?id={}&additional_field_flag=true", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_ACCOUNT_OWNER": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?id={}&additional_field_flag=true", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_TR_CASE": {"url": os.environ.get('EBESHA_CRM_TR_CASE') + "/dinamic-module/data-lists?id={}&additional_field_flag=true", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_ADDITIONAL_FIELD": {"url": os.environ.get('EBESHA_CRM_SETTING_ADDITIONAL_FIELD') + "/dinamic-module/data-lists?id={}&additional_field_flag=true", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_ADDITIONAL_MAPPING": {"url": os.environ.get('EBESHA_CRM_SETTING_ADDITIONAL_MAPPING') + "/dinamic-module/data-lists?id={}&additional_field_flag=true", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_ADDITIONAL_DATA": {"url": os.environ.get('EBESHA_CRM_SETTING_ADDITIONAL_DATA') + "/dinamic-module/data-lists?id={}&additional_field_flag=true", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_ORIGIN": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}&additional_field_flag=true", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_PRIORITY": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}&additional_field_flag=true", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_STATUS": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}&additional_field_flag=true", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_CATEGORY": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}&additional_field_flag=true", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_TR_KNOWLEDGE_MANAGEMENT": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}&additional_field_flag=true", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_KNOWLEDGE_MANAGEMENT_APPROVAL": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_SERVICE_CATEGORY": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}&additional_field_flag=true", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_OMNICHANNEL_CONFIGURATION_WHATSAPP": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}&additional_field_flag=true", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_OMNICHANNEL_SETTING_CHATBOT_INTENT": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_PROBLEM_TYPE": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_IMPACT": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_CHANGE_TYPE": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_RISK": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_INDUSTRY": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SALES_TR_ACCOUNT": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SALES_TR_CONTACT": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SALES_TR_DEAL": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_MARKETING_TR_LEAD": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SETTING_GENERAL_BUSINESS_HOUR": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_SETTING_GENERAL_GROUP": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CX_PRODUCT": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_GENERAL_TR_DISCUSSION": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_SALES": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_SALES_SLA": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?id={}", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}}
    }


class MappingSearchAPI:
    search = {
        "valid_token": f"{os.environ.get('AUTHORIZATION_URL')}/v2/users/valid-tokens",
        "tenants": {"url": os.environ.get('AUTHORIZATION_URL') + "/v3/um-tenants/?search={}&view=true", "headers": {"Authorization": "Token {}"}},
        "users": {"url": os.environ.get('AUTHORIZATION_URL') + "/v2/users/?search={}&view=true", "headers": {"Authorization": "Token {}"}},
        "departments": {"url": os.environ.get('AUTHORIZATION_URL') + "/v3/departments/?search=true", "headers": {"Authorization": "Token {}"}},
        '''"EBESHA_CRM_TR_ACCOUNT": {"url": os.environ.get('EBESHA_CRM_TR_ACCOUNT') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_ACCOUNT_OWNER": {"url": os.environ.get('EBESHA_CRM_TR_CONTACT') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_TR_CONTACT": {"url": os.environ.get('EBESHA_CRM_TR_CONTACT') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_ORIGIN": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_PRIORITY": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_CATEGORY": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_TR_KNOWLEDGE_MANAGEMENT": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?name={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_STATUS": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?name={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_KNOWLEDGE_MANAGEMENT_APPROVAL": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?name={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_SERVICE_CATEGORY": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_OMNICHANNEL_CONFIGURATION_WHATSAPP": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_GENERAL_SETTING_GROUP": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CX_PRODUCT": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_GENERAL_TR_DISCUSSION": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?search={}&fields=id,title", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_SALES": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
        "EBESHA_CRM_SETTING_SALES_SLA": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}}'''
        "EBESHA_GENERAL_SETTING_GROUP": {"url": os.environ.get('EBESHA_CRM_SETTING_ORIGIN') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "{}", "access": "read"}},
		"EBESHA_CRM_TR_CASE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,ticket_number", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_TR_CASE", "access": "read"}},
        "EBESHA_CRM_TR_ACCOUNT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_TR_ACCOUNT", "access": "read"}},
        "EBESHA_CRM_SETTING_ACCOUNT_OWNER": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_ACCOUNT_OWNER", "access": "read"}},
        "EBESHA_CRM_TR_CONTACT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_TR_CONTACT", "access": "read"}},
        "EBESHA_CRM_SETTING_ADDITIONAL_DATA": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&additional_field={}&is_active=true&is_delete=false&fields=id,datas", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_ADDITIONAL_DATA", "access": "read"}},
        "EBESHA_CRM_SETTING_ORIGIN": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_ORIGIN", "access": "read"}},
        "EBESHA_CRM_SETTING_PRIORITY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_PRIORITY", "access": "read"}},
        "EBESHA_CRM_SETTING_STATUS": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&order=sequence&sort=ASC&is_active=true&is_delete=false&fields=id,name,sequence,lock,percentage,color,icon", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_STATUS", "access": "read"}},
        "EBESHA_CRM_SETTING_CATEGORY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_CATEGORY", "access": "read"}},
        "EBESHA_CRM_SETTING_SERVICE_CATEGORY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name,parent", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_SERVICE_CATEGORY", "access": "read"}},
        "EBESHA_OMNICHANNEL_SETTING_TEMPLATE_BROADCAST": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&=is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_OMNICHANNEL_SETTING_TEMPLATE_BROADCAST", "access": "read"}},
        "EBESHA_CRM_TR_KNOWLEDGE_MANAGEMENT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_TR_KNOWLEDGE_MANAGEMENT", "access": "read"}},
        "EBESHA_CRM_SETTING_KNOWLEDGE_MANAGEMENT_APPROVAL": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,users", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_KNOWLEDGE_MANAGEMENT_APPROVAL", "access": "read"}},
        "EBESHA_OMNICHANNEL_SETTING_CHATBOT_INTENT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,tag,keyword,type,message,parent", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_OMNICHANNEL_SETTING_CHATBOT_INTENT", "access": "read"}},
        "EBESHA_OMNICHANNEL_CONFIGURATION_WHATSAPP": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,username", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_OMNICHANNEL_CONFIGURATION_WHATSAPP", "access": "read"}},
        "EBESHA_EX_SETTING_POLICY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_POLICY", "access": "read"}},
        "EBESHA_EX_SETTING_STATUS": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_STATUS", "access": "read"}},
        "EBESHA_EX_SETTING_WORKING_DAY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_WORKING_DAY", "access": "read"}},
        "EBESHA_EX_SETTING_PERMIT_TYPE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_PERMIT_TYPE", "access": "read"}},
        "EBESHA_EX_SETTING_LEAVE_TYPE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_LEAVE_TYPE", "access": "read"}},
        "EBESHA_EX_SETTING_LEAVE_RULES": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_LEAVE_RULES", "access": "read"}},
        "EBESHA_EX_SETTING_APPROVAL": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_APPROVAL", "access": "read"}},
        "EBESHA_CRM_SETTING_PROBLEM_TYPE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_PROBLEM_TYPE", "access": "read"}},
        "EBESHA_CRM_SETTING_IMPACT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_IMPACT", "access": "read"}},
        "EBESHA_CRM_SETTING_CHANGE_TYPE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_CHANGE_TYPE", "access": "read"}},
        "EBESHA_CRM_SETTING_RISK": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_RISK", "access": "read"}},
        "EBESHA_CX_PRODUCT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CX_PRODUCT", "access": "read"}},
        "EBESHA_SALES_TR_ACCOUNT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SALES_TR_ACCOUNT", "access": "read"}},
        "EBESHA_SALES_TR_CONTACT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SALES_TR_CONTACT", "access": "read"}},
        "EBESHA_SALES_TR_DEAL": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SALES_TR_DEAL", "access": "read"}},
        "EBESHA_MARKETING_TR_LEAD": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_MARKETING_TR_LEAD", "access": "read"}},
        "EBESHA_CRM_SETTING_INDUSTRY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_INDUSTRY", "access": "read"}},
        "EBESHA_SETTING_GENERAL_CURRENCY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SETTING_GENERAL_CURRENCY", "access": "read"}},
        "EBESHA_SETTING_GENERAL_CITY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SETTING_GENERAL_CITY", "access": "read"}},
        "EBESHA_SETTING_GENERAL_GROUP": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SETTING_GENERAL_GROUP", "access": "read"}},
        "EBESHA_SETTING_GENERAL_PROVINCE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SETTING_GENERAL_PROVINCE", "access": "read"}},
        "EBESHA_SETTING_GENERAL_POSTAL_CODE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,postal_code,description", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SETTING_GENERAL_POSTAL_CODE", "access": "read"}},
        "EBESHA_SETTING_GENERAL_REASON": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SETTING_GENERAL_REASON", "access": "read"}},
        "EBESHA_SETTING_GENERAL_BUSINESS_HOUR": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SETTING_GENERAL_BUSINESS_HOUR", "access": "read"}},
        "EBESHA_OMNICHANNEL_SETTING_DISTRIBUTION_MESSAGE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_OMNICHANNEL_SETTING_DISTRIBUTION_MESSAGE", "access": "read"}},
        "EBESHA_CRM_SETTING_CATEGORY_SALES_KIT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_CATEGORY_SALES_KIT", "access": "read"}},
        "EBESHA_EX_SETTING_CATEGORY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_CATEGORY", "access": "read"}},
        "EBESHA_EX_SETTING_EMPLOYEE_TYPE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_EMPLOYEE_TYPE", "access": "read"}},
        "auth_user_tenant": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/user-management/auth-user-tenants?search={}&view=true", "headers": {"Authorization": "Token {}"}},
        "EBESHA_OMNICHANNEL_EMAIL_LIST": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,mail_from,mail_folder", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_OMNICHANNEL_EMAIL_LIST", "access": "read"}},
        "EBESHA_GENERAL_TR_DISCUSSION": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,title", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_GENERAL_TR_DISCUSSION", "access": "read"}},
        "EBESHA_CRM_SETTING_SALES": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_SALES", "access": "read"}},
        "EBESHA_CRM_SETTING_SALES_SLA": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?search={}&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_SALES_SLA", "access": "read"}}
    }


class MappingRefferenceAPI:
    refference = {
        "tenants": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/user-management/tenants?view=true", "headers": {"Authorization": "Token {}"}},
        "users": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/user-management/users?view=true", "headers": {"Authorization": "Token {}"}},
        "departments": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/user-management/departments?view=true", "headers": {"Authorization": "Token {}"}},
        "EBESHA_CRM_TR_CASE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,ticket_number", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_TR_CASE", "access": "read"}},
        "EBESHA_CRM_TR_ACCOUNT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_TR_ACCOUNT", "access": "read"}},
        "EBESHA_CRM_SETTING_ACCOUNT_OWNER": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_ACCOUNT_OWNER", "access": "read"}},
        "EBESHA_CRM_TR_CONTACT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_TR_CONTACT", "access": "read"}},
        "EBESHA_CRM_SETTING_ADDITIONAL_DATA": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?additional_field={}&is_active=true&is_delete=false&fields=id,datas", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_ADDITIONAL_DATA", "access": "read"}},
        "EBESHA_CRM_SETTING_ORIGIN": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_ORIGIN", "access": "read"}},
        "EBESHA_CRM_SETTING_PRIORITY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_PRIORITY", "access": "read"}},
        "EBESHA_CRM_SETTING_STATUS": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?order=sequence&sort=ASC&is_active=true&is_delete=false&fields=id,name,sequence,lock,percentage,color,icon", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_STATUS", "access": "read"}},
        "EBESHA_CRM_SETTING_CATEGORY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_CATEGORY", "access": "read"}},
        "EBESHA_CRM_SETTING_SERVICE_CATEGORY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&parent=null&fields=id,name,parent", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_SERVICE_CATEGORY", "access": "read"}},
        "EBESHA_OMNICHANNEL_SETTING_TEMPLATE_BROADCAST": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?=is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_OMNICHANNEL_SETTING_TEMPLATE_BROADCAST", "access": "read"}},
        "EBESHA_CRM_TR_KNOWLEDGE_MANAGEMENT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_TR_KNOWLEDGE_MANAGEMENT", "access": "read"}},
        "EBESHA_CRM_SETTING_KNOWLEDGE_MANAGEMENT_APPROVAL": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,users", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_KNOWLEDGE_MANAGEMENT_APPROVAL", "access": "read"}},
        "EBESHA_OMNICHANNEL_SETTING_CHATBOT_INTENT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,tag,keyword,type,message,parent", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_OMNICHANNEL_SETTING_CHATBOT_INTENT", "access": "read"}},
        "EBESHA_OMNICHANNEL_CONFIGURATION_WHATSAPP": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,username", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_OMNICHANNEL_CONFIGURATION_WHATSAPP", "access": "read"}},
        "EBESHA_EX_SETTING_POLICY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_POLICY", "access": "read"}},
        "EBESHA_EX_SETTING_STATUS": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_STATUS", "access": "read"}},
        "EBESHA_EX_SETTING_WORKING_DAY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_WORKING_DAY", "access": "read"}},
        "EBESHA_EX_SETTING_PERMIT_TYPE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_PERMIT_TYPE", "access": "read"}},
        "EBESHA_EX_SETTING_LEAVE_TYPE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_LEAVE_TYPE", "access": "read"}},
        "EBESHA_EX_SETTING_LEAVE_RULES": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_LEAVE_RULES", "access": "read"}},
        "EBESHA_EX_SETTING_APPROVAL": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_APPROVAL", "access": "read"}},
        "EBESHA_CRM_SETTING_PROBLEM_TYPE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_PROBLEM_TYPE", "access": "read"}},
        "EBESHA_CRM_SETTING_IMPACT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_IMPACT", "access": "read"}},
        "EBESHA_CRM_SETTING_CHANGE_TYPE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_CHANGE_TYPE", "access": "read"}},
        "EBESHA_CRM_SETTING_RISK": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_RISK", "access": "read"}},
        "EBESHA_CX_PRODUCT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?parent=null&is_active=true&is_delete=false&fields=id,name,parent", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CX_PRODUCT", "access": "read"}},
        "EBESHA_SALES_TR_ACCOUNT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SALES_TR_ACCOUNT", "access": "read"}},
        "EBESHA_SALES_TR_CONTACT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SALES_TR_CONTACT", "access": "read"}},
        "EBESHA_SALES_TR_DEAL": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SALES_TR_DEAL", "access": "read"}},
        "EBESHA_MARKETING_TR_LEAD": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_MARKETING_TR_LEAD", "access": "read"}},
        "EBESHA_CRM_SETTING_INDUSTRY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_INDUSTRY", "access": "read"}},
        "EBESHA_SETTING_GENERAL_CURRENCY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SETTING_GENERAL_CURRENCY", "access": "read"}},
        "EBESHA_SETTING_GENERAL_CITY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SETTING_GENERAL_CITY", "access": "read"}},
        "EBESHA_SETTING_GENERAL_GROUP": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SETTING_GENERAL_GROUP", "access": "read"}},
        "EBESHA_SETTING_GENERAL_PROVINCE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SETTING_GENERAL_PROVINCE", "access": "read"}},
        "EBESHA_SETTING_GENERAL_POSTAL_CODE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,postal_code,description", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SETTING_GENERAL_POSTAL_CODE", "access": "read"}},
        "EBESHA_SETTING_GENERAL_REASON": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SETTING_GENERAL_REASON", "access": "read"}},
        "EBESHA_SETTING_GENERAL_BUSINESS_HOUR": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_SETTING_GENERAL_BUSINESS_HOUR", "access": "read"}},
        "EBESHA_OMNICHANNEL_SETTING_DISTRIBUTION_MESSAGE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_OMNICHANNEL_SETTING_DISTRIBUTION_MESSAGE", "access": "read"}},
        "EBESHA_CRM_SETTING_CATEGORY_SALES_KIT": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_CATEGORY_SALES_KIT", "access": "read"}},
        "EBESHA_EX_SETTING_CATEGORY": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_CATEGORY", "access": "read"}},
        "EBESHA_EX_SETTING_EMPLOYEE_TYPE": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?is_active=true&is_delete=false&fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_SETTING_EMPLOYEE_TYPE", "access": "read"}},
        "auth_user_tenant": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/user-management/auth-user-tenants?view=true", "headers": {"Authorization": "Token {}"}},
        "EBESHA_OMNICHANNEL_EMAIL_LIST": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,mail_from,mail_folder", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_OMNICHANNEL_EMAIL_LIST", "access": "read"}},
        "EBESHA_GENERAL_TR_DISCUSSION": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,title", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_GENERAL_TR_DISCUSSION", "access": "read"}},
        "EBESHA_CRM_SETTING_SALES": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_SALES", "access": "read"}},
        "EBESHA_CRM_SETTING_SALES_SLA": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_CRM_SETTING_SALES_SLA", "access": "read"}},
        "EBESHA_EX_MS_EMPLOYEES": {"url": os.environ.get('EBESHA_CRM_GATEWAY') + "/dinamic-module/data-lists?fields=id,name", "headers": {"Authorization": "{}"}, "body": {"module": "EBESHA_EX_MS_EMPLOYEES", "access": "read"}}
    }


class Messages:
    success_save_data = "Successfully save data"
    success_update_data = "Successfully update data"
    undifined_message = "Pesan tidak dikenali\r\n"
    failed_convert_case_system = "Failed convert to case, system failure auto generate case, please contact your administrator."
    failed_convert_case = "Sorry, the system is currently under maintenance. Please temporarily contact the agent to make a complaint.\n(Mohon maaf, saat ini sistem sedang dalam pemeliharaan. Untuk sementara silakan menghubungi agent untuk melakukan aduan)"
    new_email = "Successfully update data"
    auto_assign_email = "Omnichannel email has been auto-assigned to you from {}"
    case_auto_generate = "Successfully update data"
    failed_ai_message = "Sorry that Virtual Assistant is currently unavailable, please contact an agent."
    deal_reminder = "Deal Reminder {} has due date in {}"
    success_import = "Success import data <a href='{}'>View Detail</a>"
    deal_assignment = "{} Assign Deals/opti {} to you and has a due date in {}"
    duplicate_data = "Duplicate value, data already exist"
    column_not_exist = "Column doesn't exist"
    table_not_exist = "Table doesn't exist"
    field_not_null = "Please fill the mandatory field"
    syntax_error = "Unable to process the request due to a query syntax error. Please check your search or sorting parameters."
    failed_process = "Failed process"
    activity_assignment = {
        "EBESHA_CRM_TR_ACTIVITY_TASK": "{} create {} with subject {} to you in {} {}-{}", 
        "EBESHA_CRM_TR_ACTIVITY_CALL": "{} create {} with subject {} to you in due date {}{}{}"
    }

class Calendar:
    days = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']


class GroupTypeData:
    character = ["character varying", "Character varying", "text"]
    array = ["ARRAY"]
    date = ["timestamp with time zone", "timestamp without time zone",
            "timestamp", "date", "Timestamp"]


class ConversationType:
    SERVICE = "SERVICE"
    AUTHENTICATION = "AUTHENTICATION"
    MARKETING = "MARKETING"
    UTILITY = "UTILITY"


class AdditionalType:
    Dropdown = "Dropdown"
    Textbox = "Textbox"
    Textarea = "Textarea"
    Number = "Number"

class ActionType:
    ASSIGN = "ASSIGN"
    AUTO_HANDLE = "AUTO HANDLE"
    AUTO_RELEASE = "AUTO RELEASE"
    AUTO_RESOLVED = "AUTO RESOLVED"
    AUTO_GENERATE_CASE = "AUTO GENERATE CASE"
    BROADCAST = "BROADCAST"
    COMPOSE = "COMPOSE"
    HANDLE = "HANDLE"
    RELEASE = "RELEASE"
    REPLY = "REPLY"
    REPLY_ALL = "REPLY ALL"
    FORWARD = "FORWARD"
    LINK_TO_CASE = "LINK TO CASE"
    UNLINK_TO_CASE = "UNLINK TO CASE"
    CONVERT_TO_CASE = "CONVERT TO CASE"
    DELETE = "DELETE"
    INFO = "INFO"
    RESOLVED = "RESOLVED"
    HOLD = "HOLD"

class Email:
    type = {"inbox": "inbox", "send": "send",
            "draft": "draft", "junk": "junk", "trash": "trash"}


class EmailType:
    INBOX = "inbox"
    SEND = "send"
    DRAFT = "draft"
    JUNK = "junk"
    TRASH = "trash"
    ALL = ["inbox","send","draft","junk","trash"]

class MailServiceConstants:
    exchange = 'exchange'
    exchange2013 = 'exchange2013'
    gmail = 'gmail'
    hotmail = 'hotmail'
    imap = 'imap'
    gmail = 'gmail'
    mailru = 'mail.ru'
    office365 = 'office365'
    outlook = 'outlook'
    rediffcom = 'rediff.com'
    yahoo = 'yahoo'
    yandex = 'yandex'
    CHOICES = (
        (exchange, exchange),
        (exchange2013, exchange2013),
        (gmail, gmail),
        (hotmail, hotmail),
        (imap, imap),
        (mailru, mailru),
        (office365, office365),
        (outlook, outlook),
        (rediffcom, rediffcom),
        (yahoo, yahoo),
        (yandex, yandex)
    )

class ErrorWhatsapp:
    whatsapp = {
        '401': 'Invalid credential',
        '406': 'Auth not recognize',
        '407': 'IP Address not allowed',
        '400': 'This message is sent outside of allowed window (24h).',
        '404': 'Resource not found, Could not retrieve phone number from contact store.',
        '605': 'Upload Media Failed.',
        '1009': 'Invalid number of buttons.'
    }


class ErrorFacebook:
    facebook = {
        '401': 'Invalid credential',
        '406': 'Auth not recognize',
        '407': 'IP Address not allowed',
        '400': 'This message is sent outside of allowed window (24h).',
        '404': 'Resource not found, Could not retrieve phone number from contact store.',
        '605': 'Upload Media Failed.',
        '1009': 'Invalid number of buttons.'
    }


class ErrorInstagram:
    instagram = {
        '401': 'Invalid credential',
        '406': 'Auth not recognize',
        '407': 'IP Address not allowed',
        '400': 'This message is sent outside of allowed window (24h).',
        '404': 'Resource not found, Could not retrieve phone number from contact store.',
        '605': 'Upload Media Failed.',
        '1009': 'Invalid number of buttons.'
    }


class ErrorLiveChat:
    live_chat = {
        '401': 'Invalid credential',
        '406': 'Auth not recognize',
        '407': 'IP Address not allowed',
        '400': 'This message is sent outside of allowed window (24h).',
        '404': 'Resource not found, Could not retrieve phone number from contact store.',
        '605': 'Upload Media Failed.',
        '1009': 'Invalid number of buttons.'
    }


class ErrorTelegram:
    telegram = {
        '401': 'Invalid credential',
        '406': 'Auth not recognize',
        '407': 'IP Address not allowed',
        '400': 'This message is sent outside of allowed window (24h).',
        '404': 'Resource not found, Could not retrieve phone number from contact store.',
        '605': 'Upload Media Failed.',
        '1009': 'Invalid number of buttons.'
    }


class ErrorTwitter:
    twitter = {
        '401': 'Invalid credential',
        '406': 'Auth not recognize',
        '407': 'IP Address not allowed',
        '400': 'This message is sent outside of allowed window (24h).',
        '404': 'Resource not found, Could not retrieve phone number from contact store.',
        '605': 'Upload Media Failed.',
        '1009': 'Invalid number of buttons.'
    }


class TransactionHistory:
    JSON_FORMAT = {"message": ""}


class BroadcastType:
    TEXT = 'TEXT'
    IMAGE = 'IMAGE'
    DOCUMENT = 'DOCUMENT'
    VIDEO = 'VIDEO'
    VOICE = 'VOICE'
    AUDIO = 'AUDIO'


class TemplateType:
    DYNAMIC = 'DYNAMIC'
    STATIC = 'STATIC'
    CHOICES = (
        (DYNAMIC, DYNAMIC),
        (STATIC, STATIC)
    )


class StatusTemplate:
    NAME = {'APPROVED': 'Approved', 'NEW': 'New',
            'REJECTED': 'Rejected', 'PENDING': 'Pending'}


class MessageType:
    ERRORS = 'ERRORS'
    TEXT = 'TEXT'
    INTERACTIVE = 'INTERACTIVE'
    INTERACTIVE_BUTTON = 'INTERACTIVE_BUTTON'
    INTERACTIVE_LIST = 'INTERACTIVE_LIST'
    TEXT = 'TEXT'
    ATTACHMENT = 'ATTACHMENT'
    ATTACHMENTS = 'ATTACHMENTS'
    FILE = 'FILE'
    IMAGE = 'IMAGE'
    DOCUMENT = 'DOCUMENT'
    VIDEO = 'VIDEO'
    VOICE = 'VOICE'
    AUDIO = 'AUDIO'
    LOCATION = 'LOCATION'
    CONTACT = 'CONTACT'
    CONTACTS = 'CONTACTS'
    PHOTO = 'PHOTO'
    STORY_MENTION = 'STORY MENTION'
    REPLY_TO = 'REPLY_TO'
    SYSTEM_STORY_MENTION = 'STORY_MENTION'
    ASSIGN = 'ASSIGN'
    STICKER = 'STICKER'
    RESOLVED = 'RESOLVED'
    POSTBACK = 'POSTBACK'
    SHARE = 'SHARE'
    FALLBACK = 'FALLBACK'
    SUMMARY = 'SUMMARY'
    CHOICES = (
        (TEXT, TEXT),
        (INTERACTIVE, INTERACTIVE),
        (INTERACTIVE_LIST, INTERACTIVE_LIST),
        (INTERACTIVE_BUTTON, INTERACTIVE_BUTTON),
        (ATTACHMENT, ATTACHMENT),
        (IMAGE, IMAGE),
        (DOCUMENT, DOCUMENT),
        (VIDEO, VIDEO),
        (VOICE, VOICE),
        (AUDIO, AUDIO),
        (LOCATION, LOCATION),
        (CONTACT, CONTACT),
        (PHOTO, PHOTO),
        (STORY_MENTION, STORY_MENTION),
        (REPLY_TO, REPLY_TO),
        (SYSTEM_STORY_MENTION, SYSTEM_STORY_MENTION),
        (ASSIGN, ASSIGN),
        (STICKER, STICKER),
        (POSTBACK, POSTBACK),
        (SHARE, SHARE),
        (FALLBACK, FALLBACK),
        (RESOLVED, RESOLVED),
        (SUMMARY, SUMMARY),
    )


class PostingType:
    FEED_TEXT = 'FEED_TEXT'
    FEED_VIDEO = 'FEED_VIDEO'
    FEED_PHOTO = 'FEED_PHOTO'
    FEED_REALS = 'FEED_REALS'
    FEED_CAROUSEL = 'FEED_CAROUSEL'
    STORIES_VIDEO = 'STORIES_VIDEO'
    STORIES_PHOTO = 'STORIES_PHOTO'


class CommentType:
    COMMENT_TEXT = 'COMMENT_TEXT'
    COMMENT_VIDEO = 'COMMENT_VIDEO'
    COMMENT_PHOTO = 'COMMENT_PHOTO'


class AiType:
    VANESHA = 'VANESHA'
    GPT_3_5 = 'GPT_3_5'
    GPT_4 = 'GPT_4'
    HUGGING_FACE = 'HUGGING_FACE'
    GEMINI = 'GEMINI'
    AZURE = 'AZURE'


class StatusLevelInitial:
    first_level = ["NEW", "OPEN"]
    process_level = ["IN PROCESS", "IN PROGRESS", "ON PROGRESS", "INPROCESS",
                     "INPROGRESS", "ONPROGRESS", "IN-PROCESS", "IN-PROGRESS", "ON-PROGRESS"]
    hold_level = ["ONHOLD", "ON HOLD", "ON-HOLD", "HOLD", "PENDING"]
    resolved_level = ["RESOLVED", "RESOLVE", "SOLVED"]
    closed_level = ["CLOSE", "CLOSED", "DONE"]


class ModuleName:
    EBESHA_CRM_TR_ACCOUNT = "EBESHA_CRM_TR_ACCOUNT"
    EBESHA_CRM_TR_CONTACT = "EBESHA_CRM_TR_CONTACT"
    EBESHA_CRM_TR_CASE = "EBESHA_CRM_TR_CASE"
    EBESHA_CRM_TR_CASE_HISTORY = "EBESHA_CRM_TR_CASE_HISTORY"
    EBESHA_CRM_TR_ACTIVITY_CALL = "EBESHA_CRM_TR_ACTIVITY_CALL"
    EBESHA_CRM_TR_ACTIVITY_TASK = "EBESHA_CRM_TR_ACTIVITY_TASK"
    EBESHA_CRM_TR_ACTIVITY_NOTE = "EBESHA_CRM_TR_ACTIVITY_NOTE"
    EBESHA_CRM_TR_KNOWLEDGE_MANAGEMENT = "EBESHA_CRM_TR_KNOWLEDGE_MANAGEMENT"
    EBESHA_CRM_TR_KNOWLEDGE_MANAGEMENT_USER_APPROVAL = "EBESHA_CRM_TR_KNOWLEDGE_MANAGEMENT_USER_APPROVAL"
    EBESHA_CRM_SETTING_ACCOUNT_OWNER = "EBESHA_CRM_SETTING_ACCOUNT_OWNER"
    EBESHA_CRM_SETTING_ADDITIONAL_DATA = "EBESHA_CRM_SETTING_ADDITIONAL_DATA"
    EBESHA_CRM_SETTING_ADDITIONAL_FIELD = "EBESHA_CRM_SETTING_ADDITIONAL_FIELD"
    EBESHA_CRM_SETTING_ADDITIONAL_MAPPING = "EBESHA_CRM_SETTING_ADDITIONAL_MAPPING"
    EBESHA_CRM_SETTING_CASE = "EBESHA_CRM_SETTING_CASE"
    EBESHA_CRM_SETTING_CASE_AUTO_GENERATE = "EBESHA_CRM_SETTING_CASE_AUTO_GENERATE"
    EBESHA_CRM_SETTING_CATEGORY = "EBESHA_CRM_SETTING_CATEGORY"
    EBESHA_CRM_SETTING_CATEGORY_SALES_KIT = "EBESHA_CRM_SETTING_CATEGORY_SALES_KIT"
    EBESHA_CRM_SETTING_CHANGE_TYPE = "EBESHA_CRM_SETTING_CHANGE_TYPE"
    EBESHA_CRM_SETTING_GROUP = "EBESHA_CRM_SETTING_GROUP"
    EBESHA_CRM_SETTING_IMPACT = "EBESHA_CRM_SETTING_IMPACT"
    EBESHA_CRM_SETTING_INDUSTRY = "EBESHA_CRM_SETTING_INDUSTRY"
    EBESHA_CRM_SETTING_KNOWLEDGE_MANAGEMENT_APPROVAL = "EBESHA_CRM_SETTING_KNOWLEDGE_MANAGEMENT_APPROVAL"
    EBESHA_CRM_SETTING_ORIGIN = "EBESHA_CRM_SETTING_ORIGIN"
    EBESHA_CRM_SETTING_PRIORITY = "EBESHA_CRM_SETTING_PRIORITY"
    EBESHA_CRM_SETTING_PROBLEM_TYPE = "EBESHA_CRM_SETTING_PROBLEM_TYPE"
    EBESHA_CRM_SETTING_RISK = "EBESHA_CRM_SETTING_RISK"
    EBESHA_CRM_SETTING_STATUS = "EBESHA_CRM_SETTING_STATUS"
    EBESHA_CRM_SETTING_SALES_KIT = "EBESHA_CRM_SETTING_SALES_KIT"
    EBESHA_CRM_SETTING_SERVICE_CATEGORY = "EBESHA_CRM_SETTING_SERVICE_CATEGORY"
    EBESHA_CRM_SETTING_SLA = "EBESHA_CRM_SETTING_SLA"
    EBESHA_CRM_SETTING_SLA_HOLIDAY = "EBESHA_CRM_SETTING_SLA_HOLIDAY"
    EBESHA_CRM_SETTING_SLA_PARAMETER = "EBESHA_CRM_SETTING_SLA_PARAMETER"
    EBESHA_SETTING_GENERAL_CURRENCY = "EBESHA_SETTING_GENERAL_CURRENCY"
    EBESHA_SETTING_GENERAL_CITY = "EBESHA_SETTING_GENERAL_CITY"
    EBESHA_SETTING_GENERAL_DASHBOARD = "EBESHA_SETTING_GENERAL_DASHBOARD"
    EBESHA_SETTING_GENERAL_ESCALATION = "EBESHA_SETTING_GENERAL_ESCALATION"
    EBESHA_SETTING_GENERAL_GROUP = "EBESHA_SETTING_GENERAL_GROUP"
    EBESHA_SETTING_GENERAL_INTEGRATION = "EBESHA_SETTING_GENERAL_INTEGRATION"
    EBESHA_SETTING_GENERAL_INTEGRATION_AUTHENTICATION = "EBESHA_SETTING_GENERAL_INTEGRATION_AUTHENTICATION"
    EBESHA_SETTING_GENERAL_NOTIFICATION = "EBESHA_SETTING_GENERAL_NOTIFICATION"
    EBESHA_SETTING_GENERAL_POSTAL_CODE = "EBESHA_SETTING_GENERAL_POSTAL_CODE"
    EBESHA_SETTING_GENERAL_PROVINCE = "EBESHA_SETTING_GENERAL_PROVINCE"
    EBESHA_SETTING_GENERAL_REASON = "EBESHA_SETTING_GENERAL_REASON"
    EBESHA_SETTING_GENERAL_REPORT = "EBESHA_SETTING_GENERAL_REPORT"
    EBESHA_TR_GENERAL_NOTIFICATION_LIST = "EBESHA_TR_GENERAL_NOTIFICATION_LIST"
    EBESHA_TR_GENERAL_HISTORY = "EBESHA_TR_GENERAL_HISTORY"
    EBESHA_TR_GENERAL_ATTACHMENT = "EBESHA_TR_GENERAL_ATTACHMENT"
    EBESHA_OMNICHANNEL_EMAIL_LIST = "EBESHA_OMNICHANNEL_EMAIL_LIST"
    EBESHA_OMNICHANNEL_CONFIGURATION_EMAIL = "EBESHA_OMNICHANNEL_CONFIGURATION_EMAIL"
    EBESHA_OMNICHANNEL_SESSION_FACEBOOK = "EBESHA_OMNICHANNEL_SESSION_FACEBOOK"
    EBESHA_OMNICHANNEL_USER_FACEBOOK = "EBESHA_OMNICHANNEL_USER_FACEBOOK"
    EBESHA_OMNICHANNEL_CHAT_FACEBOOK = "EBESHA_OMNICHANNEL_CHAT_FACEBOOK"
    EBESHA_OMNICHANNEL_BROADCAST_WHATSAPP = "EBESHA_OMNICHANNEL_BROADCAST_WHATSAPP"
    EBESHA_OMNICHANNEL_CONFIGURATION_FACEBOOK = "EBESHA_OMNICHANNEL_CONFIGURATION_FACEBOOK"
    EBESHA_OMNICHANNEL_SESSION_WHATSAPP = "EBESHA_OMNICHANNEL_SESSION_WHATSAPP"
    EBESHA_OMNICHANNEL_USER_WHATSAPP = "EBESHA_OMNICHANNEL_USER_WHATSAPP"
    EBESHA_OMNICHANNEL_CHAT_WHATSAPP = "EBESHA_OMNICHANNEL_CHAT_WHATSAPP"
    EBESHA_OMNICHANNEL_CONFIGURATION_WHATSAPP = "EBESHA_OMNICHANNEL_CONFIGURATION_WHATSAPP"
    EBESHA_OMNICHANNEL_SESSION_INSTAGRAM = "EBESHA_OMNICHANNEL_SESSION_INSTAGRAM"
    EBESHA_OMNICHANNEL_USER_INSTAGRAM = "EBESHA_OMNICHANNEL_USER_INSTAGRAM"
    EBESHA_OMNICHANNEL_CHAT_INSTAGRAM = "EBESHA_OMNICHANNEL_CHAT_INSTAGRAM"
    EBESHA_OMNICHANNEL_CONFIGURATION_INSTAGRAM = "EBESHA_OMNICHANNEL_CONFIGURATION_INSTAGRAM"
    EBESHA_OMNICHANNEL_SESSION_LIVE_CHAT = "EBESHA_OMNICHANNEL_SESSION_LIVE_CHAT"
    EBESHA_OMNICHANNEL_USER_LIVE_CHAT = "EBESHA_OMNICHANNEL_USER_LIVE_CHAT"
    EBESHA_OMNICHANNEL_CHAT_LIVE_CHAT = "EBESHA_OMNICHANNEL_CHAT_LIVE_CHAT"
    EBESHA_OMNICHANNEL_CONFIGURATION_LIVE_CHAT = "EBESHA_OMNICHANNEL_CONFIGURATION_LIVE_CHAT"
    EBESHA_OMNICHANNEL_GROUPING_LIVE_CHAT = "EBESHA_OMNICHANNEL_GROUPING_LIVE_CHAT"
    EBESHA_OMNICHANNEL_SESSION_TWITTER = "EBESHA_OMNICHANNEL_SESSION_TWITTER"
    EBESHA_OMNICHANNEL_USER_TWITTER = "EBESHA_OMNICHANNEL_USER_TWITTER"
    EBESHA_OMNICHANNEL_CHAT_TWITTER = "EBESHA_OMNICHANNEL_CHAT_TWITTER"
    EBESHA_OMNICHANNEL_MENTION_TWITTER = "EBESHA_OMNICHANNEL_MENTION_TWITTER"
    EBESHA_OMNICHANNEL_CONFIGURATION_TWITTER = "EBESHA_OMNICHANNEL_CONFIGURATION_TWITTER"
    EBESHA_OMNICHANNEL_SESSION_TELEGRAM = "EBESHA_OMNICHANNEL_SESSION_TELEGRAM"
    EBESHA_OMNICHANNEL_USER_TELEGRAM = "EBESHA_OMNICHANNEL_USER_TELEGRAM"
    EBESHA_OMNICHANNEL_CHAT_TELEGRAM = "EBESHA_OMNICHANNEL_CHAT_TELEGRAM"
    EBESHA_OMNICHANNEL_CONFIGURATION_TELEGRAM = "EBESHA_OMNICHANNEL_CONFIGURATION_TELEGRAM"
    EBESHA_OMNICHANNEL_SETTING_DISTRIBUTION_USER_CALCULATE = "EBESHA_OMNICHANNEL_SETTING_DISTRIBUTION_USER_CALCULATE"
    EBESHA_OMNICHANNEL_SETTING_WORKING_HOUR = "EBESHA_OMNICHANNEL_SETTING_WORKING_HOUR"
    EBESHA_OMNICHANNEL_SETTING_AUTO_REPLY = "EBESHA_OMNICHANNEL_SETTING_AUTO_REPLY"
    EBESHA_OMNICHANNEL_SETTING_SUGGESTION_MESSAGE = "EBESHA_OMNICHANNEL_SETTING_SUGGESTION_MESSAGE"
    EBESHA_OMNICHANNEL_SETTING_CHATBOT_INTENT = "EBESHA_OMNICHANNEL_SETTING_CHATBOT_INTENT"
    EBESHA_OMNICHANNEL_SETTING_CHATBOT_RESPONSE = "EBESHA_OMNICHANNEL_SETTING_CHATBOT_RESPONSE"
    EBESHA_OMNICHANNEL_SETTING_TEMPLATE_BROADCAST = "EBESHA_OMNICHANNEL_SETTING_TEMPLATE_BROADCAST"
    EBESHA_OMNICHANNEL_SETTING_TEMPLATE_BROADCAST_SCHEDULER = "EBESHA_OMNICHANNEL_SETTING_TEMPLATE_BROADCAST_SCHEDULER"
    EBESHA_OMNICHANNEL_SETTING_DISTRIBUTION_MESSAGE_ROUTING = "EBESHA_OMNICHANNEL_SETTING_DISTRIBUTION_MESSAGE_ROUTING"
    EBESHA_OMNICHANNEL_SETTING_ASSIGN_GROUP = "EBESHA_OMNICHANNEL_SETTING_ASSIGN_GROUP"
    EBESHA_OMNICHANNEL_SETTING_ASSIGN_GROUP_ACCOUNT = "EBESHA_OMNICHANNEL_SETTING_ASSIGN_GROUP_ACCOUNT"
    EBESHA_OMNICHANNEL_SETTING_ASSIGN_GROUP_DEPARTMENT = "EBESHA_OMNICHANNEL_SETTING_ASSIGN_GROUP_DEPARTMENT"
    EBESHA_OMNICHANNEL_SETTING_DISTRIBUTION_MESSAGE = "EBESHA_OMNICHANNEL_SETTING_DISTRIBUTION_MESSAGE"
    EBESHA_OMNICHANNEL_SETTING_DISTRIBUTION_MESSAGE_ACCOUNT = "EBESHA_OMNICHANNEL_SETTING_DISTRIBUTION_MESSAGE_ACCOUNT"
    EBESHA_OMNICHANNEL_SETTING_DISTRIBUTION_MESSAGE_DEPARTMENT = "EBESHA_OMNICHANNEL_SETTING_DISTRIBUTION_MESSAGE_DEPARTMENT"
    EBESHA_LOG_AUDIT_TRAIL = "EBESHA_LOG_AUDIT_TRAIL"
    EBESHA_LOG_REMOTE_ACCESS = "EBESHA_LOG_REMOTE_ACCESS"
    EBESHA_LOG_SOCMED = "EBESHA_LOG_SOCMED"
    EBESHA_REPORT = "EBESHA_REPORT"
    EBESHA_DASHBOARD = "EBESHA_DASHBOARD"
    EBESHA_EX_SETTING_APPROVAL = "EBESHA_EX_SETTING_APPROVAL"
    EBESHA_EX_SETTING_LEAVE_RULES = "EBESHA_EX_SETTING_LEAVE_RULES"
    EBESHA_EX_SETTING_LEAVE_TYPE = "EBESHA_EX_SETTING_LEAVE_TYPE"
    EBESHA_EX_SETTING_PERMIT_TYPE = "EBESHA_EX_SETTING_PERMIT_TYPE"
    EBESHA_EX_SETTING_POLICY = "EBESHA_EX_SETTING_POLICY"
    EBESHA_EX_SETTING_STATUS = "EBESHA_EX_SETTING_STATUS"
    EBESHA_EX_SETTING_WORKING_DAY = "EBESHA_EX_SETTING_WORKING_DAY"
    EBESHA_EX_MS_EMPLOYEES = "EBESHA_EX_MS_EMPLOYEES"
    EBESHA_EX_TR_PRESENCES = "EBESHA_EX_TR_PRESENCES"
    EBESHA_EX_TR_TASKS = "EBESHA_EX_TR_TASKS"
    EBESHA_EX_TR_OVERTIMES = "EBESHA_EX_TR_OVERTIMES"
    EBESHA_EX_TR_SUMMARY = "EBESHA_EX_TR_SUMMARY"
    EBESHA_EX_TR_PERMIT = "EBESHA_EX_TR_PERMIT"
    EBESHA_EX_TR_LEAVE = "EBESHA_EX_TR_LEAVE"
    EBESHA_EX_TR_HISTORIES_BUCT = "EBESHA_EX_TR_HISTORIES_BUCT"
    EBESHA_SETTING_GENERAL_INTEGRATION_MAPPING = "EBESHA_SETTING_GENERAL_INTEGRATION_MAPPING"
    EBESHA_CRM_TR_SERVICE_INFORMATION = "EBESHA_CRM_TR_SERVICE_INFORMATION"
    EBESHA_CX_BILLING = "EBESHA_CX_BILLING"
    EBESHA_CX_CUSTOMER_SATISFACTION = "EBESHA_CX_CUSTOMER_SATISFACTION"
    EBESHA_CX_NEWS = "EBESHA_CX_NEWS"
    EBESHA_CX_PRODUCT = "EBESHA_CX_PRODUCT"
    EBESHA_CX_PROMOTION = "EBESHA_CX_PROMOTION"
    EBESHA_CX_SUBSCRIBE = "EBESHA_CX_SUBSCRIBE"
    EBESHA_CRM_TR_CHANGE_MANAGEMENT = "EBESHA_CRM_TR_CHANGE_MANAGEMENT"
    EBESHA_CRM_TR_PROBLEM_MANAGEMENT = "EBESHA_CRM_TR_PROBLEM_MANAGEMENT"
    EBESHA_SALES_TR_ACCOUNT = "EBESHA_SALES_TR_ACCOUNT"
    EBESHA_SALES_TR_CONTACT = "EBESHA_SALES_TR_CONTACT"
    EBESHA_SALES_TR_ACHIVEMENT = "EBESHA_SALES_TR_ACHIVEMENT"
    EBESHA_SALES_TR_PERSON_ACHIVEMENT = "EBESHA_SALES_TR_PERSON_ACHIVEMENT"
    EBESHA_SALES_TR_DEAL = "EBESHA_SALES_TR_DEAL"
    EBESHA_SALES_TR_DEAL_HISTORY = "EBESHA_SALES_TR_DEAL_HISTORY"
    EBESHA_MARKETING_TR_ACHIVEMENT = "EBESHA_MARKETING_TR_ACHIVEMENT"
    EBESHA_MARKETING_TR_PERSON_ACHIVEMENT = "EBESHA_MARKETING_TR_PERSON_ACHIVEMENT"
    EBESHA_MARKETING_TR_LEAD = "EBESHA_MARKETING_TR_LEAD"
    EBESHA_MARKETING_TR_LEAD_HISTORY = "EBESHA_MARKETING_TR_LEAD_HISTORY"
    EBESHA_OMNICHANNEL_FEED_FACEBOOK = "EBESHA_OMNICHANNEL_FEED_FACEBOOK"
    EBESHA_OMNICHANNEL_COMMENT_FACEBOOK = "EBESHA_OMNICHANNEL_COMMENT_FACEBOOK"
    EBESHA_OMNICHANNEL_FEED_INSTAGRAM = "EBESHA_OMNICHANNEL_FEED_INSTAGRAM"
    EBESHA_OMNICHANNEL_COMMENT_INSTAGRAM = "EBESHA_OMNICHANNEL_COMMENT_INSTAGRAM"
    EBESHA_OMNICHANNEL_FEED_FACEBOOK_INSIGHTS = "EBESHA_OMNICHANNEL_FEED_FACEBOOK_INSIGHTS"
    EBESHA_OMNICHANNEL_FEED_INSTAGRAM_INSIGHTS = "EBESHA_OMNICHANNEL_FEED_INSTAGRAM_INSIGHTS"
    EBESHA_AI_SETTING_KNOWLEDGE = "EBESHA_AI_SETTING_KNOWLEDGE"
    EBESHA_AI_SETTING_DATABASE = "EBESHA_AI_SETTING_DATABASE"
    EBESHA_SETTING_GENERAL_BUSINESS_HOUR = "EBESHA_SETTING_GENERAL_BUSINESS_HOUR"
    EBESHA_OMNICHANNEL_TELEPHONY = "EBESHA_OMNICHANNEL_TELEPHONY"
    EBESHA_OMNICHANNEL_USER_TELEPHONY = "EBESHA_OMNICHANNEL_USER_TELEPHONY"
    EBESHA_OMNICHANNEL_CHAT_SUMMARY_WHATSAPP = "EBESHA_OMNICHANNEL_CHAT_SUMMARY_WHATSAPP"
    EBESHA_OMNICHANNEL_CHAT_SUMMARY_FACEBOOK = "EBESHA_OMNICHANNEL_CHAT_SUMMARY_FACEBOOK"
    EBESHA_OMNICHANNEL_CHAT_SUMMARY_INSTAGRAM = "EBESHA_OMNICHANNEL_CHAT_SUMMARY_INSTAGRAM"
    EBESHA_OMNICHANNEL_CHAT_SUMMARY_TELEGRAM = "EBESHA_OMNICHANNEL_CHAT_SUMMARY_TELEGRAM"
    EBESHA_OMNICHANNEL_CHAT_SUMMARY_TWITTER = "EBESHA_OMNICHANNEL_CHAT_SUMMARY_TWITTER"
    EBESHA_OMNICHANNEL_CHAT_SUMMARY_LIVE_CHAT = "EBESHA_OMNICHANNEL_CHAT_SUMMARY_LIVE_CHAT"
    EBESHA_SALES_TR_DEAL_ITEM = "EBESHA_SALES_TR_DEAL_ITEM"
    EBESHA_OMNICHANNEL_LOG_TELEPHONY = "EBESHA_OMNICHANNEL_LOG_TELEPHONY"
    EBESHA_OMNICHANNEL_LOG_AGENT = "EBESHA_OMNICHANNEL_LOG_AGENT"
    EBESHA_EX_SETTING_CATEGORY = "EBESHA_EX_SETTING_CATEGORY"
    EBESHA_EX_SETTING_EMPLOYEE_TYPE = "EBESHA_EX_SETTING_EMPLOYEE_TYPE"
    EBESHA_SALES_TR_COMPETITOR = "EBESHA_SALES_TR_COMPETITOR"
    EBESHA_GENERAL_TR_DISCUSSION = "EBESHA_GENERAL_TR_DISCUSSION"
    EBESHA_CRM_SETTING_SALES = "EBESHA_CRM_SETTING_SALES"
    EBESHA_CRM_SETTING_SALES_SLA = "EBESHA_CRM_SETTING_SALES_SLA"

class TransformModuleName:
    TRANSFORM = {
        "EBESHA_CRM_TR_ACCOUNT" : "Account Service",
        "EBESHA_CRM_TR_CONTACT" : "Contact Service",
        "EBESHA_CRM_TR_CASE" : "Case",
        "EBESHA_SALES_TR_DEAL" : "Opportunity",
        "EBESHA_SALES_TR_LEAD" : "Leads",
        "EBESHA_CRM_TR_CASE_HISTORY" : "Case History",
        "EBESHA_CRM_TR_ACTIVITY_CALL" : "Activity Call",
        "EBESHA_CRM_TR_ACTIVITY_TASK" : "Activity Task",
        "EBESHA_CRM_TR_ACTIVITY_NOTE" : "Activity Note",
        "EBESHA_SALES_TR_ACCOUNT" : "Account Sales",
        "EBESHA_SALES_TR_CONTACT" : "Contact Sales"
    }
	
class NotificationFlag:
    AUTO_GENERATE_CASE_SOCMED = "AUTO_GENERATE_CASE_SOCMED"
    CHAT_RESOLVED_WHATSAPP = "CHAT_RESOLVED_WHATSAPP"
    CHAT_RESOLVED_INSTAGRAM = "CHAT_RESOLVED_INSTAGRAM"
    CHAT_RESOLVED_TELEGRAM = "CHAT_RESOLVED_TELEGRAM"
    CHAT_RESOLVED_TWITTER = "CHAT_RESOLVED_TWITTER"
    CHAT_RESOLVED_FACEBOOK = "CHAT_RESOLVED_FACEBOOK"
    CHAT_RESOLVED_LIVE_CHAT = "CHAT_RESOLVED_LIVE_CHAT"
    CHAT_CONFIRM_RESOLVED_WHATSAPP = "CHAT_CONFIRM_RESOLVED_WHATSAPP"
    CHAT_CONFIRM_RESOLVED_INSTAGRAM = "CHAT_CONFIRM_RESOLVED_INSTAGRAM"
    CHAT_CONFIRM_RESOLVED_TELEGRAM = "CHAT_CONFIRM_RESOLVED_TELEGRAM"
    CHAT_CONFIRM_RESOLVED_TWITTER = "CHAT_CONFIRM_RESOLVED_TWITTER"
    CHAT_CONFIRM_RESOLVED_FACEBOOK = "CHAT_CONFIRM_RESOLVED_FACEBOOK"
    CHAT_CONFIRM_RESOLVED_LIVE_CHAT = "CHAT_CONFIRM_RESOLVED_LIVE_CHAT"
    CASE_NOTIFICATION_PUBLIC = "CASE_NOTIFICATION_PUBLIC"
    CX_SUBSCRIPTION_CUSTOMER = "CX_SUBSCRIPTION_CUSTOMER"
    CX_SUBSCRIPTION_PRODUCT = "CX_SUBSCRIPTION_PRODUCT"
    EX_PERMIT_NOTIFICATION_PUBLIC = "EX_PERMIT_NOTIFICATION_PUBLIC"
    EX_PERMIT_NOTIFICATION_APPROVAL_PUBLIC = "EX_PERMIT_NOTIFICATION_APPROVAL_PUBLIC"
    EX_LEAVE_NOTIFICATION_APPROVAL_PUBLIC = "EX_LEAVE_NOTIFICATION_APPROVAL_PUBLIC"
    EX_LEAVE_NOTIFICATION_PUBLIC = "EX_LEAVE_NOTIFICATION_PUBLIC"
    EX_OVERTIME_NOTIFICATION_PUBLIC = "EX_OVERTIME_NOTIFICATION_PUBLIC"
    EX_OVERTIME_NOTIFICATION_APPROVAL_PUBLIC = "EX_OVERTIME_NOTIFICATION_APPROVAL_PUBLIC"
    DEAL_REMINDER_DUE_DATE = "DEAL_REMINDER_DUE_DATE"
    DEAL_ASSIGNMENT = "DEAL_ASSIGNMENT"
    ASSIGN_CASE = "ASSIGN_CASE"
    ACTIVITY_ASSIGNMENT = {
        "EBESHA_CRM_TR_ACTIVITY_TASK":"ACTIVITY_TASK_ASSIGNMENT",
        "EBESHA_CRM_TR_ACTIVITY_CALL":"ACTIVITY_CALL_ASSIGNMENT"
    }

class NotificationEmailEscalation:
    CASE_RESPONSE_TABLE_OPEN = "<table style='font-size: 14px;font-family: arial, sans-serif;border-collapse: collapse;width: 100%;'>"
    CASE_RESPONSE_TABLE_HEADER = "<tr><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: left;padding: 8px;'>Ticket number</th><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: left;padding: 8px;'>Subject</th><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: left;padding: 8px;'>Account</th><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: left;padding: 8px;'>Contact</th><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: left;padding: 8px;'>Status</th><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: left;padding: 8px;'>Date Time</th><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: left;padding: 8px;'>Time Elapsed</th></tr>"
    CASE_RESPONSE_TABLE_BODY = "<tr><td style='border: 1px solid #dddddd;text-align: left;padding: 8px;'>{ticket_number}</td><td style='border: 1px solid #dddddd;text-align: left;padding: 8px;'>{subject}</td><td style='border: 1px solid #dddddd;text-align: left;padding: 8px;'>{account}</td><td style='border: 1px solid #dddddd;text-align: left;padding: 8px;'>{contact}</td><td style='border: 1px solid #dddddd;text-align: left;padding: 8px;'>{status}</td><td style='border: 1px solid #dddddd;text-align: left;padding: 8px;'>{created_date}</td><td style='border: 1px solid #dddddd;text-align: left;padding: 8px;'>{time_elapsed}</td></tr>"
    CASE_RESPONSE_TABLE_CLOSE = "</table>"
    DEAL_REMINDER_TABLE_OPEN = "<table style='font-size: 14px;font-family: arial, sans-serif;border-collapse: collapse;width: 100%;'>"
    DEAL_REMINDER_TABLE_HEADER = "<tr><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: left;padding: 8px;'>Name</th><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: right;padding: 8px;'>Revenue</th><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: left;padding: 8px;'>Account</th><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: left;padding: 8px;'>Contact</th><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: left;padding: 8px;'>Status</th><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: left;padding: 8px;'>Sales Name</th><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: left;padding: 8px;'>Assign To</th><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: left;padding: 8px;'>Due Date</th><th style='background-color: #FFAA06;border: 1px solid #dddddd;text-align: left;padding: 8px;'>Time Elapsed</th></tr>"
    DEAL_REMINDER_TABLE_BODY = "<tr><td style='border: 1px solid #dddddd;text-align: left;padding: 8px;'>{name}</td><td style='border: 1px solid #dddddd;text-align: right;padding: 8px;'>{revenue}</td><td style='border: 1px solid #dddddd;text-align: left;padding: 8px;'>{account}</td><td style='border: 1px solid #dddddd;text-align: left;padding: 8px;'>{contact}</td><td style='border: 1px solid #dddddd;text-align: left;padding: 8px;'>{status}</td><td style='border: 1px solid #dddddd;text-align: left;padding: 8px;'>{sales}</td><td style='border: 1px solid #dddddd;text-align: left;padding: 8px;'>{assign_to}</td><td style='border: 1px solid #dddddd;text-align: left;padding: 8px;'>{due_date}</td><td style='border: 1px solid #dddddd;text-align: left;padding: 8px;'>{time_elapsed}</td></tr>"
    DEAL_REMINDER_TABLE_CLOSE = "</table>"

class IntegrationConstants:
    AI_CONVERSATION_TYPE = {"VANESHA" : "AI_CONVERSATION_VANESHA"}
    AI_HUGGING_FACE_API_INFERENCE = "AI_HUGGING_FACE_API_INFERENCE"
    AI_SUMMARY_CHAT_VANESHA = "AI_SUMMARY_CHAT_VANESHA"
    AI_SUGGESTION_SOLUTION_VANESHA = "AI_SUGGESTION_SOLUTION_VANESHA"
    FACEBOOK_SEND_MESSAGES_TEXT = 'FACEBOOK_SEND_MESSAGES_TEXT'
    FACEBOOK_SEND_MESSAGES_INTERACTIVE_LIST = 'FACEBOOK_SEND_MESSAGES_INTERACTIVE_LIST'
    FACEBOOK_SEND_MESSAGES_INTERACTIVE_BUTTON = 'FACEBOOK_SEND_MESSAGES_INTERACTIVE_BUTTON'
    FACEBOOK_SEND_MESSAGES_ATTACHMENT = 'FACEBOOK_SEND_MESSAGES_ATTACHMENT'
    FACEBOOK_SEND_MESSAGES_IMAGE = 'FACEBOOK_SEND_MESSAGES_IMAGE'
    FACEBOOK_SEND_MESSAGES_FILE = 'FACEBOOK_SEND_MESSAGES_FILE'
    FACEBOOK_SEND_MESSAGES_VIDEO = 'FACEBOOK_SEND_MESSAGES_VIDEO'
    FACEBOOK_SEND_MESSAGES_AUDIO = 'FACEBOOK_SEND_MESSAGES_AUDIO'
    FACEBOOK_POSTING_FEED_TEXT = 'FACEBOOK_POSTING_FEED_TEXT'
    FACEBOOK_POSTING_FEED_IMAGE = 'FACEBOOK_POSTING_FEED_IMAGE'
    FACEBOOK_POSTING_FEED_VIDEO = 'FACEBOOK_POSTING_FEED_VIDEO'
    FACEBOOK_POSTING_STORIES_IMAGE_STEP_1 = 'FACEBOOK_POSTING_STORIES_IMAGE_STEP_1'
    FACEBOOK_POSTING_STORIES_IMAGE_STEP_2 = 'FACEBOOK_POSTING_STORIES_IMAGE_STEP_2'
    FACEBOOK_POSTING_STORIES_VIDEO_STEP_1 = 'FACEBOOK_POSTING_STORIES_VIDEO_STEP_1'
    FACEBOOK_POSTING_STORIES_VIDEO_STEP_2 = 'FACEBOOK_POSTING_STORIES_VIDEO_STEP_2'
    FACEBOOK_POSTING_COMMENT_TEXT = 'FACEBOOK_POSTING_COMMENT_TEXT'
    FACEBOOK_POSTING_COMMENT_IMAGE = 'FACEBOOK_POSTING_COMMENT_IMAGE'
    FACEBOOK_POSTING_COMMENT_VIDEO = 'FACEBOOK_POSTING_COMMENT_VIDEO'
    FACEBOOK_POSTING_INSIGHTS = 'FACEBOOK_POSTING_INSIGHTS'
    TWITTER_SEND_MESSAGES_INTERACTIVE_LIST = 'TWITTER_SEND_MESSAGES_INTERACTIVE_LIST'
    TWITTER_SEND_MESSAGES_INTERACTIVE_BUTTON = 'TWITTER_SEND_MESSAGES_INTERACTIVE_BUTTON'
    TWITTER_SEND_MESSAGES_TEXT = 'TWITTER_SEND_MESSAGES_TEXT'
    TWITTER_SEND_MESSAGES_ATTACHMENT = 'TWITTER_SEND_MESSAGES_ATTACHMENT'
    WHATSAPP_SEND_MESSAGES_INTERACTIVE_BUTTON = 'WHATSAPP_SEND_MESSAGES_INTERACTIVE_BUTTON'
    WHATSAPP_SEND_MESSAGES_INTERACTIVE_LIST = 'WHATSAPP_SEND_MESSAGES_INTERACTIVE_LIST'
    WHATSAPP_SEND_MESSAGES_TEXT = 'WHATSAPP_SEND_MESSAGES_TEXT'
    WHATSAPP_SEND_MESSAGES_DOCUMENT = 'WHATSAPP_SEND_MESSAGES_DOCUMENT'
    WHATSAPP_GENERATE_TOKEN = 'WHATSAPP_GENERATE_TOKEN'
    WHATSAPP_GENERATE_TOKEN_BROADCAST_MESSAGE = 'WHATSAPP_GENERATE_TOKEN_BROADCAST_MESSAGE'
    WHATSAPP_SEND_MESSAGES_IMAGE = 'WHATSAPP_SEND_MESSAGES_IMAGE'
    WHATSAPP_SEND_MESSAGES_VIDEO = 'WHATSAPP_SEND_MESSAGES_VIDEO'
    WHATSAPP_SEND_MESSAGES_AUDIO = 'WHATSAPP_SEND_MESSAGES_AUDIO'
    WHATSAPP_SEND_MESSAGES_VOICE = 'WHATSAPP_SEND_MESSAGES_VOICE'
    WHATSAPP_SEND_MESSAGES_LOCATION = 'WHATSAPP_SEND_MESSAGES_LOCATION'
    WHATSAPP_GET_MEDIA = 'WHATSAPP_GET_MEDIA'
    WHATSAPP_SEND_MESSAGES_BROADCAST_STATIC = 'WHATSAPP_SEND_MESSAGES_BROADCAST_STATIC'
    WHATSAPP_SEND_MESSAGES_BROADCAST_TEXT = 'WHATSAPP_SEND_MESSAGES_BROADCAST_TEXT'
    WHATSAPP_SEND_MESSAGES_BROADCAST_ATTACHMENT = 'WHATSAPP_SEND_MESSAGES_BROADCAST_ATTACHMENT'
    WHATSAPP_GET_PROFILE = 'WHATSAPP_GET_PROFILE'
    WHATSAPP_UPDATE_PROFILE = 'WHATSAPP_UPDATE_PROFILE'
    WHATSAPP_DELETE_PROFILE = 'WHATSAPP_DELETE_PROFILE'
    WHATSAPP_GET_BUSINESS_INFO = 'WHATSAPP_GET_BUSINESS_INFO'
    WHATSAPP_UPDATE_BUSINESS_INFO = 'WHATSAPP_UPDATE_BUSINESS_INFO'
    WHATSAPP_GET_STATUS_TEMPLATE = 'WHATSAPP_GET_STATUS_TEMPLATE'
    WHATSAPP_REQUEST_TEMPLATE_TEXT = 'WHATSAPP_REQUEST_TEMPLATE_TEXT'
    WHATSAPP_REQUEST_TEMPLATE_IMAGE = 'WHATSAPP_REQUEST_TEMPLATE_IMAGE'
    WHATSAPP_UPLOAD_MEDIA = 'WHATSAPP_UPLOAD_MEDIA'
    WHATSAPP_UPLOAD_MEDIA_STEP_1 = 'WHATSAPP_UPLOAD_MEDIA_STEP_1'
    WHATSAPP_UPLOAD_MEDIA_STEP_2 = 'WHATSAPP_UPLOAD_MEDIA_STEP_2'
    FACEBOOK_GET_PROFILE = 'FACEBOOK_GET_PROFILE'
    TWITTER_GET_PROFILE = 'TWITTER_GET_PROFILE'
    TWITTER_UPLOAD_FILE = 'TWITTER_UPLOAD_FILE'
    TWITTER_UPLOAD_MEDIA = 'TWITTER_UPLOAD_MEDIA'
    SDP_CREATE_CASE = 'SDP_CREATE_CASE'
    SDP_UPDATED_CASE = 'SDP_UPDATED_CASE'
    SDP_CLOSE_CASE = 'SDP_CLOSE_CASE'
    SDP_GET_CASE = 'SDP_GET_CASE'
    SDP_GET_REQUEST_TYPE = 'SDP_GET_REQUEST_TYPE'
    SDP_GET_MODE = 'SDP_GET_MODE'
    SDP_GET_IMPACT = 'SDP_GET_IMPACT'
    SDP_GET_LEVEL = 'SDP_GET_LEVEL'
    SDP_GET_URGENCY = 'SDP_GET_URGENCY'
    SDP_GET_DETAIL_CASE = 'SDP_GET_DETAIL_CASE'
    SDP_FILTER_BY = ["MyOpen_Or_Unassigned", "Unassigned_System", "Open_User", "Onhold_User", "Overdue_User", "All_Pending_User",
                     "All_Pending_Requests_Tasks_User", "Due_Today_User", "All_Completed_User", "My_Pending_Approval", "All_User",
                     "Open_System", "Onhold_System", "Overdue_System", "Overdue_System_Today", "Pending_Approval", "All_Pending", "All_Completed", "Waiting_Update",
                     "Updated_By_Me", "All_Requests"]
    TELEGRAM_GET_MEDIA_STEP_1 = 'TELEGRAM_GET_MEDIA_STEP_1'
    TELEGRAM_GET_MEDIA_STEP_2 = 'TELEGRAM_GET_MEDIA_STEP_2'
    TELEGRAM_SEND_MESSAGES_TEXT = 'TELEGRAM_SEND_MESSAGES_TEXT'
    TELEGRAM_SEND_MESSAGES_DOCUMENT = 'TELEGRAM_SEND_MESSAGES_DOCUMENT'
    TELEGRAM_SEND_MESSAGES_IMAGE = 'TELEGRAM_SEND_MESSAGES_IMAGE'
    TELEGRAM_SEND_MESSAGES_VIDEO = 'TELEGRAM_SEND_MESSAGES_VIDEO'
    TELEGRAM_SEND_MESSAGES_AUDIO = 'TELEGRAM_SEND_MESSAGES_AUDIO'
    TELEGRAM_SEND_MESSAGES_VOICE = 'TELEGRAM_SEND_MESSAGES_VOICE'
    TELEGRAM_SEND_MESSAGES_LOCATION = 'TELEGRAM_SEND_MESSAGES_LOCATION'
    TELEGRAM_SEND_MESSAGES_INTERACTIVE_BUTTON = 'TELEGRAM_SEND_MESSAGES_INTERACTIVE_BUTTON'
    TELEGRAM_SEND_MESSAGES_INTERACTIVE_LIST = 'TELEGRAM_SEND_MESSAGES_INTERACTIVE_LIST'
    INSTAGRAM_GET_PROFILE = 'INSTAGRAM_GET_PROFILE'
    INSTAGRAM_GET_MY_PROFILE = 'INSTAGRAM_GET_MY_PROFILE'
    INSTAGRAM_SEND_MESSAGES_TEXT = 'INSTAGRAM_SEND_MESSAGES_TEXT'
    INSTAGRAM_SEND_MESSAGES_INTERACTIVE_BUTTON = 'INSTAGRAM_SEND_MESSAGES_INTERACTIVE_BUTTON'
    INSTAGRAM_SEND_MESSAGES_INTERACTIVE_LIST = 'INSTAGRAM_SEND_MESSAGES_INTERACTIVE_LIST'
    INSTAGRAM_SEND_MESSAGES_AUDIO = 'INSTAGRAM_SEND_MESSAGES_AUDIO'
    INSTAGRAM_SEND_MESSAGES_IMAGE = 'INSTAGRAM_SEND_MESSAGES_IMAGE'
    INSTAGRAM_SEND_MESSAGES_VIDEO = 'INSTAGRAM_SEND_MESSAGES_VIDEO'
    INSTAGRAM_POSTING_FEED_IMAGE_STEP_1 = 'INSTAGRAM_POSTING_FEED_IMAGE_STEP_1'
    INSTAGRAM_POSTING_FEED_IMAGE_STEP_2 = 'INSTAGRAM_POSTING_FEED_IMAGE_STEP_2'
    INSTAGRAM_POSTING_FEED_REALS_STEP_1 = 'INSTAGRAM_POSTING_FEED_REALS_STEP_1'
    INSTAGRAM_POSTING_FEED_REALS_STEP_2 = 'INSTAGRAM_POSTING_FEED_REALS_STEP_2'
    INSTAGRAM_POSTING_FEED_CAROUSEL_IMAGE_STEP_1 = 'INSTAGRAM_POSTING_FEED_CAROUSEL_IMAGE_STEP_1'
    INSTAGRAM_POSTING_FEED_CAROUSEL_REALS_STEP_1 = 'INSTAGRAM_POSTING_FEED_CAROUSEL_REALS_STEP_1'
    INSTAGRAM_POSTING_FEED_CAROUSEL_STEP_2 = 'INSTAGRAM_POSTING_FEED_CAROUSEL_STEP_2'
    INSTAGRAM_POSTING_FEED_CAROUSEL_STEP_3 = 'INSTAGRAM_POSTING_FEED_CAROUSEL_STEP_3'
    INSTAGRAM_POSTING_STORIES_IMAGE_STEP_1 = 'INSTAGRAM_POSTING_STORIES_IMAGE_STEP_1'
    INSTAGRAM_POSTING_STORIES_IMAGE_STEP_2 = 'INSTAGRAM_POSTING_STORIES_IMAGE_STEP_2'
    INSTAGRAM_POSTING_STORIES_VIDEO_STEP_1 = 'INSTAGRAM_POSTING_STORIES_VIDEO_STEP_1'
    INSTAGRAM_POSTING_STORIES_VIDEO_STEP_2 = 'INSTAGRAM_POSTING_STORIES_VIDEO_STEP_2'
    INSTAGRAM_POSTING_COMMENT_TEXT = 'INSTAGRAM_POSTING_COMMENT_TEXT'
    INSTAGRAM_POSTING_COMMENT_REPLY_TEXT = 'INSTAGRAM_POSTING_COMMENT_REPLY_TEXT'
    INSTAGRAM_POSTING_COMMENT_IMAGE = 'INSTAGRAM_POSTING_COMMENT_IMAGE'
    INSTAGRAM_POSTING_COMMENT_VIDEO = 'INSTAGRAM_POSTING_COMMENT_VIDEO'
    INSTAGRAM_POSTING_IMAGE_INSIGHTS = 'INSTAGRAM_POSTING_IMAGE_INSIGHTS'
    INSTAGRAM_POSTING_REALS_INSIGHTS = 'INSTAGRAM_POSTING_REALS_INSIGHTS'
    INSTAGRAM_POSTING_CAROUSEL_INSIGHTS = 'INSTAGRAM_POSTING_CAROUSEL_INSIGHTS'
    TWITTER_REPLY_MENTION_TEXT = "TWITTER_REPLY_MENTION_TEXT"
    TWITTER_REPLY_MENTION_ATTACHMENT = "TWITTER_REPLY_MENTION_ATTACHMENT"
    CHOICES = (
        (FACEBOOK_GET_PROFILE, FACEBOOK_GET_PROFILE),
        (FACEBOOK_SEND_MESSAGES_ATTACHMENT, FACEBOOK_SEND_MESSAGES_ATTACHMENT),
        (FACEBOOK_SEND_MESSAGES_IMAGE, FACEBOOK_SEND_MESSAGES_IMAGE),
        (FACEBOOK_SEND_MESSAGES_FILE, FACEBOOK_SEND_MESSAGES_FILE),
        (FACEBOOK_SEND_MESSAGES_VIDEO, FACEBOOK_SEND_MESSAGES_VIDEO),
        (FACEBOOK_SEND_MESSAGES_AUDIO, FACEBOOK_SEND_MESSAGES_AUDIO),
        (FACEBOOK_SEND_MESSAGES_INTERACTIVE_LIST,
         FACEBOOK_SEND_MESSAGES_INTERACTIVE_LIST),
        (FACEBOOK_SEND_MESSAGES_INTERACTIVE_BUTTON,
         FACEBOOK_SEND_MESSAGES_INTERACTIVE_BUTTON),
        (FACEBOOK_SEND_MESSAGES_TEXT, FACEBOOK_SEND_MESSAGES_TEXT),
        (TWITTER_GET_PROFILE, TWITTER_GET_PROFILE),
        (TWITTER_SEND_MESSAGES_ATTACHMENT, TWITTER_SEND_MESSAGES_ATTACHMENT),
        (TWITTER_SEND_MESSAGES_TEXT, TWITTER_SEND_MESSAGES_TEXT),
        (TWITTER_UPLOAD_FILE, TWITTER_UPLOAD_FILE),
        (TWITTER_SEND_MESSAGES_INTERACTIVE_BUTTON,
         TWITTER_SEND_MESSAGES_INTERACTIVE_BUTTON),
        (TWITTER_SEND_MESSAGES_INTERACTIVE_LIST,
         TWITTER_SEND_MESSAGES_INTERACTIVE_LIST),
        (WHATSAPP_SEND_MESSAGES_DOCUMENT, WHATSAPP_SEND_MESSAGES_DOCUMENT),
        (WHATSAPP_SEND_MESSAGES_TEXT, WHATSAPP_SEND_MESSAGES_TEXT),
        (WHATSAPP_SEND_MESSAGES_INTERACTIVE_BUTTON,
         WHATSAPP_SEND_MESSAGES_INTERACTIVE_BUTTON),
        (WHATSAPP_SEND_MESSAGES_INTERACTIVE_LIST,
         WHATSAPP_SEND_MESSAGES_INTERACTIVE_LIST),
        (WHATSAPP_GENERATE_TOKEN, WHATSAPP_GENERATE_TOKEN),
        (WHATSAPP_GENERATE_TOKEN_BROADCAST_MESSAGE,
         WHATSAPP_GENERATE_TOKEN_BROADCAST_MESSAGE),
        (WHATSAPP_SEND_MESSAGES_IMAGE, WHATSAPP_SEND_MESSAGES_IMAGE),
        (WHATSAPP_SEND_MESSAGES_VIDEO, WHATSAPP_SEND_MESSAGES_VIDEO),
        (WHATSAPP_GET_MEDIA, WHATSAPP_GET_MEDIA),
        (WHATSAPP_SEND_MESSAGES_AUDIO, WHATSAPP_SEND_MESSAGES_AUDIO),
        (WHATSAPP_SEND_MESSAGES_VOICE, WHATSAPP_SEND_MESSAGES_VOICE),
        (WHATSAPP_SEND_MESSAGES_LOCATION, WHATSAPP_SEND_MESSAGES_LOCATION),
        (WHATSAPP_SEND_MESSAGES_BROADCAST_STATIC,
         WHATSAPP_SEND_MESSAGES_BROADCAST_STATIC),
        (WHATSAPP_SEND_MESSAGES_BROADCAST_TEXT,
         WHATSAPP_SEND_MESSAGES_BROADCAST_TEXT),
        (WHATSAPP_SEND_MESSAGES_BROADCAST_ATTACHMENT,
         WHATSAPP_SEND_MESSAGES_BROADCAST_ATTACHMENT),
        (WHATSAPP_GET_PROFILE, WHATSAPP_GET_PROFILE),
        (WHATSAPP_UPDATE_PROFILE, WHATSAPP_UPDATE_PROFILE),
        (WHATSAPP_DELETE_PROFILE, WHATSAPP_DELETE_PROFILE),
        (WHATSAPP_GET_BUSINESS_INFO, WHATSAPP_GET_BUSINESS_INFO),
        (WHATSAPP_UPDATE_BUSINESS_INFO, WHATSAPP_UPDATE_BUSINESS_INFO),
        (SDP_CREATE_CASE, SDP_CREATE_CASE),
        (SDP_UPDATED_CASE, SDP_UPDATED_CASE),
        (SDP_GET_DETAIL_CASE, SDP_GET_DETAIL_CASE),
        (SDP_GET_CASE, SDP_GET_CASE),
        (SDP_GET_REQUEST_TYPE, SDP_GET_REQUEST_TYPE),
        (SDP_GET_MODE, SDP_GET_MODE),
        (SDP_GET_IMPACT, SDP_GET_IMPACT),
        (SDP_GET_LEVEL, SDP_GET_LEVEL),
        (SDP_GET_URGENCY, SDP_GET_URGENCY),
        (TELEGRAM_GET_MEDIA_STEP_1, TELEGRAM_GET_MEDIA_STEP_1),
        (TELEGRAM_GET_MEDIA_STEP_2, TELEGRAM_GET_MEDIA_STEP_2),
        (TELEGRAM_SEND_MESSAGES_TEXT, TELEGRAM_SEND_MESSAGES_TEXT),
        (TELEGRAM_SEND_MESSAGES_DOCUMENT, TELEGRAM_SEND_MESSAGES_DOCUMENT),
        (TELEGRAM_SEND_MESSAGES_IMAGE, TELEGRAM_SEND_MESSAGES_IMAGE),
        (TELEGRAM_SEND_MESSAGES_VIDEO, TELEGRAM_SEND_MESSAGES_VIDEO),
        (TELEGRAM_SEND_MESSAGES_AUDIO, TELEGRAM_SEND_MESSAGES_AUDIO),
        (TELEGRAM_SEND_MESSAGES_VOICE, TELEGRAM_SEND_MESSAGES_VOICE),
        (TELEGRAM_SEND_MESSAGES_LOCATION, TELEGRAM_SEND_MESSAGES_LOCATION),
        (INSTAGRAM_GET_PROFILE, INSTAGRAM_GET_PROFILE),
        (INSTAGRAM_SEND_MESSAGES_TEXT, INSTAGRAM_SEND_MESSAGES_TEXT),
        (INSTAGRAM_SEND_MESSAGES_IMAGE, INSTAGRAM_SEND_MESSAGES_IMAGE),
        (INSTAGRAM_SEND_MESSAGES_VIDEO, INSTAGRAM_SEND_MESSAGES_VIDEO),
        (INSTAGRAM_SEND_MESSAGES_AUDIO, INSTAGRAM_SEND_MESSAGES_AUDIO),
        (INSTAGRAM_SEND_MESSAGES_INTERACTIVE_BUTTON,
         INSTAGRAM_SEND_MESSAGES_INTERACTIVE_BUTTON),
        (INSTAGRAM_SEND_MESSAGES_INTERACTIVE_LIST,
         INSTAGRAM_SEND_MESSAGES_INTERACTIVE_LIST),
        (TWITTER_REPLY_MENTION_TEXT, TWITTER_REPLY_MENTION_TEXT),
        (TWITTER_REPLY_MENTION_ATTACHMENT, TWITTER_REPLY_MENTION_ATTACHMENT)
    )


class ObjectInteractiveSocmeds:
    OBJECT_MESSAGE_INTERACTIVE_BUTTON = '{"type": "reply", "reply": {"id": "btn{num}", "title": "{message}"}}'
    OBJECT_MESSAGE_INTERACTIVE_LIST = '{"id": "list{num}","title": "{message}","description": ""}'
    OBJECT_MESSAGE_INTERACTIVE_BUTTON_FACEBOOK = '{"type":"postback","title":"{message}","payload":"{message}"}'
    OBJECT_MESSAGE_INTERACTIVE_LIST_FACEBOOK = '{"content_type":"text","title":"{message}","payload":"{message}"}'
    OBJECT_MESSAGE_INTERACTIVE_BUTTON_INSTAGRAM = '{"type":"postback","title":"{message}","payload":"{message}"}'
    OBJECT_MESSAGE_INTERACTIVE_LIST_INSTAGRAM = '{"content_type":"text","title":"{message}","payload":"{message}"}'
    OBJECT_MESSAGE_INTERACTIVE_LIST_TWITTER = '{"label": "{message}","description": "{message}","metadata": "{message}"}'
    OBJECT_MESSAGE_INTERACTIVE_BUTTON_TWITTER = '{"label": "{message}","description": "{message}","metadata": "{message}"}'
    OBJECT_MESSAGE_INTERACTIVE_BUTTON_TELEGRAM = '/{message}'
    OBJECT_MESSAGE_INTERACTIVE_LIST_TELEGRAM = '/{message}'

class CustomQuery:
    ModuleName = {
                    'EBESHA_OMNICHANNEL_EMAIL_LIST':'email_group_list.sql'
                 }

class DealStatusReminderExc:
    Status = ['Hold','Close Lost', 'Close Won']
	
class AttributeModuleField:
    FIELD_NAME = {
        "EBESHA_CRM_TR_ACCOUNT" : "name",
        "EBESHA_CRM_TR_CONTACT" : "name",
        "EBESHA_CRM_TR_CASE" : "ticket_number",
        "EBESHA_SALES_TR_DEAL" : "deal_number",
        "EBESHA_SALES_TR_LEAD" : "name",
        "EBESHA_SALES_TR_ACCOUNT" : "name",
        "EBESHA_SALES_TR_CONTACT" : "name"
    }
	
class UMModuleIntegration:
	get_data = ["tenants", "users", "departments"]
