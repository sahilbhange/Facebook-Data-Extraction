# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 15:26:26 2018

@author: sahil
"""

import requests
import json
import sys
import time
import datetime
'''
reloading sys for utf8 encoding is for Python 2.7
This line should be removed for Python 3
In Python 3, we need to specify encoding when open a file
f = open("file.csv", encoding='utf-8')
'''
#reload(sys)
#sys.setdefaultencoding('utf8')

class FacebookScraper:
    '''
    FacebookScraper class to scrape facebook info
    '''

    def __init__(self, token):
        self.token = token

    @staticmethod
    def convert_to_epochtime(date_string):
        '''Enter date_string in 2000-01-01 format and convert to epochtime for GET request'''
        try:
            epoch = int(time.mktime(time.strptime(date_string, '%Y-%m-%d')))
            return epoch
        except ValueError:
            print('Invalid string format. Make sure to use %Y-%m-%d')
            quit()

    def get_feed_data(self, target_page, offset, fields, json_path, date_string):
        """This function will get the feed data"""
        
        url = "https://graph.facebook.com/v2.10/{}/feed".format(target_page)
        param = dict()
        param["access_token"] = self.token
        param["limit"] = "100"
        param["offset"] = offset
        param["fields"] = fields
        param["since"] = self.convert_to_epochtime(date_string)
        #print("PARAMETER---",param)
        #print("URL---",url)
        r = requests.get(url, param)
        data = json.loads(r.text)
        f = open(json_path, "w", encoding='utf-8')  #In Python 3, we need to specify encoding when open a file
        #f = open(json_path, "w") # This code is for python 2.7
        f.write(json.dumps(data, indent=4))
        print("json file has been generated")

        f.close()

        return data
   
    def create_table(self, list_rows, file_path, page_name, table_name):
        '''This method will create a table according to header and table name'''

        if table_name == "feed" :
            header = ["page_name", "id", "type", "created_time", "message", "lifetime_post_impressions", "lifetime_post_impressions_unique", "lifetime_post_consumptions", "lifetime_post_consumptions_unique", "name", "description", "actions_name", "share_count", "comment_count", "like_count", "sad_count", "wow_count", "love_count", "haha_count", "angry_count"]
        elif table_name == "comment_replies":
            header = ["page_name", "parent_comment_id", "parent_comment_message", "reply_comment_message", "comment_id", "created_time", "comment_like_cnt"]
        elif table_name == "comments":
            header = ["page_name", "post_id", "created_time", "message", "reply_cmt_cnt", "comments_like_cnt", "comment_haha_cnt", "comment_sad_cnt", "comment_wow_cnt", "comment_love_cnt", "comment_angry_cnt", "message_id"]
            print("Specified table name is not valid.")
        else:
            quit()

        file = open(file_path, 'w',encoding='utf-8')
        #file = open(file_path, 'w')
        file.write(','.join(header) + '\n')
        for i in list_rows:
            file.write('"' + page_name + '",')
            for j in range(len(i)):
                row_string = ''
                if j < len(i) -1 :
                    row_string += '"' + str(i[j]).replace('"', '').replace('\n', '') + '"' + ','
                else:
                    row_string += '"' + str(i[j]).replace('"', '').replace('\n', '') + '"' + '\n'
                file.write(row_string)
        file.close()
        print("Generated {} table csv File for {}".format(table_name, page_name))

    def convert_feed_data(self, response_json_list):
        '''This method takes response json data and convert to csv'''
        print("convert_feed_data-----")
        list_all = []
        for response_json in response_json_list:
            data = response_json["data"]
            #print("FEED data--",data)
            for i in range(len(data)):
                list_row = []
                row = data[i]
                id = row["id"]
                try:
                    type = row["type"]
                except KeyError:
                    type = ""
                try:
                    created_time = row["created_time"]
                except KeyError:
                    created_time = ""
                try:
                    message = row["message"]
                except KeyError:
                    message = ""                   
                try:
                    lifetime_post_impressions = row["insights"]["data"][0]["values"][0]["value"]
                except KeyError:
                    lifetime_post_impressions = ""      
                try:
                    lifetime_post_impressions_unique = row["insights"]["data"][1]["values"][0]["value"]
                except KeyError:
                    lifetime_post_impressions_unique = ""
                try:
                    lifetime_post_consumptions = row["insights"]["data"][2]["values"][0]["value"]
                except KeyError:
                    lifetime_post_consumptions = ""    
                try:
                    lifetime_post_consumptions_unique = row["insights"]["data"][3]["values"][0]["value"]
                except KeyError:
                    lifetime_post_consumptions_unique = ""  
                try:
                    name = row["name"]
                except KeyError:
                    name = ""
                try:
                    description = row["description"]
                except KeyError:
                    description = ""
                try:
                    actions_link = row["actions"][0]["link"]
                except KeyError:
                    actions_link = ""
                try:
                    share_count = row["shares"]["count"]
                except KeyError:
                    share_count = ""
                try:
                    comment_count = row["comments"]["summary"]["total_count"]
                except KeyError:
                    comment_count = ""
                try:
                    like_count = row["likes"]["summary"]["total_count"]
                except KeyError:
                    like_count = ""
                try:
                    sad_count = row["sad"]["summary"]["total_count"]
                except KeyError:
                    sad_count = ""                    
                try:
                    wow_count = row["wow"]["summary"]["total_count"]
                except KeyError:
                    wow_count = ""
                try:
                    love_count = row["love"]["summary"]["total_count"]
                except KeyError:
                    love_count = ""
                try:
                    haha_count = row["haha"]["summary"]["total_count"]
                except KeyError:
                    haha_count = ""
                try:
                    angry_count = row["angry"]["summary"]["total_count"]
                except KeyError:
                    angry_count = ""               
               
                list_row.extend((id, type, created_time, message,lifetime_post_impressions,lifetime_post_impressions_unique,lifetime_post_consumptions,lifetime_post_consumptions_unique, name,description, actions_link, share_count, comment_count, like_count,sad_count,wow_count,love_count,haha_count,angry_count))
                list_all.append(list_row)
       
        return list_all

    def convert_comments_data(self, response_json_list):
        '''Function to extract post comment data'''
        list_all = []
        for response_json in response_json_list:
            data = response_json["data"]
            # like_list = []
            for i in range(len(data)):
                #print("datalen--",len(data))
                row = data[i]
                post_id = row["id"]
                try:
                   comment_count = row["comments"]["summary"]["total_count"]
                   #print("comment_count---",comment_count)
                except KeyError:
                    comment_count = 0
                if comment_count > 0:
                    comments = row["comments"]["data"]
                    for comment in comments:
                        row_list = []
                        created_time = comment["created_time"]
                        message = comment["message"].encode('latin1', 'ignore')
                        reply_cmt_cnt=comment["comment_count"]                        
                        comment_like_cnt = comment["like_count"]
                        comment_haha_cnt = comment["haha"]["summary"]["total_count"]
                        comment_sad_cnt = comment["sad"]["summary"]["total_count"]
                        comment_wow_cnt = comment["wow"]["summary"]["total_count"]
                        comment_love_cnt = comment["love"]["summary"]["total_count"]
                        comment_angry_cnt = comment["angry"]["summary"]["total_count"]                        
                        message_id = comment["id"]
                        row_list.extend((post_id, created_time, message,\
                        reply_cmt_cnt,comment_like_cnt,comment_haha_cnt,comment_sad_cnt,comment_wow_cnt,comment_love_cnt,comment_angry_cnt,message_id))
                        #print(row_list)
                        list_all.append(row_list)
               
                # Check if the next link exists
                try:
                    next_link = row["comments"]["paging"]["next"]
                    print("Next link for comments data")
                except KeyError:
                    next_link = None
                    continue
               
                if next_link is not None:
                    r = requests.get(next_link.replace("limit=200", "limit=200"))
                    comments_data = json.loads(r.text)
                    while True:
                        for i in range(len(comments_data["data"])):
                            row_list = []
                            comment = comments_data["data"][i]
                            created_time = comment["created_time"]
                            message = comment["message"].encode('latin1', 'ignore')
                            reply_cmt_cnt=comment["comment_count"]                            
                            comment_like_cnt = comment["like_count"]
                            comment_haha_cnt = comment["haha"]["summary"]["total_count"]                            
                            comment_sad_cnt = comment["sad"]["summary"]["total_count"]
                            comment_wow_cnt = comment["wow"]["summary"]["total_count"]
                            comment_love_cnt = comment["love"]["summary"]["total_count"]
                            comment_angry_cnt = comment["angry"]["summary"]["total_count"]                                                    
                            message_id = comment["id"]
                            row_list.extend((post_id, created_time, message,\
                            reply_cmt_cnt,comment_like_cnt,comment_haha_cnt,comment_sad_cnt,comment_wow_cnt,comment_love_cnt,comment_angry_cnt,message_id))
                            list_all.append(row_list)
                        try:
                            next = comments_data["paging"]["next"]
                            r = requests.get(next.replace("limit=200", "limit=200"))
                            comments_data = json.loads(r.text)
                        except KeyError:
                            break
        return list_all
   
    def convert_comment_replies_data(self, response_json_list):
        '''This will get the replies to the comments posted on FB'''
        print("convert_comment_replies_data-----")
        list_all = []
        for response_json in response_json_list:
            data = response_json["data"]
            #print("data len---",len(data))
        for i in range(len(data)):
            row = data[i]
            comments=row["comments"]["data"]
            for j in range(len(comments)):
                cmt_data=comments[j]
                try:
                    comment_count=cmt_data["comment_count"]
                except KeyError:
                    comment_count = 0                
                if comment_count > 0:
                    #print("comment_count",comment_count)
                    try:
                        reply_cmt = cmt_data["comments"]["data"]
                    except:
                        print("Breaking loop out of reply cmt")
                        break
                    for k in range(len(reply_cmt)):
                        #print("Reply comment message--",reply_cmt[k]["message"])     
                        row_list = []
                        parent_comment_id = cmt_data["id"]
                        parent_comment_message = cmt_data["message"]
                        reply_comment_message = reply_cmt[k]["message"]
                        comment_id = reply_cmt[k]["id"]
                        created_time = reply_cmt[k]["created_time"]
                        comment_like_cnt = reply_cmt[k]["like_count"]

                        row_list.extend((parent_comment_id, parent_comment_message, reply_comment_message,comment_id,created_time,comment_like_cnt))                     
                        list_all.append(row_list)
               
                # Check if the next link exists
                try:
                    next_link = cmt_data["comments"]["paging"]["next"]
                except KeyError:
                    next_link = None
                    continue
                else:
                    print("No reply comments in the post")
                    break
                
                if next_link is not None:
                    r = requests.get(next_link.replace("limit=100", "limit=100"))
                    comments_data = json.loads(r.text)
                    while True:
                        for i in range(len(comments_data["data"])):
                            row_list = []
                            #comment = comments_data["data"][i]
                            #print("Next loop comment data",comment)
                            print("Next loop reply comment data ")
                            parent_comment_id = cmt_data["id"]
                            parent_comment_message = cmt_data["message"]
                            reply_comment_message = reply_cmt[k]["message"]
                            comment_id = reply_cmt[k]["id"]
                            created_time = reply_cmt[k]["created_time"]
                            comment_like_cnt = reply_cmt[k]["like_count"]
                            row_list.extend((parent_comment_id, parent_comment_message, reply_comment_message,comment_id,created_time,comment_like_cnt))                     
                            list_all.append(row_list)
                        try:
                            next = comments_data["paging"]["next"]
                            r = requests.get(next.replace("limit=100", "limit=100"))
                            comments_data = json.loads(r.text)
                        except KeyError:
                            #print("Comments for the post {} completed".format(post_id))
                            break 
        return list_all

if __name__ == "__main__":
    now = datetime.datetime.now()
    current_day=now.strftime("%Y%m%d")
#    token_input = sys.argv[1]
    #target_page_input = sys.argv[1]
    #date_since_input = sys.argv[2]
    token_input = 'EAACEdEose0cBAONZArWfcY6D9c8NnoAkCa5rsiyQWLfhLUZBgeyK0QdFBstiAf9ILJNgk44EgccBQmm08iJ1GvphMV1JRj2ejepFhJfT9odBo2mUERZCIGOZCdxqu2ZA4OxJKNjZCGRU4wBWuZATcnq395mt0GKGB8Tr1ljDftG0OeP9RK45GKRspGI3SYL51916FbfKxQTSgZDZD'
    target_page_input = 'MITSARutgers'
    date_since_input = '2017-01-01'
    json_path_input = target_page_input+"_data_"+current_day+".json"
    csv_feed_path_input = target_page_input+"_feed_"+current_day+".csv"
    csv_reply_comment_path_input = target_page_input+"_reply_comments_"+current_day+".csv"
    csv_comments_path_input = target_page_input+"_post_comments_"+current_day+".csv"

    # Get request parameters 
    field_input='id,created_time,name,message,insights.metric(post_impressions,post_impressions_unique,post_consumptions,post_consumptions_unique),comments.summary(true).limit(200){created_time,message,reactions.type(SAD).summary(1).as(sad),reactions.type(WOW).summary(1).as(wow),reactions.type(LOVE).summary(1).as(love),reactions.type(HAHA).summary(1).as(haha),reactions.type(ANGRY).summary(1).as(angry),id,like_count,comment_count,comments.limit(200){message,created_time,like_count,comments.limit(200),reactions.type(SAD).summary(1).as(sad),reactions.type(WOW).summary(1).as(wow),reactions.type(LOVE).summary(1).as(love),reactions.type(HAHA).summary(1).as(haha),reactions.type(ANGRY).summary(1).as(angry)}},shares,type,link,actions,place,targeting,feed_targeting,scheduled_publish_time,backdated_time,description,likes.summary(true),reactions.type(SAD).summary(1).as(sad),reactions.type(WOW).summary(1).as(wow),reactions.type(LOVE).summary(1).as(love),reactions.type(HAHA).summary(1).as(haha),reactions.type(ANGRY).summary(1).as(angry)'

    fb = FacebookScraper(token_input)
    
    print("Get request parameters--",field_input)

    offset = 0
    json_list = []
    while True:
        path = str(offset) + "_" + json_path_input
        #print("path--",path)
        try:
            data = fb.get_feed_data(target_page_input, str(offset), field_input, path, date_since_input)
            check = data['data']
            if (len(check) >= 100):
                json_list.append(data)
                offset += 100
                print("Offset--",offset)
            else:
                json_list.append(data)
                print("End of loop for obtaining more than 100 feed records.")
                break
        except KeyError:
            print("Error with get request.")
            quit()
    
    print("Create feed table")    
    feed_table_list = fb.convert_feed_data(json_list)
    print(feed_table_list[0])
    fb.create_table(feed_table_list, csv_feed_path_input, target_page_input, "feed")
    print("Feed generated")    
    
    print("Create Comment table")
    comments_table_list = fb.convert_comments_data(json_list)
    print(comments_table_list[0])
    fb.create_table(comments_table_list, csv_comments_path_input, target_page_input, "comments")
    print("comments_table_list generated")
    
    print("Create Comment replies table")
    comment_replies_list = fb.convert_comment_replies_data(json_list)
    print(comment_replies_list[0])
    fb.create_table(comment_replies_list, csv_reply_comment_path_input, target_page_input, "comment_replies")
    print("comments_table_list generated")
