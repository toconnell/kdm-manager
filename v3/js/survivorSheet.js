app.controller("survivorSheetController", function($scope) {
    // this is the root controller for the survivor sheet; it is initialized
    // at the top of the sheet, so it's like...a mini root scope, sort of.

    $scope.scratch = {}

    // tabs!
    $scope.tabsObject.tabs = [
        {
            id: 0,
            name: 'Sheet',
        },
        {
            id: 1,
            name: 'Notes',
        },
        {
            id: 2,
            name: 'Logs',
        },
        {
            id: 6,
            name: 'Admin',
        },
    ]

    // call this to set the $scope up
    $scope.initializeScope = function() {
        $scope.userPromise.then(
            function(payload) {
                // check the favorite box (or not)
                $scope.updateFavoriteBox();

                // set the understanding AI or leave it undef
                if ($scope.survivor.sheet.abilities_and_impairments.indexOf('analyze') != -1 ) {
                    $scope.scratch.understandingAI = 'analyze';
                } else if ($scope.survivor.sheet.abilities_and_impairments.indexOf('explore') != -1 ) {
                    $scope.scratch.understandingAI = 'explore';
                } else if ($scope.survivor.sheet.abilities_and_impairments.indexOf('tinker') != -1 ) {
                    $scope.scratch.understandingAI = 'tinker';
                };

                // load the partner
                $scope.loadPartnerInfo(); 
            },
            function(errorPayload) {
                console.log("Unable to initialize Survivor Sheet scope! " + errorPayload);
            }
        );
    };


    // notes

    $scope.setNewSurvivorNoteBody = function(blank) {
        // gets the note content from the editable div.
        var noteContainer = document.getElementById('survivorNoteNewNoteInput');
        if (blank) {
            noteContainer.innerHTML = ''; 
        } else {
            var newNote = noteContainer.innerHTML;
            $scope.scratch.newSurvivorNote.note = newNote;
        };
    }

    $scope.initNewSurvivorNote = function() {
        // blanks out and resets the controls;
        console.warn('Initializing new survivor note controls...');
        $scope.setNewSurvivorNoteBody(true);
        $scope.scratch.newNoteHasFocus = false;

    };

    $scope.addNewSurvivorNote = function() {

        if ($scope.scratch.newSurvivorNote.note === '') {
            console.warn('New survivor note is blank: Ignoring attempt to add...');
            return false;
        };

        var addNotePromise = $scope.postJSONtoAPI(
            'survivor',
            'add_note',
            {'note': $scope.scratch.newSurvivorNote},
            false,
            true,
            true
        );
        addNotePromise.then(
            function(payload) {
                console.info('Added survivor note!');
                $scope.ngHide('survivorNoteControls');
                $scope.initNewSurvivorNote();
            },
            function(errorPayload) {
                console.error('Failed to add survivor note!');
            }
        );

    }

    $scope.updateSurvivorNote = function(note, index) {
        // updates a note based on the value of note.update_operation

        if (note.update_operation === 'Update' || note.update_operation === undefined) {

            // get the latest/greatest body if we're doing an update
            var noteContainer = document.getElementById('survivorNoteBodyId' + note._id.$oid);
            note.note = noteContainer.innerHTML;

            $scope.postJSONtoAPI(
                'survivor',
                'update_note',
                {'note': note},
                false, true, false
            );

        } else if (note.update_operation === 'Delete') {
            // handle deletes; needs a special carve-out
            $scope.postJSONtoAPI(
                'survivor',
                'rm_note',
                {'_id': note._id.$oid}, false, true, false
            );
            note.deleted = true;
        } else {
            // throw a warning if it's anything else
            console.error("'" + note.update_operation + "' is not a valid survivor note operation!");
            console.warn('Ignoring unknown/unhandled survivor note operation...');
        }

        note.update_operation = undefined; //sets it back to the three dots

    };


    // email
    $scope.resetEmail = function() {
        console.warn('Reverting email address!');
        $scope.scratch.newSurvivorEmail = $scope.survivor.sheet.email;
    };

    $scope.setEmail = function() {

        // init
        var newEmail = $scope.scratch.newSurvivorEmail;
        if (newEmail === undefined) {$scope.resetEmail(); return false;}
        newEmail.toLowerCase();

        // now do it; only handle the failure case
        var res = $scope.postJSONtoAPI('survivor','set_email', {'email': newEmail});
        res.error(function(data, status, headers, config) {$scope.resetEmail()});
    };

    // partner controls
    $scope.setPartner = function(partner_oid) {
        $scope.survivor.sheet.partner_id = partner_oid;
        if (partner_oid == 'UNSET') {
            $scope.survivor.sheet.partner_id = undefined
            var js_obj = {partner_id: 'UNSET'}
        } else {
            var js_obj = {partner_id: partner_oid.$oid}
        };
        $scope.postJSONtoAPI('survivor','set_partner', js_obj, false);
        $scope.loadPartnerInfo(); 
    };
    $scope.loadPartnerInfo = function() {
        if ($scope.survivor.sheet.partner_id !== undefined) {
            console.log('Loading partner OID ' + JSON.stringify($scope.survivor.sheet.partner_id));
            for (var p_index in $scope.settlement.user_assets.survivors) {
                var partner = $scope.settlement.user_assets.survivors[p_index];
                if (partner.sheet._id.$oid == $scope.survivor.sheet.partner_id.$oid) {
                    $scope.partner = partner;
                };
            };
        } else {
            console.warn('Survivor has no partner.');
            $scope.partner = undefined;
            return true;
        }; 
    };

    $scope.sotfToggle = function() {
        // one-off method to toggle the SotF re-roll
        $scope.postJSONtoAPI('survivor', 'toggle_sotf_reroll', {}, false, true, true);
    };

    $scope.updateSurvival = function() {
        // this is a fancier version of what happens in the quickview
        // ultimately, it does a POST and updates the on-page $scope

        var new_total = $scope.survivor.sheet.survival;

        // enforce the max, if we're enforcing the max; always enforce the min
        if  (
                $scope.settlement.sheet.enforce_survival_limit === true && 
                new_total > $scope.settlement.sheet.survival_limit
            ) {
            new_total = $scope.settlement.sheet.survival_limit;
        } else if (new_total < 0) {
            new_total = 0;
        }; 

        $scope.postJSONtoAPI('survivor', 'set_survival', {"value": new_total}, false, true, true);
    };

    // tags / epithets
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
    $scope.addEpithet = function () {
        if ($scope.scratch.new_epithet === null) {return false};
        if ($scope.scratch.new_epithet === undefined) {console.error("'" + $scope.scratch.new_epithet + "' is not a handle!"); return false};
        if ($scope.survivor.sheet.epithets.indexOf($scope.scratch.new_epithet) == -1) {
            $scope.survivor.sheet.epithets.push($scope.scratch.new_epithet);
            var js_obj = {"handle": $scope.scratch.new_epithet, "type": "epithets"};
//            console.warn(js_obj);
            $scope.postJSONtoAPI('survivor','add_game_asset', js_obj, false);
        } else {
            console.error("Epithet handle '" + $scope.scratch.new_epithet + "' has already been added!")
        };
        $scope.initAssetLists();
    };
    $scope.rmEpithet = function (ep_index) {
        var removedEpithet = $scope.survivor.sheet.epithets[ep_index];
        $scope.survivor.sheet.epithets.splice(ep_index, 1);
        var js_obj = {"handle": removedEpithet, "type": "epithets"};
        $scope.postJSONtoAPI('survivor','rm_game_asset', js_obj, false);
    };

    // generic
    $scope.updateAttrib = function(attrib) {
        var value = $scope.survivor.sheet[attrib];
        if (value === null) {value = 0};
        if (value < 0) {value = 0};
        var js_obj = {'attribute': attrib, 'value': value};
        $scope.postJSONtoAPI('survivor', 'set_attribute', js_obj);
    };


    // favorite / retired / dead
    $scope.updateFavoriteBox = function() {
        if ($scope.survivor.sheet.favorite.indexOf($scope.user_login) == -1) {
            $scope.scratch.favoriteBox = false;
        } else {
            $scope.scratch.favoriteBox = true;
        };
    };

    //
    // toggles start here!
    //

    $scope.toggleDamage = function(loc) {
//        console.warn(loc);
        $scope.postJSONtoAPI('survivor','toggle_damage',{'location': loc}, false, true, true);
    };

    $scope.toggleCursedItem = function(handle) {
    //        console.log(handle);
        var itemIndex = $scope.survivor.sheet.cursed_items.indexOf(handle);
        if (itemIndex === -1) {
            $scope.survivor.sheet.cursed_items.push(handle);
            $scope.postJSONtoAPI('survivor','add_cursed_item', {'handle': handle}, true, true, true);
        } else {
            $scope.survivor.sheet.cursed_items.splice(itemIndex, 1);
            $scope.postJSONtoAPI('survivor','rm_cursed_item', {'handle': handle}, true, true, true);
        };
    };

    // favorite requires special logic, since it's an append
    $scope.toggleFavorite = function() {
        var user_index = $scope.survivor.sheet.favorite.indexOf($scope.user_login);
        if (user_index === -1) {
            $scope.postJSONtoAPI('survivor','add_favorite',{'user_email': $scope.user_login}, false, true, true);
            $scope.scratch.favoriteBox = true;
        } else {
            $scope.postJSONtoAPI('survivor','rm_favorite',{'user_email': $scope.user_login}, false, true, true);
            $scope.scratch.favoriteBox = false;
        };
    };

    // campaign-specific attribs
    $scope.toggleSpecialAttrib = function(sa_handle) {
        if ($scope.survivor.sheet[sa_handle] === undefined) {
            $scope.survivor.sheet[sa_handle] = true;
        } else if ($scope.survivor.sheet[sa_handle] === true) {
            $scope.survivor.sheet[sa_handle] = false;
        } else if ($scope.survivor.sheet[sa_handle] === false) {
            $scope.survivor.sheet[sa_handle] = true;
        };
        js_obj = {handle: sa_handle, value: $scope.survivor.sheet[sa_handle]};
        $scope.postJSONtoAPI('survivor','set_special_attribute',js_obj);
    }; 

    // abstracted survivor toggles
    $scope.toggleStatusFlag = function(flag) {
        $scope.postJSONtoAPI('survivor','toggle_status_flag', {'flag': flag}, false, true, true);
    };
    $scope.toggleBoolean = function(attrib) {
        $scope.postJSONtoAPI('survivor','toggle_boolean', {'attribute': attrib}, false, true, true);
    };

    // sex is a toggle 
    $scope.toggleSurvivorSex = function() {
        var new_sex = 'M'
        if ($scope.survivor.sheet.sex == 'M') {
            new_sex = 'F';
        };
        $scope.postJSONtoAPI('survivor','set_sex', {'sex': new_sex}, false, true, true);
    };


    $scope.setRetired = function() {
        var retired = false;
        if ($scope.survivor.sheet.retired != true) {retired = true};
        $scope.postJSONtoAPI('survivor','set_retired', {'retired': retired}, false, true, true)
    };

    $scope.setWeaponProficiencyAttribs = function() {
        // points
        var js_obj = {attribute: 'Weapon Proficiency', value: $scope.survivor.sheet['Weapon Proficiency']}
        var attrPromise = $scope.postJSONtoAPI('survivor', 'set_attribute', js_obj, false, true, false);
        // proficiency type
        if ($scope.survivor.sheet.weapon_proficiency_type != null) {
            attrPromise.then(
                function(payload) {
                    js_obj = {'handle': $scope.survivor.sheet.weapon_proficiency_type};
                    $scope.postJSONtoAPI('survivor', 'set_weapon_proficiency_type', js_obj, false, false, false);
                },
                function(errorPayload) {
                    console.error('Could not set weapon proficiency type!');
                }
            );
        };
        
    };

    // set the scratch.whateverAI variables. Call this whenever we have a change
    $scope.setAttributeAI = function(attribute) {

		console.info('Setting scratch.' + attribute + 'AI...');
		var handles = null
		if (attribute === 'courage'){
			handles = ['stalwart', 'prepared', 'matchmaker']
		} else if (attribute === 'understanding'){
			handles = ['analyze', 'explore', 'tinker']
		};

		if (handles === null) {
			console.error("'" + attribute + "' is not a known attribute! Cannot set scratch AI...");
			return false
		};

		var scratch_key = attribute + 'AI'
		$scope.scratch[scratch_key] = null;

        for (var i = 0; i < handles.length; i++) {
            var handle = handles[i];
            if ($scope.survivor.sheet.abilities_and_impairments.indexOf(handle) !== -1) {
                $scope.scratch[scratch_key] = handle;
            };
        };
		if ($scope.scratch[scratch_key] === undefined || $scope.scratch[scratch_key] === null) {
			console.warn('Could not set scratch.' + scratch_key + '...');
            $scope.scratch[scratch_key] = undefined;
		} else {
			console.info('Set scratch.' + scratch_key + " to '" + $scope.scratch[scratch_key] + "'!");
		};
    };

	// Updates courage; can also set the related A&I after the promise returns
    $scope.updateCourage = function() {
        var js_obj = {attribute: 'Courage', value: $scope.survivor.sheet.Courage};
        var couragePromise = $scope.postJSONtoAPI('survivor', 'set_attribute', js_obj, false, true, false);
        if ($scope.scratch.courageAI !== undefined) {
            couragePromise.then(
				function(payload){
					console.warn("Attribute updated! Setting A&I!");
		            js_obj = {
						handle: $scope.scratch.courageAI,
						type: 'abilities_and_impairments'
					};
    	        	$scope.postJSONtoAPI(
						'survivor', 'add_game_asset', js_obj, false, false, true
					);
				},
				function(errorPayload){
					console.error('Failed to update Courage!' + errorPayload);
				}
			);
        };
    };
	// Updates understanding; mirrors the method above for understanding
    $scope.updateUnderstanding = function() {
        var js_obj = {attribute: 'Understanding', value: $scope.survivor.sheet.Understanding};
        var understandingPromise = $scope.postJSONtoAPI(
			'survivor', 'set_attribute', js_obj, false, true, false
		);
        if ($scope.scratch.understandingAI !== undefined) {
			understandingPromise.then(
				function(payload){
					console.warn("Attribute updated! Setting A&I!");
		            js_obj = {
						handle: $scope.scratch.understandingAI,
						type: 'abilities_and_impairments'
					};
    		        $scope.postJSONtoAPI(
						'survivor', 'add_game_asset', js_obj, false, false, true
					);
				},
				function(errorPayload){
					console.error('Failed to update Understanding!' + errorPayload);
				}
			);
        };
    };

    // abilities and Impairments
    $scope.rmAI = function(ai_handle, ai_index) {
//        console.log(ai_handle + " index: " + ai_index);
        $scope.survivor.sheet.abilities_and_impairments.splice(ai_index, 1);
        js_obj = {"handle": ai_handle, "type": "abilities_and_impairments"};
        $scope.postJSONtoAPI('survivor', 'rm_game_asset', js_obj);
    };

    $scope.addAI = function() {
        var ai_handle = $scope.scratch.newAI;
        if (ai_handle === null || ai_handle === undefined) {return false};
        $scope.survivor.sheet.abilities_and_impairments.push(ai_handle);
        js_obj = {handle: ai_handle, type: "abilities_and_impairments"};
        $scope.postJSONtoAPI('survivor', 'add_game_asset', js_obj);
    };

});


