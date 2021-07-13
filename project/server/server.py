import smtpd
import asyncore
import email
import time


class FakeLink:
    def __init__(self,signature) -> None:
        self.signature = signature

class Virus:
    def __init__(self,name,signature) -> None:
        self.name = name
        self.signature = signature
    def __str__(self) -> str:
        str = "virus name:" + self.name
        return str

class Client:
    def __init__(self,peer,emailAddress) -> None:
        self.peer = peer # identifier, The sender’s address, a tuple containing IP and incoming port
        self.emailAddress = emailAddress


class mail:
    def __init__(self, client, time) -> None:
        self.client = client    # email's sender
        self.time = time        # time of sent


### global variables ###
virusList = []
black_list = []
fake_list = []
sales_websites = []
re_size = 100                       # recent senders size of list
recent_emails = [None] * re_size 
re_index = 0                        # recent senders index in the list
spam_period = 60                    # one day = 86400 seconds
spam_count = 10                     # max number of emails in spam_period per not spam client
### ----------------- ###

# check whether or not there is a virus in msg
def is_virus(msg):
    for node in msg.walk():
        if(node.get_content_maintype() == "application"):
            file = node.get_payload(decode=True)
            for virus in virusList:
                 if virus.signature in file:
                     return True
    return False

# check whether or not this client is a spam client
def is_spam_client(peer, last_email_time):
        count = 0                               # count of client's emails in the last spam period
        i = (re_index - 1) % re_size            # to start from the last email inserted backwards
        for j in range(re_size):
            e = recent_emails[i]
            if e == None:
                break
            period = last_email_time - e.time
            if period > spam_period:            # no other emails will be in spam_period so break
                break
            # if reached here, in spam_period
            if e.client.peer[0] == peer[0]:
                count += 1
            i = (i - 1) % re_size

        if count > spam_count:
            return True
        return False

# check whether or not there is an exec file in msg
def is_exec_file(msg):
    for node in msg.walk():
        if(node.get_content_maintype() == "application"):
            file = node.get_payload(decode=True)
            file_init = file[1:4].decode("utf-8")   # bytes 1,2,3 of file
            if file_init == "ELF":
                return True          
    # if reached here, no exec file found            
    return False

# check whether or not there is a fake link in msg
def is_fake_link(msg):
    for node in msg.walk():
        if(node.get_content_maintype() == "text"):
            textMail = node.get_payload(decode=True)
            for link in fake_list:
                 if link.signature in textMail:
                     return True
    return False

# check whether or not there is a marketing content in msg
def is_sales_web(mailfrom):
    for web in sales_websites:
        if web in mailfrom:
            return True
    return False


# lists creation:

def createVirusList():
    with open("./signatures", "rb") as fd:
        lengthInBytes = fd.read(2)
        while lengthInBytes:
            length = int.from_bytes(lengthInBytes, byteorder='little') 
            name = fd.read(16).decode("utf-8")
            signature = fd.read(length)
            virusList.append(Virus(name,signature))
            lengthInBytes = fd.read(2)
        fd.close()

def createFakeList():
    with open("./fake_links.txt", "rb") as fd:
        line = fd.readline()
        while line:
            signature = line[0:len(line)-2]      # get rid of the '\n' byte at the end of each line
            fake_list.append(FakeLink(signature))
            line = fd.readline()
        fd.close()

def createWebList():
    with open("./sales_websites.txt", "r") as fd:
        line = fd.readline()
        while line:
            web = line[0:len(line)-1]      # get rid of the '\n' byte at the end of each line
            sales_websites.append(web)
            line = fd.readline()
        fd.close()



def add_to_black_list(ip, mailfrom):
    if not ip in black_list:
        black_list.append(ip)
    if not mailfrom in black_list:
        black_list.append(mailfrom)

class CustomSMTPServer(smtpd.SMTPServer):
    
    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        msg = email.message_from_string(data.decode("utf-8"))

        global re_index, recent_emails, black_list
        e = mail(Client(peer, mailfrom), time.time())
        recent_emails[re_index] = e
        re_index = (re_index + 1) % re_size

        print("----------------START OF MAIL------------------")
        
        if is_virus(msg):
            add_to_black_list(peer[0], mailfrom)
            print('\n--------NOTICE: VIRUS email was blocked!--------\n')
            print("----------------END OF MAIL------------------")
            return

        if is_spam_client(peer, e.time):
            add_to_black_list(peer[0], mailfrom)
            print('\n--------NOTICE: SPAM email was blocked!--------\n')
            print("----------------END OF MAIL------------------")
            return

        # if reached here, deliver message to target
        if is_exec_file(msg):
            print('\n--------NOTICE: EXEC file in this email, be careful--------\n')
        if is_fake_link(msg):
            print('\n--------NOTICE: FAKE LINKS in this email, be careful--------\n')
        if is_sales_web(mailfrom):
            print('\n--------NOTICE: MARKETING CONTENT in this email--------\n')

        if peer[0] in black_list or mailfrom in black_list:
            print('\n--------NOTICE: email from UNRELIABLE SENDER, may contain virus/spam--------\n')

        print ('Receiving message from:', peer)
        print ('Message addressed from:', mailfrom)
        print ('Message addressed to  :', rcpttos)
        print ('Message length        :', len(data))
        print('Message Subject:', msg['Subject'])
        for x in msg.walk():
            if x.get_content_maintype() == "text":
                print("Body of the message:", end = " ")
                print(x.get_payload())
            if(x.get_content_maintype() == "application"):
                print("The sender sent a file named:", end = " ")
                print(x.get_filename())
                
        print("----------------END OF MAIL------------------")

        return

def main():
    createVirusList()
    createFakeList()
    createWebList()
    server = CustomSMTPServer(('127.0.0.1', 1025), None)
    asyncore.loop()

if __name__ == "__main__":
    main()
