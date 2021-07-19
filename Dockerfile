FROM python:latest
ENV GOOGLE_MAPS_KEY ##YourKey

ENV EMAIL_USER ##YourKey

ENV EMAIL_PASS ##YourKey

WORKDIR /Catering

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]