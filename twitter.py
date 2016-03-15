# A python2 script for processing twitter data

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
# cache is a dictionary. The keys are the words and the values are lists with the count and the timestamp of the word.
# eg : {'India':[1,3812481246.2487]}

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
        
    def on_data(self, data):  # This increments the count of the words as and when they are encountered.
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
        return True

    def on_error(self, status):
        print "Error",status


# This is a function that does the scoring after every thirty seconds and printing after every sixty seconds.
# This function runs in parallel with the stream in a different thread.

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
                
        if(count==2):
            print "Contents of cache are:"
            for i in cache:
                 print i,'\t', cache[i][0]
            count=1
        else:
            count=2

        # the thread waits for 30 seconds before starting again
        # some time has been subtracted below. It is the time taken for scoring the cache.
        if (30-(time.time()-lasttime)>0):
            time.sleep(30-(time.time()-lasttime)) 
        
if __name__=='__main__':

    # The stream runs in the main thread. The scorer runs in a separate thread.
    
    l = listener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token,access_token_secret)
    
    t1 = threading.Thread(target=scorer) # This is the thread running the scorer
    t1.daemon = True 
    t1.start()
    
    # The following is for handling the IncompleteRead error. I am not sure if it works.
    # This also takes care of the keyboard interrupt.
    while True:
        try:
            stream = Stream(auth, l)
            stream.filter(track=[key])
        except ProtocolError:
            print "IncompleteRead. Restarting the stream"
            continue
        except KeyboardInterrupt:
            print "Done. Ending program."
            stream.disconnect()
            break
