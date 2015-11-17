
############
###### Use the data file user_edges to extract the inDeg,OutDeg of every user node
## In addition, extracts the sum of money (Bitcoin) a user has sent or received.
# Extracts the date when user was First active and last active.

#####
## The data file is from cs224W which had already done clustering of the addresses into users.
#

import pandas as pd
import numpy as np

SOURCE_FILE_ADDRESS="user_edges.csv"
DEST_FILE_ADDRESS="User_STATS.csv"

#COLOUMN_DICT={'tx_key':0,'source':1,'des':2,'value':4,'date':3}

def loadData(address=SOURCE_FILE_ADDRESS):
	df=pd.read_csv(address, header=None)
	return df

def combine2(df1,df2):
	return pd.merge(df1,df2,left_index=True,right_index=True, how='outer')


def JustDoIt():

	bitcoin_data=loadData()
	print "Loaded Bitcoin data from File:\t" + SOURCE_FILE_ADDRESS

	spent_money=bitcoin_data[[1,4]].groupby(1).aggregate(np.sum)
	print "Done with total spends!"
	received_money=bitcoin_data[[2,4]].groupby(2).aggregate(np.sum)
	print "Done with total Received!"

	result = combine2(spent_money,received_money)

	first_spend_date = bitcoin_data[[1,3]].groupby(1).aggregate(np.min)
	result=combine2(result,first_spend_date)
	last_spend_date = bitcoin_data[[1,3]].groupby(1).aggregate(np.max)
	result=combine2(result,last_spend_date)
	print "Done with spend dates!"

	first_received_date=bitcoin_data[[2,3]].groupby(2).aggregate(np.min)
	result=combine2(result,first_received_date)
	last_received_date=bitcoin_data[[2,3]].groupby(2).aggregate(np.max)
	result=combine2(result,last_received_date)
	print "Done with received dates!"

	number_paid=bitcoin_data[[1,2]].groupby(2).aggregate('count')
	result=combine2(result,number_paid)
	number_spent=bitcoin_data[[1,2]].groupby(1).aggregate('count')
	result=combine2(result,number_spent)
	print "Done with number of edges(transactions)."

	#Fill the Nan values with 0
	result=result.fillna(value=0)
	result.index.name="user"

	myHeader=["Money_spent","Money_Received","First_spend_date","Last_spend_date",\
	"first_received_date","last_received_date","num_received_money","number_paid_money"]
	result.to_csv(DEST_FILE_ADDRESS,header=myHeader)

	print "Finished Creating file:\t"+DEST_FILE_ADDRESS
	return


if __name__ == "__main__":
	JustDoIt()

