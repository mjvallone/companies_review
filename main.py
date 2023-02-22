import streamlit as st
from data_ingestion import get_linkedin_data, get_twitter_data


def update_progress_bar(progress_bar, progress, text):
  progress_bar.progress(progress, text=text)


def ingest_data(progress_bar, company_name):
  update_progress_bar(progress_bar, 10, "Getting Linkedin data...")
  linkedin_data = get_linkedin_data(company_name)
  update_progress_bar(progress_bar, 30, f"{len(linkedin_data)} posts obtained from Linkedin")
  update_progress_bar(progress_bar, 35, "Getting Twitter data...")
  twitter_data = get_twitter_data(company_name)
  update_progress_bar(progress_bar, 55, f"{len(twitter_data)} posts obtained from Twitter")
  return linkedin_data, twitter_data


def clean_and_transform_data(progress_bar,linkedin_data, twitter_data):
  # TODO I've seen company's ads or claims in tweets, should we clean them?
  # e.g. @amazon i want to return my product boat smart watch pls help this is my register no.8787042107
  # Amazon Free Same Day Delivery and Free One Day  with Amazon Prime.  Learn More Here. https://t.co/9Up3AX0sua via @amazon
  
  # TODO we could calculate here general index, get sentiment out of data texts
  update_progress_bar(progress_bar, 70, "Transforming data")
  return linkedin_data, twitter_data


def show_data(linkedin_data, twitter_data):
  st.header("Linkedin data")
  st.dataframe(linkedin_data)
  st.header("Twitter data")
  st.dataframe(twitter_data)


def get_company_review(company_name):
  progress_bar = st.progress(0, text="Searching data...")
  linkedin_data, twitter_data = ingest_data(progress_bar, company_name)
  clean_and_transform_data(progress_bar, linkedin_data, twitter_data)
  update_progress_bar(progress_bar, 100, "Process finished")
  show_data(linkedin_data, twitter_data)


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

