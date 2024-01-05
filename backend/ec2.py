# Not use in production, the data processing code will run on Lambda

import re
import json
import requests
from datetime import datetime

# Set to True for offline debug
read_from_file = False

query = "cat:cs.AI"
max_results = 50

# Function to extract entries from the API response
def extract_entries(api_response):
    entry_pattern = re.compile(r'<entry>.*?</entry>', re.DOTALL)
    published_pattern = re.compile(r'<published>(.*?)</published>', re.DOTALL)
    title_pattern = re.compile(r'<title>(.*?)</title>', re.DOTALL)
    author_pattern = re.compile(r'<author>.*?<name>(.*?)</name>.*?</author>', re.DOTALL)
    summary_pattern = re.compile(r'<summary>(.*?)</summary>', re.DOTALL)
    link_pattern = re.compile(r'<link href="(.*?)" rel="alternate" type="text/html"/>', re.DOTALL)

    entries_list = []

    for entry_match in entry_pattern.finditer(api_response):
        entry_xml = entry_match.group(0)
        entry_published_match = published_pattern.search(entry_xml)

        if entry_published_match:
            entry_published = entry_published_match.group(1)
            entry_published_date = datetime.strptime(entry_published, "%Y-%m-%dT%H:%M:%SZ")

            if not entries_list:
                # For the first entry, get all entries with the same published date
                first_entry_published_date = entry_published_date
                same_day_entries = [entry_xml]
            elif entry_published_date.date() == first_entry_published_date.date():
                same_day_entries.append(entry_xml)
            else:
                # Stop the loop when the date doesn't match
                break

    # Process entries with the same day as the first entry
    for entry_xml in same_day_entries:
        title_match = title_pattern.search(entry_xml)
        author_matches = author_pattern.findall(entry_xml)
        summary_match = summary_pattern.search(entry_xml)
        link_match = link_pattern.search(entry_xml)

        if title_match and summary_match and link_match:
            title = title_match.group(1)
            authors = ', '.join(author_matches)
            abstract = summary_match.group(1)
            link = link_match.group(1)

            entry_data = {
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "link": link
            }

            entries_list.append(entry_data)

    return entries_list

# Main code
if read_from_file:
    with open('output.txt', 'r') as file:
        api_response = file.read()
else:
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": query,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
        "start": 0,
        "max_results": max_results,
    }

    url = f"{base_url}?{('&'.join(f'{k}={v}' for k, v in params.items()))}"
    response = requests.get(url)
    api_response = response.text

    # Debug: Save API response to file
    # with open("./output.txt", "w") as file:
    #     file.write(api_response)

if read_from_file or response.status_code == 200:
    entries_list = extract_entries(api_response)

    if entries_list:
        json_data = json.dumps(entries_list, indent=2)
        file_path = "out.json"

        with open(file_path, "w") as file:
            file.write(json_data)
            print("Entry saved to JSON file")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
