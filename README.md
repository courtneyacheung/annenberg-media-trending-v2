## Description ##
This project finds uscannenbergmedia.com's trending articles based on viewership data. <br/>

## Structure ##
main.py finds the top articles <br/>
tempate.yaml creates the following AWS resources: lambda function, s3 bucket, and event rule <br/>

## Requirements ##
AWS CLI <br/>
AWS SAM CLI <br/>
Google Analytics credentials (ask for file)<br/>

## Run ##
Option 1: deploy template.yaml on PyCharm <br/>
Option 2: run
/usr/local/bin/sam sync --stack-name annenberg-trending-lambda --template-file <path to template.yaml> --s3-bucket annenberg-trending-lambda --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND --no-dependency-layer --no-watch
