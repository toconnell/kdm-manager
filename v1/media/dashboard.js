
app.controller("dashboardController", function($scope, $http) {
    $scope.scratch = {};

    $scope.toggleArrow = function(arrow){
        if ($scope.scratch[arrow] == true) {$scope.scratch[arrow] = false}
        else if ($scope.scratch[arrow] == false) {$scope.scratch[arrow] = true}
        else if ($scope.scratch[arrow] == undefined) {$scope.scratch[arrow] = true};
    };

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


    $scope.updatePassword = function(){
        if ($scope.scratch.password == $scope.scratch.password_again) {
            $scope.postJSONtoAPI('user', 'update_password', {password: $scope.scratch.password}, false);
            $scope.scratch.saved_password = true;
            $scope.scratch.password = undefined;
            $scope.scratch.password_again = undefined;
            $scope.legacySignOut($scope.user.user.current_session.$oid);
        } else {
            console.error('pw match fail');
        };
        
    };

    $scope.setPref = function(pref, setting){
        pref.value = setting;
        js_obj = {preferences: [{handle: pref.handle, value: setting}]};
        $scope.postJSONtoAPI('user','set_preferences',js_obj,false);
    };


});
