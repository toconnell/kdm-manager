// alerts -> call these anywhere

function savedAlert() {
    $('#saved_dialog').fadeIn(500);
    $('#saved_dialog').show();
    $('#saved_dialog').fadeOut(1800);
};
function errorAlert() {
    $('#error_dialog').fadeIn(500);
    $('#error_dialog').show();
    $('#error_dialog').fadeOut(5000);
};

// loaders -> call these anywhere

function showFullPageLoader()   {$('#fullPageLoader').show();};
function hideFullPageLoader()   {$('#fullPageLoader').fadeOut(1000);};
function showCornerLoader()     {$('#cornerLoader').show();};
function hideCornerLoader()     {$('#cornerLoader').fadeOut(1000);};


function showAPIerrorModal(msg, request) {
    e = document.getElementById('apiErrorModal');
    e.classList.remove('hidden');
    r = document.getElementById('apiErrorModalMsgRequest');
    r.innerHTML = request;
    m = document.getElementById('apiErrorModalMsg');
    m.innerHTML = msg;
};
function hideAPIerrorModal() {
    e = document.getElementById('apiErrorModal');
    e.classList.add('hidden');
};

// public helpers
function rollUp(e_id) {
    var e = document.getElementById(e_id);
    if (e.classList.contains('rolled_up') == true) {
        e.classList.remove('rolled_up');
    } else {
        e.classList.add('rolled_up');
    };
};

function showHide(e_id) {
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
 }

// burger sidenav
function openNav() {
    var nav = document.getElementById("mySidenav")
    nav.style.width = '75%';
}
function closeNav() {
    var nav = document.getElementById("mySidenav");
    if (nav === null){
    } else {
        nav.style.width = "0"
    };
}

function sleep (time) {return new Promise((resolve) => setTimeout(resolve, time));}

function convertMS(millis) {
  var minutes = Math.floor(millis / 60000);
  var seconds = ((millis % 60000) / 1000).toFixed(0);
  return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
};



//
//      The angular application starts here!
//

var app = angular.module('kdmManager', []);

//  directives for that ass
app.directive('customOnChange', function() {
  return {
    restrict: 'A',
    link: function (scope, element, attrs) {
      var onChangeFunc = scope.$eval(attrs.customOnChange);
      element.bind('change', onChangeFunc);
    }
  };
});



// general-use filters and other AngularJS bric-a-brack
app.filter('trustedHTML', 
   function($sce) {
      return $sce.trustAsHtml; 
   }
);

app.filter('flatten' , function(){
  return function(array){
    return array.reduce(function(flatten, group){
      group.items.forEach(function(item){
        flatten.push({ group: group.name , name: item.name})
      })
      return flatten;
    },[]);
  }
})

app.filter('orderObjectBy', function() {
  return function(items, field, reverse) {
    var filtered = [];
    angular.forEach(items, function(item) {
      filtered.push(item);
    });
    filtered.sort(function (a, b) {
      return (a[field] > b[field] ? 1 : -1);
    });
    if(reverse) filtered.reverse();
    return filtered;
  };
});




