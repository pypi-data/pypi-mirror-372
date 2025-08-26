import logging
import sys

from datetime import datetime
from celery import shared_task
from celery.schedules import crontab
#from celery.task import periodic_task

class WorkerCaseServices(object):
    @shared_task(queue='crm_case', expires=60)
    def create_notification_tasks(ticket_number, data_current_tickets, requester, json_data, token, tenant):
        logging.info("========================== START CREATE NOTIFICATION CASE TASK ==========================")
        from core.logic.case.services import LogicService
        logic_service = LogicService()

        start = datetime.now()
        logging.info(f"CRM CASE : Start queue create_notification_tasks : {start}")
        logic_service.create_notification_process(ticket_number, data_current_tickets, requester, json_data, token, tenant)
        logging.info(f"CRM CASE : End queue create_notification_tasks : {datetime.now()-start}")
        logging.info("=========================== END CREATE NOTIFICATION CASE TASK ===========================")
        return True

class WorkerOmnichannelEmailServices(object):
    @shared_task(queue='omnichannel_email', expires=60)
    def send_to_mail_server(token, module, access, email_config, json_data, full_dir, list_attachment_dir, created_by, requester):
        logging.info("================================ START SEND MAIL PROCESS ================================")
        from integration.third_party.integration import Integration
        integration = Integration(token, module, access)

        start = datetime.now()
        logging.info(f"OMNICHANNEL SEND MAIL : Start queue send_to_mail_server : {start}")
        logging.info(email_config.get('email_username'))
        values = integration.send_to_mail_server(email_config, json_data, full_dir, list_attachment_dir, created_by, requester)
        logging.info(values)
        logging.info(f"OMNICHANNEL SEND MAIL : End queue send_to_mail_server : {datetime.now()-start}")
        logging.info("================================= END SEND MAIL PROCESS =================================")
        return values

class NewObject:
    def __init__(self, data):
        self.data = data
        self.query_params = dict()

class WorkerOmnichannelWhatsappServices(object):
    @shared_task(queue='omnichannel_whatsapp', expires=60)
    def receive_message_v19(configuration, data, tenant, token):
        logging.info("================================ START WA RECEIVE MESSAGE PROCESS ================================")
        from core.callback.v19.services import CallbackService
        #request = dict()
        request = NewObject(data)
        
        callback_service = CallbackService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL WA RECEIVE MESSAGE : Start queue receive_message_v19 : {start}")
        callback_service.receive_message(configuration, data, tenant, token)
        logging.info(f"OMNICHANNEL WA RECEIVE MESSAGE : End queue receive_message_v19 : {datetime.now()-start}")
        logging.info("================================= END WA RECEIVE MESSAGE PROCESS =================================")
        return True
		
    @shared_task(queue='omnichannel_whatsapp', expires=60)
    def receive_message_v2(configuration, data, tenant, token):
        logging.info("================================ START WA RECEIVE MESSAGE PROCESS ================================")
        from core.callback.v2.services import CallbackService
        #request = dict(data=data)
        request = NewObject(data)
        
        callback_service = CallbackService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL WA RECEIVE MESSAGE : Start queue receive_message_v19 : {start}")
        callback_service.receive_message(configuration, data, tenant, token)
        logging.info(f"OMNICHANNEL WA RECEIVE MESSAGE : End queue receive_message_v19 : {datetime.now()-start}")
        logging.info("================================= END WA RECEIVE MESSAGE PROCESS =================================")
        return True
		
    @shared_task(queue='omnichannel_whatsapp', expires=60)
    def save_message_retrieve(configuration, whatsapp_user_id, payload, is_customer, tenant, is_broadcast, requester, token):
        logging.info("================================ START WA SEND MESSAGE PROCESS ================================")
        from core.send.services import SendService
        request = dict()
        send_service = SendService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL WA SEND MESSAGE : Start queue save_message_retrieve : {start}")
        send_service.save_message_retrieve(configuration, whatsapp_user_id, payload, is_customer, tenant, is_broadcast, requester, token)
        logging.info(f"OMNICHANNEL WA SEND MESSAGE : End queue save_message_retrieve : {datetime.now()-start}")
        logging.info("================================= END WA SEND MESSAGE PROCESS =================================")
        return True
		
    @shared_task(queue='omnichannel_whatsapp', expires=60)
    def save_message_notification(configuration, whatsapp_user_id, payload, is_customer, tenant, is_broadcast, requester, token):
        logging.info("================================ START WA SEND MESSAGE NOTIF PROCESS ================================")
        from core.notification.services import SendService
        request = dict()
        send_service = SendService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL WA SEND MESSAGE NOTIF : Start queue save_message_retrieve : {start}")
        send_service.save_message_retrieve(configuration, whatsapp_user_id, payload, is_customer, tenant, is_broadcast, requester, token)
        logging.info(f"OMNICHANNEL WA SEND MESSAGE NOTIF : End queue save_message_retrieve : {datetime.now()-start}")
        logging.info("================================= END WA SEND MESSAGE NOTIF PROCESS =================================")
        return True
		
    @shared_task(queue='omnichannel_whatsapp', expires=60)
    def get_summary_wa(json_data, token, access):
        logging.info("================================= START WA GET SUMMARIES CHAT =================================")
        from core.summary.services import ChatSummaryService
        summary_service = ChatSummaryService()

        start = datetime.now()
        logging.info(f"OMNICHANNEL WA GET SUMMARIES CHAT : Start queue get_summary_wa : {start}")
        summary_service.get_summary_wa(json_data, token, access)
        logging.info(f"OMNICHANNEL WA GET SUMMARIES CHAT : End queue get_summary_wa : {datetime.now()-start}")
        logging.info("================================== END WA GET SUMMARIES CHAT ==================================")
        return True

