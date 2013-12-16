from win32com.shell import shell, shellcon
import os, sys
from xml.dom import minidom
import win32crypt
import ctypes
import subprocess


outFile_path = os.path.join(os.path.dirname(sys.executable),
                            'WIFIpass.txt') 
if os.path.exists(outFile_path):
    os.remove(outFile_path)


if len(sys.argv) == 1:
    ret = subprocess.call(
        os.path.dirname(sys.executable) + '\\' + 'PsExec.exe /accepteula /i /s "' + sys.executable + '" -getpass' )
    if ret == 0:
        ctypes.windll.user32.MessageBoxW(0, u'WIFI passwords saved to\n' + outFile_path, u'Success', 64)
    else:
        ctypes.windll.user32.MessageBoxW(0, u'You must run this app as administrator!', u'Require privileges', 16)
        sys.exit(-1)
    sys.exit(0)


# Get $ProgramData path
folder = shell.SHGetFolderPath(0, shellcon.CSIDL_COMMON_APPDATA, None, 0)
if_folder = os.path.join(folder, 'Microsoft\Wlansvc\Profiles\Interfaces')    # Interfaces folder
if not os.path.exists(if_folder):
    ctypes.windll.user32.MessageBoxW(0, u'Fail to locate Interfaces folder!', u'Error', 16)    # MB_ICONERROR = 0x00000010L
    sys.exit(-1)

for root, dirs, files in os.walk(if_folder):
    if len(files) > 0:
        for file in files:
            if file.endswith('.xml'):
                xml_file = os.path.join(root, file)
                xml_doc = minidom.parse(xml_file)
                ssid = xml_doc.getElementsByTagName('SSID')[0].getElementsByTagName('name')[0].childNodes[0].data
                key = xml_doc.getElementsByTagName('keyMaterial')[0].childNodes[0].data
                binout = []
                for i in range(len(key)):
                    if i % 2 == 0:
                        binout.append(chr(int(key[i:i+2],16)))
                pwdHash=''.join(binout)
                try:
                    ret =  win32crypt.CryptUnprotectData(pwdHash, None, None, None, 0)
                except:
                    ctypes.windll.user32.MessageBoxW(0, u'You must run this app as administrator!', u'Require privileges', 16)
                    sys.exit(-1)
                with open(outFile_path, 'a+') as outFile:
                    outFile.write('SSID: {0:<20} Password: {1} \n\n'.format(ssid, ret[1]))