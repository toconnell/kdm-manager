"use strict";

app.controller("settlementSheetController", function($scope, $rootScope, $http) {

    $scope.setSettlementAttribute = function(attribName) {
        // generic setter for settlement attributes; posts the current value of
        // the attrib back to the API

        var jsonObject = {};
        jsonObject[attribName] = $scope.settlement.sheet[attribName];
   
        $scope.postJSONtoAPI(
            'settlement',
            'set_milestones',
            $scope.settlement.sheet._id.$oid,
            jsonObject,
            false,
            true,
            true,
        );

    };

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
