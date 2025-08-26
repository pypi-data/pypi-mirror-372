class DinamicPagination(object):
    def generate_previous_page(self, url, parameter, total_record):
        param = ""
        for idx, key in enumerate(dict(parameter)):
            if(key!="gateway"):
                if(key=="page"):
                    if int(parameter.get("page", 1)) == 1:
                        return None
                    else:
                        page = ((int(total_record/int(parameter.get("limit", 10)))) - 1)
                        param += f"{key}={int(parameter.get(key))-1}"
                else:
                    param += f"{key}={parameter.get(key)}"
                param += "&"
        return f"{url}?{self.replace_last(param, '&', '')}"
        
    def generate_next_page(self, url, parameter, total_record):
        param = ""
        for idx, key in enumerate(dict(parameter)):
            if(key!="gateway"):
                if(key=="page"):
                    page = ((total_record/int(parameter.get("limit", 10))))
                    if int(parameter.get(key)) < page:
                        param += f"{key}={int(parameter.get(key))+1}"
                    else:
                        return None
                else:
                    param += f"{key}={parameter.get(key)}"
                param += "&"
        return f"{url}?{self.replace_last(param, '&', '')}"
		
    def replace_last(self, string, find, replace):
        reversed = string[::-1]
        replaced = reversed.replace(find[::-1], replace[::-1], 1)
        return replaced[::-1]
