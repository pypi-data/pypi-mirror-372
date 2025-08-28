import requests

def upload_to_weaviate(tapestry_id, chunks):
    url =  "https://inthepicture.org/admin/upload_to_weaviate"

    payload = {
        "tapestry_id": tapestry_id,
        "chunks": chunks,
    }
    
    response = requests.post(url, json=payload)
    try:
        resp_json = response.json()
    except Exception:
        resp_json = {}

    if response.status_code == 200 and resp_json.get("success", False):
        return resp_json
    else:
        message = resp_json.get("message", response.text)
        return {
            "success": False,
            "code": response.status_code,
            "message": message,
            "body": {}
        }
chunks =[
     {
            "title": "UK Army Overview",
            "file_type": "txt",
            "chunk_index": 1,
            "content": "The British Army is the land warfare branch of the United Kingdom's armed forces.",
            "file_title": "UK_Army_Info"
        },
        {
            "title": "UK Army Overview",
            "file_type": "txt",
            "chunk_index": 2,
            "content": "It has a long history dating back to 1660, making it one of the oldest standing armies.",
            "file_title": "UK_Army_Info"
        },
        {
            "title": "UK Army Overview",
            "file_type": "txt",
            "chunk_index": 3,
            "content": "The army plays a crucial role in national defense and international peacekeeping missions.",
            "file_title": "UK_Army_Info"
        },
        {
            "title": "UK Army Overview",
            "file_type": "txt",
            "chunk_index": 4,
            "content": "It consists of both regular soldiers and reservists who train to maintain readiness.",
            "file_title": "UK_Army_Info"
        },
        {
            "title": "UK Army Overview",
            "file_type": "txt",
            "chunk_index": 5,
            "content": "The British Army is known for its discipline, professionalism, and commitment to service.",
            "file_title": "UK_Army_Info"
        }
]

print(upload_to_weaviate(2, chunks))