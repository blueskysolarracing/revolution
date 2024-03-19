FROM --platform=linux/arm64 python:3.11

COPY . .
RUN pip install --upgrade pip && pip install -r requirements.txt
ARG REVOLUTION_CONFIGURATIONS_MODULE=configurations.deployment

CMD ["python3", "-m", "revolution"]
