from pymongo import MongoClient

client = MongoClient('mongodb://root:example@localhost:27017')
database = client.credentials
collection = database.users

print(list(collection.find({})))
if not list(collection.find({})):
    print('Jumm')

# from requests import get

# response = get(
#     url='https://pokeapi.co/api/v2/berry/1', headers={}
# )

# print(response.json())
