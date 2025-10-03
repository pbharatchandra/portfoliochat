# FROM python:3.10-slim

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     gcc \
#     g++ \
#     && rm -rf /var/lib/apt/lists/*

# # Install Rasa and all dependencies
# RUN pip install --no-cache-dir \
#     rasa==3.6.21 \
#     google-generativeai \
#     python-dotenv \
#     gspread \
#     oauth2client

# WORKDIR /app
# COPY . /app

# # Create a non-root user (optional but recommended)
# RUN useradd -m -u 1001 rasauser
# USER 1001

# EXPOSE 5005

# ENTRYPOINT []
# CMD ["sh", "-c", "rasa run actions --port 5055 & rasa run --enable-api --cors \"*\" --port ${PORT:-5005} --model models/20251002-190021-late-mosque.tar.gz"]


# FROM python:3.10-slim

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     gcc \
#     g++ \
#     && rm -rf /var/lib/apt/lists/*

# # Install Rasa and required dependencies
# RUN pip install --no-cache-dir \
#     rasa==3.6.21 \
#     google-generativeai \
#     python-dotenv \
#     gspread \
#     oauth2client

# WORKDIR /app
# COPY . /app

# # Create a non-root user (recommended)
# RUN useradd -m -u 1001 rasauser
# USER 1001

# # Expose the port Rasa will run on
# EXPOSE 8000

# # Run only the Rasa Core server
# CMD ["sh", "-c", "rasa run --enable-api --cors \"*\" --port ${PORT} --model models/"]

# FROM rasa/rasa:3.6.21-full
# WORKDIR /app
# COPY . /app
# USER 1001
# EXPOSE 5005
# ENTRYPOINT []
# CMD ["sh", "-c", "rasa run --enable-api --cors \"*\" --port ${PORT:-5005} --model models/20251002-190021-late-mosque.tar.gz"]

FROM rasa/rasa:3.6.21-full

WORKDIR /app
COPY . /app

# No need to install additional packages if using full image
# Just ensure your model and data are copied

EXPOSE 5005
ENTRYPOINT []

CMD ["sh", "-c", "rasa run --enable-api --cors \"*\" --port ${PORT:-5005} --model models/20251002-190021-late-mosque.tar.gz"]