class WorkerOmnichannelFacebookServices(object):
    @shared_task(queue='omnichannel_facebook', expires=60)
    def receive_message_fb(configuration, data, tenant, token):
        logging.info("================================ START FB RECEIVE MESSAGE PROCESS ================================")
        from core.callback.services import CallbackService
        request = NewObject(data)
        #request = dict()
        callback_service = CallbackService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL FB RECEIVE MESSAGE : Start queue receive_message : {start}")
        callback_service.receive_message(configuration, data, tenant, token)
        logging.info(f"OMNICHANNEL FB RECEIVE MESSAGE : End queue receive_message : {datetime.now()-start}")
        logging.info("================================= END FB RECEIVE MESSAGE PROCESS =================================")
        return True
		
    @shared_task(queue='omnichannel_facebook', expires=60)
    def get_summary_fb(json_data, token, access):
        logging.info("================================= START FB GET SUMMARIES CHAT =================================")
        from core.summary.services import ChatSummaryService
        summary_service = ChatSummaryService()

        start = datetime.now()
        logging.info(f"OMNICHANNEL FB GET SUMMARIES CHAT : Start queue get_summary_fb : {start}")
        summary_service.get_summary_fb(json_data, token, access)
        logging.info(f"OMNICHANNEL FB GET SUMMARIES CHAT : End queue get_summary_fb : {datetime.now()-start}")
        logging.info("================================== END FB GET SUMMARIES CHAT ==================================")
        return True

    @shared_task(queue='omnichannel_facebook', expires=60)
    def save_message_retrieve_fb(configuration, facebook_user_id, payload, is_customer, tenant, is_broadcast, requester, token):
        logging.info("================================ START FB SEND MESSAGE PROCESS ================================")
        from core.send.services import SendService
        request = dict()
        send_service = SendService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL FB SEND MESSAGE : Start queue save_message_retrieve : {start}")
        send_service.save_message_retrieve(configuration, facebook_user_id, payload, is_customer, tenant, is_broadcast, requester, token)
        logging.info(f"OMNICHANNEL FB SEND MESSAGE : End queue save_message_retrieve : {datetime.now()-start}")
        logging.info("================================= END FB SEND MESSAGE PROCESS =================================")
        return True
		
    @shared_task(queue='omnichannel_facebook', expires=60)
    def save_message_notification_fb(configuration, facebook_user_id, payload, is_customer, tenant, is_broadcast, requester, token):
        logging.info("================================ START FB SEND MESSAGE NOTIF PROCESS ================================")
        from core.notification.services import SendService
        request = dict()
        send_service = SendService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL FB SEND MESSAGE NOTIF : Start queue save_message_retrieve : {start}")
        send_service.save_message_retrieve(configuration, facebook_user_id, payload, is_customer, tenant, is_broadcast, requester, token)
        logging.info(f"OMNICHANNEL FB SEND MESSAGE NOTIF : End queue save_message_retrieve : {datetime.now()-start}")
        logging.info("================================= END FB SEND MESSAGE NOTIF PROCESS =================================")
        return True
