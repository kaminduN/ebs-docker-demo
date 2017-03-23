import logging
import logging.handlers

from wsgiref.simple_server import make_server, WSGIServer
from SocketServer import ThreadingMixIn

# Import the SDK
import boto3
from botocore.exceptions import ClientError

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler 
LOG_FILE = '/tmp/sample-app/sample-app.log'
handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1048576, backupCount=5)
handler.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add Formatter to Handler
handler.setFormatter(formatter)

# add Handler to Logger
logger.addHandler(handler)

# First, we'll start with Client API for Amazon S3.
s3client = boto3.client('s3', region_name='eu-west-1')

s3_list ="ww"

snsclient = boto3.client('sns', region_name='eu-west-1')
sns_list ="pawed"

welcome= """
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
    <body id="sample">
      <div class="textColumn">
        <h1>Congratulations!</h1>
        <p>Your Docker Container is now running in Elastic Beanstalk on your own dedicated environment in the AWS Cloud.</p>
      </div>
    </body>
</html>
"""
def aws_resources():
    global s3_list
    global sns_list
    global welcome

    try:
        list_buckets_resp = s3client.list_buckets()
        s3_list = "</br>".join([bucket['Name'] for bucket in
                            list_buckets_resp['Buckets']])
    except ClientError as e:
        s3_list = e.response['Error']['Message']
        logger.warning('Error', e.response['Error']['Message'])

    try:
        list_topics_resp = snsclient.list_topics()
        sns_list = "</br>".join([topic['TopicArn'] for topic in
                        list_topics_resp['Topics']])
    except ClientError as e:
        sns_list = e.response['Error']['Message']
        logger.warning('Error', e.response['Error']['Message'])

    welcome = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
    <html>
    <head>
      <!--
        Copyright 2012 Amazon.com, Inc. or its affiliates. All Rights Reserved.

        Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

            http://aws.Amazon/apache2.0/

        or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
      -->
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
      <title>Welcome</title>
      <style>
      body {
        color: #ffffff;
        background-color: #E0E0E0;
        font-family: Arial, sans-serif;
        font-size:14px;
        -moz-transition-property: text-shadow;
        -moz-transition-duration: 4s;
        -webkit-transition-property: text-shadow;
        -webkit-transition-duration: 4s;
        text-shadow: none;
      }
      body.blurry {
        -moz-transition-property: text-shadow;
        -moz-transition-duration: 4s;
        -webkit-transition-property: text-shadow;
        -webkit-transition-duration: 4s;
        text-shadow: #fff 0px 0px 25px;
      }
      a {
        color: #0188cc;
      }
      .textColumn, .linksColumn {
        padding: 2em;
        height: 100%;
      }
      .textColumn {
        position: absolute;
        top: 0px;
        right: 50%;
        bottom: 0px;
        left: 0px;

        text-align: right;
        padding-top: 11em;
        background-color: #24B8EB;
      }
      .textColumn p {
        width: 75%;
        float:right;
      }
      .linksColumn {
        position: absolute;
        top:0px;
        right: 0px;
        bottom: 0px;
        left: 50%;
        background-color: #A9A9A9;
      }

      h1 {
        font-size: 500%;
        font-weight: normal;
        margin-bottom: 0em;
      }
      h2 {
        font-size: 200%;
        font-weight: normal;
        margin-bottom: 0em;
      }
      ul {
        padding-left: 1em;
        margin: 0px;
      }
      li {
        margin: 1em 0em;
      }
      </style>
    </head>
    <body id="sample">
      <div class="textColumn">
        <h1>Congratulations!</h1>
        <p>Your Docker Container is now running in Elastic Beanstalk on your own dedicated environment in the AWS Cloud.</p>
      </div>
      <div class="linksColumn"> 
        <h2>S3 Buckets</h2>
    """+\
    s3_list +\
    """
        </br>
        <h2>SNS topics</h2>
        """+\
    sns_list +\
        """
        </br>
        <h2>Documentation</h2>
        <ul>
        <li><a href="http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create_deploy_docker.html">Deploying Docker with AWS Elastic Beanstalk</a></li>
        <li><a href="http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/">AWS Elastic Beanstalk overview</a></li>
        <li><a href="http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/index.html?concepts.html">AWS Elastic Beanstalk concepts</a></li>
        </ul>
    </div>
    </body>
    </html>
    """

def application(environ, start_response):
    path    = environ['PATH_INFO']
    method  = environ['REQUEST_METHOD']
    aws_resources()
    if method == 'POST':
        try:
            if path == '/':
                request_body_size = int(environ['CONTENT_LENGTH'])
                request_body = environ['wsgi.input'].read(request_body_size)
                logger.info("Received message: %s" % request_body)
            elif path == '/scheduled':
                logger.info("Received task %s scheduled at %s", environ['HTTP_X_AWS_SQSD_TASKNAME'], environ['HTTP_X_AWS_SQSD_SCHEDULED_AT'])
        except (TypeError, ValueError):
            logger.warning('Error retrieving request body for async work.')
        response = ''
    else:
        response = welcome
    status = '200 OK'
    headers = [('Content-type', 'text/html')]

    start_response(status, headers)
    return [response]

class ThreadingWSGIServer(ThreadingMixIn, WSGIServer): 
    pass

if __name__ == '__main__':
    httpd = make_server('', 8000, application, ThreadingWSGIServer)
    print "Serving on port 8000..."
    httpd.serve_forever()
