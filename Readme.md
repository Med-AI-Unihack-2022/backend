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

# APIs

## Create a QR code (used in the web app)
Request:

```
GET http://127.0.0.1:8000/qr_codes/create?doctor_token=xxxx
```
Response:
```JSON
{
  "qr_code_token": "7ab1dbc8-96b4-11ec-aeda-06a73d562429",
  "created_at": "2022-02-26-14:00:43"
}
```

## Get the QR code image (used in the web app)
Request:

`qr_code_token` is returned by Create API.
```
GET http://127.0.0.1:8000/qr_codes/:qr_code_token?qr_code_token=2e6d6da4-96b4-11ec-ab7b-06a73d562429'
```

Response:

A QR code image

## Check approval status (web)
Request:

`qr_code_token` is returned by Create API.
```
GET http://127.0.0.1:8000/qr_codes/query?doctor_token=nick_furry_token&qr_code_token=a4fdae56-96b0-11ec-b220-06a73d562429'
```

Response:
```JSON
{
  "approved": true,
  "approved_at": "2022-02-26-13:38:36",
  "doctor_name": "Nick Furry",
  "patient_name": "Tony Stark"
}
```

## Verify the QR code ( used by the mobile app)
Request:

`patient_token` returns by backend when the patient logs in

`qr_code_token` is got from the QR code (a QR code scanner can get it)
```
GET http://127.0.0.1:8000/qr_codes/verify?patient_token=xxxx&qr_code_token=xxxxx
```

Response
```JSON
{
  "first_name": "Nick", # Doctor first name
  "last_name": "Furry", # Doctor last name
  "qr_code_token": "a4fdae56-96b0-11ec-b220-06a73d562429" # QR code token
}
```

## Approve the request
Request:

`patient_token` returns by backend when the patient logs in

`qr_code_token` is returned by Verify API
```
GET http://127.0.0.1:8000/qr_codes/approve?patient_token=tony_stark_token&qr_code_token=a4fdae56-96b0-11ec-b220-06a73d562429
```

Response:
```JSON
{
  "approved": true,
  "doctor_name": "Nick Furry",
  "patient_name": "Tony Stark"
}
```

# Design

## Peer to peer authentication (via QRcode)
1. A QRcode shows in the doctor's view

  * The web page passes the doctor token of the doctor, the backend returns a QRcode image that is generated from the combination of doctor id  and qr code token
  * The server save the QRcode information to DB
  * The web page checks the approval status every 10 seconds

2. The patient scans the QRcode and approves
  * The app scans the QR code and sends the QRcode information to backend
  * The backend uses the QRcode and patient's token to look up the relevant information in the DB
  * If there is a record, the backend returns a QR code  token and prompt message to the app
  * The patient approves the request and the app sends a request with patient token and qr code token to the backend
  * The backend changes the approval status to true

MongoDB design:
Doctor document
```JSON
{
  'id': 'xxx',
  'username': 'xxx',
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
  'username': 'xxx',
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
