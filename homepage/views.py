from django.contrib.auth.models import User , Group
from django.shortcuts import render, redirect , get_object_or_404
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.conf import settings as globalSettings
from django.core.exceptions import ObjectDoesNotExist , SuspiciousOperation
from django.views.decorators.csrf import csrf_exempt, csrf_protect
# Related to the REST Framework
from rest_framework import viewsets , permissions , serializers
from rest_framework.exceptions import *
from url_filter.integrations.drf import DjangoFilterBackend
from .serializers import *
from API.permissions import *
from ERP.models import application, permission , module ,service
from ERP.views import getApps, getModules
from django.db.models import Q
from django.http import JsonResponse
import random, string
from django.utils import timezone
from rest_framework.views import APIView
# from POS.models import *
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
import sendgrid
import os
from ERP.models import appSettingsField
from ERP.send_email import send_email

def index(request):
    return render(request, 'index.html', {"home": True })


# def vendorreg})istration(request):
#     # 1. return the same html from both , registration as well as vendor registration
#     # 2. pass a key in the final submit for registration that its a vendor ( make that user a staff)
#     # 3. redirect it to /storesetup (only if he is staff)
#
#     return render(request,"vendorregistration.html" , {"home" : False , "brandLogo" : globalSettings.BRAND_LOGO , "brandLogoInverted": globalSettings.BRAND_LOGO_INVERT , 'brandName' : globalSettings.BRAND_NAME})



def setupstore(request):
    try:
        if request.path_info.split('setupStore/')[1] == 'register':
            if request.user.pk:
                u = request.user
                u.is_staff= True
                u.save()
                if Store.objects.filter(owner = request.user).count() == 0:
                    storeData = Store.objects.create(owner = u,creator=u)
                    # storeData.creator = request.user
                    # storeData.save()
                else:

                    storeData = Store.objects.get(owner = u)

    except :
        pass
    if request.user.is_staff == True:
        if Store.objects.filter(owner = request.user).count() == 0 :
            storeData = Store.objects.create(owner = request.user)
            storeData.creator = request.user
            storeData.save()
        else:
            storeData = Store.objects.get(owner = request.user)


    if storeData.submitted:
        print "Redirecting since the store details is already setup"
        return redirect('/admin/')
    if request.method =="POST" :
        storeData.name = request.POST['storename']
        storeData.vendor_typ = request.POST['vendorType']
        storeData.mobile = request.POST['mobile']
        storeData.email = request.POST['email']
        storeData.pincode = request.POST['pincode']
        storeData.gstin = request.POST['gstin']
        storeData.cin = request.POST['CIN']
        storeData.address = request.POST['Address']
        storeData.gstincert = request.POST['gstincer']
        storeData.personelid = request.POST['personnelcer']
        storeData.creator = request.user
        storeData.submitted = True
        storeData.save()
        return redirect('/admin/')

    return render(request,"app.homepage.partnerlogin.html" , {"home" : False , "brandLogo" : globalSettings.BRAND_LOGO , "brandLogoInverted": globalSettings.BRAND_LOGO_INVERT , 'brandName' : globalSettings.BRAND_NAME,'data':storeData})


def registration(request):
    print 'herrrrrrrrrrr'
    # if not globalSettings.LITE_REGISTRATION:
    #     data = {"home" : False ,"brand_title":globalSettings.SEO_TITLE,"autoActiveReg":globalSettings.AUTO_ACTIVE_ON_REGISTER ,"font":globalSettings.ECOMMERCE_FONT, "brandLogo" : globalSettings.BRAND_LOGO ,'icon_logo':globalSettings.ICON_LOGO, "brandLogoInverted": globalSettings.BRAND_LOGO_INVERT , 'brandName' : globalSettings.BRAND_NAME,'regextra':globalSettings.REGISTRATION_EXTRA_FIELD,'verifyMobile':globalSettings.VERIFY_MOBILE,'seoDetails':{'title':globalSettings.SEO_TITLE,'description':globalSettings.SEO_DESCRIPTION,'image':globalSettings.SEO_IMG,'width':globalSettings.SEO_IMG_WIDTH,'height':globalSettings.SEO_IMG_HEIGHT,'author':globalSettings.SEO_AUTHOR,'twitter_creator':globalSettings.SEO_TWITTER_CREATOR,'twitter_site':globalSettings.SEO_TWITTER_SITE,'site_name':globalSettings.SEO_SITE_NAME,'url':globalSettings.SEO_URL,'publisher':globalSettings.SEO_PUBLISHER}}
    #     objIsGlobal = appSettingsField.objects.filter(name='isStoreGlobal')
    #
    #     isStoreGlobal = False
    #     if len(objIsGlobal)>0:
    #         if objIsGlobal[0].flag:
    #             isStoreGlobal = True
    #     data['isStoreGlobal'] = isStoreGlobal
    #     return render(request,"registration.html" , data)
    # else:
    print "Lite registration page"
    mobile = ''

    if 'mobile' in request.POST:
        mobile = request.POST['mobile']

    return render(request,"registration.lite.html" , {'mobile':mobile,"home" : False ,"autoActiveReg":globalSettings.AUTO_ACTIVE_ON_REGISTER,"font":globalSettings.ECOMMERCE_FONT, "brand_title":globalSettings.SEO_TITLE,"brandLogo" : globalSettings.BRAND_LOGO , 'icon_logo':globalSettings.ICON_LOGO, "brandLogoInverted": globalSettings.BRAND_LOGO_INVERT , 'brandName' : globalSettings.BRAND_NAME,'regextra':globalSettings.REGISTRATION_EXTRA_FIELD,'verifyMobile':globalSettings.VERIFY_MOBILE,'seoDetails':{'title':globalSettings.SEO_TITLE,'description':globalSettings.SEO_DESCRIPTION,'image':globalSettings.SEO_IMG,'width':globalSettings.SEO_IMG_WIDTH,'height':globalSettings.SEO_IMG_HEIGHT,'author':globalSettings.SEO_AUTHOR,'twitter_creator':globalSettings.SEO_TWITTER_CREATOR,'twitter_site':globalSettings.SEO_TWITTER_SITE,'site_name':globalSettings.SEO_SITE_NAME,'url':globalSettings.SEO_URL,'publisher':globalSettings.SEO_PUBLISHER}})


class RegistrationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationSerializer
    queryset = Registration.objects.all()

class EnquiryAndContactsViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = EnquiryAndContactsSerializer
    queryset = EnquiryAndContacts.objects.all()
from django.contrib.auth import authenticate , login
class UpdateInfoAPI(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.AllowAny ,)
    def post(self , request , format = None):
        print request.data,'%%%%%%%%%%%%%%%%'
        d = request.data
        u = request.user
        print u,'@@@@222'
        u.first_name = d['firstName']
        u.email = d['email']
        u.set_password(d['password'])
        u.backend = 'django.contrib.auth.backends.ModelBackend'
        u.save()

        try:
            pobj = profile.objects.get(pk=u.profile.pk)
            z  = merge_two_dicts(pObj.details, d)
            pObj.details = z
            print z,'***************************************************'
            pObj.save()
        except :
            pass

        login(request , u)
        return Response( status = status.HTTP_200_OK)


class ReSendOtpAPI(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.AllowAny ,)
    def post(self , request , format = None):
        print "herererere", request.data
        reg = Registration.objects.get(pk=request.data['id'])
        username = reg.email.split('@')[0]
        if request.data['otpType'] == 'emailOtp':
            reg.emailOTP = generateOTPCode()
            print reg.emailOTP,'email'
            msgBody = ['Your OTP to verify your email ID is <strong>%s</strong>.' %(reg.emailOTP)]
            try:
                fbUrl = appSettingsField.objects.filter(name='facebookLink')[0].value
            except:
                fbUrl = 'https://www.facebook.com/'

            try:
                twitterUrl = appSettingsField.objects.filter(name='twitterLink')[0].value
            except:
                twitterUrl = 'twitter.com'

            try:
                linkedinUrl = appSettingsField.objects.filter(name='linkedInLink')[0].value
            except:
                linkedinUrl = 'https://www.linkedin.com/'

            try:
                sendersAddress = appSettingsField.objects.filter(name='companyAddress')[0].value
            except:
                sendersAddress = ''

            try:
                sendersPhone =  appSettingsField.objects.filter(name='phone')[0].value
            except:
                sendersPhone = ''

            ctx = {
                'heading' : 'Welcome to Ecommerce',
                'recieverName' : 'Customer',
                'message': msgBody,
                # 'linkUrl': 'sterlingselect.com',
                # 'linkText' : 'View Online',
                'sendersAddress' : sendersAddress,
                'sendersPhone' : sendersPhone,
                'linkedinUrl' : linkedinUrl,
                'fbUrl' : fbUrl,
                'twitterUrl' : twitterUrl,
                'brandName' : globalSettings.BRAND_NAME,
                'username':username
            }

            email_body = get_template('app.homepage.emailOTP.html').render(ctx)
            email_subject = 'Regisration OTP'
            if globalSettings.EMAIL_API:
                sg = sendgrid.SendGridAPIClient(apikey= globalSettings.G_KEY)
                # sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
                data = {
                  "personalizations": [
                    {
                      "to": [
                        {
                          # "email": 'bhanubalram5@gmail.com'
                          "email": str(reg.email)
                          # str(orderObj.user.email)
                        }
                      ],
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
                response = sg.client.mail.send.post(request_body=data)
                print(response.body,"bodyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
            else:
                sentEmail=[]
                sentEmail.append(str(reg.email))
                # msg = EmailMessage(email_subject, email_body, to= sentEmail , from_email= 'do_not_reply@cioc.co.in' )
                msg = EmailMessage(email_subject, email_body, to= sentEmail)
                msg.content_subtype = 'html'
                msg.send()
        elif request.data['otpType'] == 'mobileOtp':
            reg.mobileOTP = generateOTPCode()
            print reg.mobileOTP,'mobile'
            mobile = reg.mobile
            if 'phoneCode' in request.data:
                phoneCode = request.data['phoneCode']
                mobile = phoneCode +''+ reg.mobile
            try:
                url = globalSettings.SMS_API_PREFIX.format(reg.mobile , 'Dear Customer,\nPlease use OTP : %s to verify your mobile number' %(reg.mobileOTP))
            except:
                url = globalSettings.SMS_API_PREFIX.format(reg.mobile , 'Dear Customer,\nPlease use OTP : %s to verify your mobile number' %(reg.mobileOTP))
            requests.get(url)
        reg.save()

        return Response( status = status.HTTP_200_OK)
