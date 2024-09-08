FROM python:3.12
EXPOSE 8080
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD streamlit run --server.port=8080 --server.address=0.0.0.0 --server.enableCORS=false --server.enableWebsocketCompression=false --server.enableXsrfProtection=false --server.headless=true app.py 
