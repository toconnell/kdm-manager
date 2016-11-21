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

    <form method="POST" action="">
        <input type="hidden" name="change_view" value="dashboard"/>
        <button id="admin_panel_floating_dashboard">Dashboard</button>
    </form>

    <div class="admin_panel_floater" id="admin_panel_hostname">host: <code><font class="maroon_text">$hostname</font></code></div>
    <div class="admin_panel_floater" id="admin_panel_api_url">api: <code><font class="maroon_text">$api_url</font></code></div>
    <div class="admin_panel_floater" id="admin_panel_version">version: <code><font class="maroon_text">$version</font></code></div>

    <table id="panel_meta_stats">
        <tr><th colspan="2">Global Stats</th></tr>
        <tr><td>Total Users:</td><td>$users</td></tr>
        <tr class="grey"><td>Recent Users:</td><td>$recent_users_count</td></tr>
        <tr><td>Sessions:</td><td>$sessions</td></tr>
        <tr class="grey"><td>Settlements:</td><td>$settlements</td></tr>
        <tr><td>Survivors:</td><td>$live_survivors/$dead_survivors ($total_survivors total)</td></tr>
        <tr class="world_primary"><th colspan="2">Latest settlement</th></tr>
        <tr class="world_secondary"><td colspan="2">$latest_settlement</td></tr>
        <tr class="world_primary"><th colspan="2">Latest fatality</th></tr>
        <tr class="world_secondary"><td colspan="2">$latest_fatality</td></tr>
        <tr class="world_primary"><th colspan="2">Latest kill</th></tr>
        <tr class="world_secondary"><td colspan="2">$latest_kill</td></tr>
        <tr class="world_primary"><th colspan="2">Current Hunt</th></tr>
        <tr class="world_secondary"><td colspan="2">$current_hunt</td></tr>
    </table>
    <div id="admin_panel_right">
        <h3 class="admin_panel_label">Killboard</h3>
        $killboard
        $world_daemon
    </div>
    \n""")
    panel_table_top = '<table id="panel_aux_table">\n'
    panel_table_header = Template('\t<tr><th colspan="2">$title</th></tr>\n')
    panel_table_row = Template('\t<tr class="$zebra"><td class="key">$key</td><td>$value</td></tr>\n')
    panel_table_bot = '</table>\n'
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
                <form action="#">
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
    panel_button = '<hr class="mobile_only"/><form action="#" method="POST"><input type="hidden" name="change_view" value="panel"/><button id="dashboard_admin_panel_launch_button" class="maroon change_view clear_left">Admin Panel!</button></form>\n'
    new_settlement_button = '<form method="POST" action="#"><input type="hidden" name="change_view" value="new_settlement" /><button class="success">+ New Settlement</button></form>\n'

    # flash
    down_arrow_flash = '<img class="dashboard_down_arrow" src="%s/icons/down_arrow.png"/> ' % settings.get("application", "STATIC_URL")
    campaign_flash = '<img class="dashboard_icon" src="%s/icons/campaign.png"/> ' % settings.get("application", "STATIC_URL")
    settlement_flash = '<img class="dashboard_icon" src="%s/icons/settlement.png"/> ' % settings.get("application", "STATIC_URL")
    system_flash = '<img class="dashboard_icon" src="%s/icons/system.png"/> ' % settings.get("application", "STATIC_URL")
    refresh_flash = '<img class="dashboard_icon" src="%s/icons/refresh.png"/> ' % settings.get("application", "STATIC_URL")
    event_log_flash = '<img class="dashboard_icon" src="%s/icons/settlement_event.png"/> ' % settings.get("application", "STATIC_URL")

    # dashboard accordions
    about = Template("""\n
    <div class="dashboard_menu">
    <h2 class="clickable about_primary" onclick="showHide('about_div')"> <font class="kdm_font dashboard_kdm_font">g</font> About %s</h2>
        <div id="about_div" style="display: none;" class="dashboard_accordion about_secondary">
        <p><b>KD:M Manager! Version $version.</b></p><hr/>
        <p>v$version went live on $latest_change_date. <a target="top" href="$latest_change_link">View change log</a>.</p>
        <p>v1.7.0, the first production release of the Manager, went live on 2015-11-29.</p>
        <p>This application is currently under <i>active development and is running in debug mode!</i></p>
        <hr/>
        <p>More Information:</p>
        <ul>
        <li>Application source code is <a href="https://github.com/toconnell/kdm-manager" target="top">available on GitHub</a>.</li>
        <li>Check <a href="https://github.com/toconnell/kdm-manager/wiki" target="top">the development wiki</a> for complete information about the project.</li>
        <li>Please <a href="https://github.com/toconnell/kdm-manager/issues" target="top">report issues here</a>.</li>
        </ul>

        <p>Credits:</p>
        <ul>
            <li>Developed and maintained by <a href="http://toconnell.info">Timothy O'Connell</a>.</li>
            <li>Icon font ('kdm-font-10') by <a href="http://steamcommunity.com/id/GeorgianBalloon" target="top">Miracle Worker</a>.</li>
        </ul>
        <hr/>
        <p>For more information, including complete release notes and updates, or to make comments/ask questions about the project, check out the development blog at <a href="http://blog.kdm-manager.com" target="top"/>blog.kdm-manager.com</a>.</p>

        </div> <!-- about_div -->
    </div>
    \n""" % (down_arrow_flash))
    preference_header = Template("<p>&ensp; <b>$title:</b></p>")
    preference_footer = "<br/><br/>"
    preference_block = Template("""\n
    <hr/>
    <p>$desc</p>
    <p>
     <input style="display: none" id="pref_true_$pref_key" class="radio_principle" type="radio" name="$pref_key" value="True" $pref_true_checked/>
     <label for="pref_true_$pref_key" class="radio_principle_label"> $affirmative </label><br>
     <input style="display: none" id="pref_false_$pref_key" class="radio_principle" type="radio" name="$pref_key" value="False" $pref_false_checked /> 
     <label for="pref_false_$pref_key" class="radio_principle_label"> $negative </label> 
    </p>
    \n""")
    motd = Template("""\n
	<img class="dashboard_bg" src="%s/tree_logo_shadow.png">
    <div class="dashboard_menu">
        <h2 class="clickable system_primary" onclick="showHide('system_div')"> <img class="dashboard_icon" src="%s/icons/system.png"/> System %s</h2>
        <div id="system_div" style="display: none;" class="dashboard_accordion system_secondary">

        <div class="dashboard_preferences">
            <p>Use the controls below to update application-wide preferences. Remember to click the "Save/Update Preferences" button below when you are finished!</p><br/>
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

        <h3>User Management</h3>
        <p>Currently signed in as: <i>$login</i> (last sign in: $last_sign_in)</p>
        $last_log_msg
        <div class="dashboard_preferences">
            <form action="#" method="POST">
            <input type="hidden" name="change_password" value="True"/>
            <input type="password" name="password" class="full_width" placeholder="password">
            <input type="password" name="password_again" class="full_width" placeholder="password (again)"/>
            <button class="warn"> Change Password</button>
            </form>
        </div>
        </div>
    </div>
    """ % (settings.get("application","STATIC_URL"), settings.get("application", "STATIC_URL"), down_arrow_flash))
    campaign_summary = Template("""\n\
    <div class="dashboard_menu">
        <h2 class="clickable campaign_summary_gradient" onclick="showHide('campaign_div')"> <img class="dashboard_icon" src="%s/icons/campaign.png"/> Campaigns %s </h2>
        <div id="campaign_div" style="display: $display" class="dashboard_accordion campaign_summary_gradient">
        <p>Games you are currently playing.</p>
            <div class="dashboard_button_list">
            $campaigns
            </div>
        </div>
    </div>
    \n""" % (settings.get("application", "STATIC_URL"), down_arrow_flash))
    settlement_summary = Template("""\n\
    <div class="dashboard_menu">
        <h2 class="clickable settlement_sheet_gradient" onclick="showHide('settlement_div')"> <img class="dashboard_icon" src="%s/icons/settlement.png"/> Settlements %s </h2>
        <div id="settlement_div" style="display: $display" class="dashboard_accordion settlement_sheet_gradient">
        <p>Manage Settlements you have created.</p>
        <div class="dashboard_button_list">
            %s
            $settlements
        </div>
        </div>
    </div>
    \n""" % (settings.get("application", "STATIC_URL"), down_arrow_flash, new_settlement_button))
    survivor_summary = Template("""\n\
    <div class="dashboard_menu">
        <h2 class="clickable survivor_sheet_gradient" onclick="showHide('survivors_div')"> <img class="dashboard_icon" src="%s/icons/survivor.png"/> Survivors %s</h2>
        <div id="survivors_div" style="display: none;" class="dashboard_accordion survivor_sheet_gradient">
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
    <div class="dashboard_menu world_panel" # burger/sidenav>
        <h2 class="clickable world_primary" onclick="showHide('world_div')"> <img class="dashboard_icon" src="%s/icons/world.png"/> World %s</h2>
        <div id="world_div" style="display: none;" class="dashboard_accordion world_secondary">


        <p><font class="green_text"><b>$active_settlements</b></font> settlements are holding fast; <font class="maroon_text"><b>$abandoned_settlements</b></font> settlements have been abandoned.</p>
        <p><font class="green_text"><b>$live_survivors</b></font> survivors are alive and fighting; <font class="maroon_text"><b>$dead_survivors</b></font> have perished.</p>

        <h3>Settlement Statistics</h3>
        <ul>
            <li>Multiplayer settlements: $total_multiplayer</li>
            <li>Settlements created in the last 30 days: $new_settlements_last_30</li>
        </ul>
        <p>Top five settlement names:</p>
        $top_settlement_names
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
        <p>Campaign counts:</p>
        <ul>
            $campaign_popularity_bullets
        </ul>
        <p>Latest settlement:</p>
        $latest_settlement


        <h3>Survivor Statistics</h3>
        <p>Top five survivor names:</p>
        $top_survivor_names
        <p>Top 10 causes of death:</p>
        $top_COD
        <p>Averages for all living survivors:</p>
        <ul>
            <li>Hunt XP: $avg_hunt_xp</li>
            <li>Insanity: $avg_insanity</li>
            <li>Courage: $avg_courage</li>
            <li>Fighting Arts: $avg_fighting_arts</li>
            <li>Understanding: $avg_understanding</li>
            <li>Disorders: $avg_disorders</li>
            <li>Abilities/Impairments: $avg_abilities</li>
        </ul>
        <p>Latest Fatality:</p>
        $latest_fatality
        <p>Newest Survivor:</p>
        $latest_survivor


        <h3>Monster Statistics</h3>
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


        <h3>User Statistics</h3>
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

    refresh_button = '\t<form method="POST" action="#"><button id="floating_refresh_button" class="yellow"> %s </button></form>\n' % refresh_flash
    view_asset_button = Template("""\n\
    <form method="POST" action="#">
    <input type="hidden" name="view_$asset_type" value="$asset_id" />
    <button id="$button_id" class="$button_class $disabled" $disabled>$asset_name <span class="tablet_and_desktop">$desktop_text</span></button>
    </form>
    \n""")