class WorkerOmnichannelInstagramServices(object):
    @shared_task(queue='omnichannel_instagram', expires=60)
    def receive_message_ig(configuration, data, tenant, token):
        logging.info("================================ START IG RECEIVE MESSAGE PROCESS ================================")
        from core.callback.services import CallbackService
        #request = dict()
        request = NewObject(data)
        callback_service = CallbackService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL IG RECEIVE MESSAGE : Start queue receive_message : {start}")
        callback_service.receive_message(configuration, data, tenant, token)
        logging.info(f"OMNICHANNEL IG RECEIVE MESSAGE : End queue receive_message : {datetime.now()-start}")
        logging.info("================================= END IG RECEIVE MESSAGE PROCESS =================================")
        return True
		
    @shared_task(queue='omnichannel_instagram', expires=60)
    def get_summary_ig(json_data, token, access):
        logging.info("================================= START IG GET SUMMARIES CHAT =================================")
        from core.summary.services import ChatSummaryService
        summary_service = ChatSummaryService()

        start = datetime.now()
        logging.info(f"OMNICHANNEL IG GET SUMMARIES CHAT : Start queue get_summary_ig : {start}")
        summary_service.get_summary_ig(json_data, token, access)
        logging.info(f"OMNICHANNEL IG GET SUMMARIES CHAT : End queue get_summary_ig : {datetime.now()-start}")
        logging.info("================================== END IG GET SUMMARIES CHAT ==================================")
        return True

    @shared_task(queue='omnichannel_instagram', expires=60)
    def save_message_retrieve_ig(configuration, instagram_user_id, payload, is_customer, tenant, is_broadcast, requester, token):
        logging.info("================================ START IG SEND MESSAGE PROCESS ================================")
        from core.send.services import SendService
        request = dict()
        send_service = SendService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL IG SEND MESSAGE : Start queue save_message_retrieve : {start}")
        send_service.save_message_retrieve(configuration, instagram_user_id, payload, is_customer, tenant, is_broadcast, requester, token)
        logging.info(f"OMNICHANNEL IG SEND MESSAGE : End queue save_message_retrieve : {datetime.now()-start}")
        logging.info("================================= END IG SEND MESSAGE PROCESS =================================")
        return True
		
    @shared_task(queue='omnichannel_instagram', expires=60)
    def save_message_notification_ig(configuration, instagram_user_id, payload, is_customer, tenant, is_broadcast, requester, token):
        logging.info("================================ START IG SEND MESSAGE NOTIF PROCESS ================================")
        from core.notification.services import SendService
        request = dict()
        send_service = SendService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL IG SEND MESSAGE NOTIF : Start queue save_message_retrieve : {start}")
        send_service.save_message_retrieve(configuration, instagram_user_id, payload, is_customer, tenant, is_broadcast, requester, token)
        logging.info(f"OMNICHANNEL IG SEND MESSAGE NOTIF : End queue save_message_retrieve : {datetime.now()-start}")
        logging.info("================================= END IG SEND MESSAGE NOTIF PROCESS =================================")
        return True
class WorkerOmnichannelTelegramServices(object):
    @shared_task(queue='omnichannel_telegram', expires=60)
    def receive_message_tg(configuration, data, tenant, token):
        logging.info("================================ START TG RECEIVE MESSAGE PROCESS ================================")
        from core.callback.services import CallbackService
        #request = dict()
        request = NewObject(data)
        callback_service = CallbackService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL TG RECEIVE MESSAGE : Start queue receive_message : {start}")
        callback_service.receive_message(configuration, data, tenant, token)
        logging.info(f"OMNICHANNEL TG RECEIVE MESSAGE : End queue receive_message : {datetime.now()-start}")
        logging.info("================================= END TG RECEIVE MESSAGE PROCESS =================================")
        return True
		
    @shared_task(queue='omnichannel_telegram', expires=60)
    def get_summary_tg(json_data, token, access):
        logging.info("================================= START TG GET SUMMARIES CHAT =================================")
        from core.summary.services import ChatSummaryService
        summary_service = ChatSummaryService()

        start = datetime.now()
        logging.info(f"OMNICHANNEL TG GET SUMMARIES CHAT : Start queue get_summary_tg : {start}")
        summary_service.get_summary_tg(json_data, token, access)
        logging.info(f"OMNICHANNEL TG GET SUMMARIES CHAT : End queue get_summary_tg : {datetime.now()-start}")
        logging.info("================================== END TG GET SUMMARIES CHAT ==================================")
        return True

    @shared_task(queue='omnichannel_telegram', expires=60)
    def save_message_retrieve_tg(configuration, telegram_user_id, payload, is_customer, tenant, is_broadcast, requester, token):
        logging.info("================================ START TG SEND MESSAGE PROCESS ================================")
        from core.send.services import SendService
        request = dict()
        send_service = SendService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL TG SEND MESSAGE : Start queue save_message_retrieve : {start}")
        send_service.save_message_retrieve(configuration, telegram_user_id, payload, is_customer, tenant, is_broadcast, requester, token)
        logging.info(f"OMNICHANNEL TG SEND MESSAGE : End queue save_message_retrieve : {datetime.now()-start}")
        logging.info("================================= END TG SEND MESSAGE PROCESS =================================")
        return True
		
    @shared_task(queue='omnichannel_telegram', expires=60)
    def save_message_notification_tg(configuration, telegram_user_id, payload, is_customer, tenant, is_broadcast, requester, token):
        logging.info("================================ START TG SEND MESSAGE NOTIF PROCESS ================================")
        from core.notification.services import SendService
        request = dict()
        send_service = SendService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL TG SEND MESSAGE NOTIF : Start queue save_message_retrieve : {start}")
        send_service.save_message_retrieve(configuration, telegram_user_id, payload, is_customer, tenant, is_broadcast, requester, token)
        logging.info(f"OMNICHANNEL TG SEND MESSAGE NOTIF : End queue save_message_retrieve : {datetime.now()-start}")
        logging.info("================================= END TG SEND MESSAGE NOTIF PROCESS =================================")
        return True
