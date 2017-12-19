import subprocess
import os
import uuid


def main():
    
    locate = os.path.expanduser("~/Library/Application Support/McNeel/Rhinoceros/MacPlugIns/")

    try:
        tmp = subprocess.check_output(['ls', locate])
    except:
        print "error"

    tmp = tmp.decode('utf-8')
    tmp = tmp.split('\n')
    
    if not 'PythonPlugins' in tmp:
        #create pythonPlugins directory
        subprocess.call(['mkdir', locate + 'PythonPlugins'])


    try:
        tmp = subprocess.check_output(['ls', locate + 'PythonPlugins/'])
    except:
        print "error"


    tmp = tmp.decode('utf-8')
    tmp = tmp.split('\n')

    pluginFolderName = ''
    
    humpty = False
    for i in tmp:
        if 'AAMPlugins' in i:
            humpty = True
            pluginFolderName = i

            break

    if not humpty:

        print "AAMPlugins folder isn't found\nSo I create AAMPlugins folder\n"
            
        #create plugins folder
        u1 = str(uuid.uuid1())
        pluginFolderName = 'AAMPlugins{' + u1 + '}'

        subprocess.call(['mkdir', locate + 'PythonPlugins/' + pluginFolderName])
        subprocess.call(['mkdir', locate + 'PythonPlugins/' + pluginFolderName + '/dev'])


    subprocess.call(['cp', "../src/AAM_Planar_cmd.py", locate + 'PythonPlugins/' + pluginFolderName + '/dev/'])
    subprocess.call(['cp', "../src/AAM_CurvedSurface_cmd.py", locate + 'PythonPlugins/' + pluginFolderName + '/dev/'])



    print "successfuly AAM Plugins is installed"
    print "Please Restart Rhinoceros"





if __name__ == "__main__":
    main()
