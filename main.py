import sys
from data_ingestion import get_linkedin_data, get_twitter_data


def ingest_data(company_name):
  print(f"Searching data for company_name: {company_name}")
  linkedin_data = get_linkedin_data(company_name)
  twitter_data = get_twitter_data(company_name)
  return linkedin_data, twitter_data

def transform_data(linkedin_data, twitter_data):
  # TODO we could calculate general index, get sentiment out of data texts
  return linkedin_data, twitter_data

def get_company_review(company_name):
  linkedin_data, twitter_data = ingest_data(company_name)
  transform_data(linkedin_data, twitter_data)


if __name__ == '__main__':
  company_name = ''.join(sys.argv[1:])
  if not company_name:
    print("You should add a company name as parameter")
  else:
    get_company_review(company_name)

