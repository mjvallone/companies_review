import settings
import requests
import json
import time
import tweepy
import pandas as pd

TWEETS_TO_GET = 10

def get_linkedin_data(company_name):
    return [] #FIXME testing purposes while waiting for api key
    linkedin_api_key='' #TODO waiting for api key approval 
    # Set the API endpoint and parameters
    endpoint = "https://api.linkedin.com/v2/organizationAcls?q=roleAssignee&role=ADMINISTRATOR&projection=(elements*(organization~(localizedName,description)))"
    params = {
        "format": "json"
    }

    # Set the headers with your access token
    headers = {
        "Authorization": f"Bearer {linkedin_api_key}"
    }

    # Send the API request and parse the JSON response
    response = requests.get(endpoint, params=params, headers=headers)
    data = json.loads(response.content)

    # Print the name and description of each organization
    for element in data["elements"]:
        organization = element["organization"]
        name = organization["localizedName"]
        description = organization["description"]

        print(f"Name: {name}")
        print(f"Description: {description}\n")
    return data


def query_tweets(api, query):
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
    return limit_handled(tweepy.Cursor(api.search_tweets,
                            q=query,
                            lang=settings.LANGUAGE,
                            result_type="mixed").items(TWEETS_TO_GET))


def extract_useful_data(tweets, tweet_list):
    # https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/api-reference/get-search-tweets#example-response
    for tweet in tweets:
        tweet_dict = {
            'text': tweet.text,
            'user_location': tweet.user.location,
            'date': tweet.created_at,
            'is_popular': tweet.metadata['result_type'] == 'popular', #could this be a "weight" to be considered?
            'retweets': tweet.retweet_count, #could this be a "weight" to be considered?
            'favorites': tweet.favorite_count, #could this be a "weight" to be considered?
            'location_geo': tweet.geo,
            'location_coord': tweet.coordinates
        }
        tweet_list.append(tweet_dict)


def get_twitter_data(company_name):
    auth = tweepy.AppAuthHandler(settings.TWITTER_CONSUMER_KEY, settings.TWITTER_CONSUMER_SECRET)

    api = tweepy.API(auth, wait_on_rate_limit=True)
    if not api:
        print("Check you authentication data")

    hashtag_tweets = query_tweets(api, f'#{company_name}')
    oficial_mention_tweets = query_tweets(api, f'@{company_name}')

    tweet_list = []
    extract_useful_data(hashtag_tweets, tweet_list)
    extract_useful_data(oficial_mention_tweets, tweet_list)

    return pd.DataFrame(tweet_list)