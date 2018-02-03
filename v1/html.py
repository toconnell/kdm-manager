# coding=utf-8
#!/usr/bin/env python

#   standard
from datetime import datetime, timedelta
from string import Template
import sys

#   custom
import admin
import api
from session import Session
from utils import load_settings, mdb, get_logger, get_latest_update_string, template_file_to_str

settings = load_settings()
logger = get_logger()

user_error_msg = Template("""
    <div id="user_error_msg" class="$err_class" onclick="hide('user_error_msg')">$err_msg</div>
    """)


class ui:
    game_asset_select_top = Template("""\n\
    <select
        class="$select_class"
        name="$operation$name"
        ng_model="$ng_model"
        ng_change="$ng_change"
        onchange="$on_change"
    >
      <option selected disabled hidden value="">$operation_pretty $name_pretty</option>
    """)
    game_asset_select_row = Template('\t  <option value="$asset">$asset</option>\n')
    game_asset_select_bot = '    </select>\n'
    text_input = Template('\t  <input onchange="this.form.submit()" type="text" class="full_width" name="$name" placeholder="$placeholder_text"/>')



class dashboard:
    # flash
    campaign_flash = '<img class="dashboard_icon" src="/media/icons/campaign.png"/> '

    #
    #   ANGULARJS dashboard components!
    #

    angular_app = Template("""\
<script src="/media/dashboard.js?v=$application_version"></script>
<div
    id="dashboardWelcomeModal"
    class="modal dashboard_welcome_modal hidden"
    ng-class="{true: 'visible', false: 'hidden'}[user.dashboard.settlements.length == 0]"
    onclick="showHide('dashboardWelcomeModal')"
    ng-init="setView('dashboard')"
>
    <p>Welcome to <b>http://kdm-manager.com</b>!</p>
    <p><b>The Manager</b> is an interactive webapp intended to make it
    easier to manage and share your Kingdom Death: <i>Monster</i> campaigns.</p>
    <p>&nbsp; </p>
    <p>This application is fan-maintained and <b>is not</b> supported by or
    affiliated with Kingdom Death.</p>
    <p>&nbsp; </p>
    <p>To get started, you will have to <b>create a new settlement</b>. Once your new
    settlement is created, you will be shown a <b>campaign summary</b>, which is
    is like a dashboard for your campaign.</p>
    <p>From the <b>campaign summary</b>, you can use the controls in the upper-left
    corner to add new survivors, view your settlement's "sheet" and add/remove
    expansion content.</p>
    <p>In order to add other players to your campaign, all you have to do is
    navigate to an individual survivor's "sheet" and change that survivor's email
    address to the email address of another registered user of this site.</p>
    <p>Changes to settlement and survivor sheets are always saved
    automatically.</p>
    <p>&nbsp; </p>
    <p>Finally, this application is <u>under active development</u> and problems <b>will</b>
    occur! Please use the controls within the app to report errors/issues.</p>
    <p>&nbsp; </p>
    <div class="kd_alert_no_exclaim">Click or tap anywhere to get started!</div>
</div>

<div
    id="dashboardControlElement"
    ng-controller="dashboardController"
    ng-init="
        initializeUser('$user_id', 'dashboard', '$api_url');
        showInitDash();
        setLatestChangeLog();
        loadExpansionAssets();
    "
>

    <img class="dashboard_bg" src="/media/tree_logo_shadow.png"> <!-- DASHBOARD LOGO ART -->

    <div class="dashboard_menu">
        <h2
            class="clickable system_primary dashboard_rollup"
            ng-click="showHide('system_div'); toggleArrow('user_preference_arrow');"
            ng-init="scratch.user_preference_arrow = false"
        >
            <img class="dashboard_icon" src="/media/icons/system.png"/>
            System
            <span class="dashboard_rollup_arrow" ng-if="scratch.user_preference_arrow == true">
                &#x25B2;
            </span>
            <span class="dashboard_rollup_arrow" ng-if="scratch.user_preference_arrow == false">
                &#x25BC;
            </span>
        </h2>

        <div id="system_div" class="dashboard_accordion system_secondary hidden">

            <h3 class="system_preference_user_login"> {{user.user.login }} </h3>
            <div class="preferences_sub_block preferences_sign_out">
                <form method="POST" action="/">
                    <input type="hidden" name="remove_session" value="{{user.user.current_session.$oid}}"/>
                    <input type="hidden" name="login" value="{{user.user.login}}"/>
                    <button>SIGN OUT</button>
                </form>
            </div>
            <div class="dashboard_preferences_container user_info">
                <p>Registered user for {{user.user.age}}.</p>
                <p ng-if="user.user.subscriber.level < 1">
                    <a href="https://thelaborinvain-2.myshopify.com/" target="top">
                        Support the Manager! Buy a lifetime subscription for $1!
                    </a>
                </p>
                <p ng-if="user.user.subscriber.level > 0">Subscription level: <b>{{user.user.subscriber.desc}}.</b>
                <p ng-if="user.user.subscriber.level > 0">Subscriber for <b>{{user.user.subscriber.age}}.</b>
                <p ng-if="user.user.subscriber.beta == true" class="maroon_text">
                    Beta warning!
                </p>
                <div class="preferences_sub_block preferences_change_pw">
                <p><b>Change Password!</b></p>
                    <input
                        type="password"
                        ng-model="scratch.password"
                        placeholder="new password"
                        ng-focus="scratch.saved_password = undefined"/><br/>
                    <input type="password" ng-model="scratch.password_again" placeholder="new password (again)"><br/>
                    <button
                        ng-click="updatePassword()"
                        class="kd_alert_no_exclaim change_pw"
                        ng-if="scratch.password != undefined && scratch.password == scratch.password_again"
                    >
                        Change Password
                    </button>
                    <p ng-if="scratch.saved_password">Password updated! <b>Signing out...</b></p>
                </div>
            </div> <!-- user info -->

            <div ng-if="user.user.preferences.beta == true" class="dashboard_user_collection_container">
                <h3>&beta; Collection</h3>
                <p>Use the checkboxes below to record which
                <i>Monster</i> expansions are in your personal collection!</p>

                <h4 class="user_collection">- Expansions - </h4>
                <div
                    class="dashboard_user_expansions_repeater clickable"
                    ng-repeat="(handle, expansion) in expansions"
                    ng-click="toggleUserExpansion(handle)"
                >
                    <div
                        class="special_attribute_checkbox"
                        ng-class="{active: user.user.collection.expansions.indexOf(handle) != -1}"
                    ></div>
                    <div
                        class="special_attribute_text"
                        ng-class="{active: user.user.collection.expansions.indexOf(handle) != -1}"
                    >
                        {{expansion.name}}
                        <div ng-if="expansion.desc != undefined" class="metrophobic">
                            {{expansion.desc}}
                        </div>
                    </div>
                </div><!-- expansion repeater -->

            </div>

            <h3> Manage Preferences</h3>
            <div class="dashboard_preferences_container">
                <p>Use the controls below to update application-wide preferences.
                These settings will affect all of your settlements and survivors!</p>

                <div class="dashboard_preference_block_group" ng-repeat="group in user.preferences">
                    <h2>{{group.name}}</h2>

                    <div
                        class="dashboard_preference"
                        ng-repeat="pref in group.items"
                        ng-if="user.user.subscriber.level >= pref.patron_level"
                    >
                        <p class="dashboard_preference_description">
                            {{pref.desc}}
                        </p>
                        <div class="dashboard_preference_elections_container">
                            <input
                                id="{{pref.handle}}_affirmative"
                                class="kd_css_checkbox kd_radio_option"
                                style="display: none"
                                type="radio"
                                ng-checked="pref.value == true"
                                ng-click="setPref(pref,true)"
                            />
                            <label for="{{pref.handle}}_affirmative">
                                {{pref.affirmative}}
                            </label>

                            <input
                                id="{{pref.handle}}_negative"
                                class="kd_css_checkbox kd_radio_option"
                                style="display: none"
                                type="radio"
                                ng-checked="pref.value == false"
                                ng-click="setPref(pref,false)"
                            />
                            <label for="{{pref.handle}}_negative">
                                {{pref.negative}}
                            </label>
                        </div> <!-- dashboar_preference_elections_container -->
                    </div><!-- dashboard_preference -->
                </div><!-- dashboard_preference_block_group -->
            </div> <!-- dashboard_preferences -->
        </div> <!-- system_div -->
    </div> <!-- preferencesContainerElement -->



    <div class="dashboard_menu">
        <h2
            class="clickable campaign_summary_gradient dashboard_rollup"
            ng-click="showHide('campaign_div'); toggleArrow('campaigns_arrow')"
            ng-init="scratch.campaigns_arrow = true"
        >
            <img class="dashboard_icon" src="/media/icons/campaign.png"/>
            Campaigns
            <span class="dashboard_rollup_arrow" ng-if="scratch.campaigns_arrow == true">
                &#x25B2;
            </span>
            <span class="dashboard_rollup_arrow" ng-if="scratch.campaigns_arrow == false">
                &#x25BC;
            </span>
        </h2>

        <div
            id="campaign_div"
            class="dashboard_accordion campaign_summary_gradient"
        >
            <p class="panel_top_tooltip">Games you are currently playing.</p>
            <p
                class="panel_top_tooltip"
                ng-if="user.user.subscriber.level < 1"
            > Campaigns created by non-subscribers are automatically removed after six months.
                <a href="https://thelaborinvain-2.myshopify.com/" target="top">
                    Purchase a lifetime subscription to the Manager</a>
                to store your campaigns permanently!
            </p> <!-- subscribers alert -->

            <div class="dashboard_button_list">

                <form
                    ng-repeat="s in campaigns | orderBy: '-'"
                    ng-if="s.sheet.abandoned == undefined"
                    method="POST"
                >
                    <input type="hidden" name="view_campaign" value="{{s.sheet._id.$oid}}" />
                    <button
                        class="kd_dying_lantern dashboard_settlement_list_settlement_button"
                        onclick="showFullPageLoader(); this.form.submit()"
                    >
                        <b>{{s.sheet.name}}</b>
                        <br/><i>{{s.sheet.campaign_pretty}}</i>
                        <ul class="dashboard_settlement_list_settlement_attribs">
                            <li ng-if="s.meta != undefined && s.meta.creator_email != user_login"><i>Created by:</i> {{s.meta.creator_email}}</li>
                            <li ng-if="s.meta != undefined"><i>Started:</i> {{s.meta.age}} ago</li>
                            <li><i>LY:</i> {{s.sheet.lantern_year}} &nbsp; <i>Survivors:</i> {{s.sheet.population}}</li>
                            <li ng-if="s.meta.player_email_list.length >= 2">
                                <i>Players:</i> {{s.meta.player_email_list.join(', ')}}
                            </li>
                        </ul>
                    </button>
                </form>

                <div
                    id="dashboardCampaignsLoader"
                    class="dashboard_settlement_loader"
                    ng-if="campaigns.length < user.dashboard.campaigns.length"
                >
                    <img
                        src="/media/loading_lantern.gif"
                        alt="Retrieving settlements..."
                    /> Retrieving campaigns...
                </div>


            </div>
        </div>
    </div>

    <div
        id="all_settlements_panel"
        class="dashboard_menu all_settlements_panel"
    >
        <h2
            class="clickable settlement_sheet_gradient dashboard_rollup"
            ng-click="showHide('all_settlements_div'); toggleArrow('settlements_arrow')"
            ng-init="scratch.settlements_arrow = false"
        >
            <img class="dashboard_icon" src="/media/icons/settlement.png"/>
            Settlements
            <span class="dashboard_rollup_arrow" ng-if="scratch.settlements_arrow == true">
                &#x25B2;
            </span>
            <span class="dashboard_rollup_arrow" ng-if="scratch.settlements_arrow == false">
                &#x25BC;
            </span>
        </h2>

        <div
            id="all_settlements_div"
            class="dashboard_accordion settlement_sheet_gradient hidden"
        >
            <p class="panel_top_tooltip">Manage settlements you have created.</p>
            <p
                class="panel_top_tooltip"
                ng-if="user.user.subscriber.level < 1"
            > Non-subscriber users may create up to three settlements:
                <a href="https://thelaborinvain-2.myshopify.com/" target="top">
                    purchase a lifetime subscription to the Manager</a>
                to create an unlimited number of settlements!
            </p> <!-- subscribers alert -->

            <div class="dashboard_button_list">
                <form
                    method="POST"
                    action=""
                    ng-if="user.dashboard.settlements.length < 3 || user.user.subscriber.level > 0"
                >
                    <input type="hidden" name="change_view" value="new_settlement" />
                    <button class="kd_blue" onclick="showFullPageLoader()">+ Create New Settlement</button>
                </form>

                <form
                    ng-repeat="s in settlements"
                    method="POST"
                >
                    <input type="hidden" name="view_settlement" value="{{s.sheet._id.$oid}}" />
                    <button
                        class="kd_dying_lantern dashboard_settlement_list_settlement_button"
                        onclick="showFullPageLoader(); this.form.submit()"
                    >
                        <b>{{s.sheet.name}}</b>
                        <span class="maroon_text" ng-if="s.sheet.abandoned != undefined">[ABANDONED]</span>
                        <br/><i>{{s.campaign_pretty}}</i>
                        <ul class="dashboard_settlement_list_settlement_attribs">
                            <li ng-if="s.meta != undefined"><i>Created:</i> {{s.meta.age}} ago</li>
                            <li>
                                <span ng-if="s.sheet.expansions.length > 0">
                                    {{s.sheet.expansions.length}} expansions
                                </span>
                                <span ng-if="s.sheet.expansions.length > 0 && s.meta != undefined">
                                    /
                                </span>
                                <span ng-if="s.meta != undefined">
                                    {{s.meta.player_email_list.length}} player(s)
                                </span>
                            </li>
                            <li><i>LY:</i> {{s.sheet.lantern_year}}</li>
                            <li><i>Population:</i> {{s.sheet.population}}</li>
                            <li><i>Deaths:</i> {{s.sheet.death_count}}</li>
                            <li ng-if="s.meta.player_email_list.length >= 2"><i>Admins:</i> {{s.sheet.admins.join(', ')}}</li>
                            <li ng-if="s.meta.player_email_list.length >= 2"><i>Players:</i> {{s.meta.player_email_list.join(', ')}}</li>
                        </ul>
                    </button>
                </form>

                <div
                    id="dashboardSettlementsLoader"
                    class="dashboard_settlement_loader"
                    ng-if="settlements.length < user.dashboard.settlements.length"
                >
                    <img
                        src="/media/loading_lantern.gif"
                        alt="Retrieving settlements..."
                    /> Retrieving settlements...
                </div>


            </div> <!-- dashboard_button_list -->

        </div> <!-- all_settlements_div -->
    </div> <!-- all_settlements_panel -->

    <div
        id="world_container"
        class="dashboard_menu world_panel"
    >

        <h2
            class="clickable world_primary dashboard_rollup"
            ng-click="showHide('world_detail_div'); toggleArrow('world_arrow')"
            ng-init="scratch.world_arrow = false"
        >
            <font class="kdm_font_hit_locations dashboard_kdm_font white">g</font>
            <font class="white">World</font>
            <span class="white dashboard_rollup_arrow" ng-if="scratch.world_arrow == true">
                &#x25B2;
            </span>
            <span class="white dashboard_rollup_arrow" ng-if="scratch.world_arrow == false">
                &#x25BC;
            </span>
        </h2>

        <div id="world_detail_div" class="dashboard_accordion world_secondary hidden world_container">

            <center ng-if="world == undefined">
                <br/>
                <img src="/media/loading_lantern.gif"><br/>
                <span class="white">Retrieving World data...</span>
                <br/>
            </center>

            <div class="world_panel_basic_box" ng-if="world != undefined">
                <p>
                    <font class="green_text"> <b>{{world.active_settlements.value}} </b></font> Settlements are holding fast.
                    <font class="maroon_text"><b> {{world.abandoned_or_removed_settlements.value}} </b></font> have been abandoned.
                </p>
                <p>
                    <font class="green_text"> <b>{{world.live_survivors.value}}</b> </font> Survivors are alive and fighting.
                    <font class="maroon_text"><b>{{world.dead_survivors.value}}</b></font> have perished.</p>
            </div>

            <div class="world_panel_basic_box" ng-if="world != undefined">
                <h3>Settlement Statistics</h3>

                <p>{{world.total_multiplayer_settlements.name}}: <b>{{world.total_multiplayer_settlements.value}}</b></p>
                <p>{{world.new_settlements_last_30.name}}: <b>{{world.new_settlements_last_30.value}}</b></p>

                <table>
                    <tr><th colspan="2">{{world.top_settlement_names.name}}</th></tr>
                    <tr ng-repeat="row in world.top_settlement_names.value" ng-class-even="'zebra'">
                        <td>{{row.name}}</td><td class="int_value">{{row.count}}</td>
                    </tr>
                </table>

                <table>
                    <tr><th colspan="2">Active Campaigns</th></tr>
                    <tr ng-repeat="(name,count) in world.settlement_popularity_contest_campaigns.value" ng-class-even="'zebra'">
                        <td>{{name}}</td> <td class="int_value">{{count}}</td>
                    </tr>
                </table>

                <table>
                    <tr><th colspan="2">Campaigns w/ Expansion Content</th></tr>
                    <tr ng-repeat="e in world.settlement_popularity_contest_expansions.value" ng-class-even="'zebra'">
                        <td>{{e.name}}</td> <td class="int_value">{{e.count}}</td>
                    </tr>
                </table>

                <table>
                    <tr><th colspan="2">Settlement Averages</th></tr>
                    <tr><td>Lantern Year </td><td class="int_value">{{world.avg_ly.value}}</td></tr>
                    <tr class="zebra"><td>Innovation Count </td><td>{{world.avg_innovations.value}}</td></tr>
                    <tr><td>Expansions</td><td> {{world.avg_expansions.value}}</td></tr>
                    <tr class="zebra"><td>Defeated Monsters</td><td> {{world.avg_defeated_monsters.value}}</td></tr>
                    <tr><td>Items in Storage</td> <td>{{world.avg_storage.value}}</td></tr>
                    <tr class="zebra"><td>Milestone Story Events</td><td> {{world.avg_milestones.value}}</td></tr>
                    <tr><td>Lost Settlements </td><td>{{world.avg_lost_settlements.value}}</td></tr>
                </table>

                <table><tr><th>Principle selection rates</th></tr></table>
                <div ng-repeat="(principle, selections) in world.principle_selection_rates.value">
                    <table>
                        <tr><th colspan="2" class="principle">{{principle}}</th></tr>
                        <tr ng-repeat="option in selections.options" ng-class-even="'zebra'">
                            <td>{{option}}</td>
                            <td class="int_value">{{selections[option].percentage}}%</td>
                        </tr>
                    </table>
                </div>

                <table>
                    <tr><th colspan="2">Top Innovations</th></tr>
                    <tr ng-repeat="row in world.top_innovations.value" ng-class-even="'zebra'">
                        <td>{{row.name}}</td><td class="int_value">{{row.count}}</td>
                    </tr>
                </table>

                <table>
                    <tr><th>Survival Limit stats</th></tr>
                    <tr><td>Average Survival Limit:</td><td class="int_value">{{world.avg_survival_limit.value}}</td></tr>
                    <tr class="zebra"><td>Max Survival Limit:</td><td>{{world.max_survival_limit.value}}</td></tr>
                </table>


            </div>

            <div class="world_panel_basic_box" ng-if="world != undefined">
                <h3>Latest Settlement</h3>
                <table>
                    <tr><td colspan="2"><b>{{world.latest_settlement.value.name}}</b></td></tr>
                    <tr><td colspan="2"><i>{{world.latest_settlement.value.campaign}}</i></td></tr>
                    <tr ng-if="world.latest_settlement.value.expansions != null">
                        <td colspan="2">{{world.latest_settlement.value.expansions}}</td>
                    </tr>
                    <tr><td>Created</td><td>{{world.latest_settlement.value.age}} ago</td></tr>
                    <tr class="zebra"><td>Players</td><td>{{world.latest_settlement.value.player_count}}</td></tr>
                    <tr><td>Population</td><td>{{world.latest_settlement.value.population}}</td></tr>
                    <tr class="zebra"><td>Death count</td><td>{{world.latest_settlement.value.death_count}}</td></tr>
                </table>

            </div>

            <div class="world_panel_basic_box" ng-if="world != undefined">
                <h3>Survivor Statistics</h3>

                <table>
                    <tr><th>Population and death stats</th></tr>
                    <tr><td>Average Population</td><td class="int_value">{{world.avg_pop.value}}</td></tr>
                    <tr class="zebra"><td>Max Population</td><td>{{world.max_pop.value}}</td></tr>
                    <tr><td>Average Death count</td><td> {{world.avg_death_count.value}}</td></tr>
                    <tr class="zebra"><td>Max Death Count</td> <td>{{world.max_death_count.value}}</td></tr>
                </table>

                <table>
                    <tr><th colspan="2">Top Survivor names</th></tr>
                    <tr ng-repeat="row in world.top_survivor_names.value" ng-class-even="'zebra'">
                        <td>{{row.name}}</td> <td class="int_value">{{row.count}}</td>
                    </tr>
                </table>

                <table>
                    <tr><th colspan="2">Top Causes of Death</th></tr>
                    <tr ng-repeat="row in world.top_causes_of_death.value" ng-class-even="'zebra'">
                        <td>{{row.cause_of_death}}</td> <td class="int_value">{{row.count}}</td>
                    </tr>
                </table>

                <table>
                    <tr><th colspan="2">Living survivor averages</th></tr>
                    <tr><td>Hunt XP</td><td>{{world.avg_hunt_xp.value}}</td></tr>
                    <tr class="zebra"><td>Insanity</td><td class="int_value">{{world.avg_insanity.value}}</td></tr>
                    <tr><td>Courage</td><td>{{world.avg_courage.value}}</td></tr>
                    <tr class="zebra"><td>Fighting Arts</td><td>{{world.avg_fighting_arts.value}}</td></tr>
                    <tr><td>Understanding</td><td>{{world.avg_understanding.value}}</td></tr>
                    <tr class="zebra"><td>Disorders</td><td>{{world.avg_disorders.value}}</td></tr>
                    <tr><td>Abilities/Impairments</td><td>{{world.avg_abilities.value}}</td></tr>
                </table>

            </div>

            <div class="world_panel_basic_box" ng-if="world != undefined">
                <h3>Latest Survivor</h3>
                <table>
                    <tr ng-if="world.latest_survivor.value.avatar != undefined">
                        <td colspan="2" class="world_panel_avatar_cell">
                            <img
                                class="world_panel_avatar"
                                ng-src="/get_image?id={{world.latest_survivor.value.avatar.$oid}}"
                                title="{{world.latest_survivor.value.name}}"
                            />
                    </tr>
                    <tr><td colspan="2"><b>{{world.latest_survivor.value.name}}</b> [{{world.latest_survivor.value.sex}}] of </td></tr>
                    <tr><td colspan="2"><i>{{world.latest_survivor.value.settlement_name}}</i></td></tr>
                    <tr ng-if="world.latest_settlement.value.epithets != null">
                        <td colspan="2">{{world.latest_survivor.value.epithets}}</td>
                    </tr>
                    <tr><td>Created</td><td>{{world.latest_survivor.value.age}} ago</td></tr>
                    <tr class="zebra"><td>Joined in LY</td><td>{{world.latest_survivor.value.born_in_ly}}</td></tr>
                    <tr><td>Hunt XP</td><td>{{world.latest_survivor.value.hunt_xp}}</td></tr>
                    <tr class="zebra"><td>Insanity</td><td>{{world.latest_survivor.value.Insanity}}</td></tr>
                    <tr><td>Courage</td><td>{{world.latest_survivor.value.Understanding}}</td></tr>
                    <tr class="zebra"><td>Understanding</td><td>{{world.latest_survivor.value.Insanity}}</td></tr>
                </table>

            </div>

            <div class="world_panel_basic_box" ng-if="world != undefined">
                <h3>Latest Fatality</h3>
                <table>
                    <tr ng-if="world.latest_fatality.value.avatar != undefined">
                        <td colspan="2" class="world_panel_avatar_cell">
                            <img
                                class="world_panel_avatar"
                                ng-src="/get_image?id={{world.latest_fatality.value.avatar.$oid}}"
                                title="{{world.latest_fatality.value.name}}"
                            />
                    </tr>
                    <tr><td colspan="2"><b>{{world.latest_fatality.value.name}}</b> [{{world.latest_fatality.value.sex}}] of </td></tr>
                    <tr><td colspan="2"><i>{{world.latest_fatality.value.settlement_name}}</i></td></tr>
                    <tr><td colspan="2">Cause of Death:</td></tr>
                    <tr><td colspan="2">&ensp; <font class="maroon_text"><b>{{world.latest_fatality.value.cause_of_death}}</b></font></td></tr>
                    <tr ng-if="world.latest_settlement.value.epithets != null">
                        <td colspan="2">{{world.latest_fatality.value.epithets}}</td>
                    </tr>
                    <tr><td>Created</td><td>{{world.latest_fatality.value.age}} ago</td></tr>
                    <tr class="zebra"><td>Died in LY</td><td>{{world.latest_fatality.value.died_in}}</td></tr>
                    <tr><td>Hunt XP</td><td>{{world.latest_fatality.value.hunt_xp}}</td></tr>
                    <tr class="zebra"><td>Insanity</td><td>{{world.latest_fatality.value.Insanity}}</td></tr>
                    <tr><td>Courage</td><td>{{world.latest_fatality.value.Understanding}}</td></tr>
                    <tr class="zebra"><td>Understanding</td><td>{{world.latest_fatality.value.Insanity}}</td></tr>
                </table>

            </div> <!-- latest fatality -->

            <div class="world_panel_basic_box" ng-if="world != undefined">
                <h3>Latest Kill</h3>
                <p><b>{{world.latest_kill.value.raw_name}}</b></p>
                <p>Defeated by the survivors of <b>{{world.latest_kill.value.settlement_name}}</b> on {{world.latest_kill.value.killed_date}} at {{world.latest_kill.value.killed_time}}.</p>
            </div>

            <div class="world_panel_basic_box" ng-if="world != undefined">
                <h3>{{world.killboard.name}}</h3>
                <table ng-repeat="(type,board) in world.killboard.value">
                    <tr><th class="principle capitalize" colspan="2">{{type}}</th></tr>
                    <tr ng-repeat="row in board" ng-class-even="'zebra'">
                        <td>{{row.name}}</td> <td class="int_value">{{row.count}}</td>
                    </tr>
                </table>
            </div>

            <div class="world_panel_basic_box" ng-if="world != undefined">
                <h3>User Statistics</h3>
                <p> <b>{{world.total_users.value}}</b> users are registered.</p>
                <p> <b>{{world.recent_sessions.value}}</b> users have managed campaigns in the last 12 hours.</p>
                <p> <b>{{world.total_users_last_30.value}}</b> users have managed campaigns in the last 30 days.</p>
                <p> <b>{{world.new_users_last_30.value}}</b> new users have registered in the last 30 days.</p>

                <table>
                    <tr><th colspan="2">Per user averages</th></tr>
                    <tr><td>Survivors</td><td class="int_value">{{world.avg_user_survivors.value}}</td></tr>
                    <tr class="zebra"><td>Settlements</td><td>{{world.avg_user_settlements.value}}</td></tr>
                    <tr><td>Avatars</td><td>{{world.avg_user_avatars.value}}</td></tr>
                </table>
            </div> <!-- user stats -->

        </div> <!-- world_detail_div -->

    </div> <!-- dashboard_menu 'World'-->

        <div
            class="dashboard_menu"
        >
            <h2
                class="clickable about_primary dashboard_rollup"
                ng-click="showHide('about_div'); toggleArrow('about_arrow')"
                ng-init="scratch.about_arrow=false"
            >
                <font class="kdm_font dashboard_kdm_font">g</font> About
                <span class="dashboard_rollup_arrow" ng-if="scratch.about_arrow == true">
                    &#x25B2;
                </span>
                <span class="dashboard_rollup_arrow" ng-if="scratch.about_arrow == false">
                    &#x25BC;
                </span>
            </h2>

            <div
                id="about_div"
                class="dashboard_accordion about_secondary hidden"
            >

                <p class="title">
                    <b>KD:M Manager! Production release {{user.meta.webapp.release}} (<a href="http://api.thewatcher.io">KDM API</a> release version {{user.meta.api.version}}).
                    </b>
                </p>

		<hr/>

		<p>About:</p>
		<ul>
                    <li>This application, which is called <i>kdm-manager.com</i>, or simply, <i>the Manager</i>, is an interactive campaign management tool for use with <i><a href="https://shop.kingdomdeath.com" target="top">Monster</a></i>, by <a href="http://kingdomdeath.com" target="top">Kingdom Death</a>.
                    </li>
                </ul>

                <p>Important Information:</p>
                <ul>
                    <li><b>This application is not developed, maintained, authorized or in any other way supported by or affiliated with <a href="http://kingdomdeath.com" target="top">Kingdom Death</a>.</b></li>
                    <li>This application is currently under active development and is running in debug mode!<li>
                    <li>Among other things, this means not only that <i>errors can and will occur</i>, but also that <i>features may be added or removed without notice</i> and <i>presentation elements are subject to change</i>.</li>
                    <li>Users' email addresses and other information are used only for the purposes of developing and maintaining this application and are never shared, published or distributed.</li>
                </ul>

                <p>Release Information:</p>
                <ul>
                    <li>Release {{user.meta.webapp.release}} of the Manager went into production on {{latest_blog_post.published}}. <a target="top" href="{{latest_blog_post.url}}">View change log</a>.</li>
                    <li>v1.7.0, the first production release of the Manager, went live {{user.meta.webapp.age}} ago on 2015-11-29.</li>
                    <li>For detailed release information, including complete notes and updates for each production release, please check the development blog at <a href="http://blog.kdm-manager.com" target="top">blog.kdm-manager.com</a>.</li>
                </ul>

                <hr/>

                <p>Thanks for using the Manager!</p>

            </div> <!-- about_div -->

        </div> <!-- dashboard_menu 'About' -->

        <div
            id="dashboardTwitter"
            class="dashboard_twitter_container modal hidden"
        >
            <h3>Updates!</h3>
            <div class="dashboard_updates_container">
                <div class="updates">
                    <p><b>http://kdm-manager.com</b> release <b>{{user.meta.webapp.release}}</b> is currently running on version <b>{{user.meta.api.version}}</b> of <a href="http://api.thewatcher.io" target="top">the Kingdom Death API</a>, which was released on {{latest_blog_post.published}}.</p>
                    <p>The KDM API currently supports version <b>1.5</b> of Kingdom Death: <i>Monster</i>.</p>
                    <a target="top" href="{{latest_blog_post.url}}"><button class="kd_blue full_width_modal_button">View latest change log</button></a>
                </div>
                <div class="twitter_embed_container">
                    <a
                        class="twitter-timeline"
                        href="https://twitter.com/kdmManager"
                        data-tweet-limit="3"
                    > Retrieving tweets...
                    </a>
                    <script async src="//platform.twitter.com/widgets.js" charset="utf-8"></script>
                </div>
            </div> <!-- dashboard_updates_container -->
            <button class="kd_alert_no_exclaim" onclick="showHide('dashboardTwitter')">Return to the Dashboard!</button>

        </div> <!-- dashboard_twitter -->

        <button
            id="dashboardTwitterButton"
            class="dashboard_twitter_button kd_promo"
            ng-click="showHide('dashboardTwitter')"
        > !
        </button>
        </div> <!-- dashboardControlElement -->

    <script type="text/javascript">
        // kill the spinner, since we're done loading the page now.
        hideFullPageLoader();
    </script>


    <div
        id="dashboardLoader"
        class="metrophobic settlements_retrieved"
        ng-if="scratch.settlementsRetrieved != scratch.settlementsRequired"
    >
        <span ng-if="user == undefined">
            Retrieving user data...
        </span>
        <span ng-if="scratch.settlementsRequired != undefined">
            Retrieving settlement {{scratch.settlementsRetrieved}} / {{scratch.settlementsRequired}}
        </span>
        <div class="corner_loading_spinner visible">
            <img class="corner_loading_spinner" src="/media/loading_io.gif">
        </div>
    </div>

    """)


    # misc html assets

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


    hunt_phase = """

<script src="/media/huntPhase.js?v=$application_version"></script>

<div
    id="huntPhaseModal"
    class="modal-black hidden"
    ng-if="user.user.preferences.beta == true"
    ng-controller = "huntPhaseRootController"
    ng-init="showHide('huntPhaseOpenerButton')"
>
    <h3 class="hunt_phase">[BETA] Basic Hunt Event simulator!</h3>
    <p class="hunt_phase_subtitle">
        Use the controls below to simulate drawing cards from the Basic Hunt Event deck!
    </p>
    <div class="hunt_phase_container">
        <div
            class="option_container controls"
        >
            <button
                class="kd_brown"
                ng-click="shuffleDeck()"
            >
                Shuffle the deck!
            </button>
            <button
                class="kd_brown draw_one"
                ng-click="draw()"
                ng-if="deck.length > 0"
            >
                <b>Draw One!</b><br/> <span class="metrophobic">{{deck.length}} remaining</span>
            </button>
        </div>
        <div class="option_container drawn_cards" ng-if="deck.length > 0 || drawn.length > 1">
            <div class="card_container">
                <span
                    class="card survivor_sheet_gradient"
                    ng-repeat="card in drawn track by $index"
                >
                    <p class="card_title">{{$index + 1}}. {{card.name}}</p>
                    <p class="card_subtitle"> - {{card.subtitle}} - </p>
                    <p
                        class="card_desc"
                        ng-bind-html="card.desc|trustedHTML"
                    ></p>
                    <div class="die_roll" ng-if="card.roll_die">
                        {{card.die_roll}}
                    </div>
                </span>
            </div>
        </div>

        <h3 class="hunt_phase">Optional Basic Hunt Event cards</h3>
        <p class="hunt_phase_subtitle">Tap or click a card to include it in your deck. Don't forget to re-shuffle afterwards!</p>

        <div class="option_container expansion_cards">

            <button
                class="expansion_card"
                ng-repeat="card in cards"
                ng-if="card.optional == true"
                ng-click="includeCard(card)"
                ng-class="{true: 'kd_blue', }[card.included]"
            >
                {{card.name}}
            </button>

        </div>

        <button class="kd_alert_no_exclaim" ng-click="showHide('huntPhaseModal')">Back</button>

    </div> <!-- container -->
</div>


    """


    expansions_manager = """\n
    <div
        id="modalExpansionsManager"
        class="modal hidden"
        ng-if="user_is_settlement_admin"
        ng-controller="updateExpansionsController"
    >

      <!-- Modal content -->
        <div class="full_size_modal_panel timeline_gradient">
            <span class="closeModal" onclick="showHide('modalExpansionsManager')">×</span>

            <h3>Expansions!</h3>

            <div class="expansions_controls_container" ng-init="addNewSettlementsToScope('$api_url')">
                <p>Use the controls below to determine which expansion content is
                enabled for this campaign. Remember to save and reload when finished!</p>

                <span
                    ng-if="new_settlement_assets != undefined"
                    ng-init="showHide('modalExpansionsOpener')"
                >
                    <!-- HACK CITY -->
                </span>

                <form method="POST" action="#">
                    <div class="expansion_content_line_item" ng-repeat="x in new_settlement_assets.expansions">
                        <input
                            id="{{x.handle}}_modal_toggle"
                            name="{{x.handle}}"
                            type="checkbox"
                            class="kd_css_checkbox kd_radio_option"
                            ng-model=incomingExpansion
                            ng-checked="settlement.sheet.expansions.indexOf(x.handle) != -1"
                            ng-click="toggleExpansion(x.handle)"
                            ng-disabled="settlement.game_assets.campaign.settlement_sheet_init.expansions.includes(x.handle)"
                        >
                        <label for="{{x.handle}}_modal_toggle">{{x.name}}</label>
                    </div> <!-- line_item -->

                    <div class="expansion_content_remove_warning">
                    <b>Warning!</b>
                    Disabling expansion content when it is required by the
                    campaign or the items on the campaign's Settlement and Survivor
                    Sheets (innovations, locations, fighting arts, etc.)
                    can cause errors and other unexpected behavior!
                    </div>

                    <button
                        type="submit"
                        class="kd_blue save_expansions"
                        onclick="closeModal('modalExpansionsManager'); showFullPageLoader()"
                    >
                        Save Changes and Reload
                    </button>

                </form>
            </div> <!-- container -->
        </div> <!-- modal content -->
    </div> <!-- parent modal -->
    """

    bulk_add_survivors = """\n
    <div
        id="modalBulkAdd" class="modal hidden"
        ng-if="user_is_settlement_admin && user.user.subscriber.level > 1"
        ng-init="showHide('bulkAddOpenerButton');"
        ng-controller="addManySurvivorsController"
    >

      <!-- Modal content -->
        <div class="full_size_modal_panel survivor_sheet_gradient bulk_add_modal">
            <span class="closeModal" onclick="showHide('modalBulkAdd')">×</span>

            <div
                id="bulkAddControlsContainer"
            >

                <h3>Add Multiple New Survivors</h3>
                <p>Use these controls to add multiple new survivors to {{settlement.sheet.name}}.
                    <span ng-if="user.user.preferences.random_names_for_unnamed_assets == true">
                        New survivors will be manageable by all players in the campaign and
                        will be assigned random names.
                    </span>
                    <span ng-if="user.user.preferences.random_names_for_unnamed_assets == false">
                      New survivors will be manageable by all players in the campaign.
                    </span>
                </p>

                <div
                    class="create_user_asset_block_group bulk_add_block_group"
                >
                    <div class="bulk_add_tumblers">
                        <div class="bulk_add_control">

                            Male

                            <button
                                type="button"
                                class="incrementer"
                                ng-click="scratch.addMaleSurvivors = scratch.addMaleSurvivors + 1"
                            >
                                &#9652;
                            </button>
                            <input
                                id="maleCountBox"
                                class="big_number_square"
                                type="number"
                                value="0"
                                min="0"
                                ng-model="scratch.addMaleSurvivors"
                            />
                            <button
                                type="button"
                                class="decrementer"
                                ng-click="scratch.addMaleSurvivors = scratch.addMaleSurvivors - 1"
                            >
                            &#9662;
                            </button>
                        </div>  <!-- bulk_add_control maleCountBox" -->
                        <div class="bulk_add_control">

                            Female

                            <button
                                type="button"
                                class="incrementer"
                                ng-click="scratch.addFemaleSurvivors = scratch.addFemaleSurvivors + 1"
                            >
                                &#9652;
                            </button>
                            <input
                                id="femaleCountBox"
                                class="big_number_square"
                                type="number"
                                value="0"
                                min="0"
                                ng-model="scratch.addFemaleSurvivors"
                            />

                            <button
                                type="button"
                                class="decrementer"
                                ng-click="scratch.addFemaleSurvivors = scratch.addFemaleSurvivors - 1"
                            >
                                &#9662;
                            </button>
                        </div> <!-- bulk_add_control female -->

                    </div> <!-- bulk_add_tumblers -->

                </div>
                <div
                    ng-if="settlement.sheet.lantern_year > 0 && (scratch.addFemaleSurvivors > 0 || scratch.addMaleSurvivors > 0)"
                > <!-- parents stuff -->
                    <h3>Parents</h3>
                    <p>Survivors without parents are not eligible for the automatic
                    application of Innovation bonuses granted to newborn survivors!
                    </p>

                    <div class="bulk_add_block_group">

                        <div class="bulk_add_parent_selectors"> <!-- parent selectors -->
                            <select
                                name="father"
                                ng-model="scratch.manySurvivorsFather"
                                ng-options="survivor._id.$oid as survivor.name for survivor in settlement.eligible_parents.male"
                            /><option selected disabled value="" name="father">Father</option></select>

                            <select
                                name="mother"
                                ng-model="scratch.manySurvivorsMother"
                                ng-options="survivor._id.$oid as survivor.name for survivor in settlement.eligible_parents.female"
                            /><option selected disabled value="" name="mother">Mother</option></select>
                        </div> <!-- parent selectors -->
                    </div> <!-- bulk_add_block_group -->

                </div><!--parents stuff -->

                <button
                    id="bulkAddSurvivors"
                    ng-if="scratch.addMaleSurvivors > 0 || scratch.addFemaleSurvivors > 0"
                    onclick="showHide('bulkAddControlsContainer'); showHide('bulkAddResultsContainer')"
                    ng-click="addManySurvivors()"
                    class="kd_blue settlement_sheet_bulk_add"
                >
                    Create New Survivors
                </button>

            </div> <!-- bulkAddControlsContainer -->

            <div
                id="bulkAddResultsContainer"
                class="bulk_add_results_container hidden"
            >
                <div
                    class="bulk_add_loader_container"
                    ng-if="scratch.showLoader == true"
                >
                    <img src="/media/loading_lantern.gif" />
                    <p>Creating {{scratch.addMaleSurvivors + scratch.addFemaleSurvivors}} new survivors...</p>
                </div>

                <form
                    action=""
                    method="POST"
                    class="bulk_add_new_survivor_form"
                    ng-repeat="s in scratch.bulkAddNewSurvivors"
                >
                    <input type="hidden" name="view_survivor" value="{{s.sheet._id.$oid}}">
                    <button
                        class="bulk_add_new_survivor"
                        ng-class="{kd_blue: s.sheet.sex == 'M', kd_alert_no_exclaim: s.sheet.sex == 'F'}"
                    >
                        <b>{{s.sheet.name}}</b> [{{s.sheet.sex}}]
                    </button>
                </form>

            </div>

        </div> <!-- modal content -->
    </div> <!-- modal parent -->

    \n"""

    settlement_notes = """\n\
    <div
        class="modal hidden"
        id="settlementNotesContainer"
        ng-if="settlement != undefined && user != undefined"
        ng-controller="settlementNotesController"
        ng-init="showHide('settlementNotesOpenerButton');"
    >

        <div class="full_size_modal_panel campaign_summary_gradient">

            <span class="closeModal" onclick="showHide('settlementNotesContainer')">×</span>

            <h3>Campaign Notes</h3>
            <p>All players in the {{settlement.sheet.name}} campaign may make
            notes and comments here. Tap or click notes to remove them.</p>

            <div class="settlement_notes_application_container">

                <div class="settlement_notes_note_container">

                    <div class="settlement_notes_controls">
                        <input ng-model="newNote" onclick="this.select()" class="add_settlement_note">
                        <button ng-click="addNote()" class="kd_blue add_settlement_note">+</button>
                    </div> <!-- settlement_notes_controls -->

                    <div
                        class="settlement_note"
                        ng-repeat="n in settlement.sheet.settlement_notes"
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
                        </div> <!-- note flair -->

                        <div class="note_content clickable" ng-click="showHide(n._id.$oid)">
                            {{n.note}} <span class="author" ng-if="n.author != user_login"> {{n.author}}</span>
                        </div> <!-- note content -->

                        <span
                            id="{{n._id.$oid}}"
                            class="kd_alert_no_exclaim note_remove hidden clickable"
                            ng-if="n.author == user_login || user_is_settlement_admin"
                            ng-click="removeNote($index, n._id.$oid)
                        ">
                            &times;
                        </span>

                    </div><!-- settlement_note -->

                </div> <!-- settlement_notes_note_container -->


            </div> <!-- settlement_notes_application_container -->

            <div
                ng-if="user_is_settlement_admin"
                ng-controller="playerManagementController"
                class="player_management_controller"
            >
                <hr/>
                <h3>Manage Players</h3>
                    <p>Add other registered users to the {{settlement.sheet.name}}
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
                            <td class="flair" ng-if="arrayContains(p.login, settlement.sheet.admins) == true">
                                <span class="player_management_flair kdm_font_hit_locations">a</span>
                            </td>
                            <td class="flair" ng-if="arrayContains(p.login, settlement.sheet.admins) == false">
                                <span class="player_management_flair kdm_font_hit_locations">b</span>
                            </td>

                            <td class="login">
                                {{p.login}}
                                <span ng-if="p._id.$oid == settlement.sheet.created_by.$oid">
                                    (Founder)
                                </span>
                            </td>

                            <td class="admin">
                                <input
                                    type="checkbox"
                                    class="player_management_admin"
                                    ng-if="p._id.$oid != settlement.sheet.created_by.$oid"
                                    ng-model="playerIsAdmin"
                                    ng-checked="settlement.sheet.admins.indexOf(p.login) != -1"
                                    ng-click="toggleAdmin(p.login)"
                                />
                            </td>
                        </tr>
                    </table>

                <hr/>

                <button
                    class="kd_blue "
                    onClick="showFullPageLoader(); showCornerLoader();"
                    ng-click="initializeSettlement();"
                >
                    Save and reload view!
                </button>

            </div> <!-- ng-if div -->
        </div><!-- full size modal panel -->

    </div> <!-- modal (parent) -->
    \n"""

    timeline = """\n

    <div
        class="modal hidden"
        id="modalTimelineContainer"
        ng-controller="timelineController"
        ng-if="settlement.sheet.timeline != undefined"
        ng_init="
            setEvents();
            initializeEventLog();
            showHide('timelineOpenerButton')
        "
    >

        <span class="touch_me timeline_overlay_current_ly">LY: <b>{{settlement.sheet.lantern_year}}</b></span>

        <div class="full_size_modal_panel timeline_gradient">

            <span class="closeModal" onclick="showHide('modalTimelineContainer')">×</span>

            <h3>{{ settlement.sheet.name}} Timeline</h3>

            <p ng-if="user_is_settlement_admin">
                Click or tap on any Lantern Year below to update events occuring during that year.
            </p>
            <p ng-if="user_is_settlement_admin == false">
                The Timeline of story, settlement and showdown events for {{settlement.sheet.name}}. Only settlement admins may modify the timeline.
            </p>

            <div class="timeline_ly_headline">
                <span>Year</span><span>Story & Special Events</span>
            </div>

            <div
                ng-repeat="t in settlement.sheet.timeline"
                ng-init="t.log_div_id = 'ly' + t.year + 'LogDivIDHandle'"
                class="timeline_whole_entry_container"
            >
                <div class="timeline_ly_container" ng-click="showHideControls(t.year)">
                    <div class="timeline_bullet_and_year_container">
                        <span ng-if="t.year >= settlement.sheet.lantern_year" class="kd_toggle_bullet"></span>
                        <span ng-if="t.year < settlement.sheet.lantern_year" class="kd_toggle_bullet checked_kd_toggle_bullet"></span>
                        <span class="timeline_ly_number">{{t.year}}</span>
                    </div>

                    <div class="timeline_events_container">
                        <span class="timeline_event" ng-repeat="e in t.settlement_event">
                            <font class="kdm_font_hit_locations">a &nbsp;</font>
                            {{e.name}}
                        </span>
                        <span class="timeline_event" ng-repeat="e in t.story_event" ng-model="story_events">
                            <font class="kdm_font">g &nbsp;</font>
                            <b>{{e.name}}</b>
                            <span class="timeline_event_page" ng-if="e.page">
                                &nbsp;(p.{{e.page}})
                            </span>
                        </span>
                        <span class="timeline_event" ng-repeat="q in t.special_showdown">
                        <span><img class="icon special_showdown" src="/media/icons/special_showdown_event.png"/></span>
                            <font class="special_showdown_text"><b>{{q.name}}</b></font>
                        </span>
                        <span
                            class="timeline_event"
                            ng-repeat="q in t.showdown_event"
                            ng-if = "q.name != undefined"
                        >
                            <font class="kdm_font">f &nbsp;</font>
                            {{q.name}}
                        </span>
                        <span class="timeline_event" ng-repeat="n in t.nemesis_encounter">
                        <span><img class="icon" src="/media/icons/nemesis_encounter_event.jpg"/></span>
                            &nbsp; <b> {{n.name}}</b>
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

                    <div class="end_current_ly" ng-if="t.year==settlement.sheet.lantern_year">
                        <input
                            type="checkbox"
                            id="endLanternYear{{t.year}}"
                            ng-model="lantern_year"
                            ng-click="setLY(t.year + 1); showHideControls(t.year); showControls(t.year+1)"
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
                    ng-if="t.year <= settlement.sheet.lantern_year && get_event_log(t.year).length >= 1 "
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
                        ng-if="l.event != undefined"
                    >
                        <div
                            ng-class-odd="'log_zebra'"
                            ng-class-even="'log_no_zebra'"
                            ng-bind-html="l.event|trustedHTML"
                            class="{{l.event_type}}"
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

    form = Template("""\n\

