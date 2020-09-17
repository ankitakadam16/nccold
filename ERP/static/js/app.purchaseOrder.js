app.config(function($stateProvider){

  $stateProvider
  .state('businessManagement.purchaseOrder', {
    url: "/purchaseOrder",
    templateUrl: '/static/ngTemplates/app.purchaseOrder.html',
    controller: 'businessManagement.purchaseOrder',
  })
  $stateProvider
  .state('businessManagement.createPO', {
    url: "/createPO",
    templateUrl: '/static/ngTemplates/app.purchaseOrder.form.html',
    controller: 'businessManagement.purchaseOrder.form',
  })
  $stateProvider
  .state('businessManagement.editPO', {
    url: "/editPO/:id",
    templateUrl: '/static/ngTemplates/app.purchaseOrder.form.html',
    controller: 'businessManagement.purchaseOrder.form',
  })
   $stateProvider
  .state('businessManagement.explorePO', {
    url: "/explorePO/:id",
    templateUrl: '/static/ngTemplates/app.purchaseOrder.explorePO.html',
    controller: 'businessManagement.purchaseOrder.explorePO',
  })
});

app.controller("businessManagement.purchaseOrder", function($scope, $state, $users, $stateParams, $http, Flash, $uibModal, $rootScope, $aside) {

  $scope.viewPo = function () {
    var url = '/api/ERP/poOrder/?limit='+$scope.limit+'&offset='+$scope.offset
    if ($scope.search.searchText.length > 0) {
      url = url+'&search='+$scope.search.searchText
    }
    $http({
      method : 'GET',
      url : url,
    }).
    then(function(response) {
      $scope.poList = response.data.results
    })
  }

  $scope.refresh = function() {
  $scope.limit = 20
  $scope.offset = 0

  $scope.search = {
    searchText : ''
  }
  $scope.viewPo()
  }
  $scope.refresh()


  $scope.prev = function() {
    if ($scope.limit > 0) {
      $scope.offset -= $scope.limit
      $scope.viewPo()
    }
  }
  $scope.next = function() {
    $scope.offset += $scope.limit
    $scope.viewPo()
  }

  // $scope.poOpenAside = function(mode, idx){
  //   if (mode == 'add') {
  //     data = ''
  //   } else {
  //     data = $scope.poList[idx]
  //   }

  // $aside.open({
  //   templateUrl: '/static/ngTemplates/app.purchaseOrder.form.html',
  //   placement: 'right',
  //   size: 'xl',
  //   resolve : {
  //     mode: function () {
  //       return mode;
  //     },
  //     data: function () {
  //       return data;
  //     },
  //   },
  //   controller: 'businessManagement.purchaseOrder.form'

  //   });

  // }
})


app.controller("businessManagement.purchaseOrder.explorePO", function($scope, $state, $users, $stateParams, $http, Flash, $uibModal, $rootScope, $aside) {
  $scope.selected='gfr'
  $scope.inWords = ''
$scope.poDetails = function(){
  $http.get('/api/ERP/poOrderAll/' + $state.params.id +'/').
    then(function(response) {
    $scope.newPo = response.data
    $scope.inWords  = price_in_words($scope.newPo.poTotal)
  })
  }
 $scope.poDetails()

 $scope.update = function(){
      if ($scope.newPo.member1_name == null || $scope.newPo.member1_name == undefined || $scope.newPo.member1_name.length == 0 || $scope.newPo.member2_name == null || $scope.newPo.member2_name == undefined || $scope.newPo.member2_name.length == 0 || $scope.newPo.member3_name == null || $scope.newPo.member3_name == undefined || $scope.newPo.member3_name.length == 0 || $scope.newPo.member1_name == null || $scope.newPo.member1_name == undefined || $scope.newPo.member1_name.length == 0 || $scope.newPo.member1_no == null || $scope.newPo.member1_no == undefined || $scope.newPo.member1_no.length == 0 || $scope.newPo.member2_no == null || $scope.newPo.member2_no == undefined || $scope.newPo.member2_no.length == 0 || $scope.newPo.member3_no == null || $scope.newPo.member3_no == undefined || $scope.newPo.member1_pos.length == 0  || $scope.newPo.member1_pos == null || $scope.newPo.member3_pos == undefined || $scope.newPo.member3_pos.length == 0 || $scope.newPo.member2_pos == null || $scope.newPo.member2_pos == undefined || $scope.newPo.member2_pos.length == 0  ) {
        Flash.create('warning','Member Details are required')
        return

      }
      $http({
        method : 'PATCH',
        url : '/api/ERP/poOrder/' + $scope.newPo.pk+'/',
        data : {
          member1_name : $scope.newPo.member1_name,
          member1_no : $scope.newPo.member1_no,
          member1_pos : $scope.newPo.member1_pos,
          member2_name : $scope.newPo.member2_name,
          member2_no : $scope.newPo.member2_no,
          member2_pos : $scope.newPo.member2_pos,
          member3_name : $scope.newPo.member3_name,
          member3_no : $scope.newPo.member3_no,
          member3_pos : $scope.newPo.member3_pos,
        }
      }).
    then(function(response) {
      Flash.create('success', 'Saved');
      // if (mode == 'new') {
      //   $scope.poitemList.push($scope.itemData)
      // }
      // $scope.newPo = response.data
      // $uibModalInstance.dismiss();
    })
 }

})

