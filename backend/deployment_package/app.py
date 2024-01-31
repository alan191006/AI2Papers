import re
import boto3
import pickle
import urllib3
import json
import base64
import pandas as pd

from datetime import datetime
from sklearn.decomposition import PCA, CountVectorizer

http = urllib3.PoolManager()

# Your DynamoDB table info
table_name = 'AI2Papers_MLModels'
model_key = 'model_id'
aws_access_key_id = 'AKIAST4MTDSBNGMQ4XAI'
aws_secret_access_key = 'GUdU+GQWleRg6ogauys0n0YJL3HSfpCX6vHBGs+M'
region_name = 'ap-southeast-2'

github_token = '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'
github_url = 'https://api.github.com/repos/alan191006/AI2Papers/contents/output.json'

def process_entries(entries, model):
    if not model:
        print("Error: Model not loaded.")
        return None

    # Convert entries to Pandas DataFrame
    df = pd.DataFrame(entries)

    # Apply CountVectorizer to 'abstract' and 'title'
    count_vec = CountVectorizer()
    ab_counts = count_vec.fit_transform(df["abstract"])
    ti_counts = count_vec.fit_transform(df["title"])

    # Apply PCA to reduce dimensionality
    pca = PCA(n_components=3)

    # Apply PCA to 'abstract' and 'title' separately
    pca_ab = pca.fit_transform(ab_counts.toarray())
    pca_ti = pca.fit_transform(ti_counts.toarray())

    # Add PCA components to DataFrame
    for i in range(3):
        df[f'PCA{i+1}_abstract'] = pca_ab[:, i]
        df[f'PCA{i+1}_title'] = pca_ti[:, i]

    # Combine PCA components for both 'abstract' and 'title'
    pca_combined_columns = [f'PCA{i+1}_abstract' for i in range(3)] + [f'PCA{i+1}_title' for i in range(3)]

    # Get model predictions for each entry
    X = df[pca_combined_columns].values
    df['predicted_score'] = model.predict(X)

    # Sort entries by predicted score in descending order
    df = df.sort_values(by='predicted_score', ascending=False)

    # Choose the top two entries
    top_entries = df.head(2)

    return top_entries

def load_model_from_dynamodb():
    dynamodb = boto3.resource('dynamodb', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name=region_name)
    table = dynamodb.Table(table_name)

    try:
        response = table.get_item(Key={'ModelId': model_key})
        serialized_model = response.get('Item', {}).get('serialized_model', '')

        return pickle.loads(serialized_model) if serialized_model else None
    except Exception as e:
        print(f"Error loading model from DynamoDB: {e}")
        return None

def make_api_request(query, max_results, read_from_file):
    if read_from_file:
        with open('output.txt', 'r') as file:
            return file.read()
    else:
        base_url = "https://export.arxiv.org/api/query"
        params = {"search_query": query, "sortBy": "submittedDate", "sortOrder": "descending", "start": 0, "max_results": max_results}
        url = f"{base_url}?{('&'.join(f'{k}={v}' for k, v in params.items()))}"

        response = http.request('GET', url)
        return response.data.decode('utf-8') if read_from_file or response.status == 200 else None

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
                                   
    latest_entry_published_date = None
    latest_day_entries = []

    for entry_match in entry_pattern.finditer(api_response):
        entry_xml = entry_match.group(0)
        entry_published_match = published_pattern.search(entry_xml)

        if entry_published_match:
            entry_published = entry_published_match.group(1)
            entry_published_date = datetime.strptime(entry_published, "%Y-%m-%dT%H:%M:%SZ")

            if latest_entry_published_date is None or entry_published_date > latest_entry_published_date:
                latest_entry_published_date = entry_published_date
                latest_day_entries = [entry_xml]
            elif entry_published_date.date() == latest_entry_published_date.date():
                latest_day_entries.append(entry_xml)

    entries_list = []

    # Process entries with the same day as the latest entry
    for entry_xml in latest_day_entries:
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

def update_github(json_data, current_sha):
    headers = {'Authorization': f'Bearer {github_token}', 'Content-Type': 'application/json'}
    data = {'message': 'Update output.json', 'content': base64.b64encode(json_data.encode()).decode(), 'sha': current_sha}

    response = http.request('PUT', github_url, headers=headers, body=json.dumps(data))
    print("GitHub Response:", response.data.decode('utf-8'))

    return {"statusCode": response.status, "body": response.data.decode('utf-8')}

def handler(event, context):
    read_from_file = False
    query = "cat:cs.AI"
    max_results = 50

    api_response = make_api_request(query, max_results, read_from_file)

    if not api_response:
        return {"statusCode": 500, "body": "Error fetching API response"}

    entries_list = extract_entries(api_response)
    
    model = load_model_from_dynamodb()
    entries_list = process_entries(entries_list, model)

    if entries_list:
        json_data = json.dumps(entries_list, indent=2)
        github_response = http.request('GET', github_url, headers={'Authorization': f'Bearer {github_token}'})

        current_sha = json.loads(github_response.data.decode('utf-8')).get('sha', '')
        return update_github(json_data, current_sha)
    else:
        return {"statusCode": 200, "body": "No entries found."}

if __name__ == "__main__":
    handler(None, None)