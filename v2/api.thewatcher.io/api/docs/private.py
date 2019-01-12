authorization_token_management = {
    "authorization_check": {
        "name": "/authorization/check",
        "desc": """\
<p><b>GET</b> or <b>POST</b> to this endpoint to determine if your Authorization
header is still valid or if it has expired.</p>""",
    },
    "authorization_refresh": {
        "name": "/authorization/refresh",
        "desc": """\
<p> Use the standard 'Authorization' header and <b>POST</b> an empty request to
this route to recieve a new Auth token based on the previous one.</p>
<p> On the back end, this route reads the incoming 'Authorization' header and,
even if the JWT token is expired, will check the 'login' and 'password' (hash)
keys: if they check out, you get a 200 and a brand new token.</p>
<p> Finally, the KDM API does NOT use refresh tokens (it just feels like
overkill, you know?).</p>\
"""
    },
}

administrative_views_and_data = {
    "admin_view_panel": {
        "name": "/admin/view/panel",
        "methods": ["GET","OPTIONS"],
        "desc": """\
<p>Access the API Admin panel. Uses HTTP basic auth (no cookies/no sessions)
and requires a user have the 'admin' bit flipped on their user.</p>
        """,
    },
    "admin_get_user_data": {
        "name": "/admin/get/user_data",
        "methods": ["GET","OPTIONS"],
        "desc": """\
<p>Retrieves a nice, juicy hunk of JSON re: recent users of the API.</p>
        """,
    },
    "admin_get_logs": {
        "name": "/admin/get/logs",
        "methods": ["GET","OPTIONS"],
        "desc": """\
<p>Dumps the contents of a number of system logs from the local filesystem where
the API is running and represents them as JSON.</p>
        """,
    },
}


user_management = {
    "user_get": {
        "name": "/user/get/&lt;user_id&gt;",
        "methods": ["GET", "OPTIONS"],
        "desc": """\
<p>Retrieve a serialized version of the user who owns &lt;user_id&gt;,
to include some additional usage and meta facts about that user.</p>
<p>Like many of the <code><b>GET</b></code> routes supported by the KD:M API,
this route will return user info whether you use <code><b>POST</b></code> or
any other supported method.</p>
        """,
    },
    "user_dashboard": {
        "name": "/user/dashboard/&lt;user_id&gt;",
        "methods": ["GET", "OPTIONS"],
        "desc": """\
<p>This fetches a serialized version of the user that includes the
<code>/world</code> output as well as a bunch of info about the
user, including their friends, settlements they own or are
playing in, etc.</p>
<p>Here's a run-down of the key elements:</p>
<pre><code>{
    "is_application_admin": true,
    "meta": {...},
    "user": {...},
    "preferences": [...],
    "dashboard": {
        "campaigns": [...],
        "settlements": [...],
    },
}</code></pre>
<p>The top-level <code>dashboard</code> element includes two arrays:
<code>campaigns</code> and <code>settlements</code>.</p>
<p>The <code>campaigns</code> array is a <b>reverse-chronological</b> list
of OIDs of all settlements where the user owns a survivor (i.e.
the survivor's <code>email</code> attribute matches the users
<code>login</code> attribute.</p>
<p>This list can include settlements owned/created by other users:
the basic idea behing the <code>campaigns</code> list is that
you probably want to show these settlements to the user when they
sign in or when they choose which settlement they want to view.</p>
<p>The <code>campaigns</code> array <u>does not</u> include any
'abandoned' settlements (i.e. any settlement with a Boolean True
value for the <code>abandoned</code> attribute.</p>
<p>See <a href="/#settlementAbandon"><code>/settlement/abandon/oid</code>
 (below)</a> for more on abandoning a settlement. </p>
<p>Conrastively, the <code>settlements</code> array is a
<b>chronologically</b> sorted list of all settlement OIDs that belong
 to the current user, whether abandoned or not.</p>
<p>This is more of an archival/historical sort of list, meant to
facilitate that kind of view/list/UX.</p>
""",
    },
    "user_set": {
        "name": "/user/set/&lt;user_id&gt;",
	"subsection": "user_attribute_management",
        "desc": """\
<p>This route supports the assignment of user-specified key/value
attributes to the user object.</p><p>To set an attribute, include
JSON in the body of the request that indicates the key/value to set.</p>
Supported attribute keys include:
    <table class="embedded_table">
        <tr><th>key</th><th>value</th></tr>
        <tr>
            <td>current_settlement</td>
            <td class="text">
                OID of an existing,non-removed settlement.
            </td>
        </tr>
    </table>
Use multiple key/value pairs to set multiple attributes in a single
request, e.g. <code>{"current_settlement": $oid, "current_session":
$oid}</code>
</p>
<p><b>Important!</b> This route does not support the assignment of
arbitrary keys and will completely fail any request that includes
unsupported keys!</p>
        """,
    },
    "user_set_preferences": {
        "name": "/user/set_preferences/&lt;user_id&gt;",
	"subsection": "user_attribute_management",
        "desc": """\
<p><b>POST</b> a list of hashes to this endpoint to set user preferences.</p>
<p>Your list has to be named <code>preferences</code> and your
hashes have to be key/value pairs where they key is a valid
preferences handle and the key is a Boolean:</p>
<code>{preferences: [{handle: "beta", value: true}, {...}]}</code>
<p>Since this is mostly a sysadmin/back-of-house kind of route,
it fails pretty easily if you try to <b>POST</b> something it doesn't
like. The good news, is that it should fail pretty descriptively.</p>
        """,
    },
    "user_add_expansion_to_collection": {
        "name": "/user/add_expansion_to_collection/&lt;user_id&gt;",
        "subsection": "user_collection_management",
        "desc": """\
<p>You can <b>POST</b> a single expansion handle to this endpoint
to add it to a user's collection of expansions:</p>
<code>{handle: "manhunter"}</code>
        """,
    },
    "user_rm_expansion_from_collection": {
        "name": "/user/rm_expansion_from_collection/&lt;user_id&gt;",
        "subsection": "user_collection_management",
        "desc": """\
<p><b>POST</b> some basic JSON to this endpoint to remove an expansion handle
from a user's collection:</p>
<code>{handle: "flower_knight"}</code>
        """,
    },
}


