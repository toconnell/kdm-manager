
// survivor search

app.controller ("survivorSearchController", function($scope) {

    $scope.loadSurvivors = function() {
        $scope.loadSettlement().then(
            function(payload) {
                var all_survivors = payload.data.user_assets.survivors;
                $scope.survivors = new Array();
                for (i=0; i < all_survivors.length; i++) {
                    var survivor = all_survivors[i];
                    $scope.survivors.push(survivor.sheet);
                }
                console.log($scope.survivors.length + " survivors loaded into scope!");
            },
            function(errorPayload) {console.log("Error loading survivors for survivor search!", errorPayload);}
        );
    };

    // test a survivor object to see if a user can manage it
    $scope.userCanManage = function(s) {
        if ($scope.user_is_settlement_admin == true) { return true;}
        else if ($scope.user_login == s.email) { return true;}
        else { s._id = ''; return false };
        return s._id = ''; false;
    };

});


// endeavor token app

app.controller("endeavorController", function($scope) {

    $scope.addToken = function(){
        var params = "endeavor_tokens=1";
        modifyAsset("settlement", $scope.settlement_id, params);
        $scope.endeavors += 1;
    };

    $scope.rmToken = function(){
        var params = "endeavor_tokens=-1";
        modifyAsset("settlement", $scope.settlement_id, params);
        $scope.endeavors -= 1;
        if ($scope.endeavors <= 0) {$scope.endeavors = 0;};
    };

});