app.controller('survivorNameController', function($scope) {
    // survivor name is an applet now. deal with it.

    $scope.scratch = {
        originalName: $scope.survivor.sheet.name,
    }

    $scope.setSurvivorName = function() {
        var nameContainer = document.getElementById('survivorName');
        var newName = nameContainer.innerHTML;
        js_obj = {name: newName};
        res = $scope.postJSONtoAPI('survivor', 'set_name', js_obj, false, true, true);
        res.then(function(payload){
            var updated_name = payload.data.sheet.name;
            $scope.scratch.originalName = updated_name;
        });
    };


    $scope.getName = function() {
        // returns an array representing the name
        var nameObject = Object;

        var nameContainer = document.getElementById('survivorName');
        $scope.survivor.sheet.name = nameContainer.innerHTML.trim();

        var nameList = $scope.survivor.sheet.name.split(' ');
        for(var i = nameList.length - 1; i >= 0; i--) {
            if(nameList[i] === undefined) {
                nameList.splice(i, 1);
            } else if (nameList[i] === null) {
                nameList.splice(i, 1);
            }
        }
        
        // first name
        nameObject.first = nameList[0];

        // middle name
        nameObject.middle = undefined;
        if (nameList.length > 2) {
            nameObject.middle = nameList.slice(1, nameList.length - 1).join(' ')
        };

        // last name
        nameObject.last = undefined;
        if (nameList.length > 1) {
            nameObject.last = nameList[nameList.length - 1]
        };

//        console.warn('got name: ');
//        console.warn('`-  first: ' + nameObject.first);
//        console.warn('`- middle: ' + nameObject.middle);
//        console.warn('`-   last: ' + nameObject.last);
        return nameObject;

    };

    $scope.renderName = function(nameObject) {
        var nameList = [];
        nameList.push(nameObject.first);
        nameList.push(nameObject.middle);
        nameList.push(nameObject.last);
        $scope.survivor.sheet.name = nameList.join(" ")
    };

    $scope.randomName = function() {
        var nameObject = $scope.getName();
        var sex = $scope.survivor.sheet.effective_sex;
        var nameList = $scope.randomSurvivorNames;
        var randomName = nameList[sex][Math.floor(Math.random() * nameList[sex].length)];
        nameObject.first = randomName;
        $scope.renderName(nameObject);
    };

    $scope.randomSurname = function() {
        var nameObject = $scope.getName();
        var nameList = $scope.randomSurnames;
        var randomSurname = nameList[Math.floor(Math.random() * nameList.length)];
        nameObject.last = randomSurname;
        $scope.renderName(nameObject);
    };
});

