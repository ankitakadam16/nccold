var app = angular.module('app', []);

app.controller('registrationLite', function($scope, $http, $timeout, $interval, $location) {
  var url = $location.absUrl()
  if (url.includes('vendor-registeration'))
  {
    $scope.userType = 'vendor'
  }
  else{
    $scope.userType = 'user'
  }

  $scope.mode = 'main';
  $scope.autoActiveReg = autoActiveReg
  console.log(autoActiveReg);{}
  $scope.showActiveMsg = false
  $scope.signUp = true

  $scope.form = {
    mobile: null,
    mobileOTP: null,
    token: null,
    reg: null,
    agree: false,
    is_staff:false
    // firstName: ''
  };

  $scope.validityChecked = false;
  $scope.validityChecked2 = false;
  $scope.details = false
  $scope.msg = ''
  $scope.getOTP = function() {
    var toSend = {
      mobile: $scope.form.mobile,
      email: $scope.form.email,
      // is_staff:$scope.form.is_staff
      // firstName: $scope.form.firstName,
    }
    $scope.mode = 'sendingOTP';
    $http({
      method: 'POST',
      url: '/api/homepage/registration/',
      data: toSend
    }).
    then(function(response) {
      console.log(response.data);
      // $scope.msg = "please wait......."
      $scope.signUp = false
      $scope.form.pk = response.data.pk;
      $scope.form.token = response.data.token;
      $scope.form.reg = response.data.pk;
      $scope.form.mobile = response.data.mobile;
      $scope.mode = 'verify';
      $scope.showMsg = true
      $scope.usernameExist = false
    }).catch(function(err) {
      $scope.mode = 'main';
      if (err.data.PARAMS == 'Username already taken') {
        $scope.usernameExist = true
      }
    })

  }
  // $scope.getvendorOTP = function() {
  //   $scope.form.is_staff =true
  //
  //   var toSend = {
  //     mobile: $scope.form.mobile,
  //     email: $scope.form.email,
  //     is_staff:$scope.form.is_staff
  //     // firstName: $scope.form.firstName,
  //   }
  //   $scope.mode = 'sendingOTP';
  //   $http({
  //     method: 'POST',
  //     url: '/api/homepage/registration/',
  //     data: toSend
  //   }).
  //   then(function(response) {
  //     $scope.signUp = false
  //     $scope.form.token = response.data.token;
  //     $scope.form.reg = response.data.pk;
  //     $scope.mode = 'verify';
  //     $scope.usernameExist = false
  //   }).catch(function(err) {
  //     $scope.mode = 'main';
  //     if (err.data.PARAMS == 'Username already taken') {
  //       $scope.usernameExist = true
  //     }
  //   })
  //
  // }


  $scope.resendOtp = function(){
    console.log($scope.form.pk,'ppppphgh');
    $scope.showMsg = false
    $http({
      method: 'POST',
      url: '/api/homepage/resendOtp/',
      data: {
      id : $scope.form.pk,
      otpType : 'mobileOtp'
    }
    }).
    then(function(response) {
      $scope.showMsg = true
    })


  }

  $scope.verify = function() {
    console.log($scope.form);
    if ($scope.userType == 'vendor') {
      $scope.form.is_staff = true
    }
    else{
        $scope.form.is_staff = false
    }
    $http({
      method: 'PATCH',
      url: '/api/homepage/registration/' + $scope.form.reg + '/',
      data: $scope.form
    }).
    then(function(response) {
      console.log(response);
       // window.location.assign("/ERP/")
      if ($scope.userType == 'vendor') {
        window.location.href = "/setupStore";
      }
      else{
          window.location.href = "/";
      }
      $scope.details = true
    }, function(err) {
      console.log(err);
      if (err.status == 400) {
        $scope.validityChecked2 = true;
      }
    })


  }
  if (mobile.length > 0) {
    console.log(mobile);
    $scope.form.mobile = mobile
    $scope.form.agree = true
    $scope.getOTP()
  }
  $scope.skip = function() {
    window.location.href = "/";
  }
  $scope.saveData = function() {
    console.log($scope.form.reg);
    $scope.form.details = 'details'
    $http({
      method: 'POST',
      url: '/api/homepage/updateInfo/',
      data: $scope.form
    }).
    then(function(response) {
      console.log(response);
      window.location.href = "/";
    }, function(err) {
      console.log(err);
      if (err.status == 400) {}
    })
  }
  $scope.continue = function() {
    window.location.href = "/";
  }
});
