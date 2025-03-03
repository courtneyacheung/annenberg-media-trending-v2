## Description ##
This project finds uscannenbergmedia.com's trending articles based on viewership. <br/>
Data is from the past 7 days, with viewership of recent articles weighted higher than older articles. <br/>
Viewership data is updated every two hours.

## Structure ##
main.py finds the top articles <br/>
template.yaml creates the following AWS resources: lambda function, s3 bucket, and event rule <br/>
arc_display.html contains code for the Arc html box

## Requirements ##
AWS CLI <br/>
AWS SAM CLI <br/>
Google Analytics API credentials file (not included in public repo)<br/>

## Run ##
Option 1: deploy template.yaml on PyCharm <br/>
Option 2: run
/usr/local/bin/sam sync --stack-name annenberg-trending-lambda --template-file <path to template.yaml> --s3-bucket annenberg-trending-lambda --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND --no-dependency-layer --no-watch
