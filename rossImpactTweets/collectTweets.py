# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

import twitter
from urllib import unquote
import io, json
import time

def oauth_login():
    # XXX: Go to http://twitter.com/apps/new to create an app and get values
    # for these credentials that you'll need to provide in place of these
    # empty string values that are defined as placeholders.
    # See https://dev.twitter.com/docs/auth/oauth for more information
    # on Twitter's OAuth implementation.

    CONSUMER_KEY = 'INSERT KEY HERE'
    CONSUMER_SECRET ='INSERT SECRET HERE'
    OAUTH_TOKEN = 'INSERT KEY HERE'
    OAUTH_TOKEN_SECRET = 'INSERT SECRET HERE'

    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                               CONSUMER_KEY, CONSUMER_SECRET)

    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

def save_json(filename, data):
    with io.open('/vagrant/rossImpactTweets/{0}.json'.format(filename),
                 'w', encoding='utf-8') as f:
        f.write(unicode(json.dumps(data, ensure_ascii=False)))

def load_json(filename):
    with io.open('/vagrant/rossImpactTweets/{0}.json'.format(filename),
                 encoding='utf-8') as f:
        return f.read()

def twitter_search(twitter_api, q, max_results=200, **kw):

    # See https://dev.twitter.com/docs/api/1.1/get/search/tweets and
    # https://dev.twitter.com/docs/using-search for details on advanced
    # search criteria that may be useful for keyword arguments

    # See https://dev.twitter.com/docs/api/1.1/get/search/tweets
    search_results = twitter_api.search.tweets(q=q, count=100, **kw)

    statuses = search_results['statuses']

    # Iterate through batches of results by following the cursor until we
    # reach the desired number of results, keeping in mind that OAuth users
    # can "only" make 180 search queries per 15-minute interval. See
    # https://dev.twitter.com/docs/rate-limiting/1.1/limits
    # for details. A reasonable number of results is ~1000, although
    # that number of results may not exist for all queries.

    # Enforce a reasonable limit
    max_results = min(10000, max_results)

    for _ in range(100): # 100*100 = 10000
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError, e: # No more results when next_results doesn't exist
            print "No more results"
            break

        # Create a dictionary from next_results, which has the following form:
        # ?max_id=313519052523986943&q=NCAA&include_entities=1
        kwargs = dict([ kv.split('=')
                        for kv in next_results[1:].split("&") ])

        search_results = twitter_api.search.tweets(**kwargs)
        statuses += search_results['statuses']

        if len(statuses) > max_results:
            print "Hit search limit"
            break

    return statuses

def collectTweets(twitter_api, filename, q, interval):
    while True:
        #Load saved tweets
        savedTweets = json.loads(load_json(filename))

        #Get the id of the most recent saved tweet
        mostRecentTweetID = savedTweets[0]['id']

        #Get an updated list of tweets
        newTweets = twitter_search(twitter_api, q, max_results=10000, since_id=mostRecentTweetID)

        #Combine the new tweets with the list of existing ones
        newTweets.extend(savedTweets)

        print "Last collection: " + str(time.localtime())
        print "Number of tweets collected: %i" % len(newTweets)

        #Save the updated set of tweets
        save_json(filename, newTweets)

        time.sleep(interval)



# <codecell>

#First tweet
firstTweetID = 635820968091471872

twitter_api = oauth_login()

q = "#rossimpact"

# <codecell>

collectTweets(twitter_api, 'rossImpactTweets', q, 60)
