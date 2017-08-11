# ebs-docker-demo
 AWS Elastic Beanstalk Docker container application sample.
 This application create a AWS Cloudwatch log group with application name and stream the logs to that. 

## To deploy

* Using AWS Elastic Beanstalk Command Line Interface (EB CLI)

  * eb init
  * eb create 'environment name'

  or

  * eb deploy 'environment name'

* Manual deploy
Zip the contents of the file and upload it as the payload in the aws console.
