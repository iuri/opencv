from flask import render_template, jsonify, abort, request, url_for, flash, redirect, send_from_directory, Blueprint
import os, requests, json

from werkzeug.utils import secure_filename

import time
import logging


# Boto3 libraries to support AWS Rekognition
import boto3
from botocore.exceptions import ClientError
from os import environ


main = Blueprint('main', __name__)


@main.route("/")
@main.route("/home")
def home():
    return render_template('index.html')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


os.environ['AWS_PROFILE'] = "VideoRekognition"
os.environ['AWS_DEFAULT_REGION'] ="us-east-1"
 
FEATURES_BLACKLIST = ("Landmarks", "Emotions", "Pose", "Quality", "BoundingBox", "Confidence")



####
### AWS Rekognition
####




####
### Faces
####


def match_faces(filename, bucket="qonteoimages", collectionId="SamsungRekCollection", region="us-east-1"):
    try:
        rek_client = boto3.client("rekognition", region)
        # print("FILENAME", filename)
        # match_response = rek_client.search_faces_by_image(CollectionId=collectionId,Image={'Bytes': image.read()}, MaxFaces=1,FaceMatchThreshold=85)
        match_response = rek_client.search_faces_by_image(
            CollectionId=collectionId,
            Image={"S3Object": {
                "Bucket": bucket,
                "Name": filename
            }               
        },
        MaxFaces=1,
        FaceMatchThreshold=90)
        
        if match_response['FaceMatches']:
            print('Hello, ',match_response['FaceMatches'][0]['Face']['ExternalImageId'])
            print('Similarity: ',match_response['FaceMatches'][0]['Similarity'])
            print('Confidence: ',match_response['FaceMatches'][0]['Face']['Confidence'])
            return match_response['FaceMatches'][0]
        else:
            print('No faces matched')
            return ''
    except Exception as e:
        logging.error('Caught Exception: ' + str(e))
        #raise Exception('Caught Exception: '.format(e)) from None
       # time.sleep(3)
        
    
def detect_faces(bucket, filename, collection_id="SamsungRekCollection", attributes=['ALL'], region="us-east-1"):
  rek_client = boto3.client("rekognition", region)
  
  response = rek_client.detect_faces(
    Image={
      "S3Object": {
        "Bucket": bucket,
        "Name": filename,
      }
    },
    Attributes=attributes,
  )
  print('FILE ', filename)
  print("FACE DETAILS ", response)
  
  if response['FaceDetails'] != []:
      match = match_faces(filename, bucket)
      print("MATCHING RESULTS ", match)


      if match != '' and match != 'None':
          if match['Similarity'] > 99 and match['Face']['Confidence'] > 99:
              # Face already exists. Append its details with match
              print("Face Exists")
              result = {**match, **response}
              return json.dumps({"FaceRecords": [result]})
          else:
              print("False Match! Person may not be the same")
              print("No matches")
              # No matches resulted. Then it indexes new Face
              index = rek_client.index_faces(
                  CollectionId=collection_id,
                  Image={'S3Object':{
                      'Bucket':bucket,
                      'Name':filename}
                  },
                  ExternalImageId=filename,
                  MaxFaces=1,
                  QualityFilter="AUTO",
                  DetectionAttributes=['ALL'])
              # result = {**index, **response}
              # return json.dumps(result)
              return json.dumps(index)


      
  return 'noface'



