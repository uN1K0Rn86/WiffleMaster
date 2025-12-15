FROM python:3.12

WORKDIR /usr/src/app

EXPOSE 5000

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV PORT=5000 FLASK_RUN_HOST=0.0.0.0

CMD ["flask", "run"]