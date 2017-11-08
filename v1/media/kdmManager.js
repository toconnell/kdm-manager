
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

function showHide(e_id) {
    var e = document.getElementById(e_id);
    var hide_class = "hidden";
    var visible_class = "visible";
    if (e === null) {console.error("No element with ID value '" + e_id + "' found on the page!"); return false}
    if (e.classList.contains(hide_class)) {
        e.classList.remove(hide_class);
        e.classList.add(visible_class);
    } else {
        e.classList.add(hide_class);
        e.classList.remove(visible_class)
    };
 }

function sleep (time) {return new Promise((resolve) => setTimeout(resolve, time));}

function convertMS(millis) {
  var minutes = Math.floor(millis / 60000);
  var seconds = ((millis % 60000) / 1000).toFixed(0);
  return minutes + ":" + (seconds < 10 ? '0' : '') + seconds;
}


//
//      The angular application starts here!
//

var app = angular.module('kdmManager', []);



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




app.controller('rootController', function($scope, $rootScope, $http) {

    // initialize rootScope elements here; these are set on every view
    $rootScope.showHide = showHide;

    // new settlement assets
    $scope.addNewSettlementsToScope = function(api_url) {
        $scope.newSettlementPromise = $http.get(api_url + 'new_settlement');
        $scope.newSettlementPromise.then(
            function(payload) {
                $scope.new_settlement_assets = payload.data;
                $scope.showLoader = false;                
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

        setInterval( function init() {
            
            showCornerLoader();

            var world_url = $scope.api_url + "world";
            $http.get(world_url).then(
                function(result) {
                    $scope.world = result.data.world;
                    hideCornerLoader();
                    console.log('[WORLD] Retrieved data successfully!')
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


    $scope.getSettlement = function(s_id, dest){
        // pass in a string of a settlement OID to push a settlement onto array
        // 'dest'
        var config = {"headers": {"Authorization": $scope.jwt}};
        $http.get($scope.api_url + 'settlement/get_summary/' + s_id, config).then(
            function(payload) {
                dest.push(payload.data);
            },
            function(errorPayload) {
                console.error("[rootController.getSettlement()] Could not get settlement " + s_id);
                console.error(errorPayload);
            }
        );
    };

    $scope.initializeUser = function(u_id, user_endpoint, api_url){
        // initialize
        var start = performance.now();
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

        $scope.userPromise = $scope.getJSONfromAPI('user', user_endpoint, 'initialize (user)')

        $scope.userPromise.then(function(payload) {
            $scope.user = payload.data;
            $scope.user_login = $scope.user.user.login;
            var stop = performance.now();
            console.warn("[USER] Initialized user " + $scope.user_login + " (" + $scope.user_id + ") in " + convertMS((stop-start)) + " seconds!");

            // if we're doing the dash, we've got to get settlements and fiddle
            // the UI for new users

            if (user_endpoint === 'dashboard') {
                console.log("[USER] Retrieving campaign assets from API...");
                $scope.initWorld();

                $scope.campaigns = [];
                for (var i = 0; i < $scope.user.dashboard.campaigns.length; i++) {
                    var s_id = $scope.user.dashboard.campaigns[i].$oid;
                    $scope.getSettlement(s_id, $scope.campaigns);
                };

                $scope.settlements = [];
                for (var i = 0; i < $scope.user.dashboard.settlements.length; i++) {
                    var s_id = $scope.user.dashboard.settlements[i].$oid;
                    $scope.getSettlement(s_id, $scope.settlements);
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
        var settlementStart = performance.now();
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
        console.log("[SETTLEMENT] Initializing '" + $scope.view + "' view...");
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
                    $scope.postJSONtoAPI('settlement', 'set_last_accessed', {}, false, false);

                    var settlementStop = performance.now();
                    console.warn("[SETTLEMENT] Settlement " + $scope.settlement_id + " initialized in " + convertMS((settlementStop - settlementStart)) + " seconds!");

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
            } else { 
                // pass
            };
        });
    }


    $scope.reinitialize = function() {

        //postJSONtoAPI() sometimes calls this to refresh the view after a
        // significant update.

        console.warn("Re-initializing view...");
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

        // initialize
        var survivor_start = performance.now();
        if ($scope.survivor_id === undefined) {
            $scope.survivor_id = s_id;
        };

        // wait for the settlement promise and then go get it, girl
        $scope.settlementPromise.then(function() {

            console.info("Initializing Survivor " + s_id);
            $scope.survivorPromise = $scope.getJSONfromAPI('survivor','get', 'initializeSurvivor()');

            $scope.survivorPromise.then(
                function(payload) {
                    $scope.survivor = payload.data;
                    var survivor_stop = performance.now();
                    console.warn("[SURVIVOR] Initialized survivor " + $scope.survivor_id + " in " + convertMS((survivor_stop - survivor_start)) + " seconds!");
                    hideFullPageLoader();
                    hideCornerLoader();

                    // now do stuff after we drop the loader
                    $scope.initAssetLists();
                    $scope.getJSONfromAPI('survivor','get_lineage','initializeSurvivor()').then(
                        function(payload) {
                            console.log("[LINEAGE] Retrieving survivor lineage data... ");
                            $scope.lineage = payload.data;
                            console.log('[LINEAGE] Lineage retrieved!');
                        },
                        function(errorPayload) {
                            console.error("[LINEAGE] Could not retrieve survivor lineage from API!" + errorPayload);
                        },
                    );
                },
                function(errorPayload) {
                    console.log("[SURVIVOR] Error loading survivor " + s_id + " " + errorPayload);
                }
            );
        });
    };


    $scope.initializeEventLog = function() {
        var eventLogStart = performance.now();
        console.log('[EVENT LOG] Initializing event log...');
        $scope.getJSONfromAPI('settlement','get_event_log', 'initializeEventLog()').then(
            function(payload) {
                $scope.event_log = payload.data;
                var eventLogStop = performance.now();
                console.warn("[EVENT LOG] Initialized event log in " + convertMS((eventLogStop - eventLogStart)) + " seconds!");
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
            if (output[b].type == exclude_type) {
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

    $scope.getJSONfromAPI = function(collection, action, requester) {
        var r_log_level = "[" + requester + "] "
//        console.log(r_log_level + "Retrieving '" + collection + "' asset '" + action + "' data from API:");
        if ($scope.api_url === undefined){console.error(r_log_level + '$scope.api_url is ' + $scope.api_url + '! API retrieval cannot proceed!'); return false};
        $scope.set_jwt_from_cookie();
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

    $scope.postJSONtoAPI = function(collection, action, json_obj, reinit, show_alert) {
        if (reinit === undefined) {reinit = true};
        if (show_alert === undefined) {show_alert = true};

        showCornerLoader();
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
        $scope.set_jwt_from_cookie();
        var config = {"headers": {"Authorization": $scope.jwt}};

        // create the URL and do the POST
        var url = $scope.api_url + collection + "/" + action + "/" + asset_id;
        var res = $http.post(url, json_obj, config);

        res.success(function(data, status, headers, config) {
            console.warn("postJSONtoAPI() call successful!");
            sleep(1000).then(() => {
                if (reinit === true) {$scope.reinitialize()} else {hideCornerLoader()};
                if (show_alert === true) {savedAlert();}
            });
        });
        res.error(function(data, status, headers, config) {
            errorAlert();
            console.error("postJSONtoAPI() call has FAILED!!!");
            console.error(data);
            showAPIerrorModal(data, config.url);
            hideCornerLoader();
        });

        return res;
    };




    // front-end helper method that sets the scope's story and settlement events
    $scope.setEvents = function() {
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

    };


    // shows the custom COD block on the Controls of Death
    $scope.showCustomCOD = function() {
        var hidden_elem_id = "addCustomCOD";
        var hidden_elem = document.getElementById(hidden_elem_id);
        hidden_elem.style.display = "block";
    };

    // modal div and button registration!
    // this needs to always be in scope of ng-init or else the whole website 
    // breaks (and the baby jesus cries)!
    $scope.registerModalDiv = function(modal_button_id, modal_div_id) {
        var btn = document.getElementById(modal_button_id);
        var modal = document.getElementById(modal_div_id);

        if (btn == undefined) {console.error("WARN: Could not find button id " + modal_button_id); return false};
        if (modal == undefined) {console.error("WARN: Could not find button id " + modal_button_id); return false};

        btn.onclick = function(b) {
            b.preventDefault();
            modal.style.display = "block";
        };
        window.onclick = function(event) {if (event.target == modal) {modal.style.display = "none";}};

        console.log( "button: " + modal_button_id + " and div: " + modal_div_id + " are linked!");
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

app.controller('newSurvivorController', function($scope) {

    $scope.addNewSurvivor = function(e) {
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
            "author": $scope.user_login,
            "author_id": $scope.user_id,
            "note": $scope.newNote,
            "lantern_year": $scope.settlement.sheet.lantern_year,
        };
        $scope.settlement.sheet.settlement_notes.unshift(new_note_object);
        $scope.postJSONtoAPI('settlement', 'add_note', new_note_object);
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


// generic survivor attrib update sans page refresh
function updateAssetAttrib(source_input, collection, asset_id) {

    // this is an all-purpose asset attribute updater. This is where most of our
    // formless submission logic happens (at least the js bits of it). Remember
    // that everything here is meant to be collection/asset agnostic!

    // a little idiot-proofing for Yours Truly
    if (typeof source_input == "string") {
        var source_input = document.getElementById(source_input);
    };

    if (source_input.hasAttribute('id') != true) {window.alert("Trigger element has no id!")};

    var attrib_key = document.getElementById(source_input.id).name;
    var new_value = document.getElementById(source_input.id).value;

    if (new_value == '') {window.alert("Blank values cannot be saved!"); return false;};

    // emphasis effect for font.survival_action_emphasize
    if (source_input.id == 'cannot_spend_survival' ) {
        if (source_input.checked == true) {
            var x = document.getElementsByClassName("survival_action_available");
            var i;
            for (i = 0; i < x.length; i++) {
                x[i].style.removeProperty('font-weight', 'bold');
                x[i].style.removeProperty('color', '#000');
                x[i].classList.remove('survival_action_emphasize');
            };
            } else {
            var x = document.getElementsByClassName("survival_action_available");
            var i;
            for (i = 0; i < x.length; i++) {
                x[i].style.setProperty('font-weight', 'bold');
                x[i].style.setProperty('color', '#000');
            };
        };
    };

    var params = attrib_key + "=" + new_value
    modifyAsset(collection, asset_id, params);

};

// burger sidenav
function openNav() {
    document.getElementById("mySidenav").style.width = '75%';
}
function closeNav() {
    var nav = document.getElementById("mySidenav");
    if (nav === null){
//        console.warn("mySidenav element does not exist!")
    } else {
        nav.style.width = "0"
    };
}

// close modal windows from a span
function closeModal(modal_div_id) {
    var modal = document.getElementById(modal_div_id);
    modal.style.display = "none";
}

function hide(id) {
    var e = document.getElementById(id);
    e.style.display="none";
};

// inc/dec functions + step-n-save
function stepAndSave(step_dir, target_element_id, collection, asset_id) {
    var input = document.getElementById(target_element_id);
    if (step_dir == "up") {input.stepUp()} else {input.stepDown()};
    var param_string = input.name + "=" + Number(input.value);
    modifyAsset(collection, asset_id, param_string)
}
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

// saves a user preference; flashes the saved alert. ho-hum
function updateUserPreference(input_element) {

    var params = input_element.name + "=" + input_element.value;

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/", true);
    xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    var params = "update_user_preferences=True&norefresh=True&" + params;
    xhr.send(params);

    savedAlert();
};



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

