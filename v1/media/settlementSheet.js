function reloadSheet() {
    showFullPageLoader();
    var reload_form = document.getElementById("settlementSheetReload");
    reload_form.submit();
//    console.warn("Settlement Sheet reload form submitted...");
};

app.controller("abandonSettlementController", function($scope) {
    $scope.abandonSettlement = function() {
        showFullPageLoader();
        $scope.postJSONtoAPI('settlement','abandon',{})
    };
});

app.controller("lanternResearchController", function($scope) {
    $scope.setLanternResearch = function() {
        js_obj = {value: $scope.settlement.sheet.lantern_research_level};
        $scope.postJSONtoAPI('settlement', 'set_lantern_research_level', js_obj, false);
    };
    $scope.incrementLanternResearch = function(modifier) {
        $scope.settlement.sheet.lantern_research_level += modifier;
        $scope.setLanternResearch();
    };
});


app.controller("milestonesController", function($scope) {
    $scope.toggleMilestone = function(m_handle) {
        console.warn(m_handle);
        var handle_index = $scope.settlement.sheet.milestone_story_events.indexOf(m_handle);
        if (handle_index == -1 ) {
            $scope.settlement.sheet.milestone_story_events.push(m_handle);
            $scope.postJSONtoAPI('settlement', 'add_milestone', {handle: m_handle}, false);
        } else {
            $scope.settlement.sheet.milestone_story_events.splice(handle_index, 1);
            $scope.postJSONtoAPI('settlement', 'rm_milestone', {handle: m_handle}, false);
        };
    };  
});


app.controller("inspirationalStatueController", function($scope) {
    $scope.setInspirationalStatue = function() {
        js_obj = {handle: $scope.settlement.sheet.inspirational_statue};
        $scope.postJSONtoAPI('settlement', 'set_inspirational_statue', js_obj, false)
    };
});

app.controller('monsterVolumesController', function($scope) {
    $scope.scratch = {};
    $scope.addMonsterVolume = function() {
        if ($scope.scratch.monster_volume == undefined) {return false};
        $scope.settlement.sheet.monster_volumes.push($scope.scratch.monster_volume);
        js_obj = {name: $scope.scratch.monster_volume};
        $scope.postJSONtoAPI('settlement', 'add_monster_volume', js_obj);
    };
    $scope.rmMonsterVolume = function(index, vol_string) { 
        $scope.settlement.sheet.monster_volumes.splice(index,1);
        var js_obj = {"name": vol_string};
        $scope.postJSONtoAPI('settlement', 'rm_monster_volume', js_obj); 
    };
});

app.controller("storageController", function($scope) {
    $scope.toggleFlippers = function(h) {
        // flips the expand/collapse arrow arround
        if (h.flippers === true) {
            h.flippers = false;
        } else if (h.flippers === false) {
            h.flippers = true;
        };
    };
    $scope.flipArrow = function(h) {
        // flips the expand/collapse arrow arround
        if (h.arrow === true) {
            h.arrow = false;
        } else if (h.arrow === false) {
            h.arrow = true;
        } else if (h.arrow === undefined) {
            h.arrow = true;
        };
    };

    $scope.setStorage = function(asset, modifier) {
        asset.quantity += modifier;
        js_obj = {handle: asset.handle, value: asset.quantity};
        $scope.postJSONtoAPI('settlement','set_storage', {storage: [js_obj]}, false, false);
    };

    $scope.loadStorage = function() {
        $scope.showHide('storageSpinner');
        $scope.showHide('storageLauncher'); 
        $scope.settlementStorage = undefined;
        var res = $scope.getJSONfromAPI('settlement','get_storage', 'loadStorage');
        res.then(
            function(payload) {
                $scope.settlementStorage = payload.data;
                $scope.showHide('storageSpinner'); 
                $scope.showHide('storageLauncher'); 
            },
            function(errorPayload) {console.log("Could not retrieve settlement storage from API!" + errorPayload);}
        );
    };
    $scope.loadStorage();

});

app.controller("settlementSheetController", function($scope) {
    $scope.scratch = {} 
    $scope.setSettlementName = function() {
        var newName = document.getElementById('settlementName').innerHTML;
        js_obj = {name: newName};
        $scope.postJSONtoAPI('settlement', 'set_name', js_obj);
    };
    $scope.incrementAttrib = function(attrib, modifier) {
        if ($scope.settlement.sheet[attrib] + modifier < 0) {return false};
        var js_obj = {'attribute': attrib, 'modifier': modifier};
        $scope.settlement.sheet[attrib] += Number(modifier);
        $scope.postJSONtoAPI('settlement', 'update_attribute', js_obj, false);
    };
    $scope.setAttrib = function(attrib, value) {
        if (value < 0) {return false};
        var js_obj = {'attribute': attrib, 'value': value};
        $scope.postJSONtoAPI('settlement', 'set_attribute', js_obj);
    };
});

