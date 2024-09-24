import json
import base64

def generate_json_download(book):
    json_data = json.dumps({
        "title": book['title'],
        "author": book['author'],
        "description": book['description']
    }, indent=4)

    # Convert JSON data to base64 for download
    b64 = base64.b64encode(json_data.encode()).decode()
    href = f'<a href="data:application/json;base64,{b64}" download="{book["title"]}.json">Download JSON</a>'
    return href
