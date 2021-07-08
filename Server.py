import smtpd
import asyncore
import email
import time
import os
import random
import string



class client:   # (sender)
    def __init__(self, peer, emailAddress):
        self.peer = peer # identifier, The sender’s address, a tuple containing IP and incoming port
        self.emailAddress = emailAddress

class email:
    def __init__(self, client, time):
        self.client = client    # email's sender
        self.time = time        # time of sent
        
### global variables ###
black_list = [client]
re_size = int(100)                   # recent senders size of list
recent_emails = [email] * re_size 
re_index = int(0)                   # recent senders index in the list
spam_period = int(86400)            # one day = 86400 seconds
spam_count = int(5)                 # max number of emails in spam_period per not spam client
### ----------------- ###

class CustomSMTPServer(smtpd.SMTPServer):
    

    # looking for a virus in data
    # signature and data should be sequences of bytes
    def is_virus(data):
        vir_file = open("viruses", "r")
        sizeInBytes = vir_file.read(2)
        while sizeInBytes:
            size = int.from_bytes(sizeInBytes, "little")      # maybe "big" 
            name = vir_file.read(16)                          # name size in bytes
            signature = vir_file.read(size)
            if signature in data:
                vir_file.close()
                return True
            sizeInBytes = vir_file.read(2)
        # if reached here, no virus found
        vir_file.close()
        return False

    def is_spam_client(peer, last_email_time):
        count = 0                               # count of client's emails in the last spam period
        i = re_index - 1                        # to start from the last email inserted backwards
        for i in range(re_size):
            e = recent_emails[i]
            period = last_email_time - e.time
            if period > spam_period:            # no other emails will be in spam_period so break
                break
            # if reached here, in spam_period
            if e.client.peer == peer:
                count += 1
            if i == 0:
                i = re_size - 1
            else:
                i -= 1
        if count > spam_count:
            return True
        return False

    # looking for a fake link in data
    # line and data should be sequences of bytes
    def is_fake_link(data):
        fl_file = open("fake_links.txt", "r")
        line = fl_file.readline()
        while line:
            if line[0:len(line)-1] in data:     # get rid of the '\n' byte at the end of each line
                fl_file.close()
                return True
            line = fl_file.readline()
        # if reached here, no fake link found
        fl_file.close()
        return False

    # check weather or not data is an exec file
    # data should be bytes
    # TODO: check if writting data to new_file is the same as downloading it (keep its file type)
    def is_exec_file(data):
        while True:
            # generating a random string of letters
            letters = string.ascii_lowercase
            filename = ''.join(random.choice(letters) for i in range(10))
            try:
                new_file = open(filename, 'x')  # 'x' throws exception in case this filename already exists
                break
            except:
                print(filename + 'already exists, try another name')
        new_file.write(data)
        os.chmod(filename, 0o777)
        executable = os.access(filename, os.X_OK)
        if executable:
            os.remove(filename)
            return True
        os.remove(filename)
        return False

    def process_message(self, peer, mailfrom, rcpttos, data):
        global re_index, recent_emails, black_list
        c = client(peer, mailfrom)
        e = email(c, time.time())
        recent_emails[re_index] = e
        if re_index == re_size - 1:
            re_index = 0
        else:
            re_index += 1

        message = email.message_from_string(data.decode('utf-8')) # maybe 'us-ascii'
        for part in message.walk():
            message_body = part.get_payload()


        if self.is_virus(data):
            if not c in black_list:
                black_list.append(c)
            print('VIRUS FOUND')
            return
        if self.is_spam_client(peer, e.time):
            if not c in black_list:
                black_list.append(c)
            print('SPAM CLIENT')
            return
        # if reached here, deliver message to target
        if self.is_exec_file(data):
            print('NOTICE: this mail contains EXEC file , could be a virus')
        if self.is_fake_link(data):
            print('NOTICE: this mail contains FAKE LINKS, be careful')
        if c in black_list:
            print('NOTICE: this mail may contain virus/spam')
        print ('Receiving message from:', peer)
        print ('Message addressed from:', mailfrom)
        print ('Message addressed to  :', rcpttos)
        print ('Message length        :', len(data))
        print ('Message data          :', message_body)
        return 


        # TODO: 
        # 1. SEQUENCE DESCRIPTION:
        # check for virus patterns/exec file in message 
        #   - if so -> add client to black list (which contains both 'virus' clients and 'spam' clients)
        #              and don't deliver to target.
        #   - if not -> check if this client sent more messages than allowed in the last period.
        #             - if so -> add it to black list and don't deliver to target.
        #             - if not -> check if this client is in black list.
        #                        - if so ->  deliver message to target with a virus/spam warning. 
        #                        - if not -> deliver message to target.
        # 2. OBJECTS: 
        #       Virus: name, signature, size(?)
        #       Client(sender): peer (identifier, The sender’s address, a tuple containing IP and incoming port), 
        #                       email address(can be changed by the sender)
        #       viruses array, black_list array
        # 3. get a virus file and understand its order
        #      

        
server = CustomSMTPServer(('127.0.0.1', 1025), None)

asyncore.loop()



