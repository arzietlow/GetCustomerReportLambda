import json  
from boto3 import client as boto3_client
from TableFunctions import makeReportColumnData
from TemplateService import getTemplateData

lambda_client = boto3_client('lambda', region_name="us-east-2")

def getReportTable(reportName, params): 

    # params was set like this: params.append(qsp['pageNum'], qsp['rowsPerPage'], qsp['searchCriteria'], qsp['sortBy'], qsp['sortOrder'])
    pageNum = params[0]
    rowsPerPage = params[1]
    searchCriteria = params[2]
    sortBy = params[3]
    sortOrder = params[4]
    smartSearch_input = ""
        
    reportTemplate = getTemplateData(reportName) # External call to TemplateService.py 
    headerInfo = reportTemplate['headerInfo']
    
    # Extract relevant information to construct data bundle for table
    columnMap = headerInfo['columns']
    columnLabels = list(columnMap.keys())
    columns = list(columnMap.values())
    tableName = reportTemplate['tableName']
    
    # Apply default sorting values if none have been given
    if sortBy == "": sortBy = headerInfo['defaultSortColumn']
    if sortOrder == "": sortOrder = headerInfo['defaultSortOrder']
    
    # Construct relevant args to retrieve the data from DataService
    colString = (str(columns)[1:-1]).replace("'","")   # Removes brackets, apostrophies surrounding each element in the columnLabels list
    
    columnData = makeReportColumnData(columns, columnLabels) # External call TableFunctions.py
    
    # Determine if we're doing smartsearch: 
    # TODO: Redesign this functionality according to UI
    # TODO: better injection protection?
    if '=' in searchCriteria:
        pair_list = [tuple(x.split('=')) for x in searchCriteria.split(';')]

        validPairs = []
        for pair in pair_list:
            if (not all(pair)) or ('%' in pair[1]) or ("'" in pair[1]) or (not pair[0] in columnMap):
                continue
            toAdd = (columnMap[pair[0]], pair[1])
            validPairs.append(toAdd)
            
        smartSearch_input = str(validPairs)
        searchCriteria = ""
    
    # Copy those args into a data request structure
    dataQueryString = {
        'smartSearch' : smartSearch_input,
        'columns' : colString,
        'table' : tableName,
        'pageNum' : pageNum,
        'rowsPerPage' : rowsPerPage,
        'searchCriteria' : searchCriteria,
        'sortBy' : sortBy,
        'sortOrder' : sortOrder
    }
    
    # Get Data using DADataService Lambda
    data_response = lambda_client.invoke(
        FunctionName="DADataService",
        InvocationType='RequestResponse',
        Payload=json.dumps(dataQueryString)
    )
    
    # TODO: Ensure response is valid here
    
    # Parse response payload into usable format
    data_string = data_response["Payload"].read().decode('utf-8')
    parsed_data = json.loads(data_string)
    
    totalRows = len(parsed_data)
    if totalRows > 1 :
        totalRows = parsed_data[-1]['totalRows']
        parsed_data = parsed_data[:-1]
    else:
        totalRows = 0
        parsed_data = []
    
    # Build required data bundle
    data_bundle = {
        "columnData" : columnData,
        "rowData" : parsed_data,
        "totalRows" : totalRows
    }
    
    ###### Required response headers to enable CORS without chrome extension #####
    headers = {
        'Content-Type': 'application/json',
        "Access-Control-Allow-Origin" : "*", # Required for CORS support
        "Access-Control-Allow-Methods" : 'OPTIONS,GET,POST',
        "Access-Control-Allow-Headers" : "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,customCognitoToken"
      }
    
    result = {
        "headers": headers,
        "data": data_bundle,
    }
    
    return result
    