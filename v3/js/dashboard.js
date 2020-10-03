
app.controller("dashboardController", function($scope, $http) {
    // as usual, only initialize it if we need it
    if ($scope.scratch === undefined) {
        $scope.scratch = {};
    };

    //
    // API notifications; get
    //

    // getNotifications
    $scope.getNotifications = function() {
        console.info('[NOTIFICATIONS] Checking for notifications...');
        var notificationPromise = $http.get($scope.api_url + "get/notifications");
        notificationPromise.then(
            function(payload) {
                $scope.scratch.notifications = payload.data;
                console.info("[NOTIFICATIONS] " + $scope.scratch.notifications.length + " alerts retrieved.")
            },
            function(payload) {
                console.error("[NOTIFICATIONS] API notifications could not be loaded!")
            }
        );
    }

    // parseNotifications; sets some variables in scratch for UI/UX stuff
    $scope.parseNotifications = function() {
        $scope.scratch.kpi_notifications = 0;
        var notifications = $scope.scratch.notifications;
        for (var i = 0; i < notifications.length; i++) {
            var note = notifications[i];
            if (note.sub_type === 'kpi') {
                $scope.scratch.kpi_notifications++;
            }
        }
    }

    // load expansion data
    $scope.loadExpansionAssets = function() {
        $scope.userPromise.then(
            function(payload){
                var expansion_promise = $http.get($scope.api_url + 'game_asset/expansions');
                expansion_promise.then(
                    function(payload) {
                        $scope.expansions = payload.data;
                    },
                    function(payload) {
                        console.error("Expansions info could not be retrieved!")
                    }
                );
            }
        );
    };

    $scope.toggleUserExpansion = function(handle){
        handle_index = $scope.user.user.collection.expansions.indexOf(handle);
        if (handle_index == -1) {
            var action = "add"
        } else {
            var action = "remove"
        };

        if (action == "add") {
            $scope.user.user.collection.expansions.push(handle);
            $scope.postJSONtoAPI('user', 'add_expansion_to_collection', {handle: handle}, false);
        } else {
            $scope.user.user.collection.expansions.splice(handle_index, 1);
            $scope.postJSONtoAPI('user', 'rm_expansion_from_collection', {handle: handle}, false);
        };
    };

    $scope.setLatestChangeLog = function(api_key) {
        console.log("[ABOUT] Retrieving latest blog post...");
        showCornerLoader();
        var url = 'https://www.googleapis.com/blogger/v3/blogs/3322385743551419703/posts?key=' + api_key
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
        if ($scope.user.user.preferences[pref.handle] == setting) {
            return true
        };
        $scope.user.user.preferences[pref.handle] = setting;
        $scope.postJSONtoAPI('user','set_preferences',js_obj,false);
    };



});