class survivor:
    no_survivors_error = '<!-- No Survivors Found! --> <div class="no_survivors_error"><p>Use the navigation menu controls in the upper left to add new survivors!</p></div>'
    new = Template("""\n\
    <span class="tablet_and_desktop nav_bar survivor_sheet_gradient"></span>
    <span class="mobile_only nav_bar_mobile survivor_sheet_gradient"></span>
    <span class="top_nav_spacer mobile_only">hidden</span>

    <br/>

    <div id="create_new_asset_form_container">
        <form method="POST" action="#" enctype="multipart/form-data">
        <input type="hidden" name="new" value="survivor" />
        <input type="hidden" name="settlement_id" value="$home_settlement">
        <input type="text" id="new_asset_name" name="name" placeholder="New Survivor Name" class="full_width" autofocus>

        <div id="block_group">
            <hr class="invisible">
            <p style="margin-top:10px;">Survivor Image (optional):<br/><br/>
                <input type="file" name="survivor_avatar" accept="image/*">
            </p>
        </div>

        <div id="block_group">
        <h2 class="new_asset">Survivor Sex</h2>
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
            <h2 class="new_asset">Permissions</h2>
            <p class="new_asset">Survivor Owner:</p>
            <input id="survivor_owner" type="email" name="email" placeholder="Survivor Email" value="$user_email">

            <p class="new_asset">
            Toggle the options below to control access to this survivor:<br/><br/>
                <input type="checkbox" id="public" class="radio_principle" name="toggle_public" > 
                <label class="radio_principle_label" for="public"> Public: anyone may manage this Survivor </label>
            </p>
            <br/><br/>
            </div>

            <br />

            <button class="success">SAVE</button>
            </form>
        </div><!-- create_new_asset_block -->
    </div>
    \n""")
    add_ancestor_top = '    <div id="block_group" title="Add survivor parents.">\n    <h2>Survivor Parents</h2>\n<p class="new_asset">Survivors without parents are not eligible for the auto-application of Innovation bonuses granted only to newborn survivors!</p>'
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
            $constellation
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
    <span class="tablet_and_desktop nav_bar survivor_sheet_gradient"></span>
    <span class="mobile_only nav_bar_mobile survivor_sheet_gradient"></span>
    <span class="top_nav_spacer mobile_only">hidden</span>

    <br class="tablet_and_desktop"/>

    <div id="asset_management_left_pane">

       <input
            id="survivor_sheet_survivor_name"
            type="text" name="name" value="$name"
            placeholder="Survivor Name"
            onchange="updateAssetAttrib(this, 'survivor', '$survivor_id')"
            onClick="this.select()"
        />

        <div class="survivor_sheet_survivor_name_from_top_spacer mobile_only"/>&nbsp</div>

        $epithet_controls

        $affinity_controls

        <p>
            Survivor Sex:
            <input
                id="survivor_sheet_survivor_sex"
                class="survivor_sex_text"
                name="sex" value="$sex"
                onchange="updateAssetAttrib(this, 'survivor', '$survivor_id')"
            />

            $mobile_avatar_img
        </p>

        <br/>

        <div id="survivor_dead_retired_container">

            <input
                id="favorite"
                class="radio_principle"
                type="checkbox"
                name="toggle_favorite"
                value="checked"
                $favorite_checked
                onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
            />
            <label
                class="radio_principle_label toggle_favorite"
                for="favorite"
            >
                &#9733; Favorite
            </label>

            <button
                id="modalDeathButton"
                class="$death_button_class"
                title="Mark this survivor as dead"
            >
                Dead
            </button>

            <input
                id="retired"
                class="radio_principle"
                type="checkbox"
                name="toggle_retired"
                value="checked"
                $retired_checked
                onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
            >
            <label
                class="radio_principle_label"
                for="retired"
                style="float: right; clear: none;"
            >
                Retired &nbsp;
            </label>


            </div> <!-- survivor_dead_retired_container -->


            <hr />


            <div id="survivor_survival_box_container">

                <div class="big_number_container left_margin">
                    <button
                        class="incrementer"
                        onclick="increment('survivalBox'); updateAssetAttrib('survivalBox','survivor','$survivor_id');"
                    >
                        +
                    </button>
                    <input
                        id="survivalBox"
                        class="big_number_square"
                        type="number"
                        name="survival" value="$survival"
                        min="0"
                        onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
                    />
                    <button
                        class="decrementer"
                        onclick="decrement('survivalBox'); updateAssetAttrib('survivalBox','survivor','$survivor_id');"
                    >
                        -
                    </button>
                </div> <!-- big_number_container -->

                <div class="big_number_caption">
                    Survival <p>(max: $survival_limit)</p>
                </div>

            </div> <!-- survivor_survival_box_container -->


            <hr />


            <div id="survivor_survival_actions_container">

                <h3>Survival Actions</h3>

                <p>
                     <input
                        id="cannot_spend_survival"
                        class="radio_principle"
                        name="toggle_cannot_spend_survival"
                        onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
                        type="checkbox"
                        value="checked" $cannot_spend_survival_checked
                     />

                     <label
                        id="cannot_spend_survival"
                        class="radio_principle_label float_right_toggle"
                        for="cannot_spend_survival">
                            Cannot<br/>spend<br/>survival
                     </label>

                    $survival_actions

                </p>


                $desktop_avatar_img

                <button class="orange bold $constellation_button_class" id="constellationModalOpener">
                    Dragon Traits ($number_of_dragon_traits)
                </button>

            </div> <!-- survivor_survival_actions_container -->


            <a id="edit_attribs">
                <hr>
            </a>

            <h3>Bonuses</h3>
            $settlement_buffs
            <hr/>
            <h3>Survivor Notes</h3>
            $survivor_notes


        </div> <!-- asset_management_left_pane -->



                <!-- MIDDLE ASSET MANAGEMENT PANE STARTS HERE -->



        <a id="edit_hit_boxes">
            <hr class="mobile_only"/>
        </a>

        <div id="asset_management_middle_pane">


            <!-- BRAIN -->

            <div class="survivor_hit_box insanity_box">

                <div class="big_number_container right_border">

                    <button
                        class="incrementer"
                        onclick="stepAndSave('up','insanityBox','survivor','$survivor_id');"
                    >
                        +
                    </button>

                    <input
                        id="insanityBox"
                        type="number"
                        class="shield"
                        name="Insanity" min="0"
                        value="$insanity"
                        onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
                    />

                    <font id="hit_box_insanity">Insanity</font>

                    <button
                        class="decrementer"
                        onclick="stepAndSave('down','insanityBox','survivor','$survivor_id');"
                    >
                        -
                    </button>

                 </div> <!-- big_number_container -->

                 <div class="hit_box_detail">
                     <input
                        id="damage_brain_light"
                        name="toggle_brain_damage_light"
                        class="damage_box_$brain_damage_light_checked damage_box"
                        type="submit"
                        value=" "
                        onclick="toggleDamage('damage_brain_light','$survivor_id');"
                    />

                    <h2>Brain</h2>

                </div> <!-- hit_box_detail -->

                <p>If your insanity is 3+, you are <b>Insane</b>.</p>

            </div> <!-- survivor_hit_box -->



            <!-- HEAD -->

            <div class="survivor_hit_box">
                <div class="big_number_container right_border">
                    <button
                        class="incrementer"
                        onclick="stepAndSave('up','headBox','survivor','$survivor_id');"
                    >
                        +
                    </button>
                    <input
                        id="headBox"
                        type="number"
                        class="shield"
                        name="Head"
                        value="$head"
                        min="0"
                        onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
                    />
                    <button
                        class="decrementer"
                        onclick="stepAndSave('down','headBox','survivor','$survivor_id');"
                    >
                        -
                    </button>
                </div>
                <div class="hit_box_detail">
                 <input
                    id="damage_head_heavy"
                    onclick="toggleDamage('damage_head_heavy','$survivor_id');"
                    type="submit"
                    class="damage_box_$head_damage_heavy_checked heavy_damage damage_box"
                    name="toggle_head_damage_heavy"
                    value=" "
                 />
                 <h2>Head</h2>
                </div> <!-- hit_box_detail -->
                <p><b>H</b>eavy Injury: Knocked Down</p>
            </div> <!-- survivor_hit_box -->

            $arms_hit_box
            $body_hit_box
            $waist_hit_box
            $legs_hit_box

            <a id="edit_wpn_prof" class="mobile_and_tablet"></a>
            <hr/>

            <!-- WEAPON PROFICIENCY -->
            <div class="survivor_sheet_secondary_attrib_container">
                <div class="big_number_container">
                    <button
                        class="incrementer"
                        onclick="stepAndSave('up','proficiencyBox','survivor','$survivor_id');"
                    >
                        +
                    </button>
                    <input
                        id="proficiencyBox"
                        name="Weapon Proficiency"
                        class="big_number_square"
                        type="number"
                        value="$weapon_proficiency"
                        min="0"
                        onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
                    />
                    <button
                        class="decrementer"
                        onclick="stepAndSave('down','proficiencyBox','survivor','$survivor_id');"
                    >
                        -
                    </button>
                </div> <!-- big_number_container -->

                <div class="big_number_caption">Weapon Proficiency</div>

                <form method="POST" action="#edit_wpn_prof">
                    <input type="hidden" name="modify" value="survivor" />
                    <input type="hidden" name="asset_id" value="$survivor_id" />
                    $weapon_proficiency_options
                </form>

                <p class="secondary_attrib_tip"><b>Specialist</b> at 3<br/><b>Master</b> at 8.</p>

            </div> <!-- survivor_sheet_secondary_attrib_container -->

            <hr/>


            <!-- COURAGE AND UNDERSTANDING -->

            <div class="survivor_sheet_secondary_attrib_container">
                <div class="big_number_container">
                    <button
                        class="incrementer"
                        onclick="stepAndSave('up','courageBox','survivor','$survivor_id');"
                    >
                        +
                    </button>
                    <input
                        id="courageBox"
                        name="Courage"
                        class="big_number_square"
                        type="number"
                        min="0"
                        value="$courage"
                        onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
                    />
                    <button
                        class="decrementer"
                        onclick="stepAndSave('down','courageBox','survivor','$survivor_id');"
                    >
                        -
                    </button>
                </div>
                <div class="big_number_caption">Courage</div>
                <br class="mobile_only"/>

                 <p class="secondary_attrib_tip">
                    $hunt_xp_3_event
                    <font class="kdm_font">g</font> <b>See the Truth</b> (p.155) occurs at 9.
                </p>

            </div> <!-- survivor_sheet_secondary_attrib_container -->


            <hr/>


            <!-- UNDERSTANDING -->

            <div class="survivor_sheet_secondary_attrib_container">
                <div class="big_number_container">
                    <button
                        class="incrementer"
                        onclick="stepAndSave('up','understandingBox','survivor','$survivor_id');"
                    >
                        +
                    </button>
                    <input
                        id="understandingBox"
                        name="Understanding"
                        class="big_number_square"
                        type="number"
                        min="0"
                        value="$understanding"
                        onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
                    />
                    <button
                        class="decrementer"
                        onclick="stepAndSave('down','understandingBox','survivor','$survivor_id');"
                    >
                        -
                    </button>
                </div>
                <div class="big_number_caption">Understanding</div>

                <br class="mobile_only"/>

                <p class="secondary_attrib_tip">
                    $courage_3_event
                    <font class="kdm_font">g</font> <b>White Secret</b> (p.169) occurs at 9.
                </p>

            </div> <!-- survivor_sheet_secondary_attrib_container -->

        </div> <!-- asset_management_middle_pane -->




                <!-- RIGHT ASSET MANAGEMENT PANE STARTS HERE -->


        <div id="asset_management_right_pane">

        <!-- EXPANSION ATTRIBUTES ; PARTNER CONTROLS -->

        <a id="edit_misc_attribs" class="mobile_and_tablet"> </a>

        <form method="POST" action="#edit_misc_attribs">
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

        <a id="edit_fighting_arts" class="mobile_and_tablet"></a>
        <hr/>

        <input
            id="survivor_sheet_cannot_use_fighting_arts"
            class="radio_principle"
            name="toggle_cannot_use_fighting_arts"
            onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
            type="checkbox"
            value="checked" $cannot_use_fighting_arts_checked
        />
        <label
            id="survivor_sheet_cannot_use_fighting_arts_label"
            class="radio_principle_label float_right_toggle"
            for="survivor_sheet_cannot_use_fighting_arts"
         >
            Cannot use<br/>Fighting Arts
        </label>

        <form method="POST" action=".#edit_fighting_arts">
            <input type="hidden" name="form_id" value="survivor_edit_fighting_arts" />
            <input type="hidden" name="modify" value="survivor" />
            <input type="hidden" name="asset_id" value="$survivor_id" />

            <button class="hidden"></button> <!-- hacks! -->

            <h3>Fighting Arts</h3>

            <p>Maximum 3.</p>

            $fighting_arts
            $add_fighting_arts
            <br class="mobile_only"/>
            $rm_fighting_arts

        </form>


        <a id="edit_disorders" class="mobile_and_tablet"></a>
        <hr />


        <!-- DISORDERS - HAS ITS OWN FORM-->

        <form method="POST" action="#edit_disorders">
            <input type="hidden" name="form_id" value="survivor_edit_disorders" />
            <input type="hidden" name="modify" value="survivor" />
            <input type="hidden" name="asset_id" value="$survivor_id" />

            <h3>Disorders</h3>
            <p class="survivor_sheet_game_asset_tip">Maximum 3.</p>

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
                  <input onchange="updateAssetAttrib(this,'survivor','$survivor_id')" type="checkbox" id="skip_next_hunt" class="radio_principle" name="toggle_skip_next_hunt" value="checked" $skip_next_hunt_checked />
                  <label class="radio_principle_label float_right_toggle" for="skip_next_hunt" id="skip_next_hunt_label"> Skip Next<br/>Hunt </label>
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


        <a id="edit_lineage" class="mobile_and_tablet"></a>
        <hr />

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


            <form action="#" method="POST" onsubmit="return confirm('This cannot be undone! Press OK to permanently delete this survivor forever, which is NOT THE SAME THING as marking it dead: permanently deleting the survivor prevents anyone from viewing and/or editing it ever again! If you are trying to delete all survivors in a settlement, you may delete the settlement from the settlement editing view.');"><input type="hidden" name="remove_survivor" value="$survivor_id"/><button class="error">Permanently Delete Survivor</button></form>
            <div class="survivor_sheet_bottom_attrib_spacer">&nbsp;</div>

    <!-- gotta put this here, outside of the other forms -->
    <form id="avatar_change_form" method="POST" enctype="multipart/form-data" action="#">
    <input type="hidden" name="modify" value="survivor" />
    <input type="hidden" name="asset_id" value="$survivor_id" />
    </form>

        </div> <!-- asset_management_right_pane -->

    <!-- SURVIVOR ATTRIBUTE CONTROLS -->

    $survivor_attrib_controls

    <!-- ONLY MODAL CONTENT PAST THIS POINT!!!! -->

        <div
            id="modalDeath" class="modal"
            ng-init="registerModalDiv('modalDeathButton','modalDeath')"
        >
            <div class="modal-content">
                <span class="closeModal" onclick="closeModal('modalDeath')">×</span>
                <h3>Controls of Death!</h3>
                <form method="POST" action="">
                <input type="hidden" name="modify" value="survivor"/>
                <input type="hidden" name="asset_id" value="$survivor_id"/>
                <input type="hidden" name="unspecified_death" value="True"/>
                <p><b>Choose cause of death:</b></p>
                <p>$cod_options</p>
                <hr/>
                <p>Or enter a custom cause of death:</p>
                <p><input type="text" class="full_width" placeholder="Cause of death" name="custom_cause_of_death" value="$custom_cause_of_death"/></p>
                <button class="error">Die</button>
                </form>
                <hr/>
                <form method="POST" action="">
                <input type="hidden" name="modify" value="survivor"/>
                <input type="hidden" name="asset_id" value="$survivor_id"/>
                <input type="hidden" name="resurrect_survivor" value="True"/>
                <button class="success">Resurrect $name</button>
                </form>

            </div> <!-- modal-content -->
        </div> <!-- modalConstellation -->

        <div
            id="modalConstellation" class="modal"
            ng-init="registerModalDiv('constellationModalOpener','modalConstellation')"
        >
            <div class="modal-content">
                <span class="closeModal" onclick="closeModal('modalConstellation')">×</span>
                <h3>The Constellations</h3>
                $constellation_table
            </div> <!-- modal-content -->
        </div> <!-- modalConstellation -->

        <div
            id="modalAffinity" class="modal"
            ng-init="registerModalDiv('modalAffinityButton','modalAffinity')"
        >
            <div class="modal-content">
                <span class="closeModal" onclick="closeModal('modalAffinity')">×</span>

                <h3>Update Permanent Survivor Affinities</h3>

                <form id="autoForm" method="POST" action="#">
                    <input type="hidden" name="modify" value="survivor" />
                    <input type="hidden" name="asset_id" value="$survivor_id" />
                    <input type="hidden" name="modal_update" value="affinities"/>

                    <div class="bulk_add_control" title="Red affinity controls">
                    <button type="button" class="incrementer" onclick="increment('redCountBox');">+</button>
                    <input id="redCountBox" class="big_number_square" type="number" name="red_affinities" value="$red_affinities"/>
                    <button type="button" class="decrementer" onclick="decrement('redCountBox');">-</button>
                    </div>
                    <div id="affinity_block" class="affinity_red">&nbsp;</div>
                    <hr/>

                    <div class="bulk_add_control" title="Blue affinity controls">
                    <button type="button" class="incrementer" onclick="increment('blueCountBox');">+</button>
                    <input id="blueCountBox" class="big_number_square" type="number" name="blue_affinities" value="$blue_affinities"/>
                    <button type="button" class="decrementer" onclick="decrement('blueCountBox');">-</button>
                    </div>
                    <div id="affinity_block" class="affinity_blue">&nbsp;</div>
                    <hr/>

                    <div class="bulk_add_control" title="Green affinity controls">
                    <button type="button" class="incrementer" onclick="increment('greenCountBox');">+</button>
                    <input id="greenCountBox" class="big_number_square" type="number" name="green_affinities" value="$green_affinities"/>
                    <button type="button" class="decrementer" onclick="decrement('greenCountBox');">-</button>
                    </div>
                    <div id="affinity_block" class="affinity_green">&nbsp;</div>
                    <hr/>

                    <center><button class="green" type="submit">Save!</button></center>
                    <br><br>
                </form>
            </div> <!-- modal-content -->
        </div> <!-- modalAffinity -->

    \n""")
    survivor_sheet_hit_box_controls = Template("""\n

            <!-- $hit_location [ render_hit_box_controls() ] -->

            <div class="survivor_hit_box">
                <div class="big_number_container right_border">
                    <button
                        class="incrementer"
                        onclick="stepAndSave('up','$number_input_id','survivor','$survivor_id');"
                    >
                        +
                    </button>
                    <input
                        id="$number_input_id"
                        type="number"
                        class="shield"
                        name="$hit_location"
                        value="$hit_location_value"
                        min="0"
                        onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
                    />
                    <button
                        class="decrementer"
                        onclick="stepAndSave('down','$number_input_id','survivor','$survivor_id');"
                    >
                        -
                    </button>
                </div>
                <div class="hit_box_detail">
                    <input
                        id="$damage_location_heavy"
                        name="$toggle_location_damage_heavy"
                        value=" "
                        class="$dmg_heavy_checked damage_heavy_checked heavy_damage damage_box"
                        onclick="toggleDamage('$damage_location_heavy','$survivor_id');"
                        type="submit"
                    />
                    <input
                        id="$damage_location_light"
                        name="$toggle_location_damage_light"
                        onclick="toggleDamage('$damage_location_light','$survivor_id');"
                        type="submit"
                        class="$dmg_light_checked damage_light_checked damage_box"
                        value=" "
                    />
                    <h2>$hit_location</h2>
                </div> <!-- hit_box_detail -->
                <p><b>H</b>eavy Injury: Knocked Down</p>
            </div> <!-- survivor_hit_box -->

    \n""")
    survivor_sheet_attrib_controls_top = '\t<div class="survivor_sheet_attrib_controls">'
    survivor_sheet_attrib_controls_token = Template("""\n

    <!-- $long_name attribute controls start here! -->

    <div id="$long_name_controls_container"
        ng-app="kdmManager"
        ng-controller="attributeController"
        ng-init="base_value=$base_value;gear_value=$gear_value;tokens_value=$tokens_value;survivor_id='$survivor_id'"
    >


        <!-- $long_name modal window controls first; token buttons next -->

        <div id="$controls_id" class="survivor_sheet_attrib_controls_modal survivor_sheet_gradient" style="display: none;">
            <span
                class="close_attrib_controls_modal"
                onClick="showHide('$controls_id')"
            >
                X
            </span>

            <h3 class="$token_class">$long_name</h3>
            <div class="synthetic_attrib_total synthetic_attrib_total_$long_name">{{ getTotal() }}</div>
            <hr/>

            <div class="survivor_sheet_attrib_controls_number_container_container">


              <!-- $long_name BASE container starts -->

              <div class="survivor_sheet_attrib_controls_number_container">

                <button
                    class="incrementer"
                    onClick="increment('base_value_$controls_id')"
                    ng-click="refresh('$long_name', 'base')"
                >
                    +
                </button>

                <input
                    id="base_value_$controls_id"
                    type="number"
                    class="survivor_sheet_attrib_controls_number"
                    ng-model="base_value"
                    value="{{raw_base}}"
                    onClick="this.select()"
                    ng-change="refresh('$long_name', 'base')"
                    />

                <button
                    class="decrementer"
                    onClick="decrement('base_value_$controls_id')"
                    ng-click="refresh('$long_name', 'base')"
                >
                    -
                </button>

                <p><b>Base</b></p>

              </div> <!-- survivor_sheet_attrib_controls_number_container -->

        <!-- end of BASE; start of GEAR -->


              <div class="survivor_sheet_attrib_controls_number_container">
              <button
                  class="incrementer"
                  onClick="increment('gear_value_$controls_id')"
                  ng-click="refresh('$long_name', 'gear')"
              >
                  +
              </button>
                 <input
                    id="gear_value_$controls_id"
                    type="number"
                    class="survivor_sheet_attrib_controls_number"
                    ng-model="gear_value"
                    value="{{raw_gear}}"
                    onClick="this.select()"
                    ng-change="refresh('$long_name', 'gear')"
                    />
              <button
                  class="decrementer"
                  onClick="decrement('gear_value_$controls_id')"
                  ng-click="refresh('$long_name', 'gear')"
              >
                  -
              </button>
              <p>Gear</p>
              </div> <!-- survivor_sheet_attrib_controls_number_container -->


        <!-- end $long_name GEAR; begin TOKENS -->

              <div class="survivor_sheet_attrib_controls_number_container">
                <button
                    class="incrementer"
                    onClick="increment('tokens_value_$controls_id')"
                    ng-click="refresh('$long_name', 'tokens')"
                >
                    +
                </button>
                  <input
                      id="tokens_value_$controls_id"
                      class="survivor_sheet_attrib_controls_number"
                      type="number"
                      value="{{raw_tokens}}"
                      onClick="this.select()"
                      ng-model="tokens_value"
                      ng-change="refresh('$long_name', 'tokens')"
                  />
                <button
                    class="decrementer"
                    onClick="decrement('tokens_value_$controls_id')"
                    ng-click="refresh('$long_name', 'tokens')"
                >
                    -
                </button>
                <p>Tokens</p>
              </div> <!-- survivor_sheet_attrib_controls_number_container -->

            </div><!-- survivor_sheet_attrib_controls_number_container_container -->

        </div> <!-- survivor_sheet_attrib_controls_modal -->


        <!-- $long_name token button -->
        <button
            class="survivor_sheet_attrib_controls_token $token_class"
            onClick="showHide('$controls_id')"
        >
        <p class="short_name">$short_name</p>
        <p class="attrib_value synthetic_attrib_total_$long_name">{{ getTotal() }}</p>
        </button>

    </div> <!-- $long_name_controls_container -->
    """)
    survivor_sheet_attrib_controls_bot = '\t</div> <!-- survivor_sheet_attrib_controls -->'

    partner_controls_top = '\n<hr/>\n\t<p><span class="tiny_break">&nbsp;</span>Partner<select name="partner_id" onchange="this.form.submit()">\n'
    partner_controls_none = '<option selected disabled>Select a Survivor</option>'
    partner_controls_opt = Template('<option value="$value" $selected>$name</option>')
    partner_controls_bot = '</select><span class="tiny_break"/>&nbsp;</span></p>\n\n'
    expansion_attrib_controls = Template("""\n
    <hr/>
    <span class="tiny_break"/>&nbsp;</span>
    <input type="hidden" name="expansion_attribs" value="None"/> <!-- Hacks -->
    <input type="hidden" name="expansion_attribs" value="None"/> <!-- Hacks -->
    $control_items
    <br class="clear_both"/>
    <span class="tiny_break"/>&nbsp;</span>
    \n""")
    expansion_attrib_item = Template("""\n
    <div class="expansion_attrib_toggle">
     <input onchange="this.form.submit()" type="checkbox" id="$item_id" class="expansion_attrib_toggle" name="expansion_attribs" value="$key" $checked/>
     <label class="expansion_attrib_toggle" for="$item_id">$key</label>
    </div> <!-- expansion_attrib_toggle -->
    \n""")
    returning_survivor_badge = Template("""\n\
    <div class="returning_survivor_badge $color_class" title="$div_title">$flag_letter</div>
    \n""")
    survivor_constellation_badge = Template("""\n\
    <div class="survivor_constellation_badge" title="Survivor Constellation">$value</div>
    \n""")
    affinity_controls = Template("""\n\
    <p>
    <button id="modalAffinityButton" class="$button_class" title="Permanent Affinity controls"> $text </button>
    </p>
    \n""")
    affinity_span = Template("""\n
    <span id="affinity_span" class="affinity_$span_class">$value</span>
    \n""")
    stat_story_event_stub = Template("""\n
               <font class="kdm_font">g</font> <b>$event</b> (p.$page) occurs at $attrib_value<br/>
    """)
    clickable_avatar_upload = Template("""\n

    <label id="survivor_sheet_avatar" for="avatar_file_input">
        <img class="survivor_avatar_image $img_class" src="$img_src" alt="$alt_text"/>
    </label>

    <input onchange='document.getElementById("avatar_change_form").submit()' id="avatar_file_input" class="hidden" type="file" name="survivor_avatar" accept="image/*" form="avatar_change_form">
    \n""")
    constellation_table_top = '<table id="survivor_constellation_table">'
    constellation_table_row_top = Template("""
        <tr><th colspan="6">&nbsp</th></tr>
        <tr>
         <th>&nbsp</th>
         <th class="$witch_class">Witch</th>
         <th class="$rust_class">Rust</th>
         <th class="$storm_class">Storm</th>
         <th class="$reaper_class">Reaper</th>
         <th>&nbsp</th>
        </tr>
    \n""")
    constellation_table_row = Template("""
        <tr>
         <th>$th</th>
          $cells
         <th>&nbsp</th>
        </tr>
    \n""")
    constellation_table_cell = Template("""
        <td class="$td_class">$value</td>
    \n""")
    constellation_table_bot = '<tr><th colspan="6">&nbsp</th></tr></table>\n\n'
    constellation_table_select_top = Template("""\n
    <br/>
    <div id="survivor_constellation_control_container">
    <form method="POST" action="/" >
        <input type="hidden" name="modify" value="survivor">
        <input type="hidden" name="asset_id" value="$survivor_id">
        <select name="set_constellation" onchange="this.form.submit()">
            <option selected disabled hidden>Set Constellation</option>
            $options
    """)
    constellation_table_select_option = Template('<option $selected>$value</option>')
    constellation_table_select_bot = Template("""\n
        </select>
