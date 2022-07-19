import PyPDF2
import requests
import urllib.request
from io import BytesIO
import boto3
import pathlib
import mysql.connector

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

def decidetosavepdf(pdfName,url,txt):
    filename = pdfName
    if (txt.find('£') > 0):
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
    set_object_access_policy(file_name)
        
def set_object_access_policy(object_key):
    """
    This function adds ACL policy for object in S3 bucket.
    :return: None
    """
    s3_client = boto3.client("s3")
    bucket_name = "pdfscrapper"
    object_key = object_key
    response = s3_client.put_object_acl(
        ACL="public-read", Bucket=bucket_name, Key=object_key
    )
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

def update_db_result_after_scrapping(judgment_title, judgment_type,decision_from,published,country,jurishdiction_code,employment_tribunal_decisions,decision_date,pdfurls,pdf_names):
    """
    insert results into database
    """
    mydb = mysql.connector.connect(
      host="127.0.0.1",
      user="root",
      password="password",
      database="pdf_parser" 
    )
    
    mycursor = mydb.cursor()

    sql = "INSERT INTO employment_tribunal_decisions (judgment_title,judgment_type,decision_from,published,country,jurishdiction_code,employment_tribunal_decisions,decision_date,pdfurls,pdf_names) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s)"
    values = (judgment_title,judgment_type,decision_from,published,country,jurishdiction_code,employment_tribunal_decisions,decision_date,pdfurls,pdf_names)

    mycursor.execute(sql,values)

    mydb.commit()

def getcurrentpage():
    """
    get current page from database
    """
    page = None
    
    mydb = mysql.connector.connect(
      host="127.0.0.1",
      user="root",
      password="password",
      database="pdf_parser" 
    )
    mycursor = mydb.cursor()

    sql = "select current_page FROM pages limit 1"

    mycursor.execute(sql)

    myresult = mycursor.fetchall()

    for x in list(myresult[0]):
       page = x.replace("[", "").replace("]", "").replace("\"","").split(",")
    return page

def getremainingPage():
    """
    get current page from database
    """
    page = None
    
    mydb = mysql.connector.connect(
      host="127.0.0.1",
      user="root",
      password="password",
      database="pdf_parser" 
    )
    mycursor = mydb.cursor()

    sql = "select remaining_page FROM pages limit 1"

    mycursor.execute(sql)

    myresult = mycursor.fetchall()

    for x in list(myresult[0]):
       page = x.replace("[", "").replace("]", "").replace("\"","").split(",")
    return page 

def update_page_values(current_page,remaining_page):
    """
    insert data in database
    """
    mydb = mysql.connector.connect(
      host="127.0.0.1",
      user="root",
      password="password",
      database="pdf_parser" 
    )
    mycursor = mydb.cursor()

    sql = """UPDATE pages SET  current_page = %s,remaining_page= %s WHERE id = 1"""

    values = (current_page,remaining_page)

    mycursor.execute(sql,values)

    mydb.commit()

def update_page_status(status):
    """
    insert data in database
    """
    mydb = mysql.connector.connect(
      host="127.0.0.1",
      user="root",
      password="password",
      database="pdf_parser" 
    )
    mycursor = mydb.cursor()

    sql = """UPDATE pages SET  status = %s WHERE id = 1"""

    values = (status)

    mycursor.execute(sql,(values,))

    mydb.commit()

def getstatusPage():
    """
    get current page from database
    """
    status = None
    
    mydb = mysql.connector.connect(
      host="127.0.0.1",
      user="root",
      password="password",
      database="pdf_parser" 
    )
    mycursor = mydb.cursor()

    sql = "select status FROM pages limit 1"

    mycursor.execute(sql)

    myresult = mycursor.fetchall()

    for x in list(myresult[0]):
       status = x.replace("[", "").replace("]", "").replace("\"","").split(",")
    return status

def scrapper_main(pdfName,url):
    decidetosavepdf(pdfName,url,extractPDFContent(url))

