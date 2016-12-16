var app = angular.module('kdmManager', []);

function savedAlert() {
    $('#saved_dialog').fadeIn(500);
    $('#saved_dialog').show();
    $('#saved_dialog').fadeOut(1800);
};

// factories and services for angularjs modules

app.factory('apiService', function($http) {
    return {
        getSettlement: function(root_url, api_route, s_id) {
            return $http.post(root_url + 'settlement/' + api_route + '/' + s_id);
        }
    }
});

app.controller('rootController', function($scope, apiService) {

    $scope.initialize = function(src_view, login, is_admin, api_url, settlement_id) {
        $scope.api_url = api_url;
        $scope.settlement_id = settlement_id;
        $scope.user_login = login;
        $scope.user_is_settlement_admin = is_admin;
        $scope.view = src_view;
        console.log("appRoot controller (" + $scope.view + ") initialized!");
        console.log($scope.user_login + " admin = " + $scope.user_is_settlement_admin);
    }

    $scope.loadSettlement = function(r) {
        var api_route = r
        if (api_route == undefined) {var api_route='get';};

        // returns a promise
        return apiService.getSettlement($scope.api_url, api_route, $scope.settlement_id);
    };

    // modal div and button registration!
    $scope.registerModalDiv = function(modal_button_id, modal_div_id) {
        var btn = document.getElementById(modal_button_id);
        var modal = document.getElementById(modal_div_id);

        if (btn == undefined) {window.alert("Could not find button id " + modal_button_id)};
        if (modal == undefined) {window.alert("Could not find button id " + modal_button_id)};

        btn.onclick = function(b) {b.preventDefault(); modal.style.display = "block";};
        window.onclick = function(event) {if (event.target == modal) {modal.style.display = "none";}};

        console.log( "button: " + modal_button_id + " and div: " + modal_div_id + " are linked!");
    };

    $scope.range  = function(count) {
        var r = [];
        for (var i = 0; i < count; i++) { r.push(i) }
        return r;
    };

});


//  common and shared angularjs controllers


