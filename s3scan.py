import os
import re
import sys
import warnings
import csv
import re
#Importing all necessary libraries and Defining permissions

from datetime import datetime, timedelta
from os.path import expanduser
from collections import defaultdict

#
SEP = "" * 40
bucket_name=""
msg1=""
status=""
#perms=""
data=[]
EXPLAINED = {
    "READ": "readable",
    "WRITE": "writable",
    "READ_ACP": "permissions readable",
    "WRITE_ACP": "permissions writeable",
    "FULL_CONTROL": "Full Control"
}

GROUPS_TO_CHECK = {
    "http://acs.amazonaws.com/groups/global/AllUsers": "Everyone",
    "http://acs.amazonaws.com/groups/global/AuthenticatedUsers": "Authenticated AWS users"
}

#The function automatically gets the IAM role attached to the Ec2 instance and returns s3 resource and client
def get_s3_obj(is_lambda=False):
    """
    Gets and returns s3 resource and client.

    :return: s3 resource and client instances.
    """
    
    session = boto3.session.Session()
    s3 = session.resource("s3")
    s3_client = session.client("s3")
    return s3, s3_client

#Removing the old csv result file from the server
def tidy(path):
    """
    Removes file described by path.

    :param path: Path to file needs to be removed.
    """
    try:
        os.remove(path)
    except OSError:
        pass

#Checking if Access control is Public
def check_acl(acl):
    """
    Checks if the Access Control List is public.

    :param acl: Acl instance that describes bucket's.
    :return: Bucket's public indicator and dangerous grants parsed from acl instance.
    """
    dangerous_grants = defaultdict(list)
    for grant in acl.grants:
        grantee = grant["Grantee"]
        if grantee["Type"] == "Group" and grantee["URI"] in GROUPS_TO_CHECK:
            dangerous_grants[grantee["URI"]].append(grant["Permission"])
    public_indicator = True if dangerous_grants else False
    return public_indicator, dangerous_grants




#Installing latest version of the Packages Required
def install_and_import(pkg):
    """
    Installs latest versions of required packages.

    :param pkg: Package name.
    """
    import importlib
    try:
        importlib.import_module(pkg)
    except ImportError:
        import pip
        pip.main(["install", pkg])
    finally:
        globals()[pkg] = importlib.import_module(pkg)




#Adding Output to the csv file
def add_to_output(msg, path):
    """
    Displays msg or writes it to file.

    :param msg: Message to handle.
    """
    if path is not None:
        with open(path, "a") as f:
            f.write(msg + '\n')
    else:
        termcolor.cprint(msg)


#Analysing the bucket permissions and also some buckets might give errors you can mention it in bucketname
def analyze_buckets(s3, s3_client, report_path=None):
    """
    Analyses buckets permissions. Sends results to defined output.

    :param s3: s3 resource instance.
    :param s3_client: s3 client instance.
    :param report_path: Path to lambda report file.
    """
    buckets = s3.buckets.all()
    try:
        bucketcount = 0

        for bucket in buckets:
            #print(buckets)
            #location = get_location(bucket.name, s3_client)
            #print(bucket)
            #bucket=s3.Bucket(name='bucketname')
            if str(bucket) == str(s3.Bucket(name='bucketname')) :
                continue
            #print(bucket.name)
            add_to_output(SEP, report_path)
            bucket_acl = bucket.Acl()
            public, grants = check_acl(bucket_acl)

            if public:
                if report_path:
                    msg = "Bucket {}: {}".format(bucket.name, "PUBLIC!")
                    bucket_name=bucket.name
                    status="PUBLIC"
                else:
                    bucket_line = termcolor.colored(
                            bucket.name, "blue", attrs=["bold"])
                    public_ind = termcolor.colored(
                            "PUBLIC!", "red", attrs=["bold"])
                    msg = "Bucket {}: {}".format(
                            bucket_line, public_ind)
                    bucket_name=bucket.name
                    status="PUBLIC"
                add_to_output(msg, report_path)
                #add_to_output("Location: {}".format(location), report_path)

                if grants:
                    for grant in grants:
                        permissions = grants[grant]
                        perm_to_print = [EXPLAINED[perm]
                                         for perm in permissions]
                        if report_path:
                            msg = "Permission: {} by {}".format(" & ".join(perm_to_print),
                                                                (GROUPS_TO_CHECK[grant]))
                            data.append((bucket_name,status,msg))
                            #os.system('echo ')
                        else:
                            msg = "Permission: {} by {}".format(
                                    termcolor.colored(
                                            " & ".join(perm_to_print), "red"),
                                    termcolor.colored(GROUPS_TO_CHECK[grant], "red"))
                            msg1= "Permission: {} by {}".format(" & ".join(perm_to_print),
                                                                (GROUPS_TO_CHECK[grant]))

                            data.append((bucket_name,status,msg1))
                        add_to_output(msg, report_path)
                
            
            bucketcount += 1
        if not bucketcount:
            add_to_output("No buckets found", report_path)
            if report_path:
                msg = "You are safe"
            else:
                msg = termcolor.colored("You are safe", "green")
            add_to_output(msg, report_path)
    except botocore.exceptions.ClientError as e:
        resolve_exception(e, report_path)







