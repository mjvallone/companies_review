import requests
import json

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