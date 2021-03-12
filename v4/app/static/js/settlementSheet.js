"use strict";

app.controller("settlementSheetController", function($scope, $rootScope, $http) {

    $scope.loadSettlementMacros = function() {
        // sets $scope.settlementMacros based on values from the API

        var reqURL = $rootScope.APIURL + 'game_assets/macros';
        console.time(reqURL);

        $http({
            method:'GET',
            url: reqURL,
        }).then(
            function(payload) {
                $scope.settlementMacros = payload.data;
				console.timeEnd(reqURL);
            },
                function(errorPayload) {
                console.error("Failed to retrieve and set macros!");
                console.error(errorPayload);
				console.timeEnd(reqURL);
            }
        );
    };

}); // settlementSheetController ends
