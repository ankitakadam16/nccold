import os
from os import path
from django.conf import settings as globalSettings
from django.core.mail import send_mail , EmailMessage
import sendgrid


def send_email(email_body, email_to, email_subject,email_cc,email_bcc, email_type):
    # email_to, email_cc and email_bcc should be a list
    # if isinstance(email_to, list):
    #     print 'list'
    # else:
    #     print 'not list'
    print 'in send email',email_to
    # print email_body
    print email_subject,'email_subject'
    print email_type , 'email_type'

    if globalSettings.EMAIL_API:
        sg = sendgrid.SendGridAPIClient(api_key= globalSettings.G_KEY)
        print globalSettings.G_KEY,'globalSettings.G_KEY'
        emailIDsList = []
        emailIDsListObj = []
        bccIds = []
        ccIds = []
        # for i in email_to:
        #     emailIDsList.append(str(i))
        # for i in globalSettings.G_ADMIN:
        #     emailIDsList.append(str(i))
        email_to = list(set(email_to))
        for i in email_to:
            emailIDsListObj.append({"email":i})
        data = {
          "personalizations": [
            {
              "to": emailIDsListObj,
              "subject": email_subject
            }
          ],
          "from": {
            "email": globalSettings.G_FROM,
            "name":globalSettings.SEO_TITLE
          },
          "content": [
            {
              "type": "text/html",
              "value": email_body
            }
          ]
        }

        # print data
        print 'beforeeeee'
        response = sg.client.mail.send.post(request_body=data)
        print response
    else:
        for i in globalSettings.G_ADMIN:
            email_to.append(i)
        msg = EmailMessage(email_subject , email_body, to= email_to )
        if email_type=='html':
            msg.content_subtype = 'html'
        msg.cc = email_cc
        msg.bcc = email_bcc
        msg.send()
    return {'EmailSent':True}

if __name__ == '__main__':
    res = send_email('Hello Hi' , ['pradeep@cioc.in'] , 'This is just subject' ,' ', '','html')
