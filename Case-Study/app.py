from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from flask_bootstrap import Bootstrap
import os

app = Flask(__name__)
bootstrap = Bootstrap(app)

# Azure Storage Account connection string
connection_string = 'DefaultEndpointsProtocol=https;AccountName=photosapp;AccountKey=TykJngJOcgQtXS+QXcaJh3umYeOMjjzWwt9bhrvOXs5nGfwWaIXHegjsH4J+3ifh0z6fHt/4Geqg+AStHKh7oA==;EndpointSuffix=core.windows.net'
container_name = 'photos'
upload_folder = 'uploads'  # Folder to store downloaded files locally

@app.route('/')
def index():
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blobs = container_client.list_blobs()

    return render_template('index.html', blobs=blobs)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file.filename)

    blob_client.upload_blob(file)

    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)

    # Download the blob to the local upload folder
    with open(os.path.join(upload_folder, filename), 'wb') as file:
        file.write(blob_client.download_blob().readall())

    return send_from_directory(upload_folder, filename, as_attachment=True)

if __name__ == '__main__':
    # Create the local upload folder if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)
    app.run(debug=True)
