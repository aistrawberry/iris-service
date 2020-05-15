FROM python:3.7

COPY ./requirement.txt /requirements.txt
WORKDIR /

RUN pip install -r requirements.txt

COPY . /

EXPOSE 5000
CMD ["python", "serving_model.py"]