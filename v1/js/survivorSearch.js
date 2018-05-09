// survivor search - shows up in all views
app.controller ("survivorSearchController", function($scope) {

    // test a survivor object to see if a user can manage it
    $scope.userCanManage = function(s) {
        if ($scope.user_is_settlement_admin == true) { return true;}
        else if ($scope.user_login == s.email) { return true;}
        else { s._id = '';  return false };
        return false;
    };

});

