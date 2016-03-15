from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from requests.packages.urllib3.exceptions import ProtocolError
import json
import re
import threading
import time
from datetime import datetime as dt
import time

in_size = raw_input("Input the cache size: ")
cache_size=int(in_size)
cache = {}
key = raw_input("Input the keyword: ")

access_token = raw_input("Enter your access token: ")
access_token_secret = raw_input("Enter your access token secret: ")
consumer_key = raw_input("Enter your api key: ")
consumer_secret = raw_input("Enter your api secret: ")

class listener(StreamListener):
    
    def __init__(self):
        self.li = []
        self.tweet = ''
        self.tweet_text = ''
        
    def on_data(self, data):
        #print data
        self.tweet = json.loads(data)
        if('text' in self.tweet):
            self.tweet_text = self.tweet['text']
            self.li = self.tweet_text.split()
            for i in self.li:
                if i in cache:
                    cache[i]=[cache[i][0]+1,time.time()]
                elif(len(cache)<cache_size):
                    cache[i]=[1,time.time()]
                    
                else:
                    for j,v in cache.items():
                        if (v[0]==0):
                            del cache[j]
                            cache[i] = [1,time.time()]
                            break
        #print cache
        #print len(cache)
        return True

    def on_error(self, status):
        print status


def scorer():
    count = 0
    while(True):
        lasttime = time.time()
        for i in cache:
            if(lasttime-cache[i][1]>60):
                cache[i][0]=cache[i][0]-1

        for i, v in cache.items():
            if v[0]<0:
                del cache[i]
                
        if(count%2==0):
            print "Contents of cache are:"
            for i in cache:
                 print i,'\t', cache[i][0]
            count=1
        else:
            count=0    
        time.sleep(30)
        
if __name__=='__main__':
    

    
    access_token = "705794186281242625-BHrd1YCM33bUCSsOMQRZpZ4BIeIGP8b"
    access_token_secret = "lS5XKMxupo9Ml2bYiCborhh76sobS1WjmtqMQYNV71QC5"
    consumer_key = "4Hw7IsUQLoGRvfhZPCOO9bguB"
    consumer_secret = "Mu7scUC4hGKx473uxfnan4joyN3SggZqcg9Ps99KWW9V3dUMEi"
    
    l = listener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token,access_token_secret)
    
    t1 = threading.Thread(target=scorer)
    t1.start()
    
    while True:
        try:
            stream = Stream(auth, l)
            stream.filter(track=[key])
        except ProtocolError:
            print "IncompleteRead. Restarting the stream"
            continue
        except KeyboardInterrupt:
            print "Done. Ending program."
            t1.join()
            stream.disconnect()
            break
