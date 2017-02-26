function reloadSheet() {
    showFullPageLoader();
    var reload_form = document.getElementById("settlementSheetReload");
    reload_form.submit();
    console.warn("Settlement Sheet reload form submitted...");
};

app.controller("locationsController", function($scope) {
    $scope.addLocation = function() {
        showFullPageLoader();
        var loc_dict = $scope.settlement.game_assets.locations[$scope.newLocation];
        $scope.settlement_sheet.locations.push(loc_dict.name);        
        params = "add_location=" + loc_dict["name"];
        modifyAsset('settlement',$scope.settlement_id,params);
        reloadSheet();
    };
    $scope.rmLocation = function(index,loc_name) {
        showFullPageLoader();
        params = "rm_location=" + loc_name;
        $scope.settlement_sheet.locations.splice(index,1);
        modifyAsset('settlement',$scope.settlement_id,params);
        reloadSheet();
    };
    $scope.setLocationLevel = function(loc_name,lvl){
        params = "location_level_" + loc_name + "=" + lvl;
        console.log(params);
        modifyAsset('settlement',$scope.settlement_id,params);
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
        if ($scope.settlement_sheet.innovations.indexOf(innovation.handle) > -1) {return true};
        return false; 
    };
    $scope.setInnovationOptions = function() {
        var res = $scope.getJSONfromAPI('settlement','get');
        res.then(
            function(payload) {
                $scope.innovation_options = payload.data.game_assets.innovations;
                for (var k in $scope.innovation_options) {
                    if ($scope.innovation_options[k].type == "principle") {
                        delete $scope.innovation_options[k];
                    };
                };
                for (var i = 0; i < $scope.settlement_sheet.innovations.length; i++) {
                    var innovation = $scope.settlement_sheet.innovations[i];
                    delete $scope.innovation_options[innovation];
                };
//                console.log("Innovations options updated!")
            },
            function(errorPayload) {console.log("Could not retrieve innovation options from API!" + errorPayload);}
        );
    };
    $scope.setInnovationDeck = function(retry) {
        $scope.innovation_deck = null;
        $scope.spinner();
        var res = $scope.getJSONfromAPI('settlement','get_innovation_deck');
        res.then(
            function(payload) {
                $scope.innovation_deck = payload.data;
                if ($scope.innovation_deck.length < 1 && $scope.settlement_sheet.innovations.length > 0) {
                    if (retry === undefined) {
                        console.warn("Empty Innovation Deck! Retrying...")
                        $scope.setInnovationDeck(true);
                    } else if (retry === true) {
                        console.warn("Blank Innovation Deck returned after retry!")
                    } else {console.error("retry was " + retry + " which is unexpected!")};
                };
//                console.log("Innovation Deck refreshed!");
                $scope.spinner("hide");
            },
            function(errorPayload) {console.log("Could not retrieve innovation deck from API!" + errorPayload);}
        );
    };
    $scope.addInnovation = function() {
//        console.warn("Adding innovation: " + $scope.newInnovation);
        if ($scope.newInnovation === null) {return false};
        $scope.settlement_sheet.innovations.push($scope.newInnovation);
        var js_obj = {"handle": $scope.newInnovation};
        var out = $scope.postJSONtoAPI('settlement', 'add_innovation', js_obj);
        $scope.setInnovationDeck();
        $scope.setInnovationOptions();
    };    
    $scope.setInnovationLevel = function(innovation_name,lvl){
        var js_obj = {"name": innovation_name, "level": lvl};
        $scope.postJSONtoAPI('settlement', 'set_innovation_level', js_obj);
    };
    $scope.rmInnovation = function(index, innovation_handle) {
        $scope.settlement_sheet.innovations.splice(index,1);
        var js_obj = {"handle": innovation_handle};
        $scope.postJSONtoAPI('settlement', 'rm_innovation', js_obj); 
        $scope.setInnovationDeck();
        $scope.setInnovationOptions();
    };
});


