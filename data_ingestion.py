import settings
import requests
import json
import time
import tweepy
import pandas as pd
from requests_oauthlib import OAuth2Session


TWEETS_TO_GET = 1000

def get_linkedin_api_key(scope):
    redirect_uri = settings.LINKEDIN_REDIRECT_URL
    client_id = settings.LINKEDIN_CLIENT_ID
    client_secret = settings.LINKEDIN_CLIENT_SECRET
    linkedin = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    authorization_url, state = linkedin.authorization_url('https://www.linkedin.com/oauth/v2/authorization')
    print (authorization_url)
    authorization_response = input('Enter redirection URL: ')
    token = linkedin.fetch_token('https://www.linkedin.com/oauth/v2/accessToken',
                             authorization_response=authorization_response,
                             include_client_id = True,
                             client_secret=client_secret)
    access_token = token['access_token']
    return access_token

def get_linkedin_data(scope, company_name):
    access_token = get_linkedin_api_key(scope)
    
    # Set the API endpoint and parameters
    endpoint = f"https://api.linkedin.com/rest/organizations?q=vanityName&vanityName={company_name}"

    # Set the headers with your access token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202210",
    }

    # Send the API request and parse the JSON response
    response = requests.get(endpoint, headers=headers)
    data = response.json()

    # Print the name and description of each organization
    for element in data["elements"]:
        name = element["localizedName"]
        description = element["localizedWebsite"]
        
        print(f"Name: {name}")
        print(f"Web: {description}\n")
    return data


def query_tweets(api, query, result_type='mixed'):
    query = query + ' -filter:retweets'

    # Helper function for handling pagination in our search and handle rate limits
    def limit_handled(cursor):
        while True:
            try:
                yield cursor.next()
            except tweepy.TooManyRequests:
                print('Reached rate limite. Sleeping for >15 minutes')
                time.sleep(15 * 61)
            except StopIteration:
                break

    #result_type=mixed: Include both popular and real time results in the response
    #FIXME we are requesting more tweets than returned, we should limit request response
    return limit_handled(tweepy.Cursor(api.search_tweets,
                            q=query,
                            lang=settings.LANGUAGE,
                            result_type=result_type).items(TWEETS_TO_GET))


def extract_useful_data(tweets, tweet_list):
    # https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/api-reference/get-search-tweets#example-response
    for tweet in tweets:
        tweet_dict = {
            'text': tweet.text,
            'user_location': tweet.user.location,
            'date': tweet.created_at,
            'is_popular': tweet.metadata['result_type'] == 'popular',
            'retweets': tweet.retweet_count,
            'favorites': tweet.favorite_count,
            'engagement': tweet.retweet_count+tweet.favorite_count
        }
        if tweet.place is not None:
            tweet_dict['place_fullname'] = tweet.place.full_name
            tweet_dict['country_code'] = tweet.place.country_code
            tweet_dict['country'] = tweet.place.country
            tweet_dict['place_type'] = tweet.place.place_type
            tweet_dict['coordinates'] = tweet.place.bounding_box.coordinates
        tweet_list.append(tweet_dict)


def get_twitter_data(company_name):
    #API limit:  900 requests/15 minutes are allowed
    # Twitter’s standard search API only “searches against a sampling of recent Tweets published in the past 7 days.”
    auth = tweepy.AppAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)

    api = tweepy.API(auth, wait_on_rate_limit=True)
    if not api:
        print("Check you authentication data")

    hashtag_popular_tweets = query_tweets(api, f'#{company_name}', 'popular')
    hashtag_recent_tweets = query_tweets(api, f'#{company_name}', 'recent')
    oficial_popular_mention_tweets = query_tweets(api, f'@{company_name}', 'popular')
    oficial_recent_mention_tweets = query_tweets(api, f'@{company_name}', 'recent')

    tweet_list = []
    extract_useful_data(hashtag_popular_tweets, tweet_list)
    extract_useful_data(hashtag_recent_tweets, tweet_list)
    extract_useful_data(oficial_popular_mention_tweets, tweet_list)
    extract_useful_data(oficial_recent_mention_tweets, tweet_list)
    tweets = pd.DataFrame(tweet_list)
    tweets['norm_engagement'] = (tweets['engagement'] - tweets['engagement'].min())/(tweets['engagement'].max()-tweets['engagement'].min())*10    
    return tweets