user_creation_and_auth = {
    "new_user": {
        "name": "/new/user",
        "key": True,
        "desc": """\
<p>Include the valid email address and password in the JSON body of your
<b>POST</b> to create a new user:</p>
<code>{'username': 'demo@kdm-manager.com', 'password': 'tehH4x0r'}</code>
<p> If you get a 200 back from the API, the user was created without
issue. Otherwise, this route produces some pretty explicit feedback when it
returns anything other than a 200.</p>\
""",
    },
    "login": {
        "name": "/login",
        "desc": """\
<p>
    The KD:M API uses JSON Web Tokens (<a
    href="https://jwt.io/">https://jwt.io</a>) to manage user
    sessions and user authentication.
</p>
<p>
    <b>POST</b> to this route with JSON containing user credentials in
    the body of the request to get a token:</p>
    <code>{"username": "demo@kdm-manager.com", "password": "l33th4x0r"}</code>
    <p>...if your credential checks out, you get a token and the the
    the user's ID (see below for working with users) back. Easy!</p>\
	""",
    },
}

password_reset = {
    "reset_password_request_code": {
        "name": "/reset_password/request_code",
        "desc": """\
<p> Resetting a password is a two-part process: first, you request a recovery
code by posting a registered user's email address to this route. This emails
your user with a URL that they can use to reset their password. <p>
<p> To request a recovery code, simply <b>POST</b> some JSON containting the
email of the user:</p>
<code>{'username': 'demo@kdm-manager.com'}</code>
<p>If this comes back 200, then the user has been emailed. Otherwise, if you
get a non-200 response, it'll have specific reasons why it did not work.</p>
<p>Additionally, if you want to handle the password reset in your own app
(the default app is https://kdm-manager.com), which you probably do, just
include the <code>app_url</code> attribute in your post:</p>
<code>
    {'username': 'demo@kdm-manager.com',
    'app_url': 'https://my-badass-kdm-app.com'}
</code>
<p>Assuming that the user email is legint, <b>POST</b>ing this value will
cause the email that the user receives to include your URL:</p>
<code><pre>
Hello demo@kdm-manager.com!

 You are receiving this message because https://my-badass-kdm-app.com recieved
a password reset request for your user, demo@kdm-manager.com.

 If you did not initiate a password reset request, please ignore this email
and continue to use your existing/current credentials: they will not be
altered in any way!

 If you made this request and would like to reset your password, please sign
https://my-badass-kdm-app.com?recover_password=True&recovery_code=MC9AU4I4NFYKJ3TWPLWVPHX29N2U08
</pre></code>
<p>From here, you would parse the user's request to your (badass) app, get their
email address and the password they want to use, and then use the
<code>/reset_password/reset</code> endpoint (below) to finish the job.</p>
<p><b>PROTIP:</b> the recovery URL that the API generates for the email
starts at the question mark, so you can put in whatever endpoint you need on
your own app, e.g. "https://my-badass-kdm-app/reset_password" or similar.
Just be careful not to use a trailing slash!</p>\
        """,
    },
    "reset_password_reset": {
        "name": "/reset_password/reset",
        "desc": """\
<p> Before you <b>POST</b> to this route, you need a recovery code.<p>
<p>Once you have it, include it with the user's email and <b>new</b> password in
the body of your request:</p>
<code>{'username': 'demo@kdm-manager.com', 'password': 's3cr3tP4ss',
'recovery_code': '9FH3BKSNFI37FB476ZHABNDOWHEUSYAB234'}</code>
<p>If your post comes back with a 200, then the user's password has been changed
to the password you <b>POST</b>ed, and you can use it to log them in.</p>
        """,
    },
}

ui_ux_helpers = {
    "get_random_names": {
        "name": "/get_random_names/10",
        "methods": ["GET"],
        "desc": """\
<p>Returns <code>count</code> random names for each possible survivor sex.</p>
<p><b>Important!</b>This method DOES NOT accept <b>POST</b>-type requests and
<code>count</code> must be an integer!</p>
<p>Output looks like this:</p>
                <pre><code>{
    "M": [
        "Fingal",
        "Pelagius",
        "Stark"
    ],
    "F": [
        "Hope",
        "Moana",
        "Rasha"
    ]
}
</code></pre>
        """,
    },
    "get_random_surnames": {
        "name": "/get_random_surnames/10",
        "methods": ["GET"],
        "desc": """\
<p>Returns <code>count</code> random surnames.</p>
<p>Output is just an array of strings:</p>
<pre><code>[
    "Skyhunter",
    "Darkhunter",
    "Stormson",
    "Butcher",
    "Hammerheart"
]</code></pre>
<p><b>Important!</b>This method DOES NOT accept <b>POST</b>-type
requests and <code>count</code> must be an integer!</p>\
        """,
    },
}

dashboard = {
    "settings_json": {
	"name": "/settings.json",
	"desc": """\
<p><b>DEPRECATED: 2019-01-13.</b> This route is going away! Consider using <code>/stat</code> instead</p>
<p> Not strictly a part of the API, but sometimes useful. Hit this route to
 download an attachement of the API's <code>settings.cfg</code> as JSON.</p>
	""",
    },
    "settings": {
	"name": "/settings",
	"desc": """\
<p><b>DEPRECATED: 2019-01-13.</b> This route is going away! Consider using <code>/stat</code> instead</p>
<p>Retrieve the API's <code>settings.cfg</code> file as JSON.</p>
	""",
    },
    "stat": {
	"name": "/stat",
	"desc": """\
<p>This is an ultra lightweight version of what you get from <code>/settings</code>.</p>
<p>This returns fewer details, but comes back in about half as much time
(about 50ms versus 100ms).</p>
	""",
    },
    "world": {
	"name": "/world",
	"desc": """\
<p> Retrieve a JSON representation of aggregate/world stats.</p>
	""",
    },
}

