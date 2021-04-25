
import os, requests, time, socket
import config
image_path = './images'
while 1:
    for f in os.listdir(image_path):
        file_path = image_path + '/' + f
        print("FILEPATH ", file_path)
        if os.path.splitext(file_path)[1].lower() in ('.jpg', '.jpeg', '.png'):
            if os.path.isfile(file_path):
                try:                    
                    headers = {
                        'Content-Location': socket.gethostname,
                        'Timestamp': str(time.time()),
                        'Authorization': config.auth_token                     
                    }
                    
                    print("Sending file...")
                    with open(file_path,'rb') as fp:
                        file_dict = {'file': (f, fp, 'multipart/form-data')}
                        response = requests.post(config.url, files=file_dict, headers=headers)
                    fp.close()
                    if response.status_code == 200 and response.text == 'ok':
                        os.remove(file_path)     
                        del headers
                        del response
                        del file_path
                except:
                    time.sleep(10)
