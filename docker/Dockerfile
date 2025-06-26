FROM python:3.12

WORKDIR /usr/local/app

# Install application dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the source code 
COPY src ./src
EXPOSE 8000

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]