function reloadSheet() {
    showFullPageLoader();
    var reload_form = document.getElementById("settlementSheetReload");
    reload_form.submit();
//    console.warn("Settlement Sheet reload form submitted...");
};

// main app controler; most things should end up here when we de-balkanize
app.controller("settlementSheetController", function($scope) {
    $scope.scratch = {
        showSettlementTumblerScold: false,
    } 

    // tabs! overwrite the root scope values
    $scope.tabsObject.tabs = [
        {
            id: 0,
            name: 'Sheet',
        },
        {
            id: 1,
            name: 'Storage',
        },
        {
            id: 6,
            name: 'Admin',
        },
    ],

    // generic settlement operations; prefer these to specific in V4
    $scope.incrementAttrib = function(attrib, modifier) {
        if ($scope.settlement.sheet[attrib] + modifier < 0) {return false};
        var js_obj = {'attribute': attrib, 'modifier': modifier};
        $scope.settlement.sheet[attrib] += Number(modifier);
        $scope.postJSONtoAPI('settlement', 'update_attribute', js_obj, false);
    };

    $scope.setAttrib = function(attrib, value, reinit) {
        if (value === undefined) {
            value = $scope.settlement.sheet[attrib]
        };
        if (reinit === undefined) {
            reinit = true;
        }; 
        if (value < 0) {return false};
        var js_obj = {'attribute': attrib, 'value': value};
        $scope.postJSONtoAPI('settlement', 'set_attribute', js_obj, reinit);
    };

    // misc. settlement sheet operations
    $scope.setSettlementName = function() {
        var newName = document.getElementById('settlementName').innerHTML;
        js_obj = {name: newName};
        $scope.postJSONtoAPI('settlement', 'set_name', js_obj);
    };


    // one-off routes
    $scope.setInspirationalStatue = function() {
        js_obj = {handle: $scope.settlement.sheet.inspirational_statue};
        $scope.postJSONtoAPI('settlement', 'set_inspirational_statue', js_obj, false)
    };

    $scope.setLostSettlements = function() {
        $scope.postJSONtoAPI('settlement', 'set_lost_settlements', {value: $scope.settlement.sheet.lost_settlements})
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

app.controller("strainMilestonesController", function($scope) {
    $scope.strainMilestonesPresent = function() {
        var count = 0;
        var sm = $scope.settlement.game_assets.strain_milestones;
        for(var prop in sm) {
            if(sm.hasOwnProperty(prop))
                ++count;
        }
        console.info(count + " Strain Milestones present in campaign game assets!");
        if (count > 0) {return true};
        return false;
    };

    $scope.toggleStrainMilestone = function(handle) {
        var s_index = $scope.settlement.sheet.strain_milestones.indexOf(handle);
        if (s_index !== -1 ) {
            $scope.settlement.sheet.strain_milestones.splice(s_index,1);
        } else {
            $scope.settlement.sheet.strain_milestones.push(handle);
        };
        $scope.postJSONtoAPI('settlement', 'toggle_strain_milestone', {handle: handle}, false, true, true);
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
    $scope.innovationInSettlement = function(innovation) {
        if ($scope.settlement.sheet.innovations.indexOf(innovation.handle) > -1) {return true};
        return false; 
    };

    $scope.setInnovationDeck = function(retry) {
        console.time('innovationDeck()');
        $scope.innovation_deck = null;
        var spinner = 'innovationDeckSpinner';
        $scope.ngShow(spinner);
        var res = $scope.postJSONtoAPI('settlement','get_innovation_deck', {return_type: 'dict'}, false, false);
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
                $scope.ngHide(spinner);
                console.timeEnd('innovationDeck()');
            },
            function(errorPayload) {
                console.log("Could not retrieve innovation deck from API!" + errorPayload);
            }
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
        var res = $scope.postJSONtoAPI('settlement', 'add_innovation', js_obj);
        $scope.newInnovation = null;
        res.then(
            function(payload) {
                console.warn("innovation added. refreshing deck...")
                $scope.setInnovationDeck();
            }
        );
    };    
    $scope.setInnovationLevel = function(innovation_name,lvl){
        var js_obj = {"handle": innovation_name, "level": lvl};
        $scope.postJSONtoAPI('settlement', 'set_innovation_level', js_obj);
    };
    $scope.rmInnovation = function(index, innovation_handle) {
        $scope.settlement.sheet.innovations.splice(index,1);
        var js_obj = {"handle": innovation_handle};
        var res = $scope.postJSONtoAPI('settlement', 'rm_innovation', js_obj); 
        res.then(
            function(payload) {
                console.warn("innovation removed. refreshing deck...")
                $scope.setInnovationDeck();
            }
        );
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

    $scope.toggleNemesisLevel = function(n_handle,n_lvl) {
        var n_lvl_array = $scope.settlement.sheet.nemesis_encounters[n_handle];
//        console.log(n_lvl_array)
        if ($scope.arrayContains(n_lvl, n_lvl_array)) {
            n_lvl_array.splice(n_lvl-1,1);
        } else { 
            n_lvl_array.push(Number(n_lvl));
        };
        js_obj = {"handle": n_handle, "levels": n_lvl_array};
        $scope.postJSONtoAPI('settlement', 'update_nemesis_levels', js_obj, false);
    };

    $scope.rmNemesis = function(index, handle) {
        $scope.settlement.sheet.nemesis_monsters.splice(index,1);
        js_obj = {'handle': handle}
        $scope.postJSONtoAPI('settlement', 'rm_monster', js_obj);
    };
    $scope.addNemesis = function() {
        if ($scope.addNemesisMonster === null) {
            console.error("nemesis handle is null!");
            return false;
        };
        $scope.settlement.sheet.nemesis_monsters.push($scope.addNemesisMonster);
        $scope.settlement.sheet.nemesis_encounters[$scope.addNemesisMonster] = [];
        js_obj = {'handle': $scope.addNemesisMonster};
        $scope.addNemesisMonster = undefined; 
        $scope.postJSONtoAPI('settlement', 'add_monster', js_obj);
    };

});


app.controller('principlesController', function($scope, $http) {

    $scope.scratch = {}

    // returns a bool representing whether the principle is set
    $scope.principleIsSet = function(p_obj) {
        for (i=0; i < p_obj.option_handles.length; i++) {
            var p_option_handle = p_obj.option_handles[i];
            var p_option = p_obj.options[p_option_handle];
            if (p_option.checked) {return true};
        };
        return false;
    };

    $scope.get_principle_group = function (target_principle) {
        var p_options = $scope.settlement.game_assets.principles_options;
        for (i=0; i < p_options.length; i++) {
            if (p_options[i].handle==target_principle) { return p_options[i]};
        };
    };

    $scope.set = function(principle, optionObj) {
        if (optionObj.checked) {
            console.warn("Principle option '" + optionObj.handle + "' is already set!");
            return false;
        };
        $scope.settlement.sheet.principles = undefined;
        $scope.postJSONtoAPI('settlement', 'set_principle', {
            "principle": principle,
            "election": optionObj.handle,
            }
        );
    };

    $scope.unsetPrinciple = function () {

        target_principle = $scope.scratch.unset; // this is a handle
        console.warn("Principle handle '" + target_principle + "' will be unset...");

        $scope.settlement.sheet.principles = undefined;

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

        $scope.postJSONtoAPI(
            'settlement',
            'set_principle',
            {"principle": target_principle, "election": false}
        );
    };
});


//
//  Tab controllers from here down; deprecated one-off controllers above
//

app.controller("settlementSheetStorageTabController", function($scope) {
    // controller for the storage tab; new in V4 2020-08

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
        $scope.postJSONtoAPI('settlement','set_storage', {storage: [js_obj]}, false, true, false);
    };

    $scope.refreshRollups = function(storage_repr) {
        var res = $scope.getJSONfromAPI('settlement','get_storage_rollups', 'updateRollups');
        res.then(
            function(payload) {
                for (i=0; i < $scope.settlementStorage.length; i++) {
                    var storage_repr = $scope.settlementStorage[i];
                    var update_dict = payload.data[storage_repr.storage_type];
                    for (const key in update_dict) {
                        let value = update_dict[key];
                        if (update_dict.hasOwnProperty(key)) {
                            storage_repr[key] = update_dict[key];
                        };
                    };
                };
            },
                function(errorPayload) {
                console.error("Failed to reload storage rollups! " + errorPayload);
            }
        );

    }

    $scope.loadStorage = function(reload) {
        // load settlement storage!
        
        // remove and reload if if requested
        if (reload === true) {
            $scope.settlementStorage = undefined;
        };

        // load it here
        if ($scope.settlementStorage === undefined) {
//            console.warn('$scope.settlementStorage is ' + $scope.settlementStorage);
            var res = $scope.getJSONfromAPI('settlement','get_storage', 'loadStorage');
            res.then(
                function(payload) {
                    $scope.settlementStorage = payload.data;
                    $scope.refreshRollups();
                },
                function(errorPayload) {
                    console.error("Could not retrieve settlement storage from API!" + errorPayload);
                }
            );
        };
    };

    //
    // load on init!
    //
    $scope.loadStorage();

});


app.controller("settlementSheetAdminTabController", function($scope) {
    // controller for the admin tab; new in V4 2020-08
    $scope.abandonSettlement = function() {
        showFullPageLoader();
        $scope.postJSONtoAPI('settlement','abandon',{})
    };

    $scope.removeSettlement = function() {
        if ($scope.scratch.confirmRemove === 'DELETE') {
            showFullPageLoader();
            $scope.postJSONtoAPI('settlement','remove',{},false,false,false)
        };
    };

});
