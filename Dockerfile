FROM python:3.10-slim

# Install Rasa and dependencies in one go
RUN pip install --no-cache-dir rasa==3.6.21 \
    google-generativeai \
    python-dotenv \
    gspread \
    oauth2client

WORKDIR /app
COPY . /app

EXPOSE 5005

ENTRYPOINT []
CMD ["sh", "-c", "rasa run actions --port 5055 & rasa run --enable-api --cors \"*\" --port ${PORT:-5005} --model models/20251002-190021-late-mosque.tar.gz"]