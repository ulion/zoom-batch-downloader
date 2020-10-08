import requests 
import shutil
import datetime
import os
from time import sleep

# Put your JWT token that you get from https://marketplace.zoom.us/ here. 
JWT = '##########'

# Put your USER ID that you get from the API. 
USERID = '##########'


headers = {
		'Authorization': 
		'Bearer {}'.format(JWT),
		'content-type':
		'application/json',
	}

# Put your own download path here, I used an external hard drive so mine will differ from yours
PATH = '/Volumes/Ext3/Zoom/'



def main():
	for year in range(2018,2022):
		for month in range(1,13):
			next_month = month + 1
			next_year = year

			if month == 12:
				next_month = 1
				next_year = year + 1

			start_date = datetime.datetime(year,month,1)
			next_date = datetime.datetime(next_year,next_month,1)

			get_recording(start_date, next_date)


def get_recording(start_date, next_date):
	
	date_string = '%Y-%m-%d'
	url = 'https://api.zoom.us/v2/users/{}/recordings?from={}&to={}&page_size=300&'.format(
				USERID,
				start_date.strftime(date_string),
				next_date.strftime(date_string)
			)

	print(url)

	response = requests.get(
		url,
		headers=headers
	)

	data = response.json()
	# print('page_count: ', data['page_count'])
	# print('page_size: ', data['page_size'])
	# print(len(data['meetings']))
	# print(data['from'])
	# print(data['to'])

	for meeting in data['meetings']:
		for record in meeting['recording_files']:
			if record['status'] != 'completed':
				continue

			print(record)
			filetype = record['file_type'].lower()
			filetype = 'txt' if filetype == 'chat' else filetype
			download_recording(
				record['download_url'], 
				'{}.{}'.format(record['recording_start'].replace(':','-'), filetype),
				record['file_size']
			)


def download_recording(download_url, filename, filesize):
	print(download_url)
	download_access_url = '{}?access_token={}'.format(download_url, JWT)
	print(download_access_url)
	local_filename = '{}/{}/{}'.format(PATH, filename[:7], filename)
	try:
		if os.path.getsize(local_filename) == filesize:
			print('SKIP EXISTED: {}'.format(filename))
			return
	except:
		pass

	total, used, free = shutil.disk_usage("/")
	print(free)
	while free < filesize + 2**30:
		print('Waiting disk space ...')
		sleep(30)
		total, used, free = shutil.disk_usage("/")
		print(free)

	with requests.get(download_access_url, stream=True) as r:
		os.makedirs(os.path.dirname(local_filename), exist_ok=True)
		with open(local_filename + '.tmp', 'wb') as f:
			shutil.copyfileobj(r.raw, f)
		os.rename(local_filename + '.tmp', local_filename)

	   
if __name__ == '__main__':
	main()




