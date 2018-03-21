'use strict'; 



var myApp = angular.module('adminPanel', []);

myApp.filter('trustedHTML', function($sce) {return $sce.trustAsHtml;});

myApp.controller('globalController', function($scope, $http, $interval) {

    $scope.scratch = {};

    $scope.now = new Date();
    $scope.getAge = function(birthday){ //only does days for now
        var birthday = new Date(birthday);
        var age = $scope.now - birthday;
        return Math.round(age / (1000 * 60 * 60 * 24));
    };

    $scope.getEventLog = function(settlement) {
        for (var i=0; i < $scope.world.meta.admins.length; i++) {
            var admin_id = $scope.world.meta.admins[i]._id.$oid;
            var admin_login = $scope.world.meta.admins[i].login;
        };
        var url = '/settlement/get_event_log/' + settlement._id.$oid;
        settlement.event_log = [{event: 'Retrieving settlement Event Log as ' + admin_login + '...'}]
        $http.post(url, {user_id: admin_id}).then(function(result){
            settlement.event_log = result.data;
        });
    };
    $scope.showHide = function(e_id) {
        var e = document.getElementById(e_id);
        var hide_class = "hidden";
        var visible_class = "visible";
        if (e === null) {console.error("showHide('" + e_id + "') -> No element with ID value '" + e_id + "' found on the page!"); return false}
        if (e.classList.contains(hide_class)) {
            e.classList.remove(hide_class);
            e.classList.add(visible_class);
        } else {
            e.classList.add(hide_class);
            e.classList.remove(visible_class)
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
//        console.warn('[RECENT SETTLEMENTS] Getting recent settlements...');
        $http.get('game_asset/campaign').then(
            function(result){$scope.campaign_assets = result.data;},
            function(result){console.error('Could not retrieve campaign asset definitions!');}
        );
        $http.get('game_asset/expansion').then(
            function(result){$scope.expansion_assets = result.data;},
            function(result){console.error('Could not retrieve expansion asset definitions!');}
        );

        $scope.retrievingSettlements = true;
        $scope.showSpinner('recentSettlementsSpinner'); 
        $http.get('admin/get/settlement_data').then(function(result){
            $scope.settlements = result.data;
            $scope.hideSpinner('recentSettlementsSpinner');
            $scope.retrievingSettlements = false;
//            console.warn('[RECENT SETTLEMENTS] Got recent settlements!');
        });
    };

    setInterval( function init() {
//        console.log("[MAIN] Refreshing main view...")
        $scope.showSpinner('spinner');
        $http.get('settings.json').then(function(result){$scope.settings = result.data;});
        $http.get('https://api.github.com/repos/toconnell/kdm-manager').then(function(result){$scope.github = result.data;});

        if ($scope.retrievingSettlements != true){
//            console.warn('Not currently retrieving settlements. Starting retrieval...');
            $scope.getRecentSettlements();
        };

        $scope.showSpinner('userSpinner');
        $scope.scratch.get_user_data_failure = false;
        $http.get('admin/get/user_data').then(
            function(result){$scope.users = result.data; $scope.hideSpinner('userSpinner')},
            function(result){
                console.error('Could not retrieve recent user data!');
                console.error(result);
                $scope.hideSpinner('userSpinner');
                $scope.scratch.get_user_data_failure = true;
                $scope.scratch.get_user_data_failure_msg = result.data;
                $scope.users = undefined;
            }
        );
        $http.get('admin/get/logs').then(function(result){$scope.logs = result.data;});

        $http.get('world').then(function(result){
            $scope.world = result.data;
            $scope.hideSpinner('spinner');
            $scope.refreshed = new Date();
            $scope.seconds_since_last_refresh = 0;
//            console.log("[MAIN] Refreshed main view!");
            });

        return init;
        }(), 120000)




    $scope.copyToClipboard = function(text) {
        window.prompt("Copy User OID to clipboard:", text);
    };

    // initialize

//    window.setInterval($scope.initialize(), 5000);


});

myApp.controller('alertsController', function($scope, $http) {

    // initialize
    $scope.newAlert = {
        expiration: 'next_release',
        type: 'kpi',
        title: null,
        body: null,
        created_by: null,
    }

    // methods
    $scope.getWebappAlerts = function() {
        console.time('getWebappAlerts()');
        $http.get('admin/get/webapp_alerts').then(
            function(result){
                $scope.webappAlerts = result.data;
                console.timeEnd('getWebappAlerts()');
            },
            function(result){console.error('Could not retrieve webapp alerts!');}
        );
    };

    $scope.createAlert = function() {
        console.warn($scope.newAlert);
        $http.post("/admin/notifications/new", $scope.newAlert).then(function(result){
            console.warn(result);
            $scope.getWebappAlerts();
            $scope.newAlert.title = null;
            $scope.newAlert.body = null;
            $scope.newAlert.created_by = null;
            $scope.showHide('createNewAlert');
        });
    };

    $scope.expireAlert = function(a) {
        $http.post("/admin/notifications/expire", a).then(function(result){
            a.expiration = 'NOW';
            console.warn(result);
            $scope.getWebappAlerts();
        });
    };

})
