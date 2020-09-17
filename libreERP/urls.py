from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings as globalSettings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from homepage.views import index
# from events.views import eventHome
from HR.views import loginView , logoutView , home , registerView , tokenAuthentication , root, generateOTP, documentView, socialMobileView, tokenView,mobileloginView
from homepage.views import setupstore, registration
# from ecommerce.views import *
from ERP.views import *
# from POS.views import *
# from ecommerce.views import renderedStatic, categoryView, productView

app_name="libreERP"
urlpatterns = [
    url(r'^$', index , name ='root'),
    url(r"^ecommerce/", index , name = 'ecommerce'), # public  ecommerce app
    url(r'^admin/', home , name ='ERP'),
    url(r'^api/', include('API.urls')),
    url(r'^django/', include(admin.site.urls)),
    url(r'^login', loginView , name ='login'),
    url(r'^mobilelogin', mobileloginView , name ='mobilelogin'),
    url(r'^t', tokenView , name ='t'),
    url(r'^register', registration , name ='register'),
    url(r'^vendor-registeration', registration , name ='vendorregistration'),
    url(r'^services', serviceRegistration , name ='serviceRegistration'),
    url(r'^token', tokenAuthentication , name ='tokenAuthentication'),
    url(r'^logout', logoutView , name ='logout'),
    url(r'^api-auth/', include('rest_framework.urls', namespace ='rest_framework')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^robots\.txt', include('robots.urls')),
    url(r'^generateOTP', generateOTP, name="generateOTP"),
    url(r'^documents', documentView , name ='document'),
    url(r'^socialMobileLogin/$', socialMobileView , name ='socialMobileLogin'),
]

if globalSettings.DEBUG:
    urlpatterns +=static(globalSettings.STATIC_URL , document_root = globalSettings.STATIC_ROOT)
    urlpatterns +=static(globalSettings.MEDIA_URL , document_root = globalSettings.MEDIA_ROOT)

urlpatterns.append(url(r'^', index , name ='index'))
