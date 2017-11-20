import subproces
import uuid


def main():
    
    locate = "~/Library/Application\ Support/McNeel/Rhinoceros/MacPlugins/"

    try:
        tmp = subprocess.check_output(['ls', locate])
    except:
        print("error")

    tmp = tmp.decode('utf-8')
    tmp = tmp.split('\n')
    

    
    if not 'PythonPlugins' in tmp:
        #create pythonPlugins directory
        subprocess.call(['mkdir', locate + 'PythonPlugins'])

    try:
        tmp = subprocess.check_output(['ls', locate + 'PythonPlugins/'])
    except:
        print('error')


    tmp = tmp.decode('utf-8')
    tmp = tmp.split('\n')

    humpty = False
    for i in tmp:
        if 'AAMPlugins' in i:
            humpty = True
            break

    if humpty:
        subprocess.call(['cp', "./AAM_Rhino.py"])

    else:
        print("AAMPlugins folder isn't found\nSo I create AAMPlugins folder\n")
            
        #create plugins folder
        u1 = str(uuid.uuid1())
        subprocess.call(['mkdir', locate + 'AAMPlugins{' + u1 + '}'])
        subprocess.call(['cp',"./AAM_Rhino.py"])


    print("successfuly AAM Plugins is installed")
    print("Please Restart Rhinoceros")





if __name__ == "__main__":
    main()
