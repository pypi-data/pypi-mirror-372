from google.cloud import storage

def delete_file_content(file_path):
    with open(file_path, 'w') as file:
        file.truncate(0)

def check_if_file_exists(bucket_name, key):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(key)
    return blob.exists()

def upload_to_gcs(local_file_name, bucket_name, object_key):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_key)
    blob.upload_from_filename(local_file_name)
    print(f"File {local_file_name} uploaded to {bucket_name}/{object_key}")

def download_from_gcs(bucket_name, object_key, local_file_name):
    delete_file_content(local_file_name)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_key)
    blob.download_to_filename(local_file_name)
    print(f"File {object_key} downloaded from {bucket_name} to {local_file_name}")

def check_if_folder_exists(bucket_name, folder_path):
    client = storage.Client()
    blobs = list(client.list_blobs(bucket_name, prefix=folder_path, delimiter="/"))
    return len(blobs) > 0  

def create_folder_if_not_exists(bucket_name, folder_path):
    if check_if_folder_exists(bucket_name, folder_path):
        print(f"Folder {folder_path} already exists in {bucket_name}.")
    else:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        placeholder_blob = bucket.blob(f"{folder_path}_folder_placeholder.txt")
        placeholder_blob.upload_from_string("", content_type="text/plain")
        print(f"Created folder: {folder_path} in {bucket_name}")

def upload_report_file_to_gcs(temp_file, bucket_name, folder_path, object_key):
    if not check_if_folder_exists(bucket_name, folder_path):
        print(f"Folder '{folder_path}' does not exist in {bucket_name}. Creating folder.")
        create_folder_if_not_exists(bucket_name, folder_path)
    upload_to_gcs(temp_file, bucket_name, object_key)
