import sys
from linkedin_search import get_linkedin_data

def ingest_data(company_name):
  linkedin_data = get_linkedin_data(company_name)
  return linkedin_data

def transform_data(data):
  return data

def get_company_review(company_name):
  data = ingest_data(company_name)
  transform_data(data)


if __name__ == '__main__':
  company_name = ''.join(sys.argv[1:])
  if not company_name:
    print("You should add a company name as parameter")
  else:
    get_company_review(company_name)