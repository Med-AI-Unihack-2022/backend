import pymongo
import uuid
from pymongo import InsertOne, DeleteOne, ReplaceOne
client = pymongo.MongoClient("mongodb+srv://unihack2022:C3KPfOZbbD4gtJHT@cluster0.gn1wm.mongodb.net/medbuddy?retryWrites=true&w=majority")

mydb = client["medbuddy"]

def init_db():
    patient_id ='12345678'
    doctor_id ='91234567'
    patient_token = 'tony_stark_token'
    doctor_token = 'nick_furry_token'
    timestamp = '6666'
    qr_token = str(uuid.uuid1())
    qr_code_content = doctor_id + ',' + qr_token + ',' + timestamp
    qr_code_id = 'qr_code_id_1'

    patient = {
      'id': patient_id,
      'username': 'tony',
      'first_name': 'Tony',
      'last_name': 'Stark',
      'age': 58,
      'authenticaion_token': patient_token,
      'password': '1234'
    }

    doctor = {
      'id': doctor_id,
      'username': 'nick',
      'first_name': 'Nick',
      'last_name': 'Furry',
      'age': 68,
      'authenticaion_token': doctor_token,
      'password': '1234'
    }

    qr_code_doc  = {
      'id': qr_code_id,
      'patient_id': patient_id,
      'doctor_id': doctor_id,
      'qr_code_content': qr_code_content,
      'doctor_token': doctor_token,
      'patient_token': patient_token,
      'expired_at': 'Never',
      'approved_at': 'Never',
    }
    mydb.patients.drop()
    mydb.doctors.drop()
    # mydb.qr_codes.drop()

    requests = [ReplaceOne({'id': patient_id}, patient, upsert=True)]
    mydb.patients.bulk_write(requests)

    requests = [ReplaceOne({'id': doctor_id}, doctor, upsert=True)]
    mydb.doctors.bulk_write(requests)

    # requests = [ReplaceOne({'id': qr_code_id}, qr_code_doc, upsert=True)]
    # mydb.qr_codes.bulk_write(requests)
