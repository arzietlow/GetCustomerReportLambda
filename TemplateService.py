import json  
import boto3

client = boto3.client('s3', 'us-east-2')

def getTemplateData(reportName):

# A simple function using S3 Select for accessing a specific JSON Object from our S3 file that contains a collection of Report Template objects
# Uses the reportName parameter to query the S3 file and retrieve the correct report format 

# TODO : detailed error logging (if needed)

    #######        RDS TEMPLATES FILENAME         #######
    filename = "RDS_Report_Templates.json"
        
    # Create Query
    exp = 'Select * from S3Object s Where s.type = \'' + reportName+ '\''
    
    select = client.select_object_content(
        Bucket='cmi-portal-report-templates',
        Key=filename,
        Expression= exp,
        ExpressionType='SQL',
        RequestProgress={
            'Enabled': False
        },
        InputSerialization={
            'CompressionType': 'NONE',
            'JSON': {
                'Type': 'DOCUMENT'
            }
        },
        OutputSerialization={
            'JSON': {
                'RecordDelimiter': '\n'
            }
        })
        
    event_stream = select['Payload']
    for event in event_stream:
        if 'Records' in event:
            try:
                data = event['Records']['Payload'].decode("utf-8")
                result = json.loads(data)
            except:
                return None
            
            return result
    
    return None
