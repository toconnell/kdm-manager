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

    // primary init starts here; auth/token methods follow

    $scope.init = function(apiUrl, apiKey, requestEndpoint, user) {

        $rootScope.APIURL = apiUrl;
        $rootScope.APIKEY = apiKey;
        $rootScope.VIEW = requestEndpoint;
		$rootScope.USER = user;

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
                    $scope.flashCapsuleAlert('Exit', true);
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
    //  API methods and methods related to refreshing the view start here
    //


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


	// alerts and pop-ups
    $rootScope.flashCapsuleAlert = function(alertType, hold) {
        // we're going to show it, so add it to visible

        $rootScope.ngCapsuleAlert = {};
        $rootScope.ngCapsuleAlert.letter = alertType.substring(0,1);
        $rootScope.ngCapsuleAlert.text = alertType;
        $rootScope.ngCapsuleAlert.style = 'blue';

        if (alertType === 'Error') {
            $rootScope.ngCapsuleAlert.style = 'pink';
        } else if (alertType === 'Exit') {
            $rootScope.ngCapsuleAlert.style = 'black';
        };

        if (hold) {
            $scope.ngShow('capsuleAlertFlasher');
        } else {
            $scope.ngFlash('capsuleAlertFlasher', 700);
        };
    };


    // ngVisible, ngHide, ngShow

    $rootScope.ngVisible = {}

    $rootScope.ngGetElement = function(elementId) {
        // get an element from the page or die screaming about it
        var err_slug = "ngGetElement('" + elementId + "') ";
        try {
            var element = document.getElementById(elementId);
        } catch(err) {
            console.error(err);
        };
        if (element === null || element === undefined) {
            console.error(err_slug + " is " + element + "!");
            throw 'ngGetElement() failed!'
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
        // if lazy is boolean, we ignore the HTML and just force the element
        // to undef
        if (lazy) {
//            console.warn("Lazy ngHide for '" + elementId + "'");
            $rootScope.ngVisible[elementId] = undefined;
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

        // create a dictionary for flash watchers -OR- return if we're already
        // flashing/watching this element...
        if ($scope.eVisibleWatch === undefined) {
            $scope.eVisibleWatch = {}
        } else if ($scope.eVisibleWatch[elementId]) {
            return true;
        };

        $scope.eVisibleWatch[elementId] = $scope.$watch(
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
                            $scope.eVisibleWatch[elementId](); // unbind it
                            delete $scope.eVisibleWatch[elementId];
                        },
                        duration
                    );
                }
            }
        );

    };


	//
    // tabs!
	//
    $rootScope.tabsObject = {   // set object defaults
        previousTab: 0,
        activeTab: 0,
        minTab: 0,
    };

    $rootScope.getPrevNextTab = function() {
        var output = {}
        for (var i = 0; i < $scope.tabsObject.tabs.length; i++) {
            var tab = $scope.tabsObject.tabs[i];
            if ($scope.tabsObject.activeTab === tab.id) {
                output.previous = $scope.tabsObject.tabs[i - 1]
                output.current = tab;
                output.next = $scope.tabsObject.tabs[i + 1]
            }
        };
        return output
    };
    $rootScope.changeTab = function(destination) {
        // figures out if we're going up (right) or down (left) in tab order
        // and briefly displays an element with an arrow, indicating that
        // we're moving in that direction

        // set defaults
        if ($scope.tabsObject.previousTab === undefined) {
            console.error(
                '$scope.tabsObject.previousTab is not set! Defaulting to zero...'
            );
            $scope.tabsObject.previousTab = 0;
        }

        var p = $rootScope.getPrevNextTab()

        if (destination === 'previous') {
            if (p.previous === undefined) {
                destination = $scope.tabsObject.activeTab
            } else {
                destination = p.previous.id;
            };
        } else if (destination === 'next') {
            if (p.next === undefined) {
                destination = $scope.tabsObject.activeTab
            } else {
                destination = p.next.id;
            };
        } else if (destination === undefined) {
            destination = 666;
        }

        // sanity check destination
        if (destination < $scope.tabsObject.minTab) {
            destination = $scope.tabsObject.minTab
        };

        $scope.tabsObject.activeTab = destination;

        // now determine direction
        var direction = 'right';
        if (destination < $scope.tabsObject.previousTab) {
            direction = 'left';
        } else if (destination === $scope.tabsObject.previousTab) {
            direction = null;
        };

        if (direction === 'right') {
            $scope.ngFlash('tabNavArrowRight', 300);
        } else if (direction === 'left') {
            $scope.ngFlash('tabNavArrowLeft', 300);
        } else {
            $scope.ngFlash('tabNavArrowNull', 300);
        };

        // now, leave a var in scope so we know
        $scope.tabsObject.previousTab = destination;
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




	// angular debugger
    document.addEventListener ("keydown", function (zEvent) {
        if (zEvent.ctrlKey  &&  zEvent.altKey  &&  zEvent.key === "d") {  // case sensitive
            var e = document.getElementById('ngDebugWindow')
            if ($rootScope.NGDEBUG === true) {
                e.classList.add('hidden')
                console.warn('Debug mode disabled!')
                $rootScope.NGDEBUG = undefined;
            } else {
                e.classList.remove('hidden')
                console.warn('Debug mode enabled!')
                $rootScope.NGDEBUG = true;
            };
        };
    } );



    //
    //  API methods below - this is where the magic happens
    //

    $rootScope.postJSONtoAPI = function(
			collection, action, objectOid,
			jsonObj = {},
			reinit = true,
			showAlert = true,
			updateSheet = false,
		) 
		{
		// welcome to the new version of postJSONtoAPI()!
		// This workhorse method has been broken into components and refactored
		// for readability. It behaves differently to the original/legacy
		// implementation, so proceed with caution!

		// first, if we're doing on-screen alerts, show the small loader
	    if (showAlert) {
            $scope.ngFlash('cornerSpinner', 500);
        };

		// sanity checks
		const requiredArgs = [collection, action, objectOid, jsonObj]
		requiredArgs.forEach(function (arg, index) {
			if (arg === undefined) {
				throw 'postJSONtoAPI() -> Required variable is undefined!';
			};
		});

		// echo the call back to the log
		if ($scope.NGDEBUG) {
			var methodDesc = $scope.argsToString([
				collection, action, objectOid, jsonObj, reinit, showAlert, updateSheet
			])
    	    console.info('postJSONtoAPI' + methodDesc);
		};

        // always serialize on response, regardless of asset type
        jsonObj.serialize_on_response = true;

        // create the URL and do the POST
        var endpoint = collection + "/" + action + "/" + objectOid;
        var url = $rootScope.APIURL + endpoint;

		console.time(endpoint);
        var promise = $http.post(url, jsonObj, $rootScope.CONFIG);

		promise.then(
			function successCallback(response) {
				if (showAlert) { $rootScope.flashCapsuleAlert('Saved') };
				console.timeEnd(endpoint);
			},
			function errorCallback(response) {
                console.error('postJSONtoAPI() failed!');
                if (response.data) {
                    console.error(response.data);
                } else {
                    console.error(response);
                };
				console.timeEnd(endpoint);
			}	
		);

		return promise;

	}; // end of postJSONtoAPI()!


    //
    // initializeSettlement
    //

    $scope.initializeSettlement = function(settlementOID) {

        // the legacy/v3 way of initializing a settlement with a mind to 
        // presenting the user a version of the serialized settlement
		// appropriate for the current $rootScope.VIEW
		// 'requestPath' is something like /settlement/<oid>

		if (!settlementOID) {
			throw "intitializeSettlement() requires 'settlementOID' arg!";
		};


        var getAction = 'get'
        if ($rootScope.VIEW === 'campaign_summary') {
            getAction = 'get_campaign';
        };

		var reqURL = $rootScope.APIURL + 'settlement/' + getAction + '/' + settlementOID;
		console.time(reqURL);

        var promise = $http.get(reqURL, $rootScope.CONFIG);

		promise.then(
			function successCallback(response) {
                $scope.settlement = response.data;
                console.timeEnd(reqURL);
                $scope.ngHide('fullPageLoader'); // in case it's showing
			},
			function errorCallback(response) {
                console.error('Could not retrieve settlement from API!');
                console.error(response);
                console.timeEnd(reqURL);
				if (response.status === 401 || response.status === 403) {
        			window.location = '/unauthorized/' + response.status;
				}
			}	
		);

    }; // initializeSettlement end




    // set methods
    $rootScope.setApiAlerts = function() {
        // gets all of Kingdom Death from the API; hangs it on 
        // $rootScope.kingdomDeath

        var reqURL = $rootScope.APIURL + 'get/notifications';
        console.time(reqURL);
        
        $http({
            method:'GET',
            url: reqURL,
        }).then(
            function successCallback(response) {
                $scope.apiAlerts = response.data;
                console.timeEnd(reqURL);
            }, function errorCallback(response) {
                console.error('Could not retrieve API alerts!');
                console.error(response);
                console.timeEnd(reqURL);
            }
        );
    };

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

    $rootScope.setKingdomDeath = function() {
        // gets all of Kingdom Death from the API; hangs it on 
        // $rootScope.kingdomDeath

        var reqURL = $rootScope.APIURL + 'kingdom_death';
        console.time(reqURL);
        
        $http({
            method:'GET',
            url: reqURL,
        }).then(
            function successCallback(response) {
                $rootScope.kingdomDeath = response.data;
                console.timeEnd(reqURL);
            }, function errorCallback(response) {
                console.error('Could not set $rootScope.kingdomDeath!');
                console.error(response);
                console.timeEnd(reqURL);
            }
        );
    };

    $rootScope.setSettlementMacros = function() {
        // gets all of Kingdom Death from the API; hangs it on 
        // $rootScope.kingdomDeath

        var reqURL = $rootScope.APIURL + 'game_asset/macros';
        console.time(reqURL);
        
        $http({
            method:'GET',
            url: reqURL,
        }).then(
            function successCallback(response) {
                $rootScope.settlementMacros = response.data;
                console.timeEnd(reqURL);
            }, function errorCallback(response) {
                console.error('Could not set $rootScope.settlementMacros!');
                console.error(response);
                console.timeEnd(reqURL);
            }
        );
    };


    $rootScope.setLatestRelease = function(force) {
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

    
    $scope.setWebappHelp = function() {
        // sets $scope.webappHelp to be our help JSON from the v4 app

        var reqURL = '/assets/help';
        console.time(reqURL);
        
        $http({
            method:'GET',
            url: reqURL,
        }).then(
            function successCallback(response) {
                $scope.webappHelp = response.data;
                console.timeEnd(reqURL);
            }, function errorCallback(response) {
                console.error('Could not retrieve webapp help!');
                console.error(response);
                console.timeEnd(reqURL);
            }
        );
    };

    // nav and control methods, i.e. that need to be accessible everywhere

    $rootScope.submitErrorReport = function(content) {
        // hits the API's /report_error endpoint
		
        var reqURL = $rootScope.APIURL + 'report_error';
		console.time(reqURL);

        var promise = $http.post(reqURL, {'value': content}, $rootScope.CONFIG);

		promise.then(
			function successCallback(response) {
                $scope.ngHide('reportErrorForm');
                $scope.ngShow('reportErrorConfirmation');
                console.timeEnd(reqURL);
			},
			function errorCallback(response) {
                console.error('Failed to POST error report to API!');
                console.error(response);
                console.timeEnd(reqURL);
				if (response.status === 401 || response.status === 403) {
        			window.location = '/unauthorized/' + response.status;
				} else {
                    $scope.ngHide('reportErrorForm');
                    $scope.ngShow('reportErrorFailure');
                };
			}	
		);
        
    };




	//
	//	utilities / junk
	//

	$rootScope.argsToString = function(argList) {
		// takes a list of arguments, turns their values into a str
		var output = '(';
		argList.forEach(function (arg, index) {
			output += "'" + arg + "'";
			if (index !== argList.length -1) {
				output += ', ';
			};
		});
        output += ')';
		return output;
	};

    $rootScope.toggleArrayItem = function(list, item) {
        // pushes 'item' onto 'list' if not present; splices it out if
        // present

        var index = list.indexOf(item);
        if (index === -1) {
            list.push(item);
        } else {
            list.splice(index, 1);
        };
    };

});
