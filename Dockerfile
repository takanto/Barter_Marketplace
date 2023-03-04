###
FROM python:3-alpine
COPY requirements.txt .

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

RUN apk update && \
    apk add python3 postgresql-libs && \
    apk add --virtual .build-deps gcc python3-dev musl-dev postgresql-dev libc-dev \
    libpq-dev make git libffi-dev openssl-dev libxml2-dev libxslt-dev zlib-dev jpeg-dev && \
    apk add --no-cache jpeg && \
    pip install psycopg2-binary --no-cache-dir && \
    pip install psycopg2 --no-cache-dir && \
    python3 -m pip install -r requirements.txt --no-cache-dir && \
    apk --purge del .build-deps

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]