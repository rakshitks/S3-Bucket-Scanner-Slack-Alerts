# S3-Bucket-Scanner-Slack-Alerts
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A python program to find Public S3 Buckets
Receive Slack alerts whenever S3 buckets become Public

## Description
Automated script which continously montiors the S3 bucket and creates an Slack alert which contains detailed report of S3 buckets which are made public with respective permission available to everyone.

## Usage
Make sure that you change channel id (CABCDEF) and Slack authorization token (xoxb-xx) in the script
1. Normal Usage

``` bash s3automation.sh ```

2. Using crontab 

```crontab -e```

This will run the task everyday at 10:30 AM

```30 10 * * * /root/s3automation.sh```


## Implementation 
You can refer this article for detailed implementation 

## Features
* Continuous Monitoring of S3 Buckets so that your data remains safe from attackers
* Slack alerts when S3 Buckets remain public
* CSV report of S3 Buckets is generated which contains name of the bucket which is public with the Permissions which are available to Everyone.


## License

MIT






