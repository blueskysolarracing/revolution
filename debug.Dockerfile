FROM --platform=linux/arm64 python:3.10

WORKDIR /usr/src/revolution

COPY ./requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

CMD ["python3", "-m", "revolution", "-d", "-i"]