<script src="/media/survivorSheet.js?v=$application_version"></script>

<div
    id = "survivor_sheet_angularjs_controller_container"
    ng-controller="survivorSheetController"
    ng-init="
        initializeSettlement('survivorSheet', '$api_url','$settlement_id','$survivor_id');
        initializeSurvivor('$survivor_id');
    "
>
    <span ng-if="settlement != undefined" ng-init="initializeUser('$user_id')"></span>
    <span ng-if="survivor != undefined" ng-init="initializeScope()"></span>

    <span
        class="tablet_and_desktop nav_bar survivor_sheet_gradient"
        style='{{settlement.survivor_color_schemes[survivor.sheet.color_scheme].style_string}}'
    >
    </span>
    <span
        class="mobile_only nav_bar_mobile survivor_sheet_gradient"
        style='{{settlement.survivor_color_schemes[survivor.sheet.color_scheme].style_string}}'
    >
    </span>
    <div class="top_nav_spacer">hidden</div>


    <div id="asset_management_left_pane">

        <div
            id="survivorName"
            contentEditable="true"
            class="survivor_sheet_survivor_name"
            onClick="rollUp('nameControl')"
            placeholder="Name"
        >

            {{survivor.sheet.name}}

        </div>
        <div
            id="nameControl"
            class="kd_sheet_ui_roll_down rolled_up"
        >
            <div class="kd_sheet_ui_roll_down_controls">
                <div class="kd_sheet_ui_number_tumbler">
                    <button
                        ng-if="user.user.subscriber.level > 1"
                        ng-click="randomName()"
                    >
                        Random Name
                    </button>
                    <button
                        ng-if="user.user.subscriber.level > 1"
                        ng-click="randomSurname()"
                    >
                        Random Surname
                    </button>
                    <button
                        class="kd_blue"
                        ng-click="setSurvivorName()"
                        onClick="rollUp('nameControl')"
                    >
                        Save Changes
                    </button>
                </div> <!-- number tumbler -->
            </div>
        </div> <!-- survival controls and rolls -->

        <div
            ng-if="survivor.sheet != undefined"
            class="survivor_sheet_kd_sheet_ui_box survivor_sex_box"
        >
            <div class="survivor_sheet_avatar_container">
                <label
                    for="avatar_file_input"
                    ng-if="survivor.sheet.avatar != undefined"
                >
                    <img
                        class="survivor_avatar_image"
                        ng-src="/get_image?id={{survivor.sheet.avatar.$oid}}"
                        alt="Click to change the avatar image for {{survivor.sheet.name}}"
                    />
                </label>
                <label
                    for="avatar_file_input"
                    ng-if="survivor.sheet.avatar == undefined"
                >
                    <img
                        class="survivor_avatar_image"
                        ng-src="/media/default_avatar_{{survivor.sheet.effective_sex}}.png"
                        alt="Click to change the avatar image for {{survivor.sheet.name}}"
                    />
                </label>
                <input
                    id="avatar_file_input"
                    ng-controller='avatarController'
                    ng-model="scratch.newAvatar"
                    ng-blur="setAvatar()"
                    class="hidden"
                    type="file"
                    name="survivor_avatar"
                    accept="image/*"
                    custom-on-change="setAvatar"
                />

            </div> <!-- avatar -->
            <div
                class="survivor_sex_toggle clickable"
                ng-click="toggleSurvivorSex()"
                ng-if="survivor.sheet.sex == survivor.sheet.effective_sex"
            >
                M <div class="kd_sheet_ui_box" ng-class="{checked: survivor.sheet.sex == 'M'}"></div>
                F <div class="kd_sheet_ui_box" ng-class="{checked: survivor.sheet.sex == 'F'}"></div>
            </div>
            <div
                class="survivor_sex_toggle clickable"
                ng-if="survivor.sheet.sex != survivor.sheet.effective_sex"
                onClick="rollUp('effectiveSexWarning')"
            >
                M <div class="kd_sheet_ui_box" ng-class="{maroon_box: survivor.sheet.effective_sex == 'M'}"></div>
                F <div class="kd_sheet_ui_box" ng-class="{maroon_box: survivor.sheet.effective_sex == 'F'}"></div>
            </div>
        </div>
        <div
            id="effectiveSexWarning"
            class="kd_sheet_ui_roll_down rolled_up clickable"
            onClick="rollUp('effectiveSexWarning')"
        >
            <div class="kd_sheet_ui_roll_down_controls">
                <div class="kd_sheet_ui_row_tip">
                    {{survivor.sheet.name}}'s base sex attribute is <b>{{survivor.sheet.sex}}</b>, but their sex has changed to <b>{{survivor.sheet.effective_sex}}</b> due the effects of a cursed item!</br>
                    In order to edit this survivor's sex, you must first remove the cursed item that changed their sex to <b>{{survivor.sheet.effective_sex}}</b>.<br/>
                    <i>Click or tap here to hide this notification.</i>
                </div>
            </div>
        </div> <!-- avatar and sex -->


        <div
            ng-controller="survivalController"
            class="survivor_sheet_kd_sheet_ui_box survival_box"
            title="Survival controls and info for {{survivor.sheet.name}}! Click or tap to modify."
            ng-if="survivor.sheet != undefined"
        >
            <div
                class="survival_box_number_container clickable"
                onClick="rollUp('survivalControl')"
            >
                <input
                    class="survival_box_number"
                    type="number"
                    ng-model="survivor.sheet.survival"
                    min="0"
                />
            </div>
            <div class="survival_box_title_and_lock">
                <div
                    class="survival_box_title clickable"
                    onClick="rollUp('survivalControl')"
                >
                    Survival
                </div>
                <div
                    class="survival_box_lock clickable"
                    ng-click="toggleStatusFlag('cannot_spend_survival')"
                >
                    <div
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.cannot_spend_survival == true}"
                    >
                    </div>
                    &#x1f512; Cannot spend survival.
                </div>
            </div>
            <div class="survival_box_survival_actions_container">
                <div
                    class="help-tip survival_box_survival_action_item"
                    ng-repeat="sa in survivor.survival_actions"
                >
                    <div
                        class="kd_sheet_ui_box"
                        ng-class="{checked: sa.available == true}"
                    >
                    </div>
                    <span class="sa_name">{{sa.name}}</span>
                    <p>{{sa.title_tip}}</p>
                </div>
            </div>
        </div> <!-- survivalController -->
        <div
            id="survivalControl"
            class="kd_sheet_ui_roll_down rolled_up"
        >
            <div class="kd_sheet_ui_roll_down_controls">
                <div
                    class="kd_sheet_ui_row_tip"
                    ng-if="settlement.sheet.enforce_survival_limit == true"
                >
                    {{settlement.sheet.name}} Survival Limit is <b>{{settlement.sheet.survival_limit}}</b>!
                </div>
                <div class="kd_sheet_ui_number_tumbler">
                    <button
                        ng-click="
                            survivor.sheet.survival = survivor.sheet.survival + 1
                        "
                    >
                        &#x25B2;
                    </button>
                    <button
                        ng-click="
                            survivor.sheet.survival = survivor.sheet.survival - 1
                        "
                    >
                        &#x25BC;
                    </button>
                    <button
                        class="kd_blue"
                        ng-click="updateSurvival()"
                        onClick="rollUp('survivalControl')"
                    >
                        Save Changes
                    </button>
                </div> <!-- number tumbler -->
            </div>
        </div> <!-- survival controls and rolls -->

        <!-- favorite / retired / dead -->
        <div
            ng-if="survivor.sheet != undefined"
            class="survivor_sheet_kd_sheet_ui_box favorite_retired_dead"
        >
            <div
                class="favorite_toggle clickable"
                ng-click="toggleFavorite()"
            >
                <div
                    class="kd_sheet_ui_box"
                    ng-class="{checked: scratch.favoriteBox == true}"
                >
                </div>
                Favorite
            </div>

            <div
                class="retired_toggle clickable"
                ng-click="setRetired()"
            >
                <div
                    class="kd_sheet_ui_box"
                    ng-class="{checked: survivor.sheet.retired == true}"
                >
                </div>
                Retired
            </div>

            <div
                class="dead_toggle clickable"
                ng-click="showHide('modalDeath')"
                ng-class="{maroon_text: survivor.sheet.dead != undefined}"
            >
                <div
                    class="kd_sheet_ui_box"
                    ng-class="{maroon_box: survivor.sheet.dead != undefined}"
                >
                </div>
                Dead
            </div>
        </div> <!-- survivor_dead_retired_container -->

        <!-- dynamic modal launchers -->
        <div
            class="survivor_sheet_kd_sheet_ui_box dynamic_modal_launchers"
        >
            <center ng-if="settlement.sheet == undefined">Waiting for campaign data...</center>
            <button
                id="cursedItemsOpener"
                class="hidden survivor_curse"
                ng-click="showHide('cursedItems')"
            >
                Cursed Items ({{survivor.sheet.cursed_items.length}})
            </button>

            <button
                id="saviorControlsModal"
                class="survivor_sheet_gradient affinity_{{survivor.sheet.savior}}"
                ng-if="settlement.game_assets.campaign.saviors == true"
                ng-click="showHide('modalSavior')"
            >
                Savior
            </button>

            <button
                id="dragonControlsModal"
                class="dragon_king"
                ng-if="settlement.game_assets.campaign.dragon_traits != undefined"
                ng-click="showHide('theConstellations'); reinitialize()"
            >
                Dragon Traits ({{survivor.dragon_traits.trait_list.length}})
            </button>

        </div> <!-- dynamic buttons -->


        <!-- affinities opener -->
        <div
            ng-if="survivor.sheet != undefined"
            class="survivor_sheet_kd_sheet_ui_box affinities_opener clickable"
            ng-click="showHide('modalAffinity')"
            title="Permanent affinity bonuses for {{survivor.sheet.name}}. Click or tap to edit!"
        >
            <div
                class="affinity_{{a}} affinity_span"
                ng-repeat="a in ['red','green','blue']"
            >
                {{survivor.sheet.affinities[a]}}
            </div>
        </div> <!-- affinities opener -->

    </div> <!-- asset_management_left_pane -->



    <!-- MIDDLE ASSET MANAGEMENT PANE STARTS HERE -->

    <div id="asset_management_middle_pane" ng-if="survivor != undefined">

        <!-- BRAIN -->

        <div class="border_box survivor_hit_box insanity_box">

            <div class="big_number_container">

                <input
                    id="insanityBox"
                    type="number"
                    class="shield"
                    name="Insanity" min="0"
                    ng-model="survivor.sheet.Insanity"
                    ng-class="{true: 'maroon_text'}[survivor.sheet.Insanity >= 3]"
                    onClick="rollUp('insanityHitBoxControl')"
                />

                Insanity

            </div> <!-- big_number_container -->

            <div class="hit_box_detail">
                <span onClick="rollUp('insanityHitBoxControl')">Brain</span>
                <div
                    class="clickable damage_box"
                    ng-class="{checked: survivor.sheet.brain_damage_light != undefined}"
                    ng-click="toggleDamage('brain_damage_light');"
                 /></div>
            </div> <!-- hit_box_detail -->

            <p>If your insanity is 3+, you are <b>Insane</b>.</p>

        </div> <!-- survivor_hit_box -->
        <div
            id="insanityHitBoxControl"
            class="kd_sheet_ui_roll_down rolled_up"
        >
            <div class="kd_sheet_ui_roll_down_controls">
                <div class="kd_sheet_ui_number_tumbler">
                    <button ng-click="survivor.sheet.Insanity = survivor.sheet.Insanity + 1">
                        &#x25B2;
                    </button>
                    <button ng-click="survivor.sheet.Insanity = survivor.sheet.Insanity - 1">
                        &#x25BC;
                    </button>
                    <button
                        class="kd_blue"
                        ng-click="updateAttrib('Insanity')"
                        onClick="rollUp('insanityHitBoxControl')"
                    >
                        Save Changes
                    </button>
                </div> <!-- number tumbler -->
            </div>
        </div>

        <!-- HEAD -->
        <div class="border_box survivor_hit_box">
            <div class="big_number_container">
                <input
                    id="headBox"
                    ng-model="survivor.sheet.Head"
                    onClick="rollUp('headHitBoxControl')"
                    type="number" class="shield"
                    min="0"
                />
            </div>
            <div class="hit_box_detail">
                <span onClick="rollUp('headHitBoxControl')">
                    <font class="kdm_font_hit_locations">b</font> Head
                </span>
                <div
                    class="clickable heavy damage_box"
                    ng-class="{checked: survivor.sheet.head_damage_heavy != undefined}"
                    ng-click="toggleDamage('head_damage_heavy');"
                 /></div>
            </div>
            <p><b>H</b>eavy Injury: Knocked Down</p>
        </div> <!-- head hit box -->
        <div
            id="headHitBoxControl"
            class="kd_sheet_ui_roll_down rolled_up"
        >
            <div class="kd_sheet_ui_roll_down_controls">
                <div class="kd_sheet_ui_number_tumbler">
                    <button ng-click="survivor.sheet.Head = survivor.sheet.Head + 1">
                        &#x25B2;
                    </button>
                    <button ng-click="survivor.sheet.Head = survivor.sheet.Head - 1">
                        &#x25BC;
                    </button>
                    <button
                        class="kd_blue"
                        ng-click="updateAttrib('Head')"
                        onClick="rollUp('headHitBoxControl')"
                    >
                        Save Changes
                    </button>
                </div> <!-- number tumbler -->
            </div>
        </div>

        <!-- ARMS -->
        <div class="border_box survivor_hit_box">
            <div class="big_number_container">
                <input
                    id="armsBox"
                    ng-model="survivor.sheet.Arms"
                    onClick="rollUp('armsHitBoxControl')"
                    type="number" class="shield"
                    min="0"
                />
            </div>
            <div class="hit_box_detail">
                <span onClick="rollUp('armsHitBoxControl')">
                    <font class="kdm_font_hit_locations">d</font> Arms
                </span>
                <div class="two_box_container">
                    <div
                        class="clickable damage_box"
                        ng-class="{checked: survivor.sheet.arms_damage_light != undefined}"
                        ng-click="toggleDamage('arms_damage_light');"
                     /></div>
                    <div
                        class="clickable heavy damage_box"
                        ng-class="{checked: survivor.sheet.arms_damage_heavy != undefined}"
                        ng-click="toggleDamage('arms_damage_heavy');"
                     /></div>
                </div>
            </div>
            <p><b>H</b>eavy Injury: Knocked Down</p>
        </div> <!-- arms hit box -->
        <div
            id="armsHitBoxControl"
            class="kd_sheet_ui_roll_down rolled_up"
        >
            <div class="kd_sheet_ui_roll_down_controls">
                <div class="kd_sheet_ui_number_tumbler">
                    <button ng-click="survivor.sheet.Arms = survivor.sheet.Arms + 1">
                        &#x25B2;
                    </button>
                    <button ng-click="survivor.sheet.Arms = survivor.sheet.Arms - 1">
                        &#x25BC;
                    </button>
                    <button
                        class="kd_blue"
                        ng-click="updateAttrib('Arms')"
                        onClick="rollUp('armsHitBoxControl')"
                    >
                        Save Changes
                    </button>
                </div><!-- number tumbler -->
            </div>
        </div>

        <!-- BODY -->
        <div class="border_box survivor_hit_box">
            <div class="big_number_container">
                <input
                    id="bodyBox"
                    ng-model="survivor.sheet.Body"
                    onClick="rollUp('bodyHitBoxControl')"
                    type="number" class="shield"
                    min="0"
                />
            </div>
            <div class="hit_box_detail">
                <span onClick="rollUp('bodyHitBoxControl')">
                    <font class="kdm_font_hit_locations">c</font> Body
                </span>
                <div class="two_box_container">
                    <div
                        class="clickable damage_box"
                        ng-class="{checked: survivor.sheet.body_damage_light != undefined}"
                        ng-click="toggleDamage('body_damage_light');"
                     /></div>
                    <div
                        class="clickable heavy damage_box"
                        ng-class="{checked: survivor.sheet.body_damage_heavy != undefined}"
                        ng-click="toggleDamage('body_damage_heavy');"
                     /></div>
                </div>
            </div>
            <p><b>H</b>eavy Injury: Knocked Down</p>
        </div> <!-- body hit box -->
        <div
            id="bodyHitBoxControl"
            class="kd_sheet_ui_roll_down rolled_up"
        >
            <div class="kd_sheet_ui_roll_down_controls">
                <div class="kd_sheet_ui_number_tumbler">
                    <button ng-click="survivor.sheet.Body = survivor.sheet.Body + 1">
                        &#x25B2;
                    </button>
                    <button ng-click="survivor.sheet.Body = survivor.sheet.Body - 1">
                        &#x25BC;
                    </button>
                    <button
                        class="kd_blue"
                        ng-click="updateAttrib('Body')"
                        onClick="rollUp('bodyHitBoxControl')"
                    >
                        Save Changes
                    </button>
                </div><!-- number tumbler -->
            </div>
        </div>

        <!-- WAIST -->
        <div class="border_box survivor_hit_box">
            <div class="big_number_container">
                <input
                    id="waistBox"
                    ng-model="survivor.sheet.Waist"
                    onClick="rollUp('waistHitBoxControl')"
                    type="number" class="shield"
                    min="0"
                />
            </div>
            <div class="hit_box_detail">
                <span onClick="rollUp('waistHitBoxControl')">
                    <font class="kdm_font_hit_locations">e</font> Waist
                </span>
                <div class="two_box_container">
                    <div
                        class="clickable damage_box"
                        ng-class="{checked: survivor.sheet.waist_damage_light != undefined}"
                        ng-click="toggleDamage('waist_damage_light');"
                     /></div>
                    <div
                        class="clickable heavy damage_box"
                        ng-class="{checked: survivor.sheet.waist_damage_heavy != undefined}"
                        ng-click="toggleDamage('waist_damage_heavy');"
                     /></div>
                </div>
            </div>
            <p><b>H</b>eavy Injury: Knocked Down</p>
        </div> <!-- waist hit box -->
        <div
            id="waistHitBoxControl"
            class="kd_sheet_ui_roll_down rolled_up"
        >
            <div class="kd_sheet_ui_roll_down_controls">
                <div class="kd_sheet_ui_number_tumbler">
                    <button ng-click="survivor.sheet.Waist = survivor.sheet.Waist + 1">
                        &#x25B2;
                    </button>
                    <button ng-click="survivor.sheet.Waist = survivor.sheet.Waist - 1">
                        &#x25BC;
                    </button>
                    <button
                        class="kd_blue"
                        ng-click="updateAttrib('Waist')"
                        onClick="rollUp('waistHitBoxControl')"
                    >
                        Save Changes
                    </button>
                </div><!-- number tumbler -->
            </div>
        </div>

        <!-- LEGS -->
        <div class="border_box survivor_hit_box">
            <div class="big_number_container">
                <input
                    id="legsBox"
                    ng-model="survivor.sheet.Legs"
                    onClick="rollUp('legsHitBoxControl')"
                    type="number" class="shield"
                    min="0"
                />
            </div>
            <div class="hit_box_detail">
                <span onClick="rollUp('legsHitBoxControl')">
                    <font class="kdm_font_hit_locations">f</font> Legs
                </span>
                <div class="two_box_container">
                    <div
                        class="clickable damage_box"
                        ng-class="{checked: survivor.sheet.legs_damage_light != undefined}"
                        ng-click="toggleDamage('legs_damage_light');"
                     /></div>
                    <div
                        class="clickable heavy damage_box"
                        ng-class="{checked: survivor.sheet.legs_damage_heavy != undefined}"
                        ng-click="toggleDamage('legs_damage_heavy');"
                     /></div>
                </div>
            </div>
            <p><b>H</b>eavy Injury: Knocked Down</p>
        </div> <!-- legs hit box -->
        <div
            id="legsHitBoxControl"
            class="kd_sheet_ui_roll_down rolled_up"
        >
            <div class="kd_sheet_ui_roll_down_controls">
                <div class="kd_sheet_ui_number_tumbler">
                    <button ng-click="survivor.sheet.Legs = survivor.sheet.Legs + 1">
                        &#x25B2;
                    </button>
                    <button ng-click="survivor.sheet.Legs = survivor.sheet.Legs - 1">
                        &#x25BC;
                    </button>
                    <button
                        class="kd_blue"
                        ng-click="updateAttrib('Legs')"
                        onClick="rollUp('legsHitBoxControl')"
                    >
                        Save Changes
                    </button>
                </div><!-- number tumbler -->
            </div>
        </div>

    </div> <!-- asset_management_middle_pane HIT BOXES END HERE -->


    <!-- once per lifetime -->
    <div
        class="survivor_sheet_once_per_lifetime_container"
        ng-if="survivor.sheet != undefined"
    >

        <!-- SOTF opl -->
        <div
            class="sotf_reroll_controls survivor_sheet_kd_sheet_ui_box clickable"
            ng-if="settlement != undefined && settlement.sheet.principles.indexOf('survival_of_the_fittest') != -1"
            ng-controller="sotfRerollController"
            ng-click="sotfToggle()"
        >
            <div
                class="kd_sheet_ui_box_row sotf_option"
                ng-class="{maroon_text: survivor.sheet.sotf_reroll == true}"
            >
                <div
                    class="kd_sheet_ui_box"
                    ng-class="{maroon_box: survivor.sheet.sotf_reroll == true}"
                >
                </div>
                Once per lifetime reroll
            </div>
            <div class="kd_sheet_ui_box_row" ng-if="survivor.sheet.sotf_reroll != true">
                <p class="sotf_reroll_caption">
                    <b>Survival of the fittest:</b> Once per lifetime, a survivor may
                    reroll a single roll result. They must keep this result.</b>
                </p>
            </div>
        </div> <!-- sotf reroll -->

    </div> <!-- once per life time -->


    <!-- PARTNER CONTROLS -->
    <div
        class="survivor_sheet_partner_controls"
        ng-if="settlement.sheet.innovations.indexOf('partnership') != -1"
    >
        <div
            class="survivor_sheet_kd_sheet_ui_box survivor_sheet_partner_opener clickable settlement_sheet_gradient"
            ng-if="survivor.sheet.partner_id == undefined"
            onClick="showHide('partnerSelect')"
        >
            Select a Partner
        </div>
        <div
            class="survivor_sheet_kd_sheet_ui_box settlement_sheet_gradient survivor_sheet_partner clickable"
            ng-if="survivor.sheet.partner_id != undefined"
            onClick="showHide('partnerSelect')"
            title="{{survivor.sheet.name}}'s partner is {{partner.sheet.name}}. Click or tap to modify!"
        >
            <img
                ng-if="partner.sheet.avatar != undefined"
                class="survivor_sheet_partner_avatar"
                ng-src="/get_image?id={{partner.sheet.avatar.$oid}}"
            />
            <img
                ng-if="partner.sheet.avatar == undefined"
                class="survivor_sheet_partner_avatar"
                ng-src="/media/default_avatar_{{partner.sheet.effective_sex}}.png"
            />
            <p>
                <b>Partner - {{partner.sheet.name}}:</b> When you both <b>Arrive</b>, gain survival up to the survival limit. Partners may only nominate each other for <font class="kdm_font">g</font> <b>Intimacy</b>. When a partner dies, the remaining partner gains a random disorder and loses this ability.
            </p>
        </div>
        <div
            id="partnerSelect"
            class="modal-black hidden partner_select_modal"
        >
            <div
                class="partner_selector clickable survivor_sheet_gradient"
                ng-repeat="s in settlement.user_assets.survivors"
                ng-if="s.sheet.dead != true && s.sheet._id.$oid != survivor_id"
                ng-click="setPartner(s.sheet._id); showHide('partnerSelect')"
            >
                <img
                    ng-if="s.sheet.avatar != undefined"
                    class="partner_select_avatar"
                    ng-src="/get_image?id={{s.sheet.avatar.$oid}}"
                />
                <img
                    ng-if="s.sheet.avatar == undefined"
                    class="partner_select_avatar"
                    ng-src="/media/default_avatar_{{survivor.sheet.effective_sex}}.png"
                />
                <div>
                    <b>{{s.sheet.name}}</b> [{{s.sheet.sex}}]<br/>
                    Hunt XP: {{s.sheet.hunt_xp}} | Courage: {{s.sheet.Courage}} | Understanding: {{s.sheet.Understanding}}<br/>
                    <span class="metrophobic" ng-if="s.sheet.email != user_login"> &nbsp; <i>{{s.sheet.email}}</i></span>
                </div>
            </div>
            <button
                ng-if="survivor.sheet.partner_id != undefined"
                ng-Click="setPartner('UNSET'); showHide('partnerSelect')"
            >
                Remove partner
            </button>
            <button
                class="kd_alert_no_exclaim"
                onClick="showHide('partnerSelect')"
            >
                Cancel
            </button>
        </div>
    </div>


    <!-- SECONDARY ATTRIBS -->
    <div class="survivor_sheet_secondary_attribs_container" ng-if="survivor.sheet != undefined">
        <!-- HUNT XP -->
        <div
            class="survivor_sheet_kd_sheet_ui_box clickable"
            onClick="rollUp('huntXPControl')"
            title="Hunt XP for {{survivor.sheet.name}}. Tap or click to edit!"
        >
            <div class="kd_sheet_ui_box_row hunt_xp">
                <span class="title">Hunt XP</span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: survivor.sheet.hunt_xp > 0}"
                ></span>
                <span
                    class="kd_sheet_ui_box heavy"
                    ng-class="{checked: survivor.sheet.hunt_xp > 1}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: survivor.sheet.hunt_xp > 2}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: survivor.sheet.hunt_xp > 3}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: survivor.sheet.hunt_xp > 4}"
                ></span>
                <span
                    class="kd_sheet_ui_box heavy"
                    ng-class="{checked: survivor.sheet.hunt_xp > 5}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: survivor.sheet.hunt_xp > 6}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: survivor.sheet.hunt_xp > 7}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: survivor.sheet.hunt_xp > 8}"
                ></span>
                <span
                    class="kd_sheet_ui_box heavy"
                    ng-class="{checked: survivor.sheet.hunt_xp > 9}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: survivor.sheet.hunt_xp > 10}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: survivor.sheet.hunt_xp > 11}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: survivor.sheet.hunt_xp > 12}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: survivor.sheet.hunt_xp > 13}"
                ></span>
                <span
                    class="kd_sheet_ui_box heavy"
                    ng-class="{checked: survivor.sheet.hunt_xp > 14}"
                ></span>
                <span
                    class="kd_sheet_ui_box heavy dotted"
                    ng-class="{checked: survivor.sheet.hunt_xp > 15}"
                >
                    <div class="dot" ng-if="survivor.sheet.hunt_xp < 16">.</div>
                </span>
            </div>
            <hr>
            <div class="kd_sheet_ui_row one_line_tip">
                <span
                    class="kd_sheet_ui_box heavy"
                    ng-class="{checked: survivor.sheet.hunt_xp > 1}"
                ></span>
                <font class="kdm_font">g</font> &nbsp; Age &nbsp
                <span
                    class="kd_sheet_ui_box heavy first"
                    ng-class="{checked: survivor.sheet.hunt_xp > 5}"
                ></span>
                <span
                    class="kd_sheet_ui_box heavy"
                    ng-class="{checked: survivor.sheet.hunt_xp > 5}"
                ></span>
                <font class="kdm_font">g</font> &nbsp; Age &nbsp
                <span
                    class="kd_sheet_ui_box heavy first"
                    ng-class="{checked: survivor.sheet.hunt_xp > 9}"
                ></span>
                <span
                    class="kd_sheet_ui_box heavy"
                    ng-class="{checked: survivor.sheet.hunt_xp > 9}"
                ></span>
                <span
                    class="kd_sheet_ui_box heavy"
                    ng-class="{checked: survivor.sheet.hunt_xp > 9}"
                ></span>
                <font class="kdm_font">g</font> &nbsp; Age &nbsp
                <span
                    class="kd_sheet_ui_box heavy first"
                    ng-class="{checked: survivor.sheet.hunt_xp > 14}"
                ></span>
                <span
                    class="kd_sheet_ui_box heavy"
                    ng-class="{checked: survivor.sheet.hunt_xp > 14}"
                ></span>
                <span
                    class="kd_sheet_ui_box heavy"
                    ng-class="{checked: survivor.sheet.hunt_xp > 14}"
                ></span>
                <span
                    class="kd_sheet_ui_box heavy"
                    ng-class="{checked: survivor.sheet.hunt_xp > 14}"
                ></span>
                <font class="kdm_font">g</font> &nbsp; Age &nbsp
            </div>
        </div> <!-- HUNT XP -->
        <div
            id="huntXPControl"
            class="kd_sheet_ui_roll_down rolled_up"
        >
            <div class="kd_sheet_ui_roll_down_controls">
                <div class="kd_sheet_ui_number_tumbler">
                    <button
                        ng-click="
                            survivor.sheet.hunt_xp = survivor.sheet.hunt_xp + 1
                        "
                    >
                        &#x25B2;
                    </button>
                    <button
                        ng-click="
                            survivor.sheet.hunt_xp = survivor.sheet.hunt_xp - 1
                        "
                    >
                        &#x25BC;
                    </button>
                    <button
                        class="kd_blue"
                        ng-click="updateAttrib('hunt_xp')"
                        onClick="rollUp('huntXPControl')"
                    >
                        Save Changes
                    </button>
                </div> <!-- number tumbler -->
            </div>
        </div>

        <!-- WEAPON PROFICIENCY -->
        <div
            class="survivor_sheet_kd_sheet_ui_box clickable"
            onClick="rollUp('weaponProficiencyControl')"
            title="Weapon Proficiency info for {{survivor.sheet.name}}. Tap or click to edit!"
        >
            <div class="kd_sheet_ui_row">
                <div class="title">
                Weapon Proficiency
                </div>
                <div class="kd_sheet_ui_box_row">
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet['Weapon Proficiency'] > 0}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet['Weapon Proficiency'] > 1}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: survivor.sheet['Weapon Proficiency'] > 2}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet['Weapon Proficiency'] > 3}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet['Weapon Proficiency'] > 4}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet['Weapon Proficiency'] > 5}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet['Weapon Proficiency'] > 6}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: survivor.sheet['Weapon Proficiency'] > 7}"
                    ></span>
                </div>
            </div>
            <div class="kd_sheet_ui_row">
                <div class="metrophobic">
                    &nbsp; <b>Type:</b>
                    <span ng-if="survivor.sheet.weapon_proficiency_type != null">
                        &nbsp; {{settlement.game_assets.weapon_proficiency_types[survivor.sheet.weapon_proficiency_type].name}}
                    </span>
                    <span
                        ng-if="survivor.sheet.weapon_proficiency_type == null"
                        class="kd_sheet_ui_dynamic_underline"
                    >
                    </span>
                </div>
                <div>
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: survivor.sheet['Weapon Proficiency'] > 2}"
                    ></span> <b>Specialist</b> &ensp;
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: survivor.sheet['Weapon Proficiency'] > 7}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: survivor.sheet['Weapon Proficiency'] > 7}"
                    ></span>
                    <b>Master</b>
                </div>
            </div>
        </div> <!-- survivor_sheet_kd_sheet_ui_box -->
        <div
            id="weaponProficiencyControl"
            class="kd_sheet_ui_roll_down rolled_up"
        >
            <div class="kd_sheet_ui_roll_down_controls">
                <div class="kd_sheet_ui_number_tumbler">
                    <button
                        ng-click="
                            survivor.sheet['Weapon Proficiency'] = survivor.sheet['Weapon Proficiency'] + 1
                        "
                    >
                        &#x25B2;
                    </button>
                    <button
                        ng-click="
                            survivor.sheet['Weapon Proficiency'] = survivor.sheet['Weapon Proficiency'] - 1
                        "
                    >
                        &#x25BC;
                    </button>
                    <select
                        ng-model="survivor.sheet.weapon_proficiency_type"
                        ng-options="dict.handle as dict.name for dict in settlement.game_assets.weapon_proficiency_types"
                        ng-selected="survivor.sheet.weapon_proficiency_type"
                    >
                        <option disabled value="">Type</option>
                    </select>
                    <button
                        class="kd_blue"
                        ng-click="setWeaponProficiencyAttribs()"
                        onClick="rollUp('weaponProficiencyControl')"
                    >
                        Save Changes
                    </button>
                </div><!-- number tumbler-->
            </div>
        </div>

        <!-- COURAGE -->
        <div
            class="survivor_sheet_kd_sheet_ui_box clickable"
            onClick="rollUp('courageControl')"
            title="Courage controller for {{survivor.sheet.name}}. Tap or click to edit!"
        >
            <div class="kd_sheet_ui_row">
                <div class="title short">
                    Courage
                </div>
                <div class="kd_sheet_ui_box_row long">
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.Courage > 0}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.Courage > 1}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: survivor.sheet.Courage > 2}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.Courage > 3}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.Courage > 4}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.Courage > 5}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.Courage > 6}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.Courage > 7}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: survivor.sheet.Courage > 8}"
                    ></span>
                </div>
            </div>
            <div class="kd_sheet_ui_row dynamic_tip_row">
                <div
                    class="dynamic_tip_container"
                    ng-repeat="m in settlement.survivor_attribute_milestones.Courage"
                    ng-if="m.event == 'story_events'"
                >
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: survivor.sheet.Courage >= m.values[0]}"
                        ng-repeat="i in numberToRange(m.boxes) track by $index"
                    ></span>
                    <font class="kdm_font">g</font>
                    <b>{{settlement.game_assets.events[m.handle].name}}</b>
                    <font class="metrophobic">
                        (p.{{settlement.game_assets.events[m.handle].page}}) &ensp; 
                    </font>
                </span>
                </div>
            </div>
            <div class="kd_sheet_ui_row_tip" ng-if="survivor.sheet.abilities_and_impairments.indexOf('stalwart') != -1">
                <b>Stalwart:</b> Can't be knocked down by brain trauma or intimidate.
            </div>
            <div class="kd_sheet_ui_row_tip" ng-if="survivor.sheet.abilities_and_impairments.indexOf('prepared') != -1">
                <b>Prepared:</b> Add Hunt XP to your roll when determining a straggler.
            </div>
            <div class="kd_sheet_ui_row_tip" ng-if="survivor.sheet.abilities_and_impairments.indexOf('matchmaker') != -1">
                <b>Matchmaker:</b> Spend 1 endeavor to trigger Intimacy story event.
            </div>
        </div>
        <div
            id="courageControl"
            class="kd_sheet_ui_roll_down rolled_up"
        >
            <div class="kd_sheet_ui_roll_down_controls">
                <div class="kd_sheet_ui_ai_toggle_container" ng-if="survivor.sheet.Courage > 2">
                    <div class="kd_sheet_ui_ai_toggle_item">
                        <input
                            type="radio"
                            name="courage_ai"
                            ng-model="scratch.courageAI"
                            id="courageStalwart"
                            value="stalwart"
                        >
                        <label for="courageStalwart">
                            <b>Stalwart:</b> Can't be knocked down by brain trauma or intimidate.
                        </label>
                    </div>
                    <hr/>
                    <div class="kd_sheet_ui_ai_toggle_item">
                        <input
                            type="radio"
                            name="courage_ai"
                            ng-model="scratch.courageAI"
                            id="couragePrepared"
                            value="prepared"
                        >
                        <label for="couragePrepared">
                            <b>Prepared:</b> Add Hunt XP to your roll when determining a straggler.
                        </label>
                    </div>
                    <hr/>
                    <div class="kd_sheet_ui_ai_toggle_item">
                        <input
                            type="radio"
                            name="courage_ai"
                            ng-model="scratch.courageAI"
                            id="courageMatchmaker"
                            value="matchmaker"
                        >
                        <label for="courageMatchmaker">
                            <b>Matchmaker:</b> Spend 1 endeavor to trigger Intimacy story event.
                        </label>
                    </div>
                </div>
                <div class="kd_sheet_ui_number_tumbler">
                    <button
                        ng-click="
                            survivor.sheet.Courage = survivor.sheet.Courage + 1
                        "
                    >
                        &#x25B2;
                    </button>
                    <button
                        ng-click="
                            survivor.sheet.Courage = survivor.sheet.Courage - 1
                        "
                    >
                        &#x25BC;
                    </button>
                    <button
                        class="kd_blue"
                        ng-click="updateCourage()"
                        onClick="rollUp('courageControl')"
                    >
                        Save Changes
                    </button>
                </div> <!-- number tumbler -->
            </div>
        </div>

        <!-- UNDERSTANDING -->
        <div
            class="survivor_sheet_kd_sheet_ui_box clickable"
            onClick="rollUp('understandingControl')"
            title="Understanding controller for {{survivor.sheet.name}}. Tap or click to edit!"
        >
            <div class="kd_sheet_ui_row">
                <div class="title short">
                    Understanding
                </div>
                <div class="kd_sheet_ui_box_row long">
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.Understanding > 0}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.Understanding > 1}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: survivor.sheet.Understanding > 2}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.Understanding > 3}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.Understanding > 4}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.Understanding > 5}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.Understanding > 6}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.Understanding > 7}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: survivor.sheet.Understanding > 8}"
                    ></span>
                </div>
            </div>
            <div class="kd_sheet_ui_row dynamic_tip_row">
                <div
                    class="dynamic_tip_container"
                    ng-repeat="m in settlement.survivor_attribute_milestones.Understanding"
                    ng-if="m.event == 'story_events'"
                >
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: survivor.sheet.Understanding >= m.values[0]}"
                        ng-repeat="i in numberToRange(m.boxes) track by $index"
                    ></span>
                    <font class="kdm_font">g</font>
                    <b>{{settlement.game_assets.events[m.handle].name}}</b>
                    <font class="metrophobic">
                        (p.{{settlement.game_assets.events[m.handle].page}}) &ensp; 
                    </font>
                </span>
                </div>
            </div>
            <div class="kd_sheet_ui_row_tip" ng-if="survivor.sheet.abilities_and_impairments.indexOf('analyze') != -1">
                <b>Analyze:</b> Look at the top AI card and return it to the top of the deck.
            </div>
            <div class="kd_sheet_ui_row_tip" ng-if="survivor.sheet.abilities_and_impairments.indexOf('explore') != -1">
                <b>Explore:</b> Add +2 to your <b>investigate</b> roll results.
            </div>
            <div class="kd_sheet_ui_row_tip" ng-if="survivor.sheet.abilities_and_impairments.indexOf('tinker') != -1">
                <b>Tinker:</b> +1 endeavor when a returning survivor.
            </div>
        </div>
        <div
            id="understandingControl"
            class="kd_sheet_ui_roll_down rolled_up"
        >
            <div class="kd_sheet_ui_roll_down_controls">
                <div class="kd_sheet_ui_ai_toggle_container" ng-if="survivor.sheet.Understanding > 2">
                    <div class="kd_sheet_ui_ai_toggle_item">
                        <input
                            type="radio"
                            name="understanding_ai"
                            ng-model="scratch.understandingAI"
                            id="understandingAnalyze"
                            value="analyze"
                        >
                        <label for="understandingAnalyze">
                            <b>Analyze:</b> Look at the top AI card and return it to the top of the deck. 
                        </label>
                    </div>
                    <hr/>
                    <div class="kd_sheet_ui_ai_toggle_item">
                        <input
                            type="radio"
                            name="understanding_ai"
                            ng-model="scratch.understandingAI"
                            id="understandingExplore"
                            value="explore"
                        >
                        <label for="understandingExplore">
                            <b>Explore:</b> Add +2 to your <b>investigate</b> roll results. 
                        </label>
                    </div>
                    <hr/>
                    <div class="kd_sheet_ui_ai_toggle_item">
                        <input
                            type="radio"
                            name="understanding_ai"
                            ng-model="scratch.understandingAI"
                            id="understandingTinker"
                            value="tinker"
                        >
                        <label for="understandingTinker">
                            <b>Tinker:</b> +1 endeavor when a returning survivor.
                        </label>
                    </div>
                </div>
                <div class="kd_sheet_ui_number_tumbler">
                    <button
                        ng-click="
                            survivor.sheet.Understanding = survivor.sheet.Understanding + 1
                        "
                    >
                        &#x25B2;
                    </button>
                    <button
                        ng-click="
                            survivor.sheet.Understanding = survivor.sheet.Understanding - 1
                        "
                    >
                        &#x25BC;
                    </button>
                    <button
                        class="kd_blue"
                        ng-click="updateUnderstanding()"
                        onClick="rollUp('understandingControl')"
                    >
                        Save Changes
                    </button>
                </div> <!-- number tumbler -->
            </div>
        </div>

    </div> <!-- survivor_sheet_secondary_attribs_container -->

    <!-- SURVIVOR SPECIAL ATTRIBUTES -->

    <div
        ng-if="settlement.game_assets.survivor_special_attributes.length >= 1"
        class="survivor_sheet_special_attributes_container"
    >
        <div
            class = "survivor_sheet_special_attribute_container clickable"
            ng-repeat="s in settlement.game_assets.survivor_special_attributes"
            ng-click="toggleSpecialAttrib(s.handle)"
            ng-class="{active: survivor.sheet[s.handle] == true}"
            title = "{{s.title_tip}}"
        >
            <div
                class="special_attribute_checkbox"
                ng-class="{active: survivor.sheet[s.handle] == true}"
            ></div>
            <div
                class="special_attribute_text"
                ng-class="{active: survivor.sheet[s.handle] == true}"
            >
                {{s.name}}
            </div>
        </div>
    </div> <!-- survivorSpecialAttribsController -->


    <!-- survivor NOTES and EPITHETS -->
    <div class="survivor_sheet_notes_and_epithets_container">

        <div class="survivor_sheet_epithet_block">
            <div
                class="survivor_sheet_kd_sheet_ui_box survivor_sheet_epithets"
                ng-if="survivor != undefined"
                title="Survivor tags (formerly 'epithets'). Click or tap to remove! Click or tap the 'New Tag' button to add tags."
            >
                <ul>
                    <li
                        class="touch_me survivor_sheet_epithet"
                        ng-repeat="e in survivor.sheet.epithets"
                        ng-click="rmEpithet($index)"
                        style="
                            background-color: #{{settlement.game_assets.epithets[e].bgcolor}};
                            color: #{{settlement.game_assets.epithets[e].color}};
                            border-color: #{{settlement.game_assets.epithets[e].bordercolor}};
                        "
                    >
                        <span>{{settlement.game_assets.epithets[e].name}}</span>
                    </li>
                    <li
                        class="touch_me survivor_sheet_epithet paper_style_toggle"
                        onClick="rollUp('addEpithetControl')"
                    >
                        <b> New Tag </b>
                    </li>
                </ul>
            </div>
            <div
                id="addEpithetControl"
                class="kd_sheet_ui_roll_down rolled_up"
            >
                <div class="kd_sheet_ui_roll_down_controls">
                    <div class="kd_sheet_ui_row_tip clickable" onClick="rollUp('addEpithetControl')">
                        Survivor tags (formerly 'epithets') appear in Survivor Search
                        results. Click here to close these controls.
                    </div>
                    <div class="kd_sheet_ui_row">
                        <select
                            name="add_epithets"
                            ng-model="scratch.new_epithet"
                            ng-change="addEpithet()"
                            ng-options="e.handle as e.name for e in epithetOptions"
                        >
                            <option value="" disabled selected>Add Tags</option>
                        </select>
                    </div>
                </div>
            </div>
        </div><!-- epithet block -->

        <!-- notes -->
        <div class="survivor_sheet_note_block">
            <div
                class="survivor_sheet_kd_sheet_ui_box survivor_sheet_survivor_notes_container"
                title="Survivor notes for {{survivor.sheet.name}}! Click or tap to add/remove notes. Notes are included in the Survivor Search results."
                ng-if="survivor.sheet != undefined"
            >
                <div class="kd_sheet_ui_row">
                    <div class="title short">Notes</div>
                </div>

                <div
                    class="survivor_sheet_survivor_notes_slug_line_container"
                >
                    <ul class="survivor_sheet_survivor_notes">
                        <li
                            class="survivor_sheet_survivor_notes_slug_line clickable"
                            ng-repeat="x in survivor.notes"
                            ng-click="rmNote($index, x._id.$oid)"
                        >
                            {{x.note}}
                        </li>
                    </ul>

                    <div
                        class="survivor_sheet_survivor_notes_slug_line add_note_starter clickable"
                        onClick="rollUp('survivorNotesControl'); document.getElementById('survivorNoteInput').focus();"
                    >
                        <i> &ensp; Add a note...</i>
                    </div>
                </div>
            </div> <!-- survivor notes opener -->
            <div
                id="survivorNotesControl"
                class="kd_sheet_ui_roll_down rolled_up"
            >
                <div class="kd_sheet_ui_roll_down_controls">
                    <div class="kd_sheet_ui_row_tip" onClick="rollUp('survivorNotesControl')">
                        Notes will appear in Survivor Search results! Click or tap a note to remove it. Click or tap here to close these controls.
                    </div>
                    <input
                        id="survivorNoteInput"
                        class="survivor_sheet_survivor_notes_input"
                        ng-model="scratch.addNote"
                        placeholder="Add a Survivor Note"
                        onClick="this.select()"
                    />
                    <button
                        class="kd_blue"
                        ng-click="addNote()"
                        onClick="rollUp('survivorNotesControl')"
                    >
                        Add Note
                    </button>
                </div>
            </div><!-- survivor Notes controls -->
        </div><!-- note block -->
    </div><!-- NOTES and EPITHETS -->

    <div id="survivor_sheet_right_pane" >

        <!-- FARTING ARTS -->
        <div
            class="survivor_sheet_fa_container"
            ng-controller='fightingArtsController'
            ng-init="setFAoptions()"
            ng-if="survivor.sheet.fighting_arts != undefined"
        >
            <div
                class="right_pane_title"
            >
                <div class="title">Fighting Arts</div>
                <div class="caption">Maximum 3.</div>
                <div
                    class="lock clickable"
                    ng-click="toggleStatusFlag('cannot_use_fighting_arts')"
                >
                    <div
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.cannot_use_fighting_arts == true}"
                    >
                    </div>
                    &#x1f512; Cannot use Fighting Arts
                </div>
            </div> <!-- title elements -->


            <div
                title="Click or tap to remove survivor Fighting Arts."
                class="survivor_sheet_card_container"
            >
                <div
                    ng-repeat="fa_handle in survivor.sheet.fighting_arts"
                    class="survivor_sheet_card survivor_sheet_gradient clickable"
                    ng-class="{true: 'faded'}[survivor.sheet.cannot_use_fighting_arts]"
                >
                    <span ng-if = "settlement.game_assets.fighting_arts[fa_handle] == undefined">
                        <img src="/media/loading_lantern.gif"><br/>
                        Loading Fighting Art data...
                    </span>
                    <span
                        ng-init="
                            FA = settlement.game_assets.fighting_arts[fa_handle];
                            expansion_handle = settlement.game_assets.fighting_arts[fa_handle].expansion;
                            expansion_dict = settlement.game_assets.expansions[expansion_handle];
                        "
                        ng-if = "settlement.game_assets.fighting_arts[fa_handle] != undefined"
                        ng-click="rmFightingArt(fa_handle, $index)"
                        title="Click or tap to remove {{FA.name}} from {{survivor.sheet.name}}"
                    >

                        <div
                            class="settlement_sheet_card_expansion_flair"
                            ng-if="expansion_handle != null"
                            title="{{expansion_dict.name}} expansion Fighting Art"
                            style='
                                color: #{{expansion_dict.flair.color}};
                                background-color: #{{expansion_dict.flair.bgcolor}};
                            '
                            >
                        {{expansion_dict.name}}
                        </div>

                            <!-- regular title -->
                        <b ng-if="FA.constellation == null" class="card_title">
                            {{FA.name}}
                        </b>

                            <!-- dragon trait title -->
                        <b ng-if="FA.constellation != null" class="card_title card_constellation">
                            {{FA.name}}
                        </b>

                        <p class="survivor_sheet_card_subhead">- {{FA.sub_type_pretty}} -</p>
                        <p class="survivor_sheet_fighting_art_color_span {{FA.sub_type}}_gradient"> </p>
                        <div
                            class="survivor_sheet_card_text"
                            ng-bind-html="FA.desc|trustedHTML"
                        >
                        </div>
                        <div
                            ng-repeat="(level, desc) in FA.levels track by $index"
                            ng-if="desc != ''"
                            title="Tap or click a {{FA.name}} skill level to toggle it on or off."
                        >
                            <div
                                class="survivor_sheet_card_level_block clickable"
                                ng-click="toggleLevel($event, fa_handle, level)"
                                ng-if="survivor.sheet.fighting_arts_levels[fa_handle].indexOf($index) !== -1"
                            >
                                <span class="survivor_sheet_card_level_number toggled_on">{{level}}</span>
                                <span
                                    class="survivor_sheet_card_level_desc toggled_on"
                                    ng-bind-html="desc|trustedHTML"
                                >
                                </span>
                            </div>
                            <div
                                class="survivor_sheet_card_level_block clickable"
                                ng-click="toggleLevel($event, fa_handle, level)"
                                ng-if="survivor.sheet.fighting_arts_levels[fa_handle].indexOf($index) === -1"
                            >
                                <span class="survivor_sheet_card_level_number">{{level}}</span>
                                <span class="survivor_sheet_card_level_desc" ng-bind-html="desc|trustedHTML"></span>
                            </div>
                        </div> <!-- levels -->
                        <div class="survivor_sheet_card_click_to_remove">Tap or click to <b>remove</b>.</div>
                    </span>
                </div>
            </div> <!-- survivor_sheet_card_container -->

            <div class="survivor_sheet_card_asset_list_container" ng-if="survivor.sheet.fighting_arts.length <= 2">
                <select
                    name="add_fighting_arts"
                    class="fighting_arts_selector"
                    ng-if="FAoptions != undefined"
                    ng-model="userFA.newFA"
                    ng-change="addFightingArt(); userFA.newFA = FAoptions[0]"
                    ng-blur="userFA.newFA = FAoptions[0]"
                    ng-options="fa.handle as (fa.name + ' (' + fa.sub_type_pretty + ')'  ) for fa in FAoptions | orderObjectBy:'handle':false"
                >
                    <option value="" disabled selected>Add Fighting Art</option>
                </select>
                <span ng-if="FAoptions == undefined">Refreshing options...</span>
            </div>


        </div> <!-- fartingArtsController -->


        <!-- DISORDERS -->
        <div
            class="survivor_sheet_disorders_container"
            ng-controller="disordersController"
            ng-if="survivor.sheet != undefined"
        >
            <div
                class="right_pane_title"
            >
                <div class="title">Disorders</div>
                <div class="caption">Maximum 3.</div>
                <div class="lock"><!-- empty --></div>
            </div> <!-- title elements -->


            <div
                title="Click or tap to remove survivor Disorders."
                class="survivor_sheet_card_container disorders_container"
            >
                <div
                    ng-repeat="d_handle in survivor.sheet.disorders"
                    class="survivor_sheet_card disorder_card_gradient clickable"
                >
                    <span ng-if = "settlement.game_assets.disorders[d_handle] == undefined">
                        <img src="/media/loading_lantern.gif"><br/>
                        Loading Disorder data...
                    </span>
                    <span
                        ng-init="
                            D = settlement.game_assets.disorders[d_handle];
                            expansion_handle = settlement.game_assets.disorders[d_handle].expansion;
                            expansion_dict = settlement.game_assets.expansions[expansion_handle];
                        "
                        ng-if = "settlement.game_assets.disorders[d_handle] != undefined"
                        ng-click="rmDisorder(d_handle, $index)"
                        title="Click or tap to remove {{D.name}} from {{survivor.sheet.name}}"
                    >
                        <!-- EXPANSION FLAIR -->

                        <div
                            class="settlement_sheet_card_expansion_flair"
                            ng-if="expansion_handle != null"
                            title="{{expansion_dict.name}} expansion Disorder"
                            style='
                                color: #{{expansion_dict.flair.color}};
                                background-color: #{{expansion_dict.flair.bgcolor}};
                            '
                        >
                            {{expansion_dict.name}}
                        </div>

                        <!-- regular title -->
                        <b ng-if="D.constellation == null" class="card_title">
                            {{D.name}}
                        </b>

                        <!-- dragon trait title -->
                        <b ng-if="D.constellation != null" class="card_title card_constellation">
                            {{D.name}}
                        </b>
                        <div
                            class="survivor_sheet_card_text disorder_flavor_text"
                            ng-bind-html="D.flavor_text|trustedHTML"
                        >
                        </div>
                        <div
                            class="survivor_sheet_card_text"
                            ng-bind-html="D.survivor_effect|trustedHTML"
                        >
                        </div>

                        <div class="survivor_sheet_card_click_to_remove remove_disorder">
                            Tap or click to <b>remove</b>.
                        </div>

                    </span> <!-- actual disorder span -->
                </div> <!-- disorder ng-repeat -->
            </div> <!-- disorders survivor_sheet_card_container -->

            <div class="survivor_sheet_card_asset_list_container" ng-if="survivor.sheet.disorders.length <= 2">
                <select
                    name="add_disorders"
                    class="disorders_selector"
                    ng-if="dOptions != undefined"
                    ng-model="userD.newD"
                    ng-change="addDisorder(); userD.newD = dOptions[0]"
                    ng-blur="userD.newD = dOptions[0]"
                    ng-options="d.handle as d.name for d in dOptions | orderObjectBy:'handle':false"
                >
                    <option value="" disabled selected>Add Disorder</option>
                </select>
            </div>
        </div> <!-- disordersController -->


        <!-- ABILITIES AND IMPAIRMENTS -->
        <div
            class="survivor_sheet_ai_container"
            ng-if="survivor.sheet != undefined"
        >
            <div
                class="right_pane_title"
            >
                <div class="title ai_title">Abilities & Impairments</div>
                <div
                    class="lock clickable"
                    ng-click="toggleStatusFlag('skip_next_hunt')"
                >
                    <div
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.skip_next_hunt == true}"
                    >
                    </div>
                    &#x1f512; skip next hunt
                </div>
            </div> <!-- title elements -->

            <div
                class="outer_ai_container"
                title="Click or tap to remove survivor Abilities & Impairments."
            >

                <div
                    class="ai_repeater clickable"
                    ng-repeat="ai_handle in survivor.sheet.abilities_and_impairments track by $index"
                    ng-click="rmAI(ai_handle, $index)"
                    title="Click or tap to remove '{{settlement.game_assets.abilities_and_impairments[ai_handle].name}}'"
                >
                    <b
                            ng-if="settlement.game_assets.abilities_and_impairments[ai_handle].constellation == undefined"
                        >
                            {{settlement.game_assets.abilities_and_impairments[ai_handle].name}}:
                        </b>
                        <b
                            ng-if="settlement.game_assets.abilities_and_impairments[ai_handle].constellation != undefined"
                            class="card_constellation"
                        >
                            {{settlement.game_assets.abilities_and_impairments[ai_handle].name}}:
                        </b>
                    <span
                        class="survivor_sheet_ai_desc"
                        ng-bind-html="settlement.game_assets.abilities_and_impairments[ai_handle].desc|trustedHTML"
                    >
                    </span>
                </div>
            </div> <!-- ai 'card' outer container -->

            <div class="survivor_sheet_card_asset_list_container">
                <select
                    name="add_abilities_and_impairments"
                    class="ai_selector"
                    ng-if="AIoptions != undefined"
                    ng_model="scratch.newAI"
                    ng_change="addAI()"
                    ng-options="ai.handle as (ai.name + ' (' + ai.sub_type_pretty + ')'  ) for ai in AIoptions"
                >
                    <option value="" disabled selected>Add Abilities & Impairments</option>
                </select>
            </div>

        </div> <!-- ai controller -->
    </div> <!-- survivor_sheet_ai_container -->


    <!-- lineage block starts here -->
    <div
        ng-controller="lineageController"
        class="survivor_sheet_kd_sheet_ui_box lineage_container"
    >
        <p
            ng-if="lineage == undefined"
            class="lineage_subhead"
        >
            Waiting for lineage data...
        </p>

        <div
            ng-if="lineage != undefined"
            class="right_pane_title"
        >
            <div class="title">Lineage</div>

        </div> <!-- title elements -->

        <div
            ng-if="lineage != undefined"
            class="survivor_sheet_block_group lineage_block"
        >

            <div>
                <p class="lineage_subhead ">
                    Facts about the life and relationships of <b>{{survivor.sheet.name}}</b> will appear here as the campaign unfolds.
                </p>
                <h4>Biography</h4>

                <!-- founder -->
                <p ng-if="survivor.sheet.founder == true">
                    <font class="kdm_font_hit_locations">a</font> Founding member of {{settlement.sheet.name}}. 
                </p>

                <!-- born or joined -->
                <p ng-if="survivor.sheet.father != undefined || survivor.sheet.mother != undefined">
                    <font class="kdm_font_hit_locations">a</font> Born in LY{{survivor.sheet.born_in_ly}}. 
                </p>
                <p ng-if="survivor.sheet.father == undefined && survivor.sheet.mother == undefined && survivor.sheet.founder == false">
                    <font class="kdm_font_hit_locations">a</font> Joined the settlement in LY{{survivor.sheet.born_in_ly}}.
                </p>

                <!-- inheritance -->
                <div ng-repeat="parent in ['father','mother']">
                    <p ng-repeat="ai in survivor.sheet.inherited[parent].abilities_and_impairments">
                        <font class="kdm_font_hit_locations">a</font> Inherited <b>{{settlement.game_assets.abilities_and_impairments[ai].name}}</b> from <b>{{survivor.sheet.parents[parent].name}}</b> ({{parent}}).
                    </p>
                    <p ng-if="survivor.sheet.inherited[parent].weapon_proficiency_type != null" ng-init="wp = survivor.sheet.inherited[parent].weapon_proficiency_type">
                        <font class="kdm_font_hit_locations">a</font> Inherited <b>{{settlement.game_assets.weapon_proficiency_types[wp].name}}</b> proficiency from <b>{{survivor.sheet.parents[parent].name}}</b> ({{parent}}).
                    </p>
                    <p ng-if="survivor.sheet.inherited[parent]['Weapon Proficiency'] > 0">
                        <font class="kdm_font_hit_locations">a</font> Inherited {{survivor.sheet['Weapon Proficiency']}} Weapon Proficiency points from <b>{{survivor.sheet.parents[parent].name}}</b> ({{parent}}).
                    </p>
                </div>

                <!-- returning survivor -->
                <p ng-if="survivor.sheet.returning_survivor.length >= 1">
                    <font class="kdm_font_hit_locations">a</font> Returning survivor in the following Lantern Years: {{survivor.sheet.returning_survivor.join(', ')}}. 
                </p>

                <!-- retired and dead -->
                <p ng-if="survivor.sheet.retired == true" >
                    <font class="kdm_font_hit_locations">a</font> Retired in LY{{survivor.sheet.retired_in}}.
                </p>
                <p ng-if="survivor.sheet.dead == true" class="maroon_text">
                    <font class="kdm_font_hit_locations">a</font> <b>Died in LY{{survivor.sheet.died_in}}.</b>
                </p>
            </div> <!-- bio -->

            <div ng-if="lineage.events.length > 0" class="survivor_sheet_event_log_container">
                <h4>Event Log</h4>
                <div
                    id="lineageEventsToggle"
                    class="clickable"
                    ng-click="showHide('lineageEventsContainer'); showHide('lineageEventsToggle');"
                >
                    <p>Tap or click here to review {{lineage.events.length}} events!</p>
                </div>
                <div
                    id="lineageEventsContainer"
                    class="clickable hidden"
                    ng-click="showHide('lineageEventsContainer'); showHide('lineageEventsToggle');"
                >
                    <p>Tap or click here to hide the event log!</p>
                    <div
                        class="lineage_event_repeater {{event.event_type}}"
                        ng-repeat="event in lineage.events"
                        ng-class-even="'zebra'"
                        title="Date({{event.created_on.$date}});"
                    >
                        {{event.ly}} - {{event.event}}
                    </div><!-- event repeater -->
                </div> <!-- events container -->
            </div> <!-- events -->

            <div
                id="survivorParents"
                class="survivor_sheet_parents_container"
                ng-if="survivor.sheet.founder == false"
            >
                <h4>Parents</h4>

                <select
                    class="survivor_sheet_father_picker"
                    ng-model="survivor.sheet.father.$oid"
                    ng-selected="survivor.sheet.father"
                    ng-options="s.sheet._id.$oid as s.sheet.name for s in settlement.user_assets.survivors | filter:maleFilter"
                    ng-change="setParent('father',survivor.sheet.father.$oid)"
                >
                    <option disabled value="">Father</option>
                </select>

                <select
                    class="survivor_sheet_mother_picker"
                    ng-model="survivor.sheet.mother.$oid"
                    ng-selected="survivor.sheet.mother"
                    ng-options="s.sheet._id.$oid as s.sheet.name for s in settlement.user_assets.survivors | filter:femaleFilter"
                    ng-change="setParent('mother', survivor.sheet.mother.$oid)"
                >
                    <option disabled value="">Mother</option>
                </select>


            </div>

            <div ng-if="lineage.intimacy_partners >= 1">
                <h4>Intimacy Partners</h4>
                <p>
                    <span ng-repeat="s in lineage.intimacy_partners">{{s.name}}{{$last ? '' : ', '}}</span>
                </p>
            </div>

            <div ng-if="lineage.siblings.full.length >= 1 || lineage.siblings.half.length >= 1">
                <h4>Siblings</h4>
                <p ng-if='lineage.siblings.full.length >= 1'>
                    <i>Full:</i> <span ng-repeat='s in lineage.siblings.full'>
                        {{s.name}}{{$last ? '' : ', '}}
                    </span>
                </p>
                <p ng-if='lineage.siblings.half.length >= 1'>
                    <i>Half</i>: <span ng-repeat='s in lineage.siblings.half'>
                        {{s.name}}{{$last ? '' : ', '}}
                    </span>
                </p>
            </div> <!-- siblings container -->

            <div ng-if="lineage.intimacy_partners.length >= 1">
                <h4>Children</h4>
                <p span ng-repeat="p in lineage.intimacy_partners">
                    <i>with</i> <b>{{p.name}}</b> [{{p.sex}}]</b><i>: </i>
                    <span ng-repeat="s in lineage.children[p._id.$oid]">
                        {{s.name}} (LY{{s.born_in_ly}}){{$last ? '' : ', '}}
                    </span>
                </p>
            </div>
        </div> <!-- survivor_sheet_block_group lineage -->
    </div> <!-- lineage -->


    <!-- ADMINISTRATION - PELIGRO! -->
    <div class="survivor_sheet_admin_block" ng-if="survivor.sheet != undefined">
        <div
            class="survivor_sheet_kd_sheet_ui_box survivor_admin maroon clickable"
            onClick="rollUp('survivorAdmin')"
            title="Survivor administration for {{survivor.sheet.name}}. Tap or click to see options."
            >
                Survivor Administration
        </div> <!-- admin opener -->

        <div
            id="survivorAdmin"
            class="kd_sheet_ui_roll_down rolled_up survivor_admin_rollup"
        >
            <div class="kd_sheet_ui_roll_down_controls survivor_admin_controls">

                <h4>Access</h4>
                <div
                    class="survivor_sheet_public_toggle clickable"
                    ng-click="toggleBoolean('public')"
                >
                    <div
                        class="kd_sheet_ui_box"
                        ng-class="{checked: survivor.sheet.public == true}"
                    >
                    </div>
                    &#x1f512; Any player may manage this survivor
                </div>
                <hr/>
                <h4>Email</h4>
                <input
                    id="survivorOwnerEmail"
                    class="survivor_owner_email"
                    onclick="this.select()"
                    type="email"
                    name="email"
                    placeholder="email"
                    ng-model="scratch.newSurvivorEmail"
                    ng-value="survivor.sheet.email"
                    ng-blur="setEmail(); showHide('emailTip')"
                    ng-focus="showHide('emailTip')"
                />

                <div id="emailTip" class="kd_sheet_ui_row_tip hidden">
                    Enter another registered user's email address here to make them a player in this campaign!
                </div>
                <hr/>

                <!-- permanent delete -->
                <div
                    class="permanently_delete_survivor"
                    ng-if="user.user.preferences.show_remove_button == true"
                >
                    <h4>Permanently Delete Survivor</h4>
                    <form
                        action="#"
                        method="POST"
                        onsubmit="return confirm('Press OK to permanently delete this survivor forever.\\r\\rThis is NOT THE SAME THING as marking it dead using controls above.\\r\\rPermanently deleting the survivor prevents anyone from viewing and/or editing this record ever again!');">
                            <input type="hidden" name="remove_survivor" value="$survivor_id"/>
                            <p>Use the button below to <u>permanently remove</u> {{survivor.sheet.name}}. Please note that this is not the same as marking the survivor dead, that this <b>cannot be undone</b> and that any relationships between {{survivor.sheet.name}} and other survivors will be removed.</p>
                        <button class="kd_alert_no_exclaim red_glow permanently_delete">Permanently Delete Survivor</button>
                    </form>
                </div> <!-- delete-o! delete-o! -->
                <div
                    class="kd_sheet_ui_row_tip"
                    ng-if="user.user.preferences.show_remove_button != true"
                >
                    <p>By default, controls for deleting survivors are hidden! If you came here to delete <b>{{survivor.sheet.name}}</b>, use the navigation controls in the upper left to return to the Dashboard, click on "System" and enable the preference that shows the remove button and come back.</p>
                    <p><b>Important!</b> Removing a surivor is permanent, <u>cannot be undone</u> and is not the same thing as marking the survivor dead using the controls above.</p>
                </div>
            </div> <!-- roll down controls admin -->
        </div <!-- roll down container admin -->
    </div> <!-- survivor admin block outermost container -->

    <div class="survivor_sheet_bottom_attrib_spacer">&nbsp;</div>

