# - *- coding: utf- 8 - *-
import requests
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import json
import modules.argus

def sort_languages(languages):
    languages = [i.lower().capitalize() for i in languages]
    print(languages)
    if "Html" in languages:
        languages.remove("Html")

    if "Css" in languages:
        languages.remove("Css")
    
    if "Qml" in languages:
        languages.remove("Qml")    
    
    print(languages)
    
    if len(languages) == 0:
        languages.append("Only markup languages")
    
    return languages

def get_all_apps():
    URL = "https://open-store.io/api/v4/apps?type=app"
    
    r = requests.get(URL)
   
    yis = json.loads(r.text)
    
    app_data = []
    
    for i in yis["data"]["packages"]:
        app_data.append(i["id"])
    
    return app_data
    

def get_app_details(app_id):
    os_url = f"https://open-store.io/api/v4/apps/{app_id}?channel=xenial"
    
    r = requests.get(os_url)

    yis = json.loads(r.text)
    
    return yis


def get_app_details_All():
    all_apps_name = get_all_apps()  
    
    all_apps_details = []
    
    for i in all_apps_name:
        #get extended app data
        apps_data = get_app_details(i)
        
        app_details = {}
        app_details["id"] = apps_data["data"]["id"]
        app_details["name"] = apps_data["data"]["name"]
        app_details["author"] = apps_data["data"]["author"]
        app_details["maintainer"] = apps_data["data"]["maintainer_name"]       
        app_details["category"] = apps_data["data"]["category"]
        app_details["license"] = apps_data["data"]["license"]
        app_details["description"] = apps_data["data"]["manifest"]["description"]
        app_details["source"] = apps_data["data"]["source"]
        
        #and apends them to the main list of apps
        all_apps_details.append(app_details)
    
    return all_apps_details


def simple_get(url):
    """
    poskusi dobiti vsebino na url-ju z HTTP GET requestom
    Če je vsebina urlja HTML ali XML, vrnemo text, drugeče None
    """
    try:
        with closing(requests.get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return "<div>error 404</div>"#None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None
    
def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
           and content_type is not None 
           and content_type.find('html') > -1)

def log_error(e):
    '''
    Vedno je dobra ideja error log. 
    Ta funkcija samo sprinta napako.
    '''
    print(e)

def get_github_languages(html):
    print(html)
    
    languages = []
    
    raw_html = simple_get(html)
    soup = BeautifulSoup(raw_html, 'html.parser')
    #get the div with the languages
    div = soup.find_all(class_="d-flex repository-lang-stats-graph")
    
    if len(div) != 0:
        #get the NON empty spans with the languages
        spans = div[0].find_all('span')
        
        for span in spans:
            languages.append(span.text)
    
    else:
        languages.append("Language not recognised.")

    return languages


def get_gitlab_languages(html):
    languages = []
    
    if "/tree/" in html:
        html = html.split("/")
        html = html[:-2]
        html = "/".join(html)
    print(html)
    '''
    if "/tree/exp" in html:
        html = html[0:-9]
    
    if "/tree/master" in html:
        html = html[0:-12]
    
    if "/tree/Ubuntu_Touch" in html:
        html = html[0:18]
    print("html")
    '''
    
    raw_html = simple_get(html)
    soup = BeautifulSoup(raw_html, 'html.parser')
    div = soup.find_all(class_="progress-bar has-tooltip")
    
    for i in div:
        soup = BeautifulSoup(i["title"], 'html.parser')
        #language
        b = soup.find_all(class_="repository-language-bar-tooltip-language")[0]
        #% of language
        c = soup.find_all(class_="repository-language-bar-tooltip-share")[0]
        languages.append(b.text)
    
    return languages
         

def main_process():
    #gets all the app names from the Openstore API
    
    languages = ["html", "CSS", "Python"]
    print(languages)
    print(sort_languages(languages))
    #all_apps_all_details = get_app_details_All()

    '''
    #filter all apps that have no source
    no_source_apps_iterater = filter((lambda x : True if (x["source"] == "") else False), all_apps_details)
    no_source_apps = list(no_source_apps_iterater)
    
    #filter all apps that are from github
    github_apps_iterater = filter((lambda x : True if ("github" in x["source"]) else False), all_apps_details)
    github_apps = list(no_source_apps_iterater)    
    
    #filter all apps that are from gitlab
    gitlab_apps_iterater = filter((lambda x : True if ("gitlab" in x["source"]) else False), all_apps_details)
    gitlab_apps = list(no_source_apps_iterater)        
    
    for i in no_source_apps:
        print(i)
    '''
    

if __name__ == "__main__":    
    main_process()
    
        
    
