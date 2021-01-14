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

    $scope.init = function(apiUrl, apiKey, requestEndpoint) {

        $rootScope.APIURL = apiUrl;
        $rootScope.APIKEY = apiKey;
        $rootScope.VIEW = requestEndpoint;

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

                // finally, if we can't stat the API on a non-login/-logout type
                // of view, then we shit-can the whole thing and log the user
                // out: this protects us from trying to load a view when the API
                // is gone for whatever reason
                if ($rootScope.VIEW === 'login' || $rootScope.VIEW == 'logout') {
                    console.warn('Not attempting automatic log-out...');
                } else {
                    console.error('Logging out...');
                    $rootScope.loadURL("/logout");
                };

            }
        );
    };

    $rootScope.setJwtFromCookie = function() {
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
                $rootScope.sessionOID = c.substring('kdm-manager_token='.length, c.length);
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

    $rootScope.ngGetElement = function(elementId) {
        // get an element from the page or die screaming about it
        var err_slug = "ngGetElement(): ID '" + elementId;
        try {
            var element = document.getElementById(elementId);
        } catch(err) {
            console.error(err);
            throw err_slug + "' not found!";
        };
        if (element === null || element === undefined) {
            throw err_slug + "' is " + element + "!";
        };
        return element;
    };

    $rootScope.ngShow = function(elementId) {
        // for legacy compatibility: wait until the $digest finishes, then
        // get the element (it won't be present until the $digest is updated
        // after the ngVisible change above);
        var eWatch = $scope.$watch(
            function() {
                $rootScope.ngVisible[elementId] = true;
                return document.getElementById(elementId)
            },
            function(newValue, oldValue, scope) {
                if (oldValue !== newValue) {
                    newValue.classList.remove('hidden');
                    eWatch(); // unbind it
                }
            }
        )
    };

    $rootScope.ngHide = function(elementId, lazy) {
        if (lazy) {
            console.warn("Lazy ngHide for '" + elementId + "'")
        } else {
            var element = $rootScope.ngGetElement(elementId);
            element.classList.add('hidden');
        };
        $rootScope.ngVisible[elementId] = false;
    }

    $rootScope.ngShowHide = function(elementId) {
        // supersedes showHide(), which is deprecated
        // toggles an element in and out of $rootScope.ngVisible, which is
        //  an arry of UI elements that are true or false

        if ($rootScope.ngVisible[elementId] === true) {
            $rootScope.ngHide(elementId);
        } else {
            $rootScope.ngShow(elementId);
        };

    };

    $rootScope.ngFlash = function(elementId, duration) {
        // shows an element; sleeps for 'duration'; takes the element out of
        // ngVisible list.
        // works a bit like ngShow(), but uses $timeout to sleep for 'duration'
        // before updating the ngVisible dict
        if (duration === undefined) {
            duration = 3000;
        };

        var eVisibleWatch = $scope.$watch(
            function() {
                $rootScope.ngVisible[elementId] = true;
                return document.getElementById(elementId)
            },
            function(newValue, oldValue, scope) {
                if (oldValue !== newValue) {
                    newValue.classList.remove('hidden');
                    $timeout(
                        function() {
                            $rootScope.ngVisible[elementId] = false;
                            eVisibleWatch(); // unbind it
                        },
                        duration
                    );
                }
            }
        );

    };

	//
    // roll up/down starts here
	//

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
    $rootScope.loadURL = function(destination) {
       // allows us to use ng-click to re-direct to URLs
        window.location = destination;
    };


    //
    //  User asset retrival methods! These are GET-type methods only
    //
    $rootScope.setExpansionAssets = function(force) {
		// sets $rootScope.expansionAssets from the API

		// first, just end and return if it's already set and we're not
		// using 'force' to demand a reload/reset
		if ($rootScope.expansionAssets !== undefined && force !== true) {
			console.warn('Expansion content already loaded!');
			return true
		};
        
		// now do it
		var reqUrl = $rootScope.APIURL + 'game_asset/expansions';
		console.time(reqUrl);
		$http.get(reqUrl).then(
            function successCallback(response) {
                $rootScope.expansionAssets = response.data;
                console.timeEnd(reqUrl);
            },
            function errorCallback(response) {
                console.error("Could not retrieve expansions!");
                console.error(response);
                console.timeEnd(reqUrl);
            }
        );
    };


    //
    // misc. API methods below
    //

    $scope.setLatestRelease = function(force) {
        // sets $rootScope.latestRelease; present in the upper-most scope since
        // various views might call for it (for whatever dumbass reasons)

		if ($rootScope.latestRelease !== undefined && force !== true) {
			console.warn('Latest release already set!');
			return true
		};

        var reqURL = $rootScope.APIURL + 'releases/latest';
        console.time(reqURL);

        $http({
            method:'POST',
            url: reqURL,
            data: {'platform': 'kdm-manager.com'},
        }).then(
            function successCallback(response) {
                $rootScope.latestRelease = response.data;
                $rootScope.latestRelease.versionString =
                    $rootScope.latestRelease.version.major + "." +
                    $rootScope.latestRelease.version.minor + "." +
                    $rootScope.latestRelease.version.patch;
                console.timeEnd(reqURL);
                console.info('Latest published release is: ' +
                    $rootScope.latestRelease.versionString
                );
            }, function errorCallback(response) {
                console.error('Could not retrieve release info!');
                console.error(response);
                console.timeEnd(reqURL);
            }
        );
    };

});
