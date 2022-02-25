import pymongo
client = pymongo.MongoClient("mongodb+srv://unihack2022:C3KPfOZbbD4gtJHT@cluster0.gn1wm.mongodb.net/medbuddy?retryWrites=true&w=majority")

mydb = client["medbuddy"]
