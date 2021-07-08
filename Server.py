import smtpd
import asyncore
import email


class virus:
    def __init__(self, size, name, signature):
        self.size = size # of signature alone
        self.name = name
        self.signature = signature

class client:   # (sender)
    def __init__(self, peer, emailAddress):
        self.peer = peer # identifier, The sender’s address, a tuple containing IP and incoming port
        self.emailAddress = emailAddress
        
### local variables ###  how to change them inside class CustomSMTPServer?
black_list = [client]
rs_size = int(10)                   # recent senders size of list
recent_senders = [client] * rs_size 
rs_index = int(0)                   # recent senders index in the list
spam_count = int(5)
### --------------- ###

class CustomSMTPServer(smtpd.SMTPServer):
    

    # looking for a virus in data
    # TODO: figure out which fields in each virus and change size accordingly 
    def is_virus(data):
        vir_file = open("viruses", "r")
        sizeInBytes = vir_file.read(2)
        while sizeInBytes:
            size = int.from_bytes(sizeInBytes, "little") - 2 # maybe "big", minus the size and name bytes 
            name = vir_file.read(2) # name size in bytes
            signature = vir_file.read(size)
            if signature in data:
                vir_file.close()
                return True
            sizeInBytes = vir_file.read(2)
        # if reached here, no virus found
        vir_file.close()
        return False

    def is_spam_client(peer):
        count = 0
        for i in range(rs_size):
            c = recent_senders[i]
            if c.peer == peer:
                count += 1
        if count >= spam_count:
            return True
        return False
            
    def process_message(self, peer, mailfrom, rcpttos, data):
        c = client(peer, mailfrom)
        recent_senders[rs_index] = c
        # if rs_index == rs_size - 1:
        #     rs_index = 0
        # rs_index += 1

        message = email.message_from_string(data.decode('utf-8')) # maybe 'us-ascii'
        for part in message.walk():
            message_body = part.get_payload()


        if self.is_virus(data):
            black_list.append(c)
            print('VIRUS FOUND')
            return
        if self.is_spam_client(peer):
            black_list.append(c)
            print('SPAM CLIENT')
            return
        # if reached here, deliver message to target
        if self.is_exec_file(data):
            print('NOTICE: this mail contain EXEC file , could be a virus')
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