</div><!-- end of the survivorSheet.js survivorSheetController scope -->


    <!--            THIS IS THE FOLD! Only Modal content below!     -->
    <!--            Everything past here needs its own controller!  -->


    <!-- CURSED ITEMS CONTROLS -->
    <div
        id="cursedItems" class="modal hidden"
        ng-controller="cursedItemsController"
        ng-if="settlement != undefined"
        ng-init="showHide('cursedItemsOpener');"
    >
        <div class="modal-content survivor_sheet_gradient">
            <span class="closeModal" onclick="showHide('cursedItems')">×</span>

            <h3>Cursed Items</h3>
            <p>Use the controls below to add cursed items to a Survivor. Cursed
            gear cannot be removed from the Survivor's gear grid. Archive the gear
            when the survivor dies.</p>

            <div class="cursed_items_flex_container">

                <div class="cursed_item_toggle" ng-repeat="c in settlement.game_assets.cursed_items">
                    <input
                        id="{{c.handle}}"
                        class="cursed_item_toggle"
                        type="checkbox"
                        ng-model="cursedItemHandle"
                        ng-change="toggleCursedItem(c.handle)"
                        ng-checked="survivor.sheet.cursed_items.indexOf(c.handle) != -1"
                    />
                    <label
                        class="cursed_item_toggle"
                        for="{{c.handle}}"
                     >
                        <span class="cursed_item_name">{{c.name}}</span>

                        <div class="cursed_item_ability_block" ng-repeat="a in c.abilities_and_impairments">
                            <span
                                ng-if="settlement.game_assets.abilities_and_impairments[a] != undefined"
                                class="cursed_item_ability"
                            >
                                {{settlement.game_assets.abilities_and_impairments[a].name}} - 
                            </span>
                            <span
                                class="cursed_item_ability_desc"
                                ng-if="settlement.game_assets.abilities_and_impairments[a] != undefined"
                                ng-bind-html="settlement.game_assets.abilities_and_impairments[a].desc|trustedHTML"
                            >
                            </span>

                        </div>
                    </label>

                </div><!-- cursed_item_toggle -->
            </div> <!-- cursed_items_flex_container-->
        </div> <!-- modal-content -->
    </div> <!-- modal -->



    <!-- SURVIVOR ATTRIBUTE CONTROLS -->

    <div
        ng-controller="attributeController"
        class="survivor_sheet_attrib_controls"
    >

        <div
            ng-repeat="token in attributeTokens"
            ng-init="control_id = token.longName + '_controller'"
            id="{{token.longName}}_controls_container"
        >

            <div
                id="{{control_id}}"
                class="survivor_sheet_attrib_controls_modal survivor_sheet_gradient hidden"
            >
                <span
                    class="close_attrib_controls_modal"
                    ng-click="showHide(control_id)"
                >
                    X
                </span>

                <h3 class="{{token.buttonClass}}">{{token.longName}}</h3>

                <div
                    class="synthetic_attrib_total synthetic_attrib_total_{{token.longName}}"
                >
                    {{ survivor.sheet[token.longName] + survivor.sheet.attribute_detail[token.longName].gear + survivor.sheet.attribute_detail[token.longName].tokens }}
                </div>

                <hr/>

                <div class="survivor_sheet_attrib_controls_number_container_container">

                    <!-- start of BASE -->

                    <div class="survivor_sheet_attrib_controls_number_container">

                        <button
                            class="incrementer"
                            ng-click="incrementBase(token.longName, 1)"
                        >
                            +
                        </button>

                        <input
                            id="base_value_{{control_id}}"
                            type="number" string-to-number
                            class="survivor_sheet_attrib_controls_number"
                            onClick="this.select()"
                            ng-model="survivor.sheet[token.longName]"
                            ng-value="survivor.sheet[token.longName]"
                            ng-blur="setBase(token.longName)"
                        />

                        <button
                            class="decrementer"
                            ng-click="incrementBase(token.longName, -1)"
                        >
                            -
                        </button>

                        <p><b>Base</b></p>

                    </div> <!-- survivor_sheet_attrib_controls_number_container -->

                    <!-- end of BASE; start of GEAR -->

                    <div class="survivor_sheet_attrib_controls_number_container">

                        <button
                            class="incrementer"
                            ng-click="incrementDetail(token.longName, 'gear', 1)"
                        >
                            +
                        </button>

                        <input
                            id="gear_value_{{token.longName}}_controller"
                            type="number"
                            class="survivor_sheet_attrib_controls_number"
                            onClick="this.select()"
                            ng-model="survivor.sheet.attribute_detail[token.longName].gear"
                            ng-value="survivor.sheet.attribute_detail[token.longName].gear"
                            ng-blur="setDetail(token.longName, 'gear')"
                        />

                        <button
                            class="decrementer"
                            ng-click="incrementDetail(token.longName, 'gear', -1)"
                        >
                            -
                        </button>

                        <p>Gear</p>

                    </div> <!-- survivor_sheet_attrib_controls_number_container GEAR -->

                    <!-- end $long_name GEAR; begin TOKENS -->

                    <div class="survivor_sheet_attrib_controls_number_container">

                        <button
                            class="incrementer"
                            ng-click="incrementDetail(token.longName, 'tokens', 1)"
                        >
                            +
                        </button>

                        <input
                            id="tokens_value_{{token.longName}}_controller"
                            class="survivor_sheet_attrib_controls_number"
                            type="number"
                            onClick="this.select()"
                            ng-model="survivor.sheet.attribute_detail[token.longName].tokens"
                            ng-value="survivor.sheet.attribute_detail[token.longName].tokens"
                            ng-blur="setDetail(token.longName, 'tokens')"
                        />

                        <button
                            class="decrementer"
                            ng-click="incrementDetail(token.longName, 'tokens', -1)"
                        >
                            -
                        </button>

                        <p>Tokens</p>

                    </div> <!-- survivor_sheet_attrib_controls_number_container -->

                </div><!-- survivor_sheet_attrib_controls_number_container_container -->

            </div> <!-- survivor_sheet_attrib_controls_modal starts out hidden -->

        <button
            class="survivor_sheet_attrib_controls_token {{token.buttonClass}}"
            ng-click="showHide(control_id)"
        >
            <p class="short_name">{{token.shortName}}</p>
            <p class="attrib_value synthetic_attrib_total_{{token.longName}}">
                {{ survivor.sheet[token.longName] + survivor.sheet.attribute_detail[token.longName].gear + survivor.sheet.attribute_detail[token.longName].tokens }}
            </p>
        </button>

        </div> <!-- attrib token controls container ng-repeat -->

    </div> <!-- survivor_sheet_attrib_controls -->


    <!-- THE CONSTELLATIONS -->


    <div
        id="theConstellations"
        class="modal hidden"
        ng-controller='theConstellationsController'
    >
        <div class="modal-content survivor_sheet_gradient">

            <span class="closeModal" onclick="showHide('theConstellations')">×</span>

            <h3>The Constellations</h3>

            <table id="survivor_constellation_table">
                <tr><th colspan="6">&nbsp;</th></tr>
                <tr>
                    <th>&nbsp;</th>
                    <th>Witch</th>
                    <th>Rust</th>
                    <th>Storm</th>
                    <th>Reaper</th>
                    <th>&nbsp;</th>
                </tr>
                <tr>
                    <th>Gambler</th>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('A1') == false">9 Understanding (max)</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('A1') == true" class="active">9 Understanding (max)</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('B1') == false">Destined disorder</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('B1') == true" class="active">Destined disorder</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('C1') == false">Fated Blow fighting art</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('C1') == true" class="active">Fated Blow fighting art</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('D1') == false">Pristine ability</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('D1') == true" class="active">Pristine ability</td>
                </tr>
                <tr>
                    <th>Absolute</th>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('A2') == false">Reincarnated Surname</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('A2') == true" class="active">Reincarnated Surname</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('B2') == false">Frozen Star secret fighting art</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('B2') == true" class="active">Frozen Star secret fighting art</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('C2') == false">Iridescent Hide ability</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('C2') == true" class="active">Iridescent Hide ability</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('D2') == false">Champion's Rite fighting art</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('D2') == true" class="active">Champion's Rite fighting art</td>
                </tr>
                <tr>
                    <th>Sculptor</th>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('A3') == false">Scar</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('A3') == true" class="active">Scar</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('B3') == false">Noble surname</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('B3') == true" class="active">Noble surname</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('C3') == false">Weapon Mastery</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('C3') == true" class="active">Weapon Mastery</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('D3') == false">+1 Accuracy attribute</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('D3') == true" class="active">+1 Accuracy attribute</td>
                </tr>
                <tr>
                    <th>Goblin</th>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('A4') == false">Oracle's Eye ability</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('A4') == true" class="active">Oracle's Eye ability</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('B4') == false">Unbreakable fighting art</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('B4') == true" class="active">Unbreakable fighting art</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('C4') == false">3+ Strength attribute</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('C4') == true" class="active">3+ Strength attribute</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('D4') == false">9 Courage (max)</td>
                    <td ng-if="survivor.dragon_traits.active_cells.includes('D4') == true" class="active">9 courage (max)</td>
                </tr>
                <tr><th colspan="6">&nbsp;</th></tr>

            </table>
            <br />

            <div id="survivor_constellation_control_container">

                <select
                    class="survivor_sheet_constellations_picker"
                    ng-if="survivor.dragon_traits.available_constellations.length >= 1"
                    ng-model="survivor.sheet.constellation"
                    ng-options="c for c in survivor.dragon_traits.available_constellations"
                    ng-change="setConstellation(survivor.sheet.constellation)"
                    ng-selected="survivor.sheet.constellation"
                >
                    <option disabled value="">Choose a Constellation</option>
                </select>

                <button
                    ng-if="survivor.sheet.constellation != undefined"
                    ng-click="unsetConstellation()"
                >
                    Unset Constellation
                </button>
            </div>

            <br/><br/>

        </div> <!-- modal-content -->

    </div> <!-- dragonTraitsModal ng-controller -->


    <!-- SAVIOR CONTROLS -->


    <div
        ng-controller="saviorController"
        id="modalSavior" class="modal hidden"
    >
        <div class="modal-content survivor_sheet_gradient">
            <span class="closeModal" onclick="showHide('modalSavior')">×</span>

            <h3>Savior</h3>

            <button
                class="affinity_red"
                ng-click="setSaviorStatus('red')"
            >
                Dream of the Beast
            </button>
            <button
                class="affinity_green"
                ng-click="setSaviorStatus('green')"
            >
                Dream of the Crown
            </button>
            <button
                class="affinity_blue"
                ng-click="setSaviorStatus('blue')"
            >
                Dream of the Lantern
            </button>

            <br/>

            <button
                ng-if = "survivor.sheet.savior != false"
                ng-click = "unsetSaviorStatus()"
            >
                Unset Savior Info
            </button>

        </div> <!-- modal-content -->

    </div> <!-- modalSavior -->

    <div
        id="modalDeath" class="modal hidden"
        ng-if="survivor != undefined"
        ng-controller="controlsOfDeath"
    >
        <div class="modal-content survivor_sheet_gradient">
            <span class="closeModal" onclick="showHide('modalDeath')">×</span>
            <h3>Controls of Death!</h3>
            <select
                class="survivor_sheet_cod_picker"
                ng-model="survivor.sheet.cause_of_death"
                ng-options="c.name as c.name disable when c.disabled for c in settlement.game_assets.causes_of_death"
                ng-change="processSelectCOD()"
                ng-selected='survivor.sheet.cause_of_death'
            >
                <option disabled value="">Choose Cause of Death</option>
            </select>

            <p id="addCustomCOD" style="display: none">
                <input
                    type="text"
                    class="custom_cod_text"
                    placeholder="Enter custom Cause of Death"
                    name="enter_cause_of_death"
                    ng-value="survivor.sheet.cause_of_death"
                    ng-model="customCOD"
                />
            </p>

            <p
                id="addCustomCOD"
                ng-if="
                    survivor.sheet.cause_of_death != undefined &&
                    settlement_cod_list.indexOf(survivor.sheet.cause_of_death) == -1
                "
            >
                <input
                    type="text"
                    class="custom_cod_text"
                    placeholder="Enter custom Cause of Death"
                    name="enter_cause_of_death"
                    ng-value="survivor.sheet.cause_of_death"
                    ng-model="customCOD"
                />
            </p>

            <div
                id="CODwarning"
                class="kd_alert control_error"
                style="display: none"
            >
                Please select or enter a Cause of Death!
            </div>

            <button
                class="kd_alert_no_exclaim red_glow"
                ng-click="submitCOD(customCOD)"
            >
                Die
            </button>

            <div ng-if="survivor.sheet.dead == true">
                <hr/>
                <button
                    class="kd_blue"
                    ng-click="resurrect()"
                >
                    Resurrect {{survivor.sheet.name}}
                </button>
            </div>

        </div> <!-- modal-content -->
    </div> <!-- modalDeath -->


    <div
        id="modalAffinity" class="modal hidden"
        ng-controller = "affinitiesController"
        ng-if="survivor != undefined"
    >
        <div class="modal-content survivor_sheet_gradient survivor_affinities_modal">
            <span class="closeModal" onclick="showHide('modalAffinity'); savedAlert()">×</span>

            <h3>Survivor Affinities</h3>
            <p>Adjust permanent affinities for <b>{{survivor.sheet.name}}</b>. Changes are saved automatically.</p><hr/>

            <div class="modal_affinity_controls_container">

                <div
                    ng-repeat="a in ['red','green','blue']"
                    class="modal_affinity_control_unit"
                >
                    <div class="bulk_add_control affinity_type" title="{{a}} affinity controls">
                        <button
                            type="button"
                            class="incrementer"
                            ng-click="incrementAffinity(a, 1)"
                        >
                            +
                        </button>
                        <input
                            id="{{a}}CountBox"
                            class="big_number_square"
                            type="number"
                            name="{{a}}_affinities"
                            ng-value="survivor.sheet.affinities[a]"
                            ng-model = 'affValue'
                            ng-change = "updateAffinity(this)"
                        />
                        <button
                            type="button"
                            class="decrementer"
                            ng-click="incrementAffinity(a, -1)"
                        >
                            -
                        </button>
                    </div>

                    <div class="affinity_block affinity_{{a}}">&nbsp;</div>

                    <hr class="affinity_spacer"/>

                </div> <!-- modal_affinity_control_unit REPEATS/ng-repeat-->

            </div> <!-- modal_affinity_controls_container -->
        </div> <!-- modal-content -->
    </div> <!-- modalAffinity -->

    \n""")




class settlement:

    new = Template("""\n\

