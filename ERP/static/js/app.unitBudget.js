app.config(function($stateProvider){

  $stateProvider
  .state('businessManagement.unitBudget', {
    url: "/unitBudget",
    templateUrl: '/static/ngTemplates/app.unitBudget.html',
    controller: 'businessManagement.unitBudget',
  })

});


app.controller("businessManagement.unitBudget", function($scope, $state, $users, $stateParams, $http, Flash, $uibModal, $rootScope, $aside) {
  $scope.me = $users.get(parseInt(USER));
  $scope.allotmentList =  []
  $scope.viewAllocation = function () {
    var url = '/api/ERP/getAllAllocation/?req='
    $http({
      method : 'GET',
      url : url,
    }).
    then(function(response) {
      $scope.allotmentList = response.data
    })
  }

  $scope.refresh = function() {
  $scope.limit = 10
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

  $scope.open = function(data){
  $uibModal.open({
    templateUrl: '/static/ngTemplates/app.viewBudget.html',
    size: 'xl',
    backdrop:false,
    resolve : {
      data: function () {
        return data;
      },
    },
    controller: function($scope, $http,data,$uibModalInstance){
      $scope.data = data
      $scope.close = function(){
        $uibModalInstance.dismiss()
      }

      $scope.withdraw = function(indx, dataval){

        var dataToSend = {
          'pk' : dataval.pk,
          'wihdrawAmount':dataval.wihdrawAmount
        }
        $http({
          method : 'POST',
          url : '/api/ERP/withdrawBudget/',
          data : dataToSend
        }).
        then(function(response) {
          Flash.create('success' ,'Saved')
          $scope.data[indx].balance = parseFloat($scope.data[indx].balance) - parseFloat(response.data.data.wihdrawAmount)
          $scope.data[indx] = response.data.data

        })
      }

    }
  }).result.then(function () {

}, function () {
  $scope.viewAllocation()
});
  }

})
