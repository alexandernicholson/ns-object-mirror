# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /usr/src/app

# Upgrade pip
RUN pip install --upgrade pip

# Copy Pipfile to the working directory
COPY requirements.txt /usr/src/app/

# Install any needed packages specified in Pipfile
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Run app.py when the container launches
CMD ["python", "app.py"]
