from __future__ import unicode_literals
from django.contrib.auth.models import User, Group
from time import time
from django.db import models

# Create your models here.

def getERPPictureUploadPath(instance , filename ):
    return 'ERP/pictureUploads/%s_%s_%s' % (str(time()).replace('.', '_'), instance.user.username, filename)


class device(models.Model):
    sshKey = models.CharField(max_length = 500 , null = True)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length = 50)

class profile(models.Model):
    user = models.ForeignKey(User , null =False , related_name='gitProfile')
    devices = models.ManyToManyField(device)

class module(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    name = models.CharField(max_length = 50 , null = False , unique = True)
    description = models.CharField(max_length = 500 , null = False)
    icon = models.CharField(max_length = 20 , null = True )
    haveCss = models.BooleanField(default = True)
    haveJs = models.BooleanField(default = True)

class application(models.Model):
    # each application in a module will have an instance of this model
    created = models.DateTimeField(auto_now_add = True)
    name = models.CharField(max_length = 50 , null = False , unique = True)
    owners = models.ManyToManyField(User , related_name = 'appsManaging' , blank = True)
    icon = models.CharField(max_length = 20 , null = True )
    haveCss = models.BooleanField(default = True)
    haveJs = models.BooleanField(default = True)
    inMenu = models.BooleanField(default = True)
    # only selected users can assign access to the application to other user
    module = models.ForeignKey(module , related_name = "apps" , null=True)
    description = models.CharField(max_length = 500 , null = False)
    canConfigure = models.ForeignKey("self" , null = True, related_name="canBeConfigureFrom")
    def __unicode__(self):
        return self.name

class appSettingsField(models.Model):
    FIELD_TYPE_CHOICES = (
        ('flag' , 'flag'),
        ('value' , 'value')
    )
    created = models.DateTimeField(auto_now_add = True)
    name = models.CharField(max_length = 50 , null = False )
    flag = models.BooleanField(default = False)
    value = models.CharField(max_length = 5000 , null = True)
    description = models.CharField(max_length = 500 , null = False)
    app = models.ForeignKey(application , related_name='settings' , null = True)
    fieldType = models.CharField(choices = FIELD_TYPE_CHOICES , default = 'flag' , null = False , max_length = 5)
    def __unicode__(self):
        return self.name
    class Meta:
        unique_together = ('name', 'app',)

class PublicApiKeys(models.Model):
    active = models.BooleanField(default = False)
    user = models.ForeignKey(User , related_name='publicApiKeysOwned') # the user who is authorized to use this api
    key = models.CharField(max_length = 30 , null = False)
    created = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(User , related_name = 'apiKeyAdministrator') # who kind of created it and can toggle active flag
    usageRemaining = models.PositiveIntegerField(default=0) # balance remaining
    app = models.ForeignKey(application , null = False)

class ApiUsage(models.Model): # to store the monthly api usage for the api
    api = models.ForeignKey(PublicApiKeys, related_name= 'usages')
    count = models.PositiveIntegerField(default=0)
    month = models.PositiveIntegerField(default=0) # assuming 0 for the month of January 2017 and 1 for february and so on

class permission(models.Model):
    app = models.ForeignKey(application , null=False , related_name="permissions")
    user = models.ForeignKey(User , related_name = "accessibleApps" , null=False)
    givenBy = models.ForeignKey(User , related_name = "approvedAccess" , null=False)
    created = models.DateTimeField(auto_now_add = True)
    def __unicode__(self):
        return self.app.name

class groupPermission(models.Model):
    app = models.ForeignKey(application , null=False)
    group = models.ForeignKey(Group , related_name = "accessibleApps" , null=False)
    givenBy = models.ForeignKey(User , related_name = "approvedGroupAccess" , null=False)
    created = models.DateTimeField(auto_now_add = True)
    def __unicode__(self):
        return self.app

MEDIA_TYPE_CHOICES = (
    ('onlineVideo' , 'onlineVideo'),
    ('video' , 'video'),
    ('image' , 'image'),
    ('onlineImage' , 'onlineImage'),
    ('doc' , 'doc'),
)

class media(models.Model):
    user = models.ForeignKey(User , related_name = 'serviceDocsUploaded' , null = False)
    created = models.DateTimeField(auto_now_add = True)
    link = models.TextField(null = True , max_length = 300) # can be youtube link or an image link
    attachment = models.FileField(upload_to = getERPPictureUploadPath , null = True ) # can be image , video or document
    mediaType = models.CharField(choices = MEDIA_TYPE_CHOICES , max_length = 10 , default = 'image')

class address(models.Model):
    street = models.CharField(max_length=300 , null = True)
    city = models.CharField(max_length=100 , null = True)
    state = models.CharField(max_length=50 , null = True)
    pincode = models.PositiveIntegerField(null = True)
    lat = models.CharField(max_length=15 ,null = True)
    lon = models.CharField(max_length=15 ,null = True)
    country = models.CharField(max_length = 50 , null = True)

    def __unicode__(self):
        return '< street :%s>,<city :%s>,<state :%s>' %(self.street ,self.city, self.state)

class service(models.Model): # contains other companies datails
    created = models.DateTimeField(auto_now_add = True)
    name = models.CharField(max_length = 100 , null = False, unique = True)
    user = models.ForeignKey(User , related_name = 'servicesCreated' , null = False) # the responsible person for this service
    address = models.ForeignKey(address , null = True )
    mobile = models.CharField(max_length = 20 , null = True)
    telephone = models.CharField(max_length = 20 , null = True)
    about = models.TextField(max_length = 2000 , null = True)
    cin = models.CharField(max_length = 100 , null = True) # company identification number
    tin = models.CharField(max_length = 100 , null = True) # tax identification number
    logo = models.CharField(max_length = 200 , null = True) # image/svg link to the logo
    web = models.TextField(max_length = 100 , null = True) # image/svg link to the logo
    doc  = models.ForeignKey(media , related_name = 'services' , null = True)
    contactPerson = models.ForeignKey(User , related_name = 'servicesContactPerson' , null = True)

    def __unicode__(self):
        return '< name :%s>,<user :%s>,<address :%s>' %(self.name ,self.user.username, self.address)

class Vendor(models.Model):
    name = models.CharField(max_length = 100 , null = False)
    address = models.TextField(max_length = 500 , null = False)
    pincode = models.PositiveIntegerField(default=0)
    gst = models.CharField(max_length = 15 , null = False , unique = True)
    bankACno = models.CharField(max_length = 100 , null = True)
    ifsc = models.CharField(max_length = 100 , null = False)
    properiterName = models.CharField(max_length = 100 , null = False)
    panNumber = models.CharField(max_length = 100 , null = False , unique = True)
    created = models.DateTimeField(auto_now_add = True)
    user = models.ForeignKey(User , related_name = 'vendorUser', null = True)
    phone =models.CharField(max_length = 100 , null = True)
    city = models.CharField(max_length = 100 , null = True)
    state = models.CharField(max_length = 100 , null = True)
    adharNo = models.CharField(max_length = 12 , null = True)
    firmNo =  models.CharField(max_length = 50 , null = True)
    branchName =  models.CharField(max_length = 200 , null = False)
    branchAddr =  models.CharField(max_length = 500 , null = False)
    email =  models.CharField(max_length = 50 , null = True)

class PoOrder(models.Model):
    vendor = models.ForeignKey(Vendor, related_name = 'vendorName', null = True)
    subject = models.TextField(max_length = 200 , null = True)
    total = models.FloatField(default=0.0)
    created = models.DateTimeField(auto_now_add = True)
    user = models.ForeignKey(User , related_name = 'poUser', null = True)
    unitAddress = models.TextField(max_length = 500 , null = True)
    deliveryAddress = models.TextField(max_length = 500 , null = True)
    dated = models.DateField(null = True)
    gfrRule = models.CharField(max_length = 200 , null = True)
    sanctionAutority = models.CharField(max_length = 200 , null = True)
    sanctionNo = models.CharField(max_length = 200 , null = True)
    sanctionDate = models.DateField(null = True)
    codeHead = models.CharField(max_length = 100 , null = True)
    minorHead = models.CharField(max_length = 100 , null = True)
    majorHead = models.CharField(max_length = 100 , null = True)
    supplyOrderNo =  models.CharField(max_length = 100 , null = True, blank = True)
    supplyOrderDate = models.DateField(null = True)
    workOrderNo =  models.CharField(max_length = 100 , null = True, blank = True)
    workOrderDate = models.DateField(null = True)
    is_application = models.BooleanField(default = False)
    is_csd = models.BooleanField(default = False)
    vendorName = models.CharField(max_length = 100 , null = True)
    vendorAddress = models.TextField(max_length = 500 , null = True)
    is_sanctioned = models.BooleanField(default = False)
    member1_name = models.CharField(max_length = 100 , null = True)
    member1_no = models.CharField(max_length = 100 , null = True)
    member1_pos = models.CharField(max_length = 100 , null = True)
    member2_name = models.CharField(max_length = 100 , null = True)
    member2_no = models.CharField(max_length = 100 , null = True)
    member2_pos = models.CharField(max_length = 100 , null = True)
    member3_name = models.CharField(max_length = 100 , null = True)
    member3_no = models.CharField(max_length = 100 , null = True)
    member3_pos = models.CharField(max_length = 100 , null = True)
    fileNo = models.CharField(max_length = 100 , null = True)
    quoteNo = models.CharField(max_length = 100 , null = True)
    quoteDate = models.DateField(null = True)
    gstVal =  models.FloatField(default=0.0)

class PoItems(models.Model):
    po = models.ForeignKey(PoOrder, related_name = 'poName', null = True)
    name = models.CharField(max_length = 100, null = False)
    denominator = models.CharField(max_length = 200 , null = True)
    quantity = models.PositiveIntegerField(default=0)
    rate = models.FloatField(default=0.0)
    amount = models.FloatField(default=0.0)
    gst = models.FloatField(default=0.0)
    total = models.FloatField(default=0.0)
    gstAmount = models.FloatField(default=0.0)
    grandTotal = models.FloatField(default=0.0)

class BudgetAllocation(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    codeHead = models.CharField(max_length = 100 , null = False)
    name = models.CharField(max_length = 500 , null = False)
    unit =  models.ForeignKey(User, related_name = 'unitUser', null = True)
    allotmentAmount = models.FloatField(default=0.0)
    withdrawalAmount = models.FloatField(default=0.0)
    balance = models.FloatField(default=0.0)
    parent =  models.ForeignKey('self', related_name = 'budget_parent', null = True)
    allotedBy =  models.ForeignKey(User, related_name = 'alloterUser', null = True)
    dated = models.DateField(null = True)
    cont_no = models.CharField(max_length = 500 , null = True)
    sanctioned_no = models.CharField(max_length = 500 , null = True)
    description =  models.CharField(max_length = 5000 , null = True)
    minorHead = models.CharField(max_length = 500 , null = True)
    is_withdrawn = models.BooleanField(default = False)
    allotment_no =  models.CharField(max_length = 500 , null = True)

class Members(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    name = models.CharField(max_length = 500 , null = False)
    rank = models.CharField(max_length = 200 , null = False)
    serviceNo = models.CharField(max_length = 100 , null = False)
    typ = models.CharField(max_length = 100 , null = False)
    unit = models.ForeignKey(User , related_name = 'memberUser', null = True)

class Contingent(models.Model):
    created = models.DateTimeField(auto_now_add = True)
    invoiceNo = models.CharField(max_length = 100 , null = True)
    invoiceDate = models.DateField(null = True)
    postingDate = models.DateField(null = True)
    amount = models.FloatField(default=0.0)
    subject = models.CharField(max_length = 100 , null = True)
    unitFileNo = models.CharField(max_length = 100 , null = True)
    crvNo = models.CharField(max_length = 100 , null = True)
    crvDate = models.DateField(null = True)
    accntLedger = models.CharField(max_length = 500 , null = True)
    po = models.ForeignKey(PoOrder, related_name = 'poContingent', null = True)
    unit = models.ForeignKey(User , related_name = 'contingentUnit', null = True)
