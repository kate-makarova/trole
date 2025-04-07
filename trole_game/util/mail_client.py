import boto3
from botocore.exceptions import ClientError

class MailClient:
    def __init__(self):
        self.sender = "Trole Online System <system@trole.online>"
        self.aws_region = "us-east-1"
        self.charset = "UTF-8"
    
    def send(self, subject, body_text, body_html, recipient):
        client = boto3.client('ses', region_name=self.aws_region)

        try:
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        recipient,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': self.charset,
                            'Data': body_html,
                        },
                        'Text': {
                            'Charset': self.charset,
                            'Data': body_text,
                        },
                    },
                    'Subject': {
                        'Charset': self.charset,
                        'Data': subject,
                    },
                },
                Source=self.sender,
            )
        except ClientError as e:
            print(e.response['Error']['Message'])
            return False
        else:
            return True