################################################################################
##
##  Make sure your LD_LIBRARY_PATH and PYTHONPATH point to a directory
##  that has libJaguarClient.so  and jaguarpy.so
##
################################################################################

import jaguarpy, os, json

class JaguarSocketClient():
    def __init__(self):
        self.jag = jaguarpy.Jaguar()

    def connect(self, apikey=None, host="127.0.0.1", port=8888, db=None):
        self.host = host
        self.port = port
        self.apikey = apikey

        if apikey is None:
            self.apikey = self.getApikey()

        if db is None:
            self.db = "vdb"
        else:
            self.db = db

        return self.jag.connect( self.host, self.port, self.apikey, self.db )


    def __getattr__(self, name):
        if hasattr(self.jag, name) and callable(getattr(self.jag, name)):
            return getattr(self.jag, name)
        else:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{attr}'")


    def disconnect(self):
        self.jag.close()

    def getApikey(self):
        try:
            hm = os.getenv("HOME")
            fpath = hm + "/.jagrc"
            f = open(fpath, 'r')
            key = f.read()
            key = key.strip()
            f.close()
            return key
        except Exception as e:
            return ''

    def jsonData(self ):
        try:
            js = self.jag.json()
            data = json.loads(js)
            return data['data']
        except Exception as e:
            return ''

    def getData(self, j):
        try:
            data = json.loads(j)
            return data['data']
        except Exception as e:
            return ''


if __name__ == "__main__":
    sockcli = JaguarSocketClient()
    apikey = sockcli.getApikey()
    sockcli.connect(apikey, "127.0.0.1", 8888, "vdb" )

    sockcli.query("help")
    sockcli.fetch()
    jd = sockcli.jsonData()
    print(jd)

    js = sockcli.json()
    jd = sockcli.getData( js )
    print(jd)

    sockcli.disconnect()
    
