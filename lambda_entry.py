from ReportService import getReportTable
import json

# MUST have keys called 'rowsPerPage', 'pageNum', 'searchCriteria', 'sortBy', and 'sortOrder' 
#           -- the last 3 can be empty strings (sort fields will be filled to defaults based on report format from s3 if they're empty)
def lambda_handler(event, context):

    reportName = event['ReportName']
        
    # All requests must have all of the following keys (values should only be required for ReportName, pageNum, rowsPerPage)
    params = []
    params.extend([event['pageNum'], event['rowsPerPage'], event['searchCriteria'], event['sortBy'], event['sortOrder']])
    
    return getReportTable(reportName, params)