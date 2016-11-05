'use strict';   // See note about 'use strict'; below

var app = angular.module('kdmManager', ['ngRoute',]);



app.controller('globalController', function($scope, $http) {});

app.controller("epithetController", function($scope) {
    $scope.epithets = [];
    $scope.formData = {};
    $scope.addItem = function (asset_id) {
        $scope.errortext = "";
        if (!$scope.addMe) {return;}
        if ($scope.epithets.indexOf($scope.addMe) == -1) {
            $scope.epithets.push($scope.addMe);
        } else {
            $scope.errortext = "The epithet has already been added!";
        };

        var http = new XMLHttpRequest();
        http.open("POST", "/", true);
        http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        var params = "add_epithet=" + $scope.addMe + "&modify=survivor&asset_id=" + asset_id
        http.send(params);

        $('#saved_dialog').show();
        $('#saved_dialog').fadeOut(1500)
    }
    $scope.removeItem = function (x, asset_id) {
        $scope.errortext = "";
        var removedEpithet = $scope.epithets[x];
        $scope.epithets.splice(x, 1);
        var http = new XMLHttpRequest();
        http.open("POST", "/", true);
        http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        var params = "remove_epithet=" + removedEpithet + "&modify=survivor&asset_id=" + asset_id;
        http.send(params);

        $('#saved_dialog').show();
        $('#saved_dialog').fadeOut(1500)

    }
});

// name change func. Going here instead of head
function updateSurvivorName(asset_id) {
    var new_name = document.getElementById("survivor_sheet_survivor_name").value;

    var http = new XMLHttpRequest();
    http.open("POST", "/", true);
    http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    var params = "name=" + new_name + "&modify=survivor&asset_id=" + asset_id
    http.send(params);

    $('#saved_dialog').show();
    $('#saved_dialog').fadeOut(1500)

};
