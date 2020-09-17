app.config(function($stateProvider){

  $stateProvider
  .state('businessManagement.allVendor', {
    url: "/allVendor",
    templateUrl: '/static/ngTemplates/app.vendor.html',
    controller: 'businessManagement.vendor',
  })
  $stateProvider
  .state('businessManagement.vendor', {
    url: "/vendor",
    templateUrl: '/static/ngTemplates/app.newVendor.form.html',
    controller: 'businessManagement.vendor.form',
  })
  .state('businessManagement.editVendor', {
    url: "/editVendor/:id",
    templateUrl: '/static/ngTemplates/app.newVendor.form.html',
    controller: 'businessManagement.vendor.form',
  })
});

app.controller("businessManagement.vendor", function($scope, $state, $users, $stateParams, $http, Flash, $uibModal, $rootScope, $aside) {

  $scope.viewVendors = function () {
    var url = '/api/ERP/vendor/?limit='+$scope.limit+'&offset='+$scope.offset
    if ($scope.search.searchText.length > 0) {
      url = url+'&search='+$scope.search.searchText
    }
    $http({
      method : 'GET',
      url : url,
    }).
    then(function(response) {
      $scope.vendorsList = response.data.results
    })
  }

  $scope.refresh = function() {
  $scope.limit = 20
  $scope.offset = 0

  $scope.search = {
    searchText : ''
  }
  $scope.viewVendors()
  }
  $scope.refresh()


  $scope.prev = function() {
    if ($scope.limit > 0) {
      $scope.offset -= $scope.limit
      $scope.viewVendors()
    }
  }
  $scope.next = function() {
    $scope.offset += $scope.limit
    $scope.viewVendors()
  }

  $scope.createVendor = function(mode, idx){
    if (mode == 'add') {
      data = ''
    } else {
      data = $scope.vendorsList[idx]
    }
    $uibModal.open({
      templateUrl: '/static/ngTemplates/app.newVendor.form.html',
      size: 'md',
      resolve : {
        mode: function () {
          return mode;
        },
        data: function () {
          return data;
        },
      },
      controller: 'businessManagement.vendor.form'
    })
  }

  $scope.deleteVendor = function(pk,indx){
    $http({
          method : 'DELETE',
          url : '/api/ERP/vendor/'+pk+'/',
        }).
        then(function(response) {
          $scope.vendorsList.splice(indx,1)
       })
    }

})

