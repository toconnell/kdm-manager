'use strict';   // See note about 'use strict'; below

var app = angular.module('kdmManager', ['ngRoute',]);

app.controller('globalController', function($scope, $http) {});

app.controller("epithetController", function($scope, $http) {
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
//        http.onload = function() {
//            alert(http.responseText);
//        }
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
//        http.onload = function() {
//            alert(http.responseText);
//        };

    }
});

