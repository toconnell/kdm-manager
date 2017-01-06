# coding=utf-8
#!/usr/bin/env python

#   standard
import Cookie
from datetime import datetime, timedelta
from string import Template
import sys

#   custom
import admin
import api
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

    <div class="admin_panel_left">
        <table class="panel_meta_stats">
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

        $response_times
    </div> <!-- admin_panel_left -->

    <div class="admin_panel_right">
        <h3 class="admin_panel_label">Killboard</h3>
        $killboard
        $world_daemon
    </div>

    <hr class="invisible"/><br/><h1>Recent User Activity</h1>

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
    <select
        class="$select_class"
        name="$operation$name"
        ng_model="$ng_model"
        ng_change="$ng_change"
        onchange="this.form.submit()"
    >
      <option selected disabled hidden value="">$operation_pretty $name_pretty</option>
    """)
    game_asset_select_row = Template('\t  <option value="$asset">$asset</option>\n')
    game_asset_select_bot = '    </select>\n'
    text_input = Template('\t  <input onchange="this.form.submit()" type="text" class="full_width" name="$name" placeholder="$placeholder_text"/>')



class dashboard:
    # settlement administrivia; needs to be above the dashboard accordions
    panel_button = '<form action="#" method="POST"><input type="hidden" name="change_view" value="panel"/><button class="dashboard_admin_panel_launch_button kd_blue tablet_and_desktop">Admin Panel!</button></form>\n'
    new_settlement_button = '<form method="POST" action="#"><input type="hidden" name="change_view" value="new_settlement" /><button class="kd_blue">+ New Settlement</button></form>\n'

    # flash
    down_arrow_flash = '<img class="dashboard_down_arrow" src="%s/icons/down_arrow.png"/> ' % settings.get("application", "STATIC_URL")
    campaign_flash = '<img class="dashboard_icon" src="%s/icons/campaign.png"/> ' % settings.get("application", "STATIC_URL")
    settlement_flash = '<img class="dashboard_icon" src="%s/icons/settlement.png"/> ' % settings.get("application", "STATIC_URL")
    system_flash = '<img class="dashboard_icon" src="%s/icons/system.png"/> ' % settings.get("application", "STATIC_URL")
    refresh_flash = '<img class="dashboard_icon" src="%s/icons/refresh.png"/> ' % settings.get("application", "STATIC_URL")

    # dashboard accordions
    about = Template("""\n
    <div class="dashboard_menu">
    <h2 class="clickable about_primary" onclick="showHide('about_div')"> <font class="kdm_font dashboard_kdm_font">g</font> About %s</h2>
        <div id="about_div" style="display: none;" class="dashboard_accordion about_secondary">
        <p class="title"><b>KD:M Manager! Version $version.</b></p><hr/>
        <p>About:</p>
        <ul>
            <li>This application, which is called <i>kdm-manager.com</i>, or, more simply, <i>the Manager</i>, is an interactive campaign management tool for use with <i><a href="https://shop.kingdomdeath.com/collections/sold-out/products/kingdom-death-monster" target="top">Monster</a></i>, by <a href="http://kingdomdeath.com" target="top">Kingdom Death</a>.</li>
        </ul>
        <p>Important Information:</p>
        <ul>
            <li><b>This application is not developed, maintained, authorized or in any other way supported by or affiliated with <a href="http://kingdomdeath.com" target="top">Kingdom Death</a>.</b></li>
            <li>This application is currently under active development and is running in debug mode!<li>
            <li>Among other things, this means not only that <i>errors can and will occur</i>, but also that <i>features may be added and removed without notice</i> and <i>presentation elements are subject to change</i>.</li>
            <li>Users' email addresses and other information are used only for the purposes of developing and maintaining this application and are never shared, published or distributed.</li>
        </ul>
        <hr/>
        <p>Release Information:</p>
        <ul>
            <li>v$version of the Manager went into production on $latest_change_date. <a target="top" href="$latest_change_link">View change log</a>.</li>
            <li>v1.7.0, the first production release of the Manager, went live on 2015-11-29.</li>
            <li>For detailed release information, including complete notes and updates for each production release, please check the development blog at <a href="http://blog.kdm-manager.com" target="top"/>blog.kdm-manager.com</a>.</li>
        </ul>
        <hr/>
        <p>Development and Support:</p>
        <ul>
            <li>Please report issues and errors using the side navigation panel within the application: this feature sends an email containing pertinent data directly to the application maintainers.</li>
            <li>Application source code is <a href="https://github.com/toconnell/kdm-manager" target="top">available on GitHub</a>.</li>
            <li>Github users may prefer to <a href="https://github.com/toconnell/kdm-manager/issues" target="top">report issues there</a>.</li>
            <li>Check <a href="https://github.com/toconnell/kdm-manager/wiki" target="top">the development wiki</a> for complete information about the project.</li>
        </ul>
        <hr/>
        <p>Credits:</p>
        <ul>
            <li>Produced, provisioned and supported by <a href="http://thelaborinvain.com">The Labor in Vain</a>.<li>
            <li>Developed, maintained and edited by <a href="http://toconnell.info">Timothy O'Connell</a>.</li>
            <li>Icon font ('kdm-font-10') by <a href="http://steamcommunity.com/id/GeorgianBalloon" target="top">Miracle Worker</a>.</li>
            <li>The <font style="font-family: Silverado; font-size: 1.3em;">Silverado Medium Condensed</font> font is licensed through <a href="https://www.myfonts.com/" target="top">MyFonts.com</a>.
            <li>Loading "spinner" gifs by <a href="http://loading.io" target="top">loading.io</a></li>
        </ul>

        </div> <!-- about_div -->
    </div>
    \n""" % (down_arrow_flash))
    preference_header = Template("""\n
    <div class="dashboard_preference_block_group">
        <h2>$title</h2>
    \n""")
    preference_footer = "</div> <!-- dashboard_preference_block_group $title--> "
    preference_block = Template("""\n
    <p class="preference_description">$desc</p>

    <div class="dashboard_preference_elections_container">
        <input
            id="pref_true_$pref_key"
            class="kd_css_checkbox kd_radio_option"
            name="$pref_key"
            style="display: none"
            type="radio"
            value="True"
            $pref_true_checked
            onchange="updateUserPreference(this);"
        />
        <label for="pref_true_$pref_key">
            $affirmative
        </label>

        <input
            id="pref_false_$pref_key"
            class="kd_css_checkbox kd_radio_option"
            name="$pref_key"
            style="display: none"
            type="radio"
            value="False"
            $pref_false_checked
            onchange="updateUserPreference(this);"
        />
        <label for="pref_false_$pref_key">
            $negative
        </label>
    </div> <!-- dashboar_preference_elections_container -->

    \n""")

    #
    #   DASHBOARD MOTD follows. this is the whole dashboard, basically.
    #

    motd = Template("""\n

	<img class="dashboard_bg" src="%s/tree_logo_shadow.png">

    <div class="dashboard_menu">
        <h2 class="clickable system_primary" onclick="showHide('system_div')"> <img class="dashboard_icon" src="%s/icons/system.png"/> System %s</h2>
        <div id="system_div" style="display: none;" class="dashboard_accordion system_secondary">

        <div class="dashboard_preferences">
            <p>Use the controls below to update application-wide preferences.
            These settings will affect all of your settlements and survivors!</p>

            $user_preferences

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
        <div style="font-family: Metrophobic">
            <p class="currently_signed_in_as">Currently signed in as: <i>$login</i> (last sign in: $last_sign_in)</p>
            $last_log_msg

            <div class="dashboard_preferences">
                <form action="#" method="POST">
                    <input type="hidden" name="change_password" value="True"/>
                    <input type="password" name="password" class="full_width" placeholder="password">
                    <input type="password" name="password_again" class="full_width" placeholder="password (again)"/>
                    <button class="kd_alert_no_exclaim red_glow"> Change Password</button>
                </form>
            </div>
        </div>

    </div>
    """ % (settings.get("application","STATIC_URL"), settings.get("application", "STATIC_URL"), down_arrow_flash))
    campaign_summary = Template("""\n\
    <div class="dashboard_menu">
        <h2 class="clickable campaign_summary_gradient" onclick="showHide('campaign_div')"> <img class="dashboard_icon" src="%s/icons/campaign.png"/> Campaigns %s </h2>
        <div id="campaign_div" style="display: $display" class="dashboard_accordion campaign_summary_gradient">
        <p class="panel_top_tooltip">Games you are currently playing.</p>
        <hr class="invisible">
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
        <h2
            class="clickable world_primary"
            onclick="showHide('world_div')"
        >
            <font class="kdm_font_hit_locations dashboard_kdm_font">g</font> World <img class="dashboard_down_arrow" src="/media/icons/down_arrow_white.png"/>
        </h2>
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
    """)

    # misc html assets

    refresh_button = """\n
    <form method="POST" action="/">
        <button
            id="floating_refresh_button"
            class="touch_me"
            onclick="showFullPageLoader()"
        >
            %s
        </button>
    </form>
    """ % refresh_flash

    view_asset_button = Template("""\n\
    <form method="POST" action="#">
    <input type="hidden" name="view_$asset_type" value="$asset_id" />
    <button id="$button_id" class="$button_class $disabled" $disabled>$asset_name <span class="tablet_and_desktop">$desktop_text</span></button>
    </form>
    \n""")



class angularJS:
    """ HTML here should only be angularJS applications. They need to be strings
    and they may not be python templates or do any other kind of variable
    expansion or anything like that. """


    expansions_manager = """\n
    <div
        id="modalExpansionsManager" class="modal"
        ng-init="registerModalDiv('bulkExpansionsManagerButton','modalExpansionsManager');"
        ng-controller="updateExpansionsController"
    >

      <!-- Modal content -->
        <div class="full_size_modal_panel timeline_gradient">
            <span class="closeModal" onclick="closeModal('modalExpansionsManager')">×</span>

            <h3>Expansions!</h3>

            <div class="expansions_controls_container">
                <p>Use the controls below to determine which expansion content is
                enabled for this campaign. Remember to save when finished!</p>

                <form method="POST" action="#">
                    <div class="expansion_content_line_item" ng-repeat="x in new_settlement_assets.expansions">
                        <input
                            id="{{x.handle}}_modal_toggle"
                            name="{{x.handle}}"
                            type="checkbox"
                            class="kd_css_checkbox kd_radio_option"
                            ng-model=incomingExpansion
                            ng-checked="arrayContains(x.handle, settlement_sheet.expansions)"
                            ng-click="toggleExpansion(x.handle)"
                        >
                        <label for="{{x.handle}}_modal_toggle">{{x.name}}</label>
                    </div> <!-- line_item -->

                    <button type="submit" class="kd_blue save_expansions">Save Changes and Reload</button>
                </form>
            </div> <!-- container -->
        </div> <!-- modal content -->
    </div> <!-- parent modal -->
    """

    bulk_add_survivors = """\n
    <div
        id="modalBulkAdd" class="modal"
        ng-init="registerModalDiv('bulkAddOpenerButton','modalBulkAdd');"
    >

      <!-- Modal content -->
        <div class="full_size_modal_panel survivor_sheet_gradient">
            <span class="closeModal" onclick="closeModal('modalBulkAdd')">×</span>

            <h3>Add Multiple New Survivors</h3>
            <p>Use these controls to add multiple new survivors to {{settlement_sheet.name}}.
            New survivors will be named randomly or 'Anonymous' according to user preference.</p>

            <div
                class="create_user_asset_block_group bulk_add_block_group"
            >
                <div class="bulk_add_control">
                    <form method="POST" action="#">
                        <input type="hidden" name="modify" value="settlement" />
                        <input type="hidden" name="asset_id" value="{{settlement_sheet._id.$oid}}" />
                        <input type="hidden" name="bulk_add_survivors" value="True" />

                        Male

                        <button
                            type="button"
                            class="incrementer"
                            onclick="increment('maleCountBox');"
                        >
                            &#9652;
                        </button>
                        <input
                            id="maleCountBox"
                            class="big_number_square"
                            type="number"
                            name="male_survivors"
                            value="0"
                            min="0"
                        />
                        <button
                            type="button"
                            class="decrementer"
                            onclick="decrement('maleCountBox');"
                        >
                        &#9662;
                        </button>
                </div>  <!-- bulk_add_control maleCountBox" -->
                <div class="bulk_add_control">

                    Female

                    <button
                        type="button"
                        class="incrementer"
                        onclick="increment('femaleCountBox');"
                    >
                        &#9652;
                    </button>
                    <input
                        id="femaleCountBox"
                        class="big_number_square"
                        type="number"
                        name="female_survivors"
                        value="0"
                        min="0"
                    />
                    <button
                        type="button"
                        class="decrementer"
                        onclick="decrement('femaleCountBox');"
                    >
                        &#9662;
                    </button>
                </div>

                <hr class="invisible"/>

                <input
                    type="submit"
                    id="bulkAddSurvivors"
                    class="kd_blue settlement_sheet_bulk_add" value="Create New Survivors"
                />

                </form>


            </div> <!-- bulk_add_survivors -->

        </div> <!-- mondal content -->
    </div> <!-- modal parent -->

    \n"""

    settlement_notes = """\n\
    <div
        class="modal"
        id="settlementNotesContainer"
        ng-controller="settlementNotesController"
        ng-init="registerModalDiv('settlementNotesOpenerButton','settlementNotesContainer');"
    >

        <div class="full_size_modal_panel campaign_summary_gradient">

            <span class="closeModal" onclick="closeModal('settlementNotesContainer')">×</span>

            <h3>Campaign Notes</h3>
            <p>All players in the {{settlement_sheet.name}} campaign may make
            notes and comments here. Tap or click notes to remove them.</p>

            <div class="settlement_notes_application_container">

                <div class="settlement_notes_note_container">

                    <div class="settlement_notes_controls">
                        <input ng-model="newNote" onclick="this.select()" class="add_settlement_note">
                        <button ng-click="addNote()" class="kd_blue add_settlement_note">+</button>
                    </div> <!-- settlement_notes_controls -->

                    <div
                        class="settlement_note"
                        ng-repeat="n in settlement_notes"
                    >
                        <div class="note_flair">
                            <font
                                ng-if="userRole(n.author) == 'settlement_admin'"
                                class="kdm_font_hit_locations"
                            > <span class="flair_text">a</span> </font>
                            <font
                                ng-if="userRole(n.author) == 'player'"
                                class="kdm_font_hit_locations"
                            > <span class="flair_text">b</span> </font>
                        </div>

                        <div class="note_content" ng-click="showHide(n.js_id);window.alert(n.js_id)">
                            {{n.note}} <span class="author" ng-if="n.author != user_login"> {{n.author}}</span>
                        </div>
                        <span
                            id="{{n.js_id}}"
                            class="kd_alert_no_exclaim note_remove hidden"
                            ng-if="n.author == user_login || user_is_settlement_admin"
                            ng-click="removeNote($index, n.js_id)
                        ">
                            &times;
                        </span>

                    </div><!-- settlement_note -->

                </div> <!-- settlement_notes_note_container -->


            </div> <!-- settlement_notes_application_container -->

            <div
                ng-if="arrayContains(user_login, settlement_sheet.admins) == true"
                ng-controller="playerManagementController"
            >
                <hr/>
                <h3>Manage Players</h3>
                    <p>Add other registered users to the {{settlement_sheet.name}}
                    campaign by adding their email addresses to the Survivor Sheets
                    of survivors in this campaign. </p>

                    <table class="player_management">
                        <tr>
                            <th colspan="2">Login</th>
                            <th>Admin</th>
                        </tr>
                        <tr
                            class="player_management_row"
                            ng-repeat="p in settlement.user_assets.players"
                        >
                            <td class="flair" ng-if="arrayContains(p.login, settlement_sheet.admins) == true">
                                <span class="player_management_flair kdm_font_hit_locations">a</span>
                            </td>
                            <td class="flair" ng-if="arrayContains(p.login, settlement_sheet.admins) == false">
                                <span class="player_management_flair kdm_font_hit_locations">b</span>
                            </td>

                            <td class="login">
                                {{p.login}}
                                <span ng-if="p._id.$oid == settlement_sheet.created_by.$oid">
                                    (Founder)
                                </span>
                            </td>

                            <td class="admin">
                                <input
                                    type="checkbox"
                                    class="player_management_admin"
                                    ng-if="p._id.$oid != settlement_sheet.created_by.$oid"
                                    ng-model="playerIsAdmin"
                                    ng-checked="arrayContains(p.login, settlement_sheet.admins) == true"
                                    ng-click="toggleAdmin(p.login)"
                                />
                            </td>
                        </tr>
                    </table>

                <hr/>
                <form action="/">
                    <center>
                        <button class="kd_blue" type="submit">Save Changes and Reload!</button>
                    </center>
                </form>
            </div> <!-- ng-if div -->
        </div><!-- full size modal panel -->

    </div> <!-- modal (parent) -->
    \n"""

    new_survivor = """\n\
    <div
        class="modal"
        id="modalNewSurvivorContainer"
        ng-controller="newSurvivorController"
        ng-init="registerModalDiv('newSurvivorButton','modalNewSurvivorContainer');"
    >

        <div class="full_size_modal_panel survivor_sheet_gradient">

            <h3>New Survivor!</h3>

            <span class="closeModal" onclick="closeModal('modalNewSurvivorContainer')">×</span>

            <form method="POST" action="#" enctype="multipart/form-data">
            <input type="hidden" name="new" value="survivor" />

            <div class="create_user_asset_block_group">

            <input
                ng-model="new_survivor_name"
                class="new_asset_name"
                type="text"
                name="name"
                placeholder="New Survivor Name"
                autofocus
                >
            </div>


            <div
                class="create_user_asset_block_group"
            >

                <h2 class="new_asset">Survivor Sex</h2>

                <input
                    id="maleInput"
                    class="kd_css_checkbox kd_radio_option"
                    type="radio"
                    name="sex"
                    value="M"
                    checked
                >
                <label
                    id="survivorSexMaleElection"
                    for="maleInput"
                >
                    Male
                </label>

                <input
                    id="femaleInput"
                    class="kd_css_checkbox kd_radio_option"
                    type="radio"
                    name="sex"
                    value="F"
                >
                <label
                    id="survivorSexFealeElection"
                    for="femaleInput"
                >
                    Female
                </label>

            </div>

            <div class="create_user_asset_block_group">
                <h2 class="no_ul">Survivor Avatar Image</h2>
                <p>Upload an image to represent this survivor (optional).</p>
                <br/>
                <input type="file" class="new_survivor_avatar" name="survivor_avatar" accept="image/*">
            </div>


            <div
                class="create_user_asset_block_group"
                ng-if="
                    settlement_sheet.lantern_year >= 1 &&
                    settlement.game_assets.eligible_parents.male.length >= 1 &&
                    settlement.game_assets.eligible_parents.female.length >= 1
                "
            >
                <h2 class="no_ul">Survivor Parents</h2>
                <p class="new_asset">Survivors without parents are not eligible
                for the automatic application of Innovation bonuses granted only
                to newborn survivors!</p>

                <div class="parent_selectors">
                    <select
                        name="father"
                        ng-model="newSurvivorFather"
                        ng-options="survivor._id.$oid as survivor.name for survivor in settlement.game_assets.eligible_parents.male"
                    /><option selected disabled value="" name="father">Father</option></select>

                    <select
                        name="mother"
                        ng-model="newSurvivorMother"
                        ng-options="survivor._id.$oid as survivor.name for survivor in settlement.game_assets.eligible_parents.female"
                    /><option selected disabled value="" name="mother">Mother</option></select>
                </div>


            </div> <!-- ancestors -->


            <div class="create_user_asset_block_group">

                <h2 class="no_ul">Access Permissions</h2>

                <p>Use the controls below to determine who is the owner of the
                survivor and whether other players may edit the survivor.</p>

                <input
                    type="email"
                    name="email"
                    placeholder="Survivor Email"
                    value="{{user_login}}"
                    onclick="this.select()"
                >

                <input
                    id="publicInput"
                    type="checkbox"
                    class="kd_css_checkbox kd_radio_option"
                    name="toggle_public"
                >
                 <label
                     id="survivorPublic"
                     for="publicInput"
                 >
                     Public - anyone may manage this survivor
                </label>

            </div> <!-- survivor perms -->

            <br />
    
            <button class="kd_blue add_new_survivor">Add {{new_survivor_name}}</button>

            <br/><br/>

            </form>

        </div><!-- full size modal panel -->

    </div> <!-- modal (parent) -->
    \n"""

    timeline = """\n

    <div
        class="modal"
        id="modalTimelineContainer"
        ng-controller="timelineController"
        ng_init="registerModalDiv('timelineOpenerButton','modalTimelineContainer');"
    >

        <span class="touch_me timeline_overlay_current_ly">LY: <b>{{current_ly}}</b></span>

        <div class="full_size_modal_panel timeline_gradient">

            <span class="closeModal" onclick="closeModal('modalTimelineContainer')">×</span>

            <h3>{{ settlement_sheet.name}} Timeline</h3>

            <p ng-if="user_is_settlement_admin">
                Click or tap on any Lantern Year below to update events occuring during that year.
            </p>
            <p ng-if="user_is_settlement_admin == false">
                The Timeline of story, settlement and showdown events for {{settlement_sheet.name}}. Only settlement admins may modify the timeline.
            </p>

            <div class="timeline_ly_headline">
                <span>Year</span><span>Story & Special Events</span>
            </div>

            <div
                ng-repeat="t in timeline"
                ng-init="t.log_div_id = 'ly' + t.year + 'LogDivIDHandle'"
                class="timeline_whole_entry_container"
            >
                <div class="timeline_ly_container" ng-click="showHideControls(t.year)">
                    <div class="timeline_bullet_and_year_container">
                        <span ng-if="t.year >= current_ly" class="kd_toggle_bullet"></span>
                        <span ng-if="t.year < current_ly" class="kd_toggle_bullet checked_kd_toggle_bullet"></span>
                        <span class="timeline_ly_number">{{t.year}}</span>
                    </div>

                    <div class="timeline_events_container">
                        <span class="timeline_event" ng-repeat="e in t.story_event" ng-model="story_events">
                            <font class="kdm_font">g &nbsp;</font>
                            <b>{{e.name}}</b>
                            <span class="timeline_event_page" ng-if="e.page">
                                &nbsp;(p.{{e.page}})
                            </span>
                        </span>
                        <span class="timeline_event" ng-repeat="q in t.special_showdown">
                        <span><img class="icon special_showdown" src="/media/icons/special_showdown_event.jpg"/></span>
                            <font class="maroon_text"><b>{{q.name}}</b></font>
                        </span>
                        <span class="timeline_event" ng-repeat="q in t.showdown_event">
                            <font class="kdm_font">f &nbsp;</font>
                            {{q.name}}
                        </span>
                        <span class="timeline_event" ng-repeat="n in t.nemesis_encounter">
                        <span><img class="icon" src="/media/icons/nemesis_encounter_event.jpg"/></span>
                            &nbsp; <b> {{n.name}}</b>
                        </span>
                        <span class="timeline_event" ng-repeat="e in t.settlement_event">
                            <font class="kdm_font_hit_locations">a &nbsp;</font>
                            {{e.name}}
                        </span>
                    </div>
                </div>


                <div
                    id="timelineControlsLY{{t.year}}"
                    style="display: none; height: 0;"
                    class="timeline_hidden_controls_container"
                    ng-if="user_is_settlement_admin == true;"
                >

                    <select
                        name="add_timeline_event"
                        class="add_timeline_event"
                        ng-model="newEvent"
                        ng-options="se.handle as se.name for se in story_events"
                        ng-change="addEvent(t.year,'story_event',newEvent)"
                    >
                        <option selected disabled value="">
                            Add Story Event
                        </option>
                    </select>

                    <br/>

                    <select
                        name="add_timeline_event"
                        class="add_timeline_event"
                        ng-model="newEvent"
                        ng-options="s for s in settlement.game_assets.special_showdown_options"
                        ng-change="addEvent(t.year,'special_showdown',newEvent)"
                    >
                        <option selected disabled value="">
                            Add Special Showdown
                        </option>
                    </select>

                    <br/>

                    <select
                        name="add_timeline_event"
                        class="add_timeline_event"
                        ng-model="newEvent"
                        ng-options="s for s in settlement.game_assets.showdown_options"
                        ng-change="addEvent(t.year,'showdown_event',newEvent)"
                    >
                        <option selected disabled value="">
                            Add Showdown
                        </option>
                    </select>

                    <br/>

                    <select
                        name="add_timeline_event"
                        class="add_timeline_event"
                        ng-model="newEvent"
                        ng-options="n for n in settlement.game_assets.nemesis_encounters"
                        ng-change="addEvent(t.year,'nemesis_encounter',newEvent)"
                    >
                        <option selected disabled value="">
                            Add Nemesis Encounter
                        </option>
                    </select>

                    <br/>

                    <select
                        name="add_settlement_event"
                        class="add_timeline_event"
                        ng-model="newEvent"
                        ng-options="se.handle as se.name for se in settlement_events"
                        ng-change="addEvent(t.year,'settlement_event',newEvent)"
                    >
                        <option selected disabled value="">
                            Add Settlement Event
                        </option>
                   </select>

                    <hr class="invisible"/>

                    <div ng-repeat="event_group in t" class="timeline_rm_controls">
                        <span ng-if="isObject(event_group)" class="timeline_rm_event_group">
                            <div
                                ng-click="rmEvent(t.year, e)"
                                ng-repeat="e in event_group"
                                class="kd_alert_no_exclaim rm_timeline_event"
                            > <b>x</b> {{e.name}}
                            </div>
                        </span>
                    </div>

                    <hr class="invisible"/>

                    <div class="end_current_ly" ng-if="t.year==current_ly">
                        <input
                            type="checkbox"
                            id="endLanternYear{{t.year}}"
                            ng-model="lantern_year"
                            ng-change="setLY(t.year + 1); showHidecontrols(t.year); showControls(t.year+1)"
                        />
                        <label
                            class="kd_blue timeline_change_ly_button"
                            for="endLanternYear{{t.year}}"
                        >
                            End Lantern Year {{t.year}}
                        </label>
                        <input
                            type="checkbox"
                            id="returnToLanternYear{{t.year - 1}}"
                            ng-model="lantern_year"
                            ng-change="setLY(t.year - 1); showHideControls(t.year); showControls(t.year-1)"
                        />
                        <label
                            class="kd_blue timeline_change_ly_button"
                            for="returnToLanternYear{{t.year - 1}}"
                            ng-if="t.year >= 1"
                        >
                            Return to Lantern Year {{t.year - 1}}
                        </label>
                    </div> <!-- end_current_ly -->

                </div> <!-- timelineControlsLy{{t.year}}-->

                <div
                    ng-if="t.year <= current_ly && get_event_log(t.year).length >= 1 "
                    ng-click="showHide(t.log_div_id)"
                    class="timeline_event_log_revealer round_top"
                >
                    LY {{t.year}} Event Log &#9662;
                </div>

                <div
                    class="timeline_event_log_container hidden"
                    id="{{t.log_div_id}}"
                    ng-click="showHide(t.log_div_id)"
                >
                    <span
                        ng-repeat="l in get_event_log(t.year)"
                    >
                        <div
                            ng-class-odd="'log_zebra'"
                            ng-class-even="'log_no_zebra'"
                            ng-bind-html="l.event|trustedHTML"
                        >
                        </div>
                   </span>

                    <div class="timeline_event_log_bottom round_bottom" > </div>
                    <br/>
                </div>

            </div> <!-- iterator ng-repeat t in timeline -->


        </div><!-- full size modal  -->

    </div> <!-- modal (parent) -->

    \n"""


class survivor:
    no_survivors_error = '<!-- No Survivors Found! --> <div class="kd_alert user_asset_sheet_error">This settlement has no survivors in it! Use the navigation menu controls in the upper left to add new survivors.</div>'


    add_ancestor_top = """\n
    <div
        class="create_user_asset_block_group"
        title="Add survivor parents."
    >

        <br/>
        <br/>
    \n"""
    add_ancestor_select_top = Template('\t<select name="$parent_role">\n\t<option selected disabled hidden value="">$pretty_role</option>')
    change_ancestor_select_top = Template('\t<select onchange="this.form.submit()" name="$parent_role">\n\t<option selected disabled hidden value="">$pretty_role</option>')
    add_ancestor_select_row = Template('\t<option value="$parent_id">$parent_name</option>\n')
    change_ancestor_select_row = Template('\t<option value="$parent_id" $selected>$parent_name</option>\n')
    add_ancestor_select_bot = '\t</select><br class="mobile_only"/><br class="mobile_only"/>'
    add_ancestor_bot = '    </div> <!-- create_user_asset_block_group parents -->\n\n'
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
            <button
                onclick="showFullPageLoader()"
                class="add_survivor_to_party orange $able_to_hunt $disabled"
                $able_to_hunt
                $disabled
            >
                ::
            </button>
        </form>

        <form method="POST" action="#">
         <input type="hidden" name="view_survivor" value="$survivor_id" />
         <button id="survivor_campaign_asset" class="$b_class $disabled" $disabled>
            $returning
            $constellation
            $avatar
            <center> <font class="$favorite"/>&#9733;</font> <b class="campaign_summary_survivor_name">$name</b> [$sex] </center>
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

    <!-- survivor sheet JS goes here !-->
    <script>
    window.onload=function(){
        var fa_disabled = document.getElementById('survivor_sheet_cannot_use_fighting_arts');
        if (fa_disabled.checked == true) {
           $('.survivor_sheet_fighting_art').addClass('strikethrough');
        };
    }
    </script>
    <!-- survivor sheet JS -->


    <script src="/media/survivorSheet.js"></script>

   <div
       id = "survivor_sheet_angularjs_controller_container"
       ng-init="
            initialize('survivorSheet', '$user_id', '$user_login', '$api_url','$settlement_id');
            loadSurvivor('$survivor_id');
       "
   >
        <span class="tablet_and_desktop nav_bar survivor_sheet_gradient"></span>
        <span class="mobile_only nav_bar_mobile survivor_sheet_gradient"></span>
        <div class="top_nav_spacer">hidden</div>


        <div id="asset_management_left_pane">

            <input
                id="survivor_sheet_survivor_name"
                type="text" name="name" value="{{survivor.name}}"
                placeholder="Survivor Name"
                onchange="updateAssetAttrib(this, 'survivor', '$survivor_id')"
                onClick="this.select()"
            />

            <hr class="invisible"/>

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

                <div class="survivor_sheet_dynamic_button_holder">

                    <button
                        id="cursedControlsModal"
                        class="orange bold modal_opener"
                    >
                        Cursed Items ({{survivor.cursed_items.length}})
                    </button>

                    <button
                        id="saviorControlsModal"
                        class="orange bold modal_opener"
                        ng-if="settlement.game_assets.campaign.saviors != undefined"
                        ng-init="registerModalDiv('saviorControlsModal','modalSavior')"
                    >
                        Savior
                    </button>

                    <button
                        id="dragonControlsModal"
                        class="orange bold modal_opener"
                        ng-if="settlement.game_assets.campaign.dragon_traits != undefined"
                        ng-init="registerModalDiv('dragonControlsModal','modalConstellation')"
                    >
                        Dragon Traits ({{survivor.constellation_traits.length}})
                    </button>

                </div>

            </p>

            <br/>

        <div class="survivor_dead_retired_container">

            <input
                id="favorite"
                class="kd_css_checkbox"
                type="checkbox"
                name="toggle_favorite"
                value="checked"
                $favorite_checked
                onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
            />
            <label
                class="toggle_favorite"
                for="favorite"
            >
                Favorite
            </label>

            <input
                id="retired"
                class="kd_css_checkbox"
                type="checkbox"
                name="toggle_retired"
                value="checked"
                $retired_checked
                onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
            >
            <label
                for="retired"
                style="float: right; clear: none;"
            >
                Retired &nbsp;
            </label>

            <button
                id="modalDeathButton"
                class="$death_button_class modal_death_button"
                title="Mark this survivor as dead"
            >
                Dead
            </button>

            </div> <!-- survivor_dead_retired_container -->


            <hr />


            <div id="survivor_survival_box_container">

                <div class="big_number_container left_margin">
                    <button
                        class="incrementer"
                        onclick="increment('survivalBox'); updateAssetAttrib('survivalBox','survivor','$survivor_id');"
                    >
                        &#9652;
                    </button>
                    <input
                        id="survivalBox"
                        class="big_number_square"
                        type="number"
                        name="survival" value="$survival"
                        min="0"
                        max="$survival_max"
                        onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
                    />
                    <button
                        class="decrementer"
                        onclick="decrement('survivalBox'); updateAssetAttrib('survivalBox','survivor','$survivor_id');"
                    >
                        &#9662;
                    </button>
                </div> <!-- big_number_container -->

                <div class="big_number_caption">
                    Survival <p>(max: $survival_limit)</p>
                </div>

            </div> <!-- survivor_survival_box_container -->


            <hr />


            <div id="survivor_survival_actions_container">

                <h3>Survival Actions</h3>

                <p class="survival_actions_container">
                     <input
                        id="cannot_spend_survival"
                        class="survivor_sheet_toggle"
                        name="toggle_cannot_spend_survival"
                        onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
                        type="checkbox"
                        value="checked" $cannot_spend_survival_checked
                     />

                     <label
                        id="cannot_spend_survival"
                        class="float_right_toggle"
                        for="cannot_spend_survival">
                            Cannot<br/>spend<br/>survival
                     </label>

                    $survival_actions

                </p>

                <div id="wideButtonHolder" class="survivor_sheet_dynamic_button_holder desktop_only">
                    <!-- This holds optional survivor modal openers; otherwise, it's empty -->
                </div>


                $desktop_avatar_img


            </div> <!-- survivor_survival_actions_container -->


            <a id="edit_attribs">
                <hr>
            </a>

            <h3>Bonuses</h3>
            <div class="survivor_sheet_survivor_settlement_bonuses">
                $settlement_buffs
            </div>
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

            <!-- HUNT XP -->

            <div class="survivor_sheet_secondary_attrib_container">
                <div class="big_number_container">
                    <button
                        class="incrementer"
                        onclick="stepAndSave('up','huntXPBox','survivor','$survivor_id');"
                    >
                        +
                    </button>
                    <input
                        id="huntXPBox"
                        name="hunt_xp"
                        class="big_number_square"
                        type="number"
                        value="$hunt_xp"
                        min="0"
                        onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
                    />
                    <button
                        class="decrementer"
                        onclick="stepAndSave('down','huntXPBox','survivor','$survivor_id');"
                    >
                        -
                    </button>
                </div> <!-- big_number_container -->

                <div class="survivor_sheet_secondary_attribute_caption">
                    <div class="big_number_caption">Hunt XP</div>
                    <p>
                        <font class="kdm_font">g</font> <b>Age</b> occurs at 2, 6, 10 and 15. $name retires at 16.
                    </p>
                </div>

            </div> <!-- survivor_sheet_secondary_attrib_container -->

            <hr class="mobile_only"/>

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

                <div class="survivor_sheet_secondary_attribute_caption">
                    <div class="big_number_caption">Weapon Proficiency</div>
                    <form method="POST" action="#edit_wpn_prof">
                        <input type="hidden" name="modify" value="survivor" />
                        <input type="hidden" name="asset_id" value="$survivor_id" />
                        $weapon_proficiency_options
                    </form>
                    <p>
                        <b>Specialist</b> at 3<br/><b>Master</b> at 8.
                    </p>
                </div>

            </div> <!-- survivor_sheet_secondary_attrib_container -->

            <hr class="mobile_only"/>

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

                <div class="survivor_sheet_secondary_attribute_caption">
                    <div class="big_number_caption">Courage</div>
                     <p>
                        $hunt_xp_3_event
                        <font class="kdm_font">g</font> <b>See the Truth</b> (p.155) occurs at 9.
                    </p>
                </div>

            </div> <!-- survivor_sheet_secondary_attrib_container -->

            <hr class="mobile_only"/>

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

                    <div class="survivor_sheet_secondary_attribute_caption">
                        <div class="big_number_caption">Understanding</div>
                        <p>
                            $courage_3_event
                            <font class="kdm_font">g</font> <b>White Secret</b> (p.169) occurs at 9.
                        </p>
                    </div>

            </div> <!-- survivor_sheet_secondary_attrib_container -->


        </div> <!-- asset_management_middle_pane -->




                <!-- RIGHT ASSET MANAGEMENT PANE STARTS HERE -->

        <a id="edit_misc_attribs" class="mobile_and_tablet"> </a>
        <hr class="no_desktop" />

        <div id="survivor_sheet_right_pane">

        <!-- EXPANSION ATTRIBUTES ; PARTNER CONTROLS -->

        <div
            class="sotf_reroll_controls"
            ng-if="arrayContains('Survival of the Fittest', settlement_sheet.principles)"
            ng-controller="sotfRerollController"
        >

        <input
            id="sotfRerollCheckbox"
            type="checkbox"
            class="kd_css_checkbox kd_radio_option"
            ng-model="sotf_reroll_toggle"
            ng-checked="survivor.sotf_reroll == true"
            ng-click="sotfToggle()"
        />
        <label
            for="sotfRerollCheckbox"
        >
        Once per lifetime reroll
        <p class="sotf_reroll_caption">
            <b>Survival of the fittest:</b> Once per lifetime, a survivor may
            reroll a single roll result. They must keep this result.</b>
        </p>
        </label>

        </div> <!-- sotf reroll -->


        $expansion_attrib_controls

        <form method="POST" action="#edit_misc_attribs">
            <button class="hidden"></button>
            <input type="hidden" name="modify" value="survivor" />
            <input type="hidden" name="asset_id" value="$survivor_id" />
            $partner_controls
        </form>


        <!-- FIGHTING ARTS -->

        <a id="edit_fighting_arts" class="mobile_and_tablet"></a>



        <h3>Fighting Arts</h3>

        <input
            id="survivor_sheet_cannot_use_fighting_arts"
            class="survivor_sheet_toggle"
            name="toggle_cannot_use_fighting_arts"
            onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
            type="checkbox"
            value="checked" $cannot_use_fighting_arts_checked
        />
        <label
            id="survivor_sheet_cannot_use_fighting_arts_label"
            class="float_right_toggle"
            for="survivor_sheet_cannot_use_fighting_arts"
         >
            Cannot use<br/>Fighting Arts
        </label>

        <p>Maximum 3.</p>

        <div class="survivor_sheet_card_container">
            $fighting_arts
        </div>

        <form method="POST" action="#edit_fighting_arts">
            <input type="hidden" name="form_id" value="survivor_edit_fighting_arts" />
            <input type="hidden" name="modify" value="survivor" />
            <input type="hidden" name="asset_id" value="$survivor_id" />

            <button class="hidden"></button> <!-- hacks! -->
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

            <div class="survivor_sheet_card_container">
                $disorders
            </div>
            $add_disorders<br class="mobile_only"/>
            $rm_disorders

        </form>


        <a id="edit_abilities" class="mobile_only"></a>
        <hr />


        <!-- ABILITIES AND IMPAIRMENTS -->


        <h3>Abilities & Impairments</h3>
        <input
            id="skip_next_hunt"
            name="toggle_skip_next_hunt"
            type="checkbox"
            class="survivor_sheet_toggle"
            value="checked"
            $skip_next_hunt_checked
            onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
        />
        <label
            class="float_right_toggle"
            for="skip_next_hunt"
            id="skip_next_hunt_label"
        >
            Skip Next<br/>
            Hunt
        </label>

        <form method="POST" action="#edit_abilities" class="abilities_and_impairments">
            <input type="hidden" name="form_id" value="survivor_edit_abilities" />
            <input type="hidden" name="modify" value="survivor" />
            <input type="hidden" name="asset_id" value="$survivor_id" />

            $abilities_and_impairments

            $add_abilities_and_impairments

            <button
                id="modalCustomAIButton"
                class="orange bold"
                title="Add custom Abilities & Impairments"
            >
                + Custom Abilities & Impairments
            </button>

            $rm_abilities_and_impairments

        </form>

        <hr/>

        <a id="edit_lineage" class="mobile_and_tablet"></a>

        <div class="survivor_sheet_right_pane_blocks_container">

            <div class="survivor_sheet_block_group">
                <h2>Lineage</h2>
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
            </div> <!-- survivor_sheet_block_group lineage -->

            <div class="survivor_sheet_block_group">
                <h2>Permissions</h2>
                <h4>Owner</h4>
                    <input
                        id="survivorOwnerEmail"
                        class="survivor_owner_email"
                        onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
                        onclick="this.select()"
                        type="email"
                        name="email"
                        placeholder="email"
                        value="$email"
                    />

                <p>Enter another registered user's email address here to make
                them a player in this campaign.</p>

                <h4>Access</h4>
                <p>Toggle this checkbox on or off to allow any player in this
                campaign to manage this survivor.</p>

                  <input
                    onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
                    type="checkbox"
                    id="public"
                    class="kd_css_checkbox kd_radio_option"
                    name="toggle_public"
                    value="checked"
                    $public_checked
                  >
                  <label
                    class="public_survivor_toggle"
                    for="public"
                  >
                    Anyone May Manage this Survivor &nbsp;
                  </label>

                  <br/>
            </div> <!-- survivor_sheet_block_group perms -->


        </div> <!-- survivor_sheet_right_pane_blocks -->


        $remove_survivor_controls

        <div class="survivor_sheet_bottom_attrib_spacer">&nbsp;</div>

        <!-- gotta put this here, outside of the other forms -->
        <form id="avatar_change_form" method="POST" enctype="multipart/form-data" action="#">
            <input type="hidden" name="modify" value="survivor" />
            <input type="hidden" name="asset_id" value="$survivor_id" />
        </form>

    </div> <!-- asset_management_right_pane -->



    <!--            THIS IS THE FOLD! Only Modal content below!     -->



    <!-- CURSED ITEMS CONTROLS -->

    <div
        id="modalCurseControls" class="modal"
        ng-controller="cursedItemsController"
        ng-init="registerModalDiv('cursedControlsModal','modalCurseControls')"
    >
        <div class="modal-content survivor_sheet_gradient">
            <span class="closeModal" onclick="closeModal('modalCurseControls')">×</span>

            <h3>Cursed Items</h3>
            <p>Use the controls below to add cursed items to a Survivor. Cursed
            gear cannot be removed from the Survivor's gear grid. Archive the gear
            when the survivor dies.</p>

            <div class="cursed_items_flex_container">

                <div class="cursed_item_toggle" ng-repeat="c in settlement.game_assets.cursed_items">
                    <input
                        id="{{c.handle}}"
                        class="cursed_item_toggle"
                        name="toggle_cursed_item"
                        onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
                        type="checkbox"
                        value="{{c.handle}}"
                        ng-checked="arrayContains(c.handle, survivor.cursed_items)"
                    />
                    <label
                        class="cursed_item_toggle"
                        for="{{c.handle}}"
                     >
                        <span class="cursed_item_name">{{c.name}}</span>

                        <div class="cursed_item_ability_block" ng-repeat="a in c.abilities_and_impairments">
                            <span class="cursed_item_ability">{{getAI(a).name}}</span>
                            <span ng-if"getAI(a).desc != undefined"> - </span>
                            <span
                                class="cursed_item_ability_desc"
                                ng-if"getAI(a).desc != undefined"
                                ng-bind-html=" getAI(a).desc|trustedHTML"
                            >
                            </span>
                        </div>
                    </label>

                </div><!-- cursed_item_toggle -->
            </div> <!-- cursed_items_flex_container-->

            <hr/>

            <form method="POST" action="/">
            <!-- This is just a refresh -->
                <button class="kd_blue" onclick="closeModal('modalCurseControls')">
                    Reload Survivor Sheet
                </button>
            </form>
        </div> <!-- modal-content -->
    </div> <!-- modal -->


    <!-- SURVIVOR ATTRIBUTE CONTROLS -->

    $survivor_attrib_controls

    <!-- DRAGON TRAITS -->

    $dragon_controls

    <!-- SAVIOR CONTROLS -->

    <div
        id="modalSavior" class="modal"
    >
        <div class="modal-content survivor_sheet_gradient">
            <span class="closeModal" onclick="closeModal('modalSavior')">×</span>

            <h3>Savior</h3>

            <form method="post" action="/">
                <input type="hidden" name="modify" value="survivor">
                <input type="hidden" name="asset_id" value="$survivor_id">
                <input type="hidden" name="set_savior_type" value="red">
                <button class="affinity_red">Dream of the Beast</button>
            </form>

            <form method="post" action="/">
                <input type="hidden" name="modify" value="survivor">
                <input type="hidden" name="asset_id" value="$survivor_id">
                <input type="hidden" name="set_savior_type" value="green">
                <button class="affinity_green">Dream of the Throne</button>
            </form>

            <form method="post" action="/">
                <input type="hidden" name="modify" value="survivor">
                <input type="hidden" name="asset_id" value="$survivor_id">
                <input type="hidden" name="set_savior_type" value="blue">
                <button class="affinity_blue">Dream of the Lantern</button>
            </form>

            <hr/>

            <form method="post" action="/">
                <input type="hidden" name="modify" value="survivor">
                <input type="hidden" name="asset_id" value="$survivor_id">
                <input type="hidden" name="set_savior_type" value="UNSET">
                <button onclick="this.form.submit()">Unset Savior Info</button>
            </form>

        </div> <!-- modal-content -->

    </div> <!-- modalSavior -->

    <div
        id="modalCustomAI" class="modal"
        ng-init="registerModalDiv('modalCustomAIButton','modalCustomAI')"
    >
        <div class="modal-content survivor_sheet_gradient" ng-app="kdmManager">
            <span class="closeModal" onclick="closeModal('modalCustomAI')">×</span>
            <h3>Create Custom A&I</h3>
            <p>Use the form below to create a new, custom <i>Abilities & Impairments</i> line for $name. As you fill in the fields below, a preview of the new line item will appear in the white box below!</p>
            <hr/>

            <form id="custom_AI_modal" method="POST" action="#edit_abilities">
                <input type="hidden" name="modify" value="survivor"/>
                <input type="hidden" name="asset_id" value="$survivor_id"/>
                <input type="hidden" name="add_custom_AI" value="True"/>
                <input type="text" class="custom_AI" ng-model="name" name="custom_AI_name" placeholder="Name">
                <input type="text" class="custom_AI" ng-model="desc" name="custom_AI_desc" placeholder="Description">
                <select name="custom_AI_type">
                    <option disabled> - A&I Type - </option>
                    <option value="ability" selected>Ability</option>
                    <option value="impairment">Impairment</option>
                    <option value="severe_injury">Severe Injury</option>
                    <option value="curse">Curse</option>
                    <option value="weapon_proficiency">Weapon Proficiency</option>
                </select>

                <p>Preview:</p>

                <div class="custom_AI_preview">
                    <b>{{ name }}:</b> {{ desc }}
                </div>

                <hr/>

                <button class="kd_blue">Add {{name}} to $name</button>

            </form>

        </div> <!-- modal-content -->
    </div> <!-- modalCustomAI -->

    <div
        id="modalDeath" class="modal"
        ng-init="registerModalDiv('modalDeathButton','modalDeath')"
    >
        <div class="modal-content survivor_sheet_gradient">
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
            <button class="kd_alert_no_exclaim red_glow">Die</button>
            </form>
            <hr/>
            <form method="POST" action="">
            <input type="hidden" name="modify" value="survivor"/>
            <input type="hidden" name="asset_id" value="$survivor_id"/>
            <input type="hidden" name="resurrect_survivor" value="True"/>
            <button class="kd_blue">Resurrect $name</button>
            </form>

        </div> <!-- modal-content -->
    </div> <!-- modalDeath -->


    <div
        id="modalAffinity" class="modal"
        ng-init="registerModalDiv('modalAffinityButton','modalAffinity')"
    >
        <div class="modal-content survivor_sheet_gradient">
            <span class="closeModal" onclick="closeModal('modalAffinity')">×</span>

            <h3>Survivor Affinities</h3>
            <p>Use these controls to adjust $name's permanent affinities. Negative values are supported. </p><hr/>

            <form method="POST" action="#" title="Survivor Sheet permanent affinity controls">
                <input type="hidden" name="modify" value="survivor" />
                <input type="hidden" name="asset_id" value="$survivor_id" />
                <input type="hidden" name="modal_update" value="affinities"/>

                <div class="modal_affinity_controls_container">

                    <div class="modal_affinity_control_unit">
                        <div class="bulk_add_control" title="Red affinity controls">
                            <button type="button" class="incrementer" onclick="increment('redCountBox');">+</button>
                            <input id="redCountBox" class="big_number_square" type="number" name="red_affinities" value="$red_affinities"/>
                            <button type="button" class="decrementer" onclick="decrement('redCountBox');">-</button>
                        </div>
                        <div class="affinity_block affinity_red">&nbsp;</div>
                    </div> <!-- modal_affinity_control_unit -->

                    <hr class="affinity_spacer"/>

                    <div class="modal_affinity_control_unit">
                        <div class="bulk_add_control" title="Blue affinity controls">
                            <button type="button" class="incrementer" onclick="increment('blueCountBox');">+</button>
                            <input id="blueCountBox" class="big_number_square" type="number" name="blue_affinities" value="$blue_affinities"/>
                            <button type="button" class="decrementer" onclick="decrement('blueCountBox');">-</button>
                        </div>
                        <div class="affinity_block affinity_blue">&nbsp;</div>
                    </div> <!-- modal_affinity_control_unit -->

                    <hr class="affinity_spacer"/>

                    <div class="modal_affinity_control_unit">
                        <div class="bulk_add_control" title="Green affinity controls">
                            <button type="button" class="incrementer" onclick="increment('greenCountBox');">+</button>
                            <input id="greenCountBox" class="big_number_square" type="number" name="green_affinities" value="$green_affinities"/>
                            <button type="button" class="decrementer" onclick="decrement('greenCountBox');">-</button>
                        </div>
                        <div class="affinity_block affinity_green">&nbsp;</div>
                    </div> <!-- modal_affinity_control_unit -->

                </div> <!-- modal_affinity_controls_container -->

                <hr/>

                <center><button class="kd_blue" type="submit">Save and Refresh!</button></center>
                <br><br>
            </form>
        </div> <!-- modal-content -->
    </div> <!-- modalAffinity -->
    \n""")
    survivor_sheet_rm_controls = Template("""\n
    <hr class="mobile_and_tablet"/>
    <div class="permanently_delete_survivor">
        <h3>Permanently Delete Survivor</h3>
        <form action="#" method="POST" onsubmit="return confirm('Press OK to permanently delete this survivor forever.\\r\\rThis is NOT THE SAME THING as marking it dead using controls above.\\r\\rPermanently deleting the survivor prevents anyone from viewing and/or editing this record ever again!');">
            <input type="hidden" name="remove_survivor" value="$survivor_id"/>
            <p>Use the button below to permanently remove $name. Please note that <b>this cannot be undone</b> and that any relationships between $name and other survivors will be removed.</p>
            <button class="kd_alert_no_exclaim red_glow permanently_delete">Permanently Delete Survivor</button>
        </form>
    </div>
    """)
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
                    value="$base_value"
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
                    value="$gear_value"
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
                      value="$tokens_value"
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
    dragon_traits_controls = Template("""\n

    <div
        id="modalConstellation" class="modal"
    >
        <div class="modal-content survivor_sheet_gradient">
            <span class="closeModal" onclick="closeModal('modalConstellation')">×</span>
            <h3>The Constellations</h3>
            $constellation_table
        </div> <!-- modal-content -->
    </div> <!-- modalConstellation -->

    """)
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
    partner_controls_top = '\n\t<p><span class="tiny_break">&nbsp;</span><h3 class="partner">Partner</h3><select name="partner_id" onchange="this.form.submit()">\n'
    partner_controls_none = '<option selected disabled>Select a Survivor</option>'
    partner_controls_opt = Template('<option value="$value" $selected>$name</option>')
    partner_controls_bot = '</select><span class="tiny_break"/>&nbsp;</span></p>\n\n'
    expansion_attrib_controls = Template("""\n

    <div class="expansion_attribs_container">
        <form method="POST" action="#edit_misc_attribs">
        <input type="hidden" name="modify" value="survivor" />
        <input type="hidden" name="asset_id" value="{{survivor._id.$oid}}" />
        <input type="hidden" name="expansion_attribs" value="None"/> <!-- Hacks -->
        <input type="hidden" name="expansion_attribs" value="None"/> <!-- Hacks -->

        $control_items

        </form>
    </div> <!-- expansion_attribs_container -->

    <hr />

    \n""")
    expansion_attrib_item = Template("""\n

    <div class="line_item">
        <input
            onchange="this.form.submit()"
            type="checkbox" id="$item_id"
            class="kd_css_checkbox kd_radio_option"
            name="expansion_attribs"
            value="$key"
            $checked
        />
        <label
            for="$item_id"
        >
            $key
        </label>
    </div> <!-- expansion_attrib line_item -->

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
    <div id="survivor_notes_angular" ng-app="kdmManager" ng-controller="survivorNotesController" ng-init="notes=$note_strings_list" title="Survivor notes controls. Survivor notes are included in the Campaign Summary Survivor Search results.">
    <p>Add notes to $name's Survivor Sheet using the controls below. Click or tap a note to remove it.</p>
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
    survivor_sheet_fa_level_toggle = Template("""\n
    <span class="survivor_sheet_fa_level_row">
        <input
            id="$input_id"
            class="fighting_art_level_toggle"
            name="fighting_art_level_toggle_$name"
            onchange="updateAssetAttrib(this,'survivor','$survivor_id')"
            type="checkbox"
            value="$lvl"
            $checked
        />
        <label
            class="fighting_art_level_toggle"
            for="$input_id"
         >
            <b>Rank $lvl:</b> $desc
        </label>
    </span>
    \n""")
    survivor_sheet_fighting_art_box = Template("""\n
    <p class="survivor_sheet_fighting_art survivor_sheet_card card_gradient $secret">
        <b class="card_title $constellation">$name</b>
        $lvl_cont
        $desc
    </p>
    \n""")
    survivor_sheet_disorder_box = Template("""\n
    <p class="survivor_sheet_disorder survivor_sheet_card disorder_card_gradient">
        <b class="card_title $constellation">$name</b>
    <span class="disorder_flavor_text">$flavor</span>
    $effect
    </p>
    \n""")


class settlement:

    new = """\n\
    <span class="tablet_and_desktop nav_bar settlement_sheet_gradient"></span>
    <span class="nav_bar_mobile mobile_only settlement_sheet_gradient"></span>
    <span class="top_nav_spacer mobile_only"> hidden </span>

    <br />

    <div
        id="create_new_asset_form_container"
        ng-controller="newSettlementController"
        ng-init="initNewSettlement('$api_url')"
    >

        <form action="#" method="POST">
            <div class="create_user_asset_block_group">
                <input type="hidden" name="new" value="settlement" />
                <input
                    type="text"
                    name="settlement_name"
                    placeholder="New Settlement Name"
                    onclick="this.select()"
                    class="new_asset_name"
                    ng-model = "settlementName"
                    autofocus
                >
            </div>

        <div class="create_user_asset_block_group">
            <h2 class="no_ul">Campaign:</h2>
            <p> Choosing an expansion campaign automatically enables expansion
            content required by that campaign and modifies the settlement timeline,
            milestones, principles, rules and Survivor Sheets. <br/><br/>
            A settlement's campaign <b>cannot be changed</b> after settlement
            creation!</p>

            <div ng-if="showLoader" class="new_settlement_loading"><img src="/media/loading_io.gif"></div>

            <div
                class="new_settlement_campaign_container"
                ng-repeat="c in new_settlement_assets.campaigns"
            >
            <input
                type="radio"
                id="{{c.handle}}"
                class="kd_css_checkbox kd_radio_option"
                name="campaign"
                value="{{c.name}}"
                ng-checked="{{c.default}}"
            />
            <label for="{{c.handle}}">{{c.name}}</label>
            </div>

        </div>  <!-- campaigns -->


        <div class="create_user_asset_block_group">
            <h2 class="no_ul">Expansions:</h2>
            <p> Enable expansion content by toggling items below. Expansion
            content may also be enabled (or disabled) later using the controls
            on the left-side navigation bar.</p>

            <div ng-if="showLoader" class="new_settlement_loading"><img src="/media/loading_io.gif"></div>

            <div
                class="new_settlement_expansions_container"
                ng-repeat="e in new_settlement_assets.expansions"
            >
            <input
                type="checkbox"
                id="{{e.handle}}"
                class="kd_css_checkbox kd_radio_option"
                name="expansions"
                value="{{e.handle}}"
            />
            <label for="{{e.handle}}">{{e.name}}
                <p ng-if="e.subtitle" class="new_settlement_asset"> {{e.subtitle}}</p>
            </label>
            </div>

        </div> <!-- expansions -->


        <div class="create_user_asset_block_group">
            <h2 class="no_ul">Survivors:</h2>
            <p>By default, new settlements are created with no survivors. Toggle options below to create the settlement with pre-made survivors. </p>

            <input type="hidden" name="survivors" value="None"/> <!-- Both of these are necessary -->
            <input type="hidden" name="survivors" value="None"/> <!-- Hack City! -->

            <input
                type="checkbox"
                id="create_prologue_survivors"
                class="kd_css_checkbox kd_radio_option"
                name="create_prologue_survivors"
                value="True"
            />
            <label
                for="create_prologue_survivors"
            >
                Four "First Story" Survivors
                <p class="new_settlement_asset">Two randomly generated male and
                female survivors will be created,and added to the <i>Departing
                Survivors</i> group. Starting gear will be added to Settlement
                Storage.</p>
            </label>

            <div ng-if="showLoader" class="new_settlement_loading"><img src="/media/loading_io.gif"></div>

            <div
                class="new_settlement_survivors_container"
                ng-repeat="s in new_settlement_assets.survivors"
            >
                <input
                    id="{{s.handle}}"
                    class="kd_css_checkbox kd_radio_option"
                    type="checkbox"
                    name="survivors"
                    value="{{s.name}}"
                />
                <label
                    for="{{s.handle}}"
                />
                    {{s.name}}
                </label>
            </div> <!-- survivors -->


        <br/><br/>

        <button ng-if="showLoader == false" class="kd_blue"> Create {{settlementName}}</button>

        <br/><br/><br/>

        </form>

    </div> <!-- create_new_asset_form_container -->
    \n"""

    storage_warning = Template(""" onclick="return confirm('Remove $item_name from Settlement Storage?');" """)
    storage_remove_button = Template("""\n\
    \t<button $confirmation id="remove_item" name="remove_item" value="$item_key" style="background-color: #$item_color; color: #$item_font_color;"> $item_key_and_count </button>
    \n""")
    storage_tag = Template('<h3 class="inventory_tag" style="color: #$color">$name</h3><hr/>')
    storage_resource_pool = Template("""\n\
    <p>Hide: $hide, Bone: $bone, Scrap: $scrap, Organ: $organ</p>
    \n""")


    # dashboard refactor
    dashboard_campaign_asset = Template("""\n
    <form method="POST" action="#">
        <input type="hidden" name="view_campaign" value="$asset_id" />
        <button class="settlement_sheet_gradient dashboard_settlement_name">
        <b class="dashboard_settlement_name">$name</b>
        <i>$campaign</i></span><br/>
        LY $ly. &ensp; Survivors: $pop &ensp;
        $players_block
        </button>
    </form>
    \n""")

    #   campaign view campaign summary
    campaign_summary_survivors_top = '<div class="campaign_summary_survivors">\n<h3 class="mobile_only">Survivors</h3>'
    campaign_summary_survivors_bot = '<hr class="mobile_only"/></div> <!-- campaign_summary_survivors -->'
    summary = Template("""\n\n
        <!--

            Campaign Summary App starts here! Beware of JS inheritance (because it
            hates you and it hates freedom and it will ruin your life).

        -->

        <script src="/media/campaignSummary.js"></script>

        <div
            id = "campaign_summary_angularjs_controller_container"
            ng-init="initialize('campaignSummary', '$user_id', '$user_login', '$api_url','$settlement_id')"
        >
            <span class="tablet_and_desktop nav_bar campaign_summary_gradient"></span>
            <span class="nav_bar_mobile mobile_only campaign_summary_gradient"></span>
            <span class="top_nav_spacer mobile_only"> hidden </span>

            <div class="campaign_summary_headline_container">
                <h1 class="settlement_name"> %s {{settlement_sheet.name}}</h1>
                <p class="campaign_summary_campaign_type">{{settlement_sheet.campaign}}</p>
                <p>Population: $population ($sex_count); $death_count deaths</p>
                <hr class="mobile_only"/>
                <p>Lantern Year: {{current_ly}}, Survival Limit: $survival_limit</p>
                <hr class="mobile_only"/>
            </div> <!-- campaign_summary_headline_container -->

            <a id="edit_hunting_party" class="mobile_only"></a>

            <span class="vertical_spacer desktop_only"></span>


            <div class="campaign_summary_panels_container">

                $survivors

                <hr class="mobile_only invisible">
                <br class="mobile_only">

                <div class="campaign_summary_facts_box">

                $special_rules


                <!-- angular.js Endeavors app -->

                <a id="endeavors"><hr class="mobile_only"/></a>

                <div ng-if="user_is_settlement_admin" class="$show_endeavor_controls">
                    <div
                        title="Manage settlement Endeavor tokens here! Settlement admins may use the controls at the right to increment or decrement the total number of tokens!"
                        class="campaign_summary_endeavor_controller"
                        ng-controller="endeavorController"
                        ng-init="endeavors=$endeavor_tokens;"
                    >

                        <span ng-if="endeavors >= 1">
                            <div
                                class="tokens"
                            >
                                <img
                                    ng-repeat="e in range(endeavors)"
                                    class="campaign_summary_endeavor_star"
                                    src="/media/icons/endeavor_star.png"
                                >
                            </div>
                            <div ng-if="user_is_settlement_admin" class="controls">
                                <button ng-click="rmToken()" > &#9662; </button>
                                <button ng-click="addToken()" > &#9652; </button>
                            </div>
                        </span>

                        <div
                            ng-if="endeavors <= 0"
                            ng-click="addToken()"
                            class="endeavor_controls_toggle settlement_sheet_block_group"
                        >
                            <h2>Endeavor Tokens</h2>
                            <span>Click or tap here to manage Endeavor Tokens.</span>
                        </div>

                        <div class="endeavor_controls_clear_div"></div>

                    </div>


                </div> <!-- show_endeavor_controls -->
            <hr class="mobile_only">
            <!-- endeavors app -->

            <div class="campaign_summary_small_box endeavor_box">
                <h4>- Available Endeavors -</h4>
                $endeavors
            </div>
            <div class="campaign_summary_small_box">
                <h4>- Settlement Bonuses -</h4>
                $settlement_bonuses
                $survivor_bonuses
            </div>
            <hr class="mobile_only"/>
            <div class="campaign_summary_small_box">
                <h4>- Principles -</h4>
                <span
                    class="kd_checkbox_checked campaign_summary_bullet"
                    ng-repeat="p in settlement_sheet.principles"
                >
                    {{p}}
                </span>

            </div>
            <div class="campaign_summary_small_box">
                <h4>- Innovations -</h4>
                <span
                    class="kd_checkbox_checked campaign_summary_bullet"
                    ng-repeat="i in settlement_sheet.innovations"
                >
                    {{i}}
                </span>
            </div>

            <hr class="mobile_only"/>

            <div class="campaign_summary_small_box">
                <h4>- Locations -</h4>
                <span
                    class="kd_checkbox_checked campaign_summary_bullet"
                    ng-repeat="l in settlement_sheet.locations"
                >
                    {{l}}
                </span>
            </div>

            <hr class="mobile_only"/>

            <div class="campaign_summary_small_box">
                <h4>- Monsters -</h4>
                <h3 class="monster_subhead"> Defeated </h3>
                <span class="kd_checkbox_checked campaign_summary_bullet" ng-repeat="d in settlement_sheet.defeated_monsters track by $index">
                    {{d}}
                </span>

                <h3 class="monster_subhead">Quarries </h3>
                <span class="kd_checkbox_checked campaign_summary_bullet" ng-repeat="n in settlement_sheet.quarries">
                    {{ settlement.game_assets.monsters[n].name }}
                </span>

                <h3 class="monster_subhead">Nemesis Monsters</h3>
                <span class="kd_checkbox_checked campaign_summary_bullet" ng-repeat="n in settlement_sheet.nemesis_monsters">
                    {{ settlement.game_assets.monsters[n].name }}
                </span>

            </div>
        </div> <!-- campaign_summary_facts_box -->

    <div class="campaign_summary_bottom_spacer"> </div>

</div> <!-- campaign_summary_panels_container -->



    <!--

        This is 'the fold'. The only content below here should be heavy-
        lift JS applications, modals, etc. That don't need to load or be
        visible right away on page load.

    -->


    <button class="manage_departing_survivors $show_departing_survivors_management_button" id="departingSurvivorsModalOpener">Manage <b>Departing</b> Survivors</button>

    <div
        id="departingSurvivorsModalContent" class="modal"
        ng-controller="manageDepartingSurvivorsController"
        ng-init="registerModalDiv('departingSurvivorsModalOpener','departingSurvivorsModalContent');"
    >
        <div class="modal-content survivor_sheet_gradient">
        <span class="closeModal" onclick="closeModal('departingSurvivorsModalContent')">x</span>
        <h3>Modify Departing Survivors</h3>
        <div class="hunting_party_macro" style="border-left: 0 none;">
          <form action="#" method="POST">
            <input type="hidden" name="modify" value="settlement"/>
            <input type="hidden" name="asset_id" value="$settlement_id"/>
            <input type="hidden" name="hunting_party_operation" value="survival"/>
            <p>Survival</p>
            <button name="operation" value="increment">+1</button>
            <button name="operation" value="decrement">-1</button>
        </form>
      </div>
      <div class="hunting_party_macro">
        <form action="#" method="POST">
            <input type="hidden" name="modify" value="settlement"/>
            <input type="hidden" name="asset_id" value="$settlement_id"/>
            <input type="hidden" name="hunting_party_operation" value="Brain Event Damage"/>
            <p>Brain Event Damage</p>
            <button name="operation" value="increment">+1</button>
        </form>
      </div>
        <hr class="invisible mobile_only"/>
      <div class="hunting_party_macro">
        <form action="#" method="POST">
            <input type="hidden" name="modify" value="settlement"/>
            <input type="hidden" name="asset_id" value="$settlement_id"/>
            <input type="hidden" name="hunting_party_operation" value="Insanity"/>
            <p>Insanity</p>
            <button name="operation" value="increment">+1</button>
            <button name="operation" value="decrement">-1</button>
        </form>
      </div>
      <div class="hunting_party_macro">
        <form action="#" method="POST">
            <input type="hidden" name="modify" value="settlement"/>
            <input type="hidden" name="asset_id" value="$settlement_id"/>
            <input type="hidden" class="clear_both" name="hunting_party_operation" value="Courage"/>
            <p>Courage</p>
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
            <p>Understanding</p>
            <button name="operation" value="increment">+1</button>
            <button name="operation" value="decrement">-1</button>
        </form>
      </div>

        <hr/>

        <h3 class="return_departing_survivors_modal">Target Monster:</h3>

        <select
            id="set_departing_survivors_current_quarry"
            class="hunting_party_current_quarry"
            name="current_quarry"
            ng-model="current_quarry"
            ng-change="saveCurrentQuarry()"
            ng-options="d for d in settlement.game_assets.defeated_monsters"
        >
            <option disabled selected value="">Set Target Monster</option>
        </select>

        <hr/>

        <div class="departing_survivors_modal_return_container">
            <h3 class="return_departing_survivors_modal" >Return Departing Survivors</h3>

            <form
                action="/"
                method="POST"
                onsubmit="return confirm('Press OK to return all Departing Survivors. This will automatically do the following for each living Departing Survivor: \\r - Remove them from the Departing Survivors group \\r - Mark them as a returning survivor during the upcoming Lantern Year \\r - Uncheck all hit location boxes \\r - Remove all armor points \\r - Remove all attribute tokens and gear modifiers \\r - Increment Hunt XP by +1 \\r - Increment Hunt XP by +4 for Saviors \\r \\rReturning Departing Survivors will also: \\r Add the current quarry to the Defeated Monsters list \\r Add the current quarry to the settlement timeline for this year \\r Update the settlement Event Log');"
            >
                <input type="hidden" name="return_departing_survivors" value="victory"/>
                <input type="hidden" name="asset_id" value="$settlement_id"/>
                <button class="kd_blue return_departing_survivors">Victorious!</button>
            </form>

            <br/>

            <form
                action="/"
                method="POST"
                onsubmit="return confirm('Press OK to return all Departing Survivors. This will automatically do the following for each Departing Survivor: \\r - Remove them from the Departing Survivors group \\r - Uncheck all hit location boxes \\r - Remove all armor points \\r - Remove all attribute tokens and gear modifiers \\r \\rReturning Departing Survivors will also: \\r Add the current quarry to the settlement timeline for this year \\ Update the settlement Event Log ');"
            >
                <input type="hidden" name="return_departing_survivors" value="defeat"/>
                <input type="hidden" name="asset_id" value="$settlement_id"/>
                <button class="kd_alert_no_exclaim red_glow return_departing_survivors">Defeated...</button>
            </form>


            <br/><br/>
        </div>

        </div> <!-- modal-content -->
    </div> <!-- modalDepartingSurvivors whole deal-->


        <!-- SURVIVOR SEARCH -->


    <input
        id="survivorSearchModalOpener"
        class="survivor_search"
        placeholder="Search Living Survivors"
        ng-model="searchText"
    </input>

    <div
        id="survivorSearchModalContent"
        class="survivor_search_modal_container modal"
    >
        <div
            class="survivor_search_modal_content survivor_sheet_gradient"
            ng-controller = "survivorSearchController"
            ng-init = "loadSurvivors();registerModalDiv('survivorSearchModalOpener','survivorSearchModalContent');"
        >

            <div id="searchTextResults" class="survivor_search_results_buttons">

                <form
                    method="POST" action="/"
                    ng-repeat="s in survivors | filter:searchText "
                >
                    <input type="hidden" name="view_survivor" value="{{s._id.$oid}}" />
                    <button
                        class="survivor_search_button kd_lantern"
                        ng-class="{disabled : userCanManage(s) == false}"
                        ng-if="s.dead == undefined && s.retired == undefined"
                    >
                      <p class="survivor_name">{{s.name}} [{{s.sex}}]</p>
                      <div class="survivor_assets"><b>Hunt XP:</b> {{s.hunt_xp}} <b>Courage:</b> {{s.Courage}} <b>Understanding:</b> {{s.Understanding }}</div>
                      <div class="survivor_assets">
                        <b>MOV</b> {{s.Movement}} |
                        <b>ACC</b> {{s.Accuracy}} |
                        <b>STR</b> {{s.Strength}} |
                        <b>EVA</b> {{s.Evasion}} |
                        <b>LUCK</b> {{s.Luck}} |
                        <b>SPD</b> {{s.Speed}}
                      </div>
                      <div ng-if="s.epithets.length >= 1" class="survivor_assets"><b>Epithets:</b> {{ s.epithets.join(", ") }}</div>
                      <div ng-if="s.fighting_arts.length >= 1" class="survivor_assets"><b>Fighting Arts:</b> {{ s.fighting_arts.join(", ") }}</div>
                      <div ng-if="s.disorders.length >= 1" class="survivor_assets"><b>Disorders:</b> {{ s.disorders.join(", ") }}</div>
                      <div ng-if="s.abilities_and_impairments.length >= 1" class="survivor_assets"><b>Abilities & Impairments:</b> {{ s.abilities_and_impairments.join(", ") }}</div>
                      <div ng-if="s.notes.length >= 1" class="survivor_assets"><b>Notes:</b>
                        <span ng-repeat="n in s.notes"> {{n.note}} </span>
                      </div>
                    </button>
                </form>
            </div>

        <hr/>
        <span class="survivor_search_retired_survivors_warning">Retired survivors are not included in these results!</span>
        <button
            class="kd_blue close_modal"
            onclick="closeModal('survivorSearchModalContent')"
        >
        Close Search Window
        </button>

        </div> <!-- survivor_search_modal_content -->

    </div> <!-- survivorSearch -->

</div> <!-- campaign_summary methods -->

    \n""" % dashboard.campaign_flash)

    form = Template("""\n\
        <!--

            Sttlement Sheet App starts here! Beware of JS inheritance (because
            it hates you and it hates freedom and it will ruin your life).

        -->

        <script src="/media/settlementSheet.js"></script>

        <div
            id = "settlement_sheet_angularjs_controller_container"
            ng-init="initialize('settlementSheet', '$user_id', '$user_login', '$api_url','$settlement_id')"
        >

        <span class="tablet_and_desktop nav_bar settlement_sheet_gradient"></span>
        <span class="nav_bar_mobile mobile_only settlement_sheet_gradient"></span>
        <div class="top_nav_spacer"> hidden </div>

        <div id="asset_management_left_pane">

            <input
                name="name"
                id="settlementName"
                class="settlement_sheet_settlement_name settlement_name"
                type="text"
                value="{{settlement_sheet.name}}"
                placeholder="Settlement Name"
                onclick="this.select()"
                onchange="updateAssetAttrib(this, 'settlement', '$settlement_id')"
            />

            <p
                id="campaign_type"
                class="settlement_sheet_campaign_type"
                title="Campaign type may not be changed after a settlement is created!"
            >
                {{settlement_sheet.campaign}}
            </p>


        <h1 ng-if="settlement_sheet.abandoned"class="alert">ABANDONED</h1>

        <div class="settlement_form_wide_box">
            <div class="big_number_container left_margin">
                <button
                    class="incrementer"
                    onclick="stepAndSave('up','survivalLimitBox','settlement','$settlement_id');"
                >
                    &#9652;
                </button>
                <input
                    id="survivalLimitBox"
                    class="big_number_square"
                    type="number" name="survival_limit"
                    value="$survival_limit"
                    min="$min_survival_limit"
                    onchange="updateAssetAttrib(this,'settlement','$settlement_id')"
                />
                <button
                    class="decrementer"
                    onclick="stepAndSave('down','survivalLimitBox','settlement','$settlement_id');"
                >
                    &#9662;
                </button>
            </div>
            <div class="big_number_caption">Survival Limit<br /><font class="settlement_sheet_survival_limit_caption">(min: $min_survival_limit)</font></div>
        </div><!-- settlement_form_wide_box -->

        <br class="mobile_only"/>
        <hr class="mobile_only"/>

        <div class="settlement_form_wide_box">
            <div class="big_number_container left_margin">
                <button
                    class="incrementer"
                    onclick="stepAndSave('down','populationBox','settlement','$settlement_id');"
                >
                    &#9652;
                </button>
                <input
                    id="populationBox"
                    class="big_number_square"
                    type="number" name="population"
                    value="{{settlement_sheet.population}}"
                    onchange="updateAssetAttrib(this,'settlement','$settlement_id')"
                    min="0"
                />
                <button
                    class="decrementer"
                    onclick="stepAndSave('down','populationBox','settlement','$settlement_id');"
                >
                    &#9662;
                </button>
            </div>
            <div class="big_number_caption">Population</div>
        </div> <!-- settlement_form_wide_box -->

        <br class="mobile_only"/>
        <hr class="mobile_only"/>

        <div class="settlement_form_wide_box">
            <div class="big_number_container left_margin">
                <button
                    class="decrementer"
                    onclick="stepAndSave('up','deathCountBox','settlement','$settlement_id');"
                >
                    &#9652;
                </button>
                <input
                    id="deathCountBox"
                    class="big_number_square"
                    type="number"
                    name="death_count"
                    value="{{settlement_sheet.death_count}}"
                    min="0"
                    onchange="updateAssetAttrib(this,'settlement','$settlement_id')"
                />
                <button
                    class="decrementer"
                    onclick="stepAndSave('down','deathCountBox','settlement','$settlement_id');"
                >
                    &#9662;
                </button>
            </div>
            <div class="big_number_caption">Death Count</div>
        </div> <!-- settlement_form_wide_box -->


        <hr class="invisible">



            <!-- STORAGE CONTROLS START HERE -->



        <div class="settlement_sheet_block_group settlement_storage">
            <h2>Storage</h2>
            <p>Gear and Resources may be stored without limit.<br/><br/>

            <button id="modalStorageButton" class="kd_blue">+ Add Item to Storage</button>

            <br><br class="desktop_only">
            <a id="edit_storage" class="mobile_only"/></a>

            <form method="POST" action="#edit_storage">
                <input type="hidden" name="modify" value="settlement" />
                <input type="hidden" name="asset_id" value="$settlement_id" />
                $storage
                <button id="remove_item" class="hidden" style="display: none" name="remove_item" value="" /> </button>
            </form>

        </div> <!-- settlement_sheet_block_group for storage -->

    </div> <!-- asset_management_left_pane -->




    <div id="asset_management_middle_pane">


                    <!-- LOCATIONS - THIS HAS ITS OWN FORM  -->


        <a id="edit_locations" class="mobile_only"><a/>

        <div
            class="settlement_sheet_block_group"
            ng-controller="locationsController"
            title="Click or tap an item to remove it from this list."
        >

            <h2>Settlement Locations</h2>
            <p>Locations in your settlement.</p>
            <hr class="invisible"/> <!-- this is pretty low rent -->

            <div
                ng-repeat="l in settlement_sheet.locations"
                ng-init="locationLevel = settlement_sheet.location_levels[l]"
            >
                <div class="line_item location_container">
                    <span class="bullet"></span>
                    <span
                        class="item"
                        ng-click="rmLocation($index,l);"
                    >
                        {{l}}
                    </span>
                    <span ng-if="settlement_sheet.location_levels[l] != undefined" class="location_lvl_select">
                        <select
                            class="location_level"
                            ng-model="locationLevel"
                            ng-options="locationLevel as 'Lvl. '+locationLevel for locationLevel in [1,2,3]"
                            ng-change="setLocationLevel(l,locationLevel)"
                            ng-selected="locationLevel"
                        >
                        </select>
                    </span> <!-- optional levels controls -->
                </div> <!-- location line item -->

            </div> <!-- settlement_sheet.locations repeater -->


            <div class="line_item">
                <span class="empty_bullet"></span>
                <select
                    ng-model="newLocation"
                    ng-options="l.handle as l.name for l in settlement.game_assets.locations_options"
                    ng-change="addLocation()"
                >
                    <option disabled selected value="">Add a Location</option>
                </select>
            </div> <!-- line item -->

        </div> <!-- settlement_sheet_block_group locations controller-->



                    <!-- INNOVATIONS - HAS ITS OWN FORM-->

        <a id="edit_innovations" class="mobile_only"/></a>


        <div
            class="settlement_sheet_block_group"
            ng-controller="innovationsController"
            title="Click or tap on an item to remove it from this list."
        >

            <h2>Innovations</h2>
            <p>The settlement's innovations (including weapon masteries).</p>

            <hr class="invisible"/>

            <div
                class="line_item location_container"
                ng-repeat="i in settlement_sheet.innovations"
            >
                <span class="bullet"></span>
                <span
                    class="item"
                    ng-click="rmInnovation($index,i)"
                >
                    {{i}}
                </span>
           </div>

            <div class="line_item">
                <span class="empty_bullet" /></span> $innovations_add
            </div>

            <div class="innovation_deck" ng-if="settlement_sheet.innovations.length != 0">
                <h3> - Innovation Deck - </h3>
                <ul class="asset_deck">
                    <li ng-repeat="i in $innovation_deck"> {{i}} </li>
                </ul>
            </div>

        </div> <!-- settlement_sheet_block_group innovations-->


    </div> <!-- asset_management_left_pane -->



    <!-- END OF LEFT PANE -->



    <div id="asset_management_right_pane">

        <a id="edit_principles" class="mobile_only"></a>

        <div
            class="settlement_sheet_block_group"
            ng-controller="principlesController"
        >
            <h2>Principles</h2>
            <p>The settlement's established principles.</p>

            <div principle" ng-repeat="p in settlement.game_assets.principles_options" class="settlement_sheet_principle_container">
                <div id="{{p.name}} principle" class="principles_container">

                    <div class="settlement_sheet_principle_name"> {{p.name}} </div>

                    <div
                        class="principle_option"
                        ng-repeat="o in p.options"
                    >
                        <input
                            type="radio"
                            class="kd_css_checkbox kd_radio"
                            id="{{o.input_id}}"
                            name="{{p.form_handle}}"
                            value="{{o.name}}"
                            ng-checked="o.checked"
                            ng-click="set(p.handle,o.handle)"
                        >

                        <label
                            id="{{o.input_id}}Label"
                            for="{{o.input_id}}"
                        >
                            {{ o.name }}
                        </label>

                    </div> <!-- principle_option repeater-->

                </div> <!-- principles_container -->

            </div> <!-- settlement_sheet_principle_container -->

            <br/>
            <div class="unset_principle_container">
                <span class="empty_bullet rm_bullet"></span>
                <select
                    ng-model="unset"
                    ng-change="unset_principle();"
                    ng-options="p.handle as p.name for p in settlement.game_assets.principles_options"
                >
                    <option disabled value="">Unset Principle</option>
                </select>
            </div> <!-- unset_principle_container -->

        </div> <!-- principle block group -->


                       <!-- MILESTONES -->

        <a id="edit_milestones" class="mobile_only"/></a>

        <div class="settlement_sheet_block_group">
            <h2>Milestone Story Events</h2>
            <p>Trigger these story events when milestone condition is met.</p>

            <div ng-repeat="m in settlement.game_assets.milestones_options" class="milestone_content_container">
                <input
                    id="{{m.handle}}"
                    class="kd_css_checkbox kd_radio_option"
                    type="checkbox"
                    name="toggle_milestone"
                    value="{{m.name}}"
                    onchange="updateAssetAttrib(this, 'settlement', '$settlement_id');"
                    ng-checked="arrayContains(m.name, settlement_sheet.milestone_story_events)"/>
                </input>
                <label
                    for="{{m.handle}}"
                    class="settlement_sheet_milestone_container"
                >
                    {{m.name}}
                    <span class="milestone_story_event">
                        <font class="kdm_font">g</font> <b>{{m.story_event}}</b>
                        <span class="milestone_story_reference">
                            (p.{{settlement.game_assets.events[m.story_event_handle].page}})
                        </span>
                    </span>
                </label>
            </div> <!-- milestone div -->

        </div> <!-- block_group for milestones -->




                    <!-- QUARRIES - HAS ITS OWN FORM-->

        <a id="edit_quarries"/>

        <div class="settlement_sheet_block_group" title="Click or tap an item to remove it from this list.">

            <h2>Quarries</h2>
            <p>The monsters your settlement can select to hunt.</p>

            <div>
                <div
                    class="line_item location_container"
                    ng-controller="quarriesController"
                    ng-repeat="q in settlement_sheet.quarries"
                >
                    <div> <!-- span holder -->
                        <span class="bullet"></span>
                        <span
                            class="item"
                            ng-click="removeQuarry($index, q)"
                        >
                            {{settlement.game_assets.monsters[q].name}}
                        </span>
                    </div>
                </div>
            </div>

            <div class="line_item">
                <span class="empty_bullet" /></span>
                <select
                    ng-controller="quarriesController"
                    ng-model="addQuarryMonster"
                    ng-options="q.handle as q.name for q in settlement.game_assets.quarry_options"
                    ng-change="addQuarry($index)"
                >
                    <option selected disabled value="">Add Quarry Monster</option>
                </select>
            </div> <!-- line_item -->

        </div> <!-- settlement_Sheet_block_group quarry controls-->


                    <!-- NEMESIS MONSTERS -->

        <a id="edit_nemeses"/>

        <div
            class="settlement_sheet_block_group"
            ng-controller="nemesisEncountersController"
            title="Click or tap an item to remove it from this list."
        >
            <h2><img class="icon" src="media/icons/nemesis_encounter_event.jpg"/> Nemesis Monsters</h2>
            <p>The available nemesis encounter monsters.</p>

            <div
                class="settlement_sheet_nemesis_line_item"
                ng-repeat="n in settlement_sheet.nemesis_monsters"
            >
                <span class="bullet"></span>
                <span class="item" ng-click="rmNemesis($index,n)">
                    {{settlement.game_assets.monsters[n].name}}
                </span>
                <span class="nemesis_levels">
                    <div
                        class="nemesis_level_toggle_container"
                        ng-repeat="l in range(settlement.game_assets.monsters[n].levels, 'increment')"
                    >
                        <input
                            id="{{n + '_lvl_' + l}}"
                            type="checkbox"
                            class="kd_css_checkbox"
                            ng-model="nemesisLvlToggleValue"
                            ng-checked="arrayContains(l,settlement_sheet.nemesis_encounters[n])"
                        />
                        <label
                            for="{{n + '_lvl_' + l}}"
                            id="{{n+'_lvl_'+l}}_label"
                            ng-click="toggleNemesisLevel(n,l,$event)"
                        >
                            Lvl {{l}}
                        </label>
                    </div> <!-- nemesis_level_toggle_container -->
                </span>
            </div>

            <span class="empty_bullet"></span>
            <select
                ng-model="addNemesisMonster"
                ng-options="n.handle as n.name for n in settlement.game_assets.nemesis_options"
                ng-change="addNemesis()"
            >
                <option selected disabled value="">Add Nemesis Monster</option>
            </select>

        </div> <!-- Nemesis block group/controller -->



                    <!-- DEFEATED MONSTERS -->



        <a id="edit_defeated_monsters"/>

        <div class="settlement_sheet_block_group" ng-controller="defeatedMonstersController" title="Click or tap an item to remove it from this list.">
        <h2>Defeated Monsters</h2>
        <p>A list of defeated monsters and their level.</p>

        <div
            class="line_item defeated_monsters_container"
            ng-repeat="x in settlement_sheet.defeated_monsters track by $index"
        >
            <div> <!-- span holder -->
                <span class="bullet"></span>
                <span class="item" ng-click="rmDefeatedMonster($index, x)">
                    {{x}}
                </span>
            </div>
        </div>

        <div class="line_item">
            <span class="empty_bullet" /></span>
            <select
                ng-model="dMonst"
                ng-change="addDefeatedMonster($index)"
                ng-options="d as d for d in settlement.game_assets.defeated_monsters ">
            >
                <option selected disabled value="">Add Defeated Monster</option>
            </select>
        </div> <!-- line_item -->

    </div>

    <hr class="mobile_only"/>

        <a id="edit_lost_settlements" class="mobile_only"></a>


                    <!-- LOST SETTLEMENTS ANGULARJS app -->


        <div
            class="lost_settlements_app_container"
            ng-app="kdmManager"
            ng-controller="lostSettlementsController"
            ng-init="loadLostSettlements();"
        >
        <div
            onclick="showHide('lostSettlementsTooltip'); showHide('lostSettlementsControls')"
            class="settlement_sheet_block_group lost_settlements"
        >
            <h2>Lost Settlements</h2>
            <p>Click or tap to show/hide controls.</p>
            <p style="display: none" id="lostSettlementsTooltip">
                <span class="metrophobic">See </span>
                <font class="kdm_font">g</font> <b>Game Over</b>
                <span class="metrophobic"> on p.179</span>:<br/><br/>
                    &ensp;
                        <span class="lost_settlement lost_settlement_checked"></span>
                        1. Left Overs
                    <br/>
                    &ensp;
                        <span class="lost_settlement lost_settlement_checked"></span>
                        <span class="lost_settlement lost_settlement_checked"></span>
                        2. Those Before Us
                    <br/>
                    &ensp;
                        <span class="lost_settlement lost_settlement_checked"></span>
                        <span class="lost_settlement lost_settlement_checked"></span>
                        <span class="lost_settlement lost_settlement_checked"></span>
                        3. Ocular Parasites
                    <br/>
                    &ensp;
                        <span class="lost_settlement lost_settlement_checked"></span>
                        <span class="lost_settlement lost_settlement_checked"></span>
                        <span class="lost_settlement lost_settlement_checked"></span>
                        <span class="lost_settlement lost_settlement_checked"></span>
                        4. Rainy Season
                    <br/>
            </p>

            <div
                class="lost_settlement_squares"
            >

            <span
                class="lost_settlement_box_socket"
                ng-repeat="x in lost"
            >
                <span id="box_{{x.id_num}}" class="lost_settlement {{x.class}}"></span>
            </span>

            </div>
        </div> <!-- settlement_sheet_block_group -->

        <div id="lostSettlementsControls" style="display: none" class="lost_settlements_controls">
            <button
                ng-click="rmLostSettlement(); ls_range(2)"
            >
                &#9662;
            </button>
            <button
                ng-click="addLostSettlement()"
            >
                &#9652;
            </button>
        </div>

        </div> <!-- lost settlement application -->


        <br class="mobile_only"/>
        <hr class="mobile_only"/>

        <div class="settlement_sheet_block_group">

            <h3>Abandon Settlement</h3>
            <p>Mark a settlement as "Abandoned" to prevent it from showing up in your active campaigns without removing it from the system.</p>

            <form action="#" method="POST" onsubmit="return confirm('This will prevent this settlement from appearing on any user Dashboard, including yours. Press OK to Abandon this settlement forever.');">
                <input type="hidden" name="modify" value="settlement" />
                <input type="hidden" name="asset_id" value="$settlement_id" />
                <input type="hidden" name="abandon_settlement" value="toggle" />
                <button class="kd_alert_no_exclaim red_glow"> Abandon Settlement </button>
            </form>
        </div>

    $remove_settlement_button

    </div> <!-- right pane -->


    <!--

        This is the fold! Anything below here is below the fold!
        This should only be modals, heavy angularjs stuff, etc. that is
        still within the settlementSheetApp, but that doesn't need to
        load right away.

    -->


    <div
        id="modalStorage" class="modal"
        ng-init="registerModalDiv('modalStorageButton','modalStorage');"
    >

      <!-- Modal content -->
        <div class="full_size_modal_panel timeline_gradient">
            <span class="closeModal" onclick="closeModal('modalStorage')">×</span>

                <!-- ADD TO STORAGE - THIS IS ITS OWN FORM-->
            <form method="POST" action="#edit_storage">
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
                <center><button class="kd_blue">Add!</button></center>
                <br><br><br>
            </form>
        </div> <!-- modal-content -->
    </div> <!-- modalStorage -->




</div> <!-- settlementSheetApp -->



    \n""")


    remove_settlement_button = Template("""\

    <div class="settlement_sheet_block_group">
        <h3>Permanently Remove Settlement</h3>
        <form
            action="#"
            method="POST"
            onsubmit="return confirm('Press OK to permanently delete this settlement AND ALL SURVIVORS WHO BELONG TO THIS SETTLEMENT forever. \\r\\rPlease note that this CANNOT BE UNDONE and is not the same as marking a settlement Abandoned.\\r\\rPlease consider abandoning old settlements rather than removing them, as this allows data about the settlement to be used in general kdm-manager stats.\\r\\r');"
        >
            <input type="hidden" name="remove_settlement" value="$settlement_id"/>
            <p>
                Use the button below to permanently delete <i>$settlement_name</i>.
                Please note that <b>this cannot be undone</b> and that this will
                also permanently remove all survivors associated with this
                settlement.
            </p>
            <button class="kd_alert_no_exclaim red_glow permanently_delete">
                Permanently Delete Settlement
            </button>
        </form>
    </div>
    """)

    location_level_controls = Template("""\n\
    $location_name - Lvl
    <form method="POST" action="#edit_locations" class="location_level">
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />
        <select class="location_level" name="location_level_$location_name" onchange="this.form.submit()">
            $select_items
        </select>
    </form>
    \n""")
    principle_radio = Template("""\n
        <input onchange="this.form.submit()" type="radio" id="$handle" class="radio_principle" name="principle_$principle_key" value="$option" $checked /> 
        <label class="radio_principle_label" for="$handle"> $option </label>
    \n""")
    principle_control = Template("""\n
    <div>
    <p><b>$name</b></p>
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
    innovation_heading = Template("""\n
    <h5>$name</h5><p class="$show_subhead campaign_summary_innovation_subhead innovation_gradient">$subhead</p>
    \n""")
    endeavor = Template("""\n
    <p class="$p_class">
    &nbsp; $cost $name$punc $desc $type
    </p>
    \n""")


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
            <input class="sign_in" type="email" name="login" placeholder="Email" onclick="this.select()" autofocus required>
            <input class="sign_in" type="password" name="password" placeholder="Password" required/>
			<div id="sign_in_remember_me">
			  <label class="sign_in" for="keep_me_signed_in">Stay Logged in:</label>
			</div>
			<div id="sign_in_checkbox">
			  <input type="checkbox" class="sign_in" name="keep_me_signed_in" id="keep_me_signed_in">
			</div>
			<div id="sign_in_button">
			  <button class="sign_in kd_blue">Sign In or Register</button>
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
            <button class="sign_in kd_blue">Register New User</button>
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

    def __init__(self):
        pass

    """ This is for HTML that doesn't really fit anywhere else, in terms of
    views, etc. Use this for helpers/containers/administrivia/etc. """

    basic_http_header = "Content-type: text/html\n\n"
    basic_file_header = "Content-Disposition: attachment; filename=%s\n"

    error_500 = Template("""%s<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <html><head><title>%s</title></head>
    <body>
        <h1>500 - Server Explosion!</h1>
        <hr/>
        <p>The server erupts in a shower of gore, killing your request instantly. All other servers are so disturbed that they lose 1 survival.</p>
        <hr/>
        <p>$msg</p>
        <p>$params</p>
        <hr/>
        <p>Please report errors and issues at <a href="https://github.com/toconnell/kdm-manager/issues">https://github.com/toconnell/kdm-manager/issues</a></p>
        <p>Use the information below to report this error:</p>
        <hr/>
        <p>%s</p>
        <h2>Traceback:</h2>
        $exception\n""" % (basic_http_header, settings.get("application","title"), datetime.now()))

    start_head = """<!DOCTYPE html>\n<html>
    <head>
        <meta charset="UTF-8">
        <meta name="theme-color" content="#000000">
        <title>%s</title>
        <link rel="stylesheet" type="text/css" href="/media/style.css">
        <link rel="stylesheet" type="text/css" href="/media/z-index.css">
    """ % settings.get("application","title")

    close_body = """\n
    </div><!-- container -->
    </body>
    </html>
    <script type="text/javascript">
        // kill the spinner, just in case it hasn't been killed
        //hideFullPageLoader();
    </script>
    """
    saved_dialog = """\n
    <div id="saved_dialog" class="saved_dialog_frame" style="">
        <div class="kd_blue saved_dialog_inner">
            <span class="saved_dialog_cap">S</span>
            Saved!
        </div>
    </div>

    <div id="error_dialog" class="saved_dialog_frame" style="">
        <div class="kd_alert_no_exclaim saved_dialog_inner">
            <span class="error_dialog_cap">E</span>
            <b>An Error Occurred!</b>
        </div>
    </div>
    \n"""

    full_page_loader = """\n
    <div id="fullPageLoader" class="full_page_loading_spinner">
        <img class="full_page_loading_spinner" src="/media/loading_io.gif">
    </div>
    \n"""
    mobile_hr = '<hr class="mobile_only"/>'
    dashboard_alert = Template("""\n\
    <div class="dashboard_alert_spacer"></div>
    <div class="kd_alert dashboard_alert">
    $msg
    </div>
    \n""")


    burger_top_level_button = Template("""\n
    <form method="POST" action="/"><input type="hidden" name="change_view" value="$view"/>
    <button class="sidenav_top_level"> $link_text </button>
    </form>
    \n""")
    burger_new_settlement = '<div id="mySidenav" class="sidenav">' + burger_top_level_button.safe_substitute(link_text = "Return to Dashboard", view = "dashboard") + '</div><!-- mySidenav -->' + '<button id="floating_dashboard_button" class="gradient_silver" onclick="openNav()"> &#9776; </button>'
    burger_signout_button = Template("""\n
    <form id="logout" method="POST" action="/">
    <input type="hidden" name="remove_session" value="$session_id"/>
    <input type="hidden" name="login" value="$login"/>
    <button>$login<br/>SIGN OUT</button>
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
        <div class="modal-content timeline_gradient">
            <span class="closeModal" onclick="closeModal('modalReportError')">×</span>
            <div class="report_error_container">
                <h3>Report an Issue or Error</h3>
                <p>http://kdm-manager.com is a work in progress and is under active development!</p>
                <p>If you identify an issue, error or problem with the application, whether a simple typo, a presentation problem or otherwise, there are a number of ways to report it.</p>
                <p>To rapidly submit an issue via email, use the form below:
                <div class="error_form">
                    <form method="POST" action="/">
                     <input type="hidden" name="error_report" value="from_web">
                     <textarea class="report_error" name="body" placeholder="Describe your issue here"></textarea>
                     <input type="submit" class="kd_alert_no_exclaim" value ="submit"/>
                    </form>
                </div>
                </p>
                <p>Please note that until KD:M 1.5 and/or AKD:M are released, the Manager will continues to use <u>all available 1.4n rules plus any errata or corrections from the FAQ</u> on <a href="http://kingdomdeath.com" target="top">http://kingdomdeath.com</a>.</p>
                <p><b>General Comments/Questions:</b> use <a href="http://kdm-manager.blogspot.com//" target="top">the Development blog at blog.kdm-manager.com</a> to review change logs, make comments and ask questions about the manager.</p>
                <p><b>Source code and development questions:</b> if you're interested, you can clone/download and review the <a href="https://github.com/toconnell/kdm-manager" target="top">source code for the manager</a> from GitHub. <a href="https://github.com/toconnell/kdm-manager/wiki" target="top">The development wiki</a> also has some good stuff.</p>
                <p><b>Issues and Errors:</b> feel free to mention any issues/errors on the blog comments or, if you use GitHub, you may also submit issues to <a href="https://github.com/toconnell/kdm-manager/issues" target="top">the project's issues tracker</a>.</p>
            </div>
        </div><!-- modal-content -->
    </div> <!-- modalReportError -->

    \n"""
    error_report_email = Template("""\n\
    Greetings!<br/><br/>&ensp;User $user_email [$user_id] has submitted an error report!<br/><br/>The report goes as follows:<hr/>$body<hr/>&ensp;...and that's it. Good luck!<br/><br/>Your friend,<br/>&ensp; meta.error_report_email
    \n""")
    view_render_fail_email = Template("""\n
    Greetings!<br/><br/>&ensp;User $user_email [$user_id] was logged out of the webapp instance on <b>$hostname</b> due to a render failure at $error_time.<br/><br/>&ensp;The traceback from the exception was this:<hr/><code>$exception</code><hr/>&ensp;The session object was this:<hr/><code>$session_obj</code><hr/>&ensp;Good hunting!<br/><br/>Your friend,<br/>meta.view_render_fail_email()
    \n""")
    safari_warning = Template("""\n\
    <div class="safari_warning">
    <p>It looks like you're using Safari $vers. Unfortunately, the current version
    of this application uses some presentation elements that are not fully
    supported by your browser.</p>
    <p>If you experience disruptive presentation and/or functionality issues while
    using the manager, <a href="https://www.google.com/chrome/browser"
    target="top">Chrome</a> is fully supported on Windows and OSX.</p>
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
    elif session_object.Settlement is None and session_object.session is None:
        return no_burger_string
    elif session_object.Settlement is None and session_object.session is not None:
        if session_object.session["current_view"] == "new_settlement":
            pass
        else:
            return no_burger_string
    elif not hasattr(session_object.Settlement, "settlement"):
        return no_burger_string
    elif session_object.Settlement.settlement is None:
        return no_burger_string

    view = session_object.session["current_view"]

    if view not in ["view_campaign","view_settlement","view_survivor","new_survivor","new_settlement"]:
        return "\n<!-- no burger in '%s' view -->\n\n" % view

    signout_button = meta.burger_signout_button.safe_substitute(
        session_id=session_object.session["_id"],
        login=session_object.User.user["login"],
    )

    # first, create the mini-burger for the new_settlement view
    if view == "new_settlement":
        burger_panel = Template("""\n
            <!-- $current_view burger -->

            <div id="mySidenav" class="sidenav">
              $dash
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
            dash=meta.burger_top_level_button.safe_substitute(
                link_text = "Return to Dashboard",
                view = "dashboard",
            ),
            report_error=meta.report_error_button,
            signout=signout_button,
        )

        return output


    # now, create a settlement burger.
    # first, set defaults:


    new_settlement = meta.burger_top_level_button.safe_substitute(
        link_text = "+ New Settlement",
        view = "new_settlement",
    )

    # create a list of action buttons based on view/session info
    actions = '<button id="newSurvivorButton" class="sidenav_button">+ Create New Survivor</button>'
    if session_object.User.is_settlement_admin():
        actions += '<button id="bulkAddOpenerButton" class="sidenav_button">+ Create Multiple Survivors</button>'
        actions += '<button id="bulkExpansionsManagerButton" class="sidenav_button"> Expansion Content</button>'
    if view in ["view_campaign","view_survivor"]:
        if session_object.User.is_settlement_admin():
            actions += meta.burger_change_view_button.safe_substitute(
                link_text = "Settlement Sheet",
                target_view = "view_settlement",
                settlement_id = session_object.session["current_settlement"],
            )
    if view in ["view_settlement","view_survivor"]:
        actions += meta.burger_change_view_button.safe_substitute(
            link_text = "Campaign Summary",
            target_view = "view_campaign",
            settlement_id = session_object.session["current_settlement"]
        )

    if view in ["view_survivor","view_campaign","view_settlement"]:
        actions += '<button id="timelineOpenerButton" class="sidenav_button">Timeline</button>'
        actions += '<button id="settlementNotesOpenerButton" class="sidenav_button">Notes and Players</button>'


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
        action_map=actions,
        departing_links=departing,
        favorite_links=favorites,
    )

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
    <!-- android mobile desktop/app stuff -->
    <link rel="manifest" href="/manifest.json">

    <!-- fucking jquery's dumb ass -->
    <script src="http://ajax.googleapis.com/ajax/libs/jquery/1.7/jquery.js"></script> 

    <!-- angular app -->
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.5.4/angular.min.js"></script>
    <script src="http://code.angularjs.org/1.5.3/angular-route.min.js"></script> 

    <script src="/media/kdmManager.js"></script>
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

    output += """\n
    <div
        id="container"
        onclick="closeNav()"
        ng-app="kdmManager"
        ng-controller="rootController"
    >
    \n"""

    output += view_html
    output += meta.report_error_div
    output += meta.close_body

    # all html we render gets this template substitution
    output = Template(output).safe_substitute(
            api_url = api.get_api_url(),
    )

    print(output.encode('utf8'))

    sys.exit(0)     # this seems redundant, but it's necessary in case we want
                    #   to call a render() in the middle of a load, e.g. to just
                    #   finish whatever we're doing and show a page.
