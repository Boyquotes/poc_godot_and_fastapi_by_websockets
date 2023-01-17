FROM python:3.10-slim-bullseye

# set environment variables
ENV PYTHONDONTWRITEBYTECODE True
ENV PYTHONUNBUFFERED True

# set work directory
WORKDIR /app

# install dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . .

# run uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]