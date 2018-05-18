# coding=utf-8
#!/usr/bin/env python

#   standard
from datetime import datetime, timedelta
import os
from string import Template
import sys

#   custom
import admin
import api
from session import Session
from utils import load_settings, mdb, get_logger, get_latest_update_string

settings = load_settings()
logger = get_logger()



class survivor:

    form = Template("""\n\

<script src="/js/survivorSheet.js?v=$application_version"></script>

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
                <b>Stwalwart:</b> {{settlement.game_assets.abilities_and_impairments.stalwart.summary}}
            </div>
            <div class="kd_sheet_ui_row_tip" ng-if="survivor.sheet.abilities_and_impairments.indexOf('prepared') != -1">
                <b>Prepared:</b> {{settlement.game_assets.abilities_and_impairments.prepared.summary}}
            </div>
            <div class="kd_sheet_ui_row_tip" ng-if="survivor.sheet.abilities_and_impairments.indexOf('matchmaker') != -1">
                <b>Matchmaker:</b> {{settlement.game_assets.abilities_and_impairments.matchmaker.summary}}
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
                <b>Analyze:</b> {{settlement.game_assets.abilities_and_impairments.analyze.summary}}
            </div>
            <div class="kd_sheet_ui_row_tip" ng-if="survivor.sheet.abilities_and_impairments.indexOf('explore') != -1">
                <b>Explore:</b> {{settlement.game_assets.abilities_and_impairments.explore.summary}}
            </div>
            <div class="kd_sheet_ui_row_tip" ng-if="survivor.sheet.abilities_and_impairments.indexOf('tinker') != -1">
                <b>Tinker:</b> {{settlement.game_assets.abilities_and_impairments.tinker.summary}}
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
                    ng-options="fa.handle as fa.selector_text for fa in FAoptions | orderObjectBy:'handle':false"
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
                    ng-options="d.handle as d.selector_text for d in dOptions | orderObjectBy:'handle':false"
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
                        title="Date({{event.created_on.$date|date:'yyyy-MM-dd @ h:mma'}});"
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

</div><!-- end of the survivorSheetController scope -->


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

    form = """\n\

    <script src="/js/settlementSheet.js?v=$application_version"></script>

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
                        fa_dict.handle as fa_dict.name disable when fa_dict.select_disabled for fa_dict in settlement.game_assets.inspirational_statue_options
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
                class="settlement_sheet_line_item location_container clickable"
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
                        ng-click="setLostSettlements()"
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
    \n"""


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
            Saved!
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

    start_container = '\n<div id="container" onclick="closeNav()" >'
    close_container = '\n</div><!-- container -->'


    error_report_email = Template("""\n\
    Greetings!<br/><br/>&ensp;User $user_email [$user_id] has submitted an error report!<br/><br/>The report goes as follows:<hr/>$body<hr/>&ensp;...and that's it. Good luck!<br/><br/>Your friend,<br/>&ensp; meta.error_report_email
    \n""")
    view_render_fail_email = Template("""\n
    Greetings!<br/><br/>&ensp;User $user_email [$user_id] was logged out of the webapp instance on <b>$hostname</b> due to a render failure at $error_time.<br/><br/>&ensp;The traceback from the exception was this:<hr/><code>$exception</code><hr/>&ensp;The session object was this:<hr/><code>$session_obj</code><hr/>&ensp;Good hunting!<br/><br/>Your friend,<br/>meta.view_render_fail_email()
    \n""")



def get_template(template_file_name, output_format=str):
    """ Takes template file name (not a path) as input, finds it,
    turns it into a string, and spits it out. """

    if not os.path.splitext(template_file_name)[1] == '.html':
        template_file_name += '.html'

    rel_path = os.path.join('templates', template_file_name)

    # make sure it's there; otherwise raise an exception w the abs path
    if not os.path.isfile(rel_path):
        raise IOError("Cannot find HTML template file '%s'" % os.path.abspath(rel_path))

    raw = file(rel_path, 'rb').read()

    if output_format == Template:
        return Template(raw)

    return raw



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
    <script src="https://ajax.googleapis.com/ajax/libs/angularjs/1.5.4/angular-animate.js"></script>

    <script src="/js/kdmManager.js?v=%s"></script>
    \n""" % (settings.get('application', 'version'))

    # arbitrary head insertions
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

    # 2. append generic body HTML -> all views except login
    output += meta.saved_dialog
    output += meta.corner_loader
    output += meta.full_page_loader

    # 3. put the session's current view (including all UI templates) into the
    #   container element
    output += view_html
    output += '</body>\n</html>'

    #
    # print and finish
    #
    print(output.encode('utf8'))

