#-*- coding: utf-8 -*-
import pdslib
import time

def request():
    l = ('GET', "https://pull-flv-f1.douyincdn.com/media/stream-693964764056388274_ld.flv?keeptime=00093a80&major_anchor_level=common&t_id=037-202506280004155A2B0DB278174549251C-y0utcX&unique_id=stream-693964764056388274_690_flv_ld&wsSecret=288b8ddd5c9f89f99a95abd072144e59&wsTime=685ec100", ["a:b"], "")
    pdslib.httpsetconfig(True, "http://192.168.0.3:8189")
    httplist = []
    for i in range(5):
        httplist.append(l)
    pids = pdslib.createHttpSync(httplist)
    for i in range(111):
        ss = pdslib.getHstatus(pids)
        if ss != None:
            status, code = ss
            if code == 0:
                print(status.__len__())
                for mm in status:
                    print(mm)
                break
            else:
                print(status)
        time.sleep(0.5)
    pdslib.closeHs(pids)

def uuuuuuuu():
    l = ('POST',
         "https://upload.pypi.org/legacy/",
         ["C:\\Users\\tian\\Desktop\\Pytest\\5.tar.gz","content","application/octet-stream"],
         ["Authorization:Basic X190b2tlbl9fOnB5cGldB",
          "Host:upload.pypi.org"],
         ["protocol_version:1","blake2_256_digest:11",
          "summary:ObjectToString","version:0.0.5","metadata_version:2.1","author:2","name:456","pyversion:source","filetype:sdist"])

    httplist = []
    for i in range(1):
        httplist.append(l)
    pids = pdslib.createHttpuSync(httplist)
    for i in range(11100):
        ss = pdslib.getHstatus(pids)
        if ss != None:
            status, code = ss
            if code == 0:
                print(status.__len__())
                for mm in status:
                    print(mm)
                break
            else:
                print(status)
        time.sleep(0.5)
    pdslib.closeHs(pids)

if __name__ ==  '__main__':
    print(pdslib.register(""))  get the  veirycode
    #print(pdslib.register("300bf8f6f91a83b3731c99203acdbe492821347967e86b1f571be06f64ed97c002084b362bea25670577a88a72711f376c137bd0e914a77d1a6a4eab2f6196b0"))
    request()