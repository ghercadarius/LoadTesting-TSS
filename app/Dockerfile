FROM python:3.12-bookworm
LABEL authors="Darius Gherca"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip3 install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cpu

COPY . .

ENV PORT_NUMBER=""

CMD ["python", "server.py"]
