app.config(function($stateProvider){
  $stateProvider
  .state('businessManagement.contingent', {
    url: "/contingent",
    templateUrl: '/static/ngTemplates/app.contingent.html',
    controller: 'businessManagement.contingent',
  })
  $stateProvider
  .state('businessManagement.createContingent', {
    url: "/createContingent",
    templateUrl: '/static/ngTemplates/app.contingent.form.html',
    controller: 'businessManagement.contingent.form',
  })
  $stateProvider
  .state('businessManagement.editContingent', {
    url: "/editContingent/:id",
    templateUrl: '/static/ngTemplates/app.contingent.form.html',
    controller: 'businessManagement.contingent.form',
  })
});
app.controller("businessManagement.contingent", function($scope, $state, $users, $stateParams, $http, Flash, $uibModal, $rootScope, $aside) {
  $scope.me = $users.get(parseInt(USER));
  $scope.allotmentList =  []
  $scope.viewContingent = function () {
    var url = '/api/ERP/contingent/?limit='+$scope.limit+'&offset='+$scope.offset
    if ($scope.search.searchText.length > 0) {
      url = url+'&search='+$scope.search.searchText
    }
    $http({
      method : 'GET',
      url : url,
    }).
    then(function(response) {
      $scope.contingentList = response.data.results
    })
  }

  $scope.refresh = function() {
  $scope.limit = 10
  $scope.offset = 0
  $scope.search = {
    searchText : ''
  }
  $scope.viewContingent()
  }
  $scope.refresh()


  $scope.prev = function() {
    if ($scope.limit > 0) {
      $scope.offset -= $scope.limit
      $scope.viewContingent()
    }
  }
  $scope.next = function() {
    $scope.offset += $scope.limit
    $scope.viewContingent()
  }


})
app.controller("businessManagement.contingent.form", function($scope, $state, $users, $stateParams, $http, Flash, $uibModal, $rootScope, $aside) {
$scope.reset = function(){
  $scope.form = {
    invoiceNo : '',
    invoiceDate : new Date(),
    postingDate:new Date(),
    amount:0,
    subject:'',
    unitFileNo:'',
    crvNo:'',
    crvDate:new Date(),
    accntLedger:''
  }

}
$scope.reset()

$scope.getCont = function(){
  $http({
    method : 'GET',
    url : '/api/ERP/contingent/' + $state.params.id+'/',
  }).
  then(function(response) {
    $scope.form = response.data
  })
}

if ($state.is('businessManagement.editContingent')) {

$scope.getCont()

}
$http({
  method : 'GET',
  url : '/api/ERP/poOrderAll/',
}).
then(function(response) {
  $scope.poList = response.data
})

$scope.save = function(){
  var dataToSend = {
    invoiceNo : $scope.form.invoiceNo,
    // invoiceDate : new Date(),
    // postingDate:new Date(),
    amount:$scope.form.amount,
    subject:$scope.form.subject,
    unitFileNo:$scope.form.unitFileNo,
    crvNo:$scope.form.crvNo,
    // crvDate:$scope.form.crvDate,
    accntLedger:$scope.form.accntLedger,
    po : $scope.form.po.pk
  }

  if (typeof $scope.form.invoiceDate == 'object') {
    dataToSend.invoiceDate = $scope.form.invoiceDate.toJSON().split('T')[0]
  }
  if (typeof $scope.form.postingDate == 'object') {
    dataToSend.postingDate = $scope.form.postingDate.toJSON().split('T')[0]
  }
  if (typeof $scope.form.crvDate == 'object') {
    dataToSend.crvDate = $scope.form.crvDate.toJSON().split('T')[0]
  }
  if (typeof $scope.form.po == 'object') {
    dataToSend.po = $scope.form.po.pk
  }
  console.log($scope.form.pk);
  var method = 'POST'
  var url = '/api/ERP/contingent/'
  if ($scope.form.pk) {
     method = 'PATCH'
     url = '/api/ERP/contingent/'+$scope.form.pk+'/'
  }
  $http({
    method : method,
    url : url,
    data : dataToSend
  }).
  then(function(response) {
    Flash.create('success','Saved')
    if ($state.is('businessManagement.createContingent')) {
      $scope.reset()
      $state.go('businessManagement.editContingent' , {'id' : response.data.pk})
    }
    else{
      $scope.getCont()
    }
  })
}

})