<span class="tablet_and_desktop nav_bar settlement_sheet_gradient"></span>
<span class="nav_bar_mobile mobile_only settlement_sheet_gradient"></span>

<div
    class="create_new_asset_form_container"
    ng-controller="newSettlementController"
    ng-init="
        setView('newSettlement');
        initializeUser('$user_id','get','$api_url');
        addNewSettlementsToScope('$api_url');
    "
>
    <span
        ng-if="new_settlement_assets != undefined && user != undefined"
        ng-init="hideLoader(); showHide('fullPageLoader');"
    >
    </span>

    <form action="#" method="POST">

        <div class="create_user_asset_block_group">
            <input type="hidden" name="new" value="settlement" />
            <input
                type="text"
                name="name"
                placeholder="New Settlement Name"
                onclick="this.select()"
                class="new_asset_name"
                ng-model = "settlementName"
                autofocus
            />
        </div>

        <div class="create_user_asset_block_group">
            <h2 class="no_ul">Campaign:</h2>
            <p> Choosing an expansion campaign automatically enables expansion
            content required by that campaign and modifies the settlement timeline,
            milestones, principles, rules and Survivor Sheets. <br/><br/>
            A settlement's campaign <b>cannot be changed</b> after settlement
            creation!</p>

            <div ng-if="showLoader" class="new_settlement_loading">
                <img src="/media/loading_io.gif">
            </div>

            <div
                class="new_settlement_campaign_container"
                ng-repeat="c in new_settlement_assets.campaigns"
            >
                <input
                    type="radio"
                    id="{{c.handle}}"
                    class="kd_css_checkbox kd_radio_option"
                    name="campaign"
                    value="{{c.handle}}"
                    ng-checked="{{c.default}}"
                />
                <label for="{{c.handle}}">{{c.name}}
                    <p ng-if="c.subtitle" class="new_settlement_asset"> {{c.subtitle}}</p>
                </label>
            </div>
        </div>  <!-- campaigns -->

        <div class="create_user_asset_block_group">
            <h2 class="no_ul">Expansions:</h2>
            <p> Enable expansion content by toggling items below. Expansion
            content may also be enabled (or disabled) later using the controls
            on the left-side navigation bar.</p>

            <div ng-if="showLoader" class="new_settlement_loading">
                <img src="/media/loading_io.gif">
            </div>

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
        </div> <!-- block_group expansions -->

        <div class="create_user_asset_block_group">
            <h2 class="no_ul">Survivors:</h2>
            <p>By default, new settlements are created with no survivors. Toggle options below to create the settlement with pre-made survivors. </p>

            <div ng-repeat="c in new_settlement_assets.specials">
                <input
                    type="checkbox"
                    id="{{c.handle}}_checkbox"
                    class="kd_css_checkbox kd_radio_option"
                    name="specials"
                    ng-value="c.handle"
                />
                <label
                    for="{{c.handle}}_checkbox"
                >
                    {{c.title}}
                    <p
                        class="new_settlement_asset"
                        ng-bind-html="c.desc|trustedHTML"
                    ></p>
                </label>
            </div><!-- specials repeater -->

        <div ng-if="showLoader" class="new_settlement_loading">
            <img src="/media/loading_io.gif">
        </div>

        <div
            class="new_settlement_survivors_container"
            ng-repeat="s in new_settlement_assets.survivors"
        >
            <input
                id="{{s.handle}}"
                class="kd_css_checkbox kd_radio_option"
                type="checkbox"
                name="survivors"
                value="{{s.handle}}"
            />
            <label
                for="{{s.handle}}"
            />
                {{s.name}}
            </label>
        </div> <!-- survivors -->

    </div> <!-- block_group survivors -->

    <button
        ng-if="showLoader == false"
        class="kd_blue"
        ng-click="showHide('fullPageLoader')"
    >
        Create {{settlementName}}
    </button>
