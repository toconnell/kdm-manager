

// locations application

app.controller("locationsController", function($scope) {
    $scope.add = function() {
        if (typeof $scope.add_location == "string") {
            var raw_loc = $scope.add_location;
            $scope.add_location = {name:raw_loc}; 
        };
        $scope.locations.push($scope.add_location);
        var params = "add_location=" + $scope.add_location.name;
        modifyAsset('settlement',$scope.settlement_id,params);
        $scope.add_location = undefined; 
    } 
    $scope.relist = function(loc) {
        $scope.locations.splice( $scope.locations.indexOf(loc), 1 );
        $scope.locations_options.push(loc);
    };
});


// principles application

app.controller('principlesController', function($scope, $http) {
    $scope.unset = {"name": "Unset Principle","value": "None"}
    $scope.toggle_on = function(elem_id) {
        var bullet = document.getElementById(elem_id + "_bullet_span");
        bullet.classList.add("checked_kd_toggle_bullet");
    };
    $scope.set = function(input_element,principle,selection) {
        var params = "set_principle_" + principle + "=" + selection;
        modifyAsset('settlement',$scope.settlement_id,params);
        var bulletParent = document.getElementById(principle + " principle");
        var target_bullets = bulletParent.getElementsByTagName('label');
        for (i = 0; i < target_bullets.length; i++) {
            $scope.toggle_off(target_bullets[i]);            
        }
        $scope.toggle_on(input_element);
    };
    $scope.toggle_off = function(toggle_element) {
        var input_element = toggle_element;
        input_element.style.fontWeight = "normal";
        var bullet = document.getElementById(input_element.id.slice(0,-5) + "_bullet_span");
        bullet.classList.remove("checked_kd_toggle_bullet");
    };
    $scope.unset_principle = function () {
        target_principle = $scope.unset.name;
        console.log(target_principle);
        var bulletParent = document.getElementById(target_principle + " principle");
        var target_bullets = bulletParent.getElementsByTagName('label');
        for (i = 0; i < target_bullets.length; i++) {
            $scope.toggle_off(target_bullets[i]);            
        }
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

