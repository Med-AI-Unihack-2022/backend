import uuid
from datetime import datetime
from io import BytesIO
import qrcode
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import StreamingResponse, Response

from db import mydb, init_db
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [ "*" ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


@app.post("/doctors/signin")
def signin(username: str, password: str, response: Response):
    doc_filter = {'username': username, 'password': password}
    auth_token = str(uuid.uuid1())
    doctor = mydb.doctors.find_one_and_update(doc_filter, {'$set': {'authentication_token': auth_token}})
    if not doctor:
        response.status_code = 401
        return {}
    return {
        'authentication_token': auth_token
    }

@app.post("/patients/signin")
def signin(username: str, password: str, response: Response):
    doc_filter = {'username': username, 'password': password}
    auth_token = str(uuid.uuid1())
    patient = mydb.patients.find_one_and_update(doc_filter, {'$set': {'authentication_token': auth_token}})
    if not patient:
        response.status_code = 401
        return {}
    return {
        'authentication_token': auth_token
    }


def find_doctor(doctor_token: str):
    return mydb.doctors.find_one({'authentication_token': doctor_token})

def find_patient(patient_token: str):
    return mydb.patients.find_one({'authentication_token': patient_token})

def create_qr_code_doc(qr_code_doc):
    return mydb.qr_codes.insert_one(qr_code_doc)

def update_qr_code_doc(qr_code_doc):
    return mydb.qr_codes.update_one({'id': qr_code_doc['id']}, {'$set': qr_code_doc})

def find_qr_code_by_qr_code_token(qr_code_token):
    return mydb.qr_codes.find_one({'qr_code_token': qr_code_token})


@app.get('/qr_codes/query')
def qr_codes_query(doctor_token: str, qr_code_token: str):
    # TODO Verify doctor token
    doctor = find_doctor(doctor_token)
    qr_code_doc =  find_qr_code_by_qr_code_token(qr_code_token)
    if not qr_code_doc['approved']:
        return {
            'approved': False
        }
    patient = find_patient(qr_code_doc['patient_token'])
    return {
        'approved': qr_code_doc['approved'],
        'approved_at': qr_code_doc['approved_at'],
        'doctor_name': doctor['first_name'] + ' ' + doctor['last_name'],
        'patient_name': patient['first_name'] + ' ' + patient['last_name'],
    }
@app.get('/qr_codes/approve')
def qr_codes_approve(patient_token: str, qr_code_token: str):
    # TODO Verify patient token
    patient = find_patient(patient_token)
    qr_code_doc =  find_qr_code_by_qr_code_token(qr_code_token)
    doctor = find_doctor(qr_code_doc['doctor_token'])
    qr_code_doc['patient_id'] = patient['id']
    qr_code_doc['patient_token'] = patient_token
    qr_code_doc['approved_at'] = get_timestamp_str()
    qr_code_doc['approved'] = True
    update_qr_code_doc(qr_code_doc)
    return {
        'approved': True,
        'doctor_name': doctor['first_name'] + ' ' + doctor['last_name'],
        'patient_name': patient['first_name'] + ' ' + patient['last_name'],
    }

@app.get('/qr_codes/verify')
def qr_codes_verify(patient_token: str, qr_code_token: str):
    # TODO Verify patient token
    qr_code_doc =  find_qr_code_by_qr_code_token(qr_code_token)
    doctor_id = qr_code_doc['doctor_id']
    doctor_token = qr_code_doc['doctor_token']
    doctor = find_doctor(doctor_token)
    return {
      'first_name': doctor['first_name'],
      'last_name': doctor['last_name'],
      'qr_code_token': qr_code_token
    }

# Get a QR code that will show on the doctor's screen
@app.get("/qr_codes/:qr_code_token")
def qr_codes_create(qr_code_token: str):
    qr_code_doc =  find_qr_code_by_qr_code_token(qr_code_token)
    doctor_id = qr_code_doc['doctor_id']
    qr_code_content = make_qr_code(doctor_id, qr_code_token)
    return StreamingResponse(make_qr_code_image(qr_code_content), media_type="image/png")

# Create a QR code that will show on the doctor's screen
@app.get("/qr_codes/create")
def qr_codes_create(doctor_token: str):
    doctor = find_doctor(doctor_token)
    doctor_id = doctor['id']
    qr_code_token = str(uuid.uuid1())
    qr_code_content = make_qr_code(doctor_id, qr_code_token)
    created_at = get_timestamp_str()
    qr_code_doc = {
        'id': qr_code_token,
        'doctor_id': doctor_id,
        'qr_code_content': qr_code_content,
        'doctor_token': doctor_token,
        'patient_token': '',
        'qr_code_token': qr_code_token,
        'approved': False,
        'approved_at': None,
        'expired_at': 1234,
        'created_at': created_at
    }
    create_qr_code_doc(qr_code_doc)
    return {
        'qr_code_token': qr_code_token,
        'created_at': created_at
    }

init_db()
