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