<!--        <button class="orange bold">Set constellation!</button> -->
    </form>

    <form method="POST" action="/">
        <input type="hidden" name="modify" value="survivor">
        <input type="hidden" name="asset_id" value="$survivor_id">
        <input type="hidden" name="set_constellation" value="UNSET">
        <button onclick="this.form.submit()">Unset constellation</button>
    </form>
    </div> <!-- survivor_constellation_control_container" -->
    \n""")
    survival_action_item = Template('\
        <font class="survivor_sheet_survival_action_item $f_class">$action</font><br/>\
    \n')
    epithet_angular_controls = Template("""\n
    <div id="epithet_angular" ng-app="kdmManager" ng-controller="epithetController" ng-init="epithets=[$current_epithets]" title="Survivor epithets. Use controls below to add. Click or tap to remove!">

        <ul id="epithet_angular_ul">
            <li class="touch_me" ng-repeat="x in epithets" ng-click="removeItem($index,'$survivor_id')" style="background-color: #{{x.bgcolor}}; color: #{{x.color}}; border-color: #{{x.bgcolor}}">
                <span ng-if='x.name == undefined'>{{x}}</span>
                <span ng-if='x.name'>{{x.name}}</span>
            </li>
        </ul>

    $epithet_options
<!--    <button ng-click="addItem()">Add</button> -->

    <!-- suppress error text if not debugging -->
    <!-- <p>{{errortext}}</p> -->
    </div>
    \n""")
    survivor_notes = Template("""\n
    <div id="survivor_notes_angular" ng-app="kdmManager" ng-controller="survivorNotesController" ng-init="notes=$note_strings_list" title="Survivor notes. Use controls below to add. Click or tap to remove!">

        <ul class="survivor_sheet_survivor_note">
            <li class="survivor_sheet_survivor_note touch_me" ng-repeat="x in notes" ng-click="removeNote($index,'$survivor_id')">
                {{x}}
            </li>
        </ul>

    <input class="survivor_sheet_add_survivor_note" ng-model="note" placeholder="Add a Survivor Note" onClick="this.select()"/>
    <button class="survival_limit_style survivor_sheet_add_survivor_note" ng-click="addNote('$survivor_id')">Add Note</button>
    <br/>

    <!-- suppress error text if not debugging -->
    <!-- <p>{{errortext}}</p> -->
    </div>
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
        <div class="new_settlement_asset">
            <input id="$a_id" class="radio_principle" type="checkbox" name="%s" value="$var_value" />
            <label for="$a_id" class="radio_principle_label">$var_value </label>
            $subtitle
        </div>
        \n""" % asset_dict_name)


        output = ""

        if asset_dict_name == "expansions":
            for e_key in sorted(game_assets.expansions.keys()):
                exp_dict = game_assets.expansions[e_key]
                sub = ""
                if "subtitle" in exp_dict.keys():
                    sub= '<p class="new_settlement_asset">%s</p>' % exp_dict["subtitle"]
                output += slug.safe_substitute(a_id=e_key.lower().replace(" ","_"), var_value=e_key, subtitle=sub)
        elif asset_dict_name == "survivors":
            # special custom box for prologue survivors (calls
            #   assets.Settlement.first_story() after creation
            output = """
                <input type="checkbox" id="create_prologue_survivors" class="radio_principle" name="create_prologue_survivors" value="True" />
                <label class="radio_principle_label" for="create_prologue_survivors"> Create Four "First Story" Survivors</label><br/>
            """
            for s_name in sorted(game_assets.survivors.keys()):
                s_key = s_name.lower().replace(" ","_")
                s_dict = game_assets.survivors[s_name]
                output += slug.safe_substitute(a_id=s_key, var_value=s_name, subtitle="")

        return output

    new = """\n\
    <span class="tablet_and_desktop nav_bar settlement_sheet_gradient"></span>
    <span class="nav_bar_mobile mobile_only settlement_sheet_gradient"></span>
    <span class="top_nav_spacer mobile_only"> hidden </span>

    <br />

    <div id="create_new_asset_form_container">
        <form action="#" method="POST">
        <input type="hidden" name="new" value="settlement" />
        <input type="text" id="new_asset_name" name="settlement_name" placeholder="New Settlement Name"/ class="full_width" autofocus>
        <h3 class="new_asset">Campaign:</h3>
        <p class="new_asset">
        Choosing an expansion campaign automatically enables expansion content required by that campaign and modifies the settlement timeline, milestones, principles, rules and Survivor Sheets. A settlement's campaign may <b>not</b> be changed after settlement creation!<br/><br/>
            %s
        </p>
        <h3 class="new_asset">Expansions:</h3>
        <p class="new_asset">
        Enable expansion content by toggling items below. Expansion content may also be enabled (or disabled) later using the controls on the Settlement Sheet.<br/>
        <input type="hidden" name="expansions" value="None"/> <!-- Both of these are necessary -->
        <input type="hidden" name="expansions" value="None"/> <!-- Hack City! -->
            %s
        </p>
        <h3 class="new_asset">Survivors:</h3>
        <p class="new_asset">
        By default, new settlements are created with no survivors. Toggle options below to create the settlement with pre-made survivors. <br/><br/>
            <input type="hidden" name="survivors" value="None"/> <!-- Both of these are necessary -->
            <input type="hidden" name="survivors" value="None"/> <!-- Hack City! -->
            %s<br/>
        </p>
        <hr class="new_asset" />
        <button class="success">Create!</button>
        <br/><br/><br/>
        </form>
    </div> <!-- create_new_asset_form_container -->
    \n""" % (render_campaign_toggles(), render_checkboxes("expansions"), render_checkboxes("survivors"))

    return_hunting_party_with_confirmation = Template("""\n\
        <form action="#" method="POST" onsubmit="return confirm('Press OK to return all Departing Survivors, heal all wounds, remove all armor points, attribute tokens and gear modifiers, increment Hunt XP +1 and add the current quarry to the Defeated Monsters list as well as the settlement timeline for this year.');">
            <input type="hidden" name="return_hunting_party" value="$settlement_id"/>
            <button id="return_hunting_party" class="bold yellow" >&#8629; Return Departing Survivors</button>
        </form>
    \n""")
    return_hunting_party = Template("""\n\
        <form action="#" method="POST">
            <input type="hidden" name="return_hunting_party" value="$settlement_id"/>
            <button id="return_hunting_party" class="bold gradient_orange" >&#8629; Return Departing Survivors</button>
        </form>
    \n""")
    current_quarry_select = Template("""\n\
    <br class="clear_both"/>
    <h3>Current Quarry:</h3>
    <form action="#" method="POST">
        <input type="hidden" name="modify" value="settlement"/>
        <input type="hidden" name="asset_id" value="$settlement_id"/>
        <select class="hunting_party_current_quarry" name="current_quarry" onchange="this.form.submit()">
          <option>None</option>
            $options
        </select>
    </form>
    <br class="clear_both mobile_only" />
    <hr/>
    \n""")
    hunting_party_macros = Template("""\n\
    <br class="mobile_only">
    <hr class="mobile_only">
    <button class="orange bold" id="departingSurvivorsModal">Manage Departing Survivors</button>
    <hr class="mobile_only">

    <div
        id="departingSurvivorsModalContent" class="modal"
        ng-init="registerModalDiv('departingSurvivorsModal','departingSurvivorsModalContent')"
    >
     <div class="modal-content">
     <span class="closeModal" onclick="closeModal('departingSurvivorsModalContent')">x</span>

      <div class="hunting_party_macro" style="border-left: 0 none;">
        <form action="#" method="POST">
            <input type="hidden" name="modify" value="settlement"/>
            <input type="hidden" name="asset_id" value="$settlement_id"/>
            <input type="hidden" name="hunting_party_operation" value="survival"/>
            Survival
            <button name="operation" value="increment">+1</button>
            <button name="operation" value="decrement">-1</button>
        </form>
      </div>
      <div class="hunting_party_macro">
        <form action="#" method="POST">
            <input type="hidden" name="modify" value="settlement"/>
            <input type="hidden" name="asset_id" value="$settlement_id"/>
            <input type="hidden" name="hunting_party_operation" value="Brain Event Damage"/>
            Brain Event Damage
            <button name="operation" value="increment">+1</button>
        </form>
      </div>
        <hr class="invisible mobile_only"/>
      <div class="hunting_party_macro">
        <form action="#" method="POST">
            <input type="hidden" name="modify" value="settlement"/>
            <input type="hidden" name="asset_id" value="$settlement_id"/>
            <input type="hidden" name="hunting_party_operation" value="Insanity"/>
            Insanity
            <button name="operation" value="increment">+1</button>
            <button name="operation" value="decrement">-1</button>
        </form>
      </div>
      <div class="hunting_party_macro">
        <form action="#" method="POST">
            <input type="hidden" name="modify" value="settlement"/>
            <input type="hidden" name="asset_id" value="$settlement_id"/>
            <input type="hidden" class="clear_both" name="hunting_party_operation" value="Courage"/>
            Courage
            <button name="operation" value="increment">+1</button>
            <button name="operation" value="decrement">-1</button>
        </form>
      </div>
        <hr class="invisible mobile_only"/>
      <div class="hunting_party_macro">
        <form action="#" method="POST">
            <input type="hidden" name="modify" value="settlement"/>
            <input type="hidden" name="asset_id" value="$settlement_id"/>
            <input type="hidden" name="hunting_party_operation" value="Understanding"/>
            Understanding
            <button name="operation" value="increment">+1</button>
            <button name="operation" value="decrement">-1</button>
        </form>
      </div>
    <!-- departingSurvivorsModalContent continues... -->

    \n""")
    hunting_party_macros_footer = "\t</div><!-- modal-content -->\n  </div> <!-- departingSurvivorsModalContent -->\n"
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
    <form action="#" method="POST">
     <input type="hidden" name="export_campaign" value="$export_type"/>
     <input type="hidden" name="asset_id" value="$asset_id"/>
     <button class="yellow"> $export_pretty_name </button>
    </form>
    \n""")
    event_log = Template("""\n\
        <span class="tablet_and_desktop nav_bar settlement_sheet_gradient"></span>
        <span class="nav_bar_mobile mobile_only" settlement_sheet_gradient></span>
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
        <div id="floating_event_log_anchor" class="settlement_sheet_gradient" ><a href="#event_log"><img src="%s/icons/settlement_event.png"/></a></div>
        <div id="floating_genealogy_anchor" class="settlement_sheet_gradient" ><a href="#genealogy"><img src="%s/icons/genealogy.png"/></a></div>
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
        <span class="tablet_and_desktop nav_bar campaign_summary_gradient"></span>
        <span class="nav_bar_mobile mobile_only campaign_summary_gradient"></span>
        <span class="top_nav_spacer mobile_only"> hidden </span>

        <h1 class="settlement_name"> %s $settlement_name</h1>
        <div id="campaign_summary_campaign_type">$campaign</div>

        <div id="campaign_summary_pop">
            <p>Population: $population ($sex_count); $death_count deaths</p>
            <hr class="mobile_only"/>
            <p>LY: $lantern_year, Survival Limit: $survival_limit</p>
            <hr class="mobile_only"/>
        </div>


        <a id="edit_hunting_party" class="mobile_only"></a>
        <span class="vertical_spacer desktop_only"></span>

        $survivors

        <hr class="mobile_only invisible">
        <br class="mobile_only">

        <div id="campaign_summary_facts_box">

            $special_rules

            <a id="endeavors">
                <hr class="mobile_only">
            </a>
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
    \n""" % dashboard.campaign_flash)
    form = Template("""\n\
    <span class="tablet_and_desktop nav_bar settlement_sheet_gradient"></span>
    <span class="nav_bar_mobile mobile_only settlement_sheet_gradient"></span>
    <span class="top_nav_spacer mobile_only"> hidden </span>

    <br class="tablet_and_desktop"/>

    <div id="asset_management_left_pane">

        <form method="POST" id="autoForm" action="#">
            <button id="save_button" class="success">Save</button>
            <input type="hidden" name="modify" value="settlement" />
            <input type="hidden" name="asset_id" value="$settlement_id" />

            <p id="campaign_type" class="center" title="Campaign type may not be changed after a settlement is created!">$campaign</p>

            <input id="topline_name" onchange="this.form.submit()" class="full_width" type="text" name="name" value="$name" placeholder="Settlement Name"/>
            $abandoned
            <hr class="mobile_only"/>
            <br class="tablet_and_desktop">

            <div class="settlement_form_wide_box">
                <div class="big_number_container left_margin">
                    <button class="incrementer mobile_and_tablet" onclick="increment('survivalLimitBox');">+</button>
                    <input id="survivalLimitBox" class="big_number_square" type="number" name="survival_limit" value="$survival_limit" min="$min_survival_limit"/>
                    <button class="decrementer mobile_and_tablet" onclick="decrement('survivalLimitBox');">-</button>
                </div>
                <div class="big_number_caption">Survival Limit<br />(min: $min_survival_limit)</div>
            </div>
            <br class="mobile_only"/>
            <hr class="mobile_only"/>

            <div class="settlement_form_wide_box">
                <div class="big_number_container left_margin">
                    <button class="incrementer mobile_and_tablet" onclick="increment('populationBox');">+</button>
                    <input id="populationBox" class="big_number_square" type="number" name="population" value="$population" min="0"/>
                    <button class="decrementer mobile_and_tablet" onclick="decrement('populationBox');">-</button>
                </div>
                <div class="big_number_caption">Population</div>
            </div> <!-- settlement_form_wide_box -->

            <br class="mobile_only"/><hr class="mobile_only"/>

            <div class="settlement_form_wide_box">
                <div class="big_number_container left_margin">
                    <button class="incrementer mobile_and_tablet" onclick="increment('deathCountBox');">+</button>
                    <input id="deathCountBox" class="big_number_square" type="number" name="death_count" value="$death_count" min="0"/>
                    <button class="decrementer mobile_and_tablet" onclick="decrement('deathCountBox');">-</button>
                </div>
                <div class="big_number_caption">Death Count</div>
            </div> <!-- settlement_form_wide_box -->
        </form> <!-- ending the first form -->

            <hr />

        <h3>Bulk Add New Survivors</h3>
        <form action="#" method="POST">
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

            <input type="submit" id="settlement_sheet_create_new_survivors" class="survival_limit_style" value="Create New Survivors" />
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

        <hr class="tablet_only timeline_insulator" >

        <div id="asset_management_right_pane">

                    <!-- TIMELINE: HAS ITS OWN FORM  -->
        <a id="edit_timeline" class="mobile_only"><br/><br/><br/></a>
        <h2 class="clickable timeline_show_hide" onclick="showHide('timelineBlock')">LY $lantern_year - View Timeline <img class="dashboard_down_arrow" src="http://media.kdm-manager.com/icons/down_arrow_white.png"/> </h2>
        <div id="timelineBlock" class="block_group timeline_block_group collapsing_block_group" style="display: $display_timeline;">
         <div class="big_number_container left_margin">
            <br>
             <button class="incrementer" onclick="increment('lanternYearBox');">+</button>

            <form id="autoForm" method="POST" action="#edit_timeline">
            <input type="hidden" name="modify" value="settlement" />
            <input type="hidden" name="asset_id" value="$settlement_id" />
            <input id="lanternYearBox" onchange="this.form.submit()" class="big_number_square" type="number" name="lantern_year" value="$lantern_year" min="0"/>
            </form>
             <button class="decrementer" onclick="decrement('lanternYearBox');">-</button>
         </div>
         <div class="big_number_caption""><br>Lantern Year</div>
        <p id="timeline_tooltip">Tap or click a Lantern Year number below to mark it complete (and end it).</p>
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

            <input onchange="this.form.submit()" class="big_number_square" type="number" name="lost_settlements" value="$lost_settlements" min="0"/>
            <h3>Lost Settlements</h3>
            <p>Refer to <font class="kdm_font">g</font> <b>Game Over</b> on p.179: <b>Left Overs</b> occurs at 4; <b>Those Before Us</b> occurs at 8; <b>Ocular Parasites</b> occurs at 12; <b>Rainy Season</b> occurs at 16.</p>
            </form>
        </div>

        <br>
        <hr/>
        <h3>Expansions</h3>
        <a id="edit_expansions" class="mobile_only"></a>
        <p>Toggle expansion content on/off using these controls. Adding
        or removing content will automatically update drop-down menus, timeline
        and survivor controls. </p>
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

        <form action="#" method="POST" onsubmit="return confirm('This will prevent this settlement from appearing on any user Dashboard, including yours. Press OK to Abandon this settlement forever.');">
            <input type="hidden" name="modify" value="settlement" />
            <input type="hidden" name="asset_id" value="$settlement_id" />
            <input type="hidden" name="abandon_settlement" value="toggle" />

            <h3>Abandon Settlement</h3>
            <p>Mark a settlement as "Abandoned" to prevent it from showing up in your active campaigns without removing it from the system.</p>
            <button class="full_width warn"> Abandon Settlement! </button>
        </form>

    $remove_settlement_button

    </div> <!-- right pane -->


    <!-- MODAL CONTENT ONLY BELOW THIS POINT -->

    <div
        id="modalStorage" class="modal"
        ng-init="registerModalDiv('modalStorageButton','modalStorage')"
    >

      <!-- Modal content -->
        <div class="modal-content">
            <span class="closeModal" onclick="closeModal('modalStorage')">×</span>

                <!-- ADD TO STORAGE - THIS IS ITS OWN FORM-->
            <form id="autoForm" method="POST" action="#edit_storage">
                <input type="hidden" name="modify" value="settlement" />
                <input type="hidden" name="asset_id" value="$settlement_id" />

                 <div class="big_number_container">
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


    \n""")
    remove_settlement_button = Template("""\
    <hr/>
    <h3>Permanently Remove Settlement</h3>
    <form action="#" method="POST" onsubmit="return confirm('Press OK to permanently delete this settlement AND ALL SURVIVORS WHO BELONG TO THIS SETTLEMENT forever. Please note that this CANNOT BE UNDONE and is not the same as marking a settlement Abandoned. Consider abandoning old settlements rather than removing them, as this allows data about the settlement to be used in general kdm-manager stats.');"><input type="hidden" name="remove_settlement" value="$settlement_id"/><button class="full_width error">Permanently Delete Settlement</button></form>
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
    <p class="$p_class">
    &nbsp; $cost $name$punc $desc $type
    </p>
    """)