app.controller('defeatedMonstersController', function($scope, $http) {
    $scope.addDefeatedMonster = function() {
        var params = "add_defeated_monster=" + $scope.dMonst;
        modifyAsset('settlement',$scope.settlement_id,params);
        $scope.settlement_sheet.defeated_monsters.push($scope.dMonst);
    };
    $scope.rmDefeatedMonster = function(index, monster) {
        var params = "rm_defeated_monster=" + monster;
        modifyAsset('settlement',$scope.settlement_id,params);
        $scope.settlement_sheet.defeated_monsters.splice(index,1);
    };
});

app.controller('quarriesController', function($scope, $http) {
    $scope.addQuarry = function(x) {
        // set the quarry handle that we're going to add; bail if it's bogus
        var quarry_handle = $scope.addQuarryMonster;
        if (quarry_handle === null) {console.error("quarry handle is null!"); return false};

        // update the settlement object; 
        $scope.settlement_sheet.quarries.push(quarry_handle);
        $scope.settlement.game_assets.quarry_options.splice(x, 1);

        // send an update to the legacy app
        params = "add_quarry=" + $scope.addQuarryMonster;
        modifyAsset('settlement',$scope.settlement_id,params);
    };
    $scope.removeQuarry = function(x,q_handle) {
        $scope.settlement_sheet.quarries.splice(x,1);
        var monster = $scope.settlement.game_assets.monsters[q_handle];
        $scope.settlement.game_assets.quarry_options.push(monster);
        params = "rm_quarry=" + q_handle;
        modifyAsset('settlement',$scope.settlement_id,params);
    };
});

app.controller('nemesisEncountersController', function($scope) {

    $scope.nemesisLvlChecked = function(n_handle,n_lvl) {
        var n_lvl_array = $scope.settlement_sheet.nemesis_encounters[n_handle];
        if ($scope.arrayContains(Number(n_lvl), n_lvl_array)) {
            return true
        } else {
            return false
        };
    };

    $scope.toggleNemesisLevel = function(n_handle,n_lvl,e) {
//        console.log(n_handle + " " + n_lvl);
//        console.log(e);
        var n_lvl_array = $scope.settlement_sheet.nemesis_encounters[n_handle];
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
        $scope.settlement_sheet.nemesis_monsters.splice(index,1);
        params = "rm_nemesis=" + handle;
        modifyAsset('settlement',$scope.settlement_id,params);
    };
    $scope.addNemesis = function() {
        $scope.settlement_sheet.nemesis_monsters.push($scope.addNemesisMonster);
        $scope.settlement_sheet.nemesis_encounters[$scope.addNemesisMonster] = [];
        params = "add_nemesis=" + $scope.addNemesisMonster
        modifyAsset('settlement',$scope.settlement_id,params);
    };

});

app.controller('principlesController', function($scope, $http) {
    $scope.set = function(principle,selection) {
        var params = "set_principle_" + principle + "=" + selection;
        modifyAsset('settlement',$scope.settlement_id,params);
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

        var params = "set_principle_" + target_principle + "=UNSET";
        modifyAsset('settlement',$scope.settlement_id,params);
    };

});

app.controller("lostSettlementsController", function($scope,$rootScope) {

    // get $scope.lost_settlements from the API
    $scope.loadLostSettlements = function() {
        $scope.loadSettlement().then(
            // once we've got a payload, build the controls
            function(payload) {
                $scope.lost_settlements = payload.data.sheet.lost_settlements;

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

//                console.log(JSON.stringify($scope.lost));
                console.log("lost_settlements control array initialized!");
            },

            function(errorPayload) {console.log("Error loading settlement!", errorPayload);}
        );
    };

    $scope.rmLostSettlement = function () {
        var cur = Number($scope.current_val);
        if (cur == 0) {
//            window.alert("At minimum!");
        }
        else { 
            cur--;
            $scope.current_val = cur;
            var params = "lost_settlements=" + cur;
            modifyAsset("settlement", $scope.settlement_id, params);
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
            var params = "lost_settlements=" + cur;
            modifyAsset("settlement", $scope.settlement_id, params);
        };
    };


    // Run this on controller init: creates the controls
    $scope.createLostSettlementControls = function() {

        if ($scope.lost_settlements == undefined) {console.log("lost_settlements count not available!")};

    };
    
});

