
app.controller("dashboardController", function($scope, $http) {

    $scope.setLatestChangeLog = function() {
        console.log("[ABOUT] Retrieving latest blog post...");
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
                console.log('[ABOUT] Retrieved latest dev blog post successfully!')
                hideCornerLoader();
            },
            function(errorPayload) {
                console.error("[ABOUT] Could not retrieve development blog posts!");
                console.error(errorPayload);
            }
        );
    };


});
