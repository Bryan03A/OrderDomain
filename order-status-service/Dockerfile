# Base image for Python
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install the dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code of the microservice
COPY . /app/
COPY app /app

EXPOSE 5017

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5017"]