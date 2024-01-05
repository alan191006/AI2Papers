import re
import json

# Cannot use requests because Lambda doesn't support
import urllib3

from datetime import datetime

http = urllib3.PoolManager()

def lambda_handler(event, context):
    # Set to True for offline debug
    read_from_file = False

    # Search param
    query = "cat:cs.AI"
    max_results = 50

    if read_from_file:
        # Read from file (for debugging)
        with open('output.txt', 'r') as file:
            api_response = file.read()
    else:
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
        
        response     = http.request('GET', url)
        api_response = response.data.decode('utf-8')

        # Debug: Save API response to CloudWatch Logs
        print("API Response:", api_response)

    if read_from_file or response.status == 200:
        entries_list = extract_entries(api_response)

        if entries_list:
            # Convert entries_list to JSON format
            json_data = json.dumps(entries_list, indent=2)

            # Log JSON data to CloudWatch Logs
            print("JSON Data:", json_data)

            return {
                "statusCode": 200,
                "body": json_data
            }
        else:
            return {
                "statusCode": 200,
                "body": "No entries found."
            }
    else:
        return {
            "statusCode": response.status,
            "body": response.data.decode('utf-8')
        }

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

    entries_list = []

    for entry_match in entry_pattern.finditer(api_response):
        entry_xml = entry_match.group(0)
        entry_published_match = published_pattern.search(entry_xml)

        if entry_published_match:
            entry_published = entry_published_match.group(1)
            entry_published_date = datetime.strptime(entry_published, "%Y-%m-%dT%H:%M:%SZ")

            if not entries_list:
                # Get all entry with same published day as first entry
                first_entry_published_date = entry_published_date
                same_day_entries = [entry_xml]
                
            elif entry_published_date.date() == first_entry_published_date.date():
                same_day_entries.append(entry_xml)
                
            else:
                # Stop the loop when the date doesn't match
                break

    # Process entries with the same day as the first entry
    for entry_xml in same_day_entries:
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
