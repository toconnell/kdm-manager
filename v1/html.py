# coding=utf-8
#!/usr/bin/env python

#   standard
import Cookie
from datetime import datetime, timedelta
from string import Template
import sys

#   custom
import admin
import game_assets
from session import Session
from utils import load_settings, mdb, get_logger, get_latest_update_string

settings = load_settings()
logger = get_logger()

user_error_msg = Template('<div id="user_error_msg" class="$err_class">$err_msg</div>')


class panel:
    headline = Template("""\n\
    <meta http-equiv="refresh" content="30">
    <table id="panel_meta_stats">
        <tr><th colspan="2">Global Stats</th></tr>
        <tr><td>Total Users:</td><td>$users</td></tr>
        <tr class="grey"><td>Recent Users:</td><td>$recent_users_count</td></tr>
        <tr><td>Sessions:</td><td>$sessions</td></tr>
        <tr class="grey"><td>Settlements:</td><td>$settlements</td></tr>
        <tr><td>Survivors:</td><td>$live_survivors/$dead_survivors ($total_survivors total)</td></tr>
        <tr class="grey"><td>Valkyrie:</td><td>$complete_death_records complete death recs</td></tr>
        <tr><td colspan="2">$latest_fatality</td></tr>
        <tr class="grey"><td>Current Hunt:</td><td>$current_hunt</td></tr>
        <tr><td>Latest Kill:</td><td>$latest_kill</td></tr>
    </table>
    <table id="panel_kill_board">
        <tr><th colspan="2">Kill Board</th></tr>
        $defeated_monsters
    </table>
    \n""")
    log_line = Template("""\n\
    <p class="$zebra">$line</p>
    \n""")
    user_status_summary = Template("""\n\
    <div class="panel_block">
        <table class="panel_recent_user">
            <tr class="gradient_blue bold"><th colspan="3">$user_name [$u_id]</th></tr>
            <tr><td class="key">User Created:</td><td>$user_created_on_days days ago</td><td class="m_ago">$user_created_on</td></tr>
            <tr><td class="key">Latest Sign-in:</td><td>$latest_sign_in_mins m. ago</td><td class="m_ago">$latest_sign_in</td></tr>
<!--            <tr><td class="key">Latest Activity:</td><td>$latest_activity_mins m. ago</td><td class="m_ago">$latest_activity</td></tr> -->
            <tr><td class="key" colspan="3"></td></tr>
            <tr><td class="key">Latest Activity:</td><td colspan="2" class="latest_action">$latest_activity_mins m. ago</td></tr>
            <tr><td class="latest_action" colspan="3"> $latest_action</td></tr>
            <tr><td class="key" colspan="3"></td></tr>
            <tr><td class="key">Session Length:</td><td colspan="2">$session_length minutes</td></tr>
            <tr><td class="key">User Agent:</td><td colspan="2">$ua</td></tr>
            <tr><td class="key" colspan="3"></td></tr>
            <tr><td class="key">Survivors:</td><td colspan="2">$survivor_count</td></tr>
            <tr><td class="key">Settlements:</td><td colspan="2">$settlements</td></tr>
            <tr>
             <td class="key" colspan="3">
                <form>
                 <input type="hidden" value="pickle" name="export_user_data"/>
                 <input type="hidden" value="$u_id" name="asset_id"/>
                 <br/>
                &ensp; &ensp; &ensp; <button class="gradient_blue">Download User Data Pickle</button>
                 <br /><br/>
                </form>
             </td>
            </tr>
        </table>
    </div><br/>
    \n""")


class ui:
    game_asset_select_top = Template("""\n\
    <select class="$select_class" name="$operation$name" onchange="this.form.submit()">
      <option selected disabled hidden value="">$operation_pretty $name_pretty</option>
    """)
    game_asset_select_row = Template('\t  <option value="$asset">$asset</option>\n')
    game_asset_select_bot = '    </select>\n'
    game_asset_add_custom = Template("""\n\
<input onchange="this.form.submit()" type="text" class="full_width" name="add_$asset_name" placeholder="add custom $asset_name_pretty"/>
    \n""")
    text_input = Template('\t  <input onchange="this.form.submit()" type="text" class="full_width" name="$name" placeholder="$placeholder_text"/>')


class dashboard:
    # settlement administrivia; needs to be above the dashboard accordions
    panel_button = '<hr class="mobile_only"/><form method="POST"><input type="hidden" name="change_view" value="panel"/><button class="maroon change_view">Admin Panel!</button></form>\n'
    new_settlement_button = '<form method="POST"><input type="hidden" name="change_view" value="new_settlement" /><button class="success">+ New Settlement</button></form>\n'

    # flash
    down_arrow_flash = '<img class="dashboard_down_arrow" src="%s/icons/down_arrow.png"/> ' % settings.get("application", "STATIC_URL")
    campaign_flash = '<img class="dashboard_icon" src="%s/icons/campaign.png"/> ' % settings.get("application", "STATIC_URL")
    settlement_flash = '<img class="dashboard_icon" src="%s/icons/settlement.png"/> ' % settings.get("application", "STATIC_URL")
    system_flash = '<img class="dashboard_icon" src="%s/icons/system.png"/> ' % settings.get("application", "STATIC_URL")
    refresh_flash = '<img class="dashboard_icon" src="%s/icons/refresh.png"/> ' % settings.get("application", "STATIC_URL")
    event_log_flash = '<img class="dashboard_icon" src="%s/icons/settlement_event.png"/> ' % settings.get("application", "STATIC_URL")

    # dashboard accordions
    preference_block = Template("""\n
    <p>$desc</p>
    <p>
     <input style="display: none" id="pref_true_$pref_key" class="radio_principle" type="radio" name="$pref_key" value="True" $pref_true_checked/>
     <label for="pref_true_$pref_key" class="radio_principle_label"> $affirmative </label><br>
     <input style="display: none" id="pref_false_$pref_key" class="radio_principle" type="radio" name="$pref_key" value="False" $pref_false_checked /> 
     <label for="pref_false_$pref_key" class="radio_principle_label"> $negative </label> 
    </p>
    <hr/>
    \n""")
    motd = Template("""\n
	<img class="desktop_only dashboard_bg" src="%s/tree_logo_shadow.png">
    <div class="dashboard_menu">
        <h2 class="clickable gradient_silver" onclick="showHide('system_div')"> <img class="dashboard_icon" src="%s/icons/system.png"/> System %s</h2>
        <div id="system_div" style="display: none;" class="dashboard_accordion gradient_silver">
        <p>KD:M Manager! Version $version.</p><hr/>
        <p>v$version went live on $latest_change_date. <a target="top" href="$latest_change_link">View change log</a>.</p>
        <p>The Manager is currently under active development and is running in debug mode! Application source code is <a href="https://github.com/toconnell/kdm-manager" target="top">available on GitHub</a>: please <a href="https://github.com/toconnell/kdm-manager/issues" target="top">report issues here</a>.</p><hr/>
        <p>For more information or to make comments/ask questions about the project, check out the development blog at <a href="http://blog.kdm-manager.com" target="top"/>blog.kdm-manager.com</a>. </p><hr/>
        <p>About:<ul>
            <li>Developed and maintained by <a href="http://toconnell.info">Timothy O'Connell</a>.</li>
            <li>Icon font ('kdm-font-10') by <a href="http://steamcommunity.com/id/GeorgianBalloon" target="top">Miracle Worker</a>.</li>
        </ul></p><hr/>

        <div class="dashboard_preferences">
            <h3>Preferences</h3>
            <form method="POST" action="#">
            <input type="hidden" name="update_user_preferences" value="True"/>
                $user_preferences
            <button class="error"> Save/Update Preferences</button>
            </form>
        </div>

        <hr/>

        <div class="dashboard_preferences">
            <h3>Export User Data</h3>
<!--            <form method="POST" action="#">
                <input type="hidden" name="export_user_data" value="json">
                <button class="silver">JSON</button>
            </form> -->
            <form method="POST" action="#">
                <input type="hidden" name="export_user_data" value="dict">
                <button class="silver">Python Dictionary</button>
            </form>
            <form method="POST" action="#">
                <input type="hidden" name="export_user_data" value="pickle">
                <button class="silver">Python Pickle</button>
            </form>
        </div>

        <hr>

        <p>Currently signed in as: <i>$login</i> (last sign in: $last_sign_in)</p>
        $last_log_msg
        <div class="dashboard_preferences">
            <form method="POST">
            <input type="hidden" name="change_password" value="True"/>
            <input type="password" name="password" class="full_width" placeholder="password">
            <input type="password" name="password_again" class="full_width" placeholder="password (again)"/>
            <button class="warn"> Change Password</button>
            </form>
        </div>
        <hr class="desktop_only">
        <form id="logout" method="POST"><input type="hidden" name="remove_session" value="$session_id"/><input type="hidden" name="login" value="$login"/><button class="gradient_white change_view desktop_only">SIGN OUT</button>\n\t</form>
        </div>
    </div>
    """ % (settings.get("application","STATIC_URL"), settings.get("application", "STATIC_URL"), down_arrow_flash))
    campaign_summary = Template("""\n\
    <div class="dashboard_menu">
        <h2 class="clickable gradient_purple" onclick="showHide('campaign_div')"> <img class="dashboard_icon" src="%s/icons/campaign.png"/> Campaigns %s </h2>
        <div id="campaign_div" style="display: $display" class="dashboard_accordion gradient_purple">
        <p>Games you are currently playing.</p>
            <div class="dashboard_button_list">
            $campaigns
            </div>
        </div>
    </div>
    \n""" % (settings.get("application", "STATIC_URL"), down_arrow_flash))
    settlement_summary = Template("""\n\
    <div class="dashboard_menu">
        <h2 class="clickable gradient_orange" onclick="showHide('settlement_div')"> <img class="dashboard_icon" src="%s/icons/settlement.png"/> Settlements %s </h2>
        <div id="settlement_div" style="display: $display" class="dashboard_accordion gradient_orange">
        <p>Manage Settlements you have created.</p>
        <div class="dashboard_button_list">
            $settlements
            %s
        </div>
        </div>
    </div>
    \n""" % (settings.get("application", "STATIC_URL"), down_arrow_flash, new_settlement_button))
    survivor_summary = Template("""\n\
    <div class="dashboard_menu">
        <h2 class="clickable gradient_green" onclick="showHide('survivors_div')"> <img class="dashboard_icon" src="%s/icons/survivor.png"/> Survivors %s</h2>
        <div id="survivors_div" style="display: none;" class="dashboard_accordion gradient_green">
        <p>Manage survivors created by you or shared with you. New survivors are created from the "Campaign" and "Settlement" views.</p>
        <div class="dashboard_button_list">
            $survivors
        </div>
        </div>
    </div>
    \n""" % (settings.get("application", "STATIC_URL"), down_arrow_flash))
    kill_board_row = Template('<tr><td>$monster</td><td>$kills</td></tr>')
    kill_board_foot = Template('<tr><td colspan="2">&ensp; $other_list</td></tr>')
    avatar_image = Template("""\n
    <img class="latest_fatality" src="/get_image?id=$avatar_id" alt="$name"/>
    \n""")
    world = Template("""\n
    <div class="dashboard_menu world_panel">
        <h2 class="clickable gradient_blue" onclick="showHide('world_div')"> <img class="dashboard_icon" src="%s/icons/world.png"/> World %s</h2>
        <div id="world_div" style="display: none;" class="dashboard_accordion gradient_blue">


        <p>$active_settlements settlements are holding fast; $abandoned_settlements settlements have been abandoned.</p>
        <p>$live_survivors survivors are alive and fighting; $dead_survivors have perished.</p>
        <hr/>

        <h3>Settlements:</h3>
        <ul>
            <li>Multiplayer settlements: $total_multiplayer</li>
            <li>Settlements created in the last 30 days: $new_settlements_last_30</li>
        </ul>
        <p>Averages across all settlements:</p>
        <ul>
            <li>Lantern Year: $avg_ly</li>
            <li>Innovation Count: $avg_innovations</li>
            <li>Expansions: $avg_expansions</li>
            <li>Defeated Monsters: $avg_defeated</li>
            <li>Items in Storage: $avg_storage</li>
            <li>Milestone Story Events: $avg_milestones</li>
            <li>Lost Settlements: $avg_lost_settlements</li>
        </ul>
        <p>Population and death stats:</p>
        <ul>
            <li>Average Population: $avg_pop</li>
            <li>Max Population: $max_pop</li>
            <li>Average Death count: $avg_death</li>
            <li>Max Death Count: $max_death</li>
        </ul>
        <p>Survival Limit stats:</p>
        <ul>
            <li>Average Survival Limit: $avg_survival_limit</li>
            <li>Max Survival Limit: $max_survival</li>
        </ul>
        <p>Principle selection rates:</p>
        $top_principles
        <p>Settlements using expansion content:</p>
        <ul>
            $expansion_popularity_bullets
        </ul>
        $latest_settlement
        <hr/>

        <h3>Survivors:</h3>
        <p>Averages for all living survivors:</p>
        <ul>
            <li>Hunt XP: $avg_hunt_xp</li>
            <li>Insanity: $avg_insanity</li>
            <li>Courage: $avg_courage</li>
            <li>Understanding: $avg_understanding</li>
            <li>Disorders: $avg_disorders</li>
            <li>Abilities/Impairments: $avg_abilities</li>
        </ul>
        $latest_fatality
        <br class="clear_both">
        $latest_survivor
        <hr/>

        <h3>Monsters:</h3>
        <p>Latest hunt activity:</p>
        <ul>
            <li>$current_hunt</li>
        </ul>
        <p>Latest kill:</p>
        <ul>
            $latest_kill
        </ul>
        <p>Defeated Monster Totals:
            <table class="dashboard_world_defeated_monsters">
            $defeated_monsters
            </table>
        </p>
        <hr/>

        <h3>Users:</h3>
        <p>$total_users users are registered; $recent_sessions users have managed campaigns in the last 12 hours.</p>
        <p>$total_users_last_30 users have managed campaigns in the last 30 days.</p>
        <p>Per user averages:</p>
        <ul>
            <li>Survivors: $avg_user_survivors</li>
            <li>Settlements: $avg_user_settlements</li>
            <li>Avatars: $avg_user_avatars</li>
        </ul>
        </div>
    </div>
    """ % (settings.get("application", "STATIC_URL"), down_arrow_flash))

    # misc html assets
    home_button = '\t<form method="POST" action="#"><input type="hidden" name="change_view" value="dashboard"/><button id="floating_dashboard_button" class="gradient_silver"> %s <span class="desktop_only">Return to Dashboard</span></button></form>\n' % system_flash
    refresh_button = '\t<form method="POST" action="#"><button id="floating_refresh_button" class="yellow"> %s </button></form>\n' % refresh_flash
    event_log_button = Template('\t<form method="POST" action="#">\n\t\t<input type="hidden" name="change_view" value="event_log"/>\n\t\t<button id="floating_event_log_button" class="gradient_orange"> %s <span class="desktop_only">$name Event Log</span></button>\n\t</form>\n' % event_log_flash)
    view_asset_button = Template("""\n\
    <form method="POST" action="#">
    <input type="hidden" name="view_$asset_type" value="$asset_id" />
    <button id="$button_id" class="$button_class $disabled" $disabled>$asset_name <span class="desktop_only">$desktop_text</span></button>
    </form>
    \n""")





