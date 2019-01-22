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
        "name": "Attribtue set",
        "desc": """Use the routes below to set a settlement's individual attributes, e.g. Name, Survival Limit, etc. to a specific value. <p>Attributes such as Survival Limit, Population and Death Count are more or less automatically managed by the API, but you may use the routes in this section to set them directly. Be advised that the API calculates "base" values for a number of numerical attributes and will typically set attributes to that base if you attempt to set them to a lower value.</p>""",
    },
    "settlement_update_attribute": {
        "name": "Attribute update",
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
        "desc": """Routes for adding, removing and working with settlement locations.""",
    },
    "settlement_manage_innovations": {
        "name": "Innovations",
        "desc": """Routes for adding, removing and working with settlement innovations.""",
    },
    "settlement_manage_timeline": {
        "name": "Timeline",
        "desc": """<a id="timelineDataModel"></a> use these routes to manage the
settlement's timeline.
<p> Make sure you you are familiar with the data model for the timeline
(documented in the paragraphs below) before using these routes.</p>
<p>At the highest level, every settlement's <code>sheet.timeline</code>
element is a list of hashes, where each hash represents an individual
lantern year.</p>
<p>Within each Lantern Year, the keys's values are lists of events, except
for the <code>year</code> key, which is special because it is the only
key in the Lantern Year hash whose value is an integer, instead of a list.</p>
<p>The other keys in the hash, the ones whose values are lists of events,
have to be one of the following:
<ul class="embedded">
    <li><code>settlement_event</code></li>
    <li><code>story_event</code></li>
    <li><code>special_showdown</code></li>
    <li><code>nemesis_encounter</code></li>
    <li><code>showdown_event</code></li>
</ul>
Individual events are themselves hashes. In the 1.2 revision of the
timeline data model, individual event hashes have a single key/value
pair: they either have a <code>handle</code> key, whose value is an
event handle (e.g. from the settlement JSON's <code>game_assets.events
</code> element) or a a <code>name</code> key, whose value is an
arbitrary string.</p>
<p>In generic terms, here is how a settlement's <code>
sheet.timeline</code> JSON is structured:</p>
                    <pre><code>
[
    {
        year: 0,
        showdown_event: [{name: 'name'}],
        story_event: [{handle: 'handle'}]
    },
    {year: 1, special_showdown: [{name: 'name'}], settlement_event: [{handle: 'handle'}]}
    {year: 2, }
    {year: 3, nemesis_encounter: [{name: 'name'}, {name: 'name'}], story_event: [{name: 'name'}, {handle: 'handle'}]}
    ...
]</code></pre>
<p><b>Important!</b> Individual Lantern Year hashes need not
contain any event list hashes, but they <u>absolutely must contain a
hash with the <code>year</code> key/value pair.</u></p>
<p>Any attempt to <b>POST</b> a Lantern Year without this 'magic'
key/value pair, e.g. using the <code>replace_lantern_year</code>
route below, will cause the API to throw an error.</p>
<p>Also, for now, the API does not enforce any normalization or business logic
for the timeline and individual event lists may contain as many
event hashes as necessary.</p>
<p>Finally, the API should <b>always</b> render the list of Lantern
Year hashes (i.e. <code>sheet.timeline</code> in "chronological"
order. If you get them back out of order, open a ticket.</p>
        """,
    },
    "settlement_admin_permissions": {
        "name": "Settlement administrators",
        "desc": """Each settlement has at least one administrator who serves as
        the primary owner/admin maintainer of the settlement. Each settlement
        can have as many administrators as necessary. Use these endpoints to
        add and remove admins from the lsit of settlement admins.""",
    },
    "settlement_notes_management": {
        "name": "Settlement notes",
        "desc": """Much like survivors, settlements can have notes appended to
        (or removed from them). These are stored with a creation timestamp for
        easy representation in chronological or reverse chron order. """,
    },
}
