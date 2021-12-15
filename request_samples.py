import requests

print('/cities')
print(requests.get("http://127.0.0.1:5000/cities").json())
print('\n\n')

print('/mean')
print(requests.get("http://127.0.0.1:5000/mean?city=Odessa&value_type=pressure").json())
print(requests.get("http://127.0.0.1:5000/mean?city=Kiev&value_type=temp").json())
print(requests.get("http://127.0.0.1:5000/mean?city=fsddfsddf&value_type=fdsfsdf").json())
print(requests.get("http://127.0.0.1:5000/mean").json())
print('\n\n')

print('/records')
print(requests.get("http://127.0.0.1:5000/records?city=Odessa&start_dt=2021-12-16&end_dt=2021-12-20").json())
print(requests.get("http://127.0.0.1:5000/records?city=Kiev&start_dt=2021-12-18&end_dt=2021-12-27").json())
print(requests.get("http://127.0.0.1:5000/records").json())
print(requests.get("http://127.0.0.1:5000/records?city=fsdf&start_dt=5345&end_dt=534535").json())
print('\n\n')

print('/moving_mean')
print(requests.get("http://127.0.0.1:5000/moving_mean?city=Odessa&value_type=temp").json())
print(requests.get("http://127.0.0.1:5000/moving_mean?city=Kiev&value_type=pressure").json())
print(requests.get("http://127.0.0.1:5000/moving_mean?city=fsddfsddf&value_type=fdsfsdf").json())
print(requests.get("http://127.0.0.1:5000/moving_mean").json())
