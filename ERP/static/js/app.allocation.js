app.config(function($stateProvider){

  $stateProvider
  .state('businessManagement.allocation', {
    url: "/allocation",
    templateUrl: '/static/ngTemplates/app.allocation.html',
    controller: 'businessManagement.allocation',
  })

});

app.controller("businessManagement.allocation", function($scope, $state, $users, $stateParams, $http, Flash, $uibModal, $rootScope, $aside) {

$scope.me = $users.get(parseInt(USER));

$scope.allotmentList =  []
$scope.viewAllocation = function () {
  var url = '/api/ERP/getBulkAllocation/'
  // if ($scope.search.searchText.length > 0) {
  //   url = url+'&search='+$scope.search.searchText
  // }
  $http({
    method : 'GET',
    url : url,
  }).
  then(function(response) {
    $scope.allotmentList = response.data
  })
}

$scope.refresh = function() {
$scope.limit = 20
$scope.offset = 0

$scope.search = {
  searchText : ''
}
$scope.viewAllocation()
}
$scope.refresh()


$scope.prev = function() {
  if ($scope.limit > 0) {
    $scope.offset -= $scope.limit
    $scope.viewAllocation()
  }
}
$scope.next = function() {
  $scope.offset += $scope.limit
  $scope.viewAllocation()
}



$scope.createUserAllotment =  function(mode,idx){
  if (mode == 'add') {
    data = ''
  } else {
    data = $scope.allotmentList[idx]
  }
  $uibModal.open({
    templateUrl: '/static/ngTemplates/app.newUserAllocation.form.html',
    size: 'md',
    resolve : {
      mode: function () {
        return mode;
      },
      data: function () {
        return data;
      },
    },
    controller: 'businessManagement.allocationUser.form'
  })
}

$scope.viewAllotment = function(idx){
  $uibModal.open({
    templateUrl: '/static/ngTemplates/app.newAllocation.view.html',
    size: 'lg',
    resolve : {
      data: function () {
        return $scope.allotmentList[idx];
      },
    },
    controller: 'businessManagement.allocation.view'
  })
}

$scope.viewAllAllotment = function(){
  console.log("hereeeeeeeeee");
  $uibModal.open({
    templateUrl: '/static/ngTemplates/app.newAllocation.viewAll.html',
    size: 'lg',
    controller: 'businessManagement.allocation.viewAll'
  })
}

$scope.viewAllUtilisation = function(){
  console.log("hereeeeeeeeee");
  $uibModal.open({
    templateUrl: '/static/ngTemplates/app.viewAllUtilisation.viewAll.html',
    size: 'xl',
    controller: 'businessManagement.viewAllUtilisation.viewAll'
  })
}
})

app.controller("businessManagement.allocation.viewAll", function($scope, $state, $users, $stateParams, $http, Flash, $rootScope, $uibModalInstance) {
  $http({
    method : 'GET',
    url : '/api/ERP/getAllAllocation/',
  }).
  then(function(response) {
    console.log(response.data,'aaaaaaaaaaa');
    $scope.allData = response.data
  })
})

app.controller("businessManagement.viewAllUtilisation.viewAll", function($scope, $state, $users, $stateParams, $http, Flash, $rootScope, $uibModalInstance) {
  // $http({
  //   method : 'GET',
  //   url : '/api/ERP/getAllAllocation/',
  // }).
  // then(function(response) {
  //   console.log(response.data,'aaaaaaaaaaa');
  //   $scope.allData = response.data
  // })
})

app.controller("businessManagement.allocationUser.form", function($scope, $state, $users, $stateParams, $http, Flash, $rootScope, $uibModalInstance, mode, data) {
$scope.mode = mode
$scope.parent = data
$scope.refresh = function(){
  $scope.form = {
    name:'',
    codeHead:'',
    allotmentAmount:0,
    description:'',
    sanctioned_no:'',
    cont_no:''
  }
}
$scope.refresh()



$scope.saveAllocation = function() {
  if ($scope.form.name == null || $scope.form.name.length==0 || $scope.form.codeHead == null || $scope.form.codeHead.length==0 || $scope.form.allotmentAmount == null || $scope.form.allotmentAmount.length==0) {
    Flash.create('warning' , 'Add all details')
    return
  }
  var dataToSend = {
    'name' : $scope.form.name,
    'codeHead' : $scope.form.codeHead,
    'allotmentAmount' : $scope.form.allotmentAmount,
    'balance' : $scope.form.allotmentAmount,
    'description' : $scope.form.description,
    'dated' : $scope.form.dated.toJSON().split('T')[0],
    'cont_no' : $scope.form.cont_no,
    'sanctioned_no' : $scope.form.sanctioned_no,
  }

  if (typeof $scope.parent == 'object') {
    dataToSend.parent = $scope.parent.pk

  }
  $http({
    method : 'POST',
    url : '/api/ERP/budgetAllocation/',
    data : dataToSend
  }).
  then(function(response) {
    Flash.create('success' ,'Added')
    $uibModalInstance.dismiss();
  })
}

})





app.controller("businessManagement.allocation.view", function($scope, $state, $users, $stateParams, $http, Flash, $rootScope, $uibModalInstance, data) {
$scope.data = data
$scope.me = $users.get(parseInt(USER));
  $http({
    method : 'GET',
    url : '/api/ERP/budgetAllocation/?parent=' + $scope.data.pk,
  }).
  then(function(response) {
    $scope.allData = response.data
  })

})
