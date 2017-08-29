
app.controller("dashboardController", function($scope, $http) {

    $scope.initWorld = function(api_url) {
        $scope.api_url = api_url;

        setInterval( function init() {
            showCornerLoader();

            var world_url = $scope.api_url + "world";
            $http.get(world_url).then(
                function(result) {
                    $scope.world = result.data.world;
                    hideCornerLoader();
                }
            );

            return init;
            }(), 180000)

    };

});
