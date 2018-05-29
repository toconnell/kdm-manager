
// main campaignSummary controller / root / container
app.controller ("campaignSummaryController", function($scope) {
    $scope.getStorage = function() {
        console.time('getStorage()');
        $scope.getJSONfromAPI('settlement','get_storage', 'getStorage').then(
            function(payload) { $scope.settlementStorage = payload.data; console.timeEnd('getStorage()');},
            function(errorPayload) {console.log("Could not retrieve settlement storage from API!" + errorPayload);}
        );
    };

    $scope.fadeSurvivorGroupsLoader = function() {
        $('#waitingForSurvivors').fadeOut(1500);
    };

    $scope.isVisible = function(element_id) {
        // weird little method that tests whether an HTML element has the
        // 'visible' class in its classList
        e = document.getElementById(element_id);
        if (e === null) {console.error("element ID '" + element_id + "' not found in document!"); return false}
        if (e.classList.contains('visible')) {return true};
        return false;
    };

});


// endeavor token app

app.controller("endeavorController", function($scope) {

    $scope.addToken = function(){
        $scope.postJSONtoAPI('settlement', 'update_endeavor_tokens', {"modifier": 1}, false);
        $scope.settlement.sheet.endeavor_tokens += 1;
    };

    $scope.rmToken = function(){
        $scope.postJSONtoAPI('settlement', 'update_endeavor_tokens', {"modifier": -1}, false);
        $scope.settlement.sheet.endeavor_tokens -= 1;
        if ($scope.settlement.sheet.endeavor_tokens <= 0) {$scope.settlement.sheet.endeavor_tokens = 0;};
    };

});


app.controller("manageDepartingSurvivorsController", function($scope, $rootScope) {
    $scope.scratch = {
        increment_ly_on_return: false,
        showdown_type_options: [
            {'name': 'Showdown', 'value': 'normal'},
            {'name': 'Nemesis Encounter', 'value': 'nemesis'},
            {'name': 'Special Showdown', 'value': 'special'},
        ],
    }; 


    // methods for showing/hiding control blocks

    $scope.toggleControlState = function(c) {
        // toggles a control state; c should be a string
        if ($scope.scratch[c] === 'visible') {
            $scope.scratch[c] = 'hidden';
        } else {
            $scope.scratch[c] = 'visible';
        };
    };

    $scope.initShowdownControls = function(){
        // this is kind of low-rent, but we've got exact conditions we want to
        // evaluate for showing/hiding our various controls. All of our controls
        // have a 'state' in scratch (which this sets); states are modified by
        // toggleControlState() above, rather than 'showHide()', which isn't
        // complex enough for our UX design here.

        $scope.scratch.survival_bonus_control_state = 'hidden';

        if ($scope.settlement.sheet.showdown_type != undefined) {
            $scope.scratch.showdown_type_control_state = 'hidden';
        } else {
            $scope.scratch.showdown_type_control_state = 'visible';
        };

        if ($scope.settlement.sheet.showdown_type != undefined && $scope.settlement.sheet.current_quarry != undefined) {
            $scope.scratch.showdown_current_quarry_control_state = 'hidden';
        } else {
            $scope.scratch.showdown_current_quarry_control_state = 'visible';
        };

        if ($scope.settlement.sheet.showdown_type != undefined && $scope.settlement.sheet.current_quarry != undefined) {
            $scope.scratch.showdown_manage_departing_survivors_control_state = 'visible';
        } else {
            $scope.scratch.showdown_manage_departing_survivors_control_state = 'hidden';
        };

        // always hide this one
        $scope.scratch.showdown_return_departing_survivors_control_state = 'hidden';
    };


    // misc. helper
    $scope.toggleIncrementLY = function() {
        if ($scope.scratch.increment_ly_on_return === false) {
            $scope.scratch.increment_ly_on_return = true;
        } else {
            $scope.scratch.increment_ly_on_return = false;
        };
    };

    // methods for updating the SETTLEMENT from the modal controls

    $scope.setShowdownType = function(s){
        $scope.settlement.sheet.showdown_type = s;
        var js_obj = {showdown_type: s};
        $scope.postJSONtoAPI('settlement','set_showdown_type',js_obj, false, true);
//        $scope.toggleControlState('showdown_type_control_state');
        $scope.calculateDepartingSurvivorBonus();
    };

    $scope.saveCurrentQuarry = function() {
        var q_name = $scope.settlement.sheet.current_quarry;
        js_obj = {current_quarry: q_name}
        $scope.postJSONtoAPI('settlement', 'set_current_quarry', js_obj, false);
    };    

    $scope.addCurrentQuarryToTimeline = function() {
        // replaces a TL year to include info on the current quarry

        // initialize
        var ly = $scope.settlement.sheet.lantern_year;
        var q = $scope.settlement.sheet.current_quarry;
        var s = $scope.settlement.sheet.showdown_type;
        var event_type = 'showdown_event';
        if (s === 'special') {
            event_type = 'special_showdown';
        } else if (s === 'nemesis') {
            event_type = 'nemesis_encounter';
        };

        // sanity check
        if (q === undefined) {console.error('Quarry not specified! Gotta die...'); return false;};

        // construct an updated LY
        target_ly = $scope.getTimelineLY(ly);
        if (target_ly === null) {
            console.error("Could not retrieve Timeline LY " + ly + "! Gotta die...");
            return false;
        };

        if (target_ly[event_type] === undefined) {
            target_ly[event_type] = [{name: q}]
        } else {
            target_ly[event_type].push({name: q})
        };

        $scope.postJSONtoAPI('settlement','replace_lantern_year', {'ly': target_ly}, false );

        showHide('addCurrentQuarryToTimeline');
    };

    $scope.returnDepartingSurvivors = function(a){
        showFullPageLoader();
        if ($scope.scratch.increment_ly_on_return === true) {
            $scope.setCurrentLY($scope.settlement.sheet.lantern_year + 1);
        };
        $scope.postJSONtoAPI('settlement', 'return_survivors', {aftermath: a});
    };

    $scope.updateDepartingSurvivors = function(attrib, mod){
        showFullPageLoader();
        $rootScope.hideControls = true;
        $scope.postJSONtoAPI('settlement', 'update_survivors', {
            include: 'departing', attribute: attrib, 'modifier': mod,
        });
    };

    $scope.calculateDepartingSurvivorBonus = function(){
        // calculates the total survival bonus for departing survivors
        var showdown_type = $scope.settlement.sheet.showdown_type;
//        console.warn("Calculating bonuses for '" + showdown_type + "' showdown...");
        $scope.scratch.departing_survival_bonus = 0;

        for (var i = 0; i < $scope.settlement.sheet.innovations.length; i++) {
            var i_handle = $scope.settlement.sheet.innovations[i];
            i_dict = $scope.settlement.game_assets.innovations[i_handle];

            if (i_dict.hasOwnProperty('departing_survival_bonus') === true) {
//                console.warn(i_dict);
                var base = i_dict.departing_survival_bonus["general"];

                if (base !== undefined) {
                    $scope.scratch.departing_survival_bonus += base;
                };

                if (i_dict.departing_survival_bonus[showdown_type] !== undefined) {
                    var bonus = i_dict.departing_survival_bonus[showdown_type];
                    $scope.scratch.departing_survival_bonus += bonus;
                };
            };

        };
//        console.warn($scope.scratch.departing_survival_bonus);
    };

});



