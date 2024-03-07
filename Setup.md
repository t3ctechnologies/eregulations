# Set up a new environment from scratch

This document with provide instructions to set up the environment from scratch


## AWS 
##### Parameter Store setup
The application relies on several AWS Parameter Store Key value pairs. These must be populated prior to running the CloudFormation to setup the environment. See [SSM Parameter ](/solution/stored_parameter.yml)  and s [sample](parameters.yml) parameters file Cloud Formation template. After cloning this repo, edit all the parameters file's required fields to values that correspond to your environment 
Execute this with command
```
aws cloudformation create-stack --stack-name MyStack --template-body file://stored_parameter.yml --parameters file://parameters.yml --capabilities CAPABILITY_IAM
```
##### AWS GitHub Actions
This step will ensure Github has the necessary permissions to execute AWS CloudFormation templates on your behalf. Edit the file [cf.yml](/solution/cf.yml) to match your repository
```
aws cloudformation create-stack --stack-name GitHubStack --template-body file://cf.yml --capabilities CAPABILITY_IAM
```

## Github Environment Variables

The following environment variables are required to work
##### S3 Bucket Name: 
AWS S3 Bucket Names are globally unique and  bucket Names to be used by the application must be defined in the Github environment variables prior to installing the application and resources on AWS