class survivor:
    no_survivors_error = '<!-- No Survivors Found! -->'
    new = Template("""\n\
    <span class="desktop_only nav_bar gradient_green"></span>
    <span class="mobile_only nav_bar_mobile gradient_green"></span>
    <span class="top_nav_spacer mobile_only">hidden</span>
    <br class="desktop_only"/>
    <div id="create_new_asset_form_container">
        <form method="POST" action="#" enctype="multipart/form-data">
        <input type="hidden" name="new" value="survivor" />
        <input type="hidden" name="settlement_id" value="$home_settlement">
        <input type="text" name="name" placeholder="New Survivor Name" class="full_width" autofocus>

        <hr>
        <p style="margin-top:10px;">Survivor Image (optional):<br/><br/>
        <input type="file" name="survivor_avatar" accept="image/*"></p>
        <hr>
        <div id="block_group">
        <h2>Survivor Sex</h2>
            <fieldset class="radio">
          <input type="radio" id="male_button" class="radio_principle" name="sex" value="M" checked/> 
          <label class="sex_button radio_principle_label" for="male_button"> Male </label>
          <input type="radio" id="female_button" class="radio_principle" name="sex" value="F"/> 
          <label id="female_sex_button" class="sex_button radio_principle_label" for="female_button"> Female </label>
            </fieldset>
        </div>
        <div class="create_new_asset_block">
            $add_ancestors
            <div id="block_group">
            <h2>Permissions</h2>
            <p>Survivor Owner:</p>
            <input id="survivor_owner" type="email" name="email" placeholder="Survivor Email" value="$user_email">
            <p>
            <input type="checkbox" id="public" class="radio_principle" name="toggle_public" > 
            <label class="radio_principle_label" for="public"> Anyone May Manage this Survivor </label>
            <br/><br/>
            </p>
            </div>

            <button class="success">SAVE</button>
            </form>
        </div><!-- create_new_asset_block -->
    </div>
    \n""")
    add_ancestor_top = '    <div id="block_group" title="Add survivor parents.">\n    <h2>Survivor Parents</h2>\n<p>Survivors without parents are not eligible for the auto-application of Innovation bonuses granted only to newborn survivors!</p>'
    add_ancestor_select_top = Template('\t<select name="$parent_role">\n\t<option selected disabled hidden value="">$pretty_role</option>')
    change_ancestor_select_top = Template('\t<select onchange="this.form.submit()" name="$parent_role">\n\t<option selected disabled hidden value="">$pretty_role</option>')
    add_ancestor_select_row = Template('\t<option value="$parent_id">$parent_name</option>\n')
    change_ancestor_select_row = Template('\t<option value="$parent_id" $selected>$parent_name</option>\n')
    add_ancestor_select_bot = '\t</select><br class="mobile_only"/><br class="mobile_only"/>'
    add_ancestor_bot = '    </div>\n'
    campaign_summary_hide_show = Template("""\n\
    <hr class="invisible">
    <span class="tiny_break">
    <h3 class="clickable $color align_left" onclick="showHide('$group_id')">$heading ($death_count) <img class="dashboard_down_arrow" src="%s/icons/down_arrow.png"/> </h3>
    <div id="$group_id" style="display: none;">
        $dead_survivors
    </div> <!-- deadSurvivorsBlock -->
    <hr class="invisible">
    \n""" % (settings.get("application","STATIC_URL")))
    campaign_asset = Template("""\n\
      <div class="survivor_campaign_asset_container">

        <form method="POST" action="#edit_hunting_party">
         <input type="hidden" name="modify" value="survivor" />
         <input type="hidden" name="asset_id" value="$survivor_id" />
         <input type="hidden" name="view_game" value="$settlement_id" />
         <input type="hidden" name="in_hunting_party" value="$hunting_party_checked"/>
         <button id="add_survivor_to_party" class="$able_to_hunt $disabled" $able_to_hunt $disabled>::</button>
        </form>

        <form method="POST" action="#">
         <input type="hidden" name="view_survivor" value="$survivor_id" />
         <button id="survivor_campaign_asset" class="$b_class $disabled" $disabled>
            $returning
            $avatar
            <center> <font class="$favorite"/>&#9733;</font> <b>$name</b> [$sex] </center>
            $savior
            $special_annotation
            &ensp; XP: $hunt_xp &ensp; Survival: $survival<br/>
            &ensp; Insanity: $insanity <br/>
            &ensp; Courage: $courage<br/>
            &ensp; Understanding: $understanding
         </button>
        </form>

      </div> <!-- survivor_campaign_asset_container-->
     <hr class="invisible"/>
    \n""")
    form = Template("""\n\
    <span class="desktop_only nav_bar gradient_green"></span>
    <span class="mobile_only nav_bar_mobile gradient_green"></span>
    <span class="top_nav_spacer mobile_only">hidden</span>
    <br class="desktop_only"/>
    $campaign_link

    <form method="POST" id="autoForm" action="#">
        <button id="save_button" class="success">Save</button>
        <input type="hidden" name="form_id" value="survivor_top" />
        <input type="hidden" name="modify" value="survivor" />
        <input type="hidden" name="asset_id" value="$survivor_id" />

        <div id="asset_management_left_pane">
            <input onchange="this.form.submit()" id="topline_name_fixed" class="full_width" type="text" name="name" value="$name" placeholder="Survivor Name"/>
            <br class="mobile_only"/><br class="mobile_only"/><br class="mobile_only"/>

            $epithet_controls

            <!-- SEX, SURVIVAL and MISC. SURVIVOR ATTRIBUTES -->

            $affinity_controls

            <p>
            Survivor Sex: <input onchange="this.form.submit()" class="survivor_sex_text" name="sex" value="$sex" />
            $mobile_avatar_img
            <br/>

            <div id="survivor_dead_retired_container">

                    <!-- favorite -->
                 <input type='hidden' value='unchecked' name='toggle_favorite'/>
                 <input onchange="this.form.submit()" type="checkbox" id="favorite" class="radio_principle" name="toggle_favorite" value="checked" $favorite_checked /> 
                 <label class="radio_principle_label toggle_favorite" for="favorite"> &#9733; Favorite </label>

                    <!-- dead -->
                 <input type='hidden' value='unchecked' name='toggle_dead'/>
                 <input type="checkbox" id="dead" class="radio_principle" name="toggle_dead" value="checked" onclick="showHide('COD')" $dead_checked /> 
                 <label class="radio_principle_label floating_label" for="dead"> Dead </label>

                    <!-- retired -->
                 <input type='hidden' value='unchecked' name='toggle_retired'/>
                 <input onchange="this.form.submit()" type="checkbox" id="retired" class="radio_principle" name="toggle_retired" value="checked" $retired_checked> 
                 <label class="radio_principle_label" for="retired" style="float: right; clear: none;"> Retired &nbsp; </label>
                </p>


                <div id="COD" style="display: $show_COD" >
                    <hr class="mobile_only"/> <img class="COD_down_arrow mobile_only" src="http://media.kdm-manager.com/icons/down_arrow.png"/>
                    <input onchange="this.form.submit()" class="full_width maroon" type="text" name="cause_of_death" placeholder="Cause of Death" value="$cause_of_death"/>
                </div>
            </div> <!-- survivor_dead_retired_container -->

            <hr class="mobile_only"/>

            <div id="survivor_survival_box_container">
                <div class="big_number_container left_margin">
                    <button class="incrementer" onclick="increment('survivalBox');">+</button>
                    <input type="number" id="survivalBox" class="big_number_square" name="survival" value="$survival" min="0"/>
                    <button class="decrementer" onclick="decrement('survivalBox');">-</button>
                </div>
                <div class="big_number_caption">Survival <p>(max: $survival_limit)</p></div>
            </div> <!-- survivor_survival_box_container -->

            <hr class="mobile_only"/>

            <div id="survivor_survival_actions_container">
                <p>
                 <input type='hidden' value='unchecked' name='toggle_cannot_spend_survival'/>
                 <input onchange="this.form.submit()" type="checkbox" id="cannot_spend_survival" class="radio_principle" name="toggle_cannot_spend_survival" value="checked" $cannot_spend_survival_checked /> 
                 <label class="radio_principle_label" for="cannot_spend_survival"> Cannot spend survival </label>
                 $survival_actions
                </p>

            $desktop_avatar_img

            </div>

            <hr class="mobile_only"/>
            <div class="mobile_only">
                $fighting_arts
                $departure_buffs
                $abilities_and_impairments
                $disorders
            </div>

            <a id="edit_attribs" />

            <hr class="mobile_only"/> <!-- logical break; same form -->

            <div id="survivor_stats">
                <input id="movementBox" class="big_number_square" type="number" name="Movement" value="$movement"/>
                <div class="big_number_caption">Movement<br />
                    <div class="survivor_attrib_paddles">
                    <button class="incrementer" onclick="increment('movementBox');">+</button>
                    <button class="decrementer" onclick="decrement('movementBox');">-</button>
                    </div>
                </div>
                <br class="mobile_only"/><hr/>
                <input id="accuracyBox" class="big_number_square" type="number" name="Accuracy" value="$accuracy"/>
                <div class="big_number_caption">Accuracy<br/>
                    <div class="survivor_attrib_paddles">
                    <button class="incrementer" onclick="increment('accuracyBox');">+</button>
                    <button class="decrementer" onclick="decrement('accuracyBox');">-</button>
                    </div>
                </div>
                <br class="mobile_only"/><hr/>
                <input id="strengthBox" class="big_number_square" type="number" name="Strength" value="$strength"/>
                <div class="big_number_caption">Strength<br/>
                    <div class="survivor_attrib_paddles">
                    <button class="incrementer" onclick="increment('strengthBox');">+</button>
                    <button class="decrementer" onclick="decrement('strengthBox');">-</button>
                    </div>
                </div>
                <br class="mobile_only"/><hr/>
                <input id="evasionBox" class="big_number_square" type="number" name="Evasion" value="$evasion"/>
                <div class="big_number_caption">Evasion<br/>
                    <div class="survivor_attrib_paddles">
                    <button class="incrementer" onclick="increment('evasionBox');">+</button>
                    <button class="decrementer" onclick="decrement('evasionBox');">-</button>
                    </div>
                </div>
                <br class="mobile_only"/><hr/>
                <input id="luckBox" class="big_number_square" type="number" name="Luck" value="$luck"/>
                <div class="big_number_caption">Luck<br/>
                    <div class="survivor_attrib_paddles">
                    <button class="incrementer" onclick="increment('luckBox');">+</button>
                    <button class="decrementer" onclick="decrement('luckBox');">-</button>
                    </div>
                </div>
                <br class="mobile_only"/><hr/>
                <input id="speedBox" class="big_number_square" type="number" name="Speed" value="$speed"/>
                <div class="big_number_caption">Speed<br/>
                    <div class="survivor_attrib_paddles">
                    <button class="incrementer" onclick="increment('speedBox');">+</button>
                    <button class="decrementer" onclick="decrement('speedBox');">-</button>
                    </div>
                </div>
            </div> <!-- survivor_stats -->

            <br class="mobile_only"/>
            <hr/>

            <h3>Bonuses</h3>
            $settlement_buffs


            <a id="edit_hit_boxes" />

        </div> <!-- asset_management_left_pane -->

        <hr class="mobile_only"/>   <!-- LOGICAL/ORGANIZATIONAL break -->

        <div id="asset_management_middle_pane">
                        <!-- HIT BOXES ; still the same form -->
            <a> <!-- hacks!!! for inc/dec buttons-->
            <div class="survivor_hit_box insanity_box">
             <div class="big_number_container right_border">
              <button class="incrementer mobile_only" onclick="increment('insanityBox');">+</button>
               <input id="insanityBox" type="number" class="shield" name="Insanity" value="$insanity" style="color: $insanity_number_style;" min="0"/>
               <font id="hit_box_insanity">Insanity</font>
              <button class="decrementer mobile_only" onclick="decrement('insanityBox');">-</button>
             </div>

             <div class="hit_box_detail">
              <input id="damage_brain_light" onclick="toggleDamage('damage_brain_light');" type="submit" class="damage_box_$brain_damage_light_checked damage_box" name="toggle_brain_damage_light" value=" "/>
                <h2>Brain</h2><br/>
                If your insanity is 3+, you are <b>Insane</b>.
             </div>
            </div> <!-- survivor_hit_box -->

                <!-- HEAD -->
            <div class="survivor_hit_box">
                <div class="big_number_container right_border">
                    <button class="incrementer mobile_only" onclick="increment('headBox');">+</button>
                        <input id="headBox" type="number" class="shield" name="Head" value="$head" min="0"/>
                    <button class="decrementer mobile_only" onclick="decrement('headBox');">-</button>
                </div>
                <div class="hit_box_detail">
                 <input id="damage_head_heavy" onclick="toggleDamage('damage_head_heavy');" type="submit" class="damage_box_$head_damage_heavy_checked heavy_damage damage_box" name="toggle_head_damage_heavy" value=" "/>
                    <h2>Head</h2>
                    <b>H</b>eavy Injury: Knocked Down
                </div>
            </div> <!-- survivor_hit_box -->

                <!-- ARMS -->
            <div class="survivor_hit_box">
                <div class="big_number_container right_border">
                    <button class="incrementer mobile_only" onclick="increment('armsBox');">+</button>
                        <input id="armsBox" type="number" class="shield" name="Arms" value="$arms" min="0"/>
                    <button class="decrementer mobile_only" onclick="decrement('armsBox');">-</button>
                </div>
                <div class="hit_box_detail">
                 <input id="damage_arms_heavy" onclick="toggleDamage('damage_arms_heavy');" type="submit" class="damage_box_$arms_damage_heavy_checked heavy_damage damage_box" name="toggle_arms_damage_heavy" value=" "/>
                 <input id="damage_arms_light" onclick="toggleDamage('damage_arms_light');" type="submit" class="damage_box_$arms_damage_light_checked damage_box" name="toggle_arms_damage_light" value=" "/>
                    <h2>Arms</h2>
                    <b>H</b>eavy Injury: Knocked Down
                </div>
            </div> <!-- survivor_hit_box -->

                <!-- BODY -->
            <div class="survivor_hit_box">
                <div class="big_number_container right_border">
                    <button class="incrementer mobile_only" onclick="increment('bodyBox');">+</button>
                        <input id="bodyBox" type="number" class="shield" name="Body" value="$body" min="0"/>
                    <button class="decrementer mobile_only" onclick="decrement('bodyBox');">-</button>
                </div>
                <div class="hit_box_detail">
                 <input id="damage_body_heavy" onclick="toggleDamage('damage_body_heavy');" type="submit" class="damage_box_$body_damage_heavy_checked heavy_damage damage_box" name="toggle_body_damage_heavy" value=" "/>
                 <input id="damage_body_light" onclick="toggleDamage('damage_body_light');" type="submit" class="damage_box_$body_damage_light_checked damage_box" name="toggle_body_damage_light" value=" "/>
                    <h2>Body</h2>
                    <b>H</b>eavy Injury: Knocked Down
                </div>
            </div> <!-- survivor_hit_box -->

                <!-- WAIST -->
            <div class="survivor_hit_box">
                <div class="big_number_container right_border">
                    <button class="incrementer mobile_only" onclick="increment('waistBox');">+</button>
                        <input id="waistBox" type="number" class="shield" name="Waist" value="$waist" min="0"/>
                    <button class="decrementer mobile_only" onclick="decrement('waistBox');">-</button>
                </div>
                <div class="hit_box_detail">
                 <input id="damage_waist_heavy" onclick="toggleDamage('damage_waist_heavy');" type="submit" class="damage_box_$waist_damage_heavy_checked heavy_damage damage_box" name="toggle_waist_damage_heavy" value=" "/>
                 <input id="damage_waist_light" onclick="toggleDamage('damage_waist_light');" type="submit" class="damage_box_$waist_damage_light_checked damage_box" name="toggle_waist_damage_light" value=" "/>
                    <h2>Waist</h2>
                    <b>H</b>eavy Injury: Knocked Down
                </div>
            </div> <!-- survivor_hit_box -->

        <!-- LEGS -->
            <div class="survivor_hit_box">
                <div class="big_number_container right_border">
                    <button class="incrementer mobile_only" onclick="increment('legsBox');">+</button>
                        <input id="legsBox" type="number" class="shield" name="Legs" value="$legs" min="0"/>
                    <button class="decrementer mobile_only" onclick="decrement('legsBox');">-</button>
                </div>
                <div class="hit_box_detail">
                 <input id="damage_legs_heavy" onclick="toggleDamage('damage_legs_heavy');" type="submit" class="damage_box_$legs_damage_heavy_checked heavy_damage damage_box" name="toggle_legs_damage_heavy" value=" "/>
                 <input id="damage_legs_light" onclick="toggleDamage('damage_legs_light');" type="submit" class="damage_box_$legs_damage_light_checked damage_box" name="toggle_legs_damage_light" value=" "/>
                    <h2>Legs</h2>
                    <b>H</b>eavy Injury: Knocked Down
                </div>
            </div> <!-- survivor_hit_box -->


                <!-- HIT BOXES END HERE -->


                <!-- HEAL SURVIVOR CONTROLS HERE! -->

             <select name="heal_survivor" onchange="this.form.submit()">
              <option selected disabled hidden value="">Heal Survivor</option>
              <option>Heal Injuries Only</option>
              <option>Heal Injuries and Remove Armor</option>
              <option>Return from Hunt</option>
             </select>


            <hr/>  <!-- logical break -->


                        <!-- HUNT XP and AGE -->
            <div class="big_number_container left_margin">
                <button class="incrementer" onclick="increment('huntXpBox');">+</button>
                <input id="huntXpBox" class="big_number_square" type="number" name="hunt_xp" value="$hunt_xp" min="0"/>
                <button class="decrementer" onclick="decrement('huntXpBox');">-</button>
            </div>
            <div class="big_number_caption">Hunt XP</div>
            <br class="mobile_only"/>
            <p>
                <font class="kdm_font">g</font> <b>Age</b> occurs at 2, 6, 10 and 15. The Survivor retires at 16.
            </p>
            <hr/>

                        <!-- WEAPON PROFICIENCY -->
            <div class="big_number_container left_margin">
                <button class="incrementer" onclick="increment('proficiencyBox');">+</button>
                <input onchange="this.form.submit()" id="proficiencyBox" class="big_number_square" type="number" name="Weapon Proficiency" value="$weapon_proficiency" min="0"/>
                <button class="decrementer" onclick="decrement('proficiencyBox');">-</button>
            </div>
            <div class="big_number_caption">Weapon Proficiency</div>

            $weapon_proficiency_options

            <div class="desktop_indent">
                <p><b>Specialist</b> at 3<br/><b>Master</b> at 8</p>
            </div>


            <hr/>

                        <!-- COURAGE AND UNDERSTANDING -->

            <div class="big_number_container left_margin">
                <button class="incrementer" onclick="increment('courageBox');">+</button>
                <input id="courageBox" class="big_number_square" type="number" name="Courage" value="$courage" min="0"/>
                <button class="decrementer" onclick="decrement('courageBox');">-</button>
            </div>
            <div class="big_number_caption">Courage</div>
            <br class="mobile_only"/>
            <p>
              <font class="kdm_font">g</font> <b>Bold</b> (p. 107) occurs at 3<br/>
              <font class="kdm_font">g</font> <b>See the Truth</b> (p.155) occurs at 9.
            </p>

            <hr/>

            <div class="big_number_container left_margin">
                <button class="incrementer" onclick="increment('understandingBox');">+</button>
                <input id="understandingBox" class="big_number_square" type="number" name="Understanding" value="$understanding" min="0"/>
                <button class="decrementer" onclick="decrement('understandingBox');">-</button>
            </div>
            <div class="big_number_caption">Understanding</div>
            <br class="mobile_only"/>
            <p>
               <font class="kdm_font">g</font> <b>Insight</b> (p.123) occurs at 3<br/>
                <font class="kdm_font">g</font> <b>White Secret</b> (p.169) occurs at 9.
            </p>

            </form>




            <hr class="mobile_only"/> <!-- logical division; new form starts here too -->
        </div> <!-- asset_management_middle_pane -->



        <div id="asset_management_right_pane"> <!-- asset_management_right_pane -->



                            <!-- 1.4 Misc. Attribs -->
            <a id="edit_misc_attribs" class="mobile_only"> </a>
            <form method="POST" id="autoForm" action="#edit_misc_attribs">
                <input type="hidden" name="modify" value="survivor" />
                <input type="hidden" name="asset_id" value="$survivor_id" />
                $expansion_attrib_controls
            </form>

            <form method="POST" id="autoForm" action="#edit_misc_attribs">
                <button class="hidden"></button>
                <input type="hidden" name="modify" value="survivor" />
                <input type="hidden" name="asset_id" value="$survivor_id" />
                $partner_controls
            </form>


                        <!-- FIGHTING ARTS -->
            <a id="edit_fighting_arts" class="mobile_only"> </a>
            <form method="POST" id="autoForm" action="#edit_fighting_arts">
                <input type="hidden" name="form_id" value="survivor_edit_fighting_arts" />
                <button class="hidden"></button>
                <input type="hidden" name="modify" value="survivor" />
                <input type="hidden" name="asset_id" value="$survivor_id" />

                <h3>Fighting Arts</h3>
                 <input type='hidden' value='unchecked' name='toggle_cannot_use_fighting_arts'/>
                 <input onchange="this.form.submit()" type="checkbox" id="cannot_use_fighting_arts" class="radio_principle" name="toggle_cannot_use_fighting_arts" value="checked" $cannot_use_fighting_arts_checked />
                 <label class="radio_principle_label" for="cannot_use_fighting_arts" id="float_right_toggle"> Cannot use<br/>Fighting Arts </label>
                <p>Maximum 3.</p>

                    $fighting_arts
                    $add_fighting_arts<br class="mobile_only"/>
                    $rm_fighting_arts
            </form>


            <a id="edit_disorders" class="mobile_only"></a>
            <hr />

                        <!-- DISORDERS - HAS ITS OWN FORM-->

            <form method="POST" id="autoForm" action="#edit_disorders">
                <input type="hidden" name="form_id" value="survivor_edit_disorders" />
                <input type="hidden" name="modify" value="survivor" />
                <input type="hidden" name="asset_id" value="$survivor_id" />
                <h3>Disorders</h3>
                <p>Maximum 3.</p>

                $disorders
                $add_disorders<br class="mobile_only"/>
                $rm_disorders


            </form>

            <a id="edit_abilities" class="mobile_only"></a>
            <hr />

                        <!-- ABILITIES AND IMPAIRMENTS -->


            <h3>Abilities & Impairments</h3>
                <form method="POST" id="autoForm" action="#edit_abilities">
                  <input type="hidden" name="form_id" value="survivor_edit_abilities" />
                  <input type="hidden" name="modify" value="survivor" />
                  <input type="hidden" name="asset_id" value="$survivor_id" />
                  <input type='hidden' value='unchecked' name='toggle_skip_next_hunt'/>
                  <input onchange="this.form.submit()" type="checkbox" id="skip_next_hunt" class="radio_principle" name="toggle_skip_next_hunt" value="checked" $skip_next_hunt_checked />
                  <label class="radio_principle_label" for="skip_next_hunt" id="float_right_toggle"> Skip Next<br/>Hunt </label>
                </form>
            <p>
                <form method="POST" id="autoForm" action="#edit_abilities">
                  <input type="hidden" name="form_id" value="survivor_edit_abilities" />
                  <input type="hidden" name="modify" value="survivor" />
                  <input type="hidden" name="asset_id" value="$survivor_id" />
                    $abilities_and_impairments<br class="mobile_only"/>
                    $add_abilities_and_impairments
                <input onchange="this.form.submit()" class="full_width" type="text" name="add_ability" placeholder="add custom ability or impairment"/>
                    $remove_abilities_and_impairments
                </form>
            </p>

            <hr />

            <a id="edit_lineage" class="mobile_only"></a>

            <h3>Lineage</h3>
            <h4>Parents</h4>
            <form method="POST" action="#edit_lineage">
              <input type="hidden" name="modify" value="survivor" />
              <input type="hidden" name="asset_id" value="$survivor_id" />
              $parents
            </form>
            <h4>Intimacy Partners</h4>
                $partners
            <h4>Siblings</h4>
                $siblings
            <h4>Children</h4>
            $children
            <hr />
            <h3>Permissions</h3>
            <form method="POST" id="autoForm" action="#edit_lineage">
              <input type="hidden" name="form_id" value="survivor_edit_abilities"/>
              <input type="hidden" name="modify" value="survivor" />
              <input type="hidden" name="asset_id" value="$survivor_id" />
              <p>Survivor Owner:</p>
              <input onchange="this.form.submit()" class="full_width" type="email" name="email" placeholder="email" value="$email"/>

              <input type='hidden' value='unchecked' name='toggle_public'/>
              <input onchange="this.form.submit()" type="checkbox" id="public" class="radio_principle" name="toggle_public" value="checked" $public_checked> 
              <label class="radio_principle_label" for="public"> Anyone May Manage this Survivor &nbsp; </label>
              <br/>
            </form>
            <hr />

            <form method="POST" enctype="multipart/form-data" action="#">
              <input type="hidden" />
              <input type="hidden" name="modify" value="survivor" />
              <input type="hidden" name="asset_id" value="$survivor_id" />

                <p>Survivor Image:<br/><br/>
                <input onchange="this.form.submit()" type="file" name="survivor_avatar" accept="image/*">
                </p>
            </form>

            <hr class="mobile_only"/>

            <form method="POST" onsubmit="return confirm('This cannot be undone! Press OK to permanently delete this survivor forever, which is NOT THE SAME THING as marking it dead: permanently deleting the survivor prevents anyone from viewing and/or editing it ever again! If you are trying to delete all survivors in a settlement, you may delete the settlement from the settlement editing view.');"><input type="hidden" name="remove_survivor" value="$survivor_id"/><button class="error">Permanently Delete Survivor</button></form>
            <hr class="mobile_only"/>
            <br class="mobile_only"/>
        </div> <!-- asset_management_right_pane -->


    <!-- ONLY MODAL CONTENT PAST THIS POINT!!!! -->

        <div id="modalAffinity" class="modal">

          <!-- Modal content -->
            <div class="modal-content">
                <span class="close">×</span>

                <h3>Update Permanent Survivor Affinities</h3>

                <form id="autoForm" method="POST">
                    <input type="hidden" name="modify" value="survivor" />
                    <input type="hidden" name="asset_id" value="$survivor_id" />
                    <input type="hidden" name="modal_update" value="affinities"/>

                    <div class="bulk_add_control" title="Red affinity controls">
                    <button type="button" class="incrementer" onclick="increment('redCountBox');">+</button>
                    <input id="redCountBox" class="big_number_square" type="number" name="red_affinities" value="$red_affinities"/>
                    <button type="button" class="decrementer" onclick="decrement('redCountBox');">-</button>
                    </div>
                    <div id="affinity_block" class="red">&nbsp;</div>
                    <hr/>

                    <div class="bulk_add_control" title="Blue affinity controls">
                    <button type="button" class="incrementer" onclick="increment('blueCountBox');">+</button>
                    <input id="blueCountBox" class="big_number_square" type="number" name="blue_affinities" value="$blue_affinities"/>
                    <button type="button" class="decrementer" onclick="decrement('blueCountBox');">-</button>
                    </div>
                    <div id="affinity_block" class="blue">&nbsp;</div>
                    <hr/>

                    <div class="bulk_add_control" title="Green affinity controls">
                    <button type="button" class="incrementer" onclick="increment('greenCountBox');">+</button>
                    <input id="greenCountBox" class="big_number_square" type="number" name="green_affinities" value="$green_affinities"/>
                    <button type="button" class="decrementer" onclick="decrement('greenCountBox');">-</button>
                    </div>
                    <div id="affinity_block" class="green">&nbsp;</div>
                    <hr/>


                    <center><button class="green">Save!</button></center>
                    <br><br>
                </form>
            </div> <!-- modal-content -->
        </div> <!-- modalAffinity -->

    \n""")
    partner_controls_top = '\n<p><span class="tiny_break">&nbsp;</span>Partner<select name="partner_id" onchange="this.form.submit()">\n'
    partner_controls_none = '<option selected disabled>Select a Survivor</option>'
    partner_controls_opt = Template('<option value="$value" $selected>$name</option>')
    partner_controls_bot = '</select><span class="tiny_break"/>&nbsp;</span></p><hr/>\n\n'
    expansion_attrib_controls = Template("""\n
    <span class="tiny_break"/>&nbsp;</span>
    <input type="hidden" name="expansion_attribs" value="None"/> <!-- Hacks -->
    <input type="hidden" name="expansion_attribs" value="None"/> <!-- Hacks -->
    $control_items
    <br class="clear_both"/>
    <span class="tiny_break"/>&nbsp;</span>
    <hr/>
    \n""")
    expansion_attrib_item = Template("""\n
    <div class="expansion_attrib_toggle">
     <input onchange="this.form.submit()" type="checkbox" id="$item_id" class="expansion_attrib_toggle" name="expansion_attribs" value="$key" $checked/>
     <label class="expansion_attrib_toggle" for="$item_id">$key</label>
    </div> <!-- expansion_attrib_toggle -->
    \n""")
    returning_survivor_badge = """\n\
    <div class="returning_survivor_badge" title="Returning Survivor">R</div>
    \n"""
    epithet_controls = Template("""\n\
     $epithets
     <br class="mobile_only"/>
     $add_epithets
     <br class="mobile_only"/>
     $rm_epithets
     <input onchange="this.form.submit()" class="full_width" type="text" name="add_epithet" placeholder="add a custom epithet"/>
     <hr class="mobile_only"/>
    \n""")
    affinity_controls = Template("""\n\
    <p>
    <button id="modalAffinityButton" class="$button_class" title="Permanent Affinity controls"> $text </button>
    </p>

    <script>
    window.onload = function(){
        var modal = document.getElementById('modalAffinity');
        var btn = document.getElementById("modalAffinityButton");
        var span = document.getElementsByClassName("close")[0];
        btn.onclick = function(b) {b.preventDefault(); modal.style.display = "block";}
        span.onclick = function() {modal.style.display = "none";}
        window.onclick = function(event) {if (event.target == modal) {modal.style.display = "none";}}
    };
    </script>
    \n""")
    affinity_span = Template("""\n
    <span id="affinity_span" class="$span_class">$value</span>
    \n""")