app.controller('rootController', function($scope, $rootScope, $http, $log) {
    $scope.$log = $log;
    $scope.scratch = {}
    $scope.scratch.settlementsRetrieved = 0;

    $rootScope.setView = function(view) {
        $rootScope.view = view;
        $scope.view = view;
//        console.warn("$rootScope.setView('" + view + "')");
    };

    // initialize rootScope elements here; these are set on every view
    $rootScope.showHide = showHide;
    $scope.numberToRange = function(num) {
        return new Array(num); 
    };

    $rootScope.openNav = function(e) {
        var element = document.getElementById(e);
        element.classList.add('openNav');
    };
    $rootScope.closeNav = function(e) {
        var element = document.getElementById(e);
        element.classList.remove('openNav');
    };

    // post a form to the legacy webapp (useful for buttons that you
    // want to behave like a form
    $scope.postForm = function(action, asset_id) {

        var form = document.createElement("form");
        form.method = "POST";
        form.action = "/";

        var a_input = document.createElement("input");

        a_input.name = action;
        a_input.value =  asset_id;
        a_input.classList.add('hidden');
        form.appendChild(a_input);

        document.body.appendChild(form);
        form.submit();
    };


    // new settlement assets
    $scope.addNewSettlementsToScope = function(api_url) {
        console.time('addNewSettlementsToScope()');
        $scope.newSettlementPromise = $http.get(api_url + 'new_settlement');
        $scope.newSettlementPromise.then(
            function(payload) {
                $scope.new_settlement_assets = payload.data;
                console.timeEnd('addNewSettlementsToScope()');         
            },
            function(errorPayload) {console.log("Error loading new settlement assets!" + errorPayload);}
        );
    };

    //
    // methods below here
    //

    $scope.legacySignOut = function(session_oid) {;
        console.warn("Attempting legacy sign-out...");

        // signs into the legacy webapp by emulating a form POST
        var form = document.createElement("form");
        form.method = "POST";
        form.action = "/";

        var rm = document.createElement("input");

        rm.name = 'remove_session';
        rm.value =  session_oid;
        rm.classList.add('hidden');
        form.appendChild(rm);

        document.body.appendChild(form);
        form.submit();
    }

    $scope.initWorld = function() {

        console.time('initWorld()');
        setInterval( function init() {
            
            showCornerLoader();
            var world_url = $scope.api_url + "world";
            $http.get(world_url).then(
                function(result) {
                    $scope.world = result.data.world;
                    hideCornerLoader();
                    console.log('[WORLD] Retrieved data successfully!')
                    console.timeEnd('initWorld()');
                }
            );

            return init;
            }(), 180000)

    };

    $scope.initLostSettlementsControls = function() {
        $scope.lost_settlements = $scope.settlement.sheet.lost_settlements;
        $scope.current_val = $scope.lost_settlements
        $scope.lost = [];

        // build the first elements in the control array
        for (var i = 0; i < $scope.current_val; i++) {
           $scope.lost.push({'class': 'lost_settlement_checked', 'id_num': i})
        };

        // now, based on what we've got, build the rest of the array
        do {
            if ($scope.lost.length == 4)
                {$scope.lost.push({'class': 'bold_check_box', 'id_num':4})}
            else if ($scope.lost.length == 9)
                {$scope.lost.push({'class': 'bold_check_box', 'id_num':9})}
            else if ($scope.lost.length == 14)
                {$scope.lost.push({'class': 'bold_check_box', 'id_num':14})}
            else if ($scope.lost.length == 18)
                {$scope.lost.push({'class': 'bold_check_box', 'id_num':18})}
            else
                {$scope.lost.push({'id_num':$scope.lost.length})};
        } while ($scope.lost.length < 19) ;

        console.log("lost_settlements control array initialized!");
    };


    $scope.getSettlement = function(s_dict, dest, context){
        // pass in a string of a settlement OID to push a settlement onto array
        // 'dest'

        console.time('getSettlement(' + s_dict['name'] + ', ' + context + ')');
        showCornerLoader();
        var config = {"headers": {"Authorization": $scope.jwt}};

        var s_id = s_dict._id.$oid;
        var s_json = {sheet: s_dict};

        // push the bogus/partial settlement into the dest array and get its index
        dest.push(s_json);
        var s_index = dest.indexOf(s_json);

        // now spint off a job to get the rest of the settlement info and update
        $http.get($scope.api_url + 'settlement/get_summary/' + s_id, config).then(
            function(payload) {
//                dest.push(payload.data);
                dest[s_index] = payload.data;
                $scope.scratch.settlementsRetrieved += 1;
                console.timeEnd('getSettlement(' + s_dict['name'] + ', ' + context + ')');
            },
            function(errorPayload) {
                console.error("[rootController.getSettlement()] Could not get settlement " + s_id);
                console.error(errorPayload);
            }
        );
    };

    $scope.initializeUser = function(u_id, user_endpoint, api_url){
        // initialize
        console.time('initializeUser()');
        if ($scope.user_id === undefined && u_id !== undefined) {
            $scope.user_id = u_id;
        }
        if (user_endpoint === undefined){
            user_endpoint = 'get';
        };
        if ($scope.api_url === undefined && api_url !== undefined) {
            $scope.api_url = api_url;
        };

        console.log("[USER] Initializing user " + $scope.user_id);

        $scope.userPromise = $scope.getJSONfromAPI('user', user_endpoint, 'initializeUser()')

        $scope.userPromise.then(function(payload) {
            $scope.user = payload.data;
            $scope.user_login = $scope.user.user.login;
            console.timeEnd('initializeUser()');

            // if we're doing the dash, we've got to get settlements and fiddle
            // the UI for new users

            if (user_endpoint === 'dashboard') {
                console.log("[USER] Retrieving campaign assets from API...");
                $scope.initWorld();

                // loading stuff ui/ux
                $scope.scratch.settlementsRequired = $scope.user.dashboard.campaigns.length + $scope.user.dashboard.settlements.length;

                $scope.campaigns = [];
                for (var i = 0; i < $scope.user.dashboard.campaigns.length; i++) {
                    var s_dict = $scope.user.dashboard.campaigns[i];
                    $scope.getSettlement(s_dict, $scope.campaigns, 'campaign');
                };

                $scope.settlements = [];
                for (var i = 0; i < $scope.user.dashboard.settlements.length; i++) {
                    var s_dict = $scope.user.dashboard.settlements[i];
                    $scope.getSettlement(s_dict, $scope.settlements, 'settlement');
                };

                if ($scope.user.dashboard.settlements.length === 0) {
                    showHide('campaign_div');   // this will hide it, because it's visible on-load
                    showHide('all_settlements_div');
                } else {
                    // pass
                };
            };
        },
            function(errorPayload) {
                console.error("[USER] Could not retrieve user information!");
                console.error("[USER] " + errorPayload.status + " -> " + errorPayload.data);
            }
        );

        // now do stuff that we need the settlement to do
        if ($scope.settlementPromise !== undefined) {
            $scope.settlementPromise.then(function() {
                $scope.userPromise.then(function() {
                    // determine if the user is a settlement admin
                    if ($scope.settlement.sheet.admins.indexOf($scope.user_login) == -1) {
                        $scope.user_is_settlement_admin = false;
//                        console.error($scope.user_login + ' is not a settlement admin.');
                    } else {
                        $scope.user_is_settlement_admin = true;
//                        console.warn($scope.user_login + ' is a settlement admin!');
                    };
                });
            });
        };

    };

    $scope.initializeSettlement = function(src_view, api_url, settlement_id) {

        // every view in the legacy webapp has to call this method. Therefore,
        // it's got lots of twists, turns, evaluations, etc. and can make a lot
        // of API requests.

        // intialize
        console.time('initializeSettlement()');
        if ($scope.api_url === undefined && api_url !== undefined) {
            $scope.api_url = api_url;
        };
        if ($scope.settlement_id === undefined && settlement_id !== undefined) {
            $scope.settlement_id = settlement_id;
        };
        if ($scope.view === undefined && src_view !== undefined) {
            $scope.view = src_view;
        };

        // initialize misc. scope elements
        $rootScope.departing_survivor_count = 0;
        $rootScope.hideControls = true;

        // now do it
        console.log("[SETTLEMENT] Initializing " + $scope.settlement_id + " '"+ $scope.view + "' view...");
        if ($scope.settlement_id !== undefined) {

            var settlement_endpoint = 'get'
            if ($scope.view === 'campaignSummary') {
                settlement_endpoint = 'get_campaign';
            };

            // save the promise to get the settlement to the $scope
            $scope.settlementPromise = $scope.getJSONfromAPI(
                'settlement', settlement_endpoint, 'initializeSettlement()'
            );

            // init the settlement
            $scope.settlementPromise.then(
                function(payload) {
                    // get the settlement; touch-up some of the arrays for UI/UX purposes
                    $scope.settlement = payload.data;

                    // finish initializing the settlement
                    $rootScope.hideControls = false; 
                    $scope.postJSONtoAPI('settlement', 'set_last_accessed', {}, false, false, false);

                    console.timeEnd('initializeSettlement()');

                },
                function(errorPayload) {console.log($scope.log_level + "Error loading settlement!" + errorPayload);}
            );



        };

        // if we're viewing the Settlement Sheet or Campaign Summary, do this stuff
        $scope.settlementPromise.then(function() {
            if ($scope.view == 'settlementSheet') {
                $scope.initAssetLists();
                $scope.initLostSettlementsControls();
                hideFullPageLoader();
                hideCornerLoader();
            } else if ($scope.view == 'campaignSummary') {;
                hideFullPageLoader();
                hideCornerLoader();
            } else if ($scope.view == 'survivorSheet') {
                $scope.randomNamesPromise = $http.get(api_url + 'get_random_names/200');
                $scope.randomNamesPromise.then(function(payload) {
                    $scope.randomSurvivorNames = payload.data;
                });
                if ($scope.survivorPromise != undefined) { 
                    $scope.survivorPromise.then(function() {
                        hideFullPageLoader();
                        hideCornerLoader();
                    });
                };
            };
        });
    }


    $scope.reinitialize = function(caller) {

        //postJSONtoAPI() sometimes calls this to refresh the view after a
        // significant update.

        if (caller === undefined) {
            console.warn("Re-initializing view...");
        } else {
            console.warn(caller + " method wants to reinitialize the view...");
        };
        showCornerLoader();
        if ($scope.view === 'survivorSheet') {
            $scope.initializeSurvivor();
        } else if ($scope.view === 'settlementSheet') {
            $scope.initializeSettlement(); 
        } else if ($scope.view === 'campaignSummary') {
            $scope.initializeSettlement(); 
        } else {
            console.error($scope.view + ' cannot be reinitialized!');
        };
    };



    $scope.initializeSurvivor = function(s_id) {
        // pulls a specific survivor down from the API and sets it as
        // $scope.survivor; also sets some other helpful $scope vars

        console.time('initializeSurvivor()');

        // initialize
        if ($scope.survivor_id === undefined) {
            $scope.survivor_id = s_id;
        };

        // wait for the settlement promise and then go get it, girl
        $scope.settlementPromise.then(function() {

            console.info("Initializing Survivor " + $scope.survivor_id);
            $scope.survivorPromise = $scope.getJSONfromAPI('survivor','get', 'initializeSurvivor()');

            $scope.survivorPromise.then(
                function(payload) {
                    $scope.survivor = payload.data;
                    hideFullPageLoader();
                    hideCornerLoader();
                    console.timeEnd('initializeSurvivor()');

                    // now do stuff after we drop the loader
                    $scope.initAssetLists();

                    //lineage first
                    console.time('$scope.lineage');
                    console.log("[LINEAGE] Retrieving survivor lineage data... ");
                    $scope.getJSONfromAPI('survivor','get_lineage','initializeSurvivor()').then(
                        function(payload) {
                            $scope.lineage = payload.data;
                            console.log('[LINEAGE] Lineage retrieved!');
                            console.timeEnd('$scope.lineage');
                        },
                        function(errorPayload) {
                            console.error("[LINEAGE] Could not retrieve survivor lineage from API!" + errorPayload);
                        }
                    );
                },
                function(errorPayload) {
                    console.log("[SURVIVOR] Error loading survivor " + s_id + " " + errorPayload);
                }
            );
        });
    };


    $scope.initializeEventLog = function() {
        console.time('initializeEventLog()');
        console.log('[EVENT LOG] Initializing event log...');
        $scope.getJSONfromAPI('settlement','get_event_log', 'initializeEventLog()').then(
            function(payload) {
                $scope.event_log = payload.data;
                console.timeEnd('initializeEventLog()');
            },
            function(errorPayload) {
                console.log($scope.log_level + "Error loading event_log!" + errorPayload);
            }
        );
    };

    $scope.setGameAssetOptions = function(game_asset, destination, exclude_type) {
        // generic method to create a set of options by comparing a baseline
        // list to a list of items to exclude from that list
        // 'game_asset' wants to be something from settlement.game_assets
        // 'user_asset' wants to be a user's list, e.g. $scope.survivor.sheet.epithets
        // 'destination' wants to be the output, e.g. $scope.locationOptions

        console.time("setGameAssetOptions(" + game_asset + ", " + destination + ", " + exclude_type +")");

        // initialize
        console.log("Refreshing '" + game_asset + "' game asset options...");
        if ($scope.view == 'survivorSheet') {
            var user_asset = $scope.survivor.sheet;
        } else if ($scope.view == 'settlementSheet') {
            var user_asset = $scope.settlement.sheet;
        } else {
            console.error('I DO NOT KNOW HOW TO SET ASSETS FOR THIS VIEW!');
            return false
        };

        // now do it!
        var output = {};
        angular.copy($scope.settlement.game_assets[game_asset], output);
        for (var i = 0; i < user_asset[game_asset].length; i++) {
            var a = user_asset[game_asset][i];

            if (output[a] != undefined) {
                if (output[a].max != undefined) {
                    var asset_max = output[a].max;
                    var asset_count = 0;
                    for (var j = 0; j < user_asset[game_asset].length; j++) {
                        if (user_asset[game_asset][j] == a) {asset_count += 1};
                    };
                    if (asset_count >= asset_max) {
                        delete output[a];
                    };
                } else {
                    delete output[a];
                };
            };
        };

        // filter anything whose 'type' matches exclude_type
        for (var b in output) {
            if (output[b].sub_type == exclude_type) {
                delete output[b];
            };
        };

        for (var c in output) {
            if (output[c].selectable == false) {
                delete output[c];
            };
        };

        $scope[destination] = output;
        console.log("Game asset '" + game_asset + "' options updated!");
        console.timeEnd("setGameAssetOptions(" + game_asset + ", " + destination + ", " + exclude_type +")");
    };


    $scope.initAssetLists = function() {
        // call this once you've got a settlement sheet in scope, i.e. hitch it to
        // the $scope.settlementPromise
        if ($scope.view == 'survivorSheet') {
            console.log('Initializing Survivor Sheet asset pickers...');

            $scope.setGameAssetOptions('abilities_and_impairments', "AIoptions", "curse");

            $scope.setGameAssetOptions('fighting_arts', "FAoptions");
            $scope.FAoptions["_random"]  = {handle: "_random", name: "* Random Fighting Art", type_pretty: "Special"};

            $scope.setGameAssetOptions('disorders', "dOptions");
            $scope.dOptions["_random"]  = {handle: "_random", name: "* Random Disorder", type_pretty: "Special"};

            $scope.setGameAssetOptions('epithets', "epithetOptions");

            //  custom COD junk
            $scope.settlement.game_assets.causes_of_death.push({'name': ' --- ', 'disabled': true});
            $scope.settlement.game_assets.causes_of_death.push({'name': '* Custom Cause of Death', 'handle': 'custom'});
            var cod_list = [];
            for (var i = 0; i < $scope.settlement.game_assets.causes_of_death.length; i++) {
                cod_list.push($scope.settlement.game_assets.causes_of_death[i]["name"]);
            };
            $scope.settlement_cod_list = cod_list;
        } else {
            console.log('Initializing Settlement Sheet asset pickers...');
            $scope.setGameAssetOptions('locations', "locationOptions");
            $scope.setGameAssetOptions('innovations', "innovationOptions", "principle");
        };
//       console.log("'" + view + "' view asset pickers initialized!")
    };



    $scope.set_jwt_from_cookie = function() {
        var cname = "jwt_token";
        var name = cname + "=";
        var decodedCookie = decodeURIComponent(document.cookie);
        var ca = decodedCookie.split(';');
        for(var i = 0; i <ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0) == ' ') {
                c = c.substring(1);
            }
            if (c.indexOf('session=') == 0) {
                $scope.session_oid = c.substring('session='.length, c.length);
            };
            if (c.indexOf(name) == 0) {
                $scope.jwt = c.substring(name.length, c.length);
                return true;
            };
        }
        console.error("Could not set JWT from cookie!");
        console.error("Session: " + $scope.session_oid);
        if ($scope.session_oid !== undefined) {
            $scope.legacySignOut($scope.session_oid);
        };
        console.error("Bad cookie: " + decodedCookie);
        $scope.jwt = false;
        return false;
    };
    $scope.set_jwt_from_cookie();

    $scope.getJSONfromAPI = function(collection, action, requester) {
        var r_log_level = "[" + requester + "] "
//        console.log(r_log_level + "Retrieving '" + collection + "' asset '" + action + "' data from API:");
        if ($scope.api_url === undefined){console.error(r_log_level + '$scope.api_url is ' + $scope.api_url + '! API retrieval cannot proceed!'); return false};
        var config = {"headers": {"Authorization": $scope.jwt}};
        if (collection == "settlement") {
            var url = $scope.api_url + "settlement/" + action + "/" + $scope.settlement_id;
        } else if (collection == "survivor") {
            var url = $scope.api_url + "survivor/" + action + "/" + $scope.survivor_id;
        } else if (collection == "user") {
            var url = $scope.api_url + "user/" + action + "/" + $scope.user_id;
        };
        console.log(r_log_level + "getJSONfromAPI() -> " + url);
        return $http.get(url, config);
    };

    $scope.postJSONtoAPI = function(collection, action, json_obj, reinit, show_alert, update_sheet) {
        console.time('postJSONtoAPI(' + collection + ', ' + action + ')');
        if (reinit === undefined) {reinit = true};
        if (show_alert === undefined) {show_alert = true};

        // always serialize on response, regardless of asset type
        json_obj.serialize_on_response = true;

        if (show_alert === true) {
            showCornerLoader();
        };

        // figure out which asset ID to use
        if (collection == 'settlement') {
            var asset_id = $scope.settlement_id;
        } else if (collection == 'survivor') {
            var asset_id = $scope.survivor_id;
            if (asset_id === undefined) {asset_id = $rootScope.survivor_id};
        } else if (collection == 'user') {
            var asset_id = $scope.user_id;
        } else {
            console.error("Collection '" + collection + "' is not supported by postJSONtoAPI method!");  
            errorAlert();
            return false;
        };

        // get auth header
        var config = {"headers": {"Authorization": $scope.jwt}};

        // create the URL and do the POST
        var endpoint = collection + "/" + action + "/" + asset_id;
        var url = $scope.api_url + endpoint;
        var res = $http.post(url, json_obj, config);

        res.success(function(data, status, headers, config) {
            console.warn("postJSONtoAPI(/'" + endpoint + "') call successful!");
            console.timeEnd('postJSONtoAPI(' + collection + ', ' + action + ')');
            if (update_sheet === true) {
                console.warn('Updating ' + collection + ' sheet from response!');
                $scope[collection] = data;
            };
            sleep(1000).then(() => {
                if (reinit === true) {$scope.reinitialize('postJSONtoAPI(/' + endpoint + ')')};
                if (show_alert === true) {savedAlert();}
            });
            hideCornerLoader();
        });
        res.error(function(data, status, headers, config) {
            errorAlert();
            console.error("postJSONtoAPI('" + endpoint + "') call has FAILED!!!");
            console.error(data);
            showAPIerrorModal(data, config.url);
            hideCornerLoader();
        });

        return res;
    };




    // front-end helper method that sets the scope's story and settlement events
    $scope.setEvents = function() {
        console.time('setEvents()');
        var all_events = $scope.settlement.game_assets.events;

        $scope.story_events = new Array();
        $scope.settlement_events = new Array();


        for (var property in all_events) {
            if (all_events.hasOwnProperty(property)) {
                var e = all_events[property];
                if (e.type == 'story_event') {
                    $scope.story_events.push(e);
                } else if (e.type == 'settlement_event') {
                    $scope.settlement_events.push(e)
                };
            };
        };

        $scope.story_events.sort(compare);
        $scope.settlement_events.sort(compare);

        console.log("Initialized " + $scope.story_events.length + " story events and " + $scope.settlement_events.length + " settlement events!");
        console.timeEnd('setEvents()');

    };


    // shows the custom COD block on the Controls of Death
    $scope.showCustomCOD = function() {
        var hidden_elem_id = "addCustomCOD";
        var hidden_elem = document.getElementById(hidden_elem_id);
        hidden_elem.style.display = "block";
    };

    // helpers and laziness - junk drawer functions
    $scope.isObject = function(a) {return typeof a === 'object';};

    $scope.range  = function(count,command) {
        var r = [];
        for (var i = 0; i < count; i++) {
            if (command=='increment') {
                r.push(i+1)
            } else {
                r.push(i) 
            };
        }
        return r;
    };

    $scope.hasattr = function(obj, name) {
        if (obj === undefined) {console.error("hasattr() called against undefined object. '" + name + "' cannot be an attribute of am undefined object.");};
        if (obj.indexOf(name) > -1) {
            return true
        };
        return false;
    };

    $scope.arrayContains = function(needle, arrhaystack) {
        if (arrhaystack === undefined) {console.warn("Cannot find " + needle + " in undefined!"); return false;};
        if (typeof arrhaystack != "array") {
            if (typeof arrhaystack == "object") {
            } else {
                console.warn(arrhaystack + ' does not appear to be an array or an object!')
            };
        };
        if (arrhaystack.indexOf(needle) > -1) {
            return true;
        };
        return false; 
    };


});


