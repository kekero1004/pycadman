# network/cloud_sync.py

import requests

def login(username, password):
    response = requests.post('https://example.com/api/login', json={'username': username, 'password': password})
    if response.status_code == 200:
        token = response.json().get('token')
        return token
    else:
        print("로그인 실패")
        return None

def sync_with_cloud(project_data, token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post('https://example.com/api/sync', json=project_data, headers=headers)
    if response.status_code == 200:
        print("클라우드와 동기화되었습니다.")
    else:
        print("동기화 실패")
