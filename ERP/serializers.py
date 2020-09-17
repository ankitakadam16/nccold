from django.contrib.auth.models import User , Group
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.exceptions import *
from .models import *
from PIM.serializers import *
from HR.models import profile
# from HR.serializers import userSearchSerializer
from rest_framework.response import Response
# from fabric.api import *
import os
from django.conf import settings as globalSettings
from django.db.models import Sum, Count

class userProfileLiteSerializer(serializers.ModelSerializer):
    # to be used in the typehead tag search input, only a small set of fields is responded to reduce the bandwidth requirements
    class Meta:
        model = profile
        fields = ( 'rank',)

class userSearchSerializer(serializers.ModelSerializer):
    profile = userProfileLiteSerializer(many = False , read_only = True)
    class Meta:
        model = User
        fields = ( 'pk', 'username' , 'first_name' , 'last_name'  , 'profile' , 'is_superuser')

class addressSerializer(serializers.ModelSerializer):
    class Meta:
        model = address
        fields = ('pk' , 'street' , 'city' , 'state' , 'pincode', 'lat' , 'lon', 'country')

class serviceSerializer(serializers.ModelSerializer):
    # user = userSearchSerializer(many = False , read_only = True)
    address = addressSerializer(many = False, read_only = True)
    contactPerson = userSearchSerializer(many = False , read_only = True)
    class Meta:
        model = service
        fields = ('pk' , 'created' ,'name' , 'user' , 'cin' , 'tin' , 'address' , 'mobile' , 'telephone' , 'logo' , 'about', 'doc', 'web' ,'contactPerson')

    def assignValues(self , instance , validated_data):
        if 'cin' in validated_data:
            instance.cin = validated_data['cin']
        if 'tin' in validated_data:
            instance.tin = validated_data['tin']
        if 'mobile' in validated_data:
            instance.mobile = validated_data['mobile']
        if 'telephone' in validated_data:
            instance.telephone = validated_data['telephone']
        if 'logo' in validated_data:
            instance.logo = validated_data['logo']
        if 'about' in validated_data:
            instance.about = validated_data['about']
        if 'doc' in validated_data:
            instance.doc = validated_data['doc']
        if 'web' in validated_data:
            instance.web = validated_data['web']
        if 'address' in self.context['request'].data and self.context['request'].data['address'] is not None:
            instance.address_id = int(self.context['request'].data['address'])
        if 'contactPerson' in self.context['request'].data and self.context['request'].data['contactPerson'] is not None:
            instance.contactPerson_id = int(self.context['request'].data['contactPerson'])
        instance.save()

    def create(self , validated_data):
        s = service(name = validated_data['name'] , user =validated_data['user'])
        self.assignValues(s, validated_data)
        return s
    def update(self , instance , validated_data):
        self.assignValues(instance , validated_data)
        return instance

class serviceLiteSerializer(serializers.ModelSerializer):
    address = addressSerializer(many = False, read_only = True)
    class Meta:
        model = service
        fields = ('pk'  ,'name' , 'address' , 'mobile' )

class deviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = device
        fields = ('pk', 'sshKey' , 'created' , 'name')

class profileSerializer(serializers.ModelSerializer):
    devices = deviceSerializer(many = True , read_only = True)
    class Meta:
        model = profile
        fields = ('pk', 'user' , 'devices')

class moduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = module
        fields = ( 'pk', 'name' , 'icon' , 'haveJs' , 'haveCss')

class applicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = application
        fields = ( 'pk', 'name', 'module' , 'description' , 'icon', 'canConfigure'  ,  'haveJs' , 'haveCss' , 'inMenu')

class applicationSettingsSerializer(serializers.ModelSerializer):
    # non admin mode
    class Meta:
        model = appSettingsField
        fields = ( 'pk', 'name', 'flag' , 'value' , 'fieldType')