//  common and shared angularjs controllers. These controllers are used by
//  more than one (usually all) User Asset views. check out the assets.py
//  ua_decorator() method: it basically suffixes our main user asset views
//  with HTML that calls these controllers

app.controller("updateExpansionsController", function($scope) {
    $scope.toggleExpansion = function(e_handle) {
//        console.log($scope.settlement.game_assets.campaign.settlement_sheet_init.expansions.includes(e_handle));
        var input_element = document.getElementById(e_handle + "_modal_toggle");
        if (input_element.checked) {
            $scope.postJSONtoAPI('settlement', 'add_expansions', {'expansions': [e_handle]});
        } else {
            $scope.postJSONtoAPI('settlement', 'rm_expansions', {'expansions': [e_handle]});
        };
    };
});

app.controller('newSurvivorController', function($scope, $http) {
    $scope.scratch = {}
    $scope.scratch.newSurvivorsCreated = 0;
    $scope.scratch.newSurvivorSheets = [];
    $scope.scratch.newSurvivorSex = 'M';
    $scope.scratch.primaryDonor = 'father';
    $scope.scratch.newSurvivorPublic = false;
    $scope.toggleSex = function() {
        if ($scope.scratch.newSurvivorSex === 'M'){
            $scope.scratch.newSurvivorSex = 'F';
        } else if ($scope.scratch.newSurvivorSex === 'F') {
            $scope.scratch.newSurvivorSex = 'R';
        } else if ($scope.scratch.newSurvivorSex === 'R') {
            $scope.scratch.newSurvivorSex = 'M';
        };
    };
    $scope.toggleDonor = function() {
        if ($scope.scratch.primaryDonor === 'father'){
            $scope.scratch.primaryDonor = 'mother';
        } else {
            $scope.scratch.primaryDonor = 'father';
        }; 
    };
    $scope.togglePublic = function() {
        if ($scope.scratch.newSurvivorPublic === true){
            $scope.scratch.newSurvivorPublic = false;
        } else {
            $scope.scratch.newSurvivorPublic = true;
        }; 
    };

    $scope.setAvatar = function(e) {
        // uses the custom-on-change directive to convert the file to a str for
        // POSTing back to the API when the user pulls the trigger
        var reader = new FileReader();
        reader.readAsBinaryString(e.target.files[0]);
        reader.onload = function () {
            $scope.scratch.newSurvivorAvatar = btoa(reader.result);
        };
    };

    $scope.setNewSurvivorName = function() {
        var newName = document.getElementById('newSurvivorName').innerHTML;
        $scope.scratch.newSurvivorName = newName;
        if (newName === "") {
            $scope.scratch.newSurvivorName = undefined;
        };
    };

    $scope.createNewSurvivor = function() {
        // in which we fire some JSON at the API and attempt to make a new
        // survivor and show it to the user

        // 1.) start the clock, show the loader
        console.time('createNewSurvivor()');
        $scope.showHide('newSurvivorCreationLoader')

        // 2.) create the POST body
        var json_post = {
            settlement: $scope.settlement.sheet._id.$oid,
            name: $scope.scratch.newSurvivorName,
            sex: $scope.scratch.newSurvivorSex,
            avatar: $scope.scratch.newSurvivorAvatar,
            father: $scope.scratch.newSurvivorFather,
            mother: $scope.scratch.newSurvivorMother,
            primary_donor_parent: $scope.scratch.primaryDonor,
            email: $scope.scratch.newSurvivorEmail,
            'public': $scope.scratch.newSurvivorPublic, 
        }
//        console.warn(json_post);

        // 3.) create a promise for the post operation
        var config = {"headers": {"Authorization": $scope.jwt}};
        var res = $http.post(
            $scope.api_url + "new/survivor",
            json_post,
            config
        );

        // 4.) process the result, closing the loader and, if successful,
        // showing the new survivor link box, whose innerHTML we'll fiddle
        res.then(
            function(payload) {
                $scope.newSurvivorData = payload.data;
                $scope.scratch.newSurvivorsCreated += 1;

                var sheet = $scope.newSurvivorData.sheet;
                $scope.scratch.newSurvivorSheets.push(sheet);
   
                // clear the fields, i.e. so we don't repeat stuff
                $scope.scratch.newSurvivorAvatar = undefined;

                var newName = document.getElementById('newSurvivorName');
                newName.innerHTML = "";
                $scope.setNewSurvivorName();

                // wrap up, close up 
                console.timeEnd('createNewSurvivor()');
                $scope.showHide('newSurvivorCreationLoader');


            },
            function(errorPayload) {
                console.log("Failed to create new Survivor!" + errorPayload);
                $scope.showHide('newSurvivorCreationLoader')
            }
        );
    };

}); 


