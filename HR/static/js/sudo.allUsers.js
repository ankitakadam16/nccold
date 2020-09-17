app.controller('admin.manageUsers', function($scope, $http, $aside, $state, Flash, $users, $filter, $timeout, $uibModal) {

  $scope.limit = 20
  $scope.offset = 0

  $scope.userform = {
    userText: '',
    sort: ''
  }

  $scope.Usernext = function() {
    $scope.offset += $scope.limit
    $scope.usersData()
  }
  $scope.prevUser = function() {
    if ($scope.limit > 0) {
      $scope.offset -= $scope.limit

      $scope.usersData()
    }

  }

  $scope.delete = function(indx , pk){
     $http({
      method: 'DELETE',
      url: '/api/HR/users/'+indx+'/'
    }).
    then(function(response) {
      $scope.allUsers.splice(indx,1)
    })
  }

  $scope.allUsers = []
  $scope.usersData = function() {
    var url = '/api/HR/users/?limit=' + $scope.limit + '&offset=' + $scope.offset
    if ($scope.userform.userText.length > 0) {
      url = url + '&username__icontains=' + $scope.userform.userText
    }

    if ($scope.userform.sort.length > 0) {
      if ($scope.userform.userText.length > 0) {
        url = url + '&username__icontains=' + $scope.userform.userText
      }
      url = url + '&sort=' + $scope.userform.sort
    }
    $http({
      method: 'GET',
      url: url
    }).
    then(function(response) {
      $scope.allUsers = response.data.results
    })
  }
  $scope.usersData()
  $scope.searchUser = function() {
    $scope.usersData()
  }
  $scope.Usersorting = function(val) {
    $scope.userform.sort = '-' + val
    console.log($scope.userform.sort);
    $scope.usersData()
  }
})


app.controller('admin.manageUsers.userform', function($scope, $http, $aside, $state, Flash, $users, $filter, $timeout, $uibModal) {

  $scope.getUser = function() {
    $http({
      method: 'GET',
      url: '/api/HR/getUser/?id=' + $state.params.id,
    }).
    then(function(response) {
      $scope.data = response.data
    })
  }



  $scope.resetForm = function() {
    $scope.data = {
      first_name : "",
      username : "",
      last_name : "",
      mobile : "",
      email : '',
      pNumber:"",
      rank:"",
      dateOfComm:"",
      address:"",
      dateOfJoin:"",
    }
  }

  if ($state.is('businessManagement.editUsers')) {
    $scope.getUser()
  } else {
    $scope.resetForm()
  }

  $scope.createUser = function() {
    // if($scope.data.username == null || $scope.data.username.length == 0 || $scope.data.first_name == null || $scope.data.first_name.length == 0 $scope.data.last_name == null || $scope.data.last_name.length == 0 ||$scope.data.email == null || $scope.data.email.length == 0 ||$scope.data.mobile == null || $scope.data.mobile.length == 0 || $scope.data.pNumber == null || $scope.data.pNumber.length == 0 || $scope.data.rank == null || $scope.data.rank.length == 0 || $scope.data.dateOfComm == null || $scope.data.dateOfComm.length == 0 || $scope.data.address == null || $scope.data.address.length == 0 || $scope.data.dateOfJoin == null || $scope.data.dateOfJoin.length == 0){
    //   Flash.create('warining' , 'All details are required')
    //   return
    // }
    if ($scope.data.username == null || $scope.data.username.length == 0 || $scope.data.first_name == null || $scope.data.first_name.length == 0 || $scope.data.last_name == null || $scope.data.last_name.length == 0 ||$scope.data.email == null || $scope.data.email.length == 0 ||$scope.data.mobile == null || $scope.data.mobile.length == 0 || $scope.data.pNumber == null || $scope.data.pNumber.length == 0 || $scope.data.rank == null || $scope.data.rank.length == 0 || $scope.data.dateOfComm == null || $scope.data.dateOfComm.length == 0 || $scope.data.address == null || $scope.data.address.length == 0 || $scope.data.dateOfJoin == null || $scope.data.dateOfJoin.length == 0) {
      Flash.create('warining' , 'All details are required')
      return
    } 
    var dataToSend = $scope.data
    if (typeof $scope.data.dateOfComm == 'object') {
      dataToSend.dateOfComm = $scope.data.dateOfComm.toJSON().split('T')[0]
    }
     if (typeof $scope.data.dateOfJoin == 'object') {
      dataToSend.dateOfJoin = $scope.data.dateOfJoin.toJSON().split('T')[0]
    }
    var method = 'POST';
    var url = '/api/HR/getUser/'
    // if ($scope.data.pk) {
    //   url += $scope.data.pk;
    // }
    $http({method : method , url : url , data : $scope.data}).
    then(function(response) {
      Flash.create('success' , 'New User Created');
        if (!$scope.data.pk) {
        $state.go('businessManagement.editUsers',{'id': response.data.pk})
      }
    })
  }




});




app.controller('controller.user.upload', function($scope, $http, $aside, $state, Flash, $users, $filter, $timeout, $uibModal) {

  $scope.bulkForm = {
    xlFile: emptyFile,
    success: false,
    usrCount: 0
  }
  $scope.upload = function() {
    if ($scope.bulkForm.xlFile == emptyFile) {
      Flash.create('warning', 'No file selected')
      return
    }
    $scope.locationData = window.location
    console.log($scope.bulkForm.xlFile);
    var fd = new FormData()
    fd.append('xl', $scope.bulkForm.xlFile);
    fd.append('locationData', $scope.locationData);
    console.log('*************', fd);
    $http({
      method: 'POST',
      url: '/api/HR/bulkUserCreation/',
      data: fd,
      transformRequest: angular.identity,
      headers: {
        'Content-Type': undefined
      }
    }).
    then(function(response) {
      Flash.create('success', 'Created');
      // $scope.bulkForm.usrCount = response.data.count;
      // $scope.bulkForm.success = true;
    })

  }

});
