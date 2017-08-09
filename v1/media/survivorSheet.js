app.controller("survivorSheetController", function($scope) {
    // this is the root controller for the survivor sheet; it is initialized
    // at the top of the sheet, so it's like...a mini root scope, sort of.

    $scope.setSurvivorName = function() {
        $scope.postJSONtoAPI('survivor','set_name', {"name": $scope.survivor.sheet.name});
        sleep(500).then(() => {
            $scope.initializeSurvivor($scope.survivor_id);
        });
    };

    $scope.updateSex = function() {
        var sex = $scope.survivorSex.toUpperCase();
        if (sex == '') {return false};
        if (sex > 1) {sex = $scope.survivor.sheet.sex; };
        if (sex != 'M' && sex != 'F') {sex = $scope.survivor.sheet.sex; };
        if (sex != $scope.survivor.sheet.sex) {
            $scope.postJSONtoAPI('survivor','set_sex', {'sex': sex})
            $scope.initializeSurvivor($scope.survivor_id);
        } else {
            $scope.survivorSex = sex;
        };
        sleep(500).then(() => {
            $scope.initializeSurvivor($scope.survivor_id);
        });
    };

    $scope.setRetired = function() {
        $scope.postJSONtoAPI('survivor','set_retired', {'retired': $scope.retiredCheckBox})
    };

});


app.controller("affinitiesController", function($scope) {

    $scope.updateAffinity = function(element) {
        var color = element.a;
        var value = element.affValue;
//        console.log(color + "==" + value);
        $scope.survivor.sheet.affinities[color] = value;
        if (value === null) {return false};
        $scope.postJSONtoAPI('survivor','set_affinity', {'color': color, 'value': value})
    };

    $scope.incrementAffinity = function(color, modifier) {
        $scope.survivor.sheet.affinities[color] += modifier;
        js_obj = {'red':0, 'blue':0, 'green':0};
        js_obj[color] += modifier;
        $scope.postJSONtoAPI('survivor','update_affinities', {"aff_dict": js_obj});
    };

});


app.controller("attributeController", function($scope) {

    $scope.attributeTokens = [
        {
            "longName": "Movement",
            "shortName": "MOV",
            "buttonClass": "mov_token",
        },
        {
            "longName": "Accuracy",
            "shortName": "ACC",
            "buttonClass": "acc_token",
        },
        {
            "longName": "Strength",
            "shortName": "STR",
            "buttonClass": "str_token",
        },
        {
            "longName": "Evasion",
            "shortName": "EVA",
            "buttonClass": "eva_token",
        },
        {
            "longName": "Luck",
            "shortName": "LUCK",
            "buttonClass": "luck_token",
        },
        {
            "longName": "Speed",
            "shortName": "SPD",
            "buttonClass": "spd_token",
        },
    ];

    $scope.setBase = function(stat) {
        // bind the paddles to this
        if ($scope.survivor.sheet[stat] === null) {$scope.survivor.sheet[stat] = 0};
        var js_obj = {'attribute': stat, 'value': $scope.survivor.sheet[stat]};
        $scope.postJSONtoAPI('survivor', 'set_attribute', js_obj);
        sleep(500).then(() => {
            $scope.initializeSurvivor($scope.survivor_id);
        });
    };

    $scope.setDetail = function(stat, detail) {
        if ($scope.survivor.sheet.attribute_detail[stat][detail] === null) {
            $scope.survivor.sheet.attribute_detail[stat][detail] = 0;
        };
        var new_value = $scope.survivor.sheet.attribute_detail[stat][detail];
        var js_obj = {
            'attribute': stat,
            'detail': detail,
            'value': new_value,
        };
        $scope.postJSONtoAPI('survivor', 'set_attribute_detail', js_obj);
    };

    $scope.incrementBase = function(stat, modifier) {
        // bind the paddles to this
        $scope.survivor.sheet[stat] += modifier;
        var js_obj = {'attribute': stat, 'value': $scope.survivor.sheet[stat]};
        $scope.postJSONtoAPI('survivor', 'set_attribute', js_obj);
        sleep(500).then(() => {
            $scope.initializeSurvivor($scope.survivor_id);
        });
    };

    $scope.incrementDetail = function(stat, detail, modifier) {
        $scope.survivor.sheet.attribute_detail[stat][detail] += modifier;
        var js_obj = {'attribute': stat, 'detail': detail, 'value': $scope.survivor.sheet.attribute_detail[stat][detail]};
        $scope.postJSONtoAPI('survivor', 'set_attribute_detail', js_obj);
    };

});

