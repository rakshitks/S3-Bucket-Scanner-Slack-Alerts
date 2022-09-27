#!/bin/bash 

#Change channel name CABCDEF and xoxb-xxx token 


#Checking the size of file 
size=$(ls -al | grep s3result.csv | awk {'print $5'})
#echo $size


#If file size is 0 then No s3 buckets are public 
#If not then File with output result is uploaded

if [[ $size > 0 ]]
then
  curl -X POST -H 'Authorization: Bearer xoxb-xxx' \
  -H 'Content-type: application/json' \
  --data '{"channel":"CABCDEF","text":"<!channel> S3 bucket Sanity for Today"}' \
  https://slack.com/api/chat.postMessage
  curl -F file=@s3result.csv -F "initial_comment=S3 bucket are public " -F channels=CABCDEF -H "Authorization: Bearer xoxb-xxx"  https://slack.com/api/files.upload
else
  curl -X POST -H 'Authorization: Bearer xoxb-xxx' \
  -H 'Content-type: application/json' \
  --data '{"channel":"CABCDEF","text":"<!channel> S3 bucket Sanity for Today"}' \
  https://slack.com/api/chat.postMessage
  curl -X POST -H 'Authorization: Bearer xoxb-xxx' \
  -H 'Content-type: application/json' \
  --data '{"channel":"CABCDEF","text":"No s3 buckets are public"}' \
  https://slack.com/api/chat.postMessage

fi
