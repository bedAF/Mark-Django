#Docker
# Use an official Python base image from the Docker Hub
FROM python:3.10-slim

# Install necessary packages
RUN apt-get update && \
    apt-get install -y python3-pip

# Set working directory
ENV APP_HOME /project/
WORKDIR $APP_HOME
COPY . /project/

# Install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt


#copy migrations
RUN export PATH="/root/.local/bin:$PATH" && \
    python manage.py migrate
RUN export PATH="/root/.local/bin:$PATH" && \
    python manage.py collectstatic

# Expose the port
EXPOSE 3000

# Set the entrypoint
ENTRYPOINT ["python", "manage.py","runserver", "0.0.0.0:3000"]