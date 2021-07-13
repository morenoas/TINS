import smtplib
import email.utils
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Create the message
msg = MIMEMultipart()
msg['To'] = email.utils.formataddr(('Recipient', 'recipient@example.com'))
msg['From'] = email.utils.formataddr(('Author', 'author@example.com'))
msg['Subject'] = 'Simple test message'
body = "Hello"
msg.attach(MIMEText(body, 'plain'))

server = smtplib.SMTP('127.0.0.1', 1025)
server.set_debuglevel(True) # show communication with the server

try:
    for i in range (11):
        server.sendmail('author@example.com', ['recipient@example.com'], msg.as_string())
finally:
    server.quit()