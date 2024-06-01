FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1  # Prevents Python from writing pyc files to disc
ENV PYTHONUNBUFFERED 1  #  stdout and stderr will be sent to terminal in real time

WORKDIR /app

RUN pip install --upgrade pip
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY . /app
COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

CMD ["./wait-for-it.sh", "cas1:9042", "--", "./wait-for-it.sh", "cas2:9043", "--", "./wait-for-it.sh", "cas3:9044", "--", "python", "populate_books.py", "--csv_file", "books.csv"]