class settlement:


    def render_campaign_toggles():
        """ Prints the toggles for the campaigns. """

        slug = Template("""\n\
        <input type="radio" id="$c_id" class="radio_principle" name="campaign" value="$name" $checked/>
        <label class="radio_principle_label" for="$c_id">$name</label>
        \n""")

        output = ""
        for c_name in game_assets.campaigns.keys():
            c_name_flat = c_name.lower().replace(" ","_")
            c_dict = game_assets.campaigns[c_name]
            checked = ""
            if "default" in c_dict.keys():
                checked = "checked"
            output += slug.safe_substitute(name=c_name, checked=checked, c_id = c_name_flat)
        return output



    def render_checkboxes(asset_dict_name=None):
        """ Prints checkboxes for the specified asset dictionary"""

        slug = Template("""\n\
        <input id="$a_id" class="radio_principle" type="checkbox" name="%s" value="$var_value" />
        <label for="$a_id" class="radio_principle_label">$var_value</label> 
        \n""" % asset_dict_name)


        output = ""

        if asset_dict_name == "expansions":
            for e_key in sorted(game_assets.expansions.keys()):
                exp_attribs = game_assets.expansions[e_key]
                if not "existing_campaign_only" in exp_attribs:
                    output += slug.safe_substitute(a_id=e_key.lower().replace(" ","_"), var_value=e_key)
        elif asset_dict_name == "survivors":
            # special custom box for prologue survivors (calls
            #   assets.Settlement.first_story() after creation
            output = """
                <input type="checkbox" id="create_prologue_survivors" class="radio_principle" name="create_prologue_survivors" value="True" />
                <label class="radio_principle_label" for="create_prologue_survivors"> Create Four "First Story" Survivors</label><br/><br/>
            """
            for s_name in sorted(game_assets.survivors.keys()):
                s_key = s_name.lower().replace(" ","_")
                s_dict = game_assets.survivors[s_name]
                output += slug.safe_substitute(a_id=s_key, var_value=s_name)

        return output

    new = """\n\
    <span  class="desktop_only nav_bar gradient_orange"></span>
    <span class="gradient_orange nav_bar_mobile mobile_only"></span>
    <span class="top_nav_spacer mobile_only"> hidden </span>
    <br class="desktop_only"/>
    <div id="create_new_asset_form_container">
        <form method="POST">
        <input type="hidden" name="new" value="settlement" />
        <input type="text" name="settlement_name" placeholder="New Settlement Name"/ class="full_width" autofocus>
        <h3 class="new_settlement">Campaign:</h3>
        <p class="new_settlement">
        Choosing an expansion campaign automatically enables expansion content for that campaign and modifies the settlement timeline, milestones and principles. Campaign type may <b>not</b> be changed after settlement creation!<br/><br/>
            %s
        </p>
        <h3 class="new_settlement">Expansions:</h3>
        <p class="new_settlement">
        Enable expansion content by toggling items below. Expansions may also be enabled (or disabled) later from the Settlement Sheet.<br/><br/>
        <input type="hidden" name="expansions" value="None"/> <!-- Both of these are necessary -->
        <input type="hidden" name="expansions" value="None"/> <!-- Hack City! -->
            %s
        </p>
        <h3 class="new_settlement">Survivors:</h3>
        <p class="new_settlement">
        By default, new settlements start with no survivors. Toggle options below to add survivors. <br/><br/>
            <input type="hidden" name="survivors" value="None"/> <!-- Both of these are necessary -->
            <input type="hidden" name="survivors" value="None"/> <!-- Hack City! -->
            %s
        </p>
        <hr class="new_settlement" />
        <button class="success">Create!</button>
        </form>
    </div>
    \n""" % (render_campaign_toggles(), render_checkboxes("expansions"), render_checkboxes("survivors"))

    return_hunting_party_with_confirmation = Template("""\n\
        <form method="POST" onsubmit="return confirm('Press OK to return the survivors, increment Hunt XP +1 and add the current quarry to the Defeated Monsters list as well as the settlement timeline for this year.');">
            <input type="hidden" name="return_hunting_party" value="$settlement_id"/>
            <button id="return_hunting_party" class="bold yellow" >&#8629; Return Hunting Party</button>
        </form>
        <hr />
    \n""")
    return_hunting_party = Template("""\n\
        <form method="POST">
            <input type="hidden" name="return_hunting_party" value="$settlement_id"/>
            <button id="return_hunting_party" class="bold gradient_orange" >&#8629; Return Hunting Party</button>
        </form>
        <hr/>
    \n""")
    current_quarry_select = Template("""\n\
    <br class="clear_both"/>
    <h3>Current Quarry:</h3>
    <form method="POST">
        <input type="hidden" name="modify" value="settlement"/>
        <input type="hidden" name="asset_id" value="$settlement_id"/>
        <select name="current_quarry" onchange="this.form.submit()">
          <option>None</option>
            $options
        </select>
    </form>
    <br class="clear_both mobile_only" />
    \n""")
    hunting_party_macros = Template("""\n\
    <hr>
    <h3>Manage Hunting Party:</h3>
    <div id="hunting_party_macro_container">
    <div class="hunting_party_macro" style="border-left: 0 none;">
        <form method="POST">
            <input type="hidden" name="modify" value="settlement"/>
            <input type="hidden" name="asset_id" value="$settlement_id"/>
            <input type="hidden" name="hunting_party_operation" value="survival"/>
            Survival
            <button name="operation" value="increment">+1</button>
            <button name="operation" value="decrement">-1</button>
        </form>
    </div>
    <div class="hunting_party_macro">
        <form method="POST">
            <input type="hidden" name="modify" value="settlement"/>
            <input type="hidden" name="asset_id" value="$settlement_id"/>
            <input type="hidden" name="hunting_party_operation" value="Brain Event Damage"/>
            Brain Event Damage
            <button name="operation" value="increment">+1</button>
        </form>
    </div>
    <div class="hunting_party_macro">
        <form method="POST">
            <input type="hidden" name="modify" value="settlement"/>
            <input type="hidden" name="asset_id" value="$settlement_id"/>
            <input type="hidden" name="hunting_party_operation" value="Insanity"/>
            Insanity
            <button name="operation" value="increment">+1</button>
            <button name="operation" value="decrement">-1</button>
        </form>
    </div>
    <div class="hunting_party_macro">
        <form method="POST">
            <input type="hidden" name="modify" value="settlement"/>
            <input type="hidden" name="asset_id" value="$settlement_id"/>
            <input type="hidden" class="clear_both" name="hunting_party_operation" value="Courage"/>
            Courage
            <button name="operation" value="increment">+1</button>
            <button name="operation" value="decrement">-1</button>
        </form>
    </div>
    <div class="hunting_party_macro">
        <form method="POST">
            <input type="hidden" name="modify" value="settlement"/>
            <input type="hidden" name="asset_id" value="$settlement_id"/>
            <input type="hidden" name="hunting_party_operation" value="Understanding"/>
            Understanding
            <button name="operation" value="increment">+1</button>
            <button name="operation" value="decrement">-1</button>
        </form>
    </div>
    </div><!-- hunting party macro container -->

    \n""")
    storage_warning = Template(""" onclick="return confirm('Remove $item_name from Settlement Storage?');" """)
    storage_remove_button = Template("""\n\
    \t<button $confirmation id="remove_item" name="remove_item" value="$item_key" style="background-color: #$item_color; color: #$item_font_color;"> $item_key_and_count </button>
    \n""")
    storage_tag = Template('<h3 class="inventory_tag" style="color: #$color">$name</h3><hr/>')
    storage_resource_pool = Template("""\n\
    <p>Hide: $hide, Bone: $bone, Scrap: $scrap, Organ: $organ</p>
    \n""")

    player_controls_none = Template('<p>Add other players to the "$name" campaign by making them the Owner of a Survivor in this Settlement!<br/><br/></p>')
    player_controls_table_top = '<table class="player_management_controls"><tr><th>Email Address</th><th>Role</th></tr>\n'
    player_controls_table_row = Template("""<tr><td>$email</td><td>$role</td></tr>\n""")
    player_controls_table_bot = '<tr class="controller"><td colspan="2"><button class="full_width gradient_orange">Update Player Roles</button></2></tr></table>'

    #   campaign view campaign summary
    campaign_summary_survivors_top = '<div id="campaign_summary_survivors">\n<h3 class="mobile_only">Survivors</h3>'
    campaign_summary_survivors_bot = '<hr class="mobile_only"/></div> <!-- campaign_summary_survivors -->'
    export_button = Template("""\n\
    <form method="POST">
     <input type="hidden" name="export_campaign" value="$export_type"/>
     <input type="hidden" name="asset_id" value="$asset_id"/>
     <button class="yellow"> $export_pretty_name </button>
    </form>
    \n""")
    event_log = Template("""\n\
        <span class="desktop_only nav_bar gradient_orange"></span>
        <span class="gradient_orange nav_bar_mobile mobile_only"></span>
        <a id="event_log"><span class="top_nav_spacer mobile_only"> hidden </span></a>
        <h1 class="settlement_name"> $settlement_name Event Log</h1>
        $log_lines
        <a id="genealogy"><br/></a>
        <hr class="mobile_only"/>
        <h1 class="settlement_name"> $settlement_name Lineage and Intimacy Records</h1>
        <p>Survivor ancestry is represented below by organizing survivors into "generations". <b>Intimacy</b> partners are organized into generations according to the Lantern Year in which they are born: in each generation, all children of those partners are shown. Generations are separated by a horizontal rule. The "family tree" style view of survivor generations is only available at wide/desktop resolution.</p>
        <hr class="mobile_only"/>
        $family_tree
        $generations
        $no_family
        <div id="floating_event_log_anchor" class="gradient_orange" ><a href="#event_log"><img src="%s/icons/settlement_event.png"/></a></div>
        <div id="floating_genealogy_anchor" class="gradient_orange" ><a href="#genealogy"><img src="%s/icons/genealogy.png"/></a></div>
        \n""" % (settings.get("application", "STATIC_URL"), settings.get("application", "STATIC_URL")))
    event_table_top = '<table class="settlement_event_log"><tr><th>LY</th><th>Event</th></tr>\n'
    event_table_row = Template('<tr class="zebra_$zebra"><td>$ly</td><td>$event</td></tr>\n')
    event_table_bot = '</table>\n\n'
    genealogy_headline = Template('\n<h3 class="$h_class">$value</h3>\n')
    genealogy_survivor_span = Template('\t<span class="genealogy_survivor $class_color" style="display:$display"><b>$name</b> $born $dead</span>\n')
    timeline_button = Template("""\n
        <form id="autoForm" method="POST" action="#edit_timeline">
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />
            <button id="remove_item" name="increment_lantern_year" class="$button_class $button_color" value="1" $disabled> &nbsp; $LY &nbsp; </button>
        </form>
    \n""")
    timeline_add_event = Template('<input type="text" class="$input_class" onchange="this.form.submit()" event_type="text" name="add_$event_type$LY" placeholder="add $pretty_event_type"/>\n')
    timeline_year_break = '<input type="submit" class="hidden" value="None"/> <hr/></p>\n</form>\n\n'
    timeline_form_top = Template("""\n
            <!-- LY $year form -->
            <form id="autoForm" method="POST" action="#edit_timeline">
            <input type="hidden" name="modify" value="settlement" />
            <input type="hidden" name="asset_id" value="$settlement_id" />
    """)
    summary = Template("""\n\
        <span class="desktop_only nav_bar gradient_purple"></span>
        <span class="gradient_purple nav_bar_mobile mobile_only"></span>
        <span class="top_nav_spacer mobile_only"> hidden </span>
        <h1 class="settlement_name"> %s $settlement_name</h1>
        <div id="campaign_summary_pop">
            <p>Population: $population ($sex_count); $death_count deaths</p>
            <hr class="mobile_only"/>
            <p>LY: $lantern_year, Survival Limit: $survival_limit</p>
            <hr class="mobile_only"/>
        </div>
        <form method="POST" class="mobile_only">
          <input type="hidden" name="change_view" value="new_survivor"/>
          <button class="full_width survivor bold" id="campaign_summary_new_survivor">+ Create New Survivor</button>
          <hr/>
        </form>


        <a id="edit_hunting_party" class="mobile_only"></a>
        <span class="vertical_spacer desktop_only"></span>

        $survivors

        <hr class="mobile_only invisible">
        <br class="mobile_only">

        <div id="campaign_summary_facts_box">
            <form method="POST">
            <input type="hidden" name="change_view" value="new_survivor"/>
            <button class="bold survivor desktop_only" id="campaign_summary_new_survivor">+ Create New Survivor</button>
            </form>

            $special_rules

            <hr class="mobile_only">

            <div class="campaign_summary_small_box endeavor_box">
                <h4>Available Endeavors</h4>
                $endeavors
            </div>
            <div class="campaign_summary_small_box">
                <h4>Settlement Bonuses</h4>
                $settlement_bonuses
                $survivor_bonuses
            </div>
            <hr class="mobile_only"/>
            <div class="campaign_summary_small_box">
                <h3>Principles</h3>
                $principles
            </div>
            <div class="campaign_summary_small_box">
                <h3>Innovations</h3>
                $innovations
            </div>
            <hr class="mobile_only"/>
            <div class="campaign_summary_small_box">
                <h3>Locations</h3>
                <p>$locations</p>
            </div>
            <hr class="mobile_only"/>
            <div class="campaign_summary_small_box">
                <h3>Monsters</h3>
                <h4>Defeated</h4>
                <p>$defeated_monsters</p>
                <h4>Quarries</h4>
                <p>$quarries</p>
                <h4>Nemeses</h4>
                <p>$nemesis_monsters</p>
            </div>
        </div>
        <div id="export_controls">
            <hr class="mobile_only"/>
            $export_xls
        </div>
    \n""" % dashboard.campaign_flash)
    form = Template("""\n\
    $game_link

    <span class="desktop_only nav_bar gradient_orange"></span>
    <span class="gradient_orange nav_bar_mobile mobile_only"></span>
    <span class="top_nav_spacer mobile_only"> hidden </span>
    <br class="desktop_only"/>

    <div id="asset_management_left_pane">
        <form method="POST" id="autoForm" action="#">
            <button id="save_button" class="success">Save</button>
            <input type="hidden" name="modify" value="settlement" />
            <input type="hidden" name="asset_id" value="$settlement_id" />

            <p class="center" title="Campaign type may not be changed after a settlement is created!">$campaign</p>
            <input id="topline_name" onchange="this.form.submit()" class="full_width" type="text" name="name" value="$name" placeholder="Settlement Name"/>
            $abandoned
            <hr class="mobile_only"/>
            <div class="settlement_form_wide_box">
                <div class="big_number_container left_margin">
                    <button class="incrementer mobile_only" onclick="increment('survivalLimitBox');">+</button>
                    <input id="survivalLimitBox" class="big_number_square" type="number" name="survival_limit" value="$survival_limit" min="$min_survival_limit"/>
                    <button class="decrementer mobile_only" onclick="decrement('survivalLimitBox');">-</button>
                </div>
                <div class="big_number_caption">Survival Limit<br />(min: $min_survival_limit)</div>
            </div>
            <br class="mobile_only"/>
            <hr class="mobile_only"/>

            <div class="settlement_form_wide_box">
                <div class="big_number_container left_margin">
                    <button class="incrementer mobile_only" onclick="increment('populationBox');">+</button>
                    <input id="populationBox" class="big_number_square" type="number" name="population" value="$population" min="0"/>
                    <button class="decrementer mobile_only" onclick="decrement('populationBox');">-</button>
                </div>
                <div class="big_number_caption">Population</div>
            </div> <!-- settlement_form_wide_box -->

            <br class="mobile_only"/><hr class="mobile_only"/>

            <div class="settlement_form_wide_box">
                <div class="big_number_container left_margin">
                    <button class="incrementer mobile_only" onclick="increment('deathCountBox');">+</button>
                    <input id="deathCountBox" class="big_number_square" type="number" name="death_count" value="$death_count" min="0"/>
                    <button class="decrementer mobile_only" onclick="decrement('deathCountBox');">-</button>
                </div>
                <div class="big_number_caption">Death Count</div>
            </div> <!-- settlement_form_wide_box -->
        </form> <!-- ending the first form -->

            <hr />

        <h3>Bulk Add New Survivors</h3>
        <form method="POST">
          <input type="hidden" name="bulk_add_survivors" value="settlement" />
          <input type="hidden" name="asset_id" value="$settlement_id" />
            <div id="bulk_add_survivors">
                <div class="bulk_add_control">
                    Male
                    <button type="button" class="incrementer" onclick="increment('maleCountBox');">+</button>
                    <input id="maleCountBox" class="big_number_square" type="number" name="male_survivors" value="0" min="0"/>
                    <button type="button" class="decrementer" onclick="decrement('maleCountBox');">-</button>
                </div>
                <div class="bulk_add_control">
                    Female
                    <button type="button" class="incrementer" onclick="increment('femaleCountBox');">+</button>
                    <input id="femaleCountBox" class="big_number_square" type="number" name="female_survivors" value="0" min="0"/>
                    <button type="button" class="decrementer" onclick="decrement('femaleCountBox');">-</button>
                </div>
    <a id="settlement_notes" class="mobile_only"></a>
            <input type="submit" class="yellow full_width" value="Create New Survivors" />
            </div> <!-- bulk_add_survivors -->
        </form>
        <hr/>

        <h3>Settlement Notes</h3>
        <form id="autoForm" method="POST" action="#settlement_notes">
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />
        <textarea onchange="this.form.submit()"id="settlement_notes" name="settlement_notes" placeholder="Additional settlement notes">$settlement_notes</textarea>
        <button class="full_width yellow">Update Notes</button>
        </form>
        <hr/>



                    <!-- REMOVE FROM STORAGE - THIS IS ITS OWN FORM-->
        <form method="POST" action="#edit_storage">
            <input type="hidden" name="modify" value="settlement" />
            <input type="hidden" name="asset_id" value="$settlement_id" />
            <button id="remove_item" class="hidden" style="display: none" name="remove_item" value="" /> </button>
            <div id="block_group">
            <h2>Storage</h2>
            <p>Gear and Resources may be stored without limit.<br/><br/>
                <button id="modalStorageButton" class="yellow bold">+ Add Item to Storage</button><br><br class="desktop_only">
            <a id="edit_storage" class="mobile_only"/></a>
                $storage
        </form>

        <script>
        window.onload = function(){
            var modal = document.getElementById('modalStorage');
            var btn = document.getElementById("modalStorageButton");
            var span = document.getElementsByClassName("close")[0];
            btn.onclick = function(b) {b.preventDefault(); modal.style.display = "block";}
            span.onclick = function() {modal.style.display = "none";}
            window.onclick = function(event) {if (event.target == modal) {modal.style.display = "none";}}
        };
        </script>



        <div id="modalStorage" class="modal">

          <!-- Modal content -->
            <div class="modal-content">
                <span class="close">×</span>

                    <!-- ADD TO STORAGE - THIS IS ITS OWN FORM-->
                <form id="autoForm" method="POST" action="#edit_storage">
                    <input type="hidden" name="modify" value="settlement" />
                    <input type="hidden" name="asset_id" value="$settlement_id" />

                     <div class="big_number_container left_margin negative_30px_bottom_margin">
                         <button type="button" class="incrementer" onclick="increment('addStorageBox');">+</button>
                         <input id="addStorageBox" class="big_number_square" type="number" name="add_item_quantity" value="1" min="1"/>
                         <button type="button" class="decrementer" onclick="decrement('addStorageBox');">-</button>
                     </div> <!-- big_number_container -->
                     <div class="big_number_caption">Quantity</div>
                    <hr>

                    $add_to_storage_controls

                    <input type="text" class="full_width" name="add_item" placeholder="Add custom item to storage"/>
                    <center><button class="yellow">Submit</button></center>
                    <br><br><br>
                </form>
            </div> <!-- modal-content -->
        </div> <!-- modalStorage -->
     </div></div> <!-- asset_management_left_pane -->
    <div id="asset_management_middle_pane">

                    <!-- LOCATIONS - THIS HAS ITS OWN FORM  -->

        <a id="edit_locations" class="mobile_only"><a/>

        <div id="block_group">
         <h2>Settlement Locations</h2>
         <p>Locations in your settlement.</p>
         <hr/>
         $locations

        <form id="autoForm" method="POST" action="#edit_locations">
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />
         $locations_add
         $locations_rm
        </div>
        </form>


                    <!-- INNOVATIONS - HAS ITS OWN FORM-->

        <a id="edit_innovations" class="mobile_only"/></a>
        <form id="autoForm" method="POST" action="#edit_innovations">
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />
        <div id="block_group">
         <h2>Innovations</h2>
         <p>The settlement's innovations (including weapon masteries).</p>
        <hr/>
         $innovations
         $innovations_add
         $innovations_rm
         $innovation_deck
        </div>
        </form>

                    <!-- PRINCIPLES - HAS ITS OWN FORM-->

        <a id="edit_principles" class="mobile_only"></a>
        <form id="autoForm" method="POST" action="#edit_principles">
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />
        <div id="block_group">
         <h2>Principles</h2>
         <p>The settlement's established principles.</p>
        <hr/>

        $principles_controls
        $principles_rm

        </div> <!-- principle block group -->
        </form>




                       <!-- MILESTONES - HAS ITS OWN FORM-->

        <a id="edit_milestones" class="mobile_only"/></a>
        <form id="autoForm" method="POST" action="#edit_milestones">
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />
        <div id="block_group">
         <h2>Milestone Story Events</h2>
         <p>Trigger these story events when milestone condition is met.</p>
         <input type="hidden" name="milestone" value="none"/> <!-- hacks! -->
         <input type="hidden" name="milestone" value="none"/> <!-- need both of these -->
            $milestone_controls

        </div>
        </form>



                    <!-- QUARRIES - HAS ITS OWN FORM-->

        <a id="edit_quarries"/>
        <form id="autoForm" method="POST" action="#edit_quarries">
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />

        <div id="block_group">
         <h2>Quarries</h2>
         <p>The monsters your settlement can select to hunt.</p>
        <hr />
         <p>$quarries</p>
            $quarry_options
         <input onchange="this.form.submit()" type="text" class="full_width" name="add_quarry" placeholder="add custom quarry"/>
        </div>

        </form>

                    <!-- NEMESIS MONSTERS -->
        <a id="edit_nemeses"/>
        <form id="autoForm" method="POST" action="#edit_nemeses">
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />

        <div id="block_group">
        <h2>Nemesis Monsters</h2>
        <p>The available nemesis encounter monsters.</p>
        <hr>
        $nemesis_monsters
        </div>
        </form>

                    <!-- DEFEATED MONSTERS: HAS ITS OWN FORM -->

        <a id="edit_defeated_monsters"/>
        <form id="autoForm" method="POST" action="#edit_defeated_monsters">
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />

            <div id="block_group">
             <h2>Defeated Monsters</h2>
             <p>A list of defeated monsters and their level.</p>
            <hr/>
             $defeated_monsters
             $defeated_monsters_add
             $defeated_monsters_rm
            </div>
        </form>
        </div>


        <div id="asset_management_right_pane">

                    <!-- TIMELINE: HAS ITS OWN FORM  -->
        <a id="edit_timeline" class="mobile_only"><br/><br/><br/></a>
        <h2 class="clickable gradient_orange" onclick="showHide('timelineBlock')">LY $lantern_year - View Timeline <img class="dashboard_down_arrow" src="http://media.kdm-manager.com/icons/down_arrow.png"/> </h2>
        <div id="timelineBlock" class="block_group" style="display: $display_timeline;">
         <div class="big_number_container left_margin">
             <button class="incrementer" onclick="increment('lanternYearBox');">+</button>

            <form id="autoForm" method="POST" action="#edit_timeline">
            <input type="hidden" name="modify" value="settlement" />
            <input type="hidden" name="asset_id" value="$settlement_id" />
            <input id="lanternYearBox" onchange="this.form.submit()" class="big_number_square" type="number" name="lantern_year" value="$lantern_year" min="0"/>
            </form>
             <button class="decrementer" onclick="decrement('lanternYearBox');">-</button>
         </div>
         <div class="big_number_caption">Lantern Year</div>


         <br class="mobile_only"/>
        <p>Tap or click a Lantern Year number to mark it complete (and end it).</p>
        <hr>
         $timeline
        </div> <!-- timelineBlock -->


        <br class="mobile_only"/>

                    <!-- LOST SETTLEMENTS HAS ITS OWN FORM-->
        <div class="block_group">
            <a id="edit_lost_settlements" class="mobile_only"></a>
            <form id="autoForm" method="POST" action="#edit_lost_settlements">
            <input type="hidden" name="modify" value="settlement" />
            <input type="hidden" name="asset_id" value="$settlement_id" />

            <input onchange="this.form.submit()" class="big_number_square" type="number" name="lost_settlements" value="$lost_settlements"/>
            <h3>Lost Settlements</h3>
            <p>Refer to <font class="kdm_font">g</font> <b>Game Over</b> on p.179: <b>Left Overs</b> occurs at 4; <b>Those Before Us</b> occurs at 8; <b>Ocular Parasites</b> occurs at 12; <b>Rainy Season</b> occurs at 16.</p>
            </form>
        </div>

        <br>
        <hr/>
        <h3>Expansions</h3>
        <a id="edit_expansions" class="mobile_only"></a>
        $expansions_block
        <br /><br/>
        <hr/>

        <h3>Players</h3>
        <form id="autoForm" method="POST" action="#edit_expansions">
            <input type="hidden" name="modify" value="settlement" />
            <input type="hidden" name="asset_id" value="$settlement_id" />
            $player_controls
        </form>

        <hr/>

        <form method="POST" onsubmit="return confirm('This will prevent this settlement from appearing on any user Dashboard, including yours. Press OK to Abandon this settlement forever.');">
            <input type="hidden" name="modify" value="settlement" />
            <input type="hidden" name="asset_id" value="$settlement_id" />
            <input type="hidden" name="abandon_settlement" value="toggle" />

            <h3>Abandon Settlement</h3>
            <p>Mark a settlement as "Abandoned" to prevent it from showing up in your active campaigns without removing it from the system.</p>
            <button class="full_width warn"> Abandon Settlement! </button>
        </form>

    $remove_settlement_button

    </div>
    \n""")
    remove_settlement_button = Template("""\
    <hr/>
    <h3>Permanently Remove Settlement</h3>
    <form method="POST" onsubmit="return confirm('Press OK to permanently delete this settlement AND ALL SURVIVORS WHO BELONG TO THIS SETTLEMENT forever. Please note that this CANNOT BE UNDONE and is not the same as marking a settlement Abandoned. Consider abandoning old settlements rather than removing them, as this allows data about the settlement to be used in general kdm-manager stats.');"><input type="hidden" name="remove_settlement" value="$settlement_id"/><button class="full_width error">Permanently Delete Settlement</button></form>
    """)
    expansions_block_slug = Template("""\n\
    <form id="autoForm" method="POST" action="#edit_lost_settlements">
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />
        <p>
            <input type="hidden" name="expansion_$key" value="unchecked"/>
            <input name="expansion_$key" onchange="this.form.submit()" id="$nickname" class="radio_principle" type="checkbox" $checked />
            <label for="$nickname" class="radio_principle_label">$key</label>
        </p>
    </form>
    \n""")

    location_level_controls = Template("""\n\
    $location_name - Lvl 
    <form id="autoForm" method="POST" action="#edit_locations" class="location_level">
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />
        <select class="location_level" name="location_level_$location_name" onchange="this.form.submit()">
            $select_items
        </select>
    </form>
    \n""")
    milestone_control = Template("""\n
    <hr />
    <input onchange="this.form.submit()" id="$handle" type="checkbox" name="milestone" value="$key" class="radio_principle" $checked></input>
    <label for="$handle" class="radio_principle_label">$key</label>
    <p> &ensp; <font class="kdm_font">g</font> <b>$story_event</b> (p.$story_page) </p>
    \n""")
    principles_all_hidden_warning = '<p>(Update settlement Milestones to show controls for adding Settlement Principles.)</p>'
    principle_radio = Template("""\n
        <input onchange="this.form.submit()" type="radio" id="$handle" class="radio_principle" name="principle_$principle_key" value="$option" $checked /> 
        <label class="radio_principle_label" for="$handle"> $option </label>
    \n""")
    principle_control = Template("""\n
    <div>
    <h3>$name Principle</h3>
    <fieldset class="settlement_principle">
        $radio_buttons
    </fieldset>
    </div>
    \n""")
    special_rule = Template("""\n
    <div class="campaign_summary_special_rule" style="background-color: #$bg_color; color: #$font_color">
    <h3>$name</h3>
    $desc
    </div>
    """)
    endeavor = Template("""\n
    <p style="background-color: #$bg_color; color: #$font_color">
    &nbsp; $cost $name$punc $desc $type
    </p>
    """)


