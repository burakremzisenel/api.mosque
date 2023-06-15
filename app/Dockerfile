FROM python:3.9-bullseye

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Berlin
RUN apt-get install -y tzdata


# Copy app
COPY . /app

WORKDIR /app


# Install dependenceis
RUN pip install -r requirements.txt

# Expose port 5000
EXPOSE 5000

# Run the server when container is launched
CMD ["python3", "-u", "app.py"]
#CMD ["flask", "run", "--host", "0.0.0.0"]