class login:
    """ The HTML for form-based authentication goes here."""
    form = """\n\
    <div id="sign_in_container">
        <img src="%s/tree_logo_shadow.png" class="sign_in tablet_and_desktop"/>
        <h2 class="seo">KD:M Manager!</h2>
        <h1 class="seo">An interactive campaign manager for <a href="http://kingdomdeath.com/" target="top">Kingdom Death: <i>Monster</i></a>.</h1>
        <div id="sign_in_last_updated">%s</div>
        <div id="sign_in_controls">
            <form action="#" method="POST">
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
            <form action="#" method="POST">
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
            <form action="#" method="POST">
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
            <form method="POST" action="#" >
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
    start_head = '<!DOCTYPE html>\n<html ng-app="kdmManager" ng-controller="globalController">\n<head>\n<meta charset="UTF-8">\n<meta name="theme-color" content="#000000">\n<title>%s</title>\n<link rel="stylesheet" type="text/css" href="/style.css">\n' % settings.get("application","title")
    close_body = '\n </div><!-- container -->\n</body>\n</html>'
    saved_dialog = '\n    <div id="saved_dialog" class="success">Saved!</div>'
    mobile_hr = '<hr class="mobile_only"/>'
    dashboard_alert = Template("""\n\
    <div id="dashboard_alert_spacer"></div>
    <div class="dashboard_alert maroon">
    $msg
    </div>
    \n""")

    burger_top_level_button = Template("""\n
    <form method="POST" action="/"><input type="hidden" name="change_view" value="$view"/>
    <button class="sidenav_top_level"> $link_text </button>
    </form>
    \n""")
    burger_signout_button = Template("""\n
    <form id="logout" method="POST" action="/">
    <input type="hidden" name="remove_session" value="$session_id"/>
    <input type="hidden" name="login" value="$login"/>
    <button>SIGN OUT</button>
    </form>
    \n""")
    burger_change_view_button = Template("""\n
    <form method="POST" action="/">
    <input type="hidden" name="$target_view" value="$settlement_id" />
    <button class="sidenav_button">$link_text</button>
    </form>
    \n""")
    burger_export_button = Template("""\n
    <form method="POST" action="/">
     <input type="hidden" name="export_campaign" value="XLS"/>
     <input type="hidden" name="asset_id" value="$settlement_id"/>
     <button class="sidenav_button"> $link_text </button>
    </form>
    \n""")

    burger_anchors_campaign_summary = """\n
    <a href="#edit_hunting_party" onclick="closeNav()">Survivors</a>
    <a href="#endeavors" onclick="closeNav()">Endeavors</a>
    <a href="#principles" onclick="closeNav()">Principles</a>
    <a href="#innovations" onclick="closeNav()">Innovations</a>
    \n"""
    report_error_button = """<button id="reportErrorButton" onclick="closeNav()">Report an Issue or Error</button>"""
    report_error_div = """\n
    <div
        id="modalReportError" class="modal"
        ng-init="registerModalDiv('reportErrorButton','modalReportError')"
    >
        <div class="modal-content">
            <span class="closeModal" onclick="closeModal('modalReportError')">×</span>
            <div id="report_error_container">
                <h3>Report an Issue or Error</h3>
                <p>http://kdm-manager.com is a work in progress and is under active development!</p>
                <p>If you identify an issue, error or problem with the application, whether a simple typo, a presentation problem or otherwise, there are a number of ways to report it.</p>
                <p>To rapidly submit an issue via email, use the form below:
                <div id="error_form">
                    <form method="POST" action="/">
                     <input type="hidden" name="error_report" value="from_web">
                     <textarea id="report_error" name="body" placeholder="Describe your issue here"></textarea>
                     <input type="submit" class="error" value ="submit"/>
                    </form>
                </div>
                </p>
                <p><b>General Comments/Questions:</b> use <a href="http://kdm-manager.blogspot.com//" target="top">the Development blog at blog.kdm-manager.com</a> to review change logs, make comments and ask questions about the manager.</p>
                <p><b>Source code and development questions:</b> if you're interested, you can clone/download and review the <a href="https://github.com/toconnell/kdm-manager" target="top">source code for the manager</a> from GitHub. <a href="https://github.com/toconnell/kdm-manager/wiki" target="top">The development wiki</a> also has some good stuff.<p>
                <p><b>Issues and Errors:</b> feel free to mention any issues/errors on the blog comments or, if you use GitHub, you may also submit issues to <a href="https://github.com/toconnell/kdm-manager/issues" target="top">the project's issues tracker</a>.</p>
            </div>
        </div><!-- modal-content -->
    </div> <!-- modalReportError -->

    \n"""
    error_report_email = Template("""\n\
    Greetings!<br/><br/>&ensp;User $user_email [$user_id] has submitted an error report!<br/><br/>The report goes as follows:<hr/>$body<hr/>&ensp;...and that's it. Good luck!<br/><br/>Your friend,<br/>&ensp; meta.error_report_email
    \n""")
    safari_warning = Template("""\n\
    <div id="safari_warning">
    It looks like you're using Safari $vers. Unfortunately, the current version
    of this application uses some JavaScript elements that are not fully
    supported by your browser.
    If you experience disruptive presentation and functionality issues while
    using the manager, <a href="https://www.google.com/chrome/browser" target="top">Chrome</a> is fully supported on Windows and OSX.
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

