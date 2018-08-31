import os
import sys
import requests
import time
import threading
import json
from flask import Flask

application = Flask(__name__)
CURRENTDIR = os.path.dirname(os.path.abspath(__file__))
if CURRENTDIR not in sys.path:
        sys.path.append(CURRENTDIR)

store_dir = os.getcwd()

def check_network(url='http://www.google.com/', timeout=5):
    try:
        _ = requests.get(url, timeout=timeout)
        return True
    except requests.ConnectionError:
        return False
    return False
    
class EPA:
    def __init__(self,dataToken="YourToken"):
        self.fail_count = 0
        self.url = "https://opendata.epa.gov.tw/webapi/api/rest/datastore/355000000I-000259/?format=json"
        # # Token to get Data # #
        self.dataToken = ""
        if dataToken != 'YourToken':
            self.dataToken = '&token=' + dataToken
    
    def fetch_data(self,timeout=5):
        url = self.url + self.dataToken
        r = requests.get(url=url, verify=False, timeout=timeout)
        jf = json.loads(r.text)
        records = jf["result"]["records"]
        site_names = []
        for i in records:
            name = i["SiteName"]
            site_names.append(name)
            try:
                jfile = {}
                for j in jf:
                    jfile[j] = jf[j]
                jfile["result"]["records"] = [i]
                with open(store_dir + '/' + name + '.json', 'w') as f:
                    json.dump(jfile,f)
            except:
                with open(store_dir + '/' + name + '.json', 'w') as f:
                    f.write('{}')
    def run(self):
    # # run API service
        while 1:
            if check_network():
                try:
                    self.fetch_data(timeout=20)
                except:
                    pass
            time.sleep(600)
    
@application.route('/getEPA/<site_name>', methods=['POST', 'GET'])
def get_EPA(site_name):
    try:
        with open(store_dir + '/' + site_name + '.json') as f: 
            epa_text = f.read()
        return epa_text
    except:
        return '{}'

@application.route('/AQI/<site_name>', methods=['POST', 'GET'])
def get_AQI(site_name):
    try:
        with open(store_dir + '/' + site_name + '.json') as f: 
            epa_json = json.load(f)
        AQI = epa_json["result"]["records"][0]["AQI"]
        return AQI
    except:
        return '-1'
        
@application.route('/', methods=['POST', 'GET'])
def index():
    return ("use /getEPA/sitename to get JSON data of site, e.g. /getEPA/復興<br>"
            "use /AQI/sitename to get AQI value, e.g. /AQI/復興")
            
if __name__ == '__main__':
    try:
        try:
            with open('EPASetting.json') as f:
                settings = json.loads(f.read())
            # # settings -> {"StoreDir": dir_path, "DataToken": your_token}
            if "StoreDir" in settings:
                store_dir = settings["StoreDir"]
            if "DataToken" in settings:
                _token = settings["DataToken"]
            else:
                _token = 'YourToken'
            epa = EPA(dataToken=_token)
        except:
            epa = EPA()
            
        # # run fetch data in thread
        _thread = threading.Thread(target=epa.run)
        _thread.start()
        
        # # initialize web service
        application.run(host='0.0.0.0',port=5000)
    except KeyboardInterrupt:
        sys.exit()