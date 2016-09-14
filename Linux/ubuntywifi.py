#!/usr/bin/env python
#coding = utf-8
#Authors : kg
import os
import sys 
import re

path = "/etc/NetworkManager/system-connections/"

''' get all wifi name and passwd'''
def getAllwifi(path):
    wifiName = []
    f_list = os.listdir(path)
    for i in f_list:
        try:
            i = os.path.dirname(path) + os.sep + i 
            if judgePath(i):
                with open(i) as f:
                    data = f.read()
                    if "psk=" in data:
                        ssid = re.search(r'id=(\w\w*)', data)
                        pwd = re.search(r'psk=([\w=]*)', data)
                        w_list = 'ssid: ' + ssid.group(1) + '   passwd: ' + pwd.group(1) + '\n'
                        wifiName.append(w_list)
            else:
                print "you don't have permission, please use sudo or su"
                sys.exit()
        except Exception, e:
            print str(e)
            pass
    return wifiName

''' judge path access'''
def judgePath(path):
    if os.access(path, os.R_OK):
        return True

''' write file '''
def writeFile(com):
    f=file("wifi.txt","a+")
    for context in com:
        f.write(context)
    f.close()


if __name__ == '__main__':
    comment = getAllwifi(path)
    writeFile(comment)