app.controller("businessManagement.vendor.form", function($scope, $state, $users, $stateParams, $http, Flash, $uibModal, $rootScope, $aside) {
$scope.me = $users.get('mySelf');
  $scope.resetForm = function(){
      $scope.newVendor = {
      name : '',
      address : '',
      gst : '',
      bankACno : '',
      ifsc : '',
      properiterName : '',
      panNumber : '',
      phone :'',
      adharNo:'',
      firmNo:'',
      branchName:'',
      branchAddr:'',
      email:'',
      // editable : false,
      search : ''
    }
     $scope.editable = false
  }
  $scope.resetForm()

  // $scope.searchVendor = function(){
  //   if ($scope.newVendor.gst.length == 15 && $scope.me.is_superuser == true) {
  //     $http({
  //       method : 'GET',
  //       url : '/api/ERP/vendor/?gst='+$scope.newVendor.gst,
  //     }).
  //   then(function(response) {
  //     $scope.newVendor = response.data[0]
  //   })
  //   }
  // }

  // $scope.searchVendorPan = function(){
  //   if ($scope.newVendor.panNumber.length == 10 && $scope.me.is_superuser == true) {
  //     $http({
  //       method : 'GET',
  //       url : '/api/ERP/vendor/?panNumber='+$scope.newVendor.panNumber,
  //     }).
  //   then(function(response) {
  //     $scope.newVendor = response.data[0]
  //   })
  //   }
  // }
  $scope.$watch('newVendor.search' , function(newValue , oldValue){
    if (typeof newValue == 'object') {
      $scope.newVendor = newValue
      $scope.editable = true
    }
  },true);

  $scope.edit = function(){
    $scope.editable = false
    $state.go('businessManagement.editVendor',{'id':$scope.newVendor.pk})
    $scope.resetForm()
  }

  if ($state.is('businessManagement.editVendor')) {
     $http.get('/api/ERP/vendor/' + $state.params.id+'/').
    then(function(response) {
       $scope.newVendor =  response.data
        $scope.editable = false
    })
  }

  $scope.searchVendor = function(query){
    return $http.get('/api/ERP/vendor/?search=' + query).
    then(function(response) {
      return response.data;
    })
  }

  $scope.saveVendor = function() {
    console.log($scope.newVendor.gst.length,'aaaaaaaaaa')
    if ($scope.newVendor.gst.length != 15) {
      Flash.create('warning', 'Add valid GST')
      return
    }
    if ($scope.newVendor.name.length == 0) {
      Flash.create('warning', 'Add Firm Name')
      return
    }

    if ($scope.newVendor.phone.toString().length != 10) {
      Flash.create('warning', 'Add valid phone number')
      return
    }
    if ($scope.newVendor.address.length == 0) {
      Flash.create('warning', 'Add Address')
      return
    }
    if ($scope.newVendor.properiterName.length == 0) {
      Flash.create('warning', 'Add Proprieter name')
      return
    }
    if ($scope.newVendor.panNumber.length != 10) {
      Flash.create('warning', 'Add valid PAN Number')
      return
    }
    if ($scope.newVendor.bankACno.length == 0) {
      Flash.create('warning', 'Add Bank Account Number')
      return
    }
    if ($scope.newVendor.ifsc.length == 0) {
      Flash.create('warning', 'Add IFSC Number')
      return
    }
    if ($scope.newVendor.branchName.length == 0) {
      Flash.create('warning', 'Add Branch Name')
      return
    }
    if ($scope.newVendor.branchAddr.length == 0) {
      Flash.create('warning', 'Add Branch Address')
      return
    }
    var dataToSend = {
      name : $scope.newVendor.name,
      address : $scope.newVendor.address,
      gst : $scope.newVendor.gst,
      bankACno : $scope.newVendor.bankACno,
      ifsc : $scope.newVendor.ifsc,
      properiterName : $scope.newVendor.properiterName,
      panNumber : $scope.newVendor.panNumber,
      phone : $scope.newVendor.phone,
      branchName : $scope.newVendor.branchName,
      branchAddr : $scope.newVendor.branchAddr
    }
    if ($scope.newVendor.adharNo!=null && $scope.newVendor.adharNo.length>0) {
      if ($scope.newVendor.adharNo.length!=12) {
          Flash.create('warning' , 'Add valid Adhar Number')
          return
      }
      dataToSend.adharNo = $scope.newVendor.adharNo
    }
    if ($scope.newVendor.firmNo!=null && $scope.newVendor.firmNo.length>0) {
      dataToSend.firmNo = $scope.newVendor.firmNo
    }
    if ($scope.newVendor.email!=null && $scope.newVendor.email.length>0) {
      dataToSend.email = $scope.newVendor.email
    }
    var url = '/api/ERP/vendor/'
    var method = 'POST'
    if ($scope.newVendor.pk) {
      method = 'PATCH'
      url = url+$scope.newVendor.pk+'/'
    }
      $http({
        method : method,
        url : url,
        data : dataToSend
      }).
    then(function(response) {
      Flash.create('success', 'Saved');
      // $scope.resetForm()
      if ($state.is('businessManagement.vendor')) {
        $state.go('businessManagement.editVendor',{'id':response.data.pk})
      }
    },function(err) {
      if (err.data.gst) {
        Flash.create('warning',err.data.gst[0] );
      }
      if (err.data.panNumber) {
        Flash.create('warning',err.data.panNumber[0] );
      }
    })
    }


    })
