FROM rasa/rasa:3.6.21-full

WORKDIR /app
COPY . /app

# Install dependencies as root before switching to non-root user
RUN pip install --no-cache-dir google-generativeai python-dotenv gspread oauth2client

# Switch to non-root user
USER 1001

EXPOSE 5005

ENTRYPOINT []
CMD ["sh", "-c", "rasa run actions --port 5055 & rasa run --enable-api --cors \"*\" --port ${PORT:-5005} --model models/20251002-190021-late-mosque.tar.gz"]