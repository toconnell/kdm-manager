// srsly why does this have its own module

app.controller ("gearLookupController", function($scope) {
    $scope.loadGearLookup = function() {
        $scope.showCornerLoader();
        console.time('loadGearLookup()')
        var promise = $scope.getJSONfromAPI('settlement', 'gear_lookup', 'loadGearLookup()');
        promise.then(
            function(payload) {
                $scope.gearLookup = payload.data;
                console.timeEnd('loadGearLookup()');
                $scope.hideCornerLoader();
            },
            function(errorPayload) {console.log("Error loading settlement Gear lookup!" + errorPayload);}
        );

    };
});
