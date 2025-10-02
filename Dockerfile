FROM rasa/rasa:3.6.21-full

WORKDIR /app
COPY . /app

# Install dependencies using the Rasa user (not root)
USER 0  # Temporarily switch to root
RUN pip install --no-cache-dir --user google-generativeai python-dotenv gspread oauth2client
USER 1001  # Switch back to non-root user

EXPOSE 5005

ENTRYPOINT []
CMD ["sh", "-c", "rasa run actions --port 5055 & rasa run --enable-api --cors \"*\" --port ${PORT:-5005} --model models/20251002-190021-late-mosque.tar.gz"]