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

    $scope.init = function(apiUrl, apiKey) {

        $rootScope.APIURL = apiUrl;
        $rootScope.APIKEY = apiKey;

		// this is the main init() call for the WHOLE APPLICATION, so we go a
		// bunch of critical stuff here, in terms of setting variables in the
		// uppermost $scope, etc.

		// first, get the JWT from the cookie (if present) and inject it into
		// the root scope, since all requests use it; create the CONFIG constant

		$scope.setJwtFromCookie();
		$rootScope.CONFIG = {
			'headers': {
				'Authorization': $rootScope.JWT,
				'API-Key': apiKey,
			}
		}

		// now, reach out to the API and get that into the root scope

        var statURL = $rootScope.APIURL + 'stat';
        console.time(statURL);

        $http({
            method:'GET',
            url: statURL,
        }).then(
            function successCallback(response) {
                $rootScope.apiStat = response.data;
                console.timeEnd(statURL);
                console.info(
                    'KDM API v' + $rootScope.apiStat.meta.api.version + ' @ ' + $rootScope.APIURL
                );
            }, function errorCallback(response) {
                $rootScope.apiStat = false;
                console.error('Could not stat API!');
                console.error(response);
                console.timeEnd(statURL);
            }
        );
    };

    $scope.setJwtFromCookie = function() {
		// injects the JWT into the root scope
        var cname = "kdm-manager_token";
        var name = cname + "=";
        var decodedCookie = decodeURIComponent(document.cookie);
        var ca = decodedCookie.split(';');
        for(var i = 0; i < ca.length; i++) {
        	var c = ca[i];
            while (c.charAt(0) == ' ') {
                c = c.substring(1);
            }
            if (c.indexOf('kdm-manager_token=') == 0) {
                $scope.sessionOID = c.substring('kdm-manager_token='.length, c.length);
            };
            if (c.indexOf(name) == 0) {
                $rootScope.JWT = c.substring(name.length, c.length);
                return true;
            };
        };

		// if we're still here, we've got problems
        console.error("Could not set JWT from cookie!");
        console.error(decodedCookie);
        $rootScope.JWT = null;
    };


    //
    //  UI/UX reusable JS section starts here
    //

    // aesthetic and UX prettiness stuff
    $rootScope.toTitle = function(str) {
        str = str.replace(/_/g, ' ');
        str = str.replace(/ and /g, ' & ');
        str = str.toLowerCase().split(' ');

        // turn it into a list to iterate it
        for (var i = 0; i < str.length; i++) {
            str[i] = str[i].charAt(0).toUpperCase() + str[i].slice(1);
        }

        // turn it back into a string now
        var norm_str = str.join(' ');

        // post processing/vanity stuff
        norm_str = norm_str.replace(/Xp/g, 'XP');
        norm_str = norm_str.replace(/Of/g, 'of');
        norm_str = norm_str.replace(/ The/g, ' the');
        return norm_str;
    };


    // ngVisible, ngHide, ngShow

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

    // roll up/down starts here

    $rootScope.ngRolledUp = {};
    $rootScope.getRollDownContainer = function(e_id) {
        var e = document.getElementById(e_id);
        if (e === null) {
            console.error("roll-up element '" + e_id + "' does not exist!");
            return;
        };
        return e
    };
    $rootScope.rollUp = function(e_id) {
        var e = $rootScope.getRollDownContainer(e_id);

        if (e.classList.contains('rolled_up') == true) {
            e.classList.remove('rolled_up');
            $rootScope.ngRolledUp[e_id] = false;
        } else {
            e.classList.add('rolled_up');
            $rootScope.ngRolledUp[e_id] = true;
        };
    };
    $rootScope.rollDown = function(e_id) {
        // forces an element into the down position
        var e = $rootScope.getRollDownContainer(e_id);
        e.classList.remove('rolled_up');
        $rootScope.ngRolledUp[e_id] = false;
    }


    //
    //  browsing and navigation helpers
    //
    $scope.loadURL = function(destination) {
       // allows us to use ng-click to re-direct to URLs
        window.location = destination;
    };


    //
    //  User asset retrival methods! These are GET-type methods only
    //


    //
    // misc. API methods below
    //

    $scope.setLatestRelease = function() {
        // sets $scope.latestRelease; present in the upper-most scope since
        // various views might call for it (for whatever dumbass reasons)

        var reqURL = $scope.APIURL + 'releases/latest';
        console.time(reqURL);

        $http({
            method:'POST',
            url: reqURL,
            data: {'platform': 'kdm-manager.com'},
        }).then(
            function successCallback(response) {
                $scope.latestRelease = response.data;
                $scope.latestRelease.versionString =
                    $scope.latestRelease.version.major + "." +
                    $scope.latestRelease.version.minor + "." +
                    $scope.latestRelease.version.patch;
                console.timeEnd(reqURL);
                console.info('Latest published release is: ' +
                    $scope.latestRelease.versionString
                );
            }, function errorCallback(response) {
                console.error('Could not retrieve release info!');
                console.error(response);
                console.timeEnd(reqURL);
            }
        );
    };

});
