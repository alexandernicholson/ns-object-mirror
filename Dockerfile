# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /usr/src/app

# Install pipenv
RUN pip install --upgrade pip && \
    pip install pipenv

# Copy Pipfile to the working directory
COPY Pipfile /usr/src/app/

# Install any needed packages specified in Pipfile
RUN pipenv install --deploy --ignore-pipfile

# Copy the current directory contents into the container at /usr/src/app
COPY . /usr/src/app

# Run run.sh when the container launches
CMD ["pipenv", "run", "python", "app.py"]