game_asset_lookups = {
    "game_asset_campaign": {
        "name": "/game_asset/campaign",
        "desc": """\
<p>Accepts a <code>name</code> or <code>handle</code> parameter included in the body
of the request (which should be JSON) and returns a JSON
representation of a campaign asset:</p>
<code>{"name": "People of the Lantern"}</code>
<p>...gets you back something like this:</p>
<code>{"handle": "people_of_the_lantern","milestones":
["first_child", "first_death", "pop_15", "innovations_5",
"game_over" ], "saviors": "1.3.1", "name": "People of the Lantern",
"default": true, "principles": ["new_life", "death", "society",
"conviction"], "always_available": { "location": ["Lantern
Hoard"], "innovation": ["Language"]},"nemesis_monsters": [
"butcher", "kings_man","the_hand","watcher"],"quarries": [
"white_lion","screaming_antelope","phoenix", "beast_of_sorrow",
"great_golden_cat", "mad_steed", "golden_eyed_king"],"type":
"campaign_definition"}</code>
<p>This also works with handles, e.g.:</p>
<code>{"handle": "people_of_the_stars"}</code>
<p>Like all lookup routes, if you <b>GET</b> this endpoint,
the API will return the definitions of all assets.</p>
        """,
    },
    "game_asset_expansion": {
        "name": "/game_asset/expansion",
        "desc": """\
<p><b>POST</b> a <code>name</code> or <code>handle</code> to this endpoint
to get a particular expansion's asset definition.</p>
<p>For example, if you <b>POST</b> this:</p>
<code>{handle: "gorm"}</code>
<p>You'll get back a nice hunk of JSON definiting the asset:</p>
<pre><code>{
    "ui": {
        "pretty_category": "Quarry"
    },
    "quarries": [
        "gorm"
    ],
    "name": "Gorm",
    "always_available": {
        "location": [
            "Gormery",
            "Gormchymist"
        ],
        "innovation": [
            "Nigredo"
        ]
    },
    "released": {
        "$date": 1457913600000
    },
    "type_pretty": "Expansion",
    "timeline_add": [
        {
            "handle": "gorm_approaching_storm",
            "type": "story_event",
            "ly": 1
        },
        {
            "handle": "gorm_gorm_climate",
            "type": "settlement_event",
            "name": "Gorm Climate",
            "ly": 2
        }
    ],
    "handle": "gorm",
    "type": "expansion",
    "sub_type": "expansion",
    "flair": {
        "color": "EAE40A",
        "bgcolor": "958C83"
    }
}</code></pre>
<p>This route also supports lookups via <code>name</code> values,
e.g. <code>{name: "Flower Knight"}</code> or similar.</p>
<p>If you <b>GET</b> this route, it will return the definitions
for all supported expansion content as a dictionary/hash.</p>
        """,
    },
    "game_asset_gear": {
        "name": "/game_asset/gear",
        "desc": """\
<p><b>POST</b> a <code>name</code> or <code>handle</code> to this endpoint
to do gear lookups:</p>
<code>{handle: "lantern_halberd"}</code>
<p>...gets you back a JSON representation of the asset:</p>
<pre><code>{
    "handle": "lantern_halberd",
    "name": "Lantern Halberd",
    "rules": [
        "Reach 2",
        "Irreplaceable",
        "Unique"
    ],
    "type_pretty": "Gear",
    "keywords": [
        "weapon",
        "melee",
        "two-handed",
        "spear",
        "other"
    ],
    "type": "gear",
    "sub_type": "rare_gear",
    "desc": "After attacking, if standing, you may move up to 2 spaces directly away from the monster."
}</code></pre>
<p>This route also supports <code>name</code> lookups, e.g. <code>
{name: "Vespertine Bow"}</code>, etc.</p>
<p><b>GET</b> this endpoint to dump all gear.</p>
        """,
    },
    "game_asset_monster": {
        "name": "/game_asset/monster",
        "desc": """\
<p>
    Accepts a "name" or "handle" parameter in the <b>POST</b> body and
    returns a JSON representation of a monster type game asset.
    For example, <b>POST</b>ing to /monster with JSON such as this:
</p>
<code>{"name": "White Lion Lvl. 1"}</code>
<p>...returns JSON like this: </p>
<code>{"comment": "Lvl. 1", "handle": "white_lion", "name":
"White Lion", "level": 1, "levels": 3, "sort_order": 0, "type":
"quarry"}</code>
<p>Or, with a handle:</p>
<code>{"handle": "manhunter"}</code>
<p>...you get:</p>
<pre><code>{
    "handle": "manhunter",
    "name": "Manhunter",
    "levels": 4,
    "sort_order": 103,
    "type": "nemesis",
    "selectable": false,
    "misspellings": ["THE MANHUNTER", "MAN HUNTER"],
}</code></pre>
<p>Like all lookup routes, if you <b>GET</b> this endpoint,
the API will return the definitions of all assets.</p>
        """,
    },
}
