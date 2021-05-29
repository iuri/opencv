
import os, requests, time, socket
import config
import logging

image_path = './images'
os.chdir(".")

if not os.path.isdir(image_path):
    #now = datetime.datetime.now().strftime("%y%m%d%H%M")
    os.umask(0)
    os.makedirs(image_path, mode=0o777, exist_ok=False)

while True:
    for f in os.listdir(image_path):
        file_path = image_path + '/' + f
        if os.path.splitext(file_path)[1].lower() in ('.jpg', '.jpeg', '.png'):
            if os.path.isfile(file_path):
                try:                    
                    headers = {
                        'Content-Location': socket.gethostname(),
                        'Timestamp': str(time.time()),
                        'Authorization': config.auth_token                     
                    }
                
                    print("Sending file...", file_path)
                    with open(file_path,'rb') as fp:
                        file_dict = {'file': (f, fp, 'multipart/form-data')}
                        response = requests.post(config.url, files=file_dict, headers=headers)
                        fp.close()
                        if response.status_code == 200 and response.text == 'ok':
                            os.remove(file_path)     
                            del headers
                            del response
                            del file_path
                except Exception as e:
                    logging.error('Caught exception: ' + str(e))
                    #raise Exception('Caught exception: '.format(e)) from None
                    time.sleep(3)
