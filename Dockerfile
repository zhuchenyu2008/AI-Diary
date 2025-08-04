# Use official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the container
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Define a volume for the SQLite database
VOLUME ["/app/src/database"]

# Run the application
CMD ["python", "src/main.py"]
