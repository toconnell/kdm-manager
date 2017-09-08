'use strict'; 



var myApp = angular.module('adminPanel', []);


myApp.controller('globalController', function($scope, $http, $interval) {

    $scope.showSpinner = function() {
        $("#spinner").fadeIn(3000);
    };
    $scope.hideSpinner = function() {
        $("#spinner").fadeOut(3000);
    };

    $scope.seconds_since_last_refresh = 0;
    $scope.updateCounter = function() {
        $scope.seconds_since_last_refresh++; 
    };
    $interval($scope.updateCounter, 1000);

    setInterval( function init() {
//        console.log("Initializing...")
        $scope.showSpinner();
        $http.get('settings.json').then(function(result){$scope.settings = result.data;});
        $http.get('https://api.github.com/repos/toconnell/kdm-manager').then(function(result){$scope.github = result.data;});

        $http.get('admin/get/user_data').then(function(result){$scope.users = result.data;});
        $http.get('admin/get/logs').then(function(result){$scope.logs = result.data;});

        $http.get('world').then(function(result){
            $scope.world = result.data;
            $scope.hideSpinner();
            $scope.refreshed = new Date();
            $scope.seconds_since_last_refresh = 0;
            });

        return init;
        }(), 60000)


    $scope.showHide = function(e_id) {
        var element = document.getElementById(e_id); 
        if (element.style.display=='block') {
            element.style.display='none'
        } else {
            element.style.display='block';
        };
    };


    $scope.copyToClipboard = function(text) {
        window.prompt("Copy User OID to clipboard:", text);
    };

    // initialize

//    window.setInterval($scope.initialize(), 5000);


});

