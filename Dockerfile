# 1. Base image
FROM python:3.8.3-slim-buster

# 2. Copy files
COPY . /src
WORKDIR /src

# 3. Install dependencies
RUN pip install -r requirements.txt

CMD ["python",  "dataBaseCreation.py"]