class applicationAdminSerializer(serializers.ModelSerializer):
    module = moduleSerializer(read_only = True , many = False)
    owners = userSearchSerializer(read_only = True , many = True)
    class Meta:
        model = application
        fields = ( 'pk', 'name', 'module' , 'owners' , 'description' , 'created' , 'icon', 'canConfigure', 'haveJs' , 'haveCss' , 'inMenu')
    def create(self , validated_data):
        app =  application(**validated_data)
        app.module = module.objects.get(pk = self.context['request'].data['module']);
        # create the folder too as well as the folowing structure
        # app
        #     ---static
        #         -----js
        #         -----css
        #         -----ngTemplates
        parts = app.name.split('.')
        appName = parts[1]
        if len(parts)>=3:
            app.save()
            return app
        app.save()
        if len(app.name.split('.'))==2:
            with lcd(globalSettings.BASE_DIR):
                cmd = 'python manage.py startapp %s' %(appName)
                local(cmd)

        # adding the new app definition in the settings.py and creating the folders and files
        fileName = os.path.join(globalSettings.BASE_DIR , 'libreERP' , 'settings.py') # filepath for settings.py
        f = open(fileName , 'r')
        search = False
        lines = f.readlines()
        for l in lines:
            if l.find('INSTALLED_APPS') != -1:
                search = True
            if search:
                if l.find(')') != -1:
                    index = lines.index(l)
                    break
        lines.insert(index , ("\t'%s',# %s\n" %(appName , app.description)))
        f = open(fileName, "w")
        f.writelines(lines)
        f.close()
        os.makedirs(os.path.join(globalSettings.BASE_DIR ,appName,'static'))
        os.makedirs(os.path.join(globalSettings.BASE_DIR ,appName,'static', 'js'))
        os.makedirs(os.path.join(globalSettings.BASE_DIR ,appName,'static', 'css'))
        os.makedirs(os.path.join(globalSettings.BASE_DIR ,appName,'static', 'ngTemplates'))
        if app.haveJs:
            # create a JS file
            jsPath = os.path.join(globalSettings.BASE_DIR ,appName,'static', 'js' , ('%s.js' %(app.name)))
            f = open(jsPath, 'w')
            f.write('// you need to first configure the states for this app')
            f.close()
        if app.haveCss:
            #create a css file too
            jsPath = os.path.join(globalSettings.BASE_DIR ,appName,'static', 'css' , ('%s.css' %(app.name)))
            f = open(jsPath, 'w')
            f.write('/*here you can place all your app specific css class*/')
            f.close()
        app.save()
        return app

    def update (self, instance, validated_data):
        instance.owners.clear()
        for pk in self.context['request'].data['owners']:
            instance.owners.add(User.objects.get(pk = pk))
        instance.save()
        return instance

class applicationSettingsAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = appSettingsField
        fields = ( 'pk', 'name', 'flag' , 'value' , 'description' , 'created' , 'app', 'fieldType')
    def create(self , validated_data):
        s = appSettingsField()
        s.name = validated_data.pop('name')
        s.flag = validated_data.pop('flag')
        if 'value' in self.context['request'].data:
            s.value = self.context['request'].data['value']
        s.description = validated_data.pop('description')
        s.fieldType = validated_data.pop('fieldType')
        if s.fieldType == 'flag':
            s.value = ""
        s.app = validated_data.pop('app')
        s.save()
        return s
    def update(self ,instance, validated_data):
        for key in ['name', 'flag' , 'value' , 'description' , 'created' , 'app', 'fieldType']:
            try:
                setattr(instance , key , validated_data[key])
            except:
                pass
        instance.save()
        return instance

class permissionSerializer(serializers.ModelSerializer):
    app = applicationSerializer(read_only = True, many = False)
    class Meta:
        model = permission
        fields = ( 'pk' , 'app' , 'user' )
    def create(self , validated_data):
        user = self.context['request'].user
        if not user.is_superuser and user not in app.owners.all():
            raise PermissionDenied(detail=None)
        u = validated_data['user']
        permission.objects.filter(user = u).all().delete()
        for a in self.context['request'].data['apps']:
            app = application.objects.get(pk = a)
            p = permission.objects.create(app =  app, user = u , givenBy = user)
        return p