app.controller('disordersController', function($scope) {

    $scope.userD = {} 

    $scope.addDisorder = function() {
        var d_handle = $scope.userD.newD;
        if (d_handle === null) {return false};
        $scope.survivor.sheet.disorders.push(d_handle);
        js_obj = {"handle": d_handle, "type": "disorders"};
        $scope.postJSONtoAPI('survivor', 'add_game_asset', js_obj);
    };
    $scope.rmDisorder = function(handle, index) {
        $scope.survivor.sheet.disorders.splice(index, 1);
        js_obj = {"handle": handle, "type": "disorders"};
        $scope.postJSONtoAPI('survivor', 'rm_game_asset', js_obj);
    };


})


app.controller("affinitiesController", function($scope) {

    $scope.updateAffinity = function(element) {
        var color = element.a;
        var value = element.affValue;
//        console.log(color + "==" + value);
        $scope.survivor.sheet.affinities[color] = value;
        if (value === null) {return false};
        $scope.postJSONtoAPI('survivor','set_affinity', {'color': color, 'value': value}, false)
    };

    $scope.incrementAffinity = function(color, modifier) {
        $scope.survivor.sheet.affinities[color] += modifier;
        js_obj = {'red':0, 'blue':0, 'green':0};
        js_obj[color] += modifier;
        $scope.postJSONtoAPI('survivor','update_affinities', {"aff_dict": js_obj}, false, false);
    };

});







