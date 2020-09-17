
from django.contrib.auth.models import User , Group
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import *
from .models import *
from PIM.serializers import *
# from POS.models import Store

class userProfileLiteSerializer(serializers.ModelSerializer):
    # to be used in the typehead tag search input, only a small set of fields is responded to reduce the bandwidth requirements
    class Meta:
        model = profile
        fields = ( 'pk' , )

class userSearchSerializer(serializers.ModelSerializer):
    # to be used in the typehead tag search input, only a small set of fields is responded to reduce the bandwidth requirements
    profile = userProfileLiteSerializer(many=False , read_only=True)
    class Meta:
        model = User
        fields = ( 'pk', 'username' , 'first_name' , 'last_name' , 'profile'  ,'is_staff' , 'is_superuser' )



class userProfileSerializer(serializers.ModelSerializer):
    """ allow all the user """
    class Meta:
        model = profile
        fields = ( 'pk' , 'mobile' ,'address' )

class userProfileAdminModeSerializer(serializers.ModelSerializer):
    """ Only admin """
    class Meta:
        model = profile
        fields = ( 'pk','user' , 'mobile' ,'address' )


class userViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk' , 'username' , 'email' , 'first_name' , 'last_name' )


class userSerializer(serializers.ModelSerializer):
    profile = userProfileSerializer(many=False , read_only=True)
    # store = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('pk' , 'username' , 'email' , 'first_name' , 'last_name'  ,'profile'   , 'password' , 'is_active','is_staff' , 'last_login','is_superuser')
        # read_only_fields = ( 'profile' , 'settings' ,'is_staff' )
        # extra_kwargs = {'password': {'write_only': True} }
    def create(self , validated_data):
        raise PermissionDenied(detail=None)
    def update (self, instance, validated_data):
        user = self.context['request'].user
        if authenticate(username = user.username , password = self.context['request'].data['oldPassword']) is not None:
            user = User.objects.get(username = user.username)
            user.set_password(validated_data['password'])
            user.save()
        else :
            raise PermissionDenied(detail=None)
        return user
    # def get_store(self , obj):
    #     try:
    #         storeObj = Store.objects.get(owner__pk=obj.pk)
    #         store = storeObj.pk
    #     except:
    #         store = None
    #     return store

class userAdminSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url' , 'username' , 'email' , 'first_name' , 'last_name' , 'is_staff' ,'is_active', 'date_joined','pk' )
    def create(self , validated_data):
        print "In create"
        print  self.context['request'].user.is_superuser
        if not self.context['request'].user.is_superuser:
            raise PermissionDenied(detail=None)
        user = User.objects.create(**validated_data)
        password =  self.context['request'].data['password']
        user.set_password(password)
        user.save()
        p = user.profile
        p.mobile = self.context['request'].data['mobile']
        try:
            p.gstin = self.context['request'].data['gstin']
        except:
            pass
        try:
            p.companyName = self.context['request'].data['companyName']
        except:
            pass
        p.save()
        return user
    def update (self, instance, validated_data):
        user = self.context['request'].user
        if user.is_staff or user.is_superuser:
            u = User.objects.get(username = self.context['request'].data['username'])
            if (u.is_staff and user.is_superuser ) or user.is_superuser: # superuser can change password for everyone , staff can change for everyone but not fellow staffs
                if 'password' in self.context['request'].data:
                    u.set_password(self.context['request'].data['password'])
                u.first_name = validated_data['first_name']
                u.last_name = validated_data['last_name']
                if 'is_active' in validated_data:
                    u.is_active = validated_data['is_active']
                if 'is_staff' in validated_data:
                    u.is_active = validated_data['is_staff']

                p = u.profile
                p.mobile = self.context['request'].data['mobile']
                try:
                    p.gstin = self.context['request'].data['gstin']
                except:
                    pass
                try:
                    p.companyName = self.context['request'].data['companyName']
                except:
                    pass


                u.save()
            else:
                raise PermissionDenied(detail=None)
        try:
            return u
        except:
            raise PermissionDenied(detail=None)




class UserLiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk' , 'first_name' , 'last_name')
