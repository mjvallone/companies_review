import re
import pycountry
import numpy as np
import pandas as pd
from wordcloud import STOPWORDS
from transformers import pipeline
from geopy.geocoders import Nominatim

# MODEL_PATH = 'cardiffnlp/twitter-roberta-base-sentiment-latest' #58M tweets english
MODEL_PATH = 'finiteautomata/bertweet-base-sentiment-analysis' #40k tweets english

def analysis_emoji(text):
    # Smile -- :), : ), :-), (:, ( :, (-:, :') , :O
    text = re.sub(r'(:\s?\)|:-\)|\(\s?:|\(-:|:\'\)|:O)', ' positive_emoji ', text)
    # Laugh -- :D, : D, :-D, xD, x-D, XD, X-D
    text = re.sub(r'(:\s?D|:-D|x-?D|X-?D)', ' positive_emoji ', text)
    # Love -- <3, :*
    text = re.sub(r'(<3|:\*)', ' positive_emoji ', text)
    # Wink -- ;-), ;), ;-D, ;D, (;,  (-; , @-)
    text = re.sub(r'(;-?\)|;-?D|\(-?;|@-\))', ' positive_emoji ', text)
    # Sad -- :-(, : (, :(, ):, )-:, :-/ , :-|
    text = re.sub(r'(:\s?\(|:-\(|\)\s?:|\)-:|:-/|:-\|)', ' negative_emoji ', text)
    # Cry -- :,(, :'(, :"(
    text = re.sub(r'(:,\(|:\'\(|:"\()', ' negative_emoji ', text)
    return text


def remove_emojis(text):
    emoj = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"
                      "]+", re.UNICODE)
    return re.sub(emoj, '', text)


def process_data(text):
    text = text.lower()                                             # Lowercases the string
    text = re.sub("@[^\s]+", "", text)                              # Removes usernames
    text = re.sub('RT[\s]+', '', text)                              # Removes RT
    text= re.sub("((www\.[^\s]+)|(https?://[^\s]+))", " ", text)    # Remove URLs
    text = re.sub(r"\d+", " ", str(text))                           # Removes all digits
    text = re.sub("&quot;"," ", text)                               # Remove (&quot;)
    text = re.sub("rt", " ", text)                                  # Remove RT
    text = analysis_emoji(text)                                     # Replaces Emojis  #TODO If we use a HF model we don't need to replace emojis
    text = remove_emojis(text)                                      # Removes all Emojis #TODO If we use a HF model we don't need to remove emojis
    text = re.sub(r"\b[a-zA-Z]\b", "", str(text))                   # Removes all single characters
    text = re.sub(r"[^\w\s]", " ", str(text))                       # Removes all punctuations
    text = re.sub(r"(.)\1+", r"\1\1", text)                         # Convert more than 2 letter repetitions to 2
    text = re.sub(r"\s+", " ", str(text))                           # Replaces double spaces with single space    
    return text


def count_emoji(text):
    positive = len(re.findall(r'positive_emoji', text))
    negative = len(re.findall(r'negative_emoji', text))
    return {'positive': positive, 'negative':negative}


def get_name_from_flag(data):
    return pycountry.countries.get(flag=data).name if pycountry.countries.get(flag=data) else data


dict_countries = {
    'usa': 'us',
    'united states': 'us',
    'us': 'us',
    'u.s.': 'us',
    'united states of america': 'us',
    'estados unidos': 'us',
    'estados unidos de américa': 'us',
    'united kingdom': 'gb',
    'gb': 'gb',
    'great britain': 'gb',
    'britain': 'gb',
    'british isles': 'gb',
    'reino unido': 'gb',
    'gran bretaña': 'gb',
    'england' : 'gb'
} #TODO complete with the most frequent countries names


def unify_countries_name(country_name):
    country_name = country_name.lower()
    if country_name in dict_countries:
        return dict_countries[country_name]
    else:
        return country_name


list_countries = ['USA', 'UK', 'india'] #TODO complete with the most frequent countries


