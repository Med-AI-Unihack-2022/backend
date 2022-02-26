import uuid
from datetime import datetime
from io import BytesIO
import qrcode
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from db import mydb, init_db


app = FastAPI()

def get_timestamp_str():
    return datetime.today().strftime('%Y-%m-%d-%H:%M:%S')

def make_qr_code( doctor_id: str, qr_code_token: str):
    return f'{doctor_id},{qr_code_token}'

def make_qr_code_image( data ):
    img = qrcode.make(data)
    img_io = BytesIO()
    img.get_image().save(img_io,'png')
    img_io.seek(0)
    yield from img_io

@app.get("/")
def read_root():
    print(mydb)
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


def find_doctor(doctor_token: str):
    return mydb.doctors.find_one({'authenticaion_token': doctor_token})

def find_patient(patient_token: str):
    return mydb.patients.find_one({'authenticaion_token': patient_token})

def create_qr_code_doc(qr_code_doc):
    return mydb.qr_codes.insert_one(qr_code_doc)

def update_qr_code_doc(qr_code_doc):
    return mydb.qr_codes.update_one({'id': qr_code_doc['id']}, {'$set': qr_code_doc})

def find_qr_code_by_qr_code_token(qr_code_token):
    return mydb.qr_codes.find_one({'qr_code_token': qr_code_token})

@app.get('/qr_codes/approve')
def qr_codes_approve(patient_token: str, qr_code_token: str):
    patient = find_patient(patient_token)
    qr_code_doc =  find_qr_code_by_qr_code_token(qr_code_token)
    doctor = find_doctor(qr_code_doc['doctor_token'])
    qr_code_doc['patient_id'] = patient['id']
    qr_code_doc['patient_token'] = patient_token
    qr_code_doc['approved_at'] = get_timestamp_str()
    update_qr_code_doc(qr_code_doc)
    return {
        'approved': True,
        'doctor_name': doctor['first_name'] + ' ' + doctor['last_name'],
        'patient_name': patient['first_name'] + ' ' + patient['last_name'],
    }

@app.get('/qr_codes/verify')
def qr_codes_verify(patient_token: str, qr_code_token: str):
    qr_code_doc =  find_qr_code_by_qr_code_token(qr_code_token)
    doctor_id = qr_code_doc['doctor_id']
    doctor_token = qr_code_doc['doctor_token']
    doctor = find_doctor(doctor_token)
    return {
      'first_name': doctor['first_name'],
      'last_name': doctor['last_name'],
      'qr_code_token': qr_code_token
    }

# Create a QR code that will show on the doctor's screen
@app.get("/qr_codes/create")
def qr_codes_create(doctor_token: str):
    doctor = find_doctor(doctor_token)
    doctor_id = doctor['id']
    qr_code_token = str(uuid.uuid1())
    qr_code_content = make_qr_code(doctor_id, qr_code_token)
    qr_code_doc = {
        'id': qr_code_token,
        'doctor_id': doctor_id,
        'qr_code_content': qr_code_content,
        'doctor_token': doctor_token,
        'patient_token': '',
        'qr_code_token': qr_code_token,
        'expired_at': 1234
    }
    create_qr_code_doc(qr_code_doc)
    return StreamingResponse(make_qr_code_image(qr_code_content), media_type="image/png")

init_db()
