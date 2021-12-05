FROM python:3.8.12-bullseye

WORKDIR /usr/src/app

COPY . .

RUN pip install -r requirements.txt

RUN python -m rokt.parser -i /user/src/app/rokt/resources/sample1.txt -t sqlite

RUN set FLASK_APP=rokt/exposer.py

CMD ["flask", "run"]