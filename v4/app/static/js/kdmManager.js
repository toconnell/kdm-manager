"use strict";

var app = angular.module('kdmManager', ['ngAnimate']);

// avoid clashes with jinja2
app.config(['$interpolateProvider', function($interpolateProvider) {
    $interpolateProvider.startSymbol('{a');
    $interpolateProvider.endSymbol('a}');
}]);

// HTML insertion
app.filter(
    'trustedHTML', function($sce) { return $sce.trustAsHtml; }
);

app.controller('rootScopeController', function($scope, $rootScope, $http, $timeout) {

    $scope.init = function(apiURL) {

		// this is the main init() call for the WHOLE APPLICATION, so we go a
		// bunch of critical stuff here, in terms of setting variables in the
		// uppermost $scope, etc.

        $rootScope.apiURL = apiURL;
        var statURL = $rootScope.apiURL + 'stat';
        console.time(statURL);

        $http({
            method:'GET',
            url: statURL,
        }).then(
            function successCallback(response) {
                $rootScope.apiStat = response.data;
                console.info(
                    'KDM API v' + $rootScope.apiStat.meta.api.version + ' @ ' + $rootScope.apiURL
                );
                console.timeEnd(statURL);
            }, function errorCallback(response) {
                $rootScope.apiStat = false;
                console.error('Could not stat API!');
                console.error(response);
                console.timeEnd(statURL);
            }
        );
    };

    //
    //  UI/UX reusable JS section starts here
    //

    $rootScope.ngVisible = {}

    $rootScope.ngShow = function(elementId) {

        $rootScope.ngVisible[elementId] = true;

        // for legacy compatibility: wait until the $digest finishes, then
        // get the element (it won't be present until the $digest is updated
        // after the ngVisible change above);

        $timeout(
            function() {
                try {
                    var e = document.getElementById(elementId);
                    e.classList.remove('hidden');
                } catch(err) {
                    console.error(err);
                };
           }
        );
    };

    $rootScope.ngHide = function(elementId) {
        try {
            var e = document.getElementById(elementId);
            e.classList.add('hidden');
        } catch(err) {
            console.error(err);
        };
        $rootScope.ngVisible[elementId] = false;
    }

    $rootScope.ngShowHide = function(elementId) {
        // calls ngShow or ngHide against an element based on whether it is
		// 	currently a member of ngVisible

        if ($rootScope.ngVisible[elementId] === true) {
            $rootScope.ngHide(elementId);
        } else {
            $rootScope.ngShow(elementId);
        };

    };


    //
    //  browsing and navigation helpers
    //
    $scope.loadURL = function(destination) {
       // allows us to use ng-click to re-direct to URLs
        window.location = destination;
    };

});
