# Use an official Python image as the base
FROM python:3.13

# Set the working directory inside the container
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y libpq-dev gcc

# Install Python dependencies
#RUN pip install --no-cache-dir -r Requirements.txt
RUN pip install -r Requirements.txt

#COPY ./data /app
# Expose the default Flask AppBuilder port
EXPOSE 5000

# Set environment variables for Flask
ENV FLASK_APP=app

# Set the command to run the FAB app using flask run
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]
