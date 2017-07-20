
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

// public helpers

function sleep (time) {return new Promise((resolve) => setTimeout(resolve, time));}


//
//      The angular application starts here!
//

var app = angular.module('kdmManager', []);

// factories and services for angularjs modules

app.factory('apiService', function($http) {
    var factory = {};
    factory.getSettlement = function(root_url, api_route, s_id, config) {
            if (config === undefined) {console.error("apiService factory invoked without 'Authorization' header!")};
            return $http.get(root_url + 'settlement/' + api_route + '/' + s_id, config);
        };
    factory.getSurvivor = function(root_url, api_route, s_id, config) {
            if (config === undefined) {console.error("apiService factory invoked without 'Authorization' header!")};
            return $http.get(root_url + 'survivor/' + api_route + '/' + s_id, config);
        };
    return factory;
});

app.factory('assetService', function($http) {
    return {
        getNewSettlementAssets: function(root_url) {
            return $http.get(root_url + 'new_settlement');
        }
    }
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


app.controller('rootController', function($scope, $rootScope, apiService, assetService, $http) {

    $scope.loadSettlement = function(r) {
        var api_route = r;
        if (api_route == undefined) {var api_route='get';};

        // get the Authorization JWT stuff
        $scope.set_jwt_from_cookie();
        var config = {"headers": {"Authorization": $scope.jwt}};

        // returns a promise
        return apiService.getSettlement($scope.api_url, api_route, $scope.settlement_id, config);
    };


    $scope.reinitialize = function() {
        
        console.log("Re-initializing settlement...");
        showCornerLoader();
        $scope.initialize(
            $scope.view,
            $scope.user_id,
            $scope.user_login,
            $scope.api_url,
            $scope.settlement_id
        );
    };

    // This is the main event: initialize everything settlement-related that
    // might be required by any user asset view. This is our de facto rootScope
    // (even though we don't call it that). 
    $scope.initialize = function(src_view, u_id, login, api_url, settlement_id, survivor_id) {
        $scope.api_url = api_url;
        $scope.settlement_id = settlement_id;
        $scope.user_id = u_id;
        $scope.user_login = login;
        $scope.view = src_view;
        $scope.survivor_id = survivor_id;

        // load the settlement from the API
        $scope.loadSettlement().then(
            function(payload) {
                // get the settlement; touch-up some of the arrays for UI/UX purposes
                $scope.settlement = payload.data;
                $scope.settlement.game_assets.causes_of_death.push({'name': ' --- ', 'disabled': true});
                $scope.settlement.game_assets.causes_of_death.push({'name': '* Custom Cause of Death', 'handle': 'custom'});
                var cod_list = [];
                for (var i = 0; i < $scope.settlement.game_assets.causes_of_death.length; i++) {
                    cod_list.push($scope.settlement.game_assets.causes_of_death[i]["name"]);
                };
                $scope.settlement_cod_list = cod_list;

                // create the settlement_sheet in scope (for laziness/legacy)
                $scope.settlement_sheet = $scope.settlement.sheet;

                // create other in-scope stuff off of the sheet:
                $rootScope.current_ly = $scope.settlement_sheet.lantern_year;
                $scope.settlement_notes = $scope.settlement_sheet.settlement_notes;
                $scope.timeline = $scope.settlement_sheet.timeline;
                $scope.current_quarry = $scope.settlement_sheet.current_quarry;
                $scope.setEvents();

                // do user stuff
                $scope.user_is_settlement_admin = $scope.arrayContains(login, $scope.settlement_sheet.admins);

                // finish initializing the settlement
                console.log("Settlement '" + $scope.settlement_id + "' initialized!")
                hideFullPageLoader();
                hideCornerLoader();

                // finally, if we're initializing a survivor sheet, do that
                if ($scope.view=='survivorSheet') {
                    $scope.initializeSurvivor($scope.survivor_id);
                };

            },
            function(errorPayload) {console.log("Error loading settlement!" + errorPayload);}
        );


        // now load the event log from the API
        $scope.loadSettlement('event_log').then(
            function(payload) {
                $scope.event_log = payload.data;
                console.log($scope.event_log.length + " item event_log initialized!")
            },
            function(errorPayload) {console.log("Error loading event_log!" + errorPayload);}
        );

        assetService.getNewSettlementAssets($scope.api_url).then(
            function(payload) {
                $scope.new_settlement_assets = payload.data;
                console.log("loaded new_settlement assets!");
            },
            function(errorPayload) {console.log("Error loading new settlement assets!" + errorPayload);}
        );

        // finish
        console.log("appRoot controller (" + $scope.view + ") initialized!");
        console.log("Settlement ID = " + $scope.settlement_id);
        console.log("Current user login = " + $scope.user_login);
    }


    $scope.initializeSurvivor = function(s_id) {
        // pulls a specific survivor down from the API and sets it as
        // $scope.survivor; also sets some other helpful $scope vars

        showCornerLoader();
        console.info("Initializing survivor " + s_id);
        $scope.survivor_id = s_id;

        $scope.getJSONfromAPI('survivor','get').then(
            function(payload) {
                $scope.survivor = payload.data;
                $scope.survivor_sheet = payload.data.sheet;
                console.info("Survivor Sheet initialized for survivor " + $scope.survivor_id);
                hideCornerLoader();
            },

            function(errorPayload) {console.log("Error loading survivor " + s_id + " " + errorPayload);}
        );
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
            if (c.indexOf(name) == 0) {
                $scope.jwt = c.substring(name.length, c.length);
                return true;
            }
        }
        console.warn("Could not set JWT from cookie!");
        $scope.jwt = false;
        return false;
    };

    $scope.getJSONfromAPI = function(collection, action) {

        $scope.set_jwt_from_cookie();
        var config = {"headers": {"Authorization": $scope.jwt}};
        if (collection == "settlement") {
            return apiService.getSettlement($scope.api_url, action, $scope.settlement_id, config);
        } else if (collection = "survivor") {
            return apiService.getSurvivor($scope.api_url, action, $scope.survivor_id, config);
        };
    };

    $scope.postJSONtoAPI = function(collection, action, json_obj) {

        // figure out which asset ID to use
        if (collection == 'settlement') {
            var asset_id = $scope.settlement_id;
        } else if (collection == 'survivor') {
            var asset_id = $scope.survivor_id;
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
            savedAlert();
        });
        res.error(function(data, status, headers, config) {
            errorAlert();
            console.error("API POST FAILURE!!!");
        });

        return res;
    };


    $scope.setGameAssetOptions = function(game_asset, user_asset, destination, exclude_type) {
        // generic method to create a set of options by comparing a baseline
        // list to a list of items to exclude from that list
        // 'game_asset' wants to be something from settlement.game_assets
        // 'user_asset' wants to be a user's list, e.g. $scope.survivor.sheet.epithets
        // 'destination' wants to be the outpue, e.g. $scope.locationOptions
        showCornerLoader();
        var res = $scope.getJSONfromAPI('settlement','get');
        res.then(
            function(payload) {
                console.log("Refreshing '" + game_asset + "' game asset options...");
                var output = payload.data.game_assets[game_asset];
                for (var i = 0; i < $scope[user_asset][game_asset].length; i++) {
                    var a = $scope[user_asset][game_asset][i];
                    if (output[a] != undefined) {
                        if (output[a].max != undefined) {
                            var asset_max = output[a].max;
                            var asset_count = 0;
                            for (var j = 0; j < $scope[user_asset][game_asset].length; j++) {
                                if ($scope[user_asset][game_asset][j] == a) {asset_count += 1};
                            };
//                            console.log(a + " count: " + asset_count + "; max: " + asset_max);
                            if (asset_count >= asset_max) {
                                delete output[a];
                            };
                        } else {
                            delete output[a];
                        };
                    };
                };
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
                hideCornerLoader();
            },
            function(errorPayload) {console.error("Could not update '" + game_asset + "' game asset options!" + errorPayload);}
        );
    };

    // helper method that sets the scope's story and settlement events
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
    $scope.showHide = function(e_id) {
        var e = document.getElementById(e_id);
        var hide_class = "hidden";
        if (e.classList.contains(hide_class)) {
            e.classList.remove(hide_class);
        } else {
            e.classList.add(hide_class)
        };
    }

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
            $scope.postJSONtoAPI('settlement', 'add_expansions', [e_handle]);
        } else {
            $scope.postJSONtoAPI('settlement', 'rm_expansions', [e_handle]);
        };
        sleep(500).then(() => {
            $scope.reinitialize();
        });
    };
});

