# -*- coding: utf-8 -*-
import json
from werkzeug import check_password_hash, generate_password_hash
from .FileDB import *
from .CommonDB import *
from flask import session
PER_PAGE = 10


class MessageDB(CommonDB):
    def __init__( self,table='default',path=None):
        CommonDB.__init__(self,table=table,path=path)       

    def get_message(self,message_id):
        """Get message by id."""
        message = self.r.hgetall('message:%s' % message_id)
        if message:
            #author = self.get_user(message['author_id'])
            #message['email'] = author['email']
            message['username'] = message['author_id']
            message['id'] = message_id
        return message


    def get_messages(self,message_ids):
        """Get message list looked up by message ids."""
        messages = []
        for message_id in message_ids:
            msg = self.get_message(message_id)
            if msg:
                messages.append(msg)
        return messages
        
    def search_messages(self,message_ids,key):
        """Get message list looked up by message ids."""
        messages = []
        for message_id in message_ids:
            msg = self.get_message(message_id)
            if not key or key.lower() in msg['text'].lower():
                if key:
                    msg['text'] = msg['text'].replace(key,'<p style="display:inline;background:yellow;">%s</p>'%key)
                messages.append(msg)
        return messages
        
    def get_public_timeline_messages(self):
        """Get public timeline message list."""
        messages = self.get_messages(self.r.lrange('timeline', 0, PER_PAGE  ))
        return messages


    def get_user_timeline_messages(self,user_id,page=0):
        page = 0 if page < 0 else page
        """Get user time line message list."""
        message_ids = self.r.lrange('user:%s:timeline' % user_id, page*PER_PAGE, PER_PAGE )
        return self.get_messages(message_ids)
        
    def get_user_timeline_messages_count(self,user_id):
        return self.r.len('user:%s:timeline' % user_id)
        
    def search_user_timeline_messages(self,user_id,key):
        message_ids = self.r.lrange('user:%s:timeline' % user_id, 0, 100000)
        return self.search_messages(message_ids, key)


    def add_message_to_public_timeline(self,message_id):
        """Add message id to public timeline messages list."""        
        self.r.lpush('timeline', message_id)   
        #self.r.ltrim('timeline', 0, PER_PAGE - 1)

    
    def add_message_to_user_timeline(self,user_id, message_id):
        """Add message id to user timeline messages list."""
        followee_ids = self.get_followees(user_id)
        for followee_id in followee_ids:
            pass
            #self.r.lpush('user:%s:timeline' % followee_id, message_id)
        self.r.lpush('user:%s:timeline' % user_id, message_id)    
    
    
    
    def delete_message_from_array(self,key,mid):
        msglist = self.r.hgetall(key)
        if mid in msglist:
            msglist.remove(mid)
        for id in msglist:
            if not self.r.has("message:%s" % id):
                msglist.remove(id)
        self.r.set(key,msglist)

        
    def delete_user_message(self,user_id, mid):
        msg = self.get_message(mid)
        if msg:# and msg['username'] == user_id:
            self.r.remove("message:%d" % mid)
            self.delete_message_from_array('user:%s:timeline' % user_id,mid)
            self.delete_message_from_array('timeline',mid)
            
            followee_ids = self.get_followees(user_id)
            for followee_id in followee_ids:
                pass
                #self.delete_message_from_array('user:%s:timeline' % followee_id,mid)
        

    def push_message(self,author_id, text):
        """Add message and return its id."""
        _id = self.r.incr('message_id')
        message_id = 'message:%s' % _id
        self.r.hset(message_id, 'author_id', author_id)
        self.r.hset(message_id, 'text', text)
        self.r.hset(message_id, 'pub_date', time.time())
        return _id


    def get_followees(self,user_id):
        """Get list of user followers."""
        return []
        #return self.r.smembers('user:%s:followees' % user_id)

    def is_following(self,user1, user2):
        #return []
        return self.r.sismember('user:%s:followees' % user1, user2)


    def follow(self,user1, user2):
        """Follow the specified user."""
        self.r.sadd('user:%s:followees' % user1, user2)


    def unfollow(self,user1, user2):
        """Unfollow the specified user."""
        self.r.srem('user:%s:followees' % user1, user2)
    
