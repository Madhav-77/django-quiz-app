# Step 1: Use the Python 3.13.0 runtime as the base image
FROM python:3.13.0-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the current directory contents into the container at /app
COPY . /app

# Step 4: Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Expose port 8000 to allow external access
EXPOSE 8000

# Step 6: Run the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
