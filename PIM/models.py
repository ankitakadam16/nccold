from django.db import models
from django.contrib.auth.models import User
from ERP.models import service
from time import time
# from ecommerce.models import listing

# Create your models here.
def getThemeImageUploadPath(instance , filename ):
    return 'PIM/images/theme/%s_%s_%s' % (str(time()).replace('.', '_'), instance.user.username, filename)

PRESENCE_CHOICES = (
    ('NA' , 'NA'),
    ('Available' , 'Available'),
    ('Busy' , 'Busy'),
    ('Away' , 'Away'),
    ('On Leave' ,'On Leave'),
    ('In A Meeting' ,'In a meeting'),
)
class settings(models.Model):
    presence = models.CharField(max_length = 15 , choices = PRESENCE_CHOICES , null = False , default = 'NA')
    user = models.OneToOneField(User)

class theme(models.Model):
    main = models.CharField(max_length=10 , null = True)
    highlight = models.CharField(max_length=10 , null = True)
    background = models.CharField(max_length=10 , null = True)
    backgroundImg = models.ImageField(upload_to = getThemeImageUploadPath , null = True)
    parent = models.OneToOneField(settings , related_name = 'theme')

User.settings = property(lambda u : settings.objects.get_or_create(user = u)[0])
settings.theme = property(lambda s : theme.objects.get_or_create(parent = s)[0])

DOMAIN_CHOICES = (
    ('System' , 'System'),
    ('Administration' , 'Administration'),
    ('Application' , 'Application')
)

class notification(models.Model):
    message = models.TextField(max_length = 300 , null=True)
    link = models.URLField(max_length = 100 , null = True)
    shortInfo = models.CharField(max_length = 250 , null = True)
    read = models.BooleanField(default = False)
    user = models.ForeignKey(User)
    domain = models.CharField(null = False , default = 'SYS' , choices = DOMAIN_CHOICES , max_length = 3)
    originator = models.CharField(null = True , max_length = 20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    onHold = models.BooleanField(default = False)

def getChatMessageAttachment(instance , filename ):
    return 'chat/%s_%s' % (str(time()).replace('.', '_'), filename)

def getClientRelationshipContactDP(instance , filename ):
    return 'PIM/dp/%s_%s_%s' % (str(time()).replace('.', '_'), instance.user.username, filename)