@main.route('/index-faces', methods=['POST'])
def index_faces(bucket="qonteoimages", region="us-east-1"):
    # print("Running index_faces ...")
    if request.method == 'POST':
        rek_client = boto3.client("rekognition", region)
        s3_client = boto3.client("s3", region)
        
        response = rek_client.list_collections(MaxResults=10)

        # print("CollectionID", request.form['collection_id'])
        # print("LIST ", response['CollectionIds'])

        if request.form['collection_id'] in response['CollectionIds']:

            all_objects = s3_client.list_objects(Bucket=bucket)
            # print("ALL OBJECTS", all_objects)
            for content in all_objects['Contents']:
                # print("CONTENT ", content)
                collection_name = content['Key']
                collection_image = content['Key']
                if collection_image:
                    label = collection_name
                    # print('indexing: ',label)
                    image = content['Key']    
                    index_response=rek_client.index_faces(CollectionId=request.form['collection_id'],
                                                          Image={'S3Object':{'Bucket':bucket,'Name':image}},
                                                          ExternalImageId=label,
                                                          MaxFaces=1,
                                                          QualityFilter="AUTO",
                    DetectionAttributes=['ALL'])
                    
                    # print('FaceId: ',index_response['FaceRecords'][0]['Face']['FaceId'])
                    
                    return redirect('http://aws.qonteo.com/collections-list?msg=success');
                
    return redirect('http://aws.qonteo.com/collections-list?msg=failed');



def list_faces(collection_id, region="us-east-1", next_token="", max_results=123):
    # print("Running function list_faces ...")
    rek_client = boto3.client("rekognition", region)
    response = rek_client.list_faces(
        CollectionId=collection_id,
        MaxResults=max_results)
    return response['Faces']


@main.route("/face-one", methods=['POST'])
def face_one():
    # print("Running face-one ...")
    # print("REQUEST ", request.args)
    image_dir = url_for('static', filename=request.form['face']) 
    filename= image_dir

    return render_template('face-one.html', filename=filename, msg='')






def face_delete2(face_id, collection_id, region="us-east-1"):
    # print('Attempting to delete face ' + face_id)
    client=boto3.client('rekognition', region)
    status_code=0
    try:
        response=client.delete_faces(
            CollectionId=collection_id,
            FaceIds=[face_id]
        )
        # print("Deleted Faces:", response['DeletedFaces']);
        status_code=1
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print ('The face ' + face_id + ' was not found ')
        else:
            print ('Error other than Not Found occurred: ' + e.response['Error']['Message'])
        status_code=e.response['ResponseMetadata']['HTTPStatusCode']
    return(status_code)



@main.route('/face-delete', methods=['POST'])
def face_delete():
    if request.method == 'POST':
        if request.form['face_id'] == '':
            flash('FaceId must not be empty!')
        else:
            # Creare new colection
            # print("Deleting Face")
            if face_delete2(request.form['face_id'], request.form['collection_id']):
                return redirect('http://aws.qonteo.com/collection-one?msg=success&collection_id=SamsungRekCollection')
    return redirect('http://aws.qonteo.com/collection-one?msg=failed&collection_id=SamsungRekCollection')






####
### Collections
####








def collection_delete2(collection_id, region="us-east-1"):
    # print('Attempting to delete collection ' + collection_id)
    client=boto3.client('rekognition', region)
    status_code=0
    try:
        response=client.delete_collection(CollectionId=collection_id)
        status_code=response['StatusCode']
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            print ('The collection ' + collection_id + ' was not found ')
        else:
            print ('Error other than Not Found occurred: ' + e.response['Error']['Message'])
        status_code=e.response['ResponseMetadata']['HTTPStatusCode']
    return(status_code)



@main.route('/collection-delete', methods=['POST'])
def collection_delete():
    if request.method == 'POST':
        if request.form['collection_id'] == '':
            flash('Collection must not be empty!')
            return redirect('http://aws.qonteo.com/collections-list')
        else:
            # Creare new colection
            print("Delete Collection")
            if collection_delete2(request.form['collection_id']):
                return redirect('http://aws.qonteo.com/collections-list')
            
    return




def collection_create(collection_id, attributes=['ALL'], region="us-east-1"):
    rekognition = boto3.client("rekognition", region)

    #Create a collection
    print('Creating collection:' + collection_id)
    response=rekognition.create_collection(
        CollectionId=collection_id,
        Tags={
            'company': 'Qonteo',
            'project': 'Samsung'
        }
    )
    print('Collection ARN: ' + response['CollectionArn'])
    print('Status code: ' + str(response['StatusCode']))
    print('Done...')
    return 1




