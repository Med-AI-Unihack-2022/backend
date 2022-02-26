# Instructions

## Create a new python virtual environment
```
python3 -m venv venv
```

## Activate the virtual environment
```
source venv/bin/activate
```

## Install the dependencies
```
pip install -r requirments.txt
```

## Start the server
```
uvicorn main:app --reload
```

# Design

## Peer to peer authentication (via QRcode)
1. A QRcode shows in the doctor's view

  * The web page passes the ID of the doctor and the patient, the backend returns a QRcode and docto-token
  * The server save the QRcode information and ID information to DB
  * The web page checks the approval status every 10 seconds

2. The patient scans the QRcode and paitent's ID
  * The app sends the QRcode information to backend
  * The backend uses the QRcode and patient's ID to look up the relevant information in the DB
  * If there is a record, the backend returns a patient-token and prompt message to the app
  * The patient approves the request and the app sends a request with patient-id and patient-token to the backend
  * The backend changes the approval status to true

MongoDB design:
Doctor document
```JSON
{
  'id': 'xxx',
  'first_name': 'xxx',
  'last_name': 'xxx',
  'age': 88,
  'authenticaion_token': 'xxx',
  'password': '123456'
}
```
Patient document
```JSON
{
  'id': 'xxx',
  'first_name': 'xxx',
  'last_name': 'xxx',
  'age': 88,
  'authenticaion_token': 'xxx',
  'password': '123456'
}
```

QRcode document
> The QR code is equal to doctor_id + ',' + qr_token + ',' + timestamp
```JSON
{
  'patient_id': 'xxx',
  'doctor_id': 'xxx',
  'qrcode': 'xxxx',
  'doctor_token': 'xxx',
  'patient_token': 'xxx',
  'qr_token': 'xxx',
  'expired_at': 'xxx',
}
```