app.controller("cursedItemsController", function($scope) {

    $scope.toggleCursedItem = function(handle) {
//        console.log(handle);
        if ($scope.survivor.sheet.cursed_items.indexOf(handle) == -1) {
            $scope.postJSONtoAPI('survivor','add_cursed_item', {'handle': handle});
        } else {
            $scope.postJSONtoAPI('survivor','rm_cursed_item', {'handle': handle});
        };
        sleep(1000).then(() => {
            $scope.initializeSurvivor($scope.survivor_id);
        });
    };

});


app.controller('secondaryAttributeController', function($scope) {
    $scope.incrementAttrib = function(attrib, modifier) {
        if ($scope.survivor.sheet[attrib] + modifier < 0) {return false};
        var js_obj = {'attribute': attrib, 'modifier': modifier};
        $scope.survivor.sheet[attrib] += modifier;
        $scope.postJSONtoAPI('survivor', 'update_attribute', js_obj);
        sleep(500).then(() => {
            $scope.initializeSurvivor($scope.survivor_id);
        });
    };
    $scope.updateAttrib = function(attrib) {
        var value = $scope.survivor.sheet[attrib];
        if (value === null) {value = 0};
        if (value < 0) {value = 0};
        var js_obj = {'attribute': attrib, 'value': value};
        $scope.postJSONtoAPI('survivor', 'set_attribute', js_obj);
        sleep(500).then(() => {
            $scope.initializeSurvivor($scope.survivor_id);
        });
    };
    $scope.setWeaponProficiencyType = function() {
        js_obj = {'handle': $scope.survivor.sheet.weapon_proficiency_type};
        $scope.postJSONtoAPI('survivor', 'set_weapon_proficiency_type', js_obj);
    };
});

app.controller('saviorController', function($scope) {

    $scope.setSaviorStatus = function(color) {
        $scope.postJSONtoAPI('survivor','set_savior_status', {'color': color})
        showCornerLoader();
        $('#modalSavior').fadeOut(1000);
        sleep(2000).then(() => {
            $scope.initializeSurvivor($scope.survivor_id);
        });
    };
    $scope.unsetSaviorStatus = function() {
        $scope.postJSONtoAPI('survivor','set_savior_status', {'unset': true})
        showCornerLoader();
        $('#modalSavior').fadeOut(1000);
        sleep(2000).then(() => {
            $scope.initializeSurvivor($scope.survivor_id);
        });
    };

});

app.controller('fightingArtsController', function($scope) {
    $scope.toggleStatusFlag = function() {
        $scope.postJSONtoAPI('survivor','toggle_status_flag', {'flag': 'cannot_use_fighting_arts'});
        $scope.initializeSurvivor($scope.survivor_id); // because this could affect SA's, etc.
    };
});

app.controller('skipNextHuntController', function($scope) {
    $scope.toggleStatusFlag = function() {
        $scope.postJSONtoAPI('survivor','toggle_status_flag', {'flag': 'skip_next_hunt'});
    };
});

