import PyPDF2
import requests
import urllib.request
from io import BytesIO
import boto3
import pathlib

def extractPDFContent(url):
    txt = ""
    response = requests.get(url)
    my_raw_data = response.content

    with BytesIO(my_raw_data) as data:
        read_pdf = PyPDF2.PdfFileReader(data,strict=False)
        
        for page in range(read_pdf.getNumPages()):
            txt =txt + read_pdf.getPage(page).extractText()

    return  txt
  
def download_file(download_url, filename):
    response = urllib.request.urlopen(download_url)    
    file = open("pdfToUpload/"+filename + ".pdf", 'wb')
    file.write(response.read())
    file.close()

def decidetosavepdf(url,txt):
    filename = "Test"
    if (txt.find('Claimant') > 0):
        print('upload this link to s3')
        download_file(url, filename)
        UploadToS3(f"pdfToUpload/{filename}.pdf", "pdfscrapper")
    else:
        print('this wont be uploaded')


def UploadToS3(file_name, bucket, object_name=None, args=None):

    s3_client = boto3.client("s3", region_name="us-east-2")

    if object_name is None:
        object_name = file_name

    s3_client.upload_file(file_name, bucket, object_name, ExtraArgs=args)
        

def createS3Bucket():

    resource = boto3.resource("s3", region_name="us-east-2")

    bucket_name = "pdfscrapper"
    location = {'LocationConstraint': "us-east-2"}
    s3_bucket = resource.Bucket(bucket_name)
    s3_bucket.delete()
    bucket = resource.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration=location)

    print("Amazon S3 bucket has been created")



url ='https://assets.publishing.service.gov.uk/media/62bec613e90e073f5e9e78a0/Mr_S_Sieja_-__v-_Kovacs_Group_Ltd_-_3306375-2020_-_Judgment.pdf'
decidetosavepdf(url,extractPDFContent(url))

