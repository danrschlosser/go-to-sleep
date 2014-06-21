import requests

SRV = 'localhost:5000'
CREATE = SRV + '/users/create/'

requests.post(CREATE+"dan.r.schlosser@gmail.com")