def extract_country(text):
    for country in list_countries:
        pattern = r'\b{}\b'.format(country)
        search_pattern = re.search(pattern, text, flags=re.IGNORECASE)
        return search_pattern.group() if search_pattern else text


def process_location(text):
    if not isinstance(text, str):
        return text
    
    text = get_name_from_flag(text)
    text = unify_countries_name(text)
    text = extract_country(text)
    
    return text


def transform_user_location(data):
    data['user_location_process'] = data['user_location'].apply(lambda x: process_location(x))


def get_lat_lon(country):
    try:
        geolocalizador = Nominatim(user_agent="my_app")
        localizacion = geolocalizador.geocode(country)
        return localizacion.latitude, localizacion.longitude
    except:
        return None, None
   
   
def create_dic_lat_lon(serie):
    list_counties = serie.value_counts().index
    lat_lon = map(get_lat_lon, list_counties)
    return dict(list(zip(list_counties, lat_lon)))


def apply_lat_lon(place, serie):
    countries_lat_lon = create_dic_lat_lon(serie)
    if place in countries_lat_lon:
        return countries_lat_lon[place]
    else:
        return place


def transform_twitter_data(data, use_location = True):
    data.rename(columns={'text': 'original_text'}, inplace=True)
    data['processed_text'] = data['original_text'].apply(lambda x: process_data(x))
    data['emojis'] = data['processed_text'].apply(lambda x: count_emoji(x))
    
    if use_location:
        transform_user_location(data)
        data['lat_lon'] = data['user_location_process'].apply(lambda x: apply_lat_lon(x,data['user_location_process'] if type(x) == str else x))

def get_sentiments(data):
    sentiment_pipeline = pipeline(model=MODEL_PATH)
    sentiments_dict = {
        'POS': 'positive',
        'NEG': 'negative',
        'NEU': 'neutral'
    }
    data['output_clean'] = data['processed_text'].apply(lambda tweet: sentiment_pipeline(tweet))
    data['sentiment_label'] = data['output_clean'].apply(lambda dic: sentiments_dict[dic[0]['label']])
    data['sentiment_score'] = data['output_clean'].apply(lambda dic: dic[0]['score'])
    data.drop(columns=['output_clean'], inplace=True)


def calculate_company_index(data):
    # TODO we should create kind of a formula to calculate company_index
    # should we consider retweets, marked as favorite?
    company_index = 0
    return company_index


def count_words(text, stop_words):
    words_list = text.split()
    words_list = [word for word in words_list if not word in stop_words]
    freq = [words_list.count(w) for w in words_list]
    return dict(list(zip(words_list,freq)))


def count_words_all_texts(serie_text, stop_words):
    text = serie_text.to_list()
    text = ' '.join(text)
    return count_words(text, stop_words)

def sort_df_freq_words(serie_text, stop_words):
    dict_word = count_words_all_texts(serie_text, stop_words)
    df = pd.DataFrame(dict_word.items(), columns=['Word', 'Freq'])
    return df.sort_values('Freq',ascending=False)


def get_ranked_tweets(data, stop_words, filter_condition):
    tweets = data['original_text'][data['sentiment_label']==filter_condition]
    df_tw = sort_df_freq_words(tweets, stop_words)
    df_tw = df_tw[0:10] #FIXME how many should we show?
    df_tw['positive'] = True if filter_condition=='positive' else False
    return df_tw


def get_top_pos_neg_tokens(company_name, data):
    # FIXME from where "https", "co", "RT" came? should we remove them when cleaning data?
    stop_words = company_name.split(' ') + ["co"] + list(STOPWORDS)

    df_positive_tw = get_ranked_tweets(data, stop_words, 'positive')
    df_negative_tw = get_ranked_tweets(data, stop_words, 'negative')

    #TODO is company_name in that ranking? should we remove it?
    top_tokens = pd.concat([df_positive_tw, df_negative_tw])
    return top_tokens


def calculate_data_to_show(company_name, data):
  company_index = calculate_company_index(data)
  top_tw_tokens = get_top_pos_neg_tokens(company_name, data)
  return company_index, top_tw_tokens
