# Use a slim Python image as a base
FROM python:3.12-slim-bookworm

# Set the working directory inside the container
WORKDIR /app

# Copy your requirements file and install dependencies
# This helps with caching if your dependencies don't change often
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy your bot's code into the container
COPY . .

# Command to run your bot when the container starts
# Replace 'main.py' with the actual name of your bot's main script
CMD ["python", "main.py"]
