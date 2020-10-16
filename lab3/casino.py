from requests import get, post

url = 'http://95.217.177.249'

if __name__ == '__main__':
    resp = req.get(f'{url}/createacc=-1')
    print(resp.headers)
    print(resp.json())
