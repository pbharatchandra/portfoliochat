FROM rasa/rasa:3.6.21-full
WORKDIR /app
COPY . /app
RUN pip install google-generativeai python-dotenv
USER 1001
EXPOSE 5005
ENTRYPOINT []
CMD ["sh", "-c", "rasa run actions --port 5055 & rasa run --enable-api --cors \"*\" --port ${PORT:-5005} --model models/20251002-190021-late-mosque.tar.gz"]