app.config(function($stateProvider){
  $stateProvider
  .state('businessManagement.members', {
    url: "/members",
    templateUrl: '/static/ngTemplates/app.members.form.html',
    controller: 'businessManagement.members.form',
  })

});



app.controller("businessManagement.members.form", function($scope, $state, $users, $stateParams, $http, Flash, $uibModal, $rootScope, $aside) {
$scope.me = $users.get(parseInt(USER));
$scope.members = [{
  'name' : '',
  'rank':'',
  'serviceNo':'',
  'typ':'Member'
},{
  'name' : '',
  'rank':'',
  'serviceNo':'',
  'typ':'Member'
},{
  'name' : '',
  'rank':'',
  'serviceNo':'',
  'typ':'President'
}]
$http({
  method : 'GET',
  url : '/api/ERP/members/',
}).
then(function(response) {
  if (response.data.length>0) {
    $scope.members[0] = response.data[0]
    if (response.data.length >= 2) {
      $scope.members[1] = response.data[1]
    }
    if (response.data.length == 3) {
      $scope.members[2] = response.data[2]
    }
  }
})

$scope.save = function(indx){
  var data = $scope.members[indx]
  if (data.pk) {
    var method = 'PATCH'
    var url = '/api/ERP/members/'+data.pk+'/'
  }
  else{
    var method = 'POST'
    var url = '/api/ERP/members/'
  }
  var dataToSend = {
    name : data.name,
    rank : data.rank,
    serviceNo : data.serviceNo,
    typ : data.typ,
    unit : $scope.me.pk
  }
  $http({
    method : method,
    url : url,
    data:dataToSend,
  }).
  then(function(response) {
    $scope.members[indx] = response.data
  })
}

})