def render_burger(session_object=None):
    """ This renders hamburger ('side nav') menu and controls based on the
    'view' kwarg value.

    Returns "" (i.e. an empty string) if the view is not dashboard
    """

    # first, handle all situations in which we don't return a burger button or
    #   even write the menu
    no_burger_string = "\n<!-- no burger in this view! -->\n\n"
    if session_object is None:
        return no_burger_string
    elif session_object.session is None:
        return no_burger_string
    elif session_object.Settlement is None:
        return no_burger_string
    elif not hasattr(session_object.Settlement, "settlement"):
        return no_burger_string
    elif session_object.Settlement.settlement is None:
        return no_burger_string

    view = session_object.session["current_view"]
    if view not in ["event_log","view_campaign","view_settlement","view_survivor","new_survivor","new_settlement"]:
        return "\n<!-- no burger in '%s' view -->\n\n" % view

    # now, create a burger.
    # first, set defaults:

    signout_button = meta.burger_signout_button.safe_substitute(
        session_id=session_object.session["_id"],
        login=session_object.User.user["login"],
    )

    new_settlement = meta.burger_top_level_button.safe_substitute(
        link_text = "+ New Settlement",
        view = "new_settlement",
    )
    if view == "new_settlement":
        new_settlement = ""

    # this isn't working. gotta troubleshoot later.
    anchors = ""
