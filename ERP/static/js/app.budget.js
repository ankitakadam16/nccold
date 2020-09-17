app.config(function($stateProvider){

  $stateProvider
  .state('businessManagement.budget', {
    url: "/budget",
    templateUrl: '/static/ngTemplates/app.budget.html',
    controller: 'businessManagement.budget',
  })

});


app.controller("businessManagement.budget", function($scope, $state, $users, $stateParams, $http, Flash, $uibModal, $rootScope, $aside) {

$scope.me = $users.get(parseInt(USER));

$scope.allotmentList =  []
$scope.viewAllocation = function () {
  var url = '/api/ERP/budgetAllocation/?unit='+$scope.me.pk+'&limit='+$scope.limit+'&offset='+$scope.offset

  $http({
    method : 'GET',
    url : url,
  }).
  then(function(response) {
    $scope.allotmentList = response.data.results
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
$scope.createAllotment = function(mode,idx){
  if (mode == 'add') {
    data = ''
  } else {
    data = $scope.allotmentList[idx]
  }
  $uibModal.open({
    templateUrl: '/static/ngTemplates/app.newAllocation.form.html',
    size: 'md',
    resolve : {
      mode: function () {
        return mode;
      },
      data: function () {
        return data;
      },
    },
    controller: 'businessManagement.allocation.form'
  }).result.then(function () {

}, function () {
  $scope.viewAllocation()
});
}

$scope.allot = function(indx){
  $uibModal.open({
    templateUrl: '/static/ngTemplates/app.allotBudget.form.html',
    size: 'xl',
    backdrop:false,
    resolve : {
      data: function () {
        return $scope.allotmentList[indx];
      },
    },
    controller: 'businessManagement.allotBudget.form'
  }).result.then(function () {

}, function () {
  $scope.viewAllocation()
});
}
})


app.controller("businessManagement.allocation.form", function($scope, $state, $users, $stateParams, $http, Flash, $rootScope, $uibModalInstance, mode, data) {
$scope.mode = mode
$scope.parent = data
$scope.refresh = function(){
  $scope.form = {
    name:'',
    codeHead:'',
    allotmentAmount:0,
    minorHead:'',
    dated:new Date()
  }
}
$scope.refresh()

$scope.unitSearch = function(query){
  return $http.get('/api/HR/searchusers/?name=' + query).
  then(function(response) {
    return response.data;
  })
}


$scope.me = $users.get(parseInt(USER));

$scope.saveAllocation = function() {
  if ($scope.form.name == null || $scope.form.name.length==0 || $scope.form.minorHead == null || $scope.form.minorHead.length==0 || $scope.form.codeHead == null || $scope.form.codeHead.length==0 || $scope.form.allotmentAmount == null || $scope.form.allotmentAmount.length==0) {
    Flash.create('warning' , 'Add all details')
    return
  }
  var dataToSend = {
    'name' : $scope.form.name,
    'codeHead' : $scope.form.codeHead,
    'allotmentAmount' : $scope.form.allotmentAmount,
    'balance' : $scope.form.allotmentAmount,
    'unit' : $scope.me.pk,
    'minorHead' :$scope.form.minorHead,
    'dated' : $scope.form.dated.toJSON().split('T')[0]
  }
  // if (typeof $scope.parent == 'object') {
  //   dataToSend.parent = $scope.parent.pk
  //
  // }
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


app.controller("businessManagement.allotBudget.form", function($scope, $state, $users, $stateParams, $http, Flash, $rootScope, $uibModalInstance, data) {
$scope.budgetAlloted  = []
$scope.me = $users.get(parseInt(USER));
$scope.parent = data
$scope.getBudgetAlloted = function(){
  $http({
    method : 'GET',
    url : '/api/ERP/budgetAllocation/?parent='+data.pk,
  }).
  then(function(response) {
    $scope.budgetAlloted = response.data
  })
}

$scope.getBudgetAlloted()
$scope.unitSearch = function(){
   $http.get('/api/HR/searchusers/?only=').
  then(function(response) {
    $scope.allUsers = response.data;
  })
}
$scope.unitSearch()

$scope.form = {
  name:data.name,
  codeHead:data.codeHead,
  allotmentAmount:0,
  minorHead:data.minorHead,
  dated :new Date(),
  unit:'',
  allotment_no:''
}

$scope.close = function(){
  $uibModalInstance.dismiss()
}

$scope.withdraw = function(indx, data){

  var dataToSend = {
    'pk' : data.pk,
    'wihdrawAmount':data.wihdrawAmount
  }
  $http({
    method : 'POST',
    url : '/api/ERP/withdrawBudget/',
    data : dataToSend
  }).
  then(function(response) {
    Flash.create('success' ,'Saved')
    $scope.budgetAlloted[indx] = response.data.data
    $scope.parent.balance = parseFloat($scope.parent.balance) + parseFloat(data.wihdrawAmount)

  })
}

$scope.save = function(){

  if ($scope.form.allotmentAmount<=0) {
    Flash.create('warning','Amount should be more than 0')
    return
  }
  var dataToSend = {
    'name' : $scope.form.name,
    'codeHead' : $scope.form.codeHead,
    'allotmentAmount' : $scope.form.allotmentAmount,
    'minorHead' :$scope.form.minorHead,
    'parent':data.pk,
    'balance':  $scope.form.allotmentAmount,
    'allotment_no': $scope.form.allotment_no,
  }
  if (typeof $scope.form.unit == 'object') {
    dataToSend.unit =  $scope.form.unit.pk
  }else{
    Flash.create('warning','Add Unit')
    return
  }
  if (typeof $scope.form.dated == 'object') {
    dataToSend.dated = $scope.form.dated.toJSON().split('T')[0]
  }
  $http({
    method : 'POST',
    url : '/api/ERP/budgetAllocation/',
    data : dataToSend
  }).
  then(function(response) {
    Flash.create('success' ,'Saved')
      $scope.budgetAlloted.push(response.data)
      $scope.parent.balance = parseFloat($scope.parent.balance) - parseFloat($scope.form.allotmentAmount)
      $scope.form = {
        name:data.name,
        codeHead:data.codeHead,
        allotmentAmount:0,
        minorHead:data.minorHead,
        dated :new Date(),
        unit:'',
        allotment_no:''
      }
  })
}


})