class login:
    """ The HTML for form-based authentication goes here."""
    form = """\n\
    <div id="sign_in_container">
        <img src="%s/tree_logo_shadow.png" class="sign_in"/>
        <h2 class="seo">KD:M Manager!</h2>
        <h1 class="seo">An interactive campaign manager for <a href="http://kingdomdeath.com/" target="top">Kingdom Death: <i>Monster</i></a>.</h1>
        <div id="sign_in_last_updated">%s</div>
        <div id="sign_in_controls">
            <form method="POST">
            <input class="sign_in" type="email" name="login" placeholder="Email"/ autofocus>
            <input class="sign_in" type="password" name="password" placeholder="Password"/>
			<div id="sign_in_remember_me">
			  <label class="sign_in" for="keep_me_signed_in">Stay Logged in:</label>
			</div>
			<div id="sign_in_checkbox">
			  <input type="checkbox" class="sign_in" name="keep_me_signed_in" id="keep_me_signed_in">
			</div>
			<div id="sign_in_button">
			  <button class="sign_in green">Sign In or Register</button>
			</div>
            </form>
            <br class="mobile_only"/>
            <form method="POST">
            <input type="hidden" name="recover_password" value="True"/>
            <button class="gradient_black tiny_button">Forgot Password?</button>
            </form>
        </div>
    </div> <!-- sign_in_container -->
    \n""" % (settings.get("application", "STATIC_URL"), get_latest_update_string())
    new_user = Template("""\n\
    <div id="sign_in_container">
        <h2 class="seo">Create a New User!</h2>
        <h1 class="seo">Use an email address to share campaigns with friends.</h1>
        <div id="sign_in_controls">
            <form method="POST">
            <input class="sign_in" type="email" name="login" value="$login"/>
            <input class="sign_in" type="password" name="password" placeholder="password" autofocus/>
            <input class="sign_in" type="password" name="password_again" placeholder="password (again)"/>
			<div id="sign_in_remember_me">
			  <label class="sign_in" for="keep_me_signed_in">Stay Logged in:</label>
			</div>
			<div id="sign_in_checkbox">
			  <input type="checkbox" class="sign_in" name="keep_me_signed_in" id="keep_me_signed_in">
			</div>
            <button class="sign_in green">Register New User</button>
            </form>
        </div>
    </div> <!-- sign_in_container -->
    \n""")
    reset_pw = Template("""\n\
    <div id="sign_in_container">
        <h2 class="seo">Reset Password!</h2>
        <h1 class="seo">Reset the password for $login.</h1>
        <div id="sign_in_controls">
            <form method="POST" action="/">
            <input type="hidden" name="login" value="$login"/>
            <input type="hidden" name="recover_password" value="True"/>
            <input type="hidden" name="recovery_code" value="$recovery_code"/>
            <input class="sign_in" type="password" name="password" placeholder="password" autofocus/>
            <input class="sign_in" type="password" name="password_again" placeholder="password (again)"/>
            <input type="submit" class="sign_in gradient_green" value="Reset Password"/>
            </form>
        </div>
    </div> <!-- sign_in_container -->
    \n""")
    recover_password = """\n\
    <div id="sign_in_container">
        <h2 class="seo">Password Recovery!</h2>
        <h1 class="seo">Enter your email address below to receive an email with recovery instructions.</h1>
        <div id="sign_in_controls">
            <form method="POST">
            <input type="hidden" name="recover_password" value="True"/>
            <input class="sign_in" type="text" name="login" placeholder="email" autofocus/>
            <button class="sign_in gradient_green">Recover Password</button>
            </form>
        </div>
    </div> <!-- sign_in_container -->
    \n"""
    recovery_successful = """\n\
    <div id="sign_in_container">
        <h2 class="seo">Password Reset!</h2>
        <h1 class="seo">Use the link below to log in with your new password.</h1>
        <div id="sign_in_controls">
            <a href="">http://kdm-manager.com</a>
        </div>
    </div> <!-- sign_in_container -->
    \n"""
    pw_recovery_email = Template("""\n\
    Hello $login!<br/><br/>&ensp;You are receiving this message because a password recovery request was made at <a href="http://kdm-manager.com">http://kdm-manager.com</a> for your user, $login.<br/><br/>If you made this request and would like to reset your password, please use the following URL:<br/><br/>&ensp;<a href="http://kdm-manager.com?recover_password=True&recovery_code=$recovery_code">http://kdm-manager.com?recover_password=True&recovery_code=$recovery_code</a><br/><br/>If you did not create this request, you may ignore this email and continue to use your existing/current credentials.<br/><br/>Thanks again for using the manager!<br/><br/>Your friend,<br/>Timothy O'Connell<br/><br/>
    \n""")



