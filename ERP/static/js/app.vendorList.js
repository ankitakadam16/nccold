app.config(function($stateProvider){

  $stateProvider
  .state('businessManagement.vendorList', {
    url: "/vendorList",
    templateUrl: '/static/ngTemplates/app.vendorList.html',
    controller: 'businessManagement.vendorList',
  })
});

app.controller("businessManagement.vendorList", function($scope, $state, $users, $stateParams, $http, Flash, $uibModal, $rootScope, $aside) {

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



})
