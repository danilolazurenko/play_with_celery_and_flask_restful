import requests

#r = requests.put('http://127.0.0.1:5000/', json={'url':'https://www.google.com'})
#r = requests.get('https://www.google.com')
#print(r.content)

r = requests.post('http://127.0.0.1:5000/1', json={'success': 'True', 'html': 'still no html'})