app.controller('abilitiesAndImpairmentsController', function($scope) {

    //
    //  initialize!
    //

    $scope.init = function() {
        if ( typeof $scope.survivor_sheet !== "undefined") {
            $scope.setAIoptions();
        }
        else {
            setTimeout($scope.init, 250);
        }
    };
    $scope.init();

    // define the option setter

    $scope.setAIoptions = function() {
        $scope.setGameAssetOptions('abilities_and_impairments', "survivor_sheet", "AIoptions", "curse");
    };


    //
    //  regular methods below here
    //

    $scope.rmAI = function(ai_handle, ai_index) {
//        console.log(ai_handle + " index: " + ai_index);
        js_obj = {"handle": ai_handle, "type": "abilities_and_impairments"};
        $scope.postJSONtoAPI('survivor', 'rm_game_asset', js_obj);
        $scope.survivor.sheet.abilities_and_impairments.splice(ai_index, 1);
        sleep(500).then(() => {
            $scope.initializeSurvivor($scope.survivor_id);
        });
        $scope.setAIoptions();
    };

    $scope.addAI = function() {
        var ai_handle = $scope.newAI;
        if (ai_handle === null) {return false};
        $scope.survivor.sheet.abilities_and_impairments.push(ai_handle);
        js_obj = {"handle": ai_handle, "type": "abilities_and_impairments"};
        $scope.postJSONtoAPI('survivor', 'add_game_asset', js_obj);
        sleep(1000).then(() => {
            $scope.initializeSurvivor($scope.survivor_id);
        });
        $scope.setAIoptions();
    };

});

app.controller('metaDataController', function($scope) {
    $scope.togglePublic = function() {
        $scope.postJSONtoAPI('survivor','toggle_boolean', {'attribute': 'public'});
    };
});

app.controller("survivalController", function($scope) {

    $scope.toggleStatusFlag = function() {
        $scope.postJSONtoAPI('survivor','toggle_status_flag', {'flag': 'cannot_spend_survival'});
    };

    // bound to the increment/decrement "paddles"
    $scope.updateSurvival = function (modifier) {
        new_total = $scope.survivor.sheet.survival + modifier;
        if  (
                $scope.settlement.sheet.enforce_survival_limit == true && 
                new_total > $scope.settlement.sheet.survival_limit
            ) {
            $scope.showSLwarning();
        } else if (new_total < 0) {
            console.warn("Survival cannot be less than zero!");
        } else {
            $scope.postJSONtoAPI('survivor', 'update_survival', {"modifier": modifier});
            $scope.survivor.sheet.survival += modifier;
        };
    };

    // bound to the actual number element
    $scope.setSurvival = function () {
        if ($scope.survival_input_value === null) {return false};
        if ($scope.survival_input_value === undefined) {$scope.survival_input_value = $scope.survivor.survival};
        console.warn($scope.survival_input_value);
        new_value = $scope.survival_input_value;
        if  (
                $scope.settlement.sheet.enforce_survival_limit == true && 
                new_value > $scope.settlement.sheet.survival_limit
            ) {
            $scope.showSLwarning();
            $scope.survival_input_value = $scope.settlement.sheet.survival_limit;
        } else if (new_value < 0) {
            console.warn("Survival cannot be less than zero!");
            $scope.survival_input_value = 0;
        } else {
            $scope.postJSONtoAPI('survivor', 'set_survival', {"value": new_value});
            $scope.survival_input_value = new_value;
        };
        
    };

    $scope.showSLwarning = function () {
        $('#SLwarning').show();
        $('#SLwarning').fadeOut(4500);
    };

    $scope.setSurvivalActions = function() {
        var res = $scope.getJSONfromAPI('survivor','get_survival_actions');
        res.then(
            function(payload) {
                console.log("Refreshing Survival Actions for survivor " + $scope.survivor_id);
                $scope.survivor.survival_actions = payload.data;
            },
            function(errorPayload) {console.log("Could not retrieve Survival Actions from API!" + errorPayload);}
        );
    };

});


app.controller("sotfRerollController", function($scope) {
    $scope.sotfToggle = function() {
        $scope.postJSONtoAPI('survivor', 'toggle_sotf_reroll', {});
    };

});