app.controller('fightingArtsController', function($scope) {
    $scope.userFA = {}; // if you're gonna use ng-model, you have to have a dot in there
    $scope.addFightingArt = function() {
        var fa_handle = $scope.userFA.newFA;
        if (fa_handle === null) {return false};
        $scope.survivor.sheet.fighting_arts.push(fa_handle);
        js_obj = {"handle": fa_handle, "type": "fighting_arts"};
        $scope.postJSONtoAPI('survivor', 'add_game_asset', js_obj);
    };
    $scope.rmFightingArt = function(handle, index) {
        $scope.survivor.sheet.fighting_arts.splice(index, 1);
        js_obj = {"handle": handle, "type": "fighting_arts"};
        $scope.postJSONtoAPI('survivor', 'rm_game_asset', js_obj, false);
        $scope.initAssetLists();
    };
    $scope.toggleLevel = function($event, fa_handle, level) {
        var level = Number(level);
        js_obj = {"handle": fa_handle, "level": level};
        $scope.postJSONtoAPI('survivor', 'toggle_fighting_arts_level', js_obj);
        if ($scope.arrayContains(level, $scope.survivor.sheet.fighting_arts_levels[fa_handle]) === false) {
            $scope.survivor.sheet.fighting_arts_levels[fa_handle].push(level);
        } else {
            var level_index = $scope.survivor.sheet.fighting_arts_levels[fa_handle].indexOf(level);
            $scope.survivor.sheet.fighting_arts_levels[fa_handle].splice(level_index, 1);
        };
        $event.stopPropagation();   // so we don't remove the card (below)
    };
});