class groupPermissionSerializer(serializers.ModelSerializer):
    app = applicationSerializer(read_only = True, many = False)
    class Meta:
        model = groupPermission
        fields = ( 'pk' , 'app' , 'group' )

class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ('pk' , 'name', 'address' , 'pincode' , 'gst', 'bankACno' , 'ifsc', 'properiterName', 'panNumber', 'created', 'user', 'phone', 'city', 'state' , 'adharNo' , 'firmNo' , 'branchName' , 'branchAddr' , 'email')
    def create(self , validated_data):
        v = Vendor(**validated_data)
        v.user = self.context['request'].user
        v.save()
        return v
    def update(self , instance , validated_data):
        for key in ['name', 'address' , 'pincode' , 'gst', 'bankACno' , 'ifsc', 'properiterName', 'panNumber', 'created', 'user', 'phone', 'city', 'state' , 'adharNo' , 'firmNo' , 'branchName' , 'branchAddr' , 'email']:
            try:
                setattr(instance , key , validated_data[key])
            except:
                pass
        instance.save()
        return instance


class PoOrderSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True, many=False)
    class Meta:
        model = PoOrder
        fields = ('pk' , 'vendor', 'fileNo', 'subject' , 'total', 'unitAddress' , 'deliveryAddress' , 'dated' , 'gfrRule' , 'sanctionAutority' , 'sanctionNo' , 'sanctionDate' , 'codeHead' , 'minorHead' , 'supplyOrderNo' , 'supplyOrderDate' , 'is_application' , 'is_csd' , 'vendorName' , 'vendorAddress'  , 'is_sanctioned' , 'member1_name' , 'member1_no' , 'member1_pos' , 'member2_name' , 'member2_no' , 'member2_pos' , 'member3_name' , 'member3_no' , 'member3_pos','quoteNo' , 'quoteDate' ,'gstVal','workOrderDate','workOrderNo','majorHead')
    def create(self , validated_data):
        v = PoOrder(**validated_data)
        v.user = self.context['request'].user
        if 'vendor' in self.context['request'].data:
            v.vendor = Vendor.objects.get(pk=self.context['request'].data['vendor'])
        memberObj = Members.objects.filter(unit = self.context['request'].user)
        print
        presObj = memberObj.filter(typ = 'President').first()
        members = memberObj.filter(typ = 'Member')
        v.member3_name = presObj.name
        v.member3_no = presObj.serviceNo
        v.member3_pos = presObj.rank
        v.member1_name = members[0].name
        v.member1_no = members[0].serviceNo
        v.member1_pos = members[0].rank
        v.member2_name = members[1].name
        v.member2_no = members[1].serviceNo
        v.member2_pos = members[1].rank
        v.save()
        return v
    def update(self , instance , validated_data):
        for key in [ 'subject' , 'fileNo','total', 'unitAddress' , 'deliveryAddress' , 'dated' , 'gfrRule' , 'sanctionAutority' , 'sanctionNo' , 'sanctionDate' , 'codeHead' , 'minorHead' , 'supplyOrderNo' , 'supplyOrderDate' , 'is_application' , 'is_csd' , 'vendorName' , 'vendorAddress' , 'is_sanctioned'  , 'member1_name' , 'member1_no' , 'member1_pos' , 'member2_name' , 'member2_no' , 'member2_pos' , 'member3_name' , 'member3_no' , 'member3_pos','quoteNo' , 'quoteDate' , 'gstVal','workOrderDate','workOrderNo','majorHead']:
            try:
                setattr(instance , key , validated_data[key])
            except:
                pass
        if 'vendor' in self.context['request'].data:
            instance.vendor = Vendor.objects.get(pk=self.context['request'].data['vendor'])
        instance.save()
        return instance


class PoItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoItems
        fields = ('pk', 'po', 'name', 'denominator', 'quantity', 'rate', 'amount', 'gst', 'gstAmount', 'grandTotal')