</form>

</div> <!-- create_new_asset_form_container -->
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
    summary = Template("""\n\n

    <script src="/media/campaignSummary.js?v=$application_version"></script>
    <div
        id = "campaign_summary_angularjs_controller_container"
        ng-controller="campaignSummaryController"
        ng-init="initializeSettlement('campaignSummary','$api_url','$settlement_id');"
    >
        <!-- once we get the settlement, init the user -->
        <span
            class="hidden"
            ng-if="settlement != undefined"
            ng-init="initializeUser('$user_id')"
        >
            Hack City!
        </span>

        <span class="tablet_and_desktop nav_bar campaign_summary_gradient"></span>
        <span class="nav_bar_mobile mobile_only campaign_summary_gradient"></span>
        <span class="top_nav_spacer mobile_only"> hidden </span>

        <div class="campaign_summary_headline_container" ng-if="settlement != undefined">
            <h1 class="settlement_name"> %s {{settlement.sheet.name}}</h1>
            <p class="campaign_summary_campaign_type">{{settlement.game_assets.campaign.name}}</p>
            <p>Population:
                {{settlement.sheet.population}}
                ({{settlement.sheet.population_by_sex.M}}M/{{settlement.sheet.population_by_sex.F}}F)<span ng-if="settlement.sheet.death_count > 0">; 
                    {{settlement.sheet.death_count}} death<span ng-if="settlement.sheet.death_count > 1">s</span>
                </span>
            </p>
            <p>Lantern Year: {{settlement.sheet.lantern_year}}, Survival Limit: {{settlement.sheet.survival_limit}}</p>
        </div> <!-- campaign_summary_headline_container -->

        <div class="campaign_summary_panels_container">

            <div
                ng-if="settlement.user_assets.survivors.length == 0"
                class="kd_alert user_asset_sheet_error"
            >
                    <b>{{settlement.sheet.name}}</b> does not have any survivors!
                    Use the navigation menu controls in the upper left to add new survivors.
            </div>

            <div
                class="campaign_summary_survivors_container"
                ng-if="settlement.user_assets.survivors.length >= 1"
                ng-controller="survivorManagementController"
            >

                <h2>- Survivors - </h2>
                <p class="subtitle">Tap or click a survivor for management options.</p>

                <center
                    id="waitingForSurvivors" class=""
                    ng-if="settlement.user_assets.survivor_groups.length > 1"
                >
                    <img src="/media/loading_io.gif"/>
                    <p class="subtitle">Summarizing {{settlement.user_assets.survivors.length}} survivors...</p>
                </center>

                <div
                    class="campaign_summary_survivors_group"
                    ng-repeat="group in settlement.user_assets.survivor_groups"
                    ng-if="group.survivors.length >= 1 && user != undefined"
                    ng-init="
                        containerID = group.handle + '_container';
                        group.arrow = false;
                    "
                >
                    <span ng-init="fadeSurvivorGroupsLoader()"></span>

                    <h3 title="group.title_tip" ng-click="showHide(containerID); flipArrow(group)" class="clickable {{group.handle}}">
                        <span ng-if="group.arrow == true || group.arrow == undefined">
                            &#x25B2;
                        </span>
                        <span ng-if="group.arrow == false">
                            &#x25BC;
                        </span>

                        {{group.name}} ({{group.survivors.length}})
                    </h3>

                    <div id="{{containerID}}" >

                        <div
                            class="campaign_summary_survivor_container {{group.handle}}"
                            ng-repeat="s in group.survivors"
                            ng-init="initSurvivorCard(s)"
                        >
                            <button
                                class="campaign_summary_survivor {{group.handle}}"
                                ng-click="showSurvivorControls(s)"
                                ng-class="{
                                    disabled: s.meta.manageable == false,
                                    survivor_sheet_gradient: s.meta.manageable == true,
                                    dead_survivor_gradient: s.sheet.dead == true,
                                    affinity_red: s.sheet.savior == 'red',
                                    affinity_green: s.sheet.savior == 'green',
                                    affinity_blue: s.sheet.savior == 'blue',
                                }"
                                style='{{settlement.survivor_color_schemes[s.sheet.color_scheme].style_string}}'
                            >
                                <div
                                    ng-if="s.meta.returning_survivor == true && s.sheet.dead != true"
                                    class="campaign_summary_survivor_returning_flash"
                                >
                                    Returning Survivor
                                </div>

                                <div class="avatar_and_summary">
                                    <div class="avatar">
                                        <span class="death_x" ng-if="s.sheet.dead == true">
                                            X
                                        </span>
                                        <img
                                            class="campaign_summary_avatar"
                                            ng-if="s.sheet.avatar != undefined"
                                            ng-src="/get_image?id={{s.sheet.avatar.$oid}}"
                                        />
                                        <img
                                            class="campaign_summary_avatar"
                                            ng-if="s.sheet.avatar == undefined"
                                            ng-src="/media/default_avatar_{{s.sheet.effective_sex}}.png"
                                        />
                                    </div>
                                    <div class="summary">
                                        <div
                                            class="name"
                                            ng-class="{maroon_text: s.sheet.dead == true}"
                                        >
                                            <b>{{s.sheet.name}}</b> [{{s.sheet.effective_sex}}]
                                        </div>

                                        <div class="epithets">
                                            <span ng-repeat="e in s.sheet.epithets">
                                                {{settlement.game_assets.epithets[e].name}}{{$last ? '' : ', '}}
                                            </span>
                                        </div>
                                        <div class="attr_holder">
                                            <div class="attr maroon_text" ng-if="s.sheet.dead == true">
                                                <b>Died in Lantern Year {{s.sheet.died_in}} </b>
                                            </div>
                                            <div class="attr COD maroon_text" ng-if="s.sheet.dead == true">
                                                Cause of death: {{s.sheet.cause_of_death}}
                                            </div>
                                            <div class="attr">Hunt XP: {{s.sheet.hunt_xp}}</div>
                                            <div class="attr">Survival: {{s.sheet.survival}}</div>
                                            <div class="attr" ng-class="{maroon_text: s.sheet.Insanity >= 3}">Insanity: {{s.sheet.Insanity}}</div>
                                            <div class="attr">Courage: {{s.sheet.Courage}}</div>
                                            <div class="attr">Understanding: {{s.sheet.Understanding}}</div>
                                        </div> <!-- attr_holder -->

                                    </div> <!-- summary -->
                                </div> <!-- avatar_and_summary -->

                                <div class="campaign_summary_survivor_tags_container">
                                    <div
                                        class="survivor_tag fighting_arts_tag"
                                        ng-repeat="fa in s.sheet.fighting_arts"
                                    >
                                        {{settlement.game_assets.fighting_arts[fa].name}}
                                    </div>
                                </div>
                                <div class="campaign_summary_survivor_tags_container">
                                    <div
                                        class="survivor_tag disorders_tag"
                                        ng-repeat="d in s.sheet.disorders"
                                    >
                                        {{settlement.game_assets.disorders[d].name}}
                                    </div>
                                </div>
                                <div class="campaign_summary_survivor_tags_container">
                                    <div
                                        class="survivor_tag ai_tag {{settlement.game_assets.abilities_and_impairments[ai].sub_type}}"
                                        ng-repeat="ai in s.sheet.abilities_and_impairments track by $index"
                                    >
                                        {{settlement.game_assets.abilities_and_impairments[ai].name}}
                                    </div>
                                </div>

                                <div class="campaign_summary_survivor_tags_container">
                                    <div
                                        class="survivor_tag status_tag"
                                        ng-repeat="flag in settlement.survivor_status_flags"
                                        ng-if="s.sheet[flag.handle] == true"
                                    >
                                        {{flag.name}}
                                    </div>
                                </div>


                                <div
                                    ng-if="s.sheet.constellation != undefined"
                                    class="campaign_summary_survivor_constellation dragon_king"
                                >
                                    {{s.sheet.constellation}}
                                </div>


                            </button>

<div
    id="{{s.sheet._id.$oid}}_modal_controls"
    class="hidden modal survivor_controls modal-black"
>
    <div
        class="kd_sheet_ui_outer_ring_container"
        style='{{settlement.survivor_color_schemes[s.sheet.color_scheme].style_string}}'
    >
        <div
            class="kd_sheet_ui_inner_ring_container survivor_quickview_container"
            ng-init="
                survivalBoxID = 'survivalControl' + s.sheet._id.$oid;
                brainBoxID = 'brainControl' + s.sheet._id.$oid;
                headBoxID = 'headControl' + s.sheet._id.$oid;
                armsBoxID = 'armsControl' + s.sheet._id.$oid;
                bodyBoxID = 'bodyControl' + s.sheet._id.$oid;
                waistBoxID = 'waistControl' + s.sheet._id.$oid;
                legsBoxID = 'legsControl' + s.sheet._id.$oid;
                huntXPBoxID = 'huntXPControl' + s.sheet._id.$oid;
                weaponProficiencyBoxID = 'weaponProficiencyControl' + s.sheet._id.$oid;
                courageBoxID = 'courageControl' + s.sheet._id.$oid;
                understandingBoxID = 'understandingControl' + s.sheet._id.$oid;
                attrib_list = ['Movement','Accuracy','Strength','Evasion','Luck','Speed'];
            "
        >
            <div class="columns">
                <div class="left_column">

                    <div class="quickview_survivor_name">
                        {{s.sheet.name}}
                        <div class="quickview_sex_box">
                            M <div class="kd_sheet_ui_box" ng-class="{checked: s.sheet.effective_sex == 'M'}"></div>
                            F <div class="kd_sheet_ui_box" ng-class="{checked: s.sheet.effective_sex == 'F'}"></div>
                        </div>
                    </div> <!-- name and sex -->

                    <div
                        class="quickview_survival_container border_box"
                    >
                        <div
                            class="survival_box_number_container clickable"
                            ng-click="rollUp(survivalBoxID)"
                        >
                            <input
                                class="survival_box_number"
                                type="number"
                                ng-model="s.sheet.survival"
                                min="0"
                            />
                        </div>
                        <div class="survival_box_title_and_lock">
                            <div
                                class="survival_box_title clickable"
                                ng-click="rollUp(survivalBoxID)"
                            >
                                Survival
                            </div>
                            <div
                                class="survival_box_lock clickable"
                                ng-click="toggleSurvivorFlag(s, 'cannot_spend_survival')"
                            >
                                <div
                                    class="kd_sheet_ui_box"
                                    ng-class="{checked: s.sheet.cannot_spend_survival == true}"
                                >
                                </div>
                                &#x1f512; Cannot spend survival.
                            </div>
                        </div>
                        <div
                            class="survival_box_survival_actions_container"
                            ng-click="rollUp(survivalBoxID)"
                        >
                            <div
                                class="survival_box_survival_action_item"
                                ng-repeat="sa in s.survival_actions"
                            >
                                <div
                                    class="kd_sheet_ui_box"
                                    ng-class="{checked: sa.available == true}"
                                >
                                </div>
                                <span class="sa_name">{{sa.name}}</span>
                            </div>
                        </div>
                    </div> <!-- quickview_survival_box -->
                    <div
                        id="{{survivalBoxID}}"
                        class="kd_sheet_ui_roll_down rolled_up"
                    >
                        <div class="kd_sheet_ui_roll_down_controls">
                            <div
                                class="kd_sheet_ui_row_tip"
                                ng-if="settlement.sheet.enforce_survival_limit == true"
                            >
                                {{settlement.sheet.name}} Survival Limit is <b>{{settlement.sheet.survival_limit}}</b>!
                            </div>
                            <div class="kd_sheet_ui_number_tumbler">
                                <button ng-click="s.sheet.survival = s.sheet.survival + 1">
                                    &#x25B2;
                                </button>
                                <button ng-click="s.sheet.survival = s.sheet.survival - 1">
                                    &#x25BC;
                                </button>
                                <button
                                    class="kd_blue"
                                    ng-click="setSurvivorAttribute(s, 'survival'); rollUp(survivalBoxID)"
                                >
                                    Save Changes
                                </button>
                            </div> <!-- number tumbler -->
                        </div>
                    </div>

            <div
                class="quickview_attributes_container border_box"
            >
                <div
                    ng-repeat="A in attrib_list"
                    class="quickview_attribute_box clickable {{A}}"
                    ng-class="{last: $last}"
                    ng-click="rollUp(A + 'BoxID' + s.sheet._id.$oid)"
                >
                    <input
                        class="attribute_box_number"
                        type="number"
                        ng-value="s.sheet[A] + s.sheet.attribute_detail[A].tokens + s.sheet.attribute_detail[A].gear"
                        ng-class="{
                            maroon_text: s.sheet[A] + s.sheet.attribute_detail[A].tokens + s.sheet.attribute_detail[A].gear < s.sheet[A],
                            green_text: s.sheet[A] + s.sheet.attribute_detail[A].tokens + s.sheet.attribute_detail[A].gear > s.sheet[A],
                        };"
                    />
                    {{A}}
                </div>
            </div>
            <div
                ng-repeat="A in attrib_list"
                id="{{A}}BoxID{{s.sheet._id.$oid}}"
                class="kd_sheet_ui_roll_down rolled_up"
            >
                <div class="kd_sheet_ui_roll_down_controls quickview_attribute_tumblers_container {{A}}">
                    <div class="quickview_attribute_tumbler">
                        <button ng-click="s.sheet[A] = s.sheet[A] + 1">
                            &#x25B2;
                        </button>
                        <input
                            type="number"
                            ng-model="s.sheet[A]"
                        />
                        <button ng-click="s.sheet[A] = s.sheet[A] - 1">
                            &#x25BC;
                        </button>
                        Base
                    </div>
                    <div class="quickview_attribute_tumbler">
                        <button ng-click="s.sheet.attribute_detail[A].gear = s.sheet.attribute_detail[A].gear + 1">
                            &#x25B2;
                        </button>
                        <input
                            type="number"
                            ng-model="s.sheet.attribute_detail[A].gear"
                        />
                        <button ng-click="s.sheet.attribute_detail[A].gear = s.sheet.attribute_detail[A].gear - 1">
                            &#x25BC;
                        </button>
                        Gear
                    </div>
                    <div class="quickview_attribute_tumbler">
                        <button ng-click="s.sheet.attribute_detail[A].tokens = s.sheet.attribute_detail[A].tokens + 1">
                            &#x25B2;
                        </button>
                        <input
                            type="number"
                            ng-model="s.sheet.attribute_detail[A].tokens"
                        />
                        <button ng-click="s.sheet.attribute_detail[A].tokens = s.sheet.attribute_detail[A].tokens - 1">
                            &#x25BC;
                        </button>
                        Tokens
                    </div>
                </div>
                <button
                    class="kd_blue quickview_attribute_tumbler_save"
                    ng-click="rollUp(A + 'BoxID' + s.sheet._id.$oid); setSurvivorAttributes(s, A)"
                >
                    Save {{A}}
                </button>
            </div>

            <div class="quickview_brain_container border_box">
                <div
                    class="quickview_brain_box clickable"
                    ng-click="rollUp(brainBoxID)"
                >
                    <input
                        class="quickview_shield"
                        type="number"
                        ng-model="s.sheet.Insanity"
                        ng-class="{maroon_text: s.sheet.Insanity >= 3}"
                        min="0"
                    />
                    Insanity
                </div>
                <div
                    class="quickview_hitbox_detail brain clickable"
                    ng-click="rollUp(brainBoxID)"
                >
                    <div class="title">
                        Brain
                    </div>
                    <div
                        class="tip"
                        ng-class="{maroon_text: s.sheet.Insanity >= 3}"
                    >
                        If your insanity is 3+, you are <b>insane</b>.
                    </div>
                </div>
                <div class="quickview_hitbox_boxes brain">
                    <div
                        class="clickable damage_box"
                        ng-class="{checked: s.sheet.brain_damage_light != undefined}"
                        ng-click="toggleDamage(s, 'brain_damage_light');"
                     /></div>
                </div>
            </div>
            <div
                id="{{brainBoxID}}"
                class="kd_sheet_ui_roll_down rolled_up"
            >
                <div class="kd_sheet_ui_roll_down_controls">
                    <div class="kd_sheet_ui_number_tumbler">
                        <button ng-click="s.sheet.Insanity = s.sheet.Insanity + 1">
                            &#x25B2;
                        </button>
                        <button ng-click="s.sheet.Insanity = s.sheet.Insanity - 1">
                            &#x25BC;
                        </button>
                        <button
                            class="kd_blue"
                            ng-click="setSurvivorAttribute(s, 'Insanity'); rollUp(brainBoxID)"
                        >
                            Save Changes
                        </button>
                    </div> <!-- number tumbler -->
                </div>
            </div>

            <!-- head -->
            <div class="quickview_hitbox_container">
                <div
                    class="quickview_armor_box clickable"
                    ng-click="rollUp(headBoxID)"
                >
                    <input
                        class="quickview_shield"
                        type="number"
                        min="0"
                        ng-model="s.sheet.Head"
                    />
                </div>
                <div
                    class="quickview_hitbox_detail"
                    ng-click="rollUp(headBoxID)"
                >
                    <div class="title">
                        <font class="kdm_font_hit_locations">b</font> Head
                    </div>
                    <div class="tip">
                        Heavy Injury: Knocked Down.
                    </div>
                </div>
                <div class="quickview_hitbox_boxes">
                    <div
                        class="clickable heavy damage_box"
                        ng-class="{checked: s.sheet.head_damage_heavy != undefined}"
                        ng-click="toggleDamage(s, 'head_damage_heavy');"
                     /></div>
                </div>
            </div>
            <div
                id="{{headBoxID}}"
                class="kd_sheet_ui_roll_down rolled_up"
            >
                <div class="kd_sheet_ui_roll_down_controls">
                    <div class="kd_sheet_ui_number_tumbler">
                        <button ng-click="s.sheet.Head = s.sheet.Head + 1">
                            &#x25B2;
                        </button>
                        <button ng-click="s.sheet.Head = s.sheet.Head - 1">
                            &#x25BC;
                        </button>
                        <button
                            class="kd_blue"
                            ng-click="setSurvivorAttribute(s, 'Head'); rollUp(headBoxID)"
                        >
                            Save Changes
                        </button>
                    </div> <!-- number tumbler -->
                </div>
            </div>
            <hr/>

            <!-- arms -->
            <div class="quickview_hitbox_container">
                <div
                    class="quickview_armor_box clickable"
                    ng-click="rollUp(armsBoxID)"
                >
                    <input
                        class="quickview_shield" type="number" min="0" ng-model="s.sheet.Arms"
                    />
                </div>
                <div
                    class="quickview_hitbox_detail"
                    ng-click="rollUp(armsBoxID)"
                >
                    <div class="title">
                        <font class="kdm_font_hit_locations">d</font> Arms
                    </div>
                    <div class="tip">Heavy Injury: Knocked Down.</div>
                </div>
                <div class="quickview_hitbox_boxes">
                    <div
                        class="clickable damage_box"
                        ng-class="{checked: s.sheet.arms_damage_light != undefined}"
                        ng-click="toggleDamage(s, 'arms_damage_light');"
                     /></div>
                    <div
                        class="clickable heavy damage_box"
                        ng-class="{checked: s.sheet.arms_damage_heavy != undefined}"
                        ng-click="toggleDamage(s, 'arms_damage_heavy');"
                     /></div>
                </div>
            </div>
            <div
                id="{{armsBoxID}}"
                class="kd_sheet_ui_roll_down rolled_up"
            >
                <div class="kd_sheet_ui_roll_down_controls">
                    <div class="kd_sheet_ui_number_tumbler">
                        <button ng-click="s.sheet.Arms = s.sheet.Arms + 1">&#x25B2;</button>
                        <button ng-click="s.sheet.Arms = s.sheet.Arms - 1">&#x25BC;</button>
                        <button
                            class="kd_blue"
                            ng-click="setSurvivorAttribute(s, 'Arms'); rollUp(armsBoxID)"
                        >
                            Save Changes
                        </button>
                    </div> <!-- number tumbler -->
                </div>
            </div>
            <hr/>

            <!-- body -->
            <div class="quickview_hitbox_container">
                <div
                    class="quickview_armor_box clickable"
                    ng-click="rollUp(bodyBoxID)"
                >
                    <input
                        class="quickview_shield" type="number" min="0" ng-model="s.sheet.Body"
                    />
                </div>
                <div
                    class="quickview_hitbox_detail"
                    ng-click="rollUp(bodyBoxID)"
                >
                    <div class="title">
                        <font class="kdm_font_hit_locations">c</font> Body
                    </div>
                    <div class="tip">Heavy Injury: Knocked Down.</div>
                </div>
                <div class="quickview_hitbox_boxes">
                    <div
                        class="clickable damage_box"
                        ng-class="{checked: s.sheet.body_damage_light != undefined}"
                        ng-click="toggleDamage(s, 'body_damage_light');"
                     /></div>
                    <div
                        class="clickable heavy damage_box"
                        ng-class="{checked: s.sheet.body_damage_heavy != undefined}"
                        ng-click="toggleDamage(s, 'body_damage_heavy');"
                     /></div>
                </div>
            </div>
            <div
                id="{{bodyBoxID}}"
                class="kd_sheet_ui_roll_down rolled_up"
            >
                <div class="kd_sheet_ui_roll_down_controls">
                    <div class="kd_sheet_ui_number_tumbler">
                        <button ng-click="s.sheet.Body = s.sheet.Body + 1">&#x25B2;</button>
                        <button ng-click="s.sheet.Body = s.sheet.Body - 1">&#x25BC;</button>
                        <button
                            class="kd_blue"
                            ng-click="setSurvivorAttribute(s, 'Body'); rollUp(bodyBoxID)"
                        >
                            Save Changes
                        </button>
                    </div> <!-- number tumbler -->
                </div>
            </div>
            <hr/>

            <!-- waist -->
            <div class="quickview_hitbox_container">
                <div
                    class="quickview_armor_box clickable"
                    ng-click="rollUp(waistBoxID)"
                >
                    <input
                        class="quickview_shield" type="number" min="0" ng-model="s.sheet.Waist"
                    />
                </div>
                <div
                    class="quickview_hitbox_detail"
                    ng-click="rollUp(waistBoxID)"
                >
                    <div class="title">
                        <font class="kdm_font_hit_locations">e</font> Waist
                    </div>
                    <div class="tip">Heavy Injury: Knocked Down.</div>
                </div>
                <div class="quickview_hitbox_boxes">
                    <div
                        class="clickable damage_box"
                        ng-class="{checked: s.sheet.waist_damage_light != undefined}"
                        ng-click="toggleDamage(s, 'waist_damage_light');"
                     /></div>
                    <div
                        class="clickable heavy damage_box"
                        ng-class="{checked: s.sheet.waist_damage_heavy != undefined}"
                        ng-click="toggleDamage(s, 'waist_damage_heavy');"
                     /></div>
                </div>
            </div>
            <div
                id="{{waistBoxID}}"
                class="kd_sheet_ui_roll_down rolled_up"
            >
                <div class="kd_sheet_ui_roll_down_controls">
                    <div class="kd_sheet_ui_number_tumbler">
                        <button ng-click="s.sheet.Waist = s.sheet.Waist + 1">&#x25B2;</button>
                        <button ng-click="s.sheet.Waist = s.sheet.Waist - 1">&#x25BC;</button>
                        <button
                            class="kd_blue"
                            ng-click="setSurvivorAttribute(s, 'Waist'); rollUp(waistBoxID)"
                        >
                            Save Changes
                        </button>
                    </div> <!-- number tumbler -->
                </div>
            </div>
            <hr/>

            <!-- legs -->
            <div class="quickview_hitbox_container">
                <div
                    class="quickview_armor_box clickable"
                    ng-click="rollUp(legsBoxID)"
                >
                    <input
                        class="quickview_shield" type="number" min="0" ng-model="s.sheet.Legs"
                    />
                </div>
                <div
                    class="quickview_hitbox_detail"
                    ng-click="rollUp(legsBoxID)"
                >
                    <div class="title">
                        <font class="kdm_font_hit_locations">f</font> Legs
                    </div>
                    <div class="tip">Heavy Injury: Knocked Down.</div>
                </div>
                <div class="quickview_hitbox_boxes">
                    <div
                        class="clickable damage_box"
                        ng-class="{checked: s.sheet.legs_damage_light != undefined}"
                        ng-click="toggleDamage(s, 'legs_damage_light');"
                     /></div>
                    <div
                        class="clickable heavy damage_box"
                        ng-class="{checked: s.sheet.legs_damage_heavy != undefined}"
                        ng-click="toggleDamage(s, 'legs_damage_heavy');"
                     /></div>
                </div>
            </div>
                    <div
                        id="{{legsBoxID}}"
                        class="kd_sheet_ui_roll_down rolled_up"
                    >
                        <div class="kd_sheet_ui_roll_down_controls">
                            <div class="kd_sheet_ui_number_tumbler">
                                <button ng-click="s.sheet.Legs = s.sheet.Legs + 1">&#x25B2;</button>
                                <button ng-click="s.sheet.Legs = s.sheet.Legs - 1">&#x25BC;</button>
                                <button
                                    class="kd_blue"
                                    ng-click="setSurvivorAttribute(s, 'Legs'); rollUp(legsBoxID)"
                                >
                                    Save Changes
                                </button>
                            </div> <!-- number tumbler -->
                        </div>
                    </div>
                    <hr/>

                </div><!-- left_column -->

                <div class="right_column">

                    <!-- hunt xp-->
                    <div
                        class="quickview_secondary_container hunt_xp clickable"
                        ng-click="rollUp(huntXPBoxID)"
                    >
                        Hunt XP
                        <div
                            class="secondary_attrib_box_row hunt_xp"
                            ng-init="huntXPBoxes = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]"
                        >
                            <div
                                class="kd_sheet_ui_box"
                                ng-repeat = "b in huntXPBoxes"
                                ng-class="{
                                    checked: s.sheet.hunt_xp >= b,
                                    heavy: [2,6,10,15,16].indexOf(b) != -1,
                                }"
                            >
                            </div>
                        </div>
                    </div> <!-- Hunt XP -->
                    <div
                        id="{{huntXPBoxID}}"
                        class="kd_sheet_ui_roll_down rolled_up"
                    >
                        <div class="kd_sheet_ui_roll_down_controls">
                            <div class="kd_sheet_ui_number_tumbler">
                                <button ng-click="s.sheet.hunt_xp = s.sheet.hunt_xp + 1">
                                    &#x25B2;
                                </button>
                                <button ng-click="s.sheet.hunt_xp = s.sheet.hunt_xp - 1">
                                    &#x25BC;
                                </button>
                                <button
                                    class="kd_blue"
                                    ng-click="setSurvivorAttribute(s, 'hunt_xp'); rollUp(huntXPBoxID)"
                                >
                                    Save Changes
                                </button>
                            </div> <!-- number tumbler -->
                        </div>
                    </div>

                    <!-- weapon prof -->
                    <div
                        class="quickview_secondary_container weapon_proficiency clickable border_box"
                        ng-click="rollUp(weaponProficiencyBoxID)"
                    >
                        Weapon Proficiency
                        <div
                            class="secondary_attrib_box_row"
                            ng-init="wpBoxes = [1,2,3,4,5,6,7,8]"
                        >
                            <div class="weapon_proficiency_type">
                                <b>Type</b>:
                                <span class="null_weapon_proficiency" ng-if="s.sheet.weapon_proficiency_type == undefined"></span>
                                <span ng-if="s.sheet.weapon_proficiency_type != undefined">
                                    {{settlement.game_assets.weapon_proficiency_types[s.sheet.weapon_proficiency_type].name}}
                                </span>
                            </div>
                            <div
                                class="kd_sheet_ui_box"
                                ng-repeat = "b in wpBoxes"
                                ng-class="{
                                    checked: s.sheet['Weapon Proficiency'] >= b,
                                    heavy: [3,8].indexOf(b) != -1,
                                }"
                            >
                            </div>
                        </div>
                    </div>
                    <div
                        id="{{weaponProficiencyBoxID}}"
                        class="kd_sheet_ui_roll_down rolled_up"
                    >
                        <div class="kd_sheet_ui_roll_down_controls">
                            <div
                                class="kd_sheet_ui_row_tip"
                                ng-if="
                                    s.sheet.weapon_proficiency_type == undefined &&
                                    user.user.preferences.show_ui_tips
                                "
                            >
                                Use the controls on the <b>Survivor Sheet</b> to set the Weapon Proficiency type for {{s.sheet.name}}.
                            </div>
                            <div class="kd_sheet_ui_number_tumbler">
                                <button ng-click="s.sheet['Weapon Proficiency'] = s.sheet['Weapon Proficiency'] + 1">
                                    &#x25B2;
                                </button>
                                <button ng-click="s.sheet['Weapon Proficiency'] = s.sheet['Weapon Proficiency'] - 1">
                                    &#x25BC;
                                </button>
                                <button
                                    class="kd_blue"
                                    ng-click="setSurvivorAttribute(s, 'Weapon Proficiency'); rollUp(weaponProficiencyBoxID)"
                                >
                                    Save Changes
                                </button>
                            </div> <!-- number tumbler -->
                        </div>
                    </div>

                    <!-- Courage -->
                    <div
                        class="quickview_secondary_container courage clickable border_box"
                        ng-click="rollUp(courageBoxID)"
                    >
                        Courage
                        <div
                            class="secondary_attrib_box_row courage"
                            ng-init="courageBoxes = [1,2,3,4,5,6,7,8,9]"
                        >
                            <div
                                class="kd_sheet_ui_box"
                                ng-repeat = "b in courageBoxes"
                                ng-class="{
                                    checked: s.sheet.Courage >= b,
                                    heavy: [3,9].indexOf(b) != -1,
                                }"
                            >
                            </div>
                        </div>
                    </div>
                    <div
                        id="{{courageBoxID}}"
                        class="kd_sheet_ui_roll_down rolled_up"
                    >
                        <div class="kd_sheet_ui_roll_down_controls">
                            <div class="kd_sheet_ui_number_tumbler">
                                <button ng-click="s.sheet.Courage = s.sheet.Courage + 1">
                                    &#x25B2;
                                </button>
                                <button ng-click="s.sheet.Courage = s.sheet.Courage - 1">
                                    &#x25BC;
                                </button>
                                <button
                                    class="kd_blue"
                                    ng-click="setSurvivorAttribute(s, 'Courage'); rollUp(courageBoxID)"
                                >
                                    Save Courage
                                </button>
                            </div> <!-- number tumbler -->
                        </div>
                    </div>

                    <!-- Understanding -->
                    <div
                        class="quickview_secondary_container understanding clickable border_box"
                        ng-click="rollUp(understandingBoxID)"
                    >
                        Understanding
                        <div
                            class="secondary_attrib_box_row understanding"
                            ng-init="understandingBoxes = [1,2,3,4,5,6,7,8,9]"
                        >
                            <div
                                class="kd_sheet_ui_box"
                                ng-repeat = "b in understandingBoxes"
                                ng-class="{
                                    checked: s.sheet.Understanding >= b,
                                    heavy: [3,9].indexOf(b) != -1,
                                }"
                            >
                            </div>
                        </div>
                    </div>
                    <div
                        id="{{understandingBoxID}}"
                        class="kd_sheet_ui_roll_down rolled_up"
                    >
                        <div class="kd_sheet_ui_roll_down_controls">
                            <div class="kd_sheet_ui_number_tumbler">
                                <button ng-click="s.sheet.Understanding = s.sheet.Understanding + 1">
                                    &#x25B2;
                                </button>
                                <button ng-click="s.sheet.Understanding = s.sheet.Understanding - 1">
                                    &#x25BC;
                                </button>
                                <button
                                    class="kd_blue"
                                    ng-click="setSurvivorAttribute(s, 'Understanding'); rollUp(understandingBoxID)"
                                >
                                    Save Understanding
                                </button>
                            </div> <!-- number tumbler -->
                        </div>
                    </div>

                    <!-- Fighting Arts -->
                    <div
                        class="quickview_secondary_container fighting_arts"
                    >
                        <div class="quickview_asset_list_title_bar">
                            <div class="title">Fighting Arts</div>
                            <div class="subtitle">Maximum 3.</div>
                            <div
                                class="lockbox clickable"
                                ng-click="toggleSurvivorFlag(s, 'cannot_use_fighting_arts')"
                            >
                                <div
                                    class="kd_sheet_ui_box"
                                    ng-class="{checked: s.sheet.cannot_use_fighting_arts == true}"
                                >
                                </div>
                                &#x1f512; Cannot use Fighting Arts
                            </div>
                        </div>
                        <ul class="quickview_asset_list">
                            <li
                                ng-repeat="fa in s.sheet.fighting_arts"
                                ng-class="{true: 'faded'}[s.sheet.cannot_use_fighting_arts]"
                            >
                                <b>{{settlement.game_assets.fighting_arts[fa].name}}:</b>
                                <span ng-bind-html="settlement.game_assets.fighting_arts[fa].desc|trustedHTML"></span>
                                <br/>
                            </li>
                        </ul>
                    </div> <!-- fighting arts -->
                    <hr/>

                    <!-- Disorders -->
                    <div
                        class="quickview_secondary_container disorders"
                    >
                        <div class="quickview_asset_list_title_bar">
                            <div class="title">Disorders</div>
                            <div class="subtitle">Maximum 3.</div>
                        </div>
                        <ul class="quickview_asset_list">
                            <li
                                ng-repeat="d in s.sheet.disorders"
                            >
                                <b>{{settlement.game_assets.disorders[d].name}}:</b>
                                <span ng-bind-html="settlement.game_assets.disorders[d].survivor_effect|trustedHTML"></span>
                                <br/>
                            </li>
                        </ul>
                    </div> <!-- disorders -->
                    <hr/>

                    <!-- A&I -->
                    <div
                        class="quickview_secondary_container fighting_arts"
                    >
                        <div class="quickview_asset_list_title_bar">
                            <div class="title">Abilities & Impairments</div>
                            <div
                                class="lockbox clickable skip_next_hunt"
                                ng-click="toggleSurvivorFlag(s, 'skip_next_hunt')"
                            >
                                <div
                                    class="kd_sheet_ui_box"
                                    ng-class="{checked: s.sheet.skip_next_hunt == true}"
                                >
                                </div>
                                &#x1f512; Skip Next Hunt
                            </div>
                        </div>
                        <ul class="quickview_asset_list">
                            <li
                                ng-repeat="ai in s.sheet.abilities_and_impairments"
                            >
                                <b>{{settlement.game_assets.abilities_and_impairments[ai].name}}:</b>
                                <span ng-bind-html="settlement.game_assets.abilities_and_impairments[ai].desc|trustedHTML"></span>
                                <br/>
                            </li>
                        </ul>
                    </div> <!-- AI -->

                </div><!-- right column -->

            </div><!-- columns -->

        <div class="quickview_ui_button_container">
            <form action="" method="POST" class="edit_survivor_sheet">
                <input type="hidden" name="view_survivor" value="{{s.sheet._id.$oid}}" />
                <button
                    class="quickview_ui_button settlement_sheet_gradient"
                    onclick="showFullPageLoader()"
                    ng-click="showHide(s.sheet._id.$oid + '_modal_controls');"
                >
                    Edit <b>Survivor Sheet</b>
                >
                </button>
            </form>
            <select
                class="campaign_summary_survivor_modal_color_scheme_select"
                ng-if="user.user.subscriber.level > 1"
                ng-model="s.sheet.color_scheme"
                ng-change="setColorScheme(s);"
                ng-options="c.handle as c.name for c in settlement.survivor_color_schemes"
            >
                <option disabled value="">Set Color Scheme</option>
            </select>
            <div
                ng-if="
                    group.handle == 'available' ||
                    group.handle == 'favorite' ||
                    group.handle == 'departing'
                "
                class="departing_survivor_conditional"
            >
                <button
                   ng-if="s.sheet.departing == true"
                   ng-click="
                       toggleDepartingStatus(s);
                       showHide(s.sheet._id.$oid + '_modal_controls');
                   "
                   class="quickview_ui_button departing_toggle"
                >
                    Leave <b>Departing</b> Survivors
                </button>
                <button
                    ng-if="s.sheet.departing != true"
                    ng-click="
                        toggleDepartingStatus(s);
                        showHide(s.sheet._id.$oid + '_modal_controls');
                    "
                    class="quickview_ui_button departing_toggle"
                >
                    Join <b>Departing</b> Survivors
                </button>
            </div> <!-- conditional departing toggle -->
            <div class="back_button_holder">
                <button
                    class="quickview_ui_button"
                    ng-click="showHide(s.sheet._id.$oid + '_modal_controls')"
                >
                    Back
                </button>
            </div>
        </div> <!-- kd_sheet_ui_innter_ring_container -->
    </div> <!-- kd_sheet_ui_outer_ring_container-->
</div> <!-- quick view modal -->


                        </div>
                        </div> <!-- survivor container -->

                    </div><!-- show/hide container -->
                </div> <!-- survivors_group -->

            </div> <!-- campaign_summary_survivors_container -->

            <div class="campaign_summary_facts_box" ng-if="settlement != undefined">

                <div
                    ng-repeat="r in settlement.campaign.special_rules"
                    class="campaign_summary_special_rule"
                    style="background-color: #{{r.bg_color}}; color: #{{r.font_color}}"
                >
                    <h3>{{r.name}}</h3>
                    <span ng-bind-html="r.desc|trustedHTML"></span>
                </div>
                <div
                    ng-if="
                        user_is_settlement_admin &&
                        user.user.preferences.show_endeavor_token_controls != false
                    "
                    class="campaign_summary_small_box"
                >
                    <div
                        title="Manage settlement Endeavor tokens here! Settlement admins may use the controls at the right to increment or decrement the total number of tokens!"
                        class="campaign_summary_endeavor_controller"
                        ng-controller="endeavorController"
                    >

                        <span ng-if="settlement.sheet.endeavor_tokens >= 1">
                            <div
                                class="tokens"
                            >
                                <img
                                    ng-repeat="e in range(settlement.sheet.endeavor_tokens)"
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
                            ng-if="settlement.sheet.endeavor_tokens <= 0"
                            ng-click="addToken()"
                            class="endeavor_controls_toggle settlement_sheet_block_group clickable"
                        >
                            <h4>- Endeavor Tokens -</h4>
                            <span>Click or tap here to manage Endeavor Tokens.</span>
                        </div>

                        <div class="endeavor_controls_clear_div"></div>

                    </div>

                </div> <!-- show_endeavor_controls -->

            <div
                class="campaign_summary_small_box"
                ng-if="settlement.sheet.lantern_research_level >= 1"
            >
                <h4 class="pulse_discoveries">- Pulse Discoveries -</h4>
                <div
                    class="pulse_discovery"
                    ng-repeat="d in settlement.game_assets.pulse_discoveries"
                    ng-if="settlement.sheet.lantern_research_level >= d.level"
                    style="background-color: {{d.bgcolor}}"
                >
                    <div class="pd_level_container">
                        <div class="pd_level">{{d.level}}</div>
                    </div>
                    <div class="pd_text">
                        <b>{{d.name}}</b>
                        <span ng-if="d.subtitle != undefined"> - {{d.subtitle}}</span>
                        <br/>
                        {{d.desc}}
                    </div>
                </div><!-- repeater -->
            </div> <!-- pulse discoveries -->

            <div
                class="campaign_summary_small_box endeavor_box"
                ng-controller='availableEndeavorsController'
                ng-if="settlement.campaign.endeavor_count > 0"
            >
                <h4>- Available Endeavors ({{settlement.campaign.endeavor_count}}) -</h4>

                <!-- campaign-specific endeavors -->
                <div
                    ng-repeat="i in settlement.campaign.endeavors.campaign"
                >
                    <h5><b>{{i['name']}}</b>:</h5>
                    <div
                        ng-repeat="e_handle in i.endeavors"
                        ng-init="e = settlement.game_assets.endeavors[e_handle]"
                        class="campaign_summary_endeavor_container {{e.class}}"
                    >
                        <div class="endeavor_cost {{e.class}}">
                            <img ng-repeat="c in range(e.cost)" src="/media/icons/endeavor_star.png" class="endeavor_cost">
                        </div>
                        <div class="endeavor_text">
                            <b ng-if="e.name != undefined">{{e.name}}</b>
                            <span ng-if="e.name != undefined && e.desc != undefined"> - </span>
                            <span ng-bind-html="e.desc|trustedHTML"></span>
                        </div>
                        <div ng-if="e.cost_detail != undefined" class="cost_detail {{e.cost_detail_type}}_cost_detail">
                            <div ng-repeat="i in e.cost_detail">
                                {{i}}
                            </div>
                        </div>
                    </div> <!-- endeavor container -->
                </div> <!-- campaign-specific endeavors -->

                <!-- innovations -->
                <div
                    ng-repeat="i in settlement.campaign.endeavors.innovations"
                >
                    <h5><b>{{settlement.game_assets.innovations[i['handle']].name}}</b> ({{settlement.game_assets.innovations[i['handle']].innovation_type}}):</h5>
                    <div
                        ng-repeat="e_handle in i.endeavors"
                        ng-init="e = settlement.game_assets.endeavors[e_handle]"
                        class="campaign_summary_endeavor_container {{e.class}}"
                    >
                        <div class="endeavor_cost {{e.class}}">
                            <img ng-repeat="c in range(e.cost)" src="/media/icons/endeavor_star.png" class="endeavor_cost">
                        </div>
                        <div class="endeavor_text">
                            <b ng-if="e.name != undefined">{{e.name}}</b>
                            <span ng-if="e.name != undefined && e.desc != undefined"> - </span>
                            <span ng-bind-html="e.desc|trustedHTML"></span>
                        </div>
                        <div ng-if="e.cost_detail != undefined" class="cost_detail {{e.cost_detail_type}}_cost_detail">
                            <div ng-repeat="i in e.cost_detail">
                                {{i}}
                            </div>
                        </div>
                    </div> <!-- endeavor container -->
                </div> <!-- innovations endeavors -->

                <!-- locations -->
                <div
                    ng-repeat="l in settlement.campaign.endeavors.locations"
                >
                    <h5><b>{{settlement.game_assets.locations[l['handle']].name}}</b>:</h5>
                    <div
                        ng-repeat="e_handle in l.endeavors"
                        ng-init="e = settlement.game_assets.endeavors[e_handle]"
                        class="campaign_summary_endeavor_container {{e.class}}"
                    >
                        <div class="endeavor_cost {{e.class}}">
                            <img ng-repeat="c in range(e.cost)" src="/media/icons/endeavor_star.png" class="endeavor_cost">
                        </div>
                        <div class="endeavor_text">
                            <b ng-if="e.name != undefined">{{e.name}}</b>
                            <span ng-if="e.name != undefined && e.desc != undefined"> - </span>
                            <span ng-bind-html="e.desc|trustedHTML"></span>
                        </div>
                        <div ng-if="e.cost_detail != undefined" class="cost_detail {{e.cost_detail_type}}_cost_detail">
                            <div ng-repeat="i in e.cost_detail">
                                {{i}}
                            </div>
                        </div>
                    </div> <!-- endeavor container -->
                </div> <!-- locations endeavors -->

                <!-- survivors -->
                <div
                    ng-repeat="s in settlement.campaign.endeavors.survivors"
                >
                    <h5><b>{{s.sheet.name}} [{{s.sheet.effective_sex}}]</b>:</h5>
                    <div
                        ng-repeat="e_handle in s.sheet.endeavors"
                        ng-init="e = settlement.game_assets.endeavors[e_handle]"
                        class="campaign_summary_endeavor_container {{e.class}}"
                    >
                        <div class="endeavor_cost {{e.class}}">
                            <img ng-repeat="c in range(e.cost)" src="/media/icons/endeavor_star.png" class="endeavor_cost">
                        </div>
                        <div class="endeavor_text">
                            <b ng-if="e.name != undefined">{{e.name}}</b>
                            <span ng-if="e.name != undefined && e.desc != undefined"> - </span>
                            <span ng-bind-html="e.desc|trustedHTML"></span>
                        </div>
                        <div ng-if="e.cost_detail != undefined" class="cost_detail {{e.cost_detail_type}}_cost_detail">
                            <div ng-repeat="i in e.cost_detail">
                                {{i}}
                            </div>
                        </div>
                    </div> <!-- endeavor container -->
                </div><!-- survivor repeater -->

                <!-- storage -->
                <div
                    ng-repeat="item in settlement.campaign.endeavors.storage"
                >
                    <h5><b>{{item.name}} ({{item.type}})</b>:</h5>
                    <div
                        ng-repeat="e_handle in item.endeavors"
                        ng-init="e = settlement.game_assets.endeavors[e_handle]"
                        class="campaign_summary_endeavor_container {{e.class}}"
                    >
                        <div class="endeavor_cost {{e.class}}">
                            <img ng-repeat="c in range(e.cost)" src="/media/icons/endeavor_star.png" class="endeavor_cost">
                        </div>
                        <div class="endeavor_text">
                            <b ng-if="e.name != undefined">{{e.name}}</b>
                            <span ng-if="e.name != undefined && e.desc != undefined"> - </span>
                            <span ng-bind-html="e.desc|trustedHTML"></span>
                        </div>
                    </div> <!-- endeavor container -->
                </div> <!-- storage endeavors -->

                <!-- events -->
                <div
                    ng-repeat="item in settlement.campaign.endeavors.settlement_events"
                >
                    <h5><b>{{item.name}}</b>:</h5>
                    <div
                        ng-repeat="e_handle in item.endeavors"
                        ng-init="e = settlement.game_assets.endeavors[e_handle]"
                        class="campaign_summary_endeavor_container {{e.class}}"
                    >
                        <div class="endeavor_cost {{e.class}}">
                            <img ng-repeat="c in range(e.cost)" src="/media/icons/endeavor_star.png" class="endeavor_cost">
                        </div>
                        <div class="endeavor_text">
                            <b ng-if="e.name != undefined">{{e.name}}</b>
                            <span ng-if="e.name != undefined && e.desc != undefined"> - </span>
                            <span ng-bind-html="e.desc|trustedHTML"></span>
                        </div>
                    </div> <!-- endeavor container -->
                </div> <!-- storage endeavors -->


            </div>
            <div class="campaign_summary_small_box settlement_fact" ng-if='settlement.survivor_bonuses.all.length >=1'>
                <h4>- Settlement Bonuses -</h4>
                <span
                    class="kd_checkbox_checked campaign_summary_bullet"
                    ng-repeat="p in settlement.survivor_bonuses.all"
                >
                    <b> {{p.name}}:</b>
                    <span ng-bind-html="p.desc|trustedHTML"></span>
                </span>
            </div>
            <div class="campaign_summary_small_box settlement_fact" ng-if="settlement.sheet.principles.length >= 1">
                <h4>- Principles -</h4>
                <span
                    class="kd_checkbox_checked campaign_summary_bullet"
                    ng-repeat="p in settlement.sheet.principles"
                >
                    {{settlement.game_assets.innovations[p].name}}
                </span>

            </div>
            <div class="campaign_summary_small_box settlement_fact" ng-if="settlement.sheet.innovations.length >= 1">
                <h4>- Innovations -</h4>
                <span
                    class="kd_checkbox_checked campaign_summary_bullet"
                    ng-repeat="i in settlement.sheet.innovations"
                >
                    {{settlement.game_assets.innovations[i].name}}
                </span>
            </div>

            <div class="campaign_summary_small_box settlement_fact" ng-if="settlement.sheet.locations.length >= 1">
                <h4>- Locations -</h4>
                <span
                    class="kd_checkbox_checked campaign_summary_bullet"
                    ng-repeat="l in settlement.sheet.locations"
                >
                    {{settlement.game_assets.locations[l].name}}
                </span>
            </div>

            <div class="campaign_summary_small_box settlement_fact">
                <h4>- Monsters -</h4>

                <h3 class="monster_subhead" ng-if="settlement.sheet.monster_volumes.length >= 1">
                    Monster Volumes
                </h3>
                <span
                    class="kd_checkbox_checked campaign_summary_bullet"
                    ng-repeat='v in settlement.sheet.monster_volumes'
                >
                    {{v}}
                </span>

                <h3 class="monster_subhead" ng-if="settlement.sheet.defeated_monsters.length >=1">
                    Defeated Monsters
                </h3>
                <span
                    class="kd_checkbox_checked campaign_summary_bullet"
                    ng-repeat="d in settlement.sheet.defeated_monsters track by $index"
                >
                    {{d}}
                </span>

                <h3 class="monster_subhead">Quarries </h3>
                <span class="kd_checkbox_checked campaign_summary_bullet" ng-repeat="n in settlement.sheet.quarries">
                    {{ settlement.game_assets.monsters[n].name }}
                </span>

                <h3 class="monster_subhead">Nemesis Monsters</h3>
                <span class="kd_checkbox_checked campaign_summary_bullet" ng-repeat="n in settlement.sheet.nemesis_monsters">
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


    <button
        id="departingSurvivorsModalOpener"
        class="manage_departing_survivors kd_brown"
        ng-if="departing_survivor_count > 0"
        onclick="showHide('departingSurvivorsModalContent')"
    >
        Manage {{departing_survivor_count}} <b>Departing</b> Survivors
    </button>

    <div
        id="departingSurvivorsModalContent"
        class="hidden modal modal-black"
        ng-controller="manageDepartingSurvivorsController"
    >
        <h3>Manage Departing Survivors</h3>
        <p class="modal_subtitle">Use the controls below to modify all <i>living</i>
        survivors in the <b>Departing Survivors</b> group. </p>

        <div class="departing_survivors_control">
            <div class="label_div">Survival</div>
            <div class="button_div" ng-if="hideControls==false">
                <button
                    ng-click="updateDepartingSurvivors('survival', +1)"
                > +1
                </button>
                <button
                    ng-click="updateDepartingSurvivors('survival', -1)"
                > -1
                </button>
            </div> <!-- button div -->
        </div> <!-- departing_survivors_control Survival -->

        <div class="departing_survivors_control">
            <div class="label_div">Insanity</div>
            <div class="button_div" ng-if="hideControls==false">
                <button
                    ng-click="updateDepartingSurvivors('Insanity', +1)"
                > +1
                </button>
                <button
                    ng-click="updateDepartingSurvivors('Insanity', -1)"
                > -1
                </button>
            </div> <!-- button div -->
        </div> <!-- departing_survivors_control Insanity -->

        <div class="departing_survivors_control">
            <div class="label_div">Courage</div>
            <div class="button_div" ng-if="hideControls==false">
                <button
                    ng-click="updateDepartingSurvivors('Courage', +1)"
                > +1
                </button>
                <button
                    ng-click="updateDepartingSurvivors('Courage', -1)"
                > -1
                </button>
            </div> <!-- button div -->
        </div> <!-- departing_survivors_control Insanity -->

        <div class="departing_survivors_control">
            <div class="label_div">Understanding</div>
            <div class="button_div" ng-if="hideControls==false">
                <button
                    ng-click="updateDepartingSurvivors('Understanding', +1)"
                > +1
                </button>
                <button
                    ng-click="updateDepartingSurvivors('Understanding', -1)"
                > -1
                </button>
            </div> <!-- button div -->
        </div> <!-- departing_survivors_control Understanding -->

        <div class="departing_survivors_control">
            <div class="label_div">Hunt XP</div>
            <div class="button_div" ng-if="hideControls==false">
                <button
                    ng-click="updateDepartingSurvivors('hunt_xp', +1)"
                > +1
                </button>
                <button
                    ng-click="updateDepartingSurvivors('hunt_xp', -1)"
                > -1
                </button>
            </div> <!-- button div -->
        </div> <!-- departing_survivors_control Understanding -->

        <div class="departing_survivors_control">
            <div class="label_div">Brain Event Damage</div>
            <div class="button_div" ng-if="hideControls==false">
                <button
                    ng-click="updateDepartingSurvivors('brain_event_damage', 1)"
                    class="maroon_text"
                > 1
                </button>
            </div> <!-- button div -->
        </div> <!-- departing_survivors_control brain event damage -->


        <h3>Monster</h3>
        <p class="modal_subtitle">Use the controls below to select the monster
        facing the survivors in the upcoming Showdown. </p>

        <div class="current_hunt_container">
            <select
                id="set_departing_survivors_current_quarry"
                class="hunting_party_current_quarry"
                ng-model="settlement.sheet.current_quarry"
                ng-change="saveCurrentQuarry()"
                ng-options="d for d in settlement.game_assets.defeated_monsters"
            >
                <option disabled selected value="">Choose Monster</option>
            </select>
        </div>

        <div class="showdown_type">
            <span ng-if="settlement.sheet != undefined" ng-init="initShowdownControls()"></span>
            <h3
                class="clickable"
                ng-click="
                    showHide('showdownOptions');
                    flipShowdownArrow();
                "
            >
                Showdown
                <span class="showdown_arrow" ng-if="scratch.showdown_arrow == true">
                    &#x25BC;
                </span>
                <span class="showdown_arrow" ng-if="scratch.showdown_arrow == false">
                    &#x25B2;
                </span>
            </h3>
            <p class="modal_subtitle">Use the buttons below to select the type of
            showdown.</p>
            <div id="showdownOptions" class="options" ng-class="{hidden: settlement.sheet.showdown_type != undefined}">
                <button
                    class="departing_survivors_mgmt kd_brown"
                    ng-click="setShowdownType('normal'); showHide('showdownOptions')"
                >
                    <b>Showdown</b>
		</button>
                <button
                    class="departing_survivors_mgmt kd_special_showdown"
                    ng-click="setShowdownType('special'); showHide('showdownOptions')"
                >
                    <b>Special Showdown</b>
                </button>
            </div>
        </div>

        <div ng-if="settlement.sheet.showdown_type != undefined">
            <h3 ng-if="settlement.sheet.showdown_type == 'normal'">Return Survivors from Showdown</h3>
            <p class="modal_subtitle" ng-if="settlement.sheet.showdown_type == 'normal'">
                Use the buttons below to return <b>Departing</b> Survivors to
                <b>{{settlement.sheet.name}}</b>. This automatically marks living
                survivors as <b>Returning Survivors</b> and removes armor points,
                attribute modifiers and damage. Settlement <b>Endeavor Tokens</b>
                will also be automatically udpated.<br/>
            </p>
            <h3 ng-if="settlement.sheet.showdown_type == 'special'">Heal Survivors</h3>
            <p class="modal_subtitle" ng-if="settlement.sheet.showdown_type == 'special'">
                Use the buttons below to heal <b>Departing</b> Survivors and
                remove them from the <b>Departing Survivors</b> group. Healing
                survivors automatically removes armor points, attribute
                modifiers and damage.<br/>
            </p>

            <button
                class="kd_blue departing_survivors_mgmt"
                ng-click="returnDepartingSurvivors('victory')"
                onclick="showHide('departingSurvivorsModalContent')"
            >
                Victorious!
            </button>
            <button
                class="kd_alert_no_exclaim departing_survivors_mgmt"
                ng-click="returnDepartingSurvivors('defeat')"
                onclick="showHide('departingSurvivorsModalContent')"
            >
                Defeated...
            </button>
        </div>

        <hr>

        <button
            class="departing_survivors_mgmt"
            onclick="showHide('departingSurvivorsModalContent')"
        >
            <b>Back</b>
        </button>
    </div> <!-- modalDepartingSurvivors whole deal-->

    <div
        id="campaignSummaryStorageOpener"
        class="clickable campaign_summary_storage_opener gradient_silver clickable"
        ng-if="settlementStorage != undefined"
        ng-click="openNav('campaignSummaryStorageModal')"
    >
        &#8942;
    </div>

    <div
        id="campaignSummaryStorageModal"
        class="rightSideNav kd_dying_lantern clickable"
        ng-if="settlement != undefined && user.user.subscriber.level >= 2"
        ng-init="getStorage()"
        ng-click="closeNav('campaignSummaryStorageModal')"
    >
        <div
            class="rightSideNavContent"
        >
            <div
                class="campaign_summary_storage_type"
                ng-repeat="s_type in settlementStorage">
            >
                <h3>{{s_type.name}} Storage</h3>
                <div class="campaign_summary_storage_keywords">
                    <span
                        class="campaign_summary_storage_keyword"
                        ng-repeat="(kw, count) in s_type.keywords"
                    >
                        {{kw}}: {{count}}
                    </span>
                </div>

                <div
                    class="campaign_summary_storage_location"
                    ng-repeat="loc in s_type.locations"
                    ng-if="loc.inventory.length >= 1"
                >
                    <h4>{{loc.name}}</h4>
                    <div class="campaign_summary_storage_items">
                        <span class="campaign_summary_storage_item" ng-repeat="i in loc.collection" ng-if="i.quantity >= 1">
                            {{i.name}} <span ng-if="i.quantity >= 2">x {{i.quantity}}</span><br/>
                            <div
                                class="campaign_summary_storage_item_keywords"
                                ng-if="i.keywords.length >= 1"
                            >
                                <i>{{i.keywords.join(', ')}}</i>
                            </div>
                            <div
                                class="campaign_summary_storage_item_keywords"
                                ng-if="i.rules.length >= 1"
                            >
                                <b>{{i.rules.join(', ')}}</b>
                            </div>
                        </span>
                    </div>
                </div> <!-- location -->
            {{loc}}
            </div>
        </div> <!-- rightSideNavContent -->
        <div class="rightSideNavCloseTip">Click or tap to close!</div>
    </div>


</div> <!-- campaign_summary main root controller THIS IS THE END -->

\n""" % dashboard.campaign_flash)

    form = Template("""\n\

    <script src="/media/settlementSheet.js?v=$application_version"></script>

    <div
        id = "settlement_sheet_angularjs_controller_container"
        ng-init="initializeSettlement('settlementSheet', '$api_url','$settlement_id')"
        ng-controller="settlementSheetController"
    >

        <!-- once we get the settlement, init the user -->
        <span
            class="hidden"
            ng-if="settlement != undefined"
            ng-init="initializeUser('$user_id')"
        >
            Hack City!
        </span>

        <span class="tablet_and_desktop nav_bar settlement_sheet_gradient"></span>
        <span class="nav_bar_mobile mobile_only settlement_sheet_gradient"></span>
        <div class="top_nav_spacer"> hidden </div>

        <div id="asset_management_left_pane" ng-if="settlement != undefined">

            <div
                id="settlementName"
                contentEditable="true"
                class="settlement_sheet_settlement_name"
                ng-model="scratch.newSettlementName"
                ng-placeholder="Settlement Name"
                ng-blur="setSettlementName()"
            />{{settlement.sheet.name}}
            </div>

            <p
                id="campaign_type"
                class="settlement_sheet_campaign_type"
                title="Campaign type may not be changed after a settlement is created!"
            >
                {{settlement.game_assets.campaign.name}}
            </p>


        <h1 ng-if="settlement.sheet.abandoned"class="alert">ABANDONED</h1>

        <div class="settlement_sheet_tumblers_container">
            <div class="settlement_form_wide_box">
                <div class="big_number_container left_margin">
                    <button
                        class="incrementer"
                        ng-click="incrementAttrib('survival_limit',1)"
                    >
                        &#9652;
                    </button>
                    <input
                        id="survivalLimitBox"
                        class="big_number_square"
                        type="number"
                        name="survival_limit"
                        ng-value="settlement.sheet.survival_limit"
                        ng-model="settlement.sheet.survival_limit"
                        ng-blur="setAttrib('survival_limit', settlement.sheet.survival_limit)"
                        min="{{settlement.sheet.minimum_survival_limit}}"
                    />
                    <button
                        class="decrementer"
                        ng-click="incrementAttrib('survival_limit',-1)"
                    >
                        &#9662;
                    </button>
                </div>

                <div class="big_number_caption">
                    <div class="help-tip">
                        Survival Limit
                        <p> The minimum Survival Limit for <b>{{settlement.sheet.name}}</b>, based on settlement innovations and principles, is <b>{{settlement.sheet.minimum_survival_limit}}</b>.
                            <span ng-if="settlement.sheet.enforce_survival_limit == true">
                                The settlement Survival Limit of <b>{{settlement.sheet.survival_limit}}</b> is enforced on the Survivor Sheet.
                            </span>
                            <span ng-if="settlement.sheet.enforce_survival_limit == false">
                                Due to expansion or campaign rules, the settlement Survival Limit of <b>{{settlement.sheet.survival_limit}}</b> is <u>not</u> enforced on the Survivor Sheet!
                            </span>
                        </p>
                    </div>
                </div>

            </div><!-- settlement_form_wide_box -->

            <br class="mobile_only"/>
            <hr class="mobile_only"/>

            <div class="settlement_form_wide_box">
                <div class="big_number_container left_margin">
                    <button
                        class="incrementer"
                        ng-click="incrementAttrib('population',1)"
                    >
                        &#9652;
                    </button>
                    <input
                        id="populationBox"
                        class="big_number_square"
                        type="number" name="population"
                        ng-value="settlement.sheet.population"
                        ng-model="settlement.sheet.population"
                        ng-blur="setAttrib('population', settlement.sheet.population)"
                        min="{{Number(settlement.sheet.minimum_population)}}"
                    />
                    <button
                        class="decrementer"
                        ng-click="incrementAttrib('population',-1)"
                    >
                        &#9662;
                    </button>
                </div>
                <div class="big_number_caption">
                    <div class="help-tip">
                        Population
                        <p> The minimum Population for <b>{{settlement.sheet.name}}</b>, based on the total number of living survivors in the settlement, is <b>{{settlement.sheet.minimum_population}}</b>.
                        </p>
                    </div>
                </div>
            </div> <!-- settlement_form_wide_box -->

            <br class="mobile_only"/>
            <hr class="mobile_only"/>

            <div class="settlement_form_wide_box">
                <div class="big_number_container left_margin">
                    <button
                        class="decrementer"
                        ng-click="incrementAttrib('death_count',1)"
                    >
                        &#9652;
                    </button>
                    <input
                        id="deathCountBox"
                        class="big_number_square"
                        type="number"
                        name="death_count"
                        ng-value="settlement.sheet.death_count"
                        ng-model="settlement.sheet.death_count"
                        ng-blur="setAttrib('death_count', settlement.sheet.death_count)"
                        min="{{Number(settlement.sheet.minimum_death_count)}}"
                    />
                    <button
                        class="decrementer"
                        ng-click="incrementAttrib('death_count',-1)"
                    >
                        &#9662;
                    </button>
                </div>
                <div class="big_number_caption">
                    <div class="help-tip">
                        Death Count
                        <p> The minimum Death Count for <b>{{settlement.sheet.name}}</b>, based on the total number of dead survivors in the settlement, is <b>{{settlement.sheet.minimum_death_count}}</b>.
                        </p>
                    </div>
                </div>
            </div> <!-- settlement_form_wide_box -->
        </div> <!-- settlement_sheet_tumblers_container -->


        <hr class="invisible">



            <!-- STORAGE CONTROLS START HERE -->



        <div
            class="settlement_sheet_block_group settlement_storage"
            ng-controller="storageController"
        >

            <div id="editStorage" class="hidden modal storage_modal">

                <div
                    class="storage_modal_storage_type"
                    ng-repeat="s_type in settlementStorage"
                >
                        <h3>{{s_type.name}} Storage</h3>
                        <div
                            ng-repeat="loc in s_type.locations"
                            ng-init="loc.arrow=false"
                            class="storage_modal_storage_location"
                        >
                            <h4
                                class="clickable"
                                ng-click="showHide(loc.handle + '_container'); flipArrow(loc)"
                            >
                                {{loc.name}} <span class="metrophobic"></span>
                                <span ng-if="loc.arrow == false" class="arrow">
                                    &#x25BC;
                                </span>
                                <span ng-if="loc.arrow == true" class="arrow">
                                    &#x25B2;
                                </span>
                            </h4>
                            <div class="hidden" id="{{loc.handle}}_container"> <!-- show hide -->
                                <div
                                    class="inventory_row" ng-repeat="asset in loc.collection"
                                    ng-init="detailId = asset.handle + '_detail'; asset.flippers=false"
                                    ng-class-even="'no_zebra'"
                                    ng-class-odd="'zebra'"
                                    ng-class="{inventory_row_item_last:$last}"
                                >
                                    <div
                                        class="inventory_row_item_controls clickable"
                                        ng-click="showHide(detailId); toggleFlippers(asset)"
                                    >
                                        <span class="name">
                                            {{asset.name}}
                                        </span>
                                        <span class="quantity">
                                            {{asset.quantity}}
                                        </span>
                                    </div> <!-- controls -->
                                    <div class="flippers" ng-if="asset.flippers">
                                        <button ng-click="setStorage(asset, 1)"> + </button>
                                        <button ng-click="setStorage(asset, -1)"> - </button>
                                    </div>
                                    <div id="{{detailId}}" class="hidden inventory_row_detail">
                                        &nbsp;
                                        <div class="inventory_row_detail_keywords">
                                            <span ng-repeat="k in asset.keywords">
                                                <i>{{k}}{{$last ? '' : ', '}}</i>
                                            </span>
                                        </div>
                                        <div class="inventory_row_detail_rules" ng-if="asset.rules.length >= 1">
                                            <span ng-repeat="k in asset.rules track by $index">
                                                <b>{{k}}</b>{{$last ? '' : ', '}}
                                            </span>
                                        </div>
                                        <span
                                            ng-if="asset.desc != undefined"
                                            class="inventory_row_detail_desc"
                                            ng-bind-html="asset.desc|trustedHTML">
                                        </span>
                                    </div>
                                </div>
                            </div>

                        </div> <!-- storage_location -->

                    </div> <!-- storage_type -->

                <div class="button_spacer"></div>
                <button
                    class="kd_blue close_storage"
                    ng-click="showHide('editStorage'); loadStorage();"
                >
                    Save Changes and Return
                </button>
            </div> <!-- storage_modal container -->

            <div id="storageSpinner" class="hidden storage_loading_spinner">
                <img src="/media/loading_io.gif"><br/>
                Loading storage...
            </div>
            <div id="storageLauncher" class="visible">
                <h2 class="clickable" ng-click="showHide('editStorage')">Storage</h2>
                <p class="clickable" ng-click="showHide('editStorage')">Gear & Resources may be stored without limit. <b>Tap or click here to edit settlement storage.</b></p>
            </div>
            <div
                class="settlement_storage_type_container"
                ng-repeat="s_type in settlementStorage"
            >
                <h3 ng-if="s_type.total >= 1">
                    {{s_type.name}} Storage
                </h3>
                <div class="storage_location_keywords_rollup">
                    <span
                        class="keywords_rollup_item"
                        ng-repeat="(kw, count) in s_type.keywords"
                    >
                        {{kw}}: {{count}}
                    </span>
                </div>
                <div
                    class="settlement_storage_location"
                    ng-repeat="loc in s_type.locations"
                    ng-if="loc.inventory.length >= 1"
                    ng-init="loc.arrow = false"
                >
                    <h4
                        class="clickable"
                        ng-click="showHide(loc.handle + '_digest_container'); flipArrow(loc)"
                    >
                        {{loc.name}} ({{loc.inventory.length}})
                        <span ng-if="loc.arrow == false" class="arrow">
                            &#x25BC;
                        </span>
                        <span ng-if="loc.arrow == true" class="arrow">
                            &#x25B2;
                        </span>
                    </h4>
                    <div class="hidden" id="{{loc.handle}}_digest_container"> <!-- show hide -->
                        <div
                            class="settlement_storage_inventory_container"
                        >
                            <div
                                class="inventory_repeater clickable"
                                ng-repeat="t in loc.digest"
                                ng-init="detailId = t.handle + '_digest_detail'"
                                style="background-color: #{{loc.bgcolor}}; color: #{{loc.color}}"
                                ng-click="showHide(detailId)"
                            >
                                {{t.name}}
                                <span ng-if="t.count > 1">x {{t.count}}</span>
                                <div id="{{detailId}}" class="hidden inventory_repeater_detail">
                                    <div class="inventory_row_detail_keywords">
                                        &nbsp; <span ng-repeat="k in t.keywords">
                                            <i>{{k}}{{$last ? '' : ', '}}</i>
                                        </span>
                                    </div>
                                    <div class="inventory_row_detail_rules" ng-if="t.rules.length >= 1">
                                        &nbsp; <span ng-repeat="k in t.rules track by $index">
                                            <b>{{k}}</b>{{$last ? '' : ', '}}
                                        </span>
                                    </div>
                                    <span
                                        class="inventory_row_detail_desc"
                                        ng-if="asset.desc != undefined"
                                        ng-bind-html="t.desc|trustedHTML"
                                    >
                                    </span>
                                </div>
                            </div> <!-- inventory repeater, click to remove -->
                        </div> <!-- container flex -->
                    </div> <!-- showhide -->
                </div><!-- storage location container-->
            </div> <!-- storage type container, e.g. gear/resources-->



        </div> <!-- settlement_sheet_block_group for storage -->



    </div> <!-- asset_management_left_pane -->


    <div id="asset_management_middle_pane" ng-if="settlement != undefined">


                    <!-- LOCATIONS - ANGULARJS CONTROLS -->


        <a id="edit_locations" class="mobile_only"><a/>

        <div
            class="settlement_sheet_block_group"
            ng-if="settlement.sheet.innovations.indexOf('sculpture') != -1"
            title="Use these controls to manage your settlement's Inspirational Statue!"
        >
            <h2>Inspirational Statue</h2>
            <p>A settlement can only have one Inspirational Statue.</p>

            <div class="line_item">
                <span class="empty_bullet" ng-if="settlement.sheet.inspirational_statue == undefined"/></span>
                <span class="bullet" ng-if="settlement.sheet.inspirational_statue != undefined"/></span>
                <select
                    ng-model="settlement.sheet.inspirational_statue"
                    ng-options="
                        fa_handle as settlement.game_assets.fighting_arts[fa_handle].name for fa_handle in settlement.game_assets.inspirational_statue_options
                    "
                    ng-change="setInspirationalStatue()"
                    ng-selected="settlement.sheet.inspirational_statue"
                >
                    <option disabled value="">Select a Fighting Art</option>
                </select>
            </div> <!-- line_item -->

        </div>

        <div
            class="settlement_sheet_block_group"
            ng-controller="locationsController"
            title="Click or tap an item to remove it from this list."
        >

            <h2>Settlement Locations</h2>
            <p>Locations in your settlement.</p>
            <hr class="invisible"/> <!-- TK this is pretty low rent -->
            <div
                class="line_item location_container"
                ng-repeat="loc in settlement.sheet.locations"
                ng-init="locationLevel = settlement.sheet.location_levels[loc]"
            >
                <span class="bullet"></span>
                <span
                    class="item"
                    ng-click="rmLocation($index, loc)"
                >
                    {{settlement.game_assets.locations[loc].name}}
                </span>
                <span ng-if="settlement.sheet.location_levels[loc] != undefined" class="location_lvl_select">
                    <select
                        class="location_level"
                        ng-model="locationLevel"
                        ng-options="locationLevel as 'Lvl. '+ locationLevel for locationLevel in [1,2,3]"
                        ng-change="setLocationLevel(loc, locationLevel)"
                        ng-selected="locationLevel"
                    >
                    </select>
                </span> <!-- optional levels controls -->

            </div> <!-- line_item location_container: list/rm locations -->


            <div class="line_item">
                <span class="empty_bullet" /></span>
                <select
                    name="add_location"
                    ng_model="newLocation"
                    ng_change="addLocation()"
                    ng-options="loc.handle as loc.name for loc in locationOptions"
                >
                    <option value="" disabled selected>Add Location</option>
                </select>
            </div>

        </div> <!-- settlement_sheet_block_group locations controller-->




                    <!-- INNOVATIONS - ANGULARJS CONTROLS -->

        <a id="edit_innovations" class="mobile_only"/></a>


        <div
            class="settlement_sheet_block_group"
            ng-controller="innovationsController"
            title="Click or tap on an item to remove it from this list."
        >

            <h2>Innovations</h2>
            <p>The settlement's innovations (including weapon masteries).</p>

            <hr class="invisible"/> <!-- TK why is this still here? need to fix -->

            <div
                class="line_item location_container"
                ng-repeat="i in settlement.sheet.innovations"
                ng-init="innovationLevel = settlement.sheet.innovation_levels[i]"
            >
                <span class="bullet"></span>
                <span
                    class="item"
                    ng-click="rmInnovation($index,i)"
                >
                    {{settlement.game_assets.innovations[i].name}}
                </span>
                <span ng-if="settlement.sheet.innovation_levels[i] != undefined" class="location_lvl_select">
                    <select
                        class="location_level"
                        ng-model="innovationLevel"
                        ng-options="innovationLevel as 'Lvl. '+ innovationLevel for innovationLevel in [1,2,3]"
                        ng-change="setInnovationLevel(i,innovationLevel)"
                        ng-selected="innovationLevel"
                    >
                    </select>
                </span> <!-- optional levels controls -->
            </div>

            <div class="line_item">
                <span class="empty_bullet" /></span>
                <select
                    name="add_innovation"
                    ng_model="newInnovation"
                    ng_change="addInnovation()"
                    ng-options="i.handle as i.name for i in innovationOptions"
                >
                    <option value="" disabled selected>Add Innovation</option>
                </select>
            </div>

            <div
                id="innovationDeckContainer"
                class="innovation_deck settlement_sheet_ui_box"
                title="The current innovation deck for {{settlement.sheet.name}}. Tap or click to refresh!"
                ng-if="settlement.sheet.innovations.length != 0"
                ng-init="setInnovationDeck()"
            >
                <h3> - Innovation Deck - </h3>
                <img id="innovationDeckSpinner" class="innovation_deck_spinner" src="/media/loading_io.gif">
                <ul
                    class="asset_deck clickable"
                    ng-click="setInnovationDeck()"
                >
                    <li ng-repeat="(handle, dict) in innovation_deck"> {{dict['name']}} </li>
                </ul>

                <div
                    class="innovation_quick_pick_container"
                    ng-if="user.user.subscriber.level > 1"
                >
                    <button
                        id="innovationQuickPickLauncher"
                        class="kd_blue"
                        ng-if="innovation_deck != undefined"
                        onClick="showHide('innovationQuickPickLauncher'); showHide('innovationQuickPick')"
                        ng-click="createInnovationQuickPick()"
                    >
                        Innovate!
                    </button>
                    <div
                        id="innovationQuickPick"
                        class="innovation_quick_pick hidden"
                    >
                        <div class="kd_sheet_ui_row_tip">
                            Click on an innovation below to add it to settlement innovations!
                        </div>
                        <div
                            class="clickable innovation_quick_pick_item card_gradient"
                            ng-repeat="h in innovationQuickPickOptions"
                            ng-init="i = settlement.game_assets.innovations[h]"
                            ng-click="addInnovation(h); showHide('innovationQuickPick')"
                        >
                            <div class="innovation_name">{{i.name}}</div>
                            <div class="innovation_consequences" ng-if="i.consequences.length > 0">
                                Consequences:
                                <span ng-repeat="c_handle in i.consequences">
                                    {{settlement.game_assets.innovations[c_handle].name}}{{$last ? '' : ', '}}
                                <span>
                            </div>
                            <div class="innovation_survival_limit_bar" ng-if="i.survival_limit != undefined">
                                Survival Limit +{{i.survival_limit}}
                            </div>
                        </div>
                        <button
                            class="kd_blue"
                            ng-if="innovation_deck != undefined"
                            ng-click="createInnovationQuickPick()"
                        >
                            Draw again!
                        </button>
                        <button
                            class="kd_alert_no_exclaim"
                            onClick="showHide('innovationQuickPickLauncher'); showHide('innovationQuickPick')"
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            
            </div> <!-- innovationDeckContainer -->


        </div> <!-- settlement_sheet_block_group innovations-->

        <div
            class="settlement_sheet_block_group"
            ng-controller="lanternResearchController"
            ng-if="settlement.sheet.locations.indexOf('exhausted_lantern_hoard') != -1"
        >

            <h2>Lantern Research Level</h2>

            <div class="lantern_research_level">
                <div class="big_number_container">
                    <button
                        class="incrementer"
                        ng-click="incrementLanternResearch(1)"
                    >
                        &#9652;
                    </button>
                    <input
                        id="lanternResearchBox"
                        class="big_number_square"
                        type="number" name="population"
                        ng-value="settlement.sheet.lantern_research_level"
                        ng-model="settlement.sheet.lantern_research_level"
                        ng-blur="setLanternResearch()"
                        min="0"
                        max="5"
                    />
                    <button
                        class="decrementer"
                        ng-click="incrementLanternResearch(-1)"
                    >
                        &#9662;
                    </button>
                </div> <!-- big_number_container -->
                <div class="desc_text">
                    <p><b>Once per lantern year, spend 2 x Bone, 2 x hide, 2 x organ to research.</b><br/>If you do, gain the next level of Lantern Research.</p>
                    <p>Corresponding <b>Pulse Discoveries</b> are displayed on the Campaign Summary view.</p>
                </div> <!-- desc_text -->

            </div><!-- big_number_container -->

        </div> <!-- lantern research level -->

        <div
            class="settlement_sheet_block_group"
            ng-controller="monsterVolumesController"
            ng-if="settlement.sheet.innovations.indexOf('records') != -1"
            title="Click or tap on an item to remove it from this list."
        >

            <h2>Monster Volumes</h2>
            <p>There can be up to 3 volumes for each monster.</p>

            <div
                class="line_item location_container"
                ng-repeat="v in settlement.sheet.monster_volumes"
            >
                <span class="bullet"></span>
                <span
                    class="item"
                    ng-click="rmMonsterVolume($index, v)"
                >
                    {{v}}
                </span>
            </div> <!-- line_item -->

            <div class="line_item">
                <span class="empty_bullet"></span>
                <select
                    ng-model="scratch.monster_volume"
                    ng-options="m_string for m_string in settlement.game_assets.monster_volumes_options"
                    ng-change="addMonsterVolume()"
                >
                    <option disabled value="">Add a Monster Volume</option>
                </select>
            </div> <!-- line_item -->

        </div>


    </div> <!-- asset_management_left_pane -->



    <!-- END OF LEFT PANE -->



    <div id="asset_management_right_pane" ng-if="settlement != undefined">

        <a id="edit_principles" class="mobile_only"></a>

        <div
            class="settlement_sheet_block_group"
            ng-controller="principlesController"
        >
            <h2>Principles</h2>
            <p>The settlement's established principles.</p>

            <div
                ng-repeat="p in settlement.game_assets.principles_options"
                class="settlement_sheet_principle_container"
            >
                <div
                    id="{{p.name}} principle"
                    class="principles_container"
                >

                    <div class="settlement_sheet_principle_name">
                        {{p.name}}
                    </div>

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

        <div class="settlement_sheet_block_group" ng-controller="milestonesController">
            <h2>Milestone Story Events</h2>
            <p>Trigger these story events when milestone condition is met.</p>

            <div ng-repeat="m in settlement.game_assets.milestones_options" class="milestone_content_container">
                <input
                    id="{{m.handle}}"
                    class="kd_css_checkbox kd_radio_option"
                    type="checkbox"
                    ng-click="toggleMilestone(m.handle)"
                    ng-checked="settlement.sheet.milestone_story_events.indexOf(m.handle) != -1"
                />
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


    <div
       ng-controller="quarriesController"
       class="border_box"
    >
        <div
            class="settlement_sheet_kd_sheet_ui_box"
            title="Quarries controller for {{settlement.sheet.name}}. Tap or click to remove!"
        >
            <div class="kd_sheet_ui_row title">
                 Quarries
            </div>
            <div class="kd_sheet_ui_row">
                The monsters your settlement can select to hunt.
            </div>
            <div
                class="settlement_sheet_line_item location_container"
                ng-controller="quarriesController"
                ng-repeat="q in settlement.sheet.quarries"
            >
                <span class="kd_sheet_ui_box checked"></span>
                <span
                    class="item"
                    ng-click="removeQuarry($index, q)"
                >
                    {{settlement.game_assets.monsters[q].name}}
                </span>
            </div>
        </div> <!-- settlement_sheet_kd_sheet_ui_box -->

        <span class="empty_bullet" /></span>
        <select
            class="kd_sheet_ui_select"
            ng-model="addQuarryMonster"
            ng-options="q.handle as q.name for q in settlement.game_assets.quarry_options"
            ng-change="addQuarry($index)"
        >
            <option selected disabled value="">Add Quarry Monster</option>
        </select>

    </div> <!-- quarriesController -->

                    <!-- NEMESIS MONSTERS -->

    <div
        class="nemesis_monsters_controls_container border_box"
        ng-controller="nemesisEncountersController"
    >
        <div
            class="settlement_sheet_kd_sheet_ui_box"
            title="Nemesis Encounters controller for {{settlement.sheet.name}}. Tap or click to edit!"
        >
            <div class="kd_sheet_ui_row title">
                <img class="icon" src="media/icons/nemesis_encounter_event.jpg"/>
                Nemesis Monsters
            </div>
            <div class="kd_sheet_ui_row">
                The available nemesis encounter monsters.
            </div>
            <div
                class="settlement_sheet_line_item settlement_sheet_nemesis_line_item"
                ng-repeat="n in settlement.sheet.nemesis_monsters"
            >
                <div class="nemesis_clicker clickable" ng-click="rmNemesis($index,n)">
                    <span class="kd_sheet_ui_box checked"></span>
                    <span>{{settlement.game_assets.monsters[n].name}}</span>
                </div>
                <div class="nemesis_levels_container">
                    <div
                        class="nemesis_level_toggle clickable"
                        ng-repeat="l in range(settlement.game_assets.monsters[n].levels, 'increment')"
                        ng-click="toggleNemesisLevel(n,l)"
                    >
                        <span
                            class="kd_sheet_ui_box"
                            ng-class="{checked: settlement.sheet.nemesis_encounters[n].indexOf(l) != -1}"
                        ></span>
                        Lvl {{l}}
                    </div>
                </div>

            </div><!-- nemesis repeater / line item -->
        </div> <!-- settlement_sheet_kd_sheet_ui_box -->

        <span class="empty_bullet"></span>
        <select
            class="kd_sheet_ui_select"
            ng-model="addNemesisMonster"
            ng-options="n.handle as n.name for n in settlement.game_assets.nemesis_options"
            ng-change="addNemesis()"
        >
            <option selected disabled value="">Add Nemesis Monster</option>
        </select>
    </div> <!-- nemesis_monsters_controls_container -->


    <!-- DEFEATED MONSTERS -->
    <div
        class="border_box"
        ng-controller="defeatedMonstersController" title="Click or tap an item to remove it from this list."
    >
        <div
            class="settlement_sheet_kd_sheet_ui_box clickable"
            title="Defeated Monsters controller for {{settlement.sheet.name}}. Tap or click to remove!"
        >
            <div class="kd_sheet_ui_row title">
                Defeated Monsters
            </div>
            <div class="kd_sheet_ui_row">
                A list of defeated monsters and their level.
            </div>
            <div
                class="settlement_sheet_line_item defeated_monsters_container"
                ng-repeat="x in settlement.sheet.defeated_monsters track by $index"
            >
                <span class="kd_sheet_ui_box checked"></span>
                <span class="item" ng-click="rmDefeatedMonster($index, x)">
                    {{x}}
                </span>
            </div>
        </div><!-- settlement_sheet_kd_sheet_ui_box -->

        <div class="line_item">
            <span class="empty_bullet" /></span>
            <select
                class="kd_sheet_ui_select"
                ng-model="dMonst"
                ng-change="addDefeatedMonster()"
                ng-options="d as d for d in settlement.game_assets.defeated_monsters ">
            >
                <option selected disabled value="">Add Defeated Monster</option>
            </select>
        </div> <!-- line_item -->
    </div> <!-- defeatedMonstersController -->


    <!-- LOST SETTLEMENTS ANGULARJS app -->
    <div
        class="lost_settlement_controls_container border_box"
    >
        <div
            class="settlement_sheet_kd_sheet_ui_box clickable"
            onClick="rollUp('lostSettlementsControl')"
            title="Lost Settlements controller for {{settlement.sheet.name}}. Tap or click to edit!"
        >
            <div class="kd_sheet_ui_row title">
                Lost Settlements
            </div>
            <div class="kd_sheet_ui_box_row wrap_row">
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 0}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 1}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 2}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 3}"
                ></span>
                <span
                    class="kd_sheet_ui_box heavy"
                    ng-class="{checked: settlement.sheet.lost_settlements > 4}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 5}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 6}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 7}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 8}"
                ></span>
                <span
                    class="kd_sheet_ui_box heavy"
                    ng-class="{checked: settlement.sheet.lost_settlements > 9}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 10}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 11}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 12}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 13}"
                ></span>
                <span
                    class="kd_sheet_ui_box heavy"
                    ng-class="{checked: settlement.sheet.lost_settlements > 14}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 15}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 16}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 17}"
                ></span>
                <span
                    class="kd_sheet_ui_box"
                    ng-class="{checked: settlement.sheet.lost_settlements > 18}"
                ></span>
                <span
                    class="kd_sheet_ui_box heavy"
                    ng-class="{checked: settlement.sheet.lost_settlements > 19}"
                ></span>
            </div>
            <hr>
            <div class="kd_sheet_ui_row story_tip">
                <font class="kdm_font">g</font> &nbsp; <b>Game Over</b><span class="metrophobic">, p. {{settlement.game_assets.events['core_game_over'].page}}</span>
            </div>
            <div class="kd_sheet_ui_row dynamic_tip_row">
                <div class="lost_settlement_tip">
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: settlement.sheet.lost_settlements > 4}"
                    ></span>
                    Left Overs
                </div>
                <div class="lost_settlement_tip">
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: settlement.sheet.lost_settlements > 9}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: settlement.sheet.lost_settlements > 9}"
                    ></span>
                    Those Before Us
                </div>
            </div> <!-- dynamic_tip_row -->
            <div class="kd_sheet_ui_row dynamic_tip_row">
                <div class="lost_settlement_tip">
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: settlement.sheet.lost_settlements > 14}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: settlement.sheet.lost_settlements > 14}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: settlement.sheet.lost_settlements > 14}"
                    ></span>
                    Ocular Parasites
                </div>
                <div class="lost_settlement_tip">
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: settlement.sheet.lost_settlements > 19}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: settlement.sheet.lost_settlements > 19}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: settlement.sheet.lost_settlements > 19}"
                    ></span>
                    <span
                        class="kd_sheet_ui_box heavy"
                        ng-class="{checked: settlement.sheet.lost_settlements > 19}"
                    ></span>
                    Rainy Season
                </div>
            </div><!-- dynamic_tip_row -->
        </div> <!-- settlement_sheet_kd_sheet_ui_box -->
        <div
            id="lostSettlementsControl"
            class="kd_sheet_ui_roll_down rolled_up"
        >
            <div class="kd_sheet_ui_roll_down_controls">
                <div class="kd_sheet_ui_number_tumbler">
                    <button ng-click="settlement.sheet.lost_settlements = settlement.sheet.lost_settlements + 1">
                        &#x25B2;
                    </button>
                    <button ng-click="settlement.sheet.lost_settlements = settlement.sheet.lost_settlements - 1">
                        &#x25BC;
                    </button>
                    <button
                        class="kd_blue"
                        ng-click="setAttrib('lost_settlements',undefined,false)"
                        onClick="rollUp('lostSettlementsControl')"
                    >
                        Save Changes
                    </button>
                </div> <!-- number tumbler -->
            </div>
        </div>
    </div> <!-- lost_settlement_controls_container -->


    <!-- ABANDON -->
    <div
        class="settlement_sheet_block_group"
        ng-controller="abandonSettlementController"
        ng-if="settlement.sheet.abandoned == undefined"
    >

        <h3>Abandon Settlement</h3>
        <p>Mark a settlement as "Abandoned" to prevent it from showing up in your active campaigns without removing it from the system.</p>
        <p class="maroon_text">&nbsp; <b>This cannot be undone.</b></p>

        <button
            class="kd_alert_no_exclaim red_glow"
            ng-click="abandonSettlement()"
        >
            Abandon Settlement
        </button>
    </div> <!-- abandon controls -->

        <!-- remove settlement button -->
        <div
            ng-if="user.user.preferences.show_remove_button == true"
            class="settlement_sheet_block_group"
        >
            <h3>Permanently Remove Settlement</h3>
            <form
                action="#"
                method="POST"
                onsubmit="return confirm('Press OK to permanently delete this settlement AND ALL SURVIVORS WHO BELONG TO THIS SETTLEMENT forever. \\r\\rPlease note that this CANNOT BE UNDONE and is not the same as marking a settlement Abandoned.\\r\\rPlease consider abandoning old settlements rather than removing them, as this allows data about the settlement to be used in general kdm-manager stats.\\r\\r');"
            >
                <input type="hidden" name="remove_settlement" ng-value="settlement.sheet._id.$oid"/>
                <p>
                    Use the button below to permanently delete <b>{{settlement.sheet.name}}</b>.
                    Please note that <b>this cannot be undone</b> and that this will
                    also permanently remove all survivors associated with this
                    settlement.
                </p>
                <button class="kd_alert_no_exclaim red_glow permanently_delete">
                    Permanently Delete Settlement
                </button>
            </form>
        </div>


    </div> <!-- right pane -->


    <!--

        This is the fold! Anything below here is below the fold!
        This should only be modals, heavy angularjs stuff, etc. that is
        still within the settlementSheetApp, but that doesn't need to
        load right away.

    -->

    <form id="settlementSheetReload" method="POST" action="/"><button class="hidden" />SUBMIT</button></form>



</div> <!-- settlementSheetApp -->



    \n""")


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
    innovation_heading = Template("""\n
    <h5>$name</h5><p class="$show_subhead campaign_summary_innovation_subhead innovation_gradient">$subhead</p>
    \n""")


