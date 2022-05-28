FROM python:3.7

WORKDIR /code
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt

ADD ./app .
CMD python main.py