// Timeline Application
app.controller('timelineController', function($scope) {

    $scope.loadTimeline = function() {
        $scope.loadSettlement().then(
            function(payload) {
                $scope.settlement_sheet = payload.data.sheet;
                $scope.timeline = payload.data.sheet.timeline;
                console.log("timeline initialized!")
            },
            function(errorPayload) {console.log("Error loading timeline!", errorPayload);}
        );
        $scope.loadSettlement('event_log').then(
            function(payload) {
                $scope.event_log = payload.data;
                console.log("event_log initialized!")
            },
            function(errorPayload) {console.log("Error loading event_log!", errorPayload);}
        );

    };


    // limits $scope.event_log to only lines from target_ly
    $scope.get_event_log = function(t) {

        var target_ly = Number(t);
        local_event_log = new Array();

        for (i = 0; i < $scope.event_log.length; i++) {
            if (Number($scope.event_log[i].ly) == target_ly) {
                local_event_log.push($scope.event_log[i]);
            };
        };

//        console.log("added " + local_event_log.length + " items to local_event_log");
//        console.log($scope.local_event_log);
        return local_event_log;
    };

    $scope.showHide = function(e_id) {
        var e = document.getElementById(e_id);
        var hide_class = "hidden";
        if (e.classList.contains(hide_class)) {
            e.classList.remove(hide_class);
        } else {
            e.classList.add(hide_class)
        };
    }

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

    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/", true);
    xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded");
    var params = "modify=" + collection + "&asset_id=" + asset_id + "&" + param_string + "&norefresh=True";
//    window.alert(params);
    xhr.send(params);
    savedAlert();
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


app.controller("attributeController", function($scope) {


    $scope.getTotal = function(base,gear,tokens) {

        // generic function for computing the total value of the survivor's
        // attribute. could be a little DRYer, but FIWE: I'm a n00b at this.

        if (base == undefined) {var a = Number($scope.base_value || 0)} else {var a = Number(base)};
        if (gear == undefined) {var b = Number($scope.gear_value || 0)} else {var b = Number(gear)};
        if (tokens == undefined) {var c = Number($scope.tokens_value || 0)} else {var c = Number(tokens)};
        $scope.sum = a+b+c;
        return Number($scope.sum);
    };


    $scope.refresh = function (attrib, attrib_type, target_class) {

        // any time a user adjusts one of the inputs within the scope of our
        // controller, they call this refresh() method (even if they use the
        // increment/decrement paddles). The refresh checks all fields within
        // scope, updates the total (with innerHTML injection) and then submits
        // the incoming change back to the webapp as a survivor update

        var base = Number(document.getElementById("base_value_" + attrib + "_controller").value);
        var gear = Number(document.getElementById("gear_value_" + attrib + "_controller").value);
        var tokens = Number(document.getElementById("tokens_value_" + attrib + "_controller").value);
        var total = $scope.getTotal(base,gear,tokens);

//        window.alert("total is " + total);
        var x = document.getElementsByClassName("synthetic_attrib_total_" + attrib);
        var i;
        for (i = 0; i < x.length; i++) {
            x[i].innerHTML = total;
        };

        var source = document.getElementById(attrib_type + "_value_" + attrib + "_controller")
//        window.alert("[" + $scope.survivor_id + "] Would POST " + attrib + " -> " + attrib_type + " = " + source.value);
        var params = "angularjs_attrib_update=" + attrib + "&angularjs_attrib_type=" + attrib_type + "&angularjs_attrib_value=" + Number(source.value);
        modifyAsset("survivor", $scope.survivor_id, params);

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

// click/tap remove for the Settlement Sheet
function removeSettlementSheetAsset(html_element, group, s_id) {
//    window.alert(html_element.parentElement.classList);
    html_element.parentElement.style.display="none";
    var item_name = html_element.innerHTML.trim();
    var params = "remove_" + group + "=" + item_name;
//  window.alert(params); 
    modifyAsset("settlement", s_id, params);
};



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
    document.getElementById("mySidenav").style.width = '65%';
}
function closeNav() {
    document.getElementById("mySidenav").style.width = "0";
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
    window.alert("here");
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

// place dynamic buttons in the appropriate holder, depending on what's visible
function placeDynamicButton (button) {
    // picks the appropriate parent div for a dynamic button on the
    // Survivor Sheet. This kind of violates responsive design, because if the
    // user changes the viewport from mobile to wide, they'll lose the button
    // ...obviously a corner-case, but still makes me feel bad...

    var mobile_holder = document.getElementById("mobileButtonHolder");
    var wide_holder = document.getElementById("wideButtonHolder");

    var mq = window.matchMedia( "(min-width: 1050px) and (orientation: landscape)" );
    if (mq.matches) {
        wide_holder.appendChild(button);
    } else {
        mobile_holder.appendChild(button);
    };
}

// global func for damage toggles. 
function toggleDamage(elem_id, asset_id) {
    document.getElementById(elem_id).classList.toggle("damage_box_checked");
    var toggle_key = document.getElementById(elem_id);
    var params =  toggle_key.name + "=checked";
    modifyAsset("survivor", asset_id, params);
};


// custom toggles; we use these to insert spans (because styling bullets and
//  checkboxes and radios and whatever got to be a pain in the ass
function kd_toggle_init() {

    var toggle_box_class = 'kd_toggle_box';
    var toggles = document.getElementsByClassName(toggle_box_class);

    console.log("found " + toggles.length + " " + toggle_box_class + " elements")

    for (i = 0; i < toggles.length; i++) {
        var e = toggles[i];
        var bullet = document.createElement("span");
        bullet.classList.add("kd_toggle_bullet");
        bullet.id = e.id + "_bullet_span";
        if (e.checked == true) {
            bullet.classList.add("checked_kd_toggle_bullet"); 
            e.parentElement.style.fontWeight="bold";
        };
        e.parentElement.insertBefore(bullet,e); 
    }; 

    console.log("initialized " + toggles.length + " toggle elements");
};

function kd_toggle(toggle_element) {
    var input_element = toggle_element;
    var bullet = document.getElementById(input_element.id + "_bullet_span");
    if (bullet.classList.contains("checked_kd_toggle_bullet")) {
        bullet.classList.remove("checked_kd_toggle_bullet")
    } else {
        bullet.classList.add("checked_kd_toggle_bullet")
    };
};




// User update methods. Not a lot of these.

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





