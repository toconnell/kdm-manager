
app.controller("dashboardController", function($scope, $http) {

    $scope.setLatestChangeLog = function() {
//        console.log("getting blog");
        showCornerLoader();
        var url = 'https://www.googleapis.com/blogger/v3/blogs/3322385743551419703/posts?key=AIzaSyBAms6po9Dc82iTeRzDXMYI-bw81ufIu-0'
        var res = $http.get(url);
        res.then(
            function(payload) {
                $scope.posts = payload.data.items;

                getLatest = function() {
                    for (var i = 0; i < $scope.posts.length; i++) {
                        if ($scope.posts[i].labels.indexOf('Change Logs') === 0) {
                            return $scope.posts[i];
                        };
                    };
                };
                $scope.latest_blog_post = getLatest();
                console.log('Retrieved latest dev blog post successfully!')
                hideCornerLoader();
            },
            function(errorPayload) {
                console.error("Could not retrieve development blog posts!");
                console.error(errorPayload);
            }
        );
    };


    $scope.initWorld = function() {

        setInterval( function init() {
            showCornerLoader();

            var world_url = $scope.api_url + "world";
            $http.get(world_url).then(
                function(result) {
                    $scope.world = result.data.world;
                    console.log('Refreshed World data successfully!')
                    hideCornerLoader();
                }
            );

            return init;
            }(), 180000)

    };

});
