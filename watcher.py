
import os, requests, time, socket
import logging
import config

# logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='/var/log/watcher.log',level=logging.INFO)

image_path = './images'
os.chdir(".")

if not os.path.isdir(image_path):
    #now = datetime.datetime.now().strftime("%y%m%d%H%M")
    os.umask(0)
    os.makedirs(image_path, mode=0o777, exist_ok=False)

while 1:
    for f in os.listdir(image_path):
        file_path = image_path + '/' + f
        if os.path.splitext(file_path)[1].lower() in ('.jpg', '.jpeg', '.png'):
            if os.path.isfile(file_path):
                # print("HOST", socket.gethostname())
                try:                    
                    headers = {
                        'Content-Location': socket.gethostname(),
                        'Timestamp': str(time.time()),
                        'Authorization': config.auth_token                     
                    }
                
                    # logging.info('Sending file... %s' % file_path)
                    print("Destination", config.url)
                    with open(file_path,'rb') as fp:
                        file_dict = {'upload_file': (f, fp, 'multipart/form-data')}
                        response = requests.post(config.url, files=file_dict, headers=headers)
                        fp.close()
                        # logging.info('STATUS %s' % response.status_code)
                        print('STATUS %s' % response.status_code)
                        # print('RESULT %s' % response.text)
                        if response.status_code == 200 and response.json()['faces'] != []:
                            print('Removing file... %s' % file_path)
                            os.remove(file_path)     
                            del headers
                            del response
                            del file_path
                            time.sleep(2)
                except:
                    time.sleep(10)
