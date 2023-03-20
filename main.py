import streamlit as st
import matplotlib.pyplot as plt
from streamlit_folium import folium_static
from data_ingestion import get_twitter_data
from data_visualization import select_data, create_map
from data_transformation import transform_twitter_data, get_sentiments, calculate_data_to_show


def update_progress_bar(progress_bar, progress, text):
  progress_bar.progress(progress, text=text)


def ingest_data(progress_bar, company_name):
  update_progress_bar(progress_bar, 15, "Getting Twitter data...")
  twitter_data = get_twitter_data(company_name)
  update_progress_bar(progress_bar, 25, f"{len(twitter_data)} posts obtained from Twitter")
  return twitter_data


def clean_and_transform_data(progress_bar, twitter_data):
  # TODO I've seen company's ads or claims in tweets, should we clean them?
  # e.g. @amazon i want to return my product boat smart watch pls help this is my register no.8787042107
  # Amazon Free Same Day Delivery and Free One Day  with Amazon Prime.  Learn More Here. https://t.co/9Up3AX0sua via @amazon
  transform_twitter_data(twitter_data)

  update_progress_bar(progress_bar, 35, "Getting sentiments.. this may take a while")
  get_sentiments(twitter_data)

  update_progress_bar(progress_bar, 60, "Transforming data")
  
  return twitter_data


def show_data(twitter_data):
  # comment it once we are not in "dev mode"
  with st.expander("See Twitter data"):
    st.dataframe(twitter_data)
 
  st.header("Twitter sentiments pie diagram")
  fig1, ax1 = plt.subplots()
  ax1.pie(
    twitter_data['sentiment_label'].value_counts().tolist(), 
    labels=twitter_data['sentiment_label'].value_counts().index.tolist(), 
    autopct='%1.1f%%'
  )
  ax1.axis('equal')
  st.pyplot(fig1)


def show_top_tokens(top_tw_tokens):
  st.header("Twitter top tokens")
  col1, col2 = st.columns(2)
  with col1:
    st.header("Positive")
    st.dataframe(top_tw_tokens[top_tw_tokens['positive']])
  with col2:
    st.header("Negative")    
    st.dataframe(top_tw_tokens[~top_tw_tokens['positive']])


def show_publications_map(twitter_data):
  st.header("World map publications")
  tab1, tab2, tab3 = st.tabs(["All", "Positive", "Negative"])

  with tab1:
    st.header("All publications")
    country_counts = select_data(twitter_data, "All")
    folium_static(create_map(country_counts))

  with tab2:
    st.header("Positive publication")
    country_counts = select_data(twitter_data, "Positive")
    folium_static(create_map(country_counts))
  
  with tab3:
    st.header("Negative publications")
    country_counts = select_data(twitter_data, "Negative")
    folium_static(create_map(country_counts))


def get_company_review(company_name):
  progress_bar = st.progress(0, text="Searching data...")
  twitter_data = ingest_data(progress_bar, company_name)
  twitter_transformed_data = clean_and_transform_data(progress_bar, twitter_data)

  update_progress_bar(progress_bar, 75, "Process finished")
  tw_company_index, top_tw_tokens = calculate_data_to_show(company_name, twitter_transformed_data)
  
  update_progress_bar(progress_bar, 100, "Process finished")
  show_data(twitter_transformed_data)
  show_top_tokens(top_tw_tokens)
  show_publications_map(twitter_data)


if __name__ == '__main__':
  company_name = st.text_input("Write a company name you would like to get it review")
  col1, col2 = st.columns(2)
  with col1:
    review_btn = st.button("Get review!")
  with col2:
    clear_btn = st.button("Clear screen")

  if clear_btn:
    st.empty()

  if review_btn:
    if not company_name:
      st.warning("You should add a company name")
    else:
      get_company_review(company_name)


# # to run it only through terminal - you should comment the code similar above this
# import sys
# if __name__ == '__main__':
#   company_name = ''.join(sys.argv[1:])
#   if not company_name:
#     print("You should add a company name as parameter")
#   else:
#     get_company_review(company_name)