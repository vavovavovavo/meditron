FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .

# EXPOSE 5000

CMD ["python3", "src/server/app.py"]
# CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]