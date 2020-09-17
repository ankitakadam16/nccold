from django.contrib.auth.models import User , Group
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.conf import settings as globalSettings
# Related to the REST Framework
from rest_framework import viewsets , permissions , serializers
from rest_framework.exceptions import *
from url_filter.integrations.drf import DjangoFilterBackend
from .serializers import *
from API.permissions import *
from django.db.models import Q
from allauth.account.adapter import DefaultAccountAdapter
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
import requests
import libreERP.Checksum as Checksum
from django.views.decorators.csrf import csrf_exempt
import urllib
import hashlib
import sendgrid
import os
import random,string
from django.db.models import Sum
from reportlab import *
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm, inch
from reportlab.lib import colors , utils
from reportlab.platypus import Paragraph, Table, TableStyle, Image, Frame, Spacer, PageBreak, BaseDocTemplate, PageTemplate, SimpleDocTemplate, Flowable
from PIL import Image
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet, TA_CENTER
from reportlab.graphics import barcode , renderPDF
from reportlab.graphics.shapes import *
from reportlab.graphics.barcode.qr import QrCodeWidget
# from POS.models import Order
from num2words import num2words

def randompassword():
    length =20
    chars = string.ascii_letters + string.digits +'!@$%^&*()'
    rnd = random.SystemRandom()
    return ''.join(random.choice(chars) for x in range(length))


def makeOnlinePayment(request):
    print request.GET,'asfasdfjpsuriwquerioqweuriowuei'
    if globalSettings.PAYMENT_MODE == 'EBS':
        return redirect("/api/ERP/ebsPayment/?orderid=" + request.GET['orderid'])
    elif globalSettings.PAYMENT_MODE == 'paypal':
        return redirect("/paypalPaymentInitiate/?orderid=" + request.GET['orderid'])
    elif globalSettings.PAYMENT_MODE == 'PAYU':
        return redirect("/payuPaymentInitiate/?orderid=" + request.GET['orderid'])
    elif globalSettings.PAYMENT_MODE == 'instamojo':
        return redirect("/instamojoPaymentInitiate/?orderid=" + request.GET['orderid'])


def instamojoPaymentInitiate(request):
    orderid = request.GET['orderid']
    orderObj = Order.objects.get(pk = orderid)
    headers = { "X-Api-Key": globalSettings.INSTAMOJO_API_KEY, "X-Auth-Token": globalSettings.INSTAMOJO_AUTH_TOKEN}

    payload = {
      'purpose': orderObj.store.name + " products",
      'amount': str(orderObj.totalAmount),
      'buyer_name': orderObj.orderBy.first_name,
      'email': orderObj.orderBy.email,
      'phone':  orderObj.mobileNo,
      'redirect_url': globalSettings.SITE_ADDRESS +'/instamojoPaymentResponse/',
      'send_email': 'True',
      'send_sms': 'True',
      'webhook': globalSettings.SITE_ADDRESS +'/instamojoPaymentWebhook/',
      'allow_repeated_payments': 'False',
    }
    response = requests.post( globalSettings.INSTAMOJO_URL + "/api/1.1/payment-requests/", data=payload, headers=headers)
    print response.text
    res = response.json()
    orderObj.paymentTrackingID = res['payment_request']['id']
    orderObj.save()
    return redirect(res['payment_request']['longurl'])




from django.http import HttpResponse
import requests
# from ecommerce.models import Order
class MakeEBSPayment(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.IsAuthenticated ,)
    def get(self , request , format = None):
        MERCHANT_KEY = globalSettings.PAYTM_MERCHANT_KEY
        # order = Order.objects.get(pk = request.GET['orderid'])
        # data_dict = {
        #             'channel':'0',
        #             'account_id':'19591',
        #             'reference_no': request.GET['orderid'],
        #             'amount': order.totalAmount,
        #             'mode': globalSettings.EBS_PAYMENT_MODE,
        #             'currency': 'INR',
        #             'description':'BNI India products ',
        #             'return_url': globalSettings.SITE_ADDRESS + '/ebsPaymentResponse/',
        #             'name': request.user.first_name,
        #             'address': order.street,
        #             'city':order.city,
        #             'state':order.state,
        #             'country' : 'IN',
        #             'postal_code':order.pincode,
        #             'phone': order.user.profile.mobile,
        #             'email': order.user.email,
        #             'cust_email': globalSettings.G_ADMIN[0]
        #         }
        param_dict = data_dict

        hashVal = 'b47b8d9994e3356cf3c841ce9e025089'

        for key in sorted(param_dict.iterkeys()):
            print (("{} --> {}").format(key, param_dict[key]))
            hashVal += '|' + str(param_dict[key])


        m = hashlib.md5()
        m.update(hashVal)
        param_dict['secure_hash'] = m.hexdigest().upper()

        # res = requests.post('https://secure.ebs.in/pg/ma/payment/request', data = param_dict)

        # print res.headers
        # print res.text



        # return HttpResponse(res.text)
        return render(request, "ebs.payment.html" , {'data' : param_dict} )


class SendSMSApi(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.AllowAny ,)
    def post(self , request , format = None):
        print "came"
        if 'number' not in request.data or 'text' not in request.data:
            return Response(status = status.HTTP_400_BAD_REQUEST)
        else:
            try:
                url = globalSettings.SMS_API_PREFIX + 'mobiles=%s&message=%s'%(request.data['number'] , request.data['text'])
            except:
                url = globalSettings.SMS_API_PREFIX + 'number=%s&message=%s'%(request.data['number'] , request.data['text'])
            # print url
            requests.get(url)
            return Response(status = status.HTTP_200_OK)

def serviceRegistration(request): # the landing page for the vendors registration page
    return render(request , 'app.ecommerce.register.partner.html')

