app.controller('sudo.manageUsers.explore', function($scope, $http, $aside, $state, Flash, $users, $filter, $timeout) {

  $scope.data = $scope.tab.data;
  $scope.isStoreGlobal = false;
  $http.get('/api/ERP/appSettings/?app=25&name__iexact=isStoreGlobal').
  then(function(response) {
    if (response.data[0] != null) {
      $scope.isStoreGlobal = response.data[0].flag
    }
  })


  $scope.details = {
    Address: '',
    Company: '',
    GST: '',
    agree: '',
    designation: '',
    email: '',
    emailOTP: '',
    firstName: '',
    lastName: '',
    mobile: '',
    mobileOTP: '',
    password: '',
    pincode: '',
    rePassword: '',
    reg: '',
    statecode: '',
    token: ''
  }

  $scope.addresses = [];
  $http({
    method: 'GET',
    url: '/api/ecommerce/address/?user=' + $scope.data.pk
  }).then(function(response) {
    $scope.addresses = response.data
  })

  // $scope.details = ''
  $scope.updateProfile = false
  if ($scope.data.profile) {
    if ($scope.data.profile.details) {
      $scope.detailsUser = $scope.data.profile.details
      valid = $scope.detailsUser.replace(/u'/g, "'")
      valid = valid.replace(/'/g, '"')
      valid = valid.replace(/True/g, 'true')
      valid = valid.replace(/None/g, '""')
      $scope.details = JSON.parse(valid)
    }

  }
  $scope.updateData = function() {
    $scope.updateProfile = true
  }

  $scope.updateDetails = function() {
    // console.log($scope.details);
    $http({
      method: 'PATCH',
      url: '/api/HR/profile/' + $scope.data.profile.pk + '/',
      data: {
        details: $scope.details,
      }
    }).
    then(function(response) {
      Flash.create('success', 'Saved!')
      $scope.updateProfile = false
    })
  }


});


