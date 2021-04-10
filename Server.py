import smtpd
import asyncore

class CustomSMTPServer(smtpd.SMTPServer):
    
    def process_message(self, peer, mailfrom, rcpttos, data):
        # print message details
        print ('Receiving message from:', peer)
        print ('Message addressed from:', mailfrom)
        print ('Message addressed to  :', rcpttos)
        print ('Message length        :', data)

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
        #       Client:
        #       viruses array, black_list array
        #      




        return

server = CustomSMTPServer(('127.0.0.1', 1025), None)

asyncore.loop()


# import smtpd
# import asyncore

# server = smtpd.DebuggingServer(('127.0.0.1', 1025), None)

# asyncore.loop()