app.controller('playerManagementController', function($scope) {
    $scope.toggleAdmin = function(login) {
        var login_index = $scope.settlement.sheet.admins.indexOf(login);
        if (login_index == -1) {
            // user is not an admin
            $scope.settlement.sheet.admins.push(login);
            $scope.postJSONtoAPI('settlement','add_admin',{'login': login}, false)
        } else {
            // user is an admin
            $scope.settlement.sheet.admins.splice(login_index, 1);
            $scope.postJSONtoAPI('settlement','rm_admin',{'login': login}, false)
        };
    };
});

app.controller('settlementNotesController', function($scope, $rootScope) {

    $scope.addNote = function () {
        if (!$scope.newNote) {return;}
        var new_note_object = {
            "author_id": $scope.user_id,
            "note": $scope.newNote,
        };
        $scope.settlement.sheet.settlement_notes.unshift(new_note_object);
        $scope.postJSONtoAPI('settlement', 'add_note', new_note_object);
        $scope.newNote = "";
    };
    $scope.removeNote = function(index, n_id) {
        $scope.settlement.sheet.settlement_notes.splice(index, 1);
        $scope.postJSONtoAPI('settlement', 'rm_note', {_id: n_id}, false)
    };

    $scope.userRole = function(login) {
        if ($scope.settlement.sheet.admins.indexOf(login) == -1) {
            return 'player';
        } else {
            return 'settlement_admin'
        };
    };

}); 

