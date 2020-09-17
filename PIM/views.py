from rest_framework import viewsets , permissions , serializers
from django.shortcuts import render
from url_filter.integrations.drf import DjangoFilterBackend
from .serializers import *
from API.permissions import *
from models import *
import json
from rest_framework.views import APIView
from django.conf import settings as globalSettings
import os
from os import path
from rest_framework.response import Response
import glob
# from PIL import Image
# from flask import Flask, request, redirect, url_for
# from werkzeug.utils import secure_filename
import urllib
# import matplotlib.pyplot as plt
from ERP.models import service


class settingsViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, isOwner, )
    queryset = settings.objects.all()
    serializer_class = settingsSerializer

class themeViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, )
    queryset = theme.objects.all()
    serializer_class = themeSerializer



class notificationViewSet(viewsets.ModelViewSet):
    permission_classes = (isOwner, )
    serializer_class = notificationSerializer
    def get_queryset(self):
        return notification.objects.filter(user = self.request.user , read = False).order_by('-created')



class ImageFetchApi(APIView):
    permission_classes = (permissions.AllowAny ,)
    def get(self, request , format = None):
        img=''
        images =[]
        if request.GET['value'] == 'static':
            for img in glob.glob(os.path.join( globalSettings.BASE_DIR,  'static_shared','images' , '*')):
                # n= cv2.imread(img)
                link = '/static/images/'
                name = img.split('static_shared/images/')[1]
                image = link+name
                images.append(image)
        else:
            for media in glob.glob(os.path.join(  globalSettings.BASE_DIR, 'media_root','ecommerce','pictureUploads' , '*')):
                link = '/media/ecommerce/pictureUploads/'
                name = media.split('media_root/ecommerce/pictureUploads/')[1]
                image = link+name
                images.append(image)
        return Response(images, status = status.HTTP_200_OK)
    def post(self, request, format=None):
        print 'fffffffffffffffffffffff',request.POST
        if 'rename' in request.POST:
            if 'pictureUploads' in request.POST['path']:
                print 'picture uploadsss'
                path = os.path.join(globalSettings.BASE_DIR, 'media_root','ecommerce','pictureUploads')
            else:
                print 'staticccc'
                path = os.path.join(globalSettings.BASE_DIR, 'static_shared','images')
            old_file = os.path.join(path, request.POST['oldName'])
            new_file = os.path.join(path, request.POST['newName'])
            os.rename(old_file, new_file)
        if 'static' in request.POST:
            file =request.POST['file']
            filename = file.name
            filepath = os.path.join(globalSettings.BASE_DIR,'static_shared','images' , file.name)
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.path.join(BASE_DIR , filepath)
        if 'media' in request.POST:
            file =request.POST['file']
            filename = file.name
            filepath = os.path.join(globalSettings.BASE_DIR,'media_root','ecommerce','pictureUploads' , file.name)
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            os.path.join(BASE_DIR , filepath)
        return Response(status = status.HTTP_200_OK)
    def delete(self, request, format=None):
        if request.GET['value'] == 'static':
            image = request.GET['mediaName']
            image = image.split('static/images/')[1]
            img = os.path.join(globalSettings.BASE_DIR,'static_shared','images' , image)
            if os.path.exists(img):
              os.remove(img)
            else:
              print("The file does not exist")
        elif request.GET['value'] == 'media':
            image = request.GET['mediaName']
            image = image.split('/media/ecommerce/pictureUploads/')[1]
            img = os.path.join(globalSettings.BASE_DIR,'media_root','ecommerce','pictureUploads' , image)
            if os.path.exists(img):
              os.remove(img)
            else:
              print("The file does not exist")
        return Response(status = status.HTTP_200_OK)