app.controller("businessManagement.purchaseOrder.form", function($scope, $state, $users, $stateParams, $http, Flash, $uibModal, $rootScope, $aside) {

  $scope.vendorSearch = function(query) {
  return $http.get('/api/ERP/vendor/?search=' + query).
  then(function(response) {
    return response.data;
  })
  };

  $scope.getUnit = function(){
  $http.get('/api/HR/users/' + USER +'/').
    then(function(response) {
    $scope.newPo.unitAddress = response.data.profile.address
    $scope.newPo.deliveryAddress = response.data.profile.address
  })
  }
  $scope.workShow = true
  $scope.supplyShow = true
  $scope.add = function(){
     $scope.workShow = true
    $scope.supplyShow = true
    if ($scope.newPo.supplyOrderNo.length>0 || $scope.newPo.supplyOrderDate.length>0  || typeof $scope.newPo.supplyOrderDate == 'object' ) {
      $scope.workShow = false
    } 
     if ($scope.newPo.workOrderNo.length>0 || $scope.newPo.workOrderDate.length>0  || typeof $scope.newPo.workOrderDate == 'object'  ) {
      $scope.supplyShow = false
    } 
  }

$scope.poDetails = function(){
  $http.get('/api/ERP/poOrderAll/' + $state.params.id +'/').
    then(function(response) {
    $scope.newPo = response.data
    $scope.poitemList  = $scope.newPo.poItems
    $scope.add()
  })
  }


  $scope.itemData = {
    name:'',
    denominator:'',
    quantity:0,
    rate:0,
    amount:0,
    gst:0,
    gstAmount:0,
    grandTotal:0
  }






  $scope.getVal = function(idx){
    var data = $scope.poitemList[idx]
    $scope.poitemList[idx].amount = parseInt(data.rate) * parseInt(data.quantity)
    $scope.poitemList[idx].gstAmount = parseInt(data.amount) * parseInt(data.gst)/100
    $scope.poitemList[idx].grandTotal = parseInt(data.gstAmount) + parseInt(data.amount)
  }

  $scope.saveEntry = function(idx){
    var data = $scope.poitemList[idx]
    if (data.name == '') {
      Flash.create('warning', 'Enter Product')
      return
    }
    if (data.denominator == '') {
      Flash.create('warning', 'Enter denominator')
      return
    }
    if (data.quantity == 0) {
      Flash.create('warning', 'Quantity cannot be 0')
      return
    }

    var dataToSend = {
      name : data.name,
      denominator : data.denominator,
      quantity : data.quantity,
      rate : data.rate,
      amount : data.amount,
      gst : data.gst,
      gstAmount : data.gstAmount,
      grandTotal : data.grandTotal,
      po : $scope.newPo.pk
    }
    var method = 'POST'
    var url = '/api/ERP/poItem/'

    if (data.pk){
      method = 'PATCH'
      var url = '/api/ERP/poItem/'+data.pk+'/'
    }

    $http({
      method : method,
      url : url,
      data: dataToSend,
    }).
    then(function(response) {
      $scope.poitemList[idx] = response.data
      Flash.create('success', 'Saved');
    })

  }

  $scope.deleteEntry = function(idx){
    if ($scope.poitemList[idx].pk) {
      $http({
        method : 'DELETE',
        url : '/api/ERP/poItem/'+$scope.poitemList[idx].pk+'/'
      }).
      then(function(response) {
        $scope.poitemList.splice(idx,1)
        Flash.create('success', 'Deleted');
      })
    } else {
      $scope.poitemList.splice(idx,1)
      Flash.create('success', 'Deleted');
    }
  }

  $scope.resetForm = function(){
    $scope.newPo = {
      vendor : '',
      subject : '',
      dated:new Date(),
      unitAddress:'',
      deliveryAddress:'',
      gfrRule:'',
      sanctionAutority:'',
      sanctionNo:'',
      sanctionDate:new Date(),
      codeHead:'',
      minorHead:'',
      fileNo:'',
      vendorName:'',
      vendorAddress:'',
      quoteDate:new Date(),
      quoteNo:'',
      supplyOrderNo:'',
      supplyOrderDate:'',
      workOrderNo:'',
      workOrderDate:'',
      majorHead : ''
    }
  }

  $scope.poitemList = []
  $scope.resetForm()


  if ($state.is('businessManagement.editPO')) {
    $scope.poDetails()
  }
  else{
     $scope.getUnit()
  }


  $scope.savePo = function() {
    if (typeof $scope.newPo.vendor!='object' || $scope.newPo.vendor.length == 0) {
      Flash.create('warning', 'Add Vendor')
      return
    }
    if (typeof $scope.newPo.unitAddress == null || $scope.newPo.unitAddress.length == 0) {
      Flash.create('warning', 'Add Unit Address')
      return
    }

    if (typeof $scope.newPo.deliveryAddress == null || $scope.newPo.deliveryAddress.length == 0) {
      Flash.create('warning', 'Add Delivery Address')
      return
    }
    var dataToSend = {
      unitAddress : $scope.newPo.unitAddress,
      deliveryAddress : $scope.newPo.deliveryAddress,
      vendor : $scope.newPo.vendor.pk,
      vendorName : $scope.newPo.vendor.name,
      vendorAddress : $scope.newPo.vendor.address,
      subject : $scope.newPo.subject,
      gfrRule : $scope.newPo.gfrRule,
      sanctionAutority : $scope.newPo.sanctionAutority,
      sanctionNo : $scope.newPo.sanctionNo,
      codeHead : $scope.newPo.codeHead,
      minorHead : $scope.newPo.minorHead,
      fileNo : $scope.newPo.fileNo,
      quoteNo : $scope.newPo.quoteNo,
      supplyOrderNo : $scope.newPo.supplyOrderNo,
      workOrderNo : $scope.newPo.workOrderNo,
      majorHead : $scope.newPo.majorHead
    }
    if (typeof $scope.newPo.dated == 'object') {
      dataToSend.dated = $scope.newPo.dated.toJSON().split('T')[0]
    }
    if (typeof $scope.newPo.sanctionDate == 'object') {
        dataToSend.sanctionDate = $scope.newPo.sanctionDate.toJSON().split('T')[0]
      }
    if (typeof $scope.newPo.quoteDate == 'object') {
        dataToSend.quoteDate = $scope.newPo.quoteDate.toJSON().split('T')[0]
      }
    if (typeof $scope.newPo.supplyOrderDate == 'object') {
        dataToSend.supplyOrderDate = $scope.newPo.supplyOrderDate.toJSON().split('T')[0]
      }
    
     if (typeof $scope.newPo.workOrderDate == 'object') {
        dataToSend.workOrderDate = $scope.newPo.workOrderDate.toJSON().split('T')[0]
      }
    var url = '/api/ERP/poOrder/'
    var method = 'POST'
    if ($scope.newPo.pk) {
      method = 'PATCH'
      url = url+$scope.newPo.pk+'/'
    }
      $http({
        method : method,
        url : url,
        data : dataToSend
      }).
    then(function(response) {
      Flash.create('success', 'Saved');
      // if (mode == 'new') {
      //   $scope.poitemList.push($scope.itemData)
      // }
      $scope.newPo = response.data
      // $uibModalInstance.dismiss();
    })
    }

  $scope.addPoItem = function(){
    var itData = $scope.itemData
    $scope.poitemList.push(itData)
    $scope.itemData = {
      name:'',
      denominator:'',
      quantity:0,
      rate:0,
      amount:0,
      gst:0,
      gstAmount:0,
      grandTotal:0
    }
  }

})
