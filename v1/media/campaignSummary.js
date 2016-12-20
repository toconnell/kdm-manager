
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


app.controller("manageDepartingSurvivorsController", function($scope) {
    $scope.saveCurrentQuarry = function(select_element) {
        $scope.postJSONtoAPI('settlement', 'set', {"current_quarry": $scope.current_quarry});

        var timeline_event = {
            "name": $scope.current_quarry,
            "ly": $scope.current_ly,
            "user_login": $scope.user_login
        };

        if ($scope.arrayContains($scope.current_quarry, $scope.settlement.game_assets.showdown_options)) {
            timeline_event.type = 'showdown_event';
        } else if ($scope.arrayContains($scope.current_quarry, $scope.settlement.game_assets.nemesis_encounters)) {
            timeline_event.type = 'nemesis_encounter';
        } else if ($scope.arrayContains($scope.current_quarry, $scope.settlement.game_assets.special_showdown_options)) {
            timeline_event.type = 'special_showdown';
        };

        $scope.addEvent(timeline_event["ly"],timeline_event["type"],timeline_event["name"]);
    };    
});
