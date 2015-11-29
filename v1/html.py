#!/usr/bin/env python

#   standard
import Cookie
from datetime import datetime, timedelta
from string import Template
import sys

#   custom
import admin
from session import initialize
from utils import load_settings, mdb

settings = load_settings()

user_error_msg = Template('<div id="user_error_msg" class="$err_class">$err_msg</div>')

class settlement:
    form = Template("""\n\
    <form method="POST">
    <input type="hidden" name="modify" value="settlement" />
    <input type="hidden" name="asset_id" value="$settlement_id" />
    <hr />
    <input id="settlement_name" onchange="this.form.submit()" class="full_width" type="text" name="name" value="$name" placeholder="Settlement Name"/>
    <hr />
    <input onchange="this.form.submit()" class="big_number_square" type="number" name="survival_limit" value="$survival_limit" min="$min_survival_limit"/>
    <div class="big_number_caption">Survival Limit (min: $min_survival_limit)</div>
    <br /><hr />

    <input onchange="this.form.submit()" class="big_number_square" type="number" name="population" value="$population"/>
    <div class="big_number_caption">Population</div>
    <br /><hr />
    <input onchange="this.form.submit()" class="big_number_square" type="number" name="death_count" value="$death_count"/>
    <div class="big_number_caption">Death Count</div>
    <br /><hr />

        <h3>On Departure</h3>
        $departure_bonuses
        <h3>During Settlement Phase</h3>
        $settlement_bonuses


    <hr /> <!-- Logical section Break -->


                    <!-- STORAGE -->

    <div id="block_group">
    <h2>Storage</h2>
    <p>Gear and Resources may be stored without limit.</p>
    <hr />
        $storage
    <hr />
        $items_options<br /><br />
        $items_remove
     <input onchange="this.form.submit()" type="text" class="full_width" name="add_item" placeholder="Item or Resource"/>
    </div>

                    <!-- LOCATIONS -->

    <div id="block_group">
     <h2>Settlement Locations</h2>
     <p>Locations in your settlement.</p>
        <hr />
     <p>$locations</p>
     <select name="add_location" onchange="this.form.submit()">
      <option selected disabled hidden value=''>Add Location</option>
      <option>$locations_options</option>
     </select>
     <input onchange="this.form.submit()" type="text" class="full_width" name="add_location" placeholder="add custom location"/>
    </div>




    <hr />  <!-- Logical Section Break -->


                    <!-- PRINCIPLES -->

    <div id="block_group">
     <h2>Principles</h2>
     <p>The settlement's established principles.</p>

        <div class="$new_life_principle_hidden">
        <h3>New Life Principle</h3>
          <input onchange="this.form.submit()" type="radio" id="protect_button" class="radio_principle" name="new_life_principle" value="Protect the Young" $protect_the_young_checked /> 
            <label class="radio_principle_label" for="protect_button"> Protect the Young </label>
          <input onchange="this.form.submit()" type="radio" id="survival_button" class="radio_principle" name="new_life_principle" value="Survival of the Fittest" $survival_of_the_fittest_checked /> 
            <label class="radio_principle_label" for="survival_button"> Survival of the fittest </label>
        </div>

        <div class="$death_principle_hidden">
         <h3>Death Principle</h3>
          <input onchange="this.form.submit()" type="radio" id="cannibalize_button" class="radio_principle" name="death_principle" value="Cannibalize" $cannibalize_checked /> 
            <label class="radio_principle_label" for="cannibalize_button"> Cannibalize </label>
          <input onchange="this.form.submit()" type="radio" id="graves_button" class="radio_principle" name="death_principle" value="Graves" $graves_checked /> 
            <label class="radio_principle_label" for="graves_button"> Graves </label>
        </div>

        <div class="$society_principle_hidden">
         <h3>Society Principle</h3>
          <input onchange="this.form.submit()" type="radio" id="collective_toil_button" class="radio_principle" name="society_principle" value="Collective Toil" $collective_toil_checked /> 
            <label class="radio_principle_label" for="collective_toil_button"> Collective Toil </label>
          <input onchange="this.form.submit()" type="radio" id="accept_darkness_button" class="radio_principle" name="society_principle" value="Accept Darkness" $accept_darkness_checked /> 
            <label class="radio_principle_label" for="accept_darkness_button"> Accept Darkness </label>
        </div>

        <div class="$conviction_principle_hidden">
         <h3>Conviction Principle</h3>
          <input onchange="this.form.submit()" type="radio" id="barbaric_button" class="radio_principle" name="conviction_principle" value="Barbaric" $barbaric_checked /> 
            <label class="radio_principle_label" for="barbaric_button"> Barbaric </label>
          <input onchange="this.form.submit()" type="radio" id="romantic_button" class="radio_principle" name="conviction_principle" value="Romantic" $romantic_checked /> 
            <label class="radio_principle_label" for="romantic_button"> Romantic </label>
        </div>
    </div> <!-- principle block group -->


                    <!-- INNOVATIONS -->

    <div id="block_group">
     <h2>Innovations</h2>
     <p>The settlement's innovations (including weapon masteries).</p>
        <hr />
     <p>$innovations</p>
     <select name="add_innovation" onchange="this.form.submit()">
      <option selected disabled hidden value=''>Add Innovation</option>
      <option>$innovation_options</option>
     </select>
     <input onchange="this.form.submit()" type="text" class="full_width" name="add_innovation" placeholder="add custom innovation"/>
    </div>



    <hr />  <!-- Logical Section Break -->


                    <!-- TIMELINE -->

    <div id="block_group">
    <h2>Timeline</h2>
    <input onchange="this.form.submit()" class="big_number_square" type="number" name="lantern_year" value="$lantern_year"/>
    <div class="big_number_caption">Lantern Year</div>
    <br /><hr />
    $timeline
    </div>

                    <!-- MILESTONES -->

    <div id="block_group">
     <h2>Milestone Story Events</h2>
     <p>Trigger these story events when milestone condition is met.</p>

        <hr />
        <input onchange="this.form.submit()" id="first_child" type="checkbox" name="First child is born" class="radio_principle" $first_child_checked></input>
        <label for="first_child" class="radio_principle_label">First child is born</label>
        <p> &ensp; <img class="icon" src="$MEDIA_URL/icons/trigger_story_event.png" /> <b>Principle: New Life</b></p>
        <hr />
        <input onchange="this.form.submit()" id="first_death" type="checkbox" name="First time death count is updated" class="radio_principle" $first_death_checked></input>
        <label for="first_death" class="radio_principle_label">First time death count is updated</label>
        <p> &ensp; <img class="icon" src="$MEDIA_URL/icons/trigger_story_event.png" /> <b>Principle: Death</b></p>
        <hr />
        <input onchange="this.form.submit()" id="pop_15" type="checkbox" name="Population reaches 15" class="radio_principle" $pop_15_checked></input>
        <label for="pop_15" class="radio_principle_label">Population reaches 15</label>
        <p> &ensp; <img class="icon" src="$MEDIA_URL/icons/trigger_story_event.png" /> <b>Principle: Society</b></p>
        <hr />
        <input onchange="this.form.submit()" id="5_innovations" type="checkbox" name="Settlement has 5 innovations" class="radio_principle" $five_innovations_checked></input>
        <label for="5_innovations" class="radio_principle_label">Settlement has 5 innovations</label>
        <p> &ensp; <img class="icon" src="$MEDIA_URL/icons/trigger_story_event.png" /> <b>Hooded Knight</b></p>
        <hr />
        <input onchange="this.form.submit()" id="game_over" type="checkbox" name="Population reaches 0" class="radio_principle" $game_over_checked></input>
        <label for="game_over" class="radio_principle_label">Population reaches 0</label>
        <p> &ensp; <img class="icon" src="$MEDIA_URL/icons/trigger_story_event.png" /> <b>Game Over</b></p>

    </div>



    <hr /> <!-- Logical Section Break Here -->


                    <!-- QUARRIES -->

    <div id="block_group">
     <h2>Quarries</h2>
     <p>The monsters your settlement can select to hunt.</p>
    <hr />
     <p>$quarries</p>
     <select name="add_quarry" onchange="this.form.submit()">
      <option selected disabled hidden value=''>Add Quarry</option>
      <option>$quarry_options</option>
     </select>
     <input onchange="this.form.submit()" type="text" class="full_width" name="add_quarry" placeholder="add custom quarry"/>
    </div>

                    <!-- NEMESIS MONSTERS -->

    <div id="block_group">
    <h2>Nemesis Monsters</h2>
    <p>The available nemesis encounter monsters.</p>
    <hr>
    $nemesis_monsters
     <input onchange="this.form.submit()" type="text" class="full_width" name="add_nemesis" placeholder="add nemesis"/>
    </div>

                    <!-- DEFEATED MONSTERS -->

    <div id="block_group">
     <h2>Defeated Monsters</h2>
     <p>A list of defeated monsters and their level.</p>
     <hr />
     <p>$defeated_monsters</p>
     <input onchange="this.form.submit()" type="text" class="full_width" name="add_defeated_monster" placeholder="add defeated monster"/>
    </div>


                    <!-- LOST SETTLEMENTS -->
    <br />
    <input onchange="this.form.submit()" class="big_number_square" type="number" name="lost_settlements" value="$lost_settlements"/>
    <div class="big_number_caption">Lost Settlements</div>
    <br /><hr />

    </form>

    <br />
    <br /><hr/>
    <form method="POST" onsubmit="return confirm('This cannot be undone! Press OK to permanently delete this settlement forever.');"><input type="hidden" name="remove_settlement" value="$settlement_id"/><button class="error">Permanently Delete Settlement</button></form>
    <hr/>
    <br />
    \n""")

