sections = {
    # type descriptions / header blocks
    "public": {
        "name": "Public Routes",
        "desc": """\
<p>These routes <b>DO NOT</b> require user authentication (though some of them
require a valid API key to use).</p>
<p> When building an application, use these routes to construct
dashboard type views and to look up game asset data that does not belong to any
user, such as Fighting Arts, Gear cards, etc.</p>""",
    },
    "private": {
        'name': 'Private Routes',
        'desc': """\
<p>Private routes require an Authorization header including a JWT token.</p>
<p>(See the documentation above for more info on how to <b>POST</b> user
credentials to the <code>/login</code> route to get a token.)</p>
<p>Generally speaking, when you access any private route, you want your headers
to look something like this:</p>
<code>
{
    'content-type': 'application/json',
    'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6...'
}
</code>
<p>Finally, keep in mind that tokens are extremely short-lived, so you should be
prepared to refresh them frequently. See the section below on 'Authorization
 Token Management' for more info on checking/refreshing tokens.</p>
<p><b>Important!</b> In order to support the CORS pre-flight checks that most
 browsers are going to auto-magically perform before <b>POST</b>ing to one of
these routes, <u>all private routes supported by the KD:M API also support the
<code>OPTIONS</code> method</u>.</p>\
""",
    },

    #   public routes 
    "user_creation_and_auth": {
        "name": "User creation and auth",
        "desc": """These public routes are how you want to create new users and authenticate existing ones.""",
    },
    "password_reset": {
        "name": "Password reset",
        "desc": "Use these two routes to build a password reset mechanism.",
    },
    "user_collection_management": {
        "name": "User collection management",
        "desc": "The endpoints defined below are used to manage the User's IRL collection of game assets, e.g. expansions, etc.",
    },
    "ui_ux_helpers": {
        "name": "UI/UX Helpers",
        "desc": "These routes are intended to help with user experience by rapidly returning basic asset sets.",
    },
    "dashboard": {
        "name": "Dashboard",
        "desc": "The public endpoints here are meant to be used to create a dashboard or landing page type of view for users when they first sign in.",
    },
    "game_asset_lookups": {
        "name": "Game asset lookup routes",
        "desc": """\
Use these endpoints to get information about game assets, e.g. monsters, gear, etc.
<p>Each of these routes works essentially the same way. You can
<b>POST</b> a query to one and retireve data about a single asset if you
know its name or handle -OR- you can <b>GET</b> the route to get a list
of all assets.</p>
<p> The following lookups are currently supported by the public API:</p>
<ul>
    <li><a href="/game_asset/abilities_and_impairments">
        /game_asset/abilities_and_impairments</a>
    </li>
    <li><a href="/game_asset/campaign">
        /game_asset/campaign</a> (campaign definitions)
    </li>
    <li><a href="/game_asset/disorder">
        /game_asset/disorder</a>
    </li>
    <li><a href="/game_asset/expansion">
        /game_asset/expansion</a>
    </li>
    <li><a href="/game_asset/fighting_art">
        /game_asset/fighting_art</a>
    </li>
    <li><a href="/game_asset/gear">
        /game_asset/gear</a>
    </li>
    <li><a href="/game_asset/monster">
        /game_asset/monster</a>
    </li>
    <li><a href="/game_asset/resource">
        /game_asset/resource</a>
    </li>
    <li><a href="/game_asset/rules">
        /game_asset/rules</a>
    </li>
    <li><a href="/game_asset/storage">
        /game_asset/storage</a> (settlement storage location types)
    </li>
</ul>
        """
    },

    #   private routes
    "authorization_token_management": {
        "name": "Authorization token management",
        "desc": """\
Once you've got an authorization token, you can work with it using these routes.
Most failures from these routes are reported back as 401's, since they concern
authorization.""",
    },
    "administrative_views_and_data":{
        "name": "Administrative views and data",
        "desc": "Administrative views and data:</b> If your user has the 'admin' attribute, i.e. they are an administrator of the API server, the user can hit these routes to retrieve data about application usage, etc. These endpoints are used primarily to construct the administrator's dashboard.",
    },
    "user_management": {
        "name": "User management",
        "desc": """\
All routes for working directly with a user follow a <code>/user/&lt;action&gt;/&lt;user_id&gt;</code> convention. These routes are private and require authentication.
        """,
    },
    "user_attribute_management": {
        "name": "User attribute management (and updates)",
        "desc": "These endpoints are used to update and modify individual webapp users.",
    },
    "user_collection_management": {
        "name": "User Collection management",
        "desc": "The endpoints defined in this section are used to manage the User's IRL collection of game assets, e.g. Expansions, etc."
    },
    "create_assets": {
        "name": "Create assets",
        "desc": "To create new assets (user, survivor, settlement), <b>POST</b> JSON containing appropriate params to the /new/&lt;asset_type&gt; route. Invalid or unrecognized params will be ignored!",
    },



    #
    #   settlement routes
    #

    "settlement_management": {
        "name": "Settlement management",
        "desc": """\
<p>All routes for working with a settlement follow the normal convention in the
KDM API for working with individual user assets, i.e.
<code>/settlement/&lt;action&gt;/&lt;settlement_id&gt;</code></p>
<p>Many operations below require asset handles.</p>
<p>Asset handles may be found in the settlement's <code>game_assets</code>
element, which contains dictionaries and lists of assets that are
available to the settlement based on its campaign, expansions, etc.</p>
<p>Typical settlement JSON looks like this:</p>
<pre><code>
    {
        "user_assets": {...},
        "meta": {...},
        "sheet": {...},
        "game_assets": {
            "milestones_options": {...},
            "campaign": {...},
            "weapon_specializations": {...},
            "locations": {...},
            "innovations": {...},
            "principles_options": {...},
            "causes_of_death": {...},
            "quarry_options": {...},
            "nemesis_options": {...},
            "eligible_parents": {...},
            ...
        },
    }
</code></pre>
<p><b>Important!</b> As indicated elsewhere in this documentation,
asset handles will never change. Asset names are subject to change,
and, while name-based lookup methods are supported by various routes,
using names instead of handles is not recommended.</p>
        """,
    },
    "settlement_set_attribute": {
        "name": "Set attribtue",
        "desc": """Use the routes below to set a settlement's individual attributes, e.g. Name, Survival Limit, etc. to a specific value. <p>Attributes such as Survival Limit, Population and Death Count are more or less automatically managed by the API, but you may use the routes in this section to set them directly. Be advised that the API calculates "base" values for a number of numerical attributes and will typically set attributes to that base if you attempt to set them to a lower value.</p>""",
    },
    "settlement_update_attribute": {
        "name": "Update attributes",
        "desc": """Use the routes here to update and/or toggle individual settlement attributes. <p>Updating is different from setting, in that the update-type routes will add the value you <b>POST</b> to the current value, rather than just overwriting the value in the way a set-type route would.</p>""",
    },
    "settlement_component_gets": {
        "name": "Component GET routes (sub-GETs)",
        "desc": "The two heaviest elements of a settlement, from the perspectives of both the raw size of the JSON and how long it takes for the API server to put it together, are the event log and the settlement storage. These two endpoints allow you to get them separately, e.g. behind-the-scenes, on demand or only if necessary, etc.",
    },
    "settlement_manage_survivors": {
        "name": "Bulk survivor management",
        "desc": """These routes allow you to manage groups or types of survivors within the settlement.""",
    },
    "settlement_manage_expansions": {
        "name": "Expansion content",
        "desc": """The endpoints here all you to <b>POST</b> lists of expansion content handles to update the expansion content used in the settlement.""",
    },
    "settlement_manage_monsters": {
        "name": "Monsters",
        "desc": """These routes all allow you to do things with the settlement's various lists of monsters and monster-related attributes.""",
    },
    "settlement_manage_principles": {
        "name": "Principles and Milestones",
        "desc": """Routes for setting and unsetting princples and milestones.""",
    },
    "settlement_manage_locations": {
        "name": "Locations",
        "desc": """Routes for setting and unsetting princples and milestones.""",
    },
}