class meta:
    """ This is for HTML that doesn't really fit anywhere else, in terms of
    views, etc. Use this for helpers/containers/administrivia/etc. """

    basic_http_header = "Content-type: text/html\n\n"
    basic_file_header = "Content-Disposition: attachment; filename=%s\n"
    error_500 = Template('%s<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN"><html><head><title>%s</title></head><body><h1>500 - Internal Server Error</h1><hr/><p>$msg</p><hr/><p>Please report all issues at <a href="https://github.com/toconnell/kdm-manager/issues">https://github.com/toconnell/kdm-manager/issues</a><br/><br/>Use the information below to report the error:</p><hr/><p>%s</p>$exception' % (basic_http_header, settings.get("application","title"), datetime.now()))
    start_head = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n<title>%s</title>\n<link rel="stylesheet" type="text/css" href="/style.css">\n' % settings.get("application","title")
    close_body = '\n </div><!-- container -->\n</body>\n</html>'
    saved_dialog = '\n    <div id="saved_dialog" class="success">Saved!</div>'
    log_out_button = Template('\n\t<hr class="mobile_only"/><form id="logout" method="POST"><input type="hidden" name="remove_session" value="$session_id"/><input type="hidden" name="login" value="$login"/><button class="gradient_white change_view mobile_only">SIGN OUT</button>\n\t</form>')
    mobile_hr = '<hr class="mobile_only"/>'
    dashboard_alert = Template("""\n\
    <br/><br/><br/>
    <div class="dashboard_alert maroon">
    $msg
    </div>
    \n""")




