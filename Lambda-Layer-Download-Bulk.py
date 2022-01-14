import subprocess
import shutil
import boto3
import json
import os
from datetime import datetime
import shutil
import sys

def lambda_handler(event, context):
    
    #Parameters =============================
    encodings = ['utf-8', 'utf-16', 'windows-1250', 'windows-1252']
    
    # Make sure Lambda has get/list/put permissions to it
    s3Bucket = "S3_BUCKET"
    reqKey = "requirements.txt"

    #========================================
    
    pyVersion = f"{sys.version_info[0]}.{sys.version_info[1]}"
    print(f"You're running Python version {pyVersion}")
    dirStructure = f'/tmp/python/python/lib/python{pyVersion}/site-packages/'
    
    S3 = boto3.resource('s3')
    bucket = S3.Bucket(s3Bucket)
    obj = bucket.Object(reqKey)
    body = obj.get()['Body'].read()
    
    # Trying to decode file with a list of encodings
    for e in encodings:
        try:
            reqContent = body.decode(e)
        except UnicodeDecodeError:
            print(f'Got unicode error with {e}, trying different encoding')
        else:
            print(f'Opening the file with encoding: {e}')
            break

    # Parsing file libs
    libs = []
    for s in reqContent.splitlines():
        libs.append(s.split("=="))

    print(f"Libs read from {reqKey}: {libs}")
    
    # Delete directory structure (needed if lambda runs on the same vm)
    shutil.rmtree(dirStructure, ignore_errors=True)
    
    # Create standard layer directory structure (per AWS guidelines)
    os.makedirs(dirStructure, exist_ok=True)
    
    # That would be the folder name in S3 bucket
    ts = datetime.today().strftime('%m_%d_%Y_%H_%M_%S')
    
    for lib in libs:
        pipPackage = lib[0]
        packageVersion = lib[1]
        print(f"Installing package = {pipPackage}, version = {packageVersion}")
        
        #Pip install the package, then zip it
        subprocess.call(f'pip3 install {pipPackage}=={packageVersion} -t {dirStructure} --no-cache-dir'.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    shutil.make_archive("/tmp/python", 'zip', "/tmp/python")

    #Put the zip in your S3 Bucket
    try:
        S3.meta.client.upload_file('/tmp/python.zip', s3Bucket, f'{ts}/python.zip')
    except Exception as exception:
        print('Oops, Exception in uploading archive: ', exception)
        raise
    
    # Copy requirement.txt file in the destination folder
    try:
        copy_source = {
            'Bucket': s3Bucket,
            'Key': reqKey
        }
        S3.meta.client.copy(copy_source, s3Bucket, f'{ts}/{reqKey}')
    except Exception as exception:
        print(f'Oops, Exception in copying {reqKey}: ', exception)
        raise
        
    print(f"Archive {ts}/python.zip successfully created!")
            
    return {'statusCode': 200,'body': json.dumps('Success!')}
    