class serviceRegistrationApi(APIView):
    permission_classes = (permissions.AllowAny ,)

    def get(self, request , format = None):
        u = request.user
        if service.objects.filter(user = u).count() == 0:
            return Response(status = status.HTTP_404_NOT_FOUND)
        else:
            print service.objects.get(user = u).pk
        return Response(status = status.HTTP_200_OK)


    def post(self, request, format=None):
        u = request.user
        if not u.is_anonymous():
            if service.objects.filter(user = u).count() == 0:
                cp = customerProfile.objects.get(user = u)
                ad = cp.address
                if cp.mobile is None:
                    if 'mobile' in request.data:
                        mob = request.data['mobile']
                    else:
                        return Response({'mobile' : 'No contact number found in the account'}, status = status.HTTP_400_BAD_REQUEST)
                else:
                    mob = cp.mobile
                s = service(name = u.get_full_name() , user = u , cin = 0 , tin = 0 , address = ad , mobile = mob, telephone = mob , about = '')
            else:
                s = service.objects.get(user = u)
            s.save()
            add_application_access(u , ['app.ecommerce' , 'app.ecommerce.orders' , 'app.ecommerce.offerings','app.ecommerce.earnings'] , u)
            return Response( status = status.HTTP_200_OK)

        first_name = request.data['first_name']
        last_name = request.data['last_name']
        email = request.data['email']
        password = request.data['password']

        # serviceForm1 data
        name = request.data['name'] # company's name
        cin = request.data['cin']
        tin = request.data['tin']
        mobile = request.data['mobile']
        telephone = request.data['telephone']

        # serviceForm2 data
        street = request.data['street']
        pincode = request.data['pincode']
        city = request.data['city']
        state = request.data['state']
        about = request.data['about']

        if User.objects.filter(email = email).exists():
            content = { 'email' : 'Email ID already exists' }
            return Response(content, status=status.HTTP_400_BAD_REQUEST)
        else:
            user = User.objects.create(username = email.replace('@' , '').replace('.' ,''))
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.set_password(password)
            user.is_active = False
            user.save()
            ad = address(street = street , city = city , state = state , pincode = pincode )
            ad.save()
            se = service(name = name , user = user , cin = cin , tin = tin , address = ad , mobile = mobile, telephone = telephone , about = about)
            se.save()

            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            activation_key = hashlib.sha1(salt+email).hexdigest()
            key_expires = datetime.datetime.today() + datetime.timedelta(2)

            ak = accountsKey(user=user, activation_key=activation_key,
                key_expires=key_expires)
            link = globalSettings.SITE_ADDRESS + '/token/?key=%s' % (activation_key)
            ctx = {
                'logoUrl' : 'http://design.ubuntu.com/wp-content/uploads/ubuntu-logo32.png',
                'heading' : 'Welcome',
                'recieverName' : user.first_name,
                'message': 'Thanks for signing up. To activate your account, click this link within 48hours',
                'linkUrl': link,
                'linkText' : 'Activate',
                'sendersAddress' : 'Street 101 , State, City 100001',
                'sendersPhone' : '129087',
                'linkedinUrl' : 'linkedin.com',
                'fbUrl' : 'facebook.com',
                'twitterUrl' : 'twitter.com',
            }

            # Send email with activation key
            email_subject = 'Account confirmation'
            email_body = get_template('app.ecommerce.email.html').render(ctx)
            if globalSettings.EMAIL_API:
                sg = sendgrid.SendGridAPIClient(apikey= globalSettings.G_KEY)
                # sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
                data = {
                  "personalizations": [
                    {
                      "to": [
                        {
                          "email": email
                          # str(orderObj.user.email)
                        }
                      ],
                      "subject": email_subject
                    }
                  ],
                  "from": {
                    "email": globalSettings.G_FROM,
                    "name":"BNI India"
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
                msg = EmailMessage(email_subject, email_body, to= [email] , from_email= 'pkyisky@gmail.com' )
                msg.content_subtype = 'html'
                msg.send()
            content = {'pk' : user.pk , 'username' : user.username , 'email' : user.email}
            ak.save()
            return Response(content , status = status.HTTP_200_OK)

class addressViewSet(viewsets.ModelViewSet):
    permission_classes = (isAdmin , )
    serializer_class = addressSerializer
    def get_queryset(self):
        u = self.request.user
        has_application_permission(u , ['app.ecommerce' , 'app.ecommerce.orders'])
        return address.objects.all()

class serviceViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated , )
    serializer_class = serviceSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['name']
    def get_queryset(self):
        u = self.request.user
        return service.objects.all()

class deviceViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = deviceSerializer
    queryset = device.objects.all()

class profileViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = profileSerializer
    queryset = profile.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['id']



class AccountAdapter(DefaultAccountAdapter):

    def get_login_redirect_url(self, request):
        for a in globalSettings.DEFAULT_APPS_ON_REGISTER:
            app = application.objects.get(name = a)
            p = permission.objects.create(app =  app, user = request.user , givenBy = User.objects.get(pk=1))
        return globalSettings.ON_REGISTRATION_SUCCESS_REDIRECT

        # here we can know the device agent , or something to identify the app
        # redirect to happypocets.in/t/LKr8PiOTcILfeLgRxYA1
        # on the app login with this token  https://app.syrow.com/tlogin//?token=LKr8PiOTcILfeLgRxYA1&mode=api

def getModules(user , includeAll=False):
    if user.is_superuser:
        if includeAll:
            return module.objects.all()
        else:
            return module.objects.filter(~Q(name='public'))
    else:
        ma = []
        for m in application.objects.filter(owners__in = [user,]).values('module').distinct():
            ma.append(m['module'])
        aa = []
        for a in user.accessibleApps.all().values('app'):
            aa.append(a['app'])
        for m in application.objects.filter(pk__in = aa).values('module').distinct():
            ma.append(m['module'])
        return module.objects.filter(pk__in = ma)

class moduleViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = module.objects.all()
    serializer_class = moduleSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['name']
    def get_queryset(self):
        includeAll = False
        if 'mode' in self.request.GET:
            if self.request.GET['mode'] == 'search':
                includeAll = True
        u = self.request.user
        return getModules(u , includeAll)

def getApps(user):
    aa = []
    for a in user.accessibleApps.all().values('app'):
        aa.append(a['app'])
    if user.appsManaging.all().count()>0:
        try:
            if appSettingsField.objects.get(app=25,name='multipleStore').flag:
                return application.objects.filter(pk__in = aa).exclude(pk__in = user.appsManaging.all().values('pk')).exclude(module = module.objects.get(name = 'public')) | user.appsManaging.all()
            else:
                return application.objects.filter(pk__in = aa).exclude(pk__in = user.appsManaging.all().values('pk')).exclude(module = module.objects.get(name = 'public')).exclude(name='app.productsInventory.store') | user.appsManaging.all()
        except:
            return application.objects.filter(pk__in = aa).exclude(pk__in = user.appsManaging.all().values('pk')).exclude(module = module.objects.get(name = 'public')) | user.appsManaging.all()
    try:
        if appSettingsField.objects.get(app=25,name='multipleStore').flag:
            return application.objects.filter(pk__in = aa)
        else:
            return application.objects.filter(pk__in = aa).exclude(name='app.productsInventory.store')
    except:
        return application.objects.filter(pk__in = aa)


class applicationViewSet(viewsets.ModelViewSet):
    permission_classes = (readOnly,)
    serializer_class = applicationSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['name' , 'module']
    def get_queryset(self):
        u = self.request.user
        return getApps(u)
        # if not u.is_superuser:
        #     return getApps(u)
        # else:
        #     if 'user' in self.request.GET:
        #         return getApps(User.objects.get(username = self.request.GET['user']))
        #     try:
        #         if appSettingsField.objects.get(app=25,name='multipleStore').flag:
        #             return application.objects.filter()
        #         else:
        #             return application.objects.filter().exclude(name='app.productsInventory.store')
        #     except:
        #         return application.objects.filter()

class applicationAdminViewSet(viewsets.ModelViewSet):
    permission_classes = (isAdmin,)
    serializer_class = applicationAdminSerializer
    # queryset = application.objects.all()
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['name']
    def get_queryset(self):
        if not self.request.user.is_superuser:
            raise PermissionDenied(detail=None)
        return application.objects.all()


class applicationSettingsViewSet(viewsets.ModelViewSet):
    permission_classes = (readOnly , )
    queryset = appSettingsField.objects.all()
    serializer_class = applicationSettingsSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['app' , 'name']

class applicationSettingsAdminViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = appSettingsField.objects.all()
    serializer_class = applicationSettingsAdminSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['app' , 'name']


class groupPermissionViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = groupPermission.objects.all()
    serializer_class = groupPermissionSerializer

class permissionViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = permission.objects.all()
    serializer_class = permissionSerializer

class VendorViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['name' , 'gst' , 'panNumber']
    def get_queryset(self):
        toReturn = Vendor.objects.all()
        if 'search' in self.request.GET:
            toReturn = toReturn.filter(Q(gst__icontains = self.request.GET['search'])|Q(name__icontains = self.request.GET['search'])|Q(properiterName__icontains=self.request.GET['search'])|Q(panNumber__icontains=self.request.GET['search'])|Q(phone__icontains=self.request.GET['search'])|Q(email__icontains=self.request.GET['search']))
        return toReturn

class PoOrderViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    # queryset = PoOrder.objects.all()
    serializer_class = PoOrderSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['subject']
    def get_queryset(self):
        toReturn = PoOrder.objects.filter(user = self.request.user)
        if 'search' in self.request.GET:
            toReturn = toReturn.filter(Q(pk__icontains = self.request.GET['search'])|Q(subject__icontains = self.request.GET['search']))
        return toReturn


class PoItemsViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = PoItems.objects.all()
    serializer_class = PoItemsSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['po']

class PoOrderAllViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = PoOrder.objects.all()
    serializer_class = PoOrderAllSerializer
    # filter_backends = [DjangoFilterBackend]
    # filter_fields = ['po']


class BudgetAllocationViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    # queryset = BudgetAllocation.objects.all()
    serializer_class = BudgetAllocationSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['unit' , 'allotedBy']
    def get_queryset(self):
        if 'parent' in self.request.GET:
            toReturn = BudgetAllocation.objects.filter(parent__pk = int(self.request.GET['parent'])).order_by('-created')
        else:
            toReturn = BudgetAllocation.objects.all().order_by('-created')
        return toReturn

class ContingentViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    # queryset = PoOrder.objects.all()
    serializer_class = ContingentSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['subject']
    def get_queryset(self):
        toReturn = Contingent.objects.filter(unit = self.request.user)
        if 'search' in self.request.GET:
            toReturn = toReturn.filter(Q(pk__icontains = self.request.GET['search']))
        return toReturn

class GetBulkAllocation(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.AllowAny ,)
    def get(self, request , format = None):
        data = []
        allocationObj = BudgetAllocation.objects.filter(unit = request.user)
        allocationUniq = allocationObj.values_list('minorHead' , flat = True).distinct()
        for i in allocationUniq:
            val = {'minorHead' : i}
            allObj = allocationObj.filter(minorHead = i)
            val['codeHead'] = allObj.last().codeHead
            val['name'] = allObj.last().name
            val['created'] = allObj.last().created
            allotmentAmount = 0
            withdrawalAmount = 0
            balance = 0
            tot_amount = allObj.aggregate(tot = Sum('allotmentAmount'))
            if tot_amount['tot']!=None:
                allotmentAmount = tot_amount['tot']
            val['allotmentAmount'] = allotmentAmount
            withdraw_amount = allObj.aggregate(tot = Sum('withdrawalAmount'))
            if withdraw_amount['tot']!=None:
                withdrawalAmount = withdraw_amount['tot']
            val['withdrawalAmount'] = withdrawalAmount
            balance_amount = allObj.aggregate(tot = Sum('balance'))
            if balance_amount['tot']!=None:
                balance = balance_amount['tot']
            val['balance'] = balance
            data.append(val)

        return Response(data,status = status.HTTP_200_OK)


class GetAllAllocation(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.AllowAny ,)
    def get(self, request , format = None):
        allData = []
        if 'req' in request.GET:
            allocationObj = BudgetAllocation.objects.filter(allotedBy = request.user)
        else:
           allocationObj = BudgetAllocation.objects.filter(unit = request.user)
        allocationUniq = allocationObj.values_list('minorHead' , flat = True).distinct()
        for i in allocationUniq:
            allotObj = allocationObj.filter(minorHead = i)
            total = 0
            tot_amount = allotObj.aggregate(tot = Sum('allotmentAmount'))
            if tot_amount['tot']!=None:
                total = tot_amount['tot']
            val = {'minorHead' : i , 'data' : BudgetAllocationSerializer(allotObj,many = True).data, 'total' : total}
            val['codeHead'] = allotObj.last().codeHead
            val['name'] = allotObj.last().name
            allData.append(val)

        return Response(allData,status = status.HTTP_200_OK)

class WithdrawBudgetAPI(APIView):
    renderer_classes = (JSONRenderer,)
    permission_classes = (permissions.AllowAny ,)
    def post(self, request , format = None):
        if 'pk' in request.data:
            if 'wihdrawAmount' in request.data:
                withdrawnAmount = float(request.data['wihdrawAmount'])
            else:
                 withdrawnAmount = 0
            budObj = BudgetAllocation.objects.get(pk = int(request.data['pk']))
            parent = budObj.parent
            parent.withdrawalAmount = parent.withdrawalAmount - withdrawnAmount
            parent.balance = parent.balance + withdrawnAmount
            parent.save()
            budObj.allotmentAmount = budObj.allotmentAmount - withdrawnAmount
            budObj.balance =  budObj.balance - withdrawnAmount
            budObj.is_withdrawn = True
            budObj.save()
        val = {'data' : BudgetAllocationSerializer(budObj,many = False).data, 'total' : parent.balance}
        return Response(val,status = status.HTTP_200_OK)

def gengdf(response , poObj, request):


    MARGIN_SIZE = 8 * mm
    PAGE_SIZE = A4
    styles=getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']
    pdf_doc = SimpleDocTemplate(response, pagesize = PAGE_SIZE,
        leftMargin = MARGIN_SIZE, rightMargin = MARGIN_SIZE,
        topMargin = 4*MARGIN_SIZE, bottomMargin = 3*MARGIN_SIZE)

    tableHeaderStyle = styles['Normal'].clone('tableHeaderStyle')
    # tableHeaderStyle.textColor = colors.white;
    # tableHeaderStyle.fontSize = 7
    story = []

    summryParaSrc = """
    <para  align="center"><strong><u>CERTIFICATE OF GENUINE SUPPLIER AND RATES</u></strong><br/>
    <strong><u>VIDE GFR ART. %s</u></strong></para>
    """%(poObj.gfrRule)
    story.append(Paragraph(summryParaSrc , styleN))
    story.append(Spacer(2.5,0.5*cm))
    from reportlab.platypus import Image
    imagePath = os.path.join(globalSettings.BASE_DIR , 'static_shared','images' , 'download.png')
    f = open(imagePath, 'rb')
    ima = Image(f)
    ima.drawHeight = 1.25*inch
    ima.drawWidth = 1.25*inch
    ima.hAlign = 'CENTER'
    # ima.mask='auto'
    story.append(ima)
    # logo = "download.png"
    # f = open(logo, 'rb')
    # im = Image(f)
    # Story.append(im)
    story.append(Spacer(2.5,0.5*cm))
    summryParaSrc2 = """
    <para  align="left">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Certified that we, members of the local purchase committee are jointly and individually satisfied that the goods/services recommended for purchase are of the requisite specification and quality, priced at the prevailing market rate and the supplier <strong> %s %s </strong>, India recommended is reliable and competent to supply the goods in question it is not debarred by Department of Commerce of Ministry / department concerned. </para>
    """%(poObj.vendorName, poObj.vendorAddress)
    story.append(Paragraph(summryParaSrc2 , styleN))
    story.append(Spacer(2.5,0.5*cm))

    data = []
    pHeadSer = Paragraph('<strong>Ser</strong>' , tableHeaderStyle)
    pHeadDetails = Paragraph('<strong>Item</strong>' , tableHeaderStyle)
    pHeadDeno = Paragraph('<strong>Deno</strong>' , tableHeaderStyle)
    pHeadQty = Paragraph('<strong>Qty</strong>' , tableHeaderStyle)
    pHeadPrice = Paragraph('<strong>Rate</strong>' , tableHeaderStyle)
    pHeadAmount = Paragraph('<strong>Amount</strong>' , tableHeaderStyle)
    data.append([ pHeadSer, pHeadDetails, pHeadDeno, pHeadQty , pHeadPrice, pHeadAmount])
    grandTotal = 0
    count = 0
    tableBodyStyle = styles['Normal'].clone('tableBodyStyle')
    tableBodyStyle.fontSize = 7

    for i in poObj.poName.all():
        count+=1
        grandTotal+=i.grandTotal
        pBodySer = Paragraph(str(count) , tableBodyStyle)
        pBodyDetail = Paragraph(str(i.name) , tableBodyStyle)
        pBodyDeno= Paragraph(str(i.denominator) , tableBodyStyle)
        pBodyQty= Paragraph(str(i.quantity) , tableBodyStyle)
        pBodyRate= Paragraph(str(round(i.rate,2)) , tableBodyStyle)
        pBodyAmount= Paragraph(str(round(i.grandTotal,2)) , tableBodyStyle)
        data.append([pBodySer, pBodyDetail,pBodyDeno, pBodyQty, pBodyRate, pBodyAmount])

    data += [['', '','', Paragraph('Total Amount' , tableHeaderStyle)  , '',Paragraph(str(round(grandTotal,2)) , tableHeaderStyle) ],
            ['', '','', Paragraph('GST @ %' , tableHeaderStyle)  ,'', Paragraph('Inclusive' , tableHeaderStyle) ],
            ['', '', '',   Paragraph('Grand Total (INR)' , tableHeaderStyle), '' , Paragraph(str(round(grandTotal,2)) , tableHeaderStyle)]]
    t=Table(data)
    ts = TableStyle([('ALIGN',(1,1),(-3,-3),'RIGHT'),
                ('VALIGN',(0,1),(-1,-3),'TOP'),
                ('VALIGN',(0,-2),(-1,-2),'TOP'),
                ('VALIGN',(0,-1),(-1,-1),'TOP'),
                ('SPAN',(-3,-1),(-2,-1)),
                ('SPAN',(-3,-2),(-2,-2)),
                ('SPAN',(-3,-3),(-2,-3)),
                # ('LINEABOVE',(-2,-2),(-1,-2),0.25,colors.gray),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ])
    t.setStyle(ts)
    story.append(t)
    story.append(Spacer(2.5,0.75*cm))
    member_data = []
    member1 = """
    <para  align="left">%s<br/>%s<br/>%s<br/><strong>Member</strong> </para>
    """%(poObj.member1_name, poObj.member1_pos, poObj.member1_no)
    member2 = """
    <para  align="left">%s<br/>%s<br/>%s<br/><strong>Member</strong> </para>
    """%(poObj.member2_name, poObj.member2_pos, poObj.member2_no)
    member3 = """
    <para  align="left">%s<br/>%s<br/>%s<br/><strong>President</strong> </para>
    """%(poObj.member3_name, poObj.member3_pos, poObj.member3_no)
    member_data.append([Paragraph(member1 , tableHeaderStyle) , Paragraph(member2 , tableHeaderStyle)  , Paragraph(member3 , tableHeaderStyle) ])
    member_table=Table(member_data)
    story.append(member_table)
    story.append(Spacer(4.5,0.5*cm))
    countSign = """
    <para  align="center"><strong>COUNTERSIGNED</strong><br/><br/><br/><br/><br/><br/><br/><br/></para>
    """
    story.append(Paragraph(countSign , styleN))
    story.append(Spacer(2.5,0.75*cm))
    otherDetail = """
    <para >File No: %s <br/> Unit : %s <br/> Date : %s</para>
    """%(poObj.fileNo, poObj.unitAddress , poObj.dated)
    story.append(Paragraph(otherDetail , styleN))

    pdf_doc.build(story)


class DownloadGRF(APIView):
    renderer_classes = (JSONRenderer,)
    def get(self , request , format = None):
        if 'id' not in request.GET:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        response = HttpResponse(content_type='application/pdf')
        o = PoOrder.objects.get(id = int(request.GET['id']))
        response['Content-Disposition'] = 'attachment; filename="grf_%s.pdf'%( o.pk)
        gengdf(response , o , request)
        # f = open('./media_root/grf_%s.pdf'%( o.pk) , 'wb')
        # f.write(response.content)
        # f.close()
        return response

def genSupplyOrder(response , poObj, request):


    MARGIN_SIZE = 8 * mm
    PAGE_SIZE = A4
    styles=getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']
    pdf_doc = SimpleDocTemplate(response, pagesize = PAGE_SIZE,
        leftMargin = MARGIN_SIZE, rightMargin = MARGIN_SIZE,
        topMargin = 4*MARGIN_SIZE, bottomMargin = 3*MARGIN_SIZE)

    tableHeaderStyle = styles['Normal'].clone('tableHeaderStyle')
    # tableHeaderStyle.textColor = colors.white;
    # tableHeaderStyle.fontSize = 7
    story = []

    summryParaSrc = """
    <para  align="center"><strong>SUPPLY ORDER</strong></para>
    """
    story.append(Paragraph(summryParaSrc , styleN))
    story.append(Spacer(2.5,0.5*cm))
    story.append(Spacer(2.5,0.5*cm))
    summryParaSrc2 = """
    <para  align="left">Dear Sir,<br/> <br/> 1. Please refer to your quotation No. %s dated %s. <br/><br/>  2. Your quotation for supply of following items has been accepted. You are requested to supply the same to this Unit at the earliest: -  </para>
    """%(poObj.quoteNo, poObj.quoteDate)
    story.append(Paragraph(summryParaSrc2 , styleN))
    story.append(Spacer(2.5,0.5*cm))

    data = []
    pHeadSer = Paragraph('<strong>Ser</strong>' , tableHeaderStyle)
    pHeadDetails = Paragraph('<strong>Item</strong>' , tableHeaderStyle)
    pHeadDeno = Paragraph('<strong>Deno</strong>' , tableHeaderStyle)
    pHeadQty = Paragraph('<strong>Qty</strong>' , tableHeaderStyle)
    pHeadPrice = Paragraph('<strong>Rate</strong>' , tableHeaderStyle)
    pHeadAmount = Paragraph('<strong>Amount</strong>' , tableHeaderStyle)
    data.append([ pHeadSer, pHeadDetails, pHeadDeno, pHeadQty , pHeadPrice, pHeadAmount])
    grandTotal = 0
    count = 0
    tableBodyStyle = styles['Normal'].clone('tableBodyStyle')
    tableBodyStyle.fontSize = 7

    for i in poObj.poName.all():
        count+=1
        grandTotal+=i.grandTotal
        pBodySer = Paragraph(str(count) , tableBodyStyle)
        pBodyDetail = Paragraph(str(i.name) , tableBodyStyle)
        pBodyDeno= Paragraph(str(i.denominator) , tableBodyStyle)
        pBodyQty= Paragraph(str(i.quantity) , tableBodyStyle)
        pBodyRate= Paragraph(str(i.rate) , tableBodyStyle)
        pBodyAmount= Paragraph(str(i.grandTotal) , tableBodyStyle)
        data.append([pBodySer, pBodyDetail,pBodyDeno, pBodyQty, pBodyRate, pBodyAmount])

    data += [['', '','', Paragraph('Total Amount' , tableHeaderStyle)  , '',Paragraph(str(grandTotal) , tableHeaderStyle) ],
            ['', '','', Paragraph('GST @ %' , tableHeaderStyle)  ,'', Paragraph('Inclusive' , tableHeaderStyle) ],
            ['', '', '',   Paragraph('Grand Total (INR)' , tableHeaderStyle), '' , Paragraph(str(grandTotal) , tableHeaderStyle)]]
    t=Table(data)
    ts = TableStyle([('ALIGN',(1,1),(-3,-3),'RIGHT'),
                ('VALIGN',(0,1),(-1,-3),'TOP'),
                ('VALIGN',(0,-2),(-1,-2),'TOP'),
                ('VALIGN',(0,-1),(-1,-1),'TOP'),
                ('SPAN',(-3,-1),(-2,-1)),
                ('SPAN',(-3,-2),(-2,-2)),
                ('SPAN',(-3,-3),(-2,-3)),
                # ('LINEABOVE',(-2,-2),(-1,-2),0.25,colors.gray),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ])
    t.setStyle(ts)
    story.append(t)
    story.append(Spacer(2.5,0.75*cm))

    countSign = """
    <para  align="left">3. You are further requested that a pre-receipted bill be forwarded to this unit for early settlement of bill. An ECS (Electronic Clearing Service) form that enclosed to this letter are to be signed by you and the authorized official of the bank in which bank you need the banking transaction as payment will be made directly by the office of Controller of Defence Accounts, Agram Post, Bangalore-7. <u> Kindly fill the form correctly and have a through check.</u></para>
    """
    story.append(Paragraph(countSign , styleN))
    story.append(Spacer(2.5,0.75*cm))
    thankYou = """
    <para  align="left">Thanking you,</para>
    """
    yoursFaith = """
    <para  align="right">Yours faithfully<br/><br/>( %s )<br/>%s<br/>Commanding Officer</para>
    """ %(poObj.user.last_name , poObj.user.profile.rank)
    dataVal = [[Paragraph(thankYou , styleN),Paragraph(yoursFaith , styleN)]]
    t2=Table(dataVal)
    story.append(t2)
    story.append(Spacer(2.5,0.75*cm))

    pdf_doc.build(story)

class DownloadSupplyOrder(APIView):
    renderer_classes = (JSONRenderer,)
    def get(self , request , format = None):
        if 'id' not in request.GET:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        response = HttpResponse(content_type='application/pdf')
        o = PoOrder.objects.get(id = int(request.GET['id']))
        response['Content-Disposition'] = 'attachment; filename="saleOrder_%s.pdf'%( o.pk)
        genSupplyOrder(response , o , request)
        # f = open('./media_root/grf_%s.pdf'%( o.pk) , 'wb')
        # f.write(response.content)
        # f.close()
        return response


def genApplication(response , poObj, request):


    MARGIN_SIZE = 8 * mm
    PAGE_SIZE = A4
    styles=getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']
    pdf_doc = SimpleDocTemplate(response, pagesize = PAGE_SIZE,
        leftMargin = MARGIN_SIZE, rightMargin = MARGIN_SIZE,
        topMargin = 4*MARGIN_SIZE, bottomMargin = 3*MARGIN_SIZE)

    tableHeaderStyle = styles['Normal'].clone('tableHeaderStyle')
    # tableHeaderStyle.textColor = colors.white;
    # tableHeaderStyle.fontSize = 7
    story = []

    summryParaSrc = """
    <para  align="center"><strong><u>APPLICATION FOR LOCAL PURCHASE SANCTION: <br/> UNDER CENTRAL SHARE OF ATG 2019-20 </u></strong></para>
    """
    story.append(Paragraph(summryParaSrc , styleN))
    story.append(Spacer(2.5,0.5*cm))
    summryParaUnit = """
    <para >Unit : %s</para>
    """%(poObj.user.first_name )
    story.append(Paragraph(summryParaUnit , styleN))
    data = []
    pHeadSer = Paragraph('<strong>Ser</strong>' , tableHeaderStyle)
    pHeadDetails = Paragraph('<strong>Items to be purchased</strong>' , tableHeaderStyle)
    pHeadDeno = Paragraph('<strong>Deno</strong>' , tableHeaderStyle)
    pHeadQty = Paragraph('<strong>Qty</strong>' , tableHeaderStyle)
    pHeadPrice = Paragraph('<strong>Rate</strong>' , tableHeaderStyle)
    pHeadAmount = Paragraph('<strong>Amount</strong>' , tableHeaderStyle)
    pHeadVendor= Paragraph('<strong>'+poObj.vendorName+'<br/>'+poObj.vendorAddress+'</strong>' , tableHeaderStyle)
    data.append([ pHeadSer, pHeadDetails, pHeadDeno, pHeadQty , pHeadPrice, pHeadAmount,pHeadVendor])
    grandTotal = 0
    count = 0
    tableBodyStyle = styles['Normal'].clone('tableBodyStyle')
    tableBodyStyle.fontSize = 7
    toWordtot = ''
    for i in poObj.poName.all():
        count+=1
        grandTotal+=i.grandTotal
        pBodySer = Paragraph(str(count) , tableBodyStyle)
        pBodyDetail = Paragraph(str(i.name) , tableBodyStyle)
        pBodyDeno= Paragraph(str(i.denominator) , tableBodyStyle)
        pBodyQty= Paragraph(str(i.quantity) , tableBodyStyle)
        pBodyRate= Paragraph(str(i.rate) , tableBodyStyle)
        pBodyAmount= Paragraph(str(i.grandTotal) , tableBodyStyle)
        data.append([pBodySer, pBodyDetail,pBodyDeno, pBodyQty, pBodyRate, pBodyAmount,pHeadVendor])
    toWordtot = num2words(round(grandTotal), lang='en_IN')
    data += [[Paragraph(toWordtot , tableHeaderStyle),'', '', '','', Paragraph(str(grandTotal) , tableHeaderStyle) , '']]
    t=Table(data)
    ts = TableStyle([('ALIGN',(1,1),(-3,-3),'RIGHT'),
                ('VALIGN',(0,1),(-1,-3),'TOP'),
                ('VALIGN',(0,-2),(-1,-2),'TOP'),
                ('VALIGN',(0,-1),(-1,-1),'TOP'),
                ('SPAN',(-3,-1),(-7,-1)),
                ('SPAN',(-1,0),(-1,-1)),
                ('VALIGN',(-1,0),(-1,-1),'MIDDLE'),
                # ('SPAN',(-1,-1),(-2,-1)),
                # ('LINEABOVE',(-2,-2),(-1,-2),0.25,colors.gray),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ])
    t.setStyle(ts)
    story.append(t)
    story.append(Spacer(2.5,0.75*cm))

    desc = """
    <para  align="left">3. Document attached ( Please tick ) <br/> a. Statement of case (When CFA is DGNCC/Ex-Post Fado Sanction) <br/> b. Calling for quotation/estimated cost letter from Unit to firm  <br/> c. Quotation duly endorsed by CO of Unit <br/> i. General Dealer - Nil <br/> ii. Authorised dealer/service station - 01 <br/> d.  Competative statement (02 Copies) approved by board of officer duly recommended by group commander ( in case of Para 3 (c) (i) above) <br/> e.NA Certificate from concerned ord depot - N/A <br/> f. Authentication of authorised dealership in case of Para 3c of (ii) above  </para>
    """
    dataVal1 = Paragraph(desc , styleN)
    story.append(dataVal1)
    para1 = """
    <para  >4. State Funds</para>
    """
    para2 = """
    <para  align="right"> Alloted : <br/>Amount utilised excluding this bill : <br/>Praposal for an amount of : </para>
    """
    para3 = """
    <para > Rs 56,900.00  <br/>Rs Nil <br/>Rs Nil  </para>
    """
    dataVal = [[Paragraph(para1 , styleN),Paragraph(para2 , styleN),Paragraph(para3 , styleN)]]
    t2=Table(dataVal)
    story.append(t2)
    story.append(Spacer(2.5,0.75*cm))
    otherDetail = """
    <para >  Date : %s  <br/> File No: %s</para>
    """%(poObj.dated , poObj.fileNo )
    otherDetail2 = """
    <para align="right"> <br/><br/><br/><br/><br/><br/>Signature of Commanding Officer</para>
    """
    dataValbottom = [[Paragraph(otherDetail , styleN),Paragraph(otherDetail2 , styleN)]]
    t3=Table(dataValbottom)
    story.append(t3)
    story.append(Spacer(4.5,0.75*cm))
    summryParaSrc1 = """
    <para  align="center"><strong><u>RECOMMENDATION OF GROUP COMMANDER </u></strong></para>
    """
    story.append(Paragraph(summryParaSrc1 , styleN))
    desc1 = """
    <para  align="left">5. All documents have been scrutinized for correctness and recommended for local purchase. <br/>6. Fund state of Gp HQ is as follows:  </para>
    """
    dataVal2 = Paragraph(desc1 , styleN)
    story.append(dataVal2)
    para11 = """
    <para  align="center">Allotted</para>
    """
    para12 = """
    <para > Rs..____________________  </para>
    """
    dataVal11 = [[Paragraph(para11 , styleN),'',Paragraph(para12 , styleN)]]
    t12=Table(dataVal11)
    story.append(t12)
    para21 = """
    <para  align="center">Utilised</para>
    """
    para22 = """
    <para >1) Amount sanction at unit/Gp level <br/> 2) Amount sanction at Dte level <br/> Total utilised Rs. </para>
    """
    para23 = """
    <para > Rs..____________________ <br/> Rs..____________________ <br/> Rs..____________________  </para>
    """
    dataVal21 = [[Paragraph(para21 , styleN),Paragraph(para22 , styleN),Paragraph(para23 , styleN)]]
    t22=Table(dataVal21)
    story.append(t22)
    desc2 = """
    <para  align="left">7. Any other recommendation ________________________________________  </para>
    """
    dataVal3 = Paragraph(desc2 , styleN)
    story.append(dataVal3)
    story.append(Spacer(2.5,0.5*cm))
    para31 = """
    <para  >Date : ___________</para>
    """
    para32 = """
    <para  align="right"> Group Commander </para>
    """
    dataVal4 = [[Paragraph(para31 , styleN),Paragraph(para32 , styleN)]]
    t4=Table(dataVal4)
    story.append(t4)
    story.append(Spacer(2.5,0.5*cm))
    pdf_doc.build(story)

class DownloadApplication(APIView):
    renderer_classes = (JSONRenderer,)
    def get(self , request , format = None):
        if 'id' not in request.GET:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        response = HttpResponse(content_type='application/pdf')
        o = PoOrder.objects.get(id = int(request.GET['id']))
        response['Content-Disposition'] = 'attachment; filename="application_%s.pdf'%( o.pk)
        genApplication(response , o , request)
        # f = open('./media_root/grf_%s.pdf'%( o.pk) , 'wb')
        # f.write(response.content)
        # f.close()
        return response


def genSanction(response , poObj, request):
    MARGIN_SIZE = 8 * mm
    PAGE_SIZE = A4
    styles=getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']
    pdf_doc = SimpleDocTemplate(response, pagesize = PAGE_SIZE,
        leftMargin = MARGIN_SIZE, rightMargin = MARGIN_SIZE,
        topMargin = 4*MARGIN_SIZE, bottomMargin = 3*MARGIN_SIZE)

    tableHeaderStyle = styles['Normal'].clone('tableHeaderStyle')
    # tableHeaderStyle.textColor = colors.white;
    # tableHeaderStyle.fontSize = 7
    story = []
    tableBodyStyle = styles['Normal'].clone('tableBodyStyle')
    tableBodyStyle.fontSize = 7
    summryParaSrc = """
    <para  align="center"><strong><u>SANCTION OF EXPENDITURE UNDER ATG/AMENITY/IT </u></strong><br/>
    </para>
    """
    story.append(Paragraph(summryParaSrc , styleN))
    story.append(Spacer(2.5,0.5*cm))
    from reportlab.platypus import Image
    imagePath = os.path.join(globalSettings.BASE_DIR , 'static_shared','images' , 'download.png')
    f = open(imagePath, 'rb')
    ima = Image(f)
    ima.drawHeight = 1.25*inch
    ima.drawWidth = 1.25*inch
    ima.hAlign = 'CENTER'
    # ima.mask='auto'
    story.append(ima)
    # logo = "download.png"
    # f = open(logo, 'rb')
    # im = Image(f)
    # Story.append(im)
    # story.append(Spacer(2.5,0.5*cm))
    # story.append(Paragraph(summryParaSrc2 , styleN))
    story.append(Spacer(2.5,0.5*cm))
    mainData = []
    para1 = Paragraph('1' , tableBodyStyle)
    para2 = Paragraph('Broad Purpose of Sanction' , tableBodyStyle)
    para3 = Paragraph('Subject' , tableBodyStyle)
    mainData.append([ para1, para2, '', para3 ])
    para4 = Paragraph('2' , tableBodyStyle)
    para5 = Paragraph('Govt Authority or Schedule /Sub-Schedule of Power under which the sanction /order is being issued' , tableBodyStyle)
    para6 = Paragraph('0106/DGNCC/Pers/B&F/335/A/D(GS-VI) dt 11 Apr 1990 and 0106/DGNCC/Bud 2435/D(GS-VI/2001 dt 31 Oct 2001' , tableBodyStyle)
    mainData.append([ para4, para5, '', para6 ])
    tmain=Table(mainData , colWidths=(10*mm , 85*mm , 10*mm, 85*mm))
    tsmain = TableStyle([('ALIGN',(1,1),(-3,-3),'RIGHT'),
                ('VALIGN',(0,1),(-1,-3),'TOP'),
                ('VALIGN',(0,-2),(-1,-2),'TOP'),
                ('VALIGN',(0,-1),(-1,-1),'TOP'),
                # ('SPAN',(-3,-1),(-2,-1)),
                # ('SPAN',(-3,-2),(-2,-2)),
                # ('SPAN',(-3,-3),(-2,-3)),
                # ('LINEABOVE',(-2,-2),(-1,-2),0.25,colors.gray),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ])
    tmain.setStyle(tsmain)
    story.append(tmain)
    data = []
    pHeadSer = Paragraph('<strong>Ser</strong>' , tableHeaderStyle)
    pHeadDetails = Paragraph('<strong>Item</strong>' , tableHeaderStyle)
    pHeadDeno = Paragraph('<strong>Deno</strong>' , tableHeaderStyle)
    pHeadQty = Paragraph('<strong>Qty</strong>' , tableHeaderStyle)
    pHeadPrice = Paragraph('<strong>Rate</strong>' , tableHeaderStyle)
    pHeadAmount = Paragraph('<strong>Amount</strong>' , tableHeaderStyle)
    data.append(['3', pHeadSer, pHeadDetails, pHeadDeno, pHeadQty , pHeadPrice, pHeadAmount])
    grandTotal = 0
    count = 0


    for i in poObj.poName.all():
        count+=1
        grandTotal+=i.grandTotal
        pBodySer = Paragraph(str(count) , tableBodyStyle)
        pBodyDetail = Paragraph(str(i.name) , tableBodyStyle)
        pBodyDeno= Paragraph(str(i.denominator) , tableBodyStyle)
        pBodyQty= Paragraph(str(i.quantity) , tableBodyStyle)
        pBodyRate= Paragraph(str(round(i.rate,2)) , tableBodyStyle)
        pBodyAmount= Paragraph(str(round(i.grandTotal,2)) , tableBodyStyle)
        data.append(['',pBodySer, pBodyDetail,pBodyDeno, pBodyQty, pBodyRate, pBodyAmount])

    data += [['','', '','', Paragraph('Total Amount' , tableHeaderStyle)  , '',Paragraph(str(round(grandTotal,2)) , tableHeaderStyle) ],
            ['','', '','', Paragraph('GST @ %' , tableHeaderStyle)  ,'', Paragraph('Inclusive' , tableHeaderStyle) ],
            ['','', '', '',   Paragraph('Grand Total (INR)' , tableHeaderStyle), '' , Paragraph(str(round(grandTotal,2)) , tableHeaderStyle)]]
    t=Table(data, colWidths=(10*mm, None, None, None, None, None, None))
    ts = TableStyle([('ALIGN',(1,1),(-3,-3),'RIGHT'),
                ('VALIGN',(0,1),(-1,-3),'TOP'),
                ('VALIGN',(0,-2),(-1,-2),'TOP'),
                ('VALIGN',(0,-1),(-1,-1),'TOP'),
                ('SPAN',(-3,-1),(-2,-1)),
                ('SPAN',(-3,-2),(-2,-2)),
                ('SPAN',(-3,-3),(-2,-3)),
                ('SPAN',(0,0),(0,-1)),
                ('VALIGN',(0,0),(0,-1),'TOP'),
                # ('LINEABOVE',(-2,-2),(-1,-2),0.25,colors.gray),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ])
    t.setStyle(ts)
    story.append(t)
    bottomData = []
    para7 = Paragraph('4' , tableBodyStyle)
    para8 = Paragraph('Major Head' , tableBodyStyle)
    para9 = Paragraph('' , tableBodyStyle)
    bottomData.append([ para7, para8, '', para9 ])
    para10 = Paragraph('5' , tableBodyStyle)
    para11 = Paragraph('Minor Head' , tableBodyStyle)
    para12 = Paragraph(str(poObj.minorHead) , tableBodyStyle)
    bottomData.append([ para10, para11, '', para12 ])
    para13 = Paragraph('6' , tableBodyStyle)
    para14= Paragraph('Sub Head' , tableBodyStyle)
    para15 = Paragraph('F-2, Expenditure on other training activity' , tableBodyStyle)
    bottomData.append([ para13, para14, '', para15 ])
    para15 = Paragraph('7' , tableBodyStyle)
    para16= Paragraph('Code Head' , tableBodyStyle)
    para17 = Paragraph(str(poObj.codeHead), tableBodyStyle)
    bottomData.append([ para15, para16, '', para17 ])
    para18 = Paragraph('8' , tableBodyStyle)
    para19 = Paragraph('Balance funds available , taking into account committed liabilities, before sanction of this case' , tableBodyStyle)
    para20 = Paragraph('BALANCE OF UNIT FUND', tableBodyStyle)
    bottomData.append([ para18, para19, '', para20 ])
    para21 = Paragraph('9' , tableBodyStyle)
    para22 = Paragraph('Name of paying Agency ' , tableBodyStyle)
    para23 = Paragraph('PCDA Bangalore', tableBodyStyle)
    bottomData.append([ para21, para22, '', para23 ])
    para24 = Paragraph('10' , tableBodyStyle)
    para25 = Paragraph('Whether being issued under inherent powers or with concurrence of IFA ' , tableBodyStyle)
    para26 = Paragraph('issued under inherent', tableBodyStyle)
    bottomData.append([ para24, para25, '', para26 ])
    para27 = Paragraph('11' , tableBodyStyle)
    para28 = Paragraph('U.O number allotted by IFA' , tableBodyStyle)
    para29 = Paragraph('NA', tableBodyStyle)
    bottomData.append([ para27, para28, '', para29 ])
    para30 = Paragraph('12' , tableBodyStyle)
    para31 = Paragraph("Communication of sanction being signed by the undersigned under power delegated by CFA to sign such financial documents vide CFAs letter number 0106/DGNCC/Bud2435/D(GS-VI/2001 dated 31 Oct 2001" , tableBodyStyle)
    bottomData.append([ para30, para31, '', '' ])
    tbottom=Table(bottomData , colWidths=(10*mm , 85*mm , 10*mm, 85*mm))
    tsbottom = TableStyle([('ALIGN',(1,1),(-3,-3),'RIGHT'),
                ('VALIGN',(0,1),(-1,-3),'TOP'),
                ('VALIGN',(0,-2),(-1,-2),'TOP'),
                ('VALIGN',(0,-1),(-1,-1),'TOP'),
                ('SPAN',(-3,-1),(-1,-1)),
                # ('SPAN',(-3,-2),(-2,-2)),
                # ('SPAN',(-3,-3),(-2,-3)),
                # ('LINEABOVE',(-2,-2),(-1,-2),0.25,colors.gray),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ])
    tbottom.setStyle(tsbottom)
    story.append(tbottom)
    story.append(Spacer(2.5,0.75*cm))
    otherDetail = """
    <para >   File No: %s <br/> Date of issue : %s  </para>
    """%(poObj.dated , poObj.fileNo )
    otherDetail2 = """
    <para align="right"> <br/><br/><br/><br/><br/><br/>Signature</para>
    """
    dataValbottom = [[Paragraph(otherDetail , styleN),Paragraph(otherDetail2 , styleN)]]
    t3=Table(dataValbottom)
    story.append(t3)

    pdf_doc.build(story)


class DownloadSanction(APIView):
    renderer_classes = (JSONRenderer,)
    def get(self , request , format = None):
        if 'id' not in request.GET:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        response = HttpResponse(content_type='application/pdf')
        o = PoOrder.objects.get(id = int(request.GET['id']))
        response['Content-Disposition'] = 'attachment; filename="sanction_%s.pdf'%( o.pk)
        genSanction(response , o , request)
        # f = open('./media_root/grf_%s.pdf'%( o.pk) , 'wb')
        # f.write(response.content)
        # f.close()
        return response

def genContigent(response , poObj, request):
    MARGIN_SIZE = 8 * mm
    PAGE_SIZE = A4
    styles=getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']
    pdf_doc = SimpleDocTemplate(response, pagesize = PAGE_SIZE,
        leftMargin = MARGIN_SIZE, rightMargin = MARGIN_SIZE,
        topMargin = 4*MARGIN_SIZE, bottomMargin = 3*MARGIN_SIZE)

    tableHeaderStyle = styles['Normal'].clone('tableHeaderStyle')
    tableBodyStyle = styles['Normal'].clone('tableBodyStyle')
    tableBodyStyle.fontSize = 7
    # tableHeaderStyle.textColor = colors.white;
    # tableHeaderStyle.fontSize = 7
    story = []
    mainData = []
    header1 = """
    <para > Contingent bill No. </para>
    """
    header2 = """
    <para align = "center"> 5Navy/ATG/550/02/CB/02 <br/> 14 Jan 2020 </para>
    """
    header3 = """
    <para align = "right"> Code Head  <br/> Amount allotted  <br/>Amount expended including this bill  <br/> Amount Balance  </para>
    """
    header4 = """
    <para > : 01/550/02 <br/>  : 56,900.00 <br/> : 17,525.00 <br/>  : 39,375.00 </para>
    """
    para1 = Paragraph(header1 , tableBodyStyle)
    para2 = Paragraph(header2, tableBodyStyle)
    para3 = Paragraph(header3 , tableBodyStyle)
    para4 = Paragraph(header4, tableBodyStyle)
    mainData = [[ para1, para2, para3, para4 ]]
    tmain=Table(mainData , colWidths=(25*mm , 33*mm , 107*mm, 25*mm))
    tsmain = TableStyle([
                ('VALIGN',(0,1),(-1,-3),'TOP'),
                ('VALIGN',(0,-2),(-1,-2),'TOP'),
                ('VALIGN',(0,-1),(-1,-1),'TOP'),
            ])
    tmain.setStyle(tsmain)
    story.append(tmain)
    story.append(Spacer(2.5,0.75*cm))
    summryParaSrc = """
    <para  align="center"><strong><u>CONTINGENT BILL </u></strong><br/>
    </para>
    """
    story.append(Paragraph(summryParaSrc , styleN))
    story.append(Spacer(2.5,0.5*cm))
    summryParaSrc2 = """
    <para >Expenditure on account purchasing of ATG items under Annual Training Grant Head incurred by the
    Commanding Officer, No. 5 Kar NU NCC, Mangalore for the month Jan 2020. <br/> <strong><u>Auth:</u></strong> (a) GOI MOD Letter No. 0106/DGNCC/Bud/2435/D(GS-VI)/2001 dated 31 Oct 2001.<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(b) Dy DG NCC, Bangalore sanction letter 028/Grant/Mng/Trg dated 24 Dec 2019 (Original enclosed).<br/>Debitable to major Head 2076 Minor head 113-NCC, Code Head 1/550/02 of Defence service estimates for the financial year 2019-20.
    </para>
    """
    story.append(Paragraph(summryParaSrc2 , styleN))
    story.append(Spacer(2.5,0.5*cm))
    # d = Drawing(100, 1)
    # d.add(Line(0, 0, 100, 0))
    # story.add(d)
    summryParaSrc3 = """
    <para ><strong><u> Date</u></strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<strong><u> Details of expenditure</u></strong>
    </para>
    """
    story.append(Paragraph(summryParaSrc3 , styleN))
    summryParaSrc4 = """
    <para >Jan 2020 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Expenditure incurred towards purchasing of ATG items from M/s Radiance Enterprises
    Hamilton complex, Near D.C Office, Mangalore -575001 vide their bill No. 4050 dated 13 Jan 2020.
    </para>
    """
    story.append(Paragraph(summryParaSrc4 , styleN))
    story.append(Spacer(2.5,0.5*cm))
    data = []
    pHeadSer = Paragraph('<strong>Ser</strong>' , tableHeaderStyle)
    pHeadDetails = Paragraph('<strong>Item</strong>' , tableHeaderStyle)
    pHeadDeno = Paragraph('<strong>Deno</strong>' , tableHeaderStyle)
    pHeadQty = Paragraph('<strong>Qty</strong>' , tableHeaderStyle)
    pHeadPrice = Paragraph('<strong>Rate</strong>' , tableHeaderStyle)
    pHeadAmount = Paragraph('<strong>Amount</strong>' , tableHeaderStyle)
    data.append([ pHeadSer, pHeadDetails, pHeadDeno, pHeadQty , pHeadPrice, pHeadAmount])
    grandTotal = 0
    count = 0


    for i in poObj.po.poName.all():
        count+=1
        grandTotal+=i.grandTotal
        pBodySer = Paragraph(str(count) , tableBodyStyle)
        pBodyDetail = Paragraph(str(i.name) , tableBodyStyle)
        pBodyDeno= Paragraph(str(i.denominator) , tableBodyStyle)
        pBodyQty= Paragraph(str(i.quantity) , tableBodyStyle)
        pBodyRate= Paragraph(str(round(i.rate,2)) , tableBodyStyle)
        pBodyAmount= Paragraph(str(round(i.grandTotal,2)) , tableBodyStyle)
        data.append([pBodySer, pBodyDetail,pBodyDeno, pBodyQty, pBodyRate, pBodyAmount])

    data += [['','', '','', Paragraph('Total Amount' , tableHeaderStyle)  , '',Paragraph(str(round(grandTotal,2)) , tableHeaderStyle) ],
            ['', '','', '',Paragraph('GST @ %' , tableHeaderStyle)  ,'', Paragraph('Inclusive' , tableHeaderStyle) ],
            ['', '', '',  '', Paragraph('Grand Total (INR)' , tableHeaderStyle), '' , Paragraph(str(round(grandTotal,2)) , tableHeaderStyle)]]
    t=Table(data)
    ts = TableStyle([('ALIGN',(1,1),(-3,-3),'RIGHT'),
                ('VALIGN',(0,1),(-1,-3),'TOP'),
                ('VALIGN',(0,-2),(-1,-2),'TOP'),
                ('VALIGN',(0,-1),(-1,-1),'TOP'),
                ('SPAN',(-3,-1),(-2,-1)),
                ('SPAN',(-3,-2),(-2,-2)),
                ('SPAN',(-3,-3),(-2,-3)),
                # ('LINEABOVE',(-2,-2),(-1,-2),0.25,colors.gray),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ])
    t.setStyle(ts)
    story.append(t)
    story.append(Spacer(2.5,0.5*cm))
    summryParaSrc5 = """
    <para ><strong><u> Certified that :-</u></strong><br/>a) The above items have been received in good condition and taken on charge in the ledger vide <strong><u>  CRV No - 5 Navy/ATG /CRV/01 dated 13 Jan 2020.</u></strong><br/>b) The quotation accepted being the lowest and good quality items.<br/>c) The standard rates of items have been purchased.<br/>d) Items are required for cadet training.<br/>e) The amount in question has not been claimed/received so far.<br/>Total Amount : Rs.13,625.00 &nbsp;&nbsp;&nbsp; Advance received : Nil &nbsp;&nbsp;&nbsp; Amount due : 13,625.00
    </para>
    """
    story.append(Paragraph(summryParaSrc5 , styleN))
    story.append(Spacer(2.5,0.5*cm))
    otherDetail = """
    <para >  Date : %s  <br/> Place: </para>
    """%(poObj.po.dated )
    otherDetail2 = """
    <para  align="right">( %s )<br/>%s<br/>Commanding Officer</para>
    """ %(poObj.po.user.last_name , poObj.po.user.profile.rank)
    dataValbottom = [[Paragraph(otherDetail , styleN),Paragraph(otherDetail2 , styleN)]]
    t3=Table(dataValbottom)
    story.append(t3)
    story.append(Spacer(4.5,0.5*cm))
    countSign = """
    <para  align="center"><strong>COUNTERSIGNED</strong><br/><br/><br/><br/><br/><br/><br/><br/></para>
    """
    story.append(Paragraph(countSign , styleN))
    story.append(Spacer(4.5,0.5*cm))
    summryParaSrc6= """
    <para >It is requested that cheque for the above amount be forwarded to <strong><u>Syndicate Bank Lalbagh Branch Mangalore Account No 02411400001902 IFSC  SYSNB0000241 </u></strong> in favour of <strong>M/s Radiance Enterprises Hamilton complex Near DC Office Mangalore  575001 at the earliest.</strong> </para>
    """
    story.append(Paragraph(summryParaSrc6, styleN))
    story.append(Spacer(2.5,0.5*cm))
    summryParaSrc7= """
    <para align="right"> <strong><u>RECEIVED PAYMENT </u></strong>  </para>
    """
    story.append(Paragraph(summryParaSrc7, styleN))
    story.append(Spacer(2.5,0.5*cm))
    # bottomData = []
    # para7 = Paragraph('4' , tableBodyStyle)
    # para8 = Paragraph('Major Head' , tableBodyStyle)
    # para9 = Paragraph('' , tableBodyStyle)
    # bottomData.append([ para7, para8, '', para9 ])
    # para10 = Paragraph('5' , tableBodyStyle)
    # para11 = Paragraph('Minor Head' , tableBodyStyle)
    # para12 = Paragraph(str(poObj.minorHead) , tableBodyStyle)
    # bottomData.append([ para10, para11, '', para12 ])
    # para13 = Paragraph('6' , tableBodyStyle)
    # para14= Paragraph('Sub Head' , tableBodyStyle)
    # para15 = Paragraph('F-2, Expenditure on other training activity' , tableBodyStyle)
    # bottomData.append([ para13, para14, '', para15 ])
    # para15 = Paragraph('7' , tableBodyStyle)
    # para16= Paragraph('Code Head' , tableBodyStyle)
    # para17 = Paragraph(str(poObj.codeHead), tableBodyStyle)
    # bottomData.append([ para15, para16, '', para17 ])
    # para18 = Paragraph('8' , tableBodyStyle)
    # para19 = Paragraph('Balance funds available , taking into account committed liabilities, before sanction of this case' , tableBodyStyle)
    # para20 = Paragraph('BALANCE OF UNIT FUND', tableBodyStyle)
    # bottomData.append([ para18, para19, '', para20 ])
    # para21 = Paragraph('9' , tableBodyStyle)
    # para22 = Paragraph('Name of paying Agency ' , tableBodyStyle)
    # para23 = Paragraph('PCDA Bangalore', tableBodyStyle)
    # bottomData.append([ para21, para22, '', para23 ])
    # para24 = Paragraph('10' , tableBodyStyle)
    # para25 = Paragraph('Whether being issued under inherent powers or with concurrence of IFA ' , tableBodyStyle)
    # para26 = Paragraph('issued under inherent', tableBodyStyle)
    # bottomData.append([ para24, para25, '', para26 ])
    # para27 = Paragraph('11' , tableBodyStyle)
    # para28 = Paragraph('U.O number allotted by IFA' , tableBodyStyle)
    # para29 = Paragraph('NA', tableBodyStyle)
    # bottomData.append([ para27, para28, '', para29 ])
    # para30 = Paragraph('12' , tableBodyStyle)
    # para31 = Paragraph("Communication of sanction being signed by the undersigned under power delegated by CFA to sign such financial documents vide CFAs letter number 0106/DGNCC/Bud2435/D(GS-VI/2001 dated 31 Oct 2001" , tableBodyStyle)
    # bottomData.append([ para30, para31, '', '' ])
    # tbottom=Table(bottomData , colWidths=(10*mm , 85*mm , 10*mm, 85*mm))
    # tsbottom = TableStyle([('ALIGN',(1,1),(-3,-3),'RIGHT'),
    #             ('VALIGN',(0,1),(-1,-3),'TOP'),
    #             ('VALIGN',(0,-2),(-1,-2),'TOP'),
    #             ('VALIGN',(0,-1),(-1,-1),'TOP'),
    #             ('SPAN',(-3,-1),(-1,-1)),
    #             # ('SPAN',(-3,-2),(-2,-2)),
    #             # ('SPAN',(-3,-3),(-2,-3)),
    #             # ('LINEABOVE',(-2,-2),(-1,-2),0.25,colors.gray),
    #             ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
    #             ('BOX', (0,0), (-1,-1), 0.25, colors.black),
    #         ])
    # tbottom.setStyle(tsbottom)
    # story.append(tbottom)
    # story.append(Spacer(2.5,0.75*cm))
    # otherDetail = """
    # <para >   File No: %s <br/> Date of issue : %s  </para>
    # """%(poObj.dated , poObj.fileNo )
    # otherDetail2 = """
    # <para align="right"> <br/><br/><br/><br/><br/><br/>Signature</para>
    # """
    # dataValbottom = [[Paragraph(otherDetail , styleN),Paragraph(otherDetail2 , styleN)]]
    # t3=Table(dataValbottom)
    # story.append(t3)

    pdf_doc.build(story)

def genVendor(response , vendor, request):
    MARGIN_SIZE = 8 * mm
    PAGE_SIZE = A4
    styles=getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']
    pdf_doc = SimpleDocTemplate(response, pagesize = PAGE_SIZE,
        leftMargin = MARGIN_SIZE, rightMargin = MARGIN_SIZE,
        topMargin = 4*MARGIN_SIZE, bottomMargin = 3*MARGIN_SIZE)

    tableHeaderStyle = styles['Normal'].clone('tableHeaderStyle')
    tableBodyStyle = styles['Normal'].clone('tableBodyStyle')
    tableBodyStyle.fontSize = 7
    tableTitle = styles['Normal'].clone('tableBodyStyle')
    tableTitle.fontSize = 14
    # tableHeaderStyle.textColor = colors.white;
    # tableHeaderStyle.fontSize = 7
    story = []
    summryParaId = """
    <para><strong>#%s</strong></para>
    """ %(vendor.pk )
    story.append(Paragraph(summryParaId , tableTitle))
    summryParaSrc = """
    <para  align="center"><strong><u>NCC Budget Managment System</u></strong></para>
    """
    story.append(Paragraph(summryParaSrc , styleN))
    story.append(Spacer(2.5,0.5*cm))
    from reportlab.platypus import Image
    imagePath = os.path.join(globalSettings.BASE_DIR , 'static_shared','images' , 'download.png')
    f = open(imagePath, 'rb')
    ima = Image(f)
    ima.drawHeight = 1.25*inch
    ima.drawWidth = 1.25*inch
    ima.hAlign = 'CENTER'
    # ima.mask='auto'
    story.append(ima)
    # logo = "download.png"
    # f = open(logo, 'rb')
    # im = Image(f)
    # Story.append(im)
    story.append(Spacer(2.5,0.5*cm))
    summryParaSrc5 = """
    <para align="center"><strong><u> %s</u></strong>
    """%(vendor.name)
    story.append(Paragraph(summryParaSrc5 , styleN))
    story.append(Spacer(2.5,0.5*cm))
    data = []
    gstTitle = Paragraph('<strong>GST</strong>' , tableHeaderStyle)
    gstDetails = Paragraph('{0}'.format(vendor.gst) , tableHeaderStyle)
    data.append([ gstTitle, gstDetails])
    panTitle = Paragraph('<strong>PAN Number</strong>' , tableHeaderStyle)
    panDetails = Paragraph('{0}'.format(vendor.panNumber) , tableHeaderStyle)
    data.append([ panTitle, panDetails])
    phoneTitle = Paragraph('<strong>Phone Number</strong>' , tableHeaderStyle)
    phoneDetails = Paragraph('{0}'.format(vendor.phone) , tableHeaderStyle)
    data.append([ phoneTitle, phoneDetails])
    emailTitle = Paragraph('<strong>Email</strong>' , tableHeaderStyle)
    emailDetails = Paragraph('{0}'.format(vendor.email) , tableHeaderStyle)
    data.append([ emailTitle, emailDetails])
    addressTitle = Paragraph('<strong>Address</strong>' , tableHeaderStyle)
    addressDetails = Paragraph('{0}'.format(vendor.address) , tableHeaderStyle)
    data.append([ addressTitle, addressDetails])
    properiterNameTitle = Paragraph('<strong>Proprietor Name</strong>' , tableHeaderStyle)
    properiterNameDetails = Paragraph('{0}'.format(vendor.properiterName) , tableHeaderStyle)
    data.append([ properiterNameTitle, properiterNameDetails])
    firmNoTitle = Paragraph('<strong>Firm Registration Number</strong>' , tableHeaderStyle)
    firmNoDetails = Paragraph('{0}'.format(vendor.firmNo) , tableHeaderStyle)
    data.append([ firmNoTitle, firmNoDetails])
    adharNoTitle = Paragraph('<strong>Adhar Number</strong>' , tableHeaderStyle)
    adharNoDetails = Paragraph('{0}'.format(vendor.adharNo) , tableHeaderStyle)
    data.append([ adharNoTitle, adharNoDetails])
    bankACnoTitle = Paragraph('<strong>Bank Ac Number </strong>' , tableHeaderStyle)
    bankACnoDetails = Paragraph('{0}'.format(vendor.bankACno) , tableHeaderStyle)
    data.append([ bankACnoTitle, bankACnoDetails])
    ifscTitle = Paragraph('<strong>IFSC </strong>' , tableHeaderStyle)
    ifscDetails = Paragraph('{0}'.format(vendor.ifsc) , tableHeaderStyle)
    data.append([ ifscTitle, ifscDetails])
    branchNameTitle = Paragraph('<strong>Bank Name </strong>' , tableHeaderStyle)
    branchNameDetails = Paragraph('{0}'.format(vendor.branchName) , tableHeaderStyle)
    data.append([ branchNameTitle, branchNameDetails])
    branchAddrTitle = Paragraph('<strong>Bank Address </strong>' , tableHeaderStyle)
    branchAddrDetails = Paragraph('{0}'.format(vendor.branchAddr) , tableHeaderStyle)
    data.append([ branchAddrTitle, branchAddrDetails])
    t=Table(data)
    ts = TableStyle([('ALIGN',(1,1),(-3,-3),'RIGHT'),
                ('VALIGN',(0,1),(-1,-3),'TOP'),
                ('VALIGN',(0,-2),(-1,-2),'TOP'),
                ('VALIGN',(0,-1),(-1,-1),'TOP'),
                # ('SPAN',(-3,-1),(-2,-1)),
                # ('SPAN',(-3,-2),(-2,-2)),
                # ('SPAN',(-3,-3),(-2,-3)),
                # ('LINEABOVE',(-2,-2),(-1,-2),0.25,colors.gray),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ])
    t.setStyle(ts)
    story.append(t)
    story.append(Spacer(2.5,0.5*cm))



    pdf_doc.build(story)


class DownloadContingent(APIView):
    renderer_classes = (JSONRenderer,)
    def get(self , request , format = None):
        if 'id' not in request.GET:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        response = HttpResponse(content_type='application/pdf')
        o = Contingent.objects.get(id = int(request.GET['id']))
        response['Content-Disposition'] = 'attachment; filename="contingent_%s.pdf'%( o.pk)
        genContigent(response , o , request)
        # f = open('./media_root/grf_%s.pdf'%( o.pk) , 'wb')
        # f.write(response.content)
        # f.close()
        return response


class vendorAPI(APIView):
    renderer_classes = (JSONRenderer,)
    def get(self , request , format = None):
        if 'id' not in request.GET:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        response = HttpResponse(content_type='application/pdf')
        o = Vendor.objects.get(id = int(request.GET['id']))
        response['Content-Disposition'] = 'attachment; filename="vendor_%s.pdf'%( o.pk)
        genVendor(response , o , request)
        # f = open('./media_root/grf_%s.pdf'%( o.pk) , 'wb')
        # f.write(response.content)
        # f.close()
        return response

class MembersViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated , )
    serializer_class = MembersSerializer
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['name']
    def get_queryset(self):
        return Members.objects.filter(unit = self.request.user)


def genallotment(response , poObj, request):


    MARGIN_SIZE = 8 * mm
    PAGE_SIZE = A4
    styles=getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading1']
    pdf_doc = SimpleDocTemplate(response, pagesize = PAGE_SIZE,
        leftMargin = MARGIN_SIZE, rightMargin = MARGIN_SIZE,
        topMargin = 4*MARGIN_SIZE, bottomMargin = 3*MARGIN_SIZE)

    tableHeaderStyle = styles['Normal'].clone('tableHeaderStyle')
    # tableHeaderStyle.textColor = colors.white;
    # tableHeaderStyle.fontSize = 7
    story = []

    summryParaSrc = """
    <para  align="center">
    <strong><u>ALLOCATION LETTER</u></strong></para>
    """
    story.append(Paragraph(summryParaSrc , styleN))
    story.append(Spacer(2.5,0.5*cm))


    pdf_doc.build(story)


class AllotmentLetter(APIView):
    renderer_classes = (JSONRenderer,)
    def get(self , request , format = None):
        if 'id' not in request.GET:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        response = HttpResponse(content_type='application/pdf')
        o = BudgetAllocation.objects.get(id = int(request.GET['id']))
        response['Content-Disposition'] = 'attachment; filename="grf_%s.pdf'%( o.pk)
        genallotment(response , o , request)
        # f = open('./media_root/grf_%s.pdf'%( o.pk) , 'wb')
        # f.write(response.content)
        # f.close()
        return response