#
#   application helper functions for HTML interfacing
#

def set_cookie_js(session_id):
    """ This returns a snippet of javascript that, if inserted into the html
    head will set the cookie to have the session_id given as the first/only
    argument to this function.

    Note that the cookie will not appear to have the correct session ID until
    the NEXT page load after the one where the cookie is set.    """
    expiration = datetime.now() + timedelta(days=30)
    cookie = Cookie.SimpleCookie()
    cookie["session"] = session_id
    cookie["session"]["expires"] = expiration.strftime("%a, %d-%b-%Y %H:%M:%S PST")
    return cookie.js_output()


def authenticate_by_form(params):
    """ Pass this a cgi.FieldStorage() to try to manually authenticate a user"""

    err_msg = ""

    if "password_again" in params:
        if "login" in params and "password" in params:
            create_new = admin.create_new_user(params["login"].value.strip().lower(), params["password"].value.strip(), params["password_again"].value.strip(), params)
            if create_new == False:
                err_msg = user_error_msg.safe_substitute(err_class="warn", err_msg="Passwords did not match! Please re-enter.")
            elif create_new is None:
                err_msg = user_error_msg.safe_substitute(err_class="warn", err_msg="Email address could not be verified! Please re-enter.")
            elif create_new == True:
                pass
            else:
                logger.exception("admin.create_new_user returned unexpected results!")
                logger.error(create_new)
    if "login" in params and "password" in params:
        auth = admin.authenticate(params["login"].value.strip().lower(), params["password"].value.strip())
        if auth == False:
            output = user_error_msg.safe_substitute(err_class="error", err_msg="Invalid password! Please re-enter.")
            output += login.form
        elif auth is None:
            output = login.new_user.safe_substitute(login=params["login"].value.strip().lower())
            output += err_msg
        elif auth == True:

            s = Session()
            session_id = s.new(params["login"].value.strip().lower())
            s.User.mark_usage("authenticated successfully")

			# handle preserve sessions checkbox on the sign in view
            if "keep_me_signed_in" in params:
                if "preferences" not in s.User.user:
                    s.User.user["preferences"] = {}
                s.User.user["preferences"]["preserve_sessions"] = True
                mdb.users.save(s.User.user)

            html, body = s.current_view_html()
            render(html, body_class=body, head=[set_cookie_js(session_id)])
    else:
        output = login.form
    return output