#    if view == "view_campaign":
#        anchors = meta.burger_anchors_campaign_summary

    # create a list of action buttons based on view/session info
    actions = ""
    if view != "new_survivor":
        actions += meta.burger_change_view_button.safe_substitute(
            link_text = "+ Create New Survivor",
            target_view = "change_view",
            settlement_id = "new_survivor"
        )
    if view in ["view_campaign","event_log","view_survivor","new_survivor","new_settlement"]:
        if session_object.User.user["login"] in session_object.Settlement.get_admins():
            actions += meta.burger_change_view_button.safe_substitute(
                link_text = "Settlement Sheet",
                target_view = "view_settlement",
                settlement_id = session_object.session["current_settlement"],
            )
    if view in ["view_settlement","event_log","view_survivor","new_survivor","new_settlement"]:
        actions += meta.burger_change_view_button.safe_substitute(
            link_text = "Campaign Summary",
            target_view = "view_campaign",
            settlement_id = session_object.session["current_settlement"]
        )
    actions += meta.burger_change_view_button.safe_substitute(
        link_text = "Settlement Event Log",
        target_view = "change_view",
        settlement_id = "event_log"
    )
    actions += meta.burger_export_button.safe_substitute(
        link_text = "Export to XLS",
        settlement_id = session_object.session["current_settlement"],
    )

    # now add quick links to departing survivors for admins
    departing = ""
    hunting_party = []
    if session_object.User.user["login"] in session_object.Settlement.get_admins():
        hunting_party = session_object.Settlement.get_survivors(return_type="hunting_party")
        if hunting_party != []:
            departing = "<h3>Departing Survivors:</h3>"
            for h in hunting_party:
                if h["_id"] == session_object.session["current_asset"]:
                    pass
                else:
                    departing += meta.burger_change_view_button.safe_substitute(
                        link_text = "%s (%s)" % (h["name"],h["sex"]),
                        target_view = "view_survivor",
                        settlement_id = h["_id"],
                    )

    # now add favorites
    favorites = ""
    favorite_survivors = session_object.User.get_favorites(scope="current_settlement")
    if favorite_survivors != []:
        favorites = "<h3>Favorites:</h3>"
        for f in favorite_survivors:
            if f["_id"] == session_object.session["current_asset"]:
                pass
            elif f in hunting_party:
                pass
            else:
                favorites += meta.burger_change_view_button.safe_substitute(
                    link_text = "%s (%s)" % (f["name"],f["sex"]),
                    target_view = "view_survivor",
                    settlement_id = f["_id"],
                )
    if favorites == "<h3>Favorites:</h3>":
        favorites = ""


    burger_panel = Template("""\n
        <!-- $current_view burger -->

        <div id="mySidenav" class="sidenav">
          $dash
          $new_settlement_button
            <hr/>
            <h3>$settlement_name:</h3>
              $action_map
              $departing_links
              $favorite_links
<!--            <H3>Navigation:</h3> -->
              $anchor_map
            <hr/>
          $report_error
          $signout
        </div>

        <button id="floating_dashboard_button" class="gradient_silver" onclick="openNav()">
            &#9776;
        </button>

        <!-- end $current_view burger -->
    """)

    output = burger_panel.safe_substitute(
        settlement_name=session_object.Settlement.settlement["name"],
        current_view=view,
        dash=meta.burger_top_level_button.safe_substitute(
            link_text = "Return to Dashboard",
            view = "dashboard",
        ),
        new_settlement_button = new_settlement,
        report_error=meta.report_error_button,
        signout=signout_button,
        anchor_map=anchors,
        action_map=actions,
        departing_links=departing,
        favorite_links=favorites,
    )

    output += meta.report_error_div

    return output