app.controller('newSettlementController', function($scope, $http) {
    $scope.showLoader = true;
    $scope.hideLoader = function() {
        $scope.newSettlementPromise.then(function() {
            $scope.showLoader = false;
        });
    };

});

app.controller('timelineController', function($scope, $rootScope) {

    // limits $scope.event_log to only lines from target_ly
    $scope.get_event_log = function(t) {

        var target_ly = Number(t);
        local_event_log = new Array();

        if ($scope.event_log == undefined) {return false};

        for (i = 0; i < $scope.event_log.length; i++) {
            if (Number($scope.event_log[i].ly) == target_ly) {
                local_event_log.unshift($scope.event_log[i]);
            };
        };

//        console.log("added " + local_event_log.length + " items to local_event_log");
//        console.log($scope.local_event_log);
        return local_event_log;
    };


    $scope.showHideControls = function(ly) { 
//        console.warn('hiding LY ' + ly);
        elem_id='timelineControlsLY' + ly;

        var hidden_controls = document.getElementById(elem_id);
//        console.log(elem_id);
//        console.log("hidden controls = " + hidden_controls);

        if (hidden_controls === undefined) {
            console.warn('Hidden element is undefined!');
            return false
        } else if (hidden_controls === null && $scope.user_is_settlement_admin != true) {
            console.warn('Timeline controls are hidden! ' + $scope.user_login + ' admin status: ' + $scope.user_is_settlement_admin );
            return false;
        } else if (hidden_controls === null && $scope.user_is_settlement_admin == true) {
            console.error("Div ID " + elem_id + " is null! Timeline admin controls cannot be displayed!");
        };

        if (hidden_controls.style.display == 'none') {
            hidden_controls.style.height = 'auto';
            hidden_controls.style.display = 'flex';
        }
        else if (hidden_controls.style.display == 'flex') {
            hidden_controls.style.height = 0;
            hidden_controls.style.display = 'none';
        } else {console.log("UNHANDLED CONDITION! >" + hidden_controls.style.display + "<")};
    };

    $scope.showControls = function(ly) {
        var hidden_controls = document.getElementById('timelineControlsLY' + ly);
        hidden_controls.style.display='flex';
        hidden_controls.style.height='auto';
    };

    $scope.setLY = function(ly) {
        console.log("setting LY to " + ly);
        $scope.settlement.sheet.lantern_year = ly;
        $scope.postJSONtoAPI('settlement','set_attribute',{attribute: 'lantern_year',  value: ly});
    };

    $scope.getLYObject = function(ly) {
        // returns the local scope's timeline object for ly
        for (i = 0; i < $scope.settlement.sheet.timeline.length; i++) {
            var timeline_year = $scope.settlement.sheet.timeline[i];
            if (timeline_year.year == Number(ly)) {return timeline_year};
        }
    };

    $scope.rmEvent = function(ly,event_obj) {
        event_obj.user_login = $scope.user_login;
        event_obj.ly = ly;
        var target_ly = $scope.getLYObject(ly);
        var target_event_index = target_ly[event_obj.type].indexOf(event_obj);
        target_ly[event_obj.type].splice(target_event_index,1);
        $scope.postJSONtoAPI('settlement', 'rm_timeline_event', event_obj);
    };

    // in which we turn form input into a juicy hunk of API-safe JSON
    $rootScope.addEvent = function(ly, event_type, event_handle) {
        var event_obj = new Object();

        // use the event_type, if possible, to get the event dict from
        // active $scope. Works for story/settlement events
        if (event_type == 'story_event' || event_type == 'settlement_event') {
            event_obj = ($scope.settlement.game_assets.events[event_handle]);
        } else if (
            event_type == 'showdown_event' ||
            event_type == 'nemesis_encounter' ||
            event_type == 'special_showdown'
            ) {
            event_obj.type = event_type;
            event_obj.name = event_handle; // when is a handle not a handle?
        } else {
            console.error("ERROR! Unknown event type: " + event_type);
            return false;
        };


        event_obj.ly = ly;
        var target_ly = $scope.getLYObject(ly);

        if (!(event_obj.type in target_ly)) {
            target_ly[event_obj.type] = new Array();
        };

        for (i = 0; i < target_ly[event_obj.type].length; i++) {
            if (target_ly[event_obj.type][i] === event_obj) {
                console.log("Duplicate item. Returning true...");
                return true;
            }
        }

        // if we're still here after that iteration above, add the event
        target_ly[event_obj.type].push(event_obj);
        $scope.postJSONtoAPI('settlement', 'add_timeline_event', event_obj);

    };

});