class WorkerOmnichannelTwitterServices(object):
    @shared_task(queue='omnichannel_twitter', expires=60)
    def receive_message_tw(param, configuration, data, tenant, token):
        logging.info("================================ START TW RECEIVE MESSAGE PROCESS ================================")
        from core.callback.services import CallbackService
        #request = dict()
        request = NewObject(data)
        callback_service = CallbackService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL TW RECEIVE MESSAGE : Start queue receive_message : {start}")
        callback_service.receive_message(param, configuration, data, tenant, token)
        logging.info(f"OMNICHANNEL TW RECEIVE MESSAGE : End queue receive_message : {datetime.now()-start}")
        logging.info("================================= END TW RECEIVE MESSAGE PROCESS =================================")
        return True
		
    @shared_task(queue='omnichannel_twitter', expires=60)
    def get_summary_tw(json_data, token, access):
        logging.info("================================= START TW GET SUMMARIES CHAT =================================")
        from core.summary.services import ChatSummaryService
        summary_service = ChatSummaryService()

        start = datetime.now()
        logging.info(f"OMNICHANNEL TW GET SUMMARIES CHAT : Start queue get_summary_tw : {start}")
        summary_service.get_summary_tw(json_data, token, access)
        logging.info(f"OMNICHANNEL TW GET SUMMARIES CHAT : End queue get_summary_tw : {datetime.now()-start}")
        logging.info("================================== END TW GET SUMMARIES CHAT ==================================")
        return True
		
    @shared_task(queue='omnichannel_twitter', expires=60)
    def save_message_retrieve_tw(configuration, twitter_user_id, payload, is_customer, tenant, is_broadcast, requester, token):
        logging.info("================================ START TW SEND MESSAGE PROCESS ================================")
        from core.send.services import SendService
        request = dict()
        send_service = SendService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL TW SEND MESSAGE : Start queue save_message_retrieve : {start}")
        send_service.save_message_retrieve(configuration, twitter_user_id, payload, is_customer, tenant, is_broadcast, requester, token)
        logging.info(f"OMNICHANNEL TW SEND MESSAGE : End queue save_message_retrieve : {datetime.now()-start}")
        logging.info("================================= END TW SEND MESSAGE PROCESS =================================")
        return True
		
