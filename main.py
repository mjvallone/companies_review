import streamlit as st
import matplotlib.pyplot as plt
from streamlit_folium import folium_static
from data_ingestion import get_linkedin_data, get_twitter_data
from data_visualization import select_data, create_map
from data_transformation import transform_twitter_data, get_sentiments, calculate_data_to_show



def update_progress_bar(progress_bar, progress, text):
  progress_bar.progress(progress, text=text)


def ingest_data(progress_bar, company_name):
  update_progress_bar(progress_bar, 10, "Getting Linkedin data...")
  # linkedin_data = get_linkedin_data(company_name)
  linkedin_data = []
  update_progress_bar(progress_bar, 30, f"{len(linkedin_data)} posts obtained from Linkedin")

  update_progress_bar(progress_bar, 35, "Getting Twitter data...")
  twitter_data = get_twitter_data(company_name)
  update_progress_bar(progress_bar, 55, f"{len(twitter_data)} posts obtained from Twitter")
  return linkedin_data, twitter_data


def clean_and_transform_data(progress_bar,linkedin_data, twitter_data):
  # TODO I've seen company's ads or claims in tweets, should we clean them?
  # e.g. @amazon i want to return my product boat smart watch pls help this is my register no.8787042107
  # Amazon Free Same Day Delivery and Free One Day  with Amazon Prime.  Learn More Here. https://t.co/9Up3AX0sua via @amazon

  # transform_linkedin_data(linkedin_data) # TODO we need to figure out how to get data
  transform_twitter_data(twitter_data)

  # get_sentiments(linkedin_data)
  update_progress_bar(progress_bar, 60, "Getting sentiments")
  get_sentiments(twitter_data)

  update_progress_bar(progress_bar, 70, "Transforming data")
  
  return linkedin_data, twitter_data


def show_data(linkedin_data, twitter_data, top_tw_tokens):
  # st.header("Linkedin data")
  # st.dataframe(linkedin_data)

  # comment it once we are not in "dev mode"
  st.header("Twitter data")
  st.dataframe(twitter_data)

  st.header("Twitter top positive tokens")
  st.dataframe(top_tw_tokens[top_tw_tokens['positive']])
  
  st.header("Twitter top negative tokens")
  st.dataframe(top_tw_tokens[~top_tw_tokens['positive']])
  
  st.header("Twitter sentiments pie diagram")
  fig1, ax1 = plt.subplots()
  ax1.pie(
    twitter_data['sentiment_label'].value_counts().tolist(), 
    labels=twitter_data['sentiment_label'].value_counts().index.tolist(), 
    autopct='%1.1f%%'
  )
  ax1.axis('equal')
  st.pyplot(fig1)

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
  linkedin_data, twitter_data = ingest_data(progress_bar, company_name)
  linkedin_transformed_data, twitter_transformed_data = clean_and_transform_data(progress_bar, linkedin_data, twitter_data)

  # calculate_data_to_show(linkedin_transformed_data)  # TODO
  tw_company_index, top_tw_tokens = calculate_data_to_show(company_name, twitter_transformed_data)
  
  update_progress_bar(progress_bar, 100, "Process finished")
  show_data(linkedin_transformed_data, twitter_transformed_data, top_tw_tokens)


if __name__ == '__main__':
  company_name = st.text_input("Write a company name you would like to get it review")
  review_btn = st.button("Get review!")
  clear_btn = st.button("Clear screen")

  if clear_btn:
    st.empty()

  if review_btn:
    if not company_name:
      st.write("You should add a company name")
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