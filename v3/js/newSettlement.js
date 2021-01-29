app.controller('newSettlementController', function($scope, $http) {

    // this controller is basically a parody/travesty of an old-time HTML
    // form. we initialize a dict in $scope, the HTML elements on the view
    // update it by calling methods in this controller and we submit it
    // using the form-spoofer in main app rootScope.


    //
    //  init
    //

    $scope.newSettlement = {
        // the 'sheet' for the new settlement
        name: null,
        campaign: 'people_of_the_lantern', 
        macros: [],
        expansions: [],
        survivors: [],
    };


    //
    //  methods
    //

    $scope.setNewSettlementName = function() {
        // settlement name is captured in a div, which doesn't work with
        // ng-model. thus and so, we do this instead.
        var newName = document.getElementById('newSettlementName').innerHTML;
        $scope.newSettlement.name = newName;
        if (newName === "") {
            $scope.newSettlement.name = null;
        };        
    };

    $scope.toggleAttrib = function(type, handle) {
        // elements such as 'macros' and 'expansions' are lists; this is a
        // generic method for 'toggling' an item on or off of those lists
        var index = $scope.newSettlement[type].indexOf(handle);
        if (index == -1) {
            $scope.newSettlement[type].push(handle);
        } else {
            $scope.newSettlement[type].splice(index, 1);
        };
    };


    $scope.createSettlement = function() {
        // the main event: this is where we submit the request to the API's
        // /new/settlement endpoint and then simulate a HTML form POST to
        // change the view

        console.time('createSettlement()');

        // do UI stuff
        showFullPageLoader();
        showHide('createNewSettlementButton');
        showHide('createNewSettlementButtonLoader');

        // get auth header
        var config = {"headers": {"Authorization": $scope.jwt}};

        // create the URL and do the POST
        var url = $scope.api_url + "new/settlement";
        var creationPromise = $http.post(url, $scope.newSettlement, config); 

        creationPromise.success(function(data, status, headers, config) {
            var newSettlementId = data.sheet._id.$oid;
            $scope.postForm('view_campaign', newSettlementId);
            console.timeEnd('createSettlement()');
        });
        creationPromise.error(function(data, status, headers, config) {
            errorAlert();
            console.error('New settlement creation failed!');
            console.error(data);
            showAPIerrorModal(data, config.url);
            console.timeEnd('createSettlement()');
        });
    };
});
