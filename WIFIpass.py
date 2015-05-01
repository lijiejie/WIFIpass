'''
    Decrypt all saved WIFI passwords on Windows
    By Lijiejie ( my[at]lijiejie.com )  2015-5-1
'''

from win32com.shell import shell, shellcon
import os, sys
from xml.dom import minidom
import win32crypt
import ctypes
import subprocess


if os.path.basename(sys.executable) == 'python.exe':
    exe_file = 'python %s ' % __file__
    cur_dir = os.path.dirname(__file__)
    outfile_path = os.path.join(cur_dir, 'WIFI_pass.txt')
else:
    exe_file = sys.executable
    cur_dir = os.path.dirname(sys.executable)
    outfile_path = os.path.join(os.path.dirname(sys.executable), 'WIFI_pass.txt')

if os.path.exists(outfile_path):
    os.remove(outfile_path)

if len(sys.argv) == 1:
    ret = subprocess.call('%s /accepteula /i /s %s -getpass' % (os.path.join(cur_dir,'PsExec.exe'), exe_file) )
    if ret != 0:
        ctypes.windll.user32.MessageBoxW(0, u'Must run as administrator!', u'Require privileges', 16)
        sys.exit(1)
    sys.exit(0)

# Get $ProgramData path
folder = shell.SHGetFolderPath(0, shellcon.CSIDL_COMMON_APPDATA, None, 0)
interface_folder = os.path.join(folder, 'Microsoft\Wlansvc\Profiles\Interfaces')    # Interfaces folder

if not os.path.exists(interface_folder):
    ctypes.windll.user32.MessageBoxW(0, u'Fail to locate $Interfaces folder!', u'Error', 16)    # MB_ICONERROR = 0x00000010L
    sys.exit(-1)

for root, dirs, files in os.walk(interface_folder):
    for file in files:
        if file.endswith('.xml'):
            try:
                xml_file = os.path.join(root, file)
                xml_doc = minidom.parse(xml_file)
                ssid = xml_doc.getElementsByTagName('SSID')[0].getElementsByTagName('name')[0].childNodes[0].data
                if not xml_doc.getElementsByTagName('keyMaterial'):
                    continue
                key = xml_doc.getElementsByTagName('keyMaterial')[0].childNodes[0].data
                binout = []
                for i in range(len(key)):
                    if i % 2 == 0:
                        binout.append(chr(int(key[i:i+2],16)))
                pwdHash = ''.join(binout)
                try:
                    ret =  win32crypt.CryptUnprotectData(pwdHash, None, None, None, 0)
                except:
                    ctypes.windll.user32.MessageBoxW(0,u'Must run as administrator!', u'Require privileges', 16)
                    sys.exit(-1)
                with open(outfile_path, 'a+') as outFile:
                    outFile.write('SSID: {0:<20} Password: {1} \n\n'.format(ssid, ret[1]))
            except:
                pass

ctypes.windll.user32.MessageBoxW(0,
    u'All WIFI passwords have been saved to\n\n%s' % os.path.abspath(outfile_path),
    u'Success', 64)