app.controller('saviorController', function($scope) {

    $scope.setSaviorStatus = function(color) {
        $('#modalSavior').fadeOut(1000);
        $scope.postJSONtoAPI('survivor','set_savior_status', {'color': color})
        $scope.ngHide('modalSavior');
    };
    $scope.unsetSaviorStatus = function() {
        $('#modalSavior').fadeOut(1000);
        $scope.postJSONtoAPI('survivor','set_savior_status', {'unset': true})
        $scope.ngHide('modalSavior');
    };

});




app.controller('lineageController', function($scope) {
    $scope.maleFilter = function(s) {
        if (s.sheet._id.$oid == $scope.survivor.sheet._id.$oid) {return false};
        if (s.sheet.sex == 'M') {return true} else {return false};
    };
    $scope.femaleFilter = function(s) {
        // returns true if the survivor is female
        if (s.sheet._id.$oid == $scope.survivor.sheet._id.$oid) {return false};
        if (s.sheet.sex == 'F') {return true} else {return false};
    };
    $scope.setParent = function(role, new_oid) {
        $scope.postJSONtoAPI('survivor','set_parent', {'role': role, 'oid': new_oid}, false);
    };

    $scope.currentPartners = function(s){
        // returns true if the survivor is NOT another notch on the current
        // survivor's lipstick case
        if ($scope.survivor.sheet.intimacy_partners.indexOf(s.sheet._id.$oid) === -1)
            {return true} else {return false}; 
    };
    $scope.addIntimacyPartner = function(oid) {
    
    };
});