create_assets = {
    "new_settlement": {
        "name": "/new/settlement",
        "methods": ["POST","OPTIONS"],
        "desc": """\
<p>Use 'handle' values from the <code>/game_asset/new_settlement</code>
route (see above) as params, like this:</p>
<code><pre>{
    "campaign": "people_of_the_lantern",
    "expansions": ["dung_beetle_knight", "lion_god"],
    "survivors": ["adam", "anna"],
    "name": "Chicago",
    "special": ["create_first_story_survivors"]
}</pre></code>
<p>If successful, this route returns a serialized version of the new settlement,
including its OID, as JSON.</p>
<p>The following <code>special</code> values are supported by the API:</p>
<table class="embedded_table">
    <tr><th>value</th><th>result</th></tr>
    <tr>
     <td class="key">create_first_story_survivors</td>
     <td class="value">Creates two male and two female survivors,
     assigns them names and places Founding Stones and Cloths in
     Settlement Storage.</td>
    </tr>
    <tr>
     <td class="key">create_seven_swordsmen</td>
     <td class="value">Creates seven random survivors with the
    'Ageless' and Sword Mastery A&Is. </td>
    </tr>
</table>
<p><b>Important!</b> Unsupported <code>special</code> values are ignored.</p>\
        """,
    },
    "new_survivor": {
        "name": "/new/survivor",
	"methods": ["POST", "OPTIONS"],
        "desc": """\
<p>This works differently from <code>/new/settlement</code> in
a number of significant ways.</p>
<p> In a nutshell, the basic idea here is that the only required key
in the JSON you <b>POST</b> to this route is an object ID for the settlement
to which the survivor belongs:</p>
<code>{'settlement': '59669ace4af5ca799c968c94'}</code>
<p> Beyond that, you are free to supply any other attributes of the
survivor, so long as they comply with the data model for survivors.</p>
<p> Consult the <a href="/#survivorDataModel">Survivor Data Model (below)</a> for a
complete reference on what attributes of the survivor may be set at
creation time.</p>
<p>As a general piece of advice, it typically makes more sense to
just initialize a new survivor with defaults and then operate on it
using the routes below, unless you're doing something inheritance.</p>
<p>For normal inheritance, simply <b>POST</b> the OID's of one or
more of the survivor's parents like so:</p>
<code>{settlement: '59669ace4af5ca799c968c94', father: '5a341e6e4af5ca16907c2dff'}</code>
<p>...or like so:</p>
<code>{settlement: '59669ace4af5ca799c968c94', father: '5a341e6e4af5ca16907c2dff', mother: '5a3419c64af5ca11240f519f'}</code>
<p>This will cause normal inheritance rules to be triggered when the
new survivor is created.</p>
<p>In order to trigger conditional or special inheritance, e.g. where
an innovation requires the user to select a single parent as the donor,
you <u>must</u> specify which parent is the donor using the <code>
primary_donor_parent</code> key and setting it to 'father' or 'mother':</p>
<code>{settlement: '59669ace4af5ca799c968c94', father: '5a341e6e4af5ca16907c2dff', mother: '5a3419c64af5c
a11240f519f', primary_donor_parent: 'father'}</code>
<p>This will cause normal inheritance rules to be triggered when the
new survivor is created.</p>
<p>In order to trigger conditional or special inheritance, e.g. where
an innovation requires the user to select a single parent as the donor,
you <u>must</u> specify which parent is the donor using the <code>
primary_donor_parent</code> key and setting it to 'father' or 'mother':</p>
<code>{settlement: '59669ace4af5ca799c968c94', father: '5a341e6e4af5ca16907c2dff', mother: '5a3419c64af5ca11240f519f', primary_donor_parent: 'father'}</code>
<p>This will cause innovations such as <b>Family</b> to use the primary
donor parent to follow one-parent inheritance rules for that innovation.</p>
<p>As of API releases > 0.77.n, survivors can be created with an avatar.
Inclde the <code>avatar</code> key in the <b>POST</b> body, and let
that key's value be a string representation of the image that should
be used as the survivor's avatar.</p>
<p>(<a href="/#setAvatarAnchor">See <code>/survivor/set_avatar/<oid></code> route below</a> for more
information on how to post string representations of binary content.</p>
<p><b>Important!</b>Just like the <code>/new/settlement</code> route,
a successful <b>POST</b> to the <code>/new/survivor</code> route will return
a serialized version (i.e. JSON) of the new survivor, complete with
the <code>sheet</code> element, etc.</p>
        """,
    },
    "new_survivors": {
        "name": "/new/survivors",
	"methods": ["POST", "OPTIONS"],
        "desc": """\
<p>Not to be confused with <code>/new/survivor</code> (above),
this route adds multiple new survivors, rather than just one.</p>
<p>The JSON you have to <b>POST</b> to this route is a little different
and more limited than what you would post to <code>/new/survivor</code>.</p>
<p>The following <b>POST</b> key/value pairs are the only ones supported
by this route:</p>
<table class="embedded_table">
<tr><th>key</th><th>O/R</th><th>value type</th><th>comment</th>
<tr>
    <td>settlement_id</td>
    <td><b>R</b></td>
    <td>settlement OID</td>
    <td class="text">The OID of the settlement to which the new survivors belong.</td>
</tr>
<tr>
    <td>public</td>
    <td>O</td>
    <td>boolean</td>
    <td class="text">
        The value of the new survivors'<code>public</code> attribute.
        Defaults to <code>true</code>.
    </td>
</tr>
<tr>
    <td>male</td>
    <td>O</td>
    <td>arbitrary int</td>
    <td class="text">The number of male survivors to create.</td>
</tr>
<tr>
    <td>female</td>
    <td>O</td>
    <td>arbitrary int</td>
    <td class="text">The number of female survivors to create.</td>
</tr>
<tr>
    <td>father</td>
    <td>O</td>
    <td>survivor OID</td>
    <td class="text">The OID of the survivor that should be the father of the new survivors.</td>
</tr>
<tr>
    <td>mother</td>
    <td>O</td>
    <td>survivor OID</td>
    <td class="text">The OID of the survivor that should be the mother of the new survivors.</td>
</tr>
</table>
<p>Creating new survivors this way is very simple. This JSON, for
example, would create two new male survivors:</p>
<code>{"male": 2, "settlement_id": "5a1485164af5ca67035bea03"}</code>
<p>A successful <b>POST</b> to this route always returns a list of
serialized survivors (i.e. the ones that were created), so if
you are creating more than four or five survivors, this route is
a.) going to take a couple/few seconds to come back to you and b.)
is going to drop a pile of JSON on your head. YHBW.</p>
<p>NB: this route <i>does not</i> support random sex assignment.</p>
        """,
    },
}