class meta:
    """ This is for HTML that doesn't really fit anywhere else, in terms of
    views, etc. Use this for helpers/containers/administrivia/etc. """

    basic_http_header = "Content-type: text/html\n\n"
    basic_file_header = "Content-Disposition: attachment; filename=%s\n"

    hide_full_page_loader = '<script type="text/javascript">hideFullPageLoader();</script>'

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

    start_head = Template("""<!DOCTYPE html>\n<html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8" />
        <meta name="theme-color" content="#000000">
        <title>$title</title>
        <link rel="stylesheet" type="text/css" href="/media/fonts.css?v=$version">
        <link rel="stylesheet" type="text/css" href="/media/style.css?v=$version">
        <link rel="stylesheet" type="text/css" href="/media/color.css?v=$version">
        <link rel="stylesheet" type="text/css" href="/media/settlement_event_log.css?v=$version">
        <link rel="stylesheet" type="text/css" href="/media/hunt_phase.css?v=$version">
        <link rel="stylesheet" type="text/css" href="/media/help-tip.css">
        <link rel="stylesheet" type="text/css" href="/media/z-index.css?v=$version">
    """).safe_substitute(
        title = settings.get("application","title"),
        version = settings.get('application', 'version'),
    )

    saved_dialog = """\n
    <div id="saved_dialog" class="saved_dialog_frame" style="">
        <div class="kd_blue saved_dialog_inner">
            <span class="saved_dialog_cap">S</span>
            Saving...
        </div>
    </div>

    <div id="error_dialog" class="saved_dialog_frame" style="">
        <div class="kd_alert_no_exclaim saved_dialog_inner">
            <span class="error_dialog_cap">E</span>
            <b>An Error Occurred!</b>
        </div>
    </div>

    <div
        id="apiErrorModal"
        class="api_error_modal hidden ease clickable"
        onclick="hideAPIerrorModal()">
    >
        <p class="api_error_debug">User login: {{user_login}}</p>
        <p class="api_error_debug">Settlement OID: {{settlement.sheet._id.$oid}}</p>
        <p id="apiErrorModalMsgRequest" class="api_error_debug"></p>
        <p id="apiErrorModalMsg" class="kd_alert_no_exclaim api_error_modal_msg"></p>
        <p>Tap or click anywhere to continue...</p>
    </div>
    \n"""

    full_page_loader = """\n
    <div id="fullPageLoader" class="full_page_loading_spinner">
        <img class="full_page_loading_spinner" src="/media/loading_io.gif">
    </div>
    \n"""
    corner_loader = """\n
    <div id="cornerLoader" class="corner_loading_spinner">
        <img class="corner_loading_spinner" src="/media/loading_io.gif">
    </div>
    \n"""
    mobile_hr = '<hr class="mobile_only"/>'
    dashboard_alert = Template("""\n\
    <div class="dashboard_alert_spacer"></div>
    <div class="kd_alert dashboard_alert">
    $msg
    </div>
    \n""")


    error_report_email = Template("""\n\
    Greetings!<br/><br/>&ensp;User $user_email [$user_id] has submitted an error report!<br/><br/>The report goes as follows:<hr/>$body<hr/>&ensp;...and that's it. Good luck!<br/><br/>Your friend,<br/>&ensp; meta.error_report_email
    \n""")
    view_render_fail_email = Template("""\n
    Greetings!<br/><br/>&ensp;User $user_email [$user_id] was logged out of the webapp instance on <b>$hostname</b> due to a render failure at $error_time.<br/><br/>&ensp;The traceback from the exception was this:<hr/><code>$exception</code><hr/>&ensp;The session object was this:<hr/><code>$session_obj</code><hr/>&ensp;Good hunting!<br/><br/>Your friend,<br/>meta.view_render_fail_email()
    \n""")