app.controller('newSurvivorController', function($scope) {

    $scope.addNewSurvivor = function(e) {
    };

}); 


app.controller('playerManagementController', function($scope) {
    $scope.toggleAdmin = function(login) {
        if ($scope.arrayContains(login, $scope.settlement_sheet.admins)) {
            var login_index = $scope.settlement_sheet.admins.indexOf(login);
            $scope.settlement_sheet.admins.splice(login_index,1);
        } else { 
            $scope.settlement_sheet.admins.push(login);
        };
        var params = "toggle_admin_status=" + login;
        modifyAsset('settlement', $scope.settlement_id, params);
    };
});

app.controller('settlementNotesController', function($scope, $rootScope) {

    $scope.getID = function () {
        var text = "";
        var possible = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";

        for( var i=0; i < 20; i++ )
            text += possible.charAt(Math.floor(Math.random() * possible.length));

        return text;
    };

    $scope.addNote = function () {
        if (!$scope.newNote) {return;}
        var new_note_object = {
            "author": $scope.user_login,
            "author_id": $scope.user_id,
            "note": $scope.newNote,
            "js_id": $scope.getID(),
            "lantern_year": $rootScope.current_ly,
        };
        $scope.settlement_notes.unshift(new_note_object);
        $scope.postJSONtoAPI('settlement', 'add_note', new_note_object);
    };
    $scope.removeNote = function (x, note_js_id) {
        $scope.settlement_notes.splice(x, 1);
        $scope.postJSONtoAPI('settlement', 'rm_note', {"js_id": note_js_id, "user_login": $scope.user_login})
        sleep(500).then(() => {
            $scope.reinitialize();
        });
    };
    $scope.userRole = function(login) {
        if ($scope.arrayContains(login, $scope.settlement_sheet.admins)) {
            return 'settlement_admin'} else {
            return 'player';
        };
    };
}); 

