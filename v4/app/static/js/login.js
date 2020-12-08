app.controller("loginController", function($scope, $http) {

    $scope.resetPasswordRequest = {};

    $scope.requestPasswordReset = function() {
		// sends a request to the API; shows a message if successful
		// OR failed

		$scope.ngHide('requestPasswordResetContainer');
        $scope.ngHide('requestPasswordResetDefaultMessage')
        $scope.ngShow('lanternLoading');

        var reqURL = $scope.APIURL + 'reset_password/request_code';
        console.time(reqURL);

        $http({
            method: 'POST',
            url: $scope.APIURL + "reset_password/request_code",
        	data: {'username': $scope.resetPasswordRequest.email},
        }).then(
			function successCallback(response) {
                console.warn('Password reset request was successful!');
                $scope.resetPasswordRequest.successful = true;
                $scope.ngHide('lanternLoading');
				console.timeEnd(reqURL);
            }, function errorCallback(response) {
                $scope.resetPasswordRequest.badEmail = $scope.resetPasswordRequest.email;
                $scope.ngHide('lanternLoading');
				$scope.ngShow('requestPasswordResetContainer');
				$scope.ngShow('requestPasswordResetErrorMessage');
				console.error('Password reset request was rejected!');
                console.error(response);
				console.timeEnd(reqURL);
            }
        ); 
    };

});
