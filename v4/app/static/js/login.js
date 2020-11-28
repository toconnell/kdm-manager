app.controller("loginController", function($scope, $http) {

    $scope.setLatestRelease = function() {
        // sets $scope.latestRelease

        var reqURL = $scope.apiURL + 'releases/latest';
        console.time(reqURL);

        $http({
            method:'POST',
            url: reqURL,
            data: {'platform': 'kdm-manager.com'},
        }).then(
            function successCallback(response) {
                $scope.latestRelease = response.data;
                $scope.latestRelease.versionString =
                    $scope.latestRelease.version.major + "." +
                    $scope.latestRelease.version.minor + "." +
                    $scope.latestRelease.version.patch;
                console.info('Latest published release is: ' +
                    $scope.latestRelease.versionString
                );
                console.timeEnd(reqURL);
            }, function errorCallback(response) {
                console.error('Could not retrieve release info!');
                console.error(response);
                console.timeEnd(reqURL);
            }
        );
    };

    $scope.requestPasswordReset = function() {
		// sends a request to the API; shows a message if successful
		// OR failed

		$scope.ngHide('requestPasswordResetContainer');
        $scope.ngShow('requestPasswordResetSpinner');

        var reqURL = $scope.apiURL + 'reset_password/request_code';
        console.time(reqURL);

        $http({
            method: 'POST',
            url: $scope.apiURL + "reset_password/request_code",
        	data: {'username': $scope.resetPasswordRequest.email},
        }).then(
			function successCallback(response) {
                console.warn('Password reset request was successful!');
                $scope.ngShow('requestPasswordResetSuccessMessage');
                $scope.ngHide('requestPasswordResetSpinner');
				console.timeEnd(reqURL);
            }, function errorCallback(response) {
                $scope.resetPasswordRequest.badEmail = $scope.resetPasswordRequest.email;
                $scope.ngHide('requestPasswordResetSpinner');
				$scope.ngShow('requestPasswordResetContainer');
				$scope.ngHide('requestPasswordResetDefaultMessage');
				$scope.ngShow('requestPasswordResetErrorMessage');
				console.error('Password reset request was rejected!');
                console.error(response);
				console.timeEnd(reqURL);
            }
        ); 
    };

});