class dashboard:
    home_button = '<form method="POST"><input type="hidden" name="change_view" value="dashboard"/><button> &lt- Return to Dashboard</button></form>\n'
    headline = Template('<h2 class="full_width">$title</h2>\n')
    new_settlement_button = '<form method="POST"><input type="hidden" name="change_view" value="new_settlement" /><button class="success">+ New Settlement</button></form>\n'
    new_settlement_form = """\n\
    <form method="POST">
    <input type="hidden" name="new" value="settlement" />
    <input type="text" name="settlement_name" placeholder="Settlement Name"/ class="full_width">
    <button class="success">SAVE</button>
    </form>
    \n"""
    view_asset_button = Template("""\n\
    <form method="POST">
    <input type="hidden" name="view_$asset_type" value="$asset_id" />
    <button class="info">$asset_name</button>
    </form>
    \n""")

class login:
    """ """
    form = """\n\
    <form method="POST">
    <input class="full_width" type="text" name="login" placeholder="email"/>
    <input class="full_width" type="password" name="password" placeholder="password"/>
    <button>Go</button>
    </form>
    \n"""
    new_user = Template("""\n\
    <form method="POST">
    <input class="full_width" type="text" name="login" value="$login"/>
    <input class="full_width" type="password" name="password" placeholder="password"/>
    <input class="full_width" type="password" name="password_again" placeholder="password (again)"/>
    <button>Create New User</button>
    </form>
    \n""")