class PoOrderAllSerializer(serializers.ModelSerializer):
    vendor = VendorSerializer(read_only=True, many=False)
    poItems = serializers.SerializerMethodField()
    user = userSearchSerializer(read_only=True, many=False)
    poTotal = serializers.SerializerMethodField()
    class Meta:
        model = PoOrder
        fields = ('pk' , 'vendor', 'user', 'fileNo', 'subject' , 'total', 'unitAddress' , 'deliveryAddress' , 'dated' , 'gfrRule' , 'sanctionAutority' , 'sanctionNo' , 'sanctionDate' , 'codeHead' , 'minorHead' , 'poItems', 'is_application' , 'is_csd' , 'vendorName' , 'vendorAddress' , 'is_sanctioned'  , 'member1_name' , 'member1_no' , 'member1_pos' , 'member2_name' , 'member2_no' , 'member2_pos' , 'member3_name' , 'member3_no' , 'member3_pos' ,'quoteNo' , 'quoteDate' ,'poTotal' , 'gstVal','majorHead' , 'workOrderNo' , 'workOrderDate' , 'supplyOrderNo' , 'supplyOrderDate')
    def get_poItems(self , obj):
        allData = []
        allData = obj.poName.all()
        return PoItemsSerializer(allData , many = True).data
    def get_poTotal(self , obj):
        total = 0
        total_sum = obj.poName.all().aggregate(tot = Sum('grandTotal'))
        if total_sum['tot'] != None:
            total = total_sum['tot']
        return total

class BudgetAllocationSerializer(serializers.ModelSerializer):
    unit = userSearchSerializer(many = False , read_only = True)
    class Meta:
        model = BudgetAllocation
        fields = ('pk', 'created', 'codeHead', 'minorHead', 'unit', 'allotmentAmount', 'withdrawalAmount', 'balance','allotment_no' , 'parent' , 'allotedBy' , 'name' , 'dated' ,'cont_no' ,'sanctioned_no' , 'description' , 'is_withdrawn')
    def create(self , validated_data):
        a = BudgetAllocation(**validated_data)
        a.allotedBy = self.context['request'].user
        if 'unit' in  self.context['request'].data:
            a.unit = User.objects.get(pk = int( self.context['request'].data['unit']))
        a.save()
        if 'parent' in  self.context['request'].data:
            parentObj = BudgetAllocation.objects.get(pk = int(self.context['request'].data['parent']))
            a.parent = parentObj
            parentObj.withdrawalAmount = parentObj.withdrawalAmount + float(self.context['request'].data['allotmentAmount'])
            parentObj.balance = parentObj.balance - float(self.context['request'].data['allotmentAmount'])
            parentObj.save()
        a.save()
        return a


class MembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Members
        fields = ('pk', 'created', 'name', 'rank', 'serviceNo', 'typ', 'unit')


class ContingentSerializer(serializers.ModelSerializer):
    po =  PoOrderAllSerializer(many = False , read_only = True)
    class Meta:
        model = Contingent
        fields = ('pk', 'created', 'invoiceNo', 'invoiceDate', 'postingDate', 'amount', 'subject' , 'unitFileNo' , 'crvNo' , 'crvDate' , 'accntLedger' , 'po' , 'unit')
    def create(self , validated_data):
        v = Contingent(**validated_data)
        if 'po' in self.context['request'].data:
            v.po = PoOrder.objects.get( pk = int(self.context['request'].data['po']))
        v.unit = self.context['request'].user
        v.save()
        return v
    def update(self , instance , validated_data):
        for key in [ 'invoiceNo', 'invoiceDate', 'postingDate', 'amount', 'subject' , 'unitFileNo' , 'crvNo' , 'crvDate' , 'accntLedger' , 'unit']:
            try:
                setattr(instance , key , validated_data[key])
            except:
                pass
        if 'po' in self.context['request'].data:
            instance.po = PoOrder.objects.get(pk=self.context['request'].data['po'])
        instance.save()
        return instance