app.controller('newSettlementController', function($scope, assetService) {
    $scope.showLoader = true;
    $scope.initNewSettlement = function(api_url) {
        $scope.api_url = api_url;
        assetService.getNewSettlementAssets($scope.api_url).then(
            function(payload) {
                $scope.new_settlement_assets = payload.data;
                $scope.showLoader = false;                
            },
            function(errorPayload) {console.log("Error loading new settlement assets!" + errorPayload);}
        );
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
                local_event_log.push($scope.event_log[i]);
            };
        };

//        console.log("added " + local_event_log.length + " items to local_event_log");
//        console.log($scope.local_event_log);
        return local_event_log;
    };


    $scope.showHideControls = function(ly) { 
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
//        console.log("setting LY to " + ly);
        $rootScope.current_ly = Number(ly);
        modifyAsset('settlement', $scope.settlement_id, "lantern_year=" + $rootScope.current_ly);
        sleep(500).then(() => {
            $scope.reinitialize();
        });
    };

    $scope.getLYObject = function(ly) {
        // returns the local scope's timeline object for ly
        for (i = 0; i < $scope.timeline.length; i++) {
            var timeline_year = $scope.timeline[i];
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
    $rootScope.addEvent = function(ly,event_type,event_handle) {

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
            // do stuff
        } else {console.log("ERROR! Unknown event type: " + event_type)};


        event_obj.user_login = $scope.user_login;
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

app.controller("appRootController", function($scope) {

    $scope.initialize = function(login, is_admin, api_url, settlement_id) {
        $scope.settlement_id = settlement_id;
        $scope.api_url = api_url;
        $scope.user_login = login;
        $scope.user_is_settlement_admin = is_admin;
        console.log("angularjs app root initialized!");
        console.log($scope.user_login + " admin status = " + $scope.user_is_settlement_admin);
    }

});


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

    // strikethrough for p.survivor_sheet_fighting_art_elements
    if (source_input.id == 'survivor_sheet_cannot_use_fighting_arts' ) {
        if (source_input.checked == true) {
            $('.survivor_sheet_fighting_art').addClass('strikethrough');
        } else {
            $('.survivor_sheet_fighting_art').removeClass('strikethrough');
        };
    };

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

// showHide func for attrib controls, accordion h3's, etc.
function showHide(id) {
    var e = document.getElementById(id);
    if (e.style.display != 'none') e.style.display = 'none';
    else e.style.display = 'block';
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



