import requests
from bs4 import BeautifulSoup
from ..exceptions.custom_ssl_exception import CustomSSLError
from flask import current_app


def extract_urls(url: str) -> list:
    '''
    Function to extract all URLs from a given URL
    '''

    # check if url starts with 'http' or 'https'
    url = ensure_https(url)

    try:
        # Send a request to the given URL
        response = requests.get(url)
        
        # If the request was successful, parse the page content
        if response.status_code == 200:
            page_content = response.content
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Find all anchor tags with href attribute
            links = soup.find_all('a', href=True)
            
            # Extract the href attributes
            urls = [link['href'] for link in links]
            normalized_urls = normalize_urls(urls)
            
            return normalized_urls
        else:
            return []
        
    except requests.exceptions.SSLError as e:
        current_app.logger.info("Couldn't extract urls: {}".format(e))
        raise CustomSSLError("Couldn't extract urls.")
    
    

def ensure_https(url: str) -> str:
    '''
    make given url starts with https
    '''
    if not url.startswith(('http://', 'https://')):
        return f'https://{url}'
    return url


def normalize_urls(urls: list) -> list:
    '''
    Normalize parsed urls that extracted from url that
    given by user.
    '''

    normalized_urls = []
    
    for url in urls:
        # Ignore relative paths like '/forms/post'
        if url.startswith("/") and not url.startswith("//"):
            continue
        # If URL starts with //, prepend https:
        elif url.startswith("//"):
            normalized_urls.append("https:" + url)
        # If URL starts with # or is just '#'
        elif url.startswith("#"):
            # Ignore empty or anchor links
            continue
        # Ignore URLs that are just query parameters like '?feedViewType=cardView'
        elif url.startswith("?"):
            continue
        # Ignore mailto links
        elif url.startswith("mailto"):
            continue
        else:
            # Append base_url for relative URLs, or leave absolute URLs unchanged
            normalized_urls.append(url)
    
    return normalized_urls
