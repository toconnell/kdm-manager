app.controller ("huntPhaseRootController", function($scope) {

    $scope.deck = [];
    $scope.drawn = []

    $scope.draw = function(){
        var rand = $scope.deck[Math.floor(Math.random() * $scope.deck.length)];
        $scope.deck.splice($scope.deck.indexOf(rand), 1);
        $scope.drawn.push(rand);
    };

    $scope.cards = {
        random: {
            handle: 'random_event',
            name: 'Random Event',
            subtitle: 'basic hunt event',
            desc: "Roll d100 on the <b>Hunt Event Table</b>",
            optional: false,
        },
        baby_and_the_sword: {
            handle: 'baby_and_the_sword',
            name: 'Baby and the Sword',
            subtitle: 'basic hunt event',
            desc: "The survivors find a woman's corpse riddled with arrows. It rests in the center of a pattern drawn in blood, a screaming infant in one hand and a sword in the other. As the survivors approach, a massive worm bursts from the ground blocking their way! The survivors may Grab & Dash.",
            optional: true,
        },
        object_of_desire: {
            handle: 'object_of_desire',
            name: 'Object of Desire',
            subtitle: 'lonely tree hunt Event',
            desc: "The survivors see a tree in the distance, reaching up from the horizon like a desparate, gnarled hand. Players may nominate a survivor with 3+ courage to <b>Investigate</b>. If they do, add the <b>Lonley Tree</b> terrain card to the showdown setup and roll on the table.",
            optional: true,
        },
        dead_warrior: {
            handle: 'dead_warrior',
            name: 'Dead Warrior',
            subtitle: 'basic hunt event',
            desc: "The survivors stop a man's length away from a one-handed skeleton clad in ancient, rusted armor. A strange tablet covered in inscriptions lies next to it. If the settlement has <b>Pictographs</b>, a survivor with 3+ understanding may investigate.",
            optional: true,
        },
    }

    $scope.include = []
    $scope.includeCard = function(card) {

        if ($scope.include.indexOf(card.handle) == -1) {
            $scope.include.push(card.handle);
        } else {
            $scope.include.splice($scope.include.indexOf(card.handle), 1);
        };

        if (card.included == true) {
            card.included = false
        } else {
            card.included = true
        };
        console.warn(card.included);
    };

    $scope.shuffleDeck = function() {
        $scope.deck = [];
        $scope.drawn = [];

        var random = 12;
        for(var i=0; i < random; i++){
            $scope.deck.push($scope.cards.random);
        };
        for(var i=0; i < $scope.include.length; i++){
            var handle = $scope.include[i];
            $scope.deck.push($scope.cards[handle]);
        };


        console.warn($scope.include);
    };


});
