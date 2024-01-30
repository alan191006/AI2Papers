import re
import json
import urllib3

from datetime import datetime

# Search param
query = "cat:cs.AI"
max_results = 2000 # ArXiV max "max_results"

http = urllib3.PoolManager()

def extract_entries(api_response):
    entry_pattern     = re.compile(r'<entry>.*?</entry>', 
                                   re.DOTALL)
    published_pattern = re.compile(r'<published>(.*?)</published>', 
                                   re.DOTALL)
    title_pattern     = re.compile(r'<title>(.*?)</title>', 
                                   re.DOTALL)
    author_pattern    = re.compile(r'<author>.*?<name>(.*?)</name>.*?</author>', 
                                   re.DOTALL)
    summary_pattern   = re.compile(r'<summary>(.*?)</summary>', 
                                   re.DOTALL)
    link_pattern      = re.compile(r'<link href="(.*?)" rel="alternate" type="text/html"/>', 
                                   re.DOTALL)
                                   
    entries = []

    for entry_match in entry_pattern.finditer(api_response):
        entry_xml = entry_match.group(0)
        entries.append(entry_xml)
        
    entries_list = []

    # Process entries with the same day as the latest entry
    for entry_xml in entries:
        title_match    = title_pattern.search(entry_xml)
        author_matches = author_pattern.findall(entry_xml)
        summary_match  = summary_pattern.search(entry_xml)
        link_match     = link_pattern.search(entry_xml)

        if title_match and summary_match and link_match:
            title    = title_match.group(1)
            authors  = ', '.join(author_matches)
            abstract = summary_match.group(1)
            link     = link_match.group(1)


            entry_data = {
                "title":    title,
                "authors":  authors,
                "abstract": abstract,
                "link":     link
            }

            entries_list.append(entry_data)

    return entries_list


def save_to_json(entries_list, filename=None):
    if filename is None:
        date_str = datetime.now().strftime('%d-%m-%Y')
        filename = f"./data/data_{date_str}_mr_{max_results}.json"

    with open(filename, 'w') as json_file:
        json.dump(entries_list, json_file, indent=2)


if __name__ == "__main__":
    
    # Make API request
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "start": 0,
        "max_results": max_results,
    }

    url = f"{base_url}?{('&'.join(f'{k}={v}' for k, v in params.items()))}"

    # Make the HTTP request using urllib3
    response = http.request('GET', url)
    api_response = response.data.decode('utf-8')

    if response.status == 200:
        entries_list = extract_entries(api_response)
        save_to_json(entries_list)
    
    else:
        print(api_response.status)
    
    