app.controller("controlsOfDeath", function($scope) {

    $scope.showCODwarning = function (){
        $('#CODwarning').show();
        $('#CODwarning').fadeOut(4500);
    };

    $scope.resurrect = function() {
        // resurrects the survivor, closes the controls of death
        $scope.survivor.sheet.dead = undefined;
        $scope.survivor.sheet.cause_of_death = undefined;
        $scope.survivor.sheet.died_in = undefined
        $scope.postJSONtoAPI('survivor', 'controls_of_death', {'dead': false});
        $('#modalDeath').fadeOut(1000);
    };

    $scope.submitCOD = function(cod) {
        // get the COD from the HTML controls; POST them to the API; close
        // the modal

        if (typeof cod === 'string') {
            var cod_string = cod
        } else if (typeof cod === 'object') {
            var cod_string = cod.name;
        } else if (cod === undefined) {
            console.warn("COD is undefined! Showing warning div...")
            $scope.showCODwarning();
            return false;
        } else {
            console.warn("Invalid COD type! Type was: " + typeof cod)
            return false;
        };

        // now POST the JSON back to the mother ship
        cod_json = {
            'dead': true,
            'cause_of_death': cod_string,
            'died_in': $scope.settlement.sheet.lantern_year
        };
        $scope.survivor.sheet.dead = true;
        $scope.survivor.sheet.cause_of_death = cod_string;
        $scope.survivor.sheet.died_in = $scope.settlement.sheet.lantern_year
        $scope.postJSONtoAPI('survivor', 'controls_of_death', cod_json);
        $('#modalDeath').fadeOut(1000);

    };

    $scope.processSelectCOD = function() {
        // if the user uses the select drop-down, we do this to see what
        // to do next, e.g. whether to show the custom box
        $scope.survivorCOD = $scope.survivor.sheet.cause_of_death;
        if ($scope.survivorCOD == '* Custom Cause of Death') {
            delete $scope.survivor.sheet.cause_of_death;
            $scope.showCustomCOD();
        } else {
            $scope.submitCOD($scope.survivorCOD);
        };
    };

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
            $scope.errortext = "The note has already been added!";
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

    //
    //  initialize!
    //

    $scope.init = function() {
        if ( typeof $scope.survivor_sheet !== "undefined") {
            $scope.setEpithetOptions();
        }
        else {
            setTimeout($scope.init, 250);
        }
    };
    $scope.init();

    // define the option setter

    $scope.setEpithetOptions = function() {
        $scope.setGameAssetOptions('epithets', "survivor_sheet", "epithetOptions");
    };

    $scope.$watch("epithetOptions", function() {
        // this is our totally bogus epithet sex filter. 
        if ($scope.epithetOptions === undefined) {return false};
        for (var ep_key in $scope.epithetOptions) {
            var ep = $scope.epithetOptions[ep_key];
            if (ep.sex === undefined) {
                } else if (ep.sex != $scope.survivor.sheet.effective_sex) {
                delete $scope.epithetOptions[ep_key];
            };
        };
    });



    //
    //  regular methods below here
    //

    $scope.addEpithet = function () {
        if ($scope.new_epithet === null) {return false};
        if ($scope.survivor.sheet.epithets.indexOf($scope.new_epithet) == -1) {
            $scope.survivor.sheet.epithets.push($scope.new_epithet);
            var js_obj = {"handle": $scope.new_epithet, "type": "epithets"};
//            console.warn(js_obj);
            $scope.postJSONtoAPI('survivor','add_game_asset', js_obj);
        } else {
            console.error("Epithet handle '" + $scope.new_epithet + "' has already been added!")
        };
        $scope.setEpithetOptions();
    };
    $scope.rmEpithet = function (ep_index) {
        var removedEpithet = $scope.survivor.sheet.epithets[ep_index];
        $scope.survivor.sheet.epithets.splice(ep_index, 1);
        var js_obj = {"handle": removedEpithet, "type": "epithets"};
        $scope.postJSONtoAPI('survivor','rm_game_asset', js_obj);
    };
});


app.controller("theConstellationsController", function($scope) {
    // controls for 'The Constellations' view

    // actual methods
    $scope.unsetConstellation = function() {
        var js_obj = {"unset": true};
        $scope.postJSONtoAPI('survivor','set_constellation', js_obj);
        $scope.initializeSurvivor($scope.survivor_id);
    };

    $scope.setConstellation = function(c) {
        var js_obj = {"constellation": c};
        $scope.survivor.sheet.constellation = c;
        $scope.postJSONtoAPI('survivor','set_constellation', js_obj);
        sleep(1000).then(() => {
            $scope.initializeSurvivor($scope.survivor_id);
        });
    };

});