def render(view_html, head=[], http_headers=None, body_class=None, include_templates=[]):
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


    #
    #   HEAD ELEMENT
    #

    output += meta.start_head

    output += """\n\
    <!-- android mobile desktop/app stuff -->
    <link rel="manifest" href="/manifest.json">

    <!-- fucking jquery's dumb ass -->
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.7/jquery.js"></script> 

    <!-- angular app -->
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.5.4/angular.min.js"></script>

    <script src="/media/kdmManager.js?v=%s"></script>
    \n""" % settings.get("application", "version")

    for element in head:
        output += element

    # GA goes at the bottom of the head -- as per their docs
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

    output += "</head>"

    #
    #   BODY ELEMENT   
    #

    # 1. open the body
    output += '\n<body class="%s" ng-app="kdmManager" ng-controller="rootController">\n' % body_class

    # 3. start the container
    output += '<div id="container" onclick="closeNav()" >'

    # 4. insert the incoming HTML
    output += view_html

    output += '</div><!-- container -->'

    # 5. add on all required templates; start w/ the default/baseline
    ui_templates = ['nav.html', 'new_survivor.html','report_error.html', 'survivor_search.html']
    ui_templates += include_templates
    for t in ui_templates:
        output += template_file_to_str(t)

    # 6. close the container and the body
    output += '</body>\n</html>'

    # 7. turn the who thing into a template and stamp the API URL in
    output = Template(output).safe_substitute(api_url = api.get_api_url())

    #
    # print and finish
    #
    print(output.encode('utf8'))

