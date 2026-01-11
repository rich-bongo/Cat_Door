import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import logging

class SendEmail:
     """
     Implementation of class to send email with attached photos 
     and then clean photo directory
     """
     def __init__(self, cnfg):
          self.smtp_server = cnfg.get_config("SMTP_SERVER")
          self.smtp_port = cnfg.get_config("SMTP_PORT")
          self.from_email = cnfg.get_config("FROM_EMAIL")
          self.to_email = cnfg.get_config("TO_EMAIL") 
          self.logger = logging.getLogger('logger_util.email')
          self.logger.info('creating an instance of logger for email')
          self.from_app_pw = os.getenv("GMAIL_APP_PW")
          self.logger.info(f"email configuration: server: {self.smtp_server} port: {self.smtp_port} To: {self.to_email} From: {self.from_email}")

     """
        A class method designed to take email status to user along with directory contents
        body - email body.
        subject - email subject
        dir - directory contents to be attached to email
        returns: NA
      """

     def email_photos(self,body,subject,dir):
         msg = MIMEMultipart()
         msg['From']= self.from_email
         msg['To'] =  self.to_email      
         msg['Subject']= subject
         body_part = MIMEText(body)
         msg.attach(body_part)
         success = True
         try:
              for item in os.listdir(dir):
                    path_to_file = os.path.join(dir,item)
                    with open(path_to_file,'rb') as file:
                         msg.attach(MIMEApplication(file.read(), Name=path_to_file))
         except FileNotFoundError:
              self.logger.error(f"Error: The directory '{dir}' was not found.") 
              success = False

         with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
          try:
               server.login(self.from_email, self.from_app_pw)
               try:
                    server.sendmail(self.from_email, self.to_email, msg.as_string())
               except smtplib.SMTPConnectError as e:
                    self.logger.error(f"Connection failed: {e}")
                    success = False
               except smtplib.SMTPException as e:
                    self.logger.error(f"error sending email from: {self.from_email} to:{self.to_email} subject: {self.subject}")
                    self.logger.error(f"Exception Reason: {e}")
                    success = False
               except Exception as e:
                    self.logger.error(f"Error sending email from: {self.from_email} to:{self.to_email} subject: {self.subject}")
                    self.logger.error(f"Exception Reason: {e}")
                    success = False
                        
          except smtplib.SMTPAuthenticationError as e:
                  self.logger.error(f" Auth Error logging in {self.from_email}")
                  self.logger.error(f"Exception Reason: {e}")
                  success = False
 
         server.quit

    # delete photos only if email was successful
         if success:
              for item in os.listdir(dir):
               path_to_file = os.path.join(dir,item)    
               try:
                    if os.path.isfile(path_to_file) or os.path.islink(path_to_file):
                         os.remove(path_to_file)
               except Exception as e:
                    self.logger.error(f"Failed to delete {path_to_file}. Reason: {e}") 
    