// avatars - what a shit show
app.controller("avatarController", function($scope) {
    $scope.scratch = {newAvatar: null};
    $scope.setAvatar = function(e) {
        var reader = new FileReader();
        reader.readAsBinaryString(e.target.files[0]);
        reader.onload = function () {
            js_obj = {avatar: btoa(reader.result)};
            var postChange = $scope.postJSONtoAPI('survivor','set_avatar',js_obj,false);
            postChange.then(
                function(payload){
                    $scope.survivor.sheet.avatar = payload.data.avatar_oid;
                }
            )
        };
        reader.onerror = function (error) {
            console.error('Base 64 conversion error: ', error);
        };
    };
});



app.controller("controlsOfDeathController", function($scope) {
    $scope.customCODdict = {
        'name': '* Custom Cause of Death',
        'handle': 'custom'
    };

    $scope.initCODlist = function() {
        // checks the game_Assets.causes_of_death and pushes the 'custom' option
        // on to it, if it's not on there already

        console.info('Initializing Cause of Death list...');

        var cod_list = $scope.settlement.game_assets.causes_of_death;
        if (cod_list[cod_list.length - 1].name === $scope.customCODdict.name) {
            console.info('Custom COD option already added to list...');
        } else {
            cod_list.push({'name': ' --- ', 'disabled': true})
            cod_list.push($scope.customCODdict)
        };

        // next, if the survivor has a COD that's not in the list, add it
        // for display purposes, so the selector isn't blank

        var has_custom_cod = true;
        if ($scope.survivor.sheet.cause_of_death !== undefined) {
            for (var i = 0; i < cod_list.length; i++) {
                var cod_dict = cod_list[i];
                if (cod_dict.name === $scope.survivor.sheet.cause_of_death) {
                    has_custom_cod = false;
                };
            }
        } else {
            has_custom_cod = false;
        };

        if (has_custom_cod) {
            console.warn('Survivor has custom cause of death! Updating options list...');
            cod_list.unshift({
                'name': $scope.survivor.sheet.cause_of_death,
                'handle': '__custom__'
                }
            );
        } else {
            console.info("Survivor cause of death '" + $scope.survivor.sheet.cause_of_death + "' is not custom...")
        };

    };

    $scope.resurrect = function() {
        // resurrects the survivor, closes the controls of death
        $scope.survivor.sheet.dead = undefined;
        $scope.survivor.sheet.cause_of_death = undefined;
        $scope.survivor.sheet.died_in = undefined
        $scope.postJSONtoAPI('survivor', 'controls_of_death', {'dead': false});
    };

    $scope.submitCOD = function(cod) {
        // get the COD from the HTML controls; POST them to the API; close
        // the modal

        if (typeof cod === 'string') {
            var cod_string = cod
        } else if (typeof cod === 'object') {
            var cod_string = cod.name;
        } else if (cod === undefined) {
            console.error("COD is undefined! Showing warning div...")
            $scope.ngShow('customCODwarning');
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
        console.info('Set survivor COD to ' + $scope.survivor.sheet.cause_of_death);
        $scope.survivor.sheet.died_in = $scope.settlement.sheet.lantern_year;
        var res = $scope.postJSONtoAPI('survivor', 'controls_of_death', cod_json, false, true, false);
        res.then(
            function(payload) {
                console.info('Survivor cause of death updated successfully!');
                console.info("Cause of death: '" + $scope.survivor.sheet.cause_of_death + "'.")
                $scope.initCODlist();
            },
            function(errorPayload) {
                console.error('Failed to update survivor cause of death!')
            }
        );
    };

    $scope.processSelectCOD = function() {
        // if the user uses the select drop-down, we do this to see what
        // to do next, e.g. whether to show the custom box
        $scope.survivorCOD = $scope.survivor.sheet.cause_of_death;
        if ($scope.survivorCOD == $scope.customCODdict.name) {
            delete $scope.survivor.sheet.cause_of_death;
            $scope.ngShow('customCODinput');
        } else {
            $scope.submitCOD($scope.survivorCOD);
        };
    };

});


app.controller("removeSurvivorController", function($scope) {
    $scope.removeSurvivor = function() {
        $scope.postJSONtoAPI('survivor', 'remove', {}, false,false,false);
    };

});


app.controller("theConstellationsController", function($scope) {
    // controls for 'The Constellations' view

    // actual methods
    $scope.unsetConstellation = function() {
        var js_obj = {"unset": true};
        $scope.postJSONtoAPI('survivor','set_constellation', js_obj);
    };

    $scope.setConstellation = function(c) {
        var js_obj = {"constellation": c};
        $scope.survivor.sheet.constellation = c;
        $scope.postJSONtoAPI('survivor','set_constellation', js_obj);
    };

});