app.controller("locationsController", function($scope) {
    $scope.addLocation = function() {
        if ($scope.newLocation === null) {return false};
        $scope.settlement.sheet.locations.push($scope.newLocation);
        $scope.postJSONtoAPI('settlement', 'add_location', {"handle": $scope.newLocation});
        $scope.newLocation = null;
    };
    $scope.rmLocation = function(index, loc_handle) {
        $scope.settlement.sheet.locations.splice(index, 1);
        $scope.postJSONtoAPI('settlement', 'rm_location', {"handle": loc_handle}); 
    };
    $scope.setLocationLevel = function(loc_name, lvl) {
        var js_obj = {"handle": loc_name, "level": lvl};
        $scope.postJSONtoAPI('settlement', 'set_location_level', js_obj);
    };
});


app.controller('innovationsController', function($scope) {
    $scope.spinner = function(operation) {
        var spinner = document.getElementById('innovationDeckSpinner');
        if (spinner === null) {return false};
        if (operation == "hide") {
            spinner.style.display = "none"
        } else {
            spinner.style.display = "block"
        };
    };
    $scope.innovationInSettlement = function(innovation) {
        if ($scope.settlement.sheet.innovations.indexOf(innovation.handle) > -1) {return true};
        return false; 
    };

    $scope.setInnovationDeck = function(retry) {
        console.time('innovationDeck()');
        $scope.innovation_deck = null;
        $scope.spinner();
        var res = $scope.postJSONtoAPI('settlement','get_innovation_deck', {return_type: null});
        res.then(
            function(payload) {
                $scope.innovation_deck = payload.data;
                if ($scope.innovation_deck.length < 1 && $scope.settlement.sheet.innovations.length > 0) {
                    if (retry === undefined) {
                        console.warn("Empty Innovation Deck! Retrying...")
                        $scope.setInnovationDeck(true);
                    } else if (retry === true) {
                        console.warn("Blank Innovation Deck returned after retry!")
                    } else {console.error("retry was " + retry + " which is unexpected!")};
                };
//                console.log("Innovation Deck refreshed!");
                $scope.spinner("hide");
                console.timeEnd('innovationDeck()');
            },
            function(errorPayload) {console.log("Could not retrieve innovation deck from API!" + errorPayload);}
        );
    };
    $scope.addInnovation = function(handle) {
//        console.warn("Adding innovation: " + $scope.newInnovation);
        if (handle !== undefined) {
            $scope.newInnovation = handle;
        };
        if ($scope.newInnovation === null) {return false};
        $scope.settlement.sheet.innovations.push($scope.newInnovation);
        var js_obj = {"handle": $scope.newInnovation};
        var out = $scope.postJSONtoAPI('settlement', 'add_innovation', js_obj);
        $scope.newInnovation = null;
        sleep(500).then(() => {
            $scope.setInnovationDeck();
        });
    };    
    $scope.setInnovationLevel = function(innovation_name,lvl){
        var js_obj = {"handle": innovation_name, "level": lvl};
        $scope.postJSONtoAPI('settlement', 'set_innovation_level', js_obj);
    };
    $scope.rmInnovation = function(index, innovation_handle) {
        $scope.settlement.sheet.innovations.splice(index,1);
        var js_obj = {"handle": innovation_handle};
        $scope.postJSONtoAPI('settlement', 'rm_innovation', js_obj); 
        sleep(500).then(() => {
            $scope.setInnovationDeck();
        });
    };

    $scope.createInnovationQuickPick = function(n) {
        if (n === undefined) {
            // figure out how many to choose
            var n = 2;
            if ($scope.settlement.sheet.innovations.indexOf('symposium') != -1) {
                n = 4;
            };
        };

        // now create a list of available handles
        var arr = Object.keys($scope.innovation_deck);
      
        // adjust our number down, if we've got fewer than we want
        if (n > arr.length) {
            n = arr.length;
            console.warn('adjusting innovation draw down to ' + n);
        };
 
        // and pick random ones 
        console.warn('selecting ' + n + ' random innovations...');
        var result = new Array(n), len = arr.length, taken = new Array(len);
        if (n > len)
            throw new RangeError("createInnovationQuickPick(): more elements taken than available");
        while (n--) {
            var x = Math.floor(Math.random() * len);
            result[n] = arr[x in taken ? taken[x] : x];
            taken[x] = --len;
        }
        
        // inject into scope 
        $scope.innovationQuickPickOptions = result;
    };
});


app.controller('defeatedMonstersController', function($scope, $http) {
    $scope.addDefeatedMonster = function() {
        js_obj = {'monster': $scope.dMonst}
        $scope.postJSONtoAPI('settlement', 'add_defeated_monster', js_obj, false);
        $scope.settlement.sheet.defeated_monsters.push($scope.dMonst);
        $scope.dMonst = null;

    };
    $scope.rmDefeatedMonster = function(index, monster) {
        js_obj = {'monster': monster}
        $scope.postJSONtoAPI('settlement', 'rm_defeated_monster', js_obj, false);
        $scope.settlement.sheet.defeated_monsters.splice(index,1);
    };
});

