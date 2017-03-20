

app.controller("cursedItemsController", function($scope) {

    $scope.getAI = function(ai_handle) {
        var ai = $scope.settlement.game_assets.abilities_and_impairments;
        return ai[ai_handle];
    };

});

app.controller("sotfRerollController", function($scope) {

    $scope.sotfToggle = function() {
//        console.log($scope.sotf_reroll_toggle);
//        js_obj = {"sotf_reroll": $scope.sotf_reroll_toggle};
//        $scope.postJSONtoAPI('survivor', 'update_survivor', js_obj);
        params="sotf_reroll=" + $scope.sotf_reroll_toggle;
        modifyAsset("survivor", $scope.survivor._id.$oid, params);

    };

});


app.controller("controlsOfDeath", function($scope) {

    $scope.checkForCustomCOD = function() {
        if ($scope.arrayContains($scope.survivorCOD, $scope.survivor.causes_of_death) != true) {
            $scope.showCustomCOD();
        } else {console.log("no custom COD deteceted")};
    };

    $scope.showCODwarning = function (){
//        var hidden_elem_id = "CODwarning";
//        var hidden_elem = document.getElementById(hidden_elem_id);
        $('#CODwarning').show();
        $('#CODwarning').fadeOut(4500);
    };

    $scope.submitCOD = function(cod) {
        // here we're processing user input and passing it along to the MDB
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

        closeModal('modalDeath');
        showFullPageLoader();
        params="cause_of_death=" + cod_string
        modifyAsset("survivor", $scope.survivor._id.$oid, params);
        location.assign("/");
    };

    $scope.processSelectCOD = function() {
        // if the user uses the select drop-down, we do this to see what
        // to do next, e.g. whether to show the custom box
        if ($scope.survivorCOD.handle == 'custom') {
            $scope.showCustomCOD();
        } else {
            $scope.submitCOD($scope.survivorCOD);
        };
    };

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