def render(view_html, head=[], http_headers=None, body_class=None, session_object=None):
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

    <!-- angular app -->
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.5.4/angular.min.js"></script>
    <script src="http://code.angularjs.org/1.5.3/angular-route.min.js"></script> 
    <script src="/kdm-manager.js"></script>

    <!-- auto-save stuff -->
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
        function toggleDamage(elem_id, asset_id) {
            document.getElementById(elem_id).classList.toggle("damage_box_checked");

            var toggle_key = document.getElementById(elem_id);

        var http = new XMLHttpRequest();
        http.open("POST", "/", true);
        http.setRequestHeader("Content-type","application/x-www-form-urlencoded");
        var params =  toggle_key.name + "=checked" + "&modify=survivor" +"&asset_id=" + asset_id + "&norefresh=True";
        http.send(params);

        $('#saved_dialog').show();
        $('#saved_dialog').fadeOut(1500)

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


    #
    # now close the head elements and start writing the body, preparing to print
    #   it to stdout (i.e. render it as a response
    #

    output += '</head>\n<body class="%s">\n' % body_class

    output += render_burger(session_object) # burger goes before container

    output += '<div id="container" onclick="closeNav()" ng-controller="containerController" ng-init="init()">\n'

    output += view_html

    output += meta.close_body

    print(output.encode('utf8'))

    sys.exit(0)     # this seems redundant, but it's necessary in case we want
                    #   to call a render() in the middle of a load, e.g. to just
                    #   finish whatever we're doing and show a page.