app.controller('survivorManagementController', function($scope, $rootScope) {

    $scope.manageable_survivors = 0;
    $scope.verify_manageable = true;

    $scope.scratch={};

    // add an unset option to color schemes
    $scope.settlementPromise.then(
        function(payload) {
            var remove_color = {handle: 'None', name: ' -- Unset -- '};
            $scope.settlement.survivor_color_schemes.none = remove_color;
        }
    );

    $scope.initArrow = function(g) {
        // sets the arrow based on the group
        if (g.handle === 'the_dead') {
            g.arrow = true;
        } else {
            g.arrow = false;
        }; 
    };

    $scope.flipArrow = function(group) {
        // flips the expand/collapse arrow arround
        if (group.arrow === true) {
            group.arrow = false;
        } else if (group.arrow === false) {
            group.arrow = true;
        } else if (group.arrow === undefined) {
            group.arrow = true;
        };
    };


    $scope.setColorScheme = function(s){
        $rootScope.survivor_id = s.sheet._id.$oid;
        if (s.sheet.color_scheme == 'None') {
            $scope.postJSONtoAPI('survivor', 'set_color_scheme', {unset: true}, false);
        } else {
            json_obj = {'handle': s.sheet.color_scheme};
            $scope.postJSONtoAPI('survivor', 'set_color_scheme', json_obj, false);
        };
    };

    $scope.setSurvivorAttribute = function(s, attrib){
        // basic ish; doesn't reinit, but reloads from the return
        $rootScope.survivor_id = s.sheet._id.$oid;
        json_obj = {attribute: attrib, value: s.sheet[attrib]};
        var res = $scope.postJSONtoAPI('survivor', 'set_attribute', json_obj, false);
        res.then(
            function(payload) {
                var sheet = payload.data.sheet
                s.sheet = sheet;
            },
            function(errorPayload){console.error('ERROR!');}
        );
    };

    $scope.toggleDamage = function(s, loc){
        $rootScope.survivor_id = s.sheet._id.$oid;
        json_obj = {'location': loc};
        var res = $scope.postJSONtoAPI('survivor', 'toggle_damage', json_obj, false);
        res.then(
            function(payload) {
                var sheet = payload.data.sheet
                s.sheet = sheet;
            },
            function(errorPayload){console.error('ERROR!');}
        );
    };

    $scope.toggleSurvivorFlag = function(s, flag){
        $rootScope.survivor_id = s.sheet._id.$oid;
        json_obj = {'flag': flag};
        var res = $scope.postJSONtoAPI('survivor', 'toggle_status_flag', json_obj, false);
        res.then(
            function(payload) {
                var sheet = payload.data.sheet
                s.sheet = sheet;
            },
            function(errorPayload){console.error('ERROR!');}
        );
    };

    $scope.setSurvivorAttributes = function(s, attrib){
        $rootScope.survivor_id = s.sheet._id.$oid;
        json_obj = {
            attributes: [{attribute: attrib, value: s.sheet[attrib]}],
            attribute_details: [
                {attribute: attrib, detail: 'tokens', value: s.sheet.attribute_detail[attrib].tokens },
                {attribute: attrib, detail: 'gear', value: s.sheet.attribute_detail[attrib].gear },
            ],
        };
        var res = $scope.postJSONtoAPI('survivor', 'set_many_attributes', json_obj, false);
    };

    $scope.initSurvivorCard = function(survivor) {
        // sets survivor.meta.manageable within a given survivor. access/security
        // logic is all right here, folks. Hack away!

        survivor.meta = {};
        if (survivor.sheet.departing === true) {$rootScope.departing_survivor_count += 1};

        // set whether the survivor is returning
        var r_years = survivor.sheet.returning_survivor;
        var cur_ly = Number($scope.settlement.sheet.lantern_year);
        if (r_years != undefined) {
            if (r_years.indexOf(cur_ly) != -1) {
                survivor.meta.returning_survivor = true;
//            console.warn(cur_ly + " found in " + r_years + ". " + survivor.sheet.name + " is returning.");
            } else if (r_years.indexOf(cur_ly-1) != -1) {
                survivor.meta.returning_survivor = true;
            };
        };


        // now set perms/access
        survivor.meta.manageable = false;

        // automatic pass for all settlement admins
        if ($scope.user_is_settlement_admin == true) {
            survivor.meta.manageable = true;
        };

        // return True if the survivor belongs to the current user
        if (survivor.sheet.email === $scope.user_login){
            survivor.meta.manageable = true;
        };
        if (survivor.sheet.public === true) {
            survivor.meta.manageable = true;
        };

//        if (survivor.meta.manageable === true) {console.warn($scope.user_login + " can manage " + survivor.sheet.name)}
        if (survivor.meta.manageable === true) {$scope.manageable_survivors += 1; $scope.verify_manageable=false};
    };

    $scope.popSurvivor = function(s_id){
        // removes a survivor from whatever group they're in; returns their dict
        for (i=0; i < $scope.settlement.user_assets.survivor_groups.length; i++) {
            var g_dict = $scope.settlement.user_assets.survivor_groups[i];
            for (j=0; j < g_dict.survivors.length; j++) {
                var s_dict = g_dict.survivors[j];
                if (s_dict.sheet._id.$oid == s_id) {
                    g_dict.survivors.splice(j, 1);
                    return s_dict;
                };
            };
        };
    };

    $scope.pushSurvivor = function(s_dict, group){
        // pushes a survivor dict onto a group's survivors list
        for (i=0; i < $scope.settlement.user_assets.survivor_groups.length; i++) {
            var g_dict = $scope.settlement.user_assets.survivor_groups[i];
            if (g_dict.handle == group) {
                g_dict.survivors.push(s_dict);
                return true
            };
        };
    };

    $scope.toggleDepartingStatus = function(s){
        // this is a little hack-y, but hey: FIWE

        $rootScope.survivor_id = s.sheet._id.$oid;
        var set = true;
        if (s.sheet.departing === true) {set = false};
        if (set === true) {
            var s_dict = $scope.popSurvivor(s.sheet._id.$oid);
            $scope.pushSurvivor(s_dict, 'departing');
            $scope.postJSONtoAPI('survivor','set_status_flag', {'flag': 'departing'});
        } else {
            var s_dict = $scope.popSurvivor(s.sheet._id.$oid);
            $scope.pushSurvivor(s_dict, 'available');
            $scope.postJSONtoAPI('survivor', 'set_status_flag', {'flag': 'departing', 'unset': true})
        };

    };

    $scope.modifySurvivorAttrib = function(s, attrib, mod, max){
        s.sheet[attrib] += mod;
        if (s.sheet[attrib] < 0) {s.sheet[attrib] = 0; return false};
        if (max != undefined && s.sheet[attrib] > max) {s.sheet[attrib] = max; return false};
        json_obj = {attribute: attrib, modifier: mod}
        $rootScope.survivor_id = s.sheet._id.$oid;
        $scope.postJSONtoAPI('survivor', 'update_attribute', json_obj, false);
    };


    $scope.showSurvivorControls = function(s) {
        if (s.meta.manageable === false) {return false; };
        var s_id = s.sheet._id.$oid;
        var s_modal = s_id + '_modal_controls';
        $scope.showHide(s_modal);
    };

}); 



