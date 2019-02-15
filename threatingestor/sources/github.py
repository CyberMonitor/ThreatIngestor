import datetime
import json
import requests

from threatingestor.sources import Source
import threatingestor.artifacts

SEARCH_URL = "https://api.github.com/search/repositories"

class Plugin(Source):
  
    def __init__(self, name,search, username="", token="" ):
        if(username and token):
            self.auth = (username,token)
        else:
            self.auth= None

        self.name = name
        self.search = search

    def make_requests(self, url, params, auth):
        # Iterates through pages of results from query
        isEmpty = False
        artifact_list= []
        isFirst=True

        response = requests.get(url, params=params, auth=self.auth)
        while(True):
            for repo in response.json()['items']:
                title = "Manual Task: GitHub {u}".format(u=repo['full_name'])
                description = 'URL: {u}\nTask autogenerated by ThreatIngestor from source: {s}'.format(s=self.name, u=repo['html_url'])
                artifact = threatingestor.artifacts.Task(title, self.name, reference_link=repo['html_url'],
                                                         reference_text=description)
                artifact_list.append(artifact)

            if(response.links.get('next') is None):
                break
            
            response= requests.get(response.links.get('next')["url"], auth=self.auth)

        return artifact_list

    def run(self, saved_state):
        # if no saved_state, search max 1 day ago
        if not saved_state:
            #print("No saved State")
            saved_state = (datetime.datetime.utcnow() - datetime.timedelta(days=10)).isoformat()[:-7] + 'Z'

        params = {
                'q': "{search} created:>={timestamp}".format(search=self.search, timestamp=saved_state),
                "per_page": "100"
        }

        
        saved_state = datetime.datetime.utcnow().isoformat()[:-7] + 'Z'
        artifact_list = self.make_requests(SEARCH_URL, params, self.auth)

        return saved_state, artifact_list