app.controller('quarriesController', function($scope, $http) {
    $scope.addQuarry = function(x) {
        // set the quarry handle that we're going to add; bail if it's bogus
        var quarry_handle = $scope.addQuarryMonster;
        if (quarry_handle === null) {console.error("quarry handle is null!"); return false};

        // update the settlement object; 
        $scope.settlement.sheet.quarries.push(quarry_handle);
        $scope.settlement.game_assets.quarry_options.splice(x, 1);

        // post
        js_obj = {'handle': quarry_handle}
        $scope.postJSONtoAPI('settlement', 'add_monster', js_obj);
    };
    $scope.removeQuarry = function(x,q_handle) {
        $scope.settlement.sheet.quarries.splice(x,1);
        var monster = $scope.settlement.game_assets.monsters[q_handle];
        $scope.settlement.game_assets.quarry_options.push(monster);

        // post
        js_obj = {'handle': q_handle}
        $scope.postJSONtoAPI('settlement', 'rm_monster', js_obj);
    };
});

app.controller('nemesisEncountersController', function($scope) {

    $scope.nemesisLvlChecked = function(n_handle,n_lvl) {
        var n_lvl_array = $scope.settlement.sheet.nemesis_encounters[n_handle];
        if ($scope.arrayContains(Number(n_lvl), n_lvl_array)) {
            return true
        } else {
            return false
        };
    };

    $scope.toggleNemesisLevel = function(n_handle,n_lvl,e) {
//        console.log(n_handle + " " + n_lvl);
//        console.log(e);
        var n_lvl_array = $scope.settlement.sheet.nemesis_encounters[n_handle];
//        console.log(n_lvl_array)
        if ($scope.arrayContains(n_lvl, n_lvl_array)) {
            e.target.control.checked = false;
            n_lvl_array.splice(n_lvl-1,1);
        } else { 
            n_lvl_array.push(Number(n_lvl));
            e.target.control.checked = true;
        };
        js_obj = {"handle": n_handle, "levels": n_lvl_array};
        $scope.postJSONtoAPI('settlement', 'update_nemesis_levels', js_obj);
    };

    $scope.rmNemesis = function(index, handle) {
        $scope.settlement.sheet.nemesis_monsters.splice(index,1);
        js_obj = {'handle': handle}
        $scope.postJSONtoAPI('settlement', 'rm_monster', js_obj);
    };
    $scope.addNemesis = function() {
        if ($scope.addNemesisMonster === null) {console.error("nemesis handle is null!"); return false};
        $scope.settlement.sheet.nemesis_monsters.push($scope.addNemesisMonster);
        $scope.settlement.sheet.nemesis_encounters[$scope.addNemesisMonster] = [];
        js_obj = {'handle': $scope.addNemesisMonster};
        $scope.postJSONtoAPI('settlement', 'add_monster', js_obj);
    };

});

app.controller('principlesController', function($scope, $http) {
    $scope.get_principle_group = function (target_principle) {
        var p_options = $scope.settlement.game_assets.principles_options;
        for (i=0; i < p_options.length; i++) {
            if (p_options[i].handle==target_principle) { return p_options[i]};
        };
    };

    $scope.set = function(principle, election) {
        $scope.postJSONtoAPI('settlement', 'set_principle', {"principle": principle, "election": election});
    };
    $scope.unset_principle = function () {
        target_principle = $scope.unset;

        var p_options = $scope.settlement.game_assets.principles_options;
        for (i=0; i < p_options.length; i++) {
            if (p_options[i].handle==target_principle) { var p_group = p_options[i]};
        };

        for (var option in p_group.options) {
            if (p_group.options.hasOwnProperty(option)) {
                var target_input = document.getElementById(p_group.options[option]["input_id"]);
                target_input.checked = false;
            };
        };

        $scope.postJSONtoAPI('settlement', 'set_principle', {"principle": target_principle, "election": false});
    };
});

app.controller("lostSettlementsController", function($scope,$rootScope) {

    $scope.rmLostSettlement = function () {
        var cur = Number($scope.current_val);
        if (cur == 0) {
//            window.alert("At minimum!");
        }
        else { 
            cur--;
            $scope.current_val = cur;
            $scope.postJSONtoAPI('settlement', 'set_lost_settlements', {"value": cur}, false);
            var e = document.getElementById('box_' + cur);
            e.classList.remove('lost_settlement_checked');
        };
    };

    $scope.addLostSettlement = function () {
        var cur = Number($scope.current_val);
        if (cur == 19) {
            window.alert("At maximum!");
        }
        else { 
            var e = document.getElementById('box_' + cur);
            e.classList.remove('bold_check_box');
            e.classList.add('lost_settlement_checked');
            cur++;
            $scope.current_val = cur;
            $scope.postJSONtoAPI('settlement', 'set_lost_settlements', {"value": cur}, false);
        };
    };


    // Run this on controller init: creates the controls
    $scope.createLostSettlementControls = function() {

        if ($scope.lost_settlements == undefined) {console.log("lost_settlements count not available!")};

    };
    
});