#
#   render() funcs are the only thing that goes below here.
#


def render(view_html, head=[], http_headers=None, body_class=None):
    """ This is our basic render: feed it HTML to change what gets rendered. """

    output = http_headers
    if http_headers is None:
        output = meta.basic_http_header
    else:
        print http_headers
        try:
            print view_html.read()  # in case we're returning StringIO
        except AttributeError:
            print view_html
        sys.exit()

    output += meta.start_head

    output += """\n\
    <link rel="manifest" href="/manifest.json">

    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7/jquery.js"></script>
    <script src="http://malsup.github.com/jquery.form.js"></script>

    <script>

        $(document).ready(function() {

            $('#saved_dialog').hide();

            $('#autoForm').ajaxForm(function() {
                $('#saved_dialog').show();
                $('#saved_dialog').fadeOut(1500)
            });

            $('.autoFormChild').ajaxForm(function() {
                 $('#saved_dialog').show();
                 $('#saved_dialog').fadeOut(1500)
            });

        });

    </script>
    \n"""

    output += """\n\
        <script>
        function toggleDamage(elem_id) {document.getElementById(elem_id).classList.toggle("damage_box_checked");}
        </script>
        <script>
        function increment(elem_id) {
            document.getElementById(elem_id).stepUp();
        }
        function decrement(elem_id) {
            document.getElementById(elem_id).stepDown();
        }
        </script>
        <script>
        function showHide(id) {
            var e = document.getElementById(id);
            if (e.style.display != 'none') e.style.display = 'none';
            else e.style.display = 'block';
        }
        </script>
    \n"""


    output += """\n\
        <script>
          (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
          (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
          m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
          })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
          ga('create', 'UA-71038485-1', 'auto');
          ga('send', 'pageview');
        </script>
    \n"""

    for element in head:
        output += element

    output += '</head>\n<body class="%s">\n <div id="container">\n' % body_class
    output += view_html
    output += meta.close_body

    print(output.encode('utf8'))
    sys.exit(0)     # this seems redundant, but it's necessary in case we want
                    #   to call a render() in the middle of a load, e.g. to just
                    #   finish whatever we're doing and show a page.
