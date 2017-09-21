var app = angular.module('login', []);

app.controller("globalController", function($scope) {

    $scope.hideControls = function(element_id) {
        var controls = document.getElementById(element_id);
        controls.classList.add('hidden');
    };

    $scope.showControls = function(element_id) {
        var controls = document.getElementById(element_id);
        controls.classList.remove('hidden');
    };

    $scope.showSignInControls = function() {
        $scope.hideControls('help_controls');
        $scope.hideControls('new_user_controls');
        $scope.showControls('sign_in_controls');
        document.getElementById("signInEmail").focus()
    };    

    $scope.showNewUserControls = function() {
        $scope.hideControls('sign_in_controls');
        $scope.hideControls('help_controls');
        $scope.showControls('new_user_controls');
        document.getElementById("newUserEmail").focus()
    };    

    $scope.showHelpControls = function() {
        $scope.showControls('help_controls');
        document.getElementById("resetPasswordEmail").focus()
    };    

    $scope.loading = function(action) {
        if (action === undefined) {
            $scope.hideControls('sign_in_controls');
            $scope.hideControls('new_user_controls');
            $scope.hideControls('help_controls');
            $scope.showControls('loading_spinner');
        } else {
            $scope.hideControls('loading_spinner');
            $scope.showControls('sign_in_controls');
        };
    };

    $scope.legacySignIn = function(un, pw) {
        // signs into the legacy webapp by emulating a form POST
        var form = document.createElement("form");
        form.method = "POST";
        form.action = "/";   

        var username = document.createElement("input"); 
        var password = document.createElement("input"); 

        username.name = 'login';
        username.value = un;
        username.classList.add('hidden');
        form.appendChild(username);

        password.name = 'password';
        password.value = pw;
        password.classList.add('hidden');
        form.appendChild(password);  

        document.body.appendChild(form);
        form.submit();

    };
});

app.controller("signInController", function($scope, $http) {
    $scope.signIn = function(api_url) {
        $scope.loading();
        var data = {username: $scope.signInEmail, password: $scope.signInPassword};
        $http({
            method: 'POST',
            url: api_url + "login",
            data: data,
        }).then(function successCallback(response) {
                var r = response.data;
                console.log("Authentication successful! Initiating legacy webapp sign-in...");
                $scope.legacySignIn($scope.signInEmail, $scope.signInPassword);
                return
            }, function errorCallback(response) {
                console.error(response.data);
                $scope.loading('off');
                if (response.status === -1) {
                    $scope.showControls('api_unavailable');
                } else {
                    $scope.showControls('sign_in_error');
                };
            });
        };

});

app.controller("newUserController", function($scope, $http) {
    $scope.register = function(api_url) {
        $scope.loading();
        if ($scope.newUserPassword !== $scope.newUserPasswordAgain) {
            $scope.showControls('pw_match_error');
            $scope.loading('off');
            $scope.showNewUserControls();
            return
        } else if ($scope.newUserEmail === undefined) {
            $scope.showControls('new_user_error');
            $scope.loading('off');
            var error_div = document.getElementById('new_user_error_alert');
            error_div.innerHTML = 'Please enter a valid email address!';
            $scope.showNewUserControls();
            return
        };
        // if we're still here after validation, attempt to register:
        var data = {username: $scope.newUserEmail, password: $scope.newUserPassword};
        console.log(data);
        $http({
            method: 'POST',
            url: api_url + "new/user",
            data: data,
        }).then(function successCallback(response) {
                var r = response.data;
                console.log(r);
                $scope.legacySignIn($scope.newUserEmail, $scope.newUserPassword);
                return
            }, function errorCallback(response) {
                var r = response.data;
                console.error(r);
                $scope.loading('off');
                var error_div = document.getElementById('new_user_error_alert');
                error_div.innerHTML = r.message;
                $scope.showControls('new_user_error');
            }
        );
    };
});

app.controller("resetPasswordController", function($scope, $http) {
    $scope.loading = function(action) {
        if (action === undefined) {
            $scope.hideControls('reset_password_controls');
            $scope.showControls('loading_spinner');
        } else {
            $scope.hideControls('loading_spinner');
            $scope.showControls('reset_password_controls');
        };
    };
    $scope.reset = function(api_url) {
        $scope.loading();
        if ($scope.newPassword !== $scope.newPasswordAgain) {
            $scope.showControls('pw_match_error');
            $scope.loading('off');
            $scope.showNewUserControls();
            return
        };
        var un = document.getElementById('resetPasswordEmail').value;
        var r_code = document.getElementById('recoveryCode').value;
        data = {
            'username': un,
            'password': $scope.newPassword,
            'recovery_code': r_code,
        }
        $http({
            method: 'POST',
            url: api_url + "reset_password/reset",
            data: data,
        }).then(function successCallback(response) {
                $scope.legacySignIn(un, $scope.newPassword);
            }, function errorCallback(response) {
                var r = response;
                console.error(r);
                var error_div = document.getElementById('help_error_alert');
                error_div.innerHTML = r.data;
                $scope.showControls('help_error');
                $scope.loading('off');
                return
            }
        );
    };
});

app.controller("helpController", function($scope, $http) {
    $scope.resetPassword = function(api_url) {
        $scope.loading();
        data = {'username': $scope.resetPasswordEmail};
        $http({
            method: 'POST',
            url: api_url + "reset_password/request_code",
            data: data,
        }).then(function successCallback(response) {
                $scope.loading('off');
                var r = response.data;
                var success_p = document.getElementById('successMessage');
                success_p.innerHTML = 'Am email containing further instructions has been sent to <b>' + $scope.resetPasswordEmail + '</b>.';
                $scope.showControls('help_success');
                return
            }, function errorCallback(response) {
                $scope.loading('off');
                var r = response;
                console.error(r);
                var error_div = document.getElementById('help_error_alert');
                error_div.innerHTML = r.data;
                $scope.showControls('help_error');
                return
            }
        );
    };
});




