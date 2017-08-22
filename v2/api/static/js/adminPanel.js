'use strict'; 


var myApp = angular.module('adminPanel', []);


myApp.controller('globalController', function($scope, $http) {

    $scope.showSpinner = function() {
        $("#spinner").fadeIn(3000);
    };
    $scope.hideSpinner = function() {
        $("#spinner").fadeOut(3000);
    };

    setInterval( function init() {
        console.log("Initializing...")
        $scope.showSpinner();
        $http.get('settings.json').then(function(result){$scope.settings = result.data;});
        $http.get('https://api.github.com/repos/toconnell/kdm-manager').then(function(result){$scope.github = result.data;});

        $http.get('admin/get/active_users').then(function(result){$scope.active_users = result.data;});
        $http.get('admin/get/logs').then(function(result){$scope.logs = result.data;});

        $http.get('world').then(function(result){
            $scope.world = result.data;
            $scope.hideSpinner();
            $scope.refreshed = new Date();
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


    // initialize

//    window.setInterval($scope.initialize(), 5000);


});