class meta:
    """ This is for HTML that doesn't really fit anywhere else, in terms of
    views, etc. Use this for helpers/containers/administrivia/etc. """
    start_head = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n<title>%s</title>\n' % settings.get("application","title")
    stylesheet = Template('<link rel="stylesheet" type="text/css" href="$url">\n')
    close_head = '</head>\n<body>\n <div id="container">\n'
    close_body = '\n </div><!-- container -->\n</body>\n</html>'
    log_out_button = Template('\n\t<form method="POST"><input type="hidden" name="remove_session" value="$session_id"/><button class="error">LOG OUT</button>\n\t</form>')

#
#   application helper functions for HTML interfacing
#

def set_cookie_js(session_id):
    """ This returns a snippet of javascript that, if inserted into the html
    head will set the cookie to have the session_id given as the first/only
    argument to this function.

    Note that the cookie will not appear to have the correct session ID until
    the NEXT page load after the one where the cookie is set.    """
    expiration = datetime.now() + timedelta(days=1)
    cookie = Cookie.SimpleCookie()
    cookie["session"] = session_id
    cookie["session"]["expires"] = expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
    return cookie.js_output()


def authenticate_by_form(params):
    """ Pass this a cgi.FieldStorage() to try to manually authenticate a user"""
    if "password_again" in params:
        if "login" in params and "password" in params:
            create_new = admin.create_new_user(params["login"].value, params["password"].value, params["password_again"].value)
            if create_new == False:
                output = user_error_msg.safe_substitute(err_class="warn", err_msg="Passwords did not match! Please re-enter.")
            elif create_new is None:
                output = user_error_msg.safe_substitute(err_class="warn", err_msg="Email address could not be verified! Please re-enter.")
            else:
                pass
    if "login" in params and "password" in params:
        auth = admin.authenticate(params["login"].value, params["password"].value)
        if auth == False:
            output = user_error_msg.safe_substitute(err_class="error", err_msg="Invalid password! Please re-enter.")
            output += login.form
        elif auth is None:
            output = login.new_user.safe_substitute(login=params["login"].value)
        elif auth == True:
            S = initialize()
            session_id = S.create_new(params["login"].value)
            render(S.current_view_html(), head=[set_cookie_js(session_id)])
    else:
        output = login.form
    return output



#
#   render() func is the only thing that goes below here.
#

def render(html, head=[], http_headers=False):
    """ This is our basic render: feed it HTML to change what gets rendered. """

    output = http_headers
    if not http_headers:
        output = "Content-type: text/html\n\n"

    output += meta.start_head
    output += '<script type="text/javascript" src="http://code.jquery.com/jquery-latest.min.js"></script>'
    output += meta.stylesheet.safe_substitute(url=settings.get("application", "stylesheet"))

    for element in head:
        output += element

    output += meta.close_head
    output += html
    output += meta.close_body

    print(output)
    sys.exit(0)     # this seems redundant, but it's necessary in case we want
                    #   to call a render() in the middle of a load, e.g. to just
                    #   finish whatever we're doing and show a page.