class WorkerOmnichannelLiveChatServices(object):
    @shared_task(queue='omnichannel_live_chat', expires=60)
    def receive_message_lc(configuration, data, tenant, token):
        logging.info("================================ START LC RECEIVE MESSAGE PROCESS ================================")
        from core.callback.services import CallbackService
        #request = dict()
        request = NewObject(data)
        callback_service = CallbackService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL LC RECEIVE MESSAGE : Start queue receive_message : {start}")
        callback_service.receive_message(configuration, data, tenant, token)
        logging.info(f"OMNICHANNEL LC RECEIVE MESSAGE : End queue receive_message : {datetime.now()-start}")
        logging.info("================================= END LC RECEIVE MESSAGE PROCESS =================================")
        return True
		
    @shared_task(queue='omnichannel_live_chat', expires=60)
    def get_summary_lc(json_data, token, access):
        logging.info("================================= START LC GET SUMMARIES CHAT =================================")
        from core.summary.services import ChatSummaryService
        summary_service = ChatSummaryService()

        start = datetime.now()
        logging.info(f"OMNICHANNEL LC GET SUMMARIES CHAT : Start queue get_summary_lc : {start}")
        summary_service.get_summary_lc(json_data, token, access)
        logging.info(f"OMNICHANNEL LC GET SUMMARIES CHAT : End queue get_summary_lc : {datetime.now()-start}")
        logging.info("================================== END LC GET SUMMARIES CHAT ==================================")
        return True
		
    @shared_task(queue='omnichannel_live_chat', expires=60)
    def save_message_retrieve_lc(configuration, live_chat_user_id, payload,  is_customer, is_broadcast, requester, tenant, token, groupings):
        logging.info("================================ START LC SEND MESSAGE PROCESS ================================")
        from core.send.services import SendService
        request = dict()
        send_service = SendService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL LC SEND MESSAGE : Start queue save_message_retrieve : {start}")
        send_service.save_message_retrieve(configuration, live_chat_user_id, payload,  is_customer, is_broadcast, requester, tenant, token, groupings)
        logging.info(f"OMNICHANNEL LC SEND MESSAGE : End queue save_message_retrieve : {datetime.now()-start}")
        logging.info("================================= END LC SEND MESSAGE PROCESS =================================")
        return True
		
    @shared_task(queue='omnichannel_live_chat', expires=60)
    def save_message_notification_lc(configuration, live_chat_user_id, payload,  is_customer, is_broadcast, requester, tenant, token, groupings):
        logging.info("================================ START LC SEND MESSAGE NOTIF PROCESS ================================")
        from core.notification.services import SendService
        request = dict()
        send_service = SendService(request)

        start = datetime.now()
        logging.info(f"OMNICHANNEL LC SEND MESSAGE NOTIF : Start queue save_message_retrieve : {start}")
        send_service.save_message_retrieve(configuration, live_chat_user_id, payload,  is_customer, is_broadcast, requester, tenant, token, groupings)
        logging.info(f"OMNICHANNEL LC SEND MESSAGE NOTIF : End queue save_message_retrieve : {datetime.now()-start}")
        logging.info("================================= END LC SEND MESSAGE NOTIF PROCESS =================================")
        return True
		
class WorkerSalesServices(object):
    @shared_task(queue='ebesha_sales', expires=60)
    def process_import(created_by, module, tenant, token, schema, columns, file):
        logging.info("================================ START PROCESS IMPORT {module} ================================")
        from core.logic.bulk.services import BulkDataService
        bulk_service = BulkDataService(created_by, module, tenant, token)

        start = datetime.now()
        logging.info(f"CRM SALES PROCESS IMPORT : Start queue import data : {start}")
        bulk_service.process_import(schema, columns, file)
        logging.info(f"CRM SALES PROCESS IMPORT : End queue import data : {datetime.now()-start}")
        logging.info("================================= END PROCESS IMPORT {module} =================================")
        return True
		
    @shared_task(queue='ebesha_sales', expires=60)
    def create_task_sales(datas, current_deal, token, tenant):
        logging.info("================================== START PROCESS CREATE TASK ==================================")
        from core.logic.deal.services import DealService
        deal_service = DealService(token, tenant)

        start = datetime.now()
        logging.info(f"CRM SALES PROCESS IMPORT : Start queue import data : {start}")
        deal_service.create_task(datas, current_deal)
        logging.info(f"CRM SALES PROCESS IMPORT : End queue import data : {datetime.now()-start}")
        logging.info("=================================== END PROCESS CREATE TASK ===================================")
        return True
		
class WorkerActivityServices(object):
    @shared_task(queue='crm_activity', expires=60)
    def create_task_activity(datas, current_deal, module, token, tenant):
        logging.info("================================== START PROCESS CREATE TASK ==================================")
        from core.logic.activity.services import ActivityService
        activity_service = ActivityService(module, token, tenant)

        start = datetime.now()
        logging.info(f"CRM ACTIVITY PROCESS IMPORT : Start queue add task : {start}")
        activity_service.create_task(datas, current_deal)
        logging.info(f"CRM ACTIVITY PROCESS IMPORT : End queue add task : {datetime.now()-start}")
        logging.info("=================================== END PROCESS CREATE TASK ===================================")
        return True