// general use and general availability methods. this is like...the junk
// drawer of javascript methods

function modifyAsset(collection, asset_id, param_string) {

    // generic/global method for submitting a form to the webapp and updating a
    // survivor. Needs an id and params, e.g. 'whatever=thing&stuff=niner'
    // and so on. Used by various angular controlers.
    // 
    // this automatically handles the norefresh flag as well as the modify and
    // asset params

    var method = "POST"
    var url = "/"
    var params = "modify=" + collection + "&asset_id=" + asset_id + "&" + param_string + "&norefresh=True";

    var xhr = new XMLHttpRequest();

    xhr.onreadystatechange = function (oEvent) {  
        if (xhr.readyState === 4) {  
            if (xhr.status === 200) {  
                savedAlert();
            } else {  
                console.error(method + " -> " + xhr.responseURL + " -> " + params);
                console.error("Legacy app response was: " + xhr.status);
                console.error("Error -> '" + xhr.responseText + "' <-");  
                console.error(xhr);
                console.error(oEvent);
                errorAlert();
            }  
        }  
    }; 

//  2017-01-22 we're canceling the callback part until we can fix it for Safari
//  and firefox and the other POS browsers whose javascript sucks the sweat off
//  a dead donkey's balls
    xhr.open(method, url, true);
//    xhr.open(method, url, false);
    xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded");
//    window.alert(params);
    xhr.send(params);

}