#Exception Handling function if keys or Role does not have required Permission or is not present
def resolve_exception(exception, report_path):
    """
    Handles exceptions that appears during bucket check run.

    :param exception: Exception instance.
    :param report_path: Path to report path.
    """
    msg = str(exception)
    if report_path:
        if "AccessDenied" in msg:
            add_to_output("""Access Denied
I need permission to access S3
Check if the Lambda Execution Policy at least has AmazonS3ReadOnlyAccess, SNS Publish & Lambda Execution policies attached

To find the list of policies attached to your user, perform these steps:
1. Go to IAM (https://console.aws.amazon.com/iam/home)
2. Click "Roles" on the left hand side menu
3. Click the role lambda is running with 
4. Here it is
""", report_path)
        else:
            add_to_output("""{}
Something has gone very wrong, please check the Cloudwatch Logs Stream for further details""".format(msg),
                          report_path)
    else:
        if "InvalidAccessKeyId" in msg and "does not exist" in msg:
            add_to_output("The Access Key ID you provided does not exist", report_path)
            add_to_output("Please, make sure you give me the right credentials", report_path)
        elif "SignatureDoesNotMatch" in msg:
            add_to_output("The Secret Access Key you provided is incorrect", report_path)
            add_to_output("Please, make sure you give me the right credentials", report_path)
        elif "AccessDenied" in msg:
            add_to_output("""Access Denied
I need permission to access S3
Check if the IAM user at least has AmazonS3ReadOnlyAccess policy attached

To find the list of policies attached to your user, perform these steps:
1. Go to IAM (https://console.aws.amazon.com/iam/home)
2. Click "Users" on the left hand side menu
3. Click the user, whose credentials you give me
4. Here it is
        """, report_path)
        else:
            add_to_output("""{}
Check your credentials in ~/.aws/credentials file

The user also has to have programmatic access enabled
If you didn't enable it(when you created the account), then:
1. Click the user
2. Go to "Security Credentials" tab
3. Click "Create Access key"
4. Use these credentials""".format(msg), report_path)

#Main fucntion which mentions packages to get Terminal colors for the output results It also calls analyze_buckets and get_s3_obj functions
def main():
    if sys.version[0] == "3":
        raw_input = input
    packages = ["boto3", "botocore", "termcolor", "requests"]
    for package in packages:
        install_and_import(package)
    s3, s3_client = get_s3_obj()
    analyze_buckets(s3, s3_client)

Function where execution starts . You can define your output file name here
if __name__ == "__main__":
    main()
    with open("s3result.csv", "wt") as fp:
        writer = csv.writer(fp, delimiter=",")
        # writer.writerow(["your", "header", "foo"])  # write header
        writer.writerows(data)
    