@main.route('/collection-new', methods=['GET', 'POST'])
def collection_new():
    if request.method == 'POST':
        print("COLLECTION ID", request.form['collection_id'])
        # check if the post request has the file part
        if request.form['collection_id'] == '':
            flash('ID must not be empty!')
            return redirect(request.url)
        else:
            # Creare new colection
            print("Create Collection")
            if collection_create(request.form['collection_id']):
                return redirect('http://aws.qonteo.com/collections-list')
            
    return '''
    <!doctype html>
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <title>Create AWS Colelction</title>
      </head>
      <body>
        <h1>Create a new Collection</h1>
        <form method=post>
          <input type=text id=collection_id name=collection_id>
          <input type=submit value=Submit>
        </form>
      </body>
    </html>
    '''




@main.route("/collections-list")
def collections_list(region="us-east-1", max_results=123):
    # https://docs.aws.amazon.com/pt_br/rekognition/latest/dg/list-collection-procedure.html
    rekognition = boto3.client("rekognition", region)
    response = rekognition.list_collections(MaxResults=max_results)
    collections=response['CollectionIds']
  #  done = False        
  #  while done==True:
  #      for collection in collections:            
  #          collections.append(collection)
  #      if 'NextToken' in response:
  #          nextToken=response['NextToken']
  #          response=rekognition.list_collections(NextToken=nextToken,MaxResults=max_results)
  #      else:
  #          done = True

    
    return render_template('collections-list.html', collections=collections, total=len(collections), msg='')



@main.route("/collection-one")
def collection_one():
    # print("Running collection-one ...")
    # print("REQUEST ", request.args)
    collection_id=request.args.get('collection_id')
    faces = list_faces(collection_id)
    # print("FACES ", faces)
    return render_template('collection-one.html', collection_id=collection_id, faces=faces, total=len(faces), msg='')






####
### Labels
####


def detect_labels(bucket, filename, attributes=['ALL'], region="us-east-1"):
  rekognition = boto3.client("rekognition", region)

  response = rekognition.detect_labels(
    Image={
      "S3Object": {
        "Bucket": bucket,
        "Name": filename,
      }
    },
    MaxLabels=123,
    MinConfidence=55
  )

  x = response['Labels']
  for i in range(len(x)):
    y = x[i]
    print(y['Name'])
    if (y['Name'] == 'Face'):
        return detect_faces(bucket, filename)
  #return response['Labels']
  return 'noface'
























####
### Upload File
####
                
# https://realpython.com/python-requests/
def upload_face(json_text):
    #  print("HEADERS ", request.headers)
    #  print("HEADERS AUTH ", request.headers['Authorization'] )
    # print("Sending JSON ...")
    if request.headers['Authorization']:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': request.headers['Authorization'],
            'Timestamp': request.headers['Timestamp'],
            'Content-Location': request.headers['Content-Location']
        }

        payload = {'data': json.dumps({'data': json_text})}
        response = requests.post("https://dashboard.qonteo.com/REST/import-face-aws", data=payload, headers=headers)
        # print(response.status_code)
        # print("RESPNOSE FROM ZILL ", response.text)
    
        if response.status_code == 200:
            if response.text == 'ok':
                return 1
    return 0
    
    

#https://roytuts.com/python-flask-rest-api-file-upload/
@main.route('/upload-file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #Get current dir: print(os.path.abspath(os.getcwd()))
            file.save(os.path.join('/home/ec2-user/qonteo/webapp/main/uploads/images/', filename))
            #return redirect(url_for('uploaded_file', filename=filename))
            json_text = detect_labels('qonteoimages', filename)
            if json_text != '':
                if upload_face(json_text):
                    return "ok"
            if json_text == 'noface':
                return "ok"            
            return "nok"
    return '''
    <!doctype html>
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <title>Upload new File</title>
      </head>
      <body>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=Upload>
        </form>
      </body>
    </html>
    '''