//          angularjs controllers start here.

// all angularjs apps use this, so it needs to stay generic. at a minimum,
// an angularjs scope needs to know the following. survivor stuff is NOT handled
// here because angularjs apps that deal with survivors are necessarily
// specialized

app.controller("survivorNotesController", function($scope) {
    $scope.notes = [];
    $scope.formData = {};
    $scope.addNote = function (asset_id) {
        $scope.errortext = "";
        if (!$scope.note) {return;}
        if ($scope.notes.indexOf($scope.note) == -1) {
            $scope.notes.splice(0, 0, $scope.note);
//            $scope.notes.push($scope.note);
        } else {
            $scope.errortext = "The epithet has already been added!";
        };
        var http = new XMLHttpRequest();
        http.open("POST", "/", true);
        http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        var params = "add_survivor_note=" + $scope.note + "&modify=survivor&asset_id=" + asset_id
        http.send(params);
        savedAlert();

    };

    $scope.removeNote = function (x, asset_id) {
        $scope.errortext = "";
        var rmNote = $scope.notes[x];
        $scope.notes.splice(x, 1);

        var http = new XMLHttpRequest();
        http.open("POST", "/", true);
        http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        var params = "rm_survivor_note=" + rmNote + "&modify=survivor&asset_id=" + asset_id
        http.send(params);

        savedAlert();

    };
});

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
        var add_name = $scope.addMe.name;
        if (add_name == undefined) {var add_name = $scope.addMe};
        var params = "add_epithet=" + add_name + "&modify=survivor&asset_id=" + asset_id
        http.send(params);

        savedAlert();

    }
    $scope.removeItem = function (x, asset_id) {
        $scope.errortext = "";
        var removedEpithet = $scope.epithets[x];
        $scope.epithets.splice(x, 1);
        var http = new XMLHttpRequest();
        http.open("POST", "/", true);
        http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        var rm_name = removedEpithet.name;
        if (rm_name == undefined) {var rm_name = removedEpithet};
        var params = "remove_epithet=" + rm_name + "&modify=survivor&asset_id=" + asset_id;
        http.send(params);

        savedAlert();

    }
});



