#Python script to conect to Capital One API 
import http.client
import urllib.parse
import json
import datetime
import sys


def addTransaction(result, transaction_line, ignore_donuts):
	if ignore_donuts and transaction_line['merchant'] in {'Krispy Kreme Donuts', 'DUNKIN #336784'}:
		return

	amount = transaction_line['amount']
	date = datetime.datetime.strptime(transaction_line['transaction-time'], "%Y-%m-%dT%H:%M:%S.000Z").date()
	key = str(date.year) + "-" + str(date.month)
	if key in result:
		if amount > 0:
			tempAmount = result[key]['income'] + amount
			result[key]['income'] = tempAmount
		else:
			tempAmount = result[key]['spent'] + amount
			result[key]['spent'] = tempAmount

	else:
		value = {}
		if amount > 0:
			value['spent'] = 0
			value['income'] = amount
		else:
			value['spent'] = 0
			value['income'] = amount
		result[key] = value

	return

def computeAverage(result):
	totalSpent = 0
	totalIncome = 0
	count = 0

	for entry in result:
		count+= 1
		totalSpent += result[entry]['spent']
		totalIncome += result[entry]['income']


	averageSpent = totalSpent / count
	averageIncome = totalIncome / count

	value = {'spent': averageSpent, 'income': averageIncome}
	return value

def callEndpoint(url, args):
	headers = {"Content-type": "application/json", "Accept": "application/json"}
	conn = http.client.HTTPSConnection("2016.api.levelmoney.com")
	conn.request("POST", url, json.dumps(args), headers)
	response = conn.getresponse()
	response_body = json.loads(response.read().decode("utf-8"))
	return response_body

def writeFormatedLine(col1, col2, col3, col4, col5):
	output_file.write('{0:7s}     {1:8s}  ${2:10.2f}     {3:8s}  ${4:10.2f}'.format(col1, col2, col3, col4, abs(col5)))
	output_file.write('\n')



# Global variables to store URI's and email/password for calling APIs
ignore_donuts = '--ignore-donuts' in sys.argv

#Strings used in API calls
login_email = "interview@levelmoney.com"
login_password = "password2"
api_token = "AppTokenForInterview"

login_url = "/api/v2/core/login"
get_all_transactions_url = "/api/v2/core/get-all-transactions"


#Make API calls
login_response = callEndpoint(login_url, {"email":  login_email, "password":  login_password, "args": {'api-token': api_token}})
get_all_transactions_response = callEndpoint(get_all_transactions_url, {'args': {'uid': login_response['uid'], 'token': login_response['token'], 'api-token': api_token}})


#Open destination file
output_file = open("output.txt", "w")

#Parse response
transactions = get_all_transactions_response['transactions']
result = {}

#Parse income/expendatures from transactions into aggregate result
for transaction in transactions:
	addTransaction(result, transaction, ignore_donuts)

#Write aggregate result to file
for entry in sorted(result):
	writeFormatedLine(entry, 'income', result[entry]['income'], 'spent', result[entry]['spent'] )

average = computeAverage(result)
writeFormatedLine('average', 'income', average['income'], 'spent', average['spent'])

output_file.close()