settlement_management = {
    "settlement_get_settlement_id": {
        "name": "/settlement/get/&lt;settlement_id&gt;",
        "methods": ["GET", "OPTIONS"],
        "desc": """\
<p> Retrieve a serialized version of the settlement associated
with &lt;settlement_id&gt; (to include all related user and game
assets, including survivors).</p>
<p><b>Important!</b> Depending on the number of expansions, survivors,
users, etc. involved in a settlement/campaign, this one can take a
long time to come back (over 2.5 seconds on Production hardware).
YHBW</p>
	""",
    },
    "settlement_get_summary_settlement_id": {
        "name": "/settlement/get_summary/&lt;settlement_id&gt;",
        "methods": ["GET", "OPTIONS"],
        "desc": """\
<p>Get a nice, dashboard-friendly summary of a settlement's info.</p>
<p>This route is optimized for speedy returns, e.g. the kind you want when
showing a user a list of their settlements.</p>
        """,
    },
    "settlement_get_campaign_settlement_id": {
        "name": "/settlement/get_campaign/&lt;settlement_id&gt;",
        "methods": ["GET", "OPTIONS"],
        "desc": """\
<p>Retrieve a serialized version of the settlement where the
<code>user_assets</code> element includes the <code>groups</code>
list, among other things, and is intended to be used in creating
'campaign' type views.</p>
<p>Much like the big <code>get</code> route for settlements, this one
can take a while to come back, e.g. two or more seconds for a normal
settlement. YHBW.</p>
        """,
    },
    "settlement_get_sheet_settlement_id": {
        "name": "/settlement/get_sheet/&lt;settlement_id&gt;",
        "methods": ["GET", "OPTIONS"],
        "desc": """\
<p>A convenience endpoint that only returns the settlement's <code>sheet</code>
element, i.e. the dictionary of assets it owns.</p>
        """,
    },
    "settlement_get_game_assets_settlement_id": {
        "name": "/settlement/get_game_assets/&lt;settlement_id&gt;",
        "methods": ["GET", "OPTIONS"],
        "desc": """\
<p>A convenience endpoint that only returns the serialized settlement's <code>
game_assets</code> element, i.e. the JSON representation of the game assets
(gear, events, locations, etc.) required to represent the settlement. </p>
        """,
    },
    "settlement_get_event_log_settlement_id": {
        "name": "/settlement/get_event_log/&lt;settlement_id&gt;",
	"subsection": "settlement_component_gets",
        "desc": """\
<p><b>GET</b> this end point to retrieve all settlement event log
entries (in a giant hunk of JSON) in <u>reverse chronological
order</u>, i.e. latest first, oldest last.</p>
<p>PROTIP: For higher LY settlements this can be a really huge
list and take a long time to return: if you're a front-end
developer, definitely consider loading this one AFTER you have
rendered the rest of your view.</p>
<p>Another way to optimize  here is to include a filter key/value
pair in your <b>POST</b> body to limit your results. Some of the
accepted filter params will decrease the time it takes for your
requested lines to come back from the API:
<table class="embedded_table">
<tr><th>key</th><th>value type</th><th>scope</th>
<tr>
    <td>lines</td>
    <td>arbitrary int</td>
    <td class="text">Limit the return to the last <code>lines</code>-worth of lines: <code>{lines: 1
0}</code>. Note that this <u>does not</u> make the query or the return time better or faster for settlements with large event logs.</td>
</tr>
<tr>
    <td>ly</td>
    <td>arbitrary int</td>
    <td class="text">Limit the return to event log lines created <u>during</u> an arbitrary Lantern Year, e.g. <code>{ly: 9}</code>.<br/> Note:<ul><li>This will always return <i>something</i> and you'll get an empty list back for Lantern Years with no events.</li><li>This param triggers a performance-optimized query and will return faster than a general call to the endpoint with no params.</li></ul>
</tr>
<tr>
    <td>get_lines_after</td>
    <td>event log OID</td>
    <td class="text">Limit the return to event log lines created <u>after</u> an event log OID: <cod
e>{get_lines_after: "5a0370b54af5ca4306829050"}</code></td>
</tr>
<tr>
    <td>survivor_id</td>
    <td>arbitrary survivor's OID</td>
    <td class="text">Limit the return to event log lines that are tagged with a survivor OID: <code>
{survivor_id: "5a0123b54af1ca42945716283"}</code></td>
</tr>
</table>
<p><b>Important!</b> Though the API will accept multiple filter
params at this endpoint, <b>POST</b>ing more than one of the
above can cause...unexpected output. YHBW.</p>
        """,
    },
    "settlement_get_storage_settlement_id": {
        "name": " /settlement/get_storage/&lt;settlement_id&gt;",
	"methods": ['GET','OPTIONS'],
	"subsection": "settlement_component_gets",
        "desc": """\
<p>Hit this route to get representations of the settlement's storage.</p>
<p>What you get back is an array with two dictionaries, one for resources
and one for gear:</p>
<pre><code>[
    {
        "storage_type": "resources",
        "total":0,
        "name":"Resource",
        "locations": [
            {
                "bgcolor":"B1FB17",
                "handle":"basic_resources",
                "name":"Basic Resources",
                "collection": [
                    {
                        "handle":"_question_marks",
                        "name":"???",
                        "rules":[],
                        "consumable_keywords": ["fish","consumable","flower"],
                        "type_pretty": "Resources",
                        "keywords": ["organ","hide","bone","consumable"],
                        "desc":"You have no idea what monster bit this is. Can be used as a bone, organ, or hide!",
                        "type":"resources",
                        "sub_type":"basic_resources",
                        "quantity":0,"flippers":false
                    },
                    ...
                ],
                ...
            },
    },
], </pre></code>
<p>This JSON is optimized for representation via AngularJS, i.e. iteration over
nested lists, etc.</p>
<p>Each dictionary in the main array has an array called <code>locations</code>,
which is a list of dictionaries where each dict represents a location within the
settlement.</p>
<p>Each location dictionary has an array called <code>collection</code> which is
a list of dictionaries where each dictionary is a piece of gear or a resource.</p>
<p>The attributes of the dictionaries within the <code>collection</code> array
include the <code>desc</code>, <code>quantity</code>, etc. of an individual
game asset (piece of gear or resource or whatever).</p>
        """,
    },


	#
	#	settlement SET attributes
	#

    "settlement_set_name_settlement_id": {
        "name": "/settlement/set_name/&lt;settlement_id&gt;",
        "subsection": "settlement_set_attribute",
        "desc": """\
<p><b>POST</b> some JSON whose body contains the key 'name' and whatever the
new name is going to be as that key's value to change the settlement's
name:</p>
<code>{'name': 'The Black Lantern'}</code>
<p><b>Important!</b> Submitting an empty string will cause the API to
default the settlement's name to "UNKNOWN". There are no technical
reasons (e.g. limitations) for this, but it breaks the display in most
client apps, so null/empty names are forbidden.</p>
        """,
    },
    "settlement_set_attribute_settlement_id": {
        "name": "/settlement/set_attribute/&lt;settlement_id&gt;",
        "subsection": "settlement_set_attribute",
        "desc": """\
<p><b>POST</b> some basic JSON containing an 'attribute' and a 'value'
key where 'attribute' is an integer settlement attrib and 'value' is
the new value:</p>
<code>{'attribute': 'survival_limit', 'value': 3}</code>
<p> This route also supports incrementing the <code>population</code>
 and <code>death_count</code> attributes. </p>
	""",
    },
    "settlement_set_inspirational_statue_settlement_id": {
        "name": "/settlement/set_inspirational_statue/&lt;settlement_id&gt;",
        "subsection": "settlement_set_attribute",
        "desc": """\
<p>Set the settlement's <code>inspirational_statue</code> attrib
by <b>POST</b>ing a Fighting Art handle to this route:</p>
<code>{'handle': 'leader'}</code>
<p>This route will actually check out the handle and barf on you
if you try to <b>POST</b> an unrecognized FA handle to it. YHBW.</p>
	""",
    },
    "settlement_set_lantern_research_level_settlement_id": {
        "name": "/settlement/set_lantern_Research_level/&lt;settlement_id&gt;",
        "subsection": "settlement_set_attribute",
        "desc": """\
<p>Set the Settlement's Lantern Research Level with some basic
JSON:</p>
<code>{'value': 3}</code>
<p>This route is preferably to a generic attribute setting route
becuase it a.) ignores values over 5 and b.) forces the attrib,
which is not part of the standard data motel, to exist if it does
not.</p>
<p>Definitely use this instead of <code>set_attribute</code>.</p>
	""",
    },
    "settlement_update_set_lost_settlements_settlement_id": {
        "name": "/settlement/set_lost_settlements/&lt;settlement_id&gt;",
        "subsection": "settlement_set_attribute",
        "desc": """\
<p>Use this route to set a settlement's Lost Settlements total.</p>
<p><b>POST</b> some JSON containing the new value to set it to:</p>
<code>{"value": 2}</code>
<p>The above code would set the settlement's Lost Settlements total
to two; negative numbers will default to zero. </p>
	""",
    },


	#
	#	settlement UPDATE attributes
	#

    "settlement_update_attribute_settlement_id": {
        "name": "/settlement/update_attribute/&lt;settlement_id&gt;",
        "subsection": "settlement_update_attribute",
        "desc": """\
<p><b>POST</b> some JSON containing an 'attribute' and a 'modifier'
key where 'attribute' is an integer settlement attrib and 'mofier' is
how much you want to increment it by:</p>
<code>{'attribute': 'death_count', 'modifier': -1}</code>
<p> This route also supports incrementing the <code>survival_limit
</code> and <code>death_count</code> routes.</p>
	""",
    },
    "settlement_update_population_settlement_id": {
        "name": "/settlement/update_population/&lt;settlement_id&gt;",
        "subsection": "settlement_update_attribute",
        "desc": """\
<p><b>POST</b> some JSON containing the key 'modifier' whose value is
an integer that you want to add to the settlement's population
number.<p>
<p>This works basically identically to the <code>update_attribute</code>
route, so considering using that route instead. </p>
<p>For example, this JSON would add two to the settlement's
population number:</p>
<code>{'modifier': 2}</code>
<p><b>POST</b> negative numbers to decrease.</p>
<p><b>Important!</b> Settlement population can never go below zero,
so any 'modifier' values that would cause this simply cause the
total to become zero.</p>\
	""",
    },
    "settlement_replace_game_assets_settlement_id": {
        "name": "/settlement/replace_game_assets/&lt;settlement_id&gt;",
        "subsection": "settlement_update_attribute",
        "desc": """\
<p>This route functions nearly identically to the other update-type routes in
this subsection, except for one crucial difference: it works on list-type
attributes of the settlement (whereas the others mostly work on string or
integer type attributes).</p>
<p>This route accepts a list of <code>handles</code> and a <code>type</code>
of game asset and then evalutes the settlement's current handles of that type,
removing and adding as necessary in order to bring the settlement's list in sync
with the incoming list. </p>
<p>Your POST body needs to define the attribute <code>type</code>
you're trying to update, as well as provide a list of handles
that represent the settlement's current asset list:</p>
<pre><code>{
    "type": "locations",
    "handles": [
        "lantern_hoard","bonesmith","organ_grinder"
    ]
}</code></pre>
<p>Finally, a couple of tips/warnings on this route:<ul>
    <li>The <code>handles</code> list/array is handled by the API as if it were a set, i.e. duplicates are silently ignored.</li>
    <li>If any part of the update fails (i.e. individual add or remove operations), the whole update will fail and <u>no changes to the settlement will be saved</u>.</li>
    <li>This route does not support Location or Innovation levels! (Use <code>set_location_level</code> or <code>set_innovation_level</code> for that.)</li>
</ul></p>
	""",
    },
    "settlement_update_endeavor_tokens_settlement_id": {
        "name": "/settlement/update_endeavor_tokens/&lt;settlement_id&gt;",
        "subsection": "settlement_update_attribute",
        "desc": """\
<p>Use this route to change a settlement's endeavor token count.</p>
<p><b>POST</b> some JSON containing the number to modify by:</p>
<code>{"modifier": 2}</code>
<p>The above code would add two to the settlement's current total,
whereas the code below would decrement by one:</p>
<code>{"modifier": -1}</code>
	""",
    },
    "settlement_update_toggle_strain_milestone_settlement_id": {
        "name": "/settlement/toggle_strain_milestone/&lt;settlement_id&gt;",
        "subsection": "settlement_update_attribute",
        "desc": """\
<p>You may <b>POST</b> some JSON containing the key <code>handle</code>
and the value of a strain milestone handle to toggle that strain
milestone on or off for the settlement:</p>
<code>{"handle": "ethereal_culture_strain"}</code>
<p>The API will fail if unknown <code>handle</code> values are <b>POST</b>ed.</p>
	""",
    },


	#
	#	bulk survivor management
	#

    "settlement_update_survivors_settlement_id": {
        "name": "/settlement/update_survivors/&lt;settlement_id&gt;",
        "subsection": "settlement_manage_survivors",
        "desc": """\
<p>Use this route to update a specific group of survivors, e.g.
Departing survivors.</p>
<p><b>POST</b> some JSON including the type of survivors to include,
the attribute to modify, and the modifier:</p>
<code>{include: 'departing', attribute: 'Insanity', modifier: 1}</code>
<p><b>Important!</b> This route currently only supports the
<code>include</code> value 'departing' and will error/fail/400 on
literally anything else.</p>\
	""",
    },


	#
	#	settlement: manage expansions
	#

    "settlement_update_add_expansions_settlement_id": {
        "name": "/settlement/add_expansions/&lt;settlement_id&gt;",
        "subsection": "settlement_manage_expansions",
        "desc": """\
<p>Add expansions to a settlement by <b>POST</b>ing a list of expansion handles.
The body of your post should be a JSON-style list:</p>
<code>{'expansions': ['beta_challenge_scenarios','dragon_king']}</code>
<p>
Note that this route not only updates the settlement sheet, but also
adds/removes timeline events, updates the settlement's available game
assets (e.g. items, locations, etc.).
</p>
	""",
    },
    "settlement_update_rm_expansions_settlement_id": {
        "name": "/settlement/rm_expansions/&lt;settlement_id&gt;",
        "subsection": "settlement_manage_expansions",
        "desc": """\
<p>Remove expansions from a settlement by <b>POST</b>ing a list of
expansion handles. The body of your post should be a JSON-style
list:</p>
<code>{'expansions': ['manhunter','gorm','spidicules']}</code>
<p>
Note that this route not only updates the settlement sheet, but also
adds/removes timeline events, updates the settlement's available game
assets (e.g. items, locations, etc.).
</p>
<p><b>Important!</b> We're all adults here, and the KDM API will
<i>not</i> stop you from removing expansion handles for expansions
that are required by your settlement's campaign. If you want to
prevent users from doing this, that's got to be part of your UI/UX
considerations.</p>
	""",
    },


	#
	#	settlement: manage monsters
	#
    "settlement_set_current_quarry_settlement_id": {
        "name": "/settlement/set_current_quarry/&lt;settlement_id&gt;",
        "subsection": "settlement_manage_monsters",
        "desc": """\
<p>This route sets the settlement's 'current_quarry' attribute,
which is the monster that the settlement's Departing Survivors are
currently hunting.</p><p><b>POST</b> some simple JSON containing a monster
name (do not use handles for this):</p>
<code>{'current_quarry': 'White Lion Lvl 2'}</code>
<p>...or, the monster is unique:</p>
<code>{'current_quarry': 'Watcher'}</code>
<p><b>Important!</b> You're typically going to want to pull monster
names from the settlements' <code>game_assets -> defeated_monsters</code>
list (which is a list of monster names created for the settlement
based on expansion content, etc.)</p>
	""",
    },
    "settlement_add_defeated_monster_settlement_id": {
        "name": "/settlement/add_defeated_monster/&lt;settlement_id&gt;",
        "subsection": "settlement_manage_monsters",
        "desc": """\
<p><b>POST</b> a 'monster' string to this route to add it to the
settlement's list of defeated monsters:</p>
<code>{'monster': 'White Lion (First Story)}</code> or
<code>{'monster': 'Flower Knight Lvl 1'}</code>
<p><b>Important!</b> Watch the strings on this one and try to avoid
free text: if the API cannot parse the monster name and match it to
a known monster type/name, this will fail.</p>
	""",
    },
    "settlement_rm_defeated_monster_settlement_id": {
        "name": "/settlement/rm_defeated_monster/&lt;settlement_id&gt;",
        "subsection": "settlement_manage_monsters",
        "desc": """\
<p><b>POST</b> a 'monster' string to this route to remove it from the
settlement's list of defeated monsters, i.e. the <code>sheet.defeated_monsters</code>
array/list: </p>
<code>{'monster': 'Manhunter Lvl 4'}</code>
<p>Attempts to remove strings that do NOT exist in the list will
not fail (i.e. they will be ignored and fail 'gracefully').</p>
	""",
    },
    "settlement_add_monster_settlement_id": {
        "name": "/settlement/add_monster/&lt;settlement_id&gt;",
        "subsection": "settlement_manage_monsters",
        "desc": """\
<P>Use this route to add quarry or nemesis type monsters to the
settlement. <b>POST</b> some JSON containing the handle of the monster to
add it:</p>
<code>{'handle': 'flower_knight'}</code>
<p>The API will determine whether the monster is a nemesis or a quarry
and add it to the appropriate list. For nemesis monsters, use the
<code>/settlement/update_nemesis_levels</code> route (below) to manage
the checked/completed levels for that nemesis.</p>
<p>Make sure to check the settlement JSON <code>game_assets.monsters</code>
and use the correct handle for the desired monster.</p>
	""",
    },
    "settlement_rm_monster_settlement_id": {
        "name": "/settlement/rm_monster/&lt;settlement_id&gt;",
        "subsection": "settlement_manage_monsters",
        "desc": """\
<p><b>POST</b> some JSON containing a quarry or nemesis type monster handle
to remove it from the settlement's list:</p>
<code>{'handle': 'sunstalker'}</code>
<p>The API will determine whether the monster is a quarry or a nemesis.
When a nemesis monster is removed, its level detail is also removed.</p>
	""",
    },
    "settlement_update_nemesis_levels_settlement_id": {
        "name": "/settlement/update_nemesis_levels/&lt;settlement_id&gt;",
        "subsection": "settlement_manage_monsters",
        "desc": """\
<p>Use this method to update the Settlement sheet's <code>nemesis_encounters</code>
dictionary, i.e. to indicate that a nemesis encounter has occurred.</p>
<p>A typical dictionary might look like this:</p>
<code>        "nemesis_encounters": {"slenderman": [], "butcher": [1,2]}</code>
<p>In this example, the settlement has (somehow) encountered a
a level 1 Butcher, but has not yet encountered a Slenderman.</p>
<p>To update the dictionary, <b>POST</b> some JSON that includes the
nemesis monster's handle and the levels that are complete.</p>
<p><b>POST</b> this JSON to reset/undo/remove Butcher encounters:<p>
<code>{"handle": "butcher", "levels": []}</code>
<p><b>POST</b> this JSON to record an encounter with a level 1 Manhunter:</p>
<code>{"handle": "manhunter", "levels": [1]}</code>
	""",
    },
    "settlement_add_milestone_settlement_id": {
        "name": "/settlement/add_milestone/&lt;settlement_id&gt;",
        "subsection": "settlement_manage_principles",
        "desc": """\
<p><b>POST</b> a milestone handle (get it from <code>game_assets</code>
to this route to add it to the settlement's list of milestones:</p>
<code>{handle: 'game_over'}</code>
<p>...or...</p>
<code>{handle: 'innovations_5'}</code>
<p>This endpoint will gracefully fail and politely ignore dupes.</p>
	""",
    },
    "settlement_rm_milestone_settlement_id": {
        "name": "/settlement/rm_milestone/&lt;settlement_id&gt;",
        "subsection": "settlement_manage_principles",
        "desc": """\
<p><b>POST</b> a milestone handle (get it from <code>game_assets</code> to this
route to remove it from the settlement's list of milestones:</p>
<code>{handle: 'pop_15'}</code>
<p>...or...</p>
<code>{handle: 'first_death'}</code>
<p>This endpoint will gracefully fail and politely ignore attempts to remove
handles that are not present.</p>
	""",
    },
    "settlement_set_principle_settlement_id": {
        "name": "/settlement/set_principle/&lt;settlement_id&gt;",
        "subsection": "settlement_manage_principles",
        "desc": """\
<p><b>POST</b> some JSON to this route to set or unset a settlement principle.
Request the handle of the <code>principle</code> and the election you want to
make:</p>
<pre><code>
{
    principle: 'conviction',
    election: 'romantic',
}</code></pre>
<p>This route has a couple of unusual behaviors to note:</p>
	<ul>
    <li>It requires both keys (i.e. you will get a 400 back if you
    <b>POST</b> any JSON that does not include both).</li>
    <li>It will accept a Boolean for 'election', because this is how
    you 'un-set' a principle.</li>
	</ul>
<p> To un-set a principle, simply post the principle handle and set the
 <code>election</code> key to 'false':</p>
<code>{principle: 'new_life', election: false}</code>
<p> <b>Important!</b> Adding principles to (or removing them from) a
settlement automatically modifies all current survivors, in many
cases. If you've got survivor info up on the screen when you set a principle,
be sure to refresh any survivor info after <b>POST</b>ing JSON to this route!
</p>\
	""",
    },


	#
	#	location controls
	#

    "settlement_add_location_settlement_id": {
        "name": "/settlement/add_location/&lt;settlement_id&gt;",
        "subsection": "settlement_manage_locations",
        "desc": """\
<p> <b>POST</b> a location <code>handle</code> to this route to add
it to the settlement's Locations:</p>
<code>{'handle': 'bone_smith'}</code>
	""",
    },
    "settlement_rm_location_settlement_id": {
        "name": "/settlement/rm_location/&lt;settlement_id&gt;",
        "subsection": "settlement_manage_locations",
        "desc": """\
<p>This is basically the reverse of <code>add_location</code>
and works nearly identically. <b>POST</b> a JSON representation of a
Location handle to remove it from the settlement's list:</p>
<code>{'handle': 'barber_surgeon'}</code>
	""",
    },
    "settlement_set_location_level_settlement_id": {
        "name": "/settlement/set_location_level/&lt;settlement_id&gt;",
        "subsection": "settlement_manage_locations",
        "desc": """\
<p>For Locations that have a level (e.g. the People of the
Sun's 'Sacred Pool'), you may set the Location's level by posting
the <code>handle</code> of the location and the desired level:</p>
<code>{'handle': 'sacred_pool', 'level': 2}</code>
	""",
    },


	#
	#	innovation controls
	#


}