// close modal windows from a span
function closeModal(modal_div_id) {
    var modal = document.getElementById(modal_div_id);
    modal.style.display = "none";
}

function hide(id) {
    var e = document.getElementById(id);
    e.style.display="none";
};

function increment(elem_id) {
    var e = document.getElementById(elem_id);
    e.stepUp();
}
function decrement(elem_id) {
    var e = document.getElementById(elem_id);
    e.stepDown();
}

// button and togglebox registration 
// global func for damage toggles. 
function toggleDamage(elem_id, asset_id) {
    document.getElementById(elem_id).classList.toggle("damage_box_checked");
    var toggle_key = document.getElementById(elem_id);
    var params =  toggle_key.name + "=checked";
    modifyAsset("survivor", asset_id, params);
};


// Used to sort arrays of objects by name. Should be a lambda or something
// but FIWE. Maybe when I'm older
function compare(a,b) {
  if (a.name < b.name)
    return -1;
  if (a.name > b.name)
    return 1;
  return 0;
}



// User update methods.

app.controller('addManySurvivorsController', function($scope, $http) {
    $scope.scratch = {
        'manySurvivorsFather': undefined,
        'manySurvivorsMother': undefined,
        'addMaleSurvivors': 0,
        'addFemaleSurvivors': 0,
    };

    $scope.addManySurvivors = function() {
        $scope.scratch.showLoader = true;
        var json_post = {
            male: $scope.scratch.addMaleSurvivors,
            female: $scope.scratch.addFemaleSurvivors,
            father: $scope.scratch.manySurvivorsFather,
            mother: $scope.scratch.manySurvivorsMother,
            settlement_id: $scope.settlement.sheet._id.$oid,
        }
//        console.warn(json_post);
        var config = {"headers": {"Authorization": $scope.jwt}};
        var res = $http.post(
            $scope.api_url + "new/survivors",
            json_post,
            config
        );

        res.success(function(data, status, headers, config) {
            console.warn("addManySurvivors() success!");
            $scope.scratch.bulkAddNewSurvivors = data;
            $scope.scratch.showLoader = false;
            $scope.reinitialize();
        });
        res.error(function(data, status, headers, config) {
            console.error(data);
        });
    };

})

app.controller("sideNavController", function($scope) {
    // feed it a survivor, this returns a bool of whether it's one of
    // the user's favorites. useful in lots of different scopes, hence
    // part of the root

    $scope.favoriteFilter = function(s) {
        var fav = false;
        if (s.sheet.favorite == undefined) {return false;}
        if (s.sheet.favorite.indexOf($scope.user_login) !== -1) {fav = true};
//        console.log($scope.user_login + " -> " + s.sheet.name + " fav: " + fav);
        if (s.sheet._id.$oid === $scope.survivor_id) {fav = false};
        if (s.sheet.dead === true) {fav = false};
        if (s.sheet.departing === true) {fav = false};  //exclude departing survivors
        return fav;
    };

    $scope.departingFilter = function(s)  {
        var dep = false;
        if (s.sheet.departing === true) {dep = true};
        return dep;
    };

    $scope.countSurvivors = function(type) {
        var survivors = 0;

        incrementFavorites = function(s, index) {
            if ($scope.favoriteFilter(s) === true) {survivors += 1};
        };
        incrementDeparting = function(s, index) {
            if ($scope.departingFilter(s) === true) {survivors += 1};
        };

        if ($scope.settlement !== undefined) {
            if (type === 'favorite') {
                $scope.settlement.user_assets.survivors.forEach(incrementFavorites);
            } else if (type === 'departing') {
                $scope.settlement.user_assets.survivors.forEach(incrementDeparting);
            };
        };
        return survivors;
    };


});




