'use strict'; 



var myApp = angular.module('adminPanel', []);


myApp.controller('globalController', function($scope, $http, $interval) {

    $scope.getEventLog = function(settlement) {
        for (var i=0; i < $scope.world.meta.admins.length; i++) {
            var admin_id = $scope.world.meta.admins[i]._id.$oid;
            var admin_login = $scope.world.meta.admins[i].login;
        };
        var url = '/settlement/get_event_log/' + settlement.sheet._id.$oid;
        settlement.event_log = [{event: 'Retrieving settlement Event Log as ' + admin_login + '...'}]
        $http.post(url, {user_id: admin_id}).then(function(result){
            settlement.event_log = result.data;
        });
    };
    $scope.showHide = function(e_id) {
        var element = document.getElementById(e_id);
        if (element.style.display=='block') {
            element.style.display='none'
        } else {
            element.style.display='block';
        };
    };

    $scope.showSpinner = function(id) {
        $("#" + id).fadeIn(3000);
    };
    $scope.hideSpinner = function(id) {
        $("#" + id).fadeOut(3000);
    };

    $scope.seconds_since_last_refresh = 0;
    $scope.updateCounter = function() {
        $scope.seconds_since_last_refresh++; 
    };
    $interval($scope.updateCounter, 1000);

    $scope.getRecentSettlements = function() {
        $scope.retrievingSettlements = true;
        $scope.showSpinner('recentSettlementsSpinner'); 
        $http.get('admin/get/settlement_data').then(function(result){
            $scope.settlements = result.data;
            $scope.hideSpinner('recentSettlementsSpinner');
            $scope.retrievingSettlements = false;
//            console.warn('Got recent settlements!');
        });
    };

    setInterval( function init() {
//        console.log("Initializing...")
        $scope.showSpinner('spinner');
        $http.get('settings.json').then(function(result){$scope.settings = result.data;});
        $http.get('https://api.github.com/repos/toconnell/kdm-manager').then(function(result){$scope.github = result.data;});

        if ($scope.retrievingSettlements != true){
//            console.warn('Not currently retrieving settlements. Starting retrieval...');
            $scope.getRecentSettlements();
        };
        $http.get('admin/get/user_data').then(function(result){$scope.users = result.data;});
        $http.get('admin/get/logs').then(function(result){$scope.logs = result.data;});

        $http.get('world').then(function(result){
            $scope.world = result.data;
            $scope.hideSpinner('spinner');
            $scope.refreshed = new Date();
            $scope.seconds_since_last_refresh = 0;
            });

        return init;
        }(), 60000)




    $scope.copyToClipboard = function(text) {
        window.prompt("Copy User OID to clipboard:", text);
    };

    // initialize

//    window.setInterval($scope.initialize(), 5000);


});

