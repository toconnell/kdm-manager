#!/usr/bin/env python

#   standard
import Cookie
from datetime import datetime, timedelta
from string import Template
import sys

#   custom
import admin
from session import Session
from utils import load_settings, mdb, get_logger

settings = load_settings()
logger = get_logger()

user_error_msg = Template('<div id="user_error_msg" class="$err_class">$err_msg</div>')

class ui:
    game_asset_select_top = Template("""\n\
    <select name="$operation$name" onchange="this.form.submit()">
    <option selected disabled hidden value="">$operation_pretty $name_pretty</option>
    """)
    game_asset_select_row = Template('\t  <option value="$asset">$asset</option>\n')
    game_asset_select_bot = '    </select>\n'
    game_asset_add_custom = Template("""\n\
<input onchange="this.form.submit()" type="text" class="full_width" name="add_$asset_name" placeholder="add custom $asset_name"/>
    \n""")


class dashboard:
    # settlement administrivia; needs to be above the dashboard accordions
    new_settlement_button = '<form method="POST"><input type="hidden" name="change_view" value="new_settlement" /><button class="success">+ New Settlement</button></form>\n'
    new_settlement_form = """\n\
    <h3>Create a New Settlement</h3>
    <form method="POST">
    <input type="hidden" name="new" value="settlement" />
    <input type="text" name="settlement_name" placeholder="Settlement Name"/ class="full_width">
    <button class="success">SAVE</button>
    </form>
    \n"""

    # flash
    down_arrow_flash = '<img class="dashboard_down_arrow" src="%s/icons/down_arrow.png"/> ' % settings.get("application", "STATIC_URL")
    campaign_flash = '<img class="dashboard_icon" src="%s/icons/campaign.png"/> ' % settings.get("application", "STATIC_URL")
    settlement_flash = '<img class="dashboard_icon" src="%s/icons/settlement.png"/> ' % settings.get("application", "STATIC_URL")
    system_flash = '<img class="dashboard_icon" src="%s/icons/system.png"/> ' % settings.get("application", "STATIC_URL")

    # dashboard accordions
    motd = Template("""\n
    <h2 class="clickable gradient_silver" onclick="showHide('system_div')"> <img class="dashboard_icon" src="%s/icons/system.png"/> System Info %s</h2>
    <div id="system_div" style="display: none;" class="dashboard_accordion gradient_silver">
    <p>KD:M Manager! Version $version.</p><hr/>
    <p>$users users are managing $settlements settlements and $live_survivors survivors (in $sessions sessions).</p>
    <p>The total death count across all settlements is $dead_survivors.</p>
    <p>
    Latest Fatality:<br />
    &ensp; <b>$casualty_name</b> [$casualty_sex] of <b>$casualty_settlement</b><br/>
    &ensp; $cause_of_death <br/>
    &ensp; XP: $casualty_xp - Courage: $casualty_courage <br /> &ensp; Understanding: $casualty_understanding
    </p>
    <hr/>
    <p>This application is a work in progress! Use <a href="http://blog.kdm-manager.com"/>blog.kdm-manager.com</a> to report issues/bugs or to ask questions, share ideas for features, make comments, etc.</p><hr/>
    <p>Currently signed in as: <i>$login</i></p>
    </div>
    """ % (settings.get("application", "STATIC_URL"), down_arrow_flash))
    campaign_summary = Template("""\n\
    <h2 class="clickable gradient_purple" onclick="showHide('campaign_div')"> <img class="dashboard_icon" src="%s/icons/campaign.png"/> Campaigns %s </h2>
    <div id="campaign_div" style="display: $display" class="dashboard_accordion gradient_purple">
    <p>Games you are currently playing.</p>
    $campaigns
    </div>
    \n""" % (settings.get("application", "STATIC_URL"), down_arrow_flash))
    settlement_summary = Template("""\n\
    <h2 class="clickable gradient_orange" onclick="showHide('settlement_div')"> <img class="dashboard_icon" src="%s/icons/settlement.png"/> Settlements %s </h2>
    <div id="settlement_div" style="display: $display" class="dashboard_accordion gradient_orange">
    <p>Manage your settlements. You may not manage a settlement you did not create.</p>
    $settlements
    %s
    </div>
    \n""" % (settings.get("application", "STATIC_URL"), down_arrow_flash, new_settlement_button))
    survivor_summary = Template("""\n\
    <h2 class="clickable gradient_green" onclick="showHide('survivors_div')"> <img class="dashboard_icon" src="%s/icons/survivor.png"/> Survivors %s</h2>
    <div id="survivors_div" style="display: none;" class="dashboard_accordion gradient_green">
    <p>Manage survivors created by you or shared with you. New survivors are created from the "Campaign" and "Settlement" views.</p>
    $survivors
    </div>
    \n""" % (settings.get("application", "STATIC_URL"), down_arrow_flash))

    # misc html assets
    home_button = '<form method="POST" action="#"><input type="hidden" name="change_view" value="dashboard"/><button id="floating_dashboard_button"> %s </button></form>\n' % system_flash
    view_asset_button = Template("""\n\
    <form method="POST" action="#">
    <input type="hidden" name="view_$asset_type" value="$asset_id" />
    <button id="$button_id" class="$button_class" $disabled>$asset_name</button>
    </form>
    \n""")





class survivor:
    campaign_asset = Template("""\n\
      <div class="survivor_campaign_asset_container">

        <form method="POST" action="#edit_hunting_party">
         <input type="hidden" name="modify" value="survivor" />
         <input type="hidden" name="asset_id" value="$survivor_id" />
         <input type="hidden" name="view_game" value="$settlement_id" />
         <input type="hidden" name="in_hunting_party" value="$hunting_party_checked"/>
         <button id="add_survivor_to_party" class="$able_to_hunt" $able_to_hunt $disabled>::</button>
        </form>

        <form method="POST" action="#">
         <input type="hidden" name="view_survivor" value="$survivor_id" />
         <button id="survivor_campaign_asset" class="$b_class" $disabled>
            <center><b>$name</b> [$sex] </center>
            $special_annotation
            &ensp; XP: $hunt_xp &ensp; Survival: $survival<br/>
            &ensp; Insanity: $insanity <br/>
            &ensp; Courage: $courage<br/>
            &ensp; Understanding: $understanding
         </button>
        </form>
      </div>
      <hr class="invisible"/>
    \n""")
    form = Template("""\n\
    $campaign_link

    <form method="POST" id="autoForm" action="#">
        <button id="save_button" class="success">Save</button>
        <input type="hidden" name="form_id" value="survivor_top" />
        <input type="hidden" name="modify" value="survivor" />
        <input type="hidden" name="asset_id" value="$survivor_id" />

        <input id="topline_name_fixed" class="full_width" type="text" name="name" value="$name" placeholder="Survivor Name"/>
        <br /><br /><br />
        $epithets
        <br />
        $add_epithets<br />
        $rm_epithets
        <input onchange="this.form.submit()" class="full_width" type="text" name="add_epithet" placeholder="add a custom epithet"/>
        <hr />

        <!-- SEX, SURVIVAL and MISC. SURVIVOR ATTRIBUTES -->

        <p>
         Survivor sex: <b>$sex</b>
            <!-- dead -->
         <input type='hidden' value='unchecked' name='toggle_dead'/>
         <input type="checkbox" id="dead" class="radio_principle" name="toggle_dead" value="checked" onclick="showHide('COD')" $dead_checked /> 
         <label class="radio_principle_label floating_label" for="dead"> Dead </label>

            <!-- retired -->
         <input type='hidden' value='unchecked' name='toggle_retired'/>
         <input type="checkbox" id="retired" class="radio_principle" name="toggle_retired" value="checked" $retired_checked> 
         <label class="radio_principle_label" for="retired" style="float: right; clear: none;"> Retired </label>
        </p>

        <div id="COD" style="display: $show_COD">
            <hr/>
            <input onchange="this.form.submit()" class="full_width" type="text" name="cause_of_death" placeholder="Cause of Death" value="$cause_of_death"/>
        </div>

        <hr/>

        <div class="big_number_container left_margin">
            <button class="incrementer" onclick="increment('survivalBox');">+</button>
            <input type="number" id="survivalBox" class="big_number_square" name="survival" value="$survival" max="$survival_limit" min="0"/>
            <button class="decrementer" onclick="decrement('survivalBox');">-</button>
        </div>
        <div class="big_number_caption">Survival <p>(max: $survival_limit)</p></div>
        <hr />
        <p>
         <input type='hidden' value='unchecked' name='toggle_cannot_spend_survival'/>
         <input onchange="this.form.submit()" type="checkbox" id="cannot_spend_survival" class="radio_principle" name="toggle_cannot_spend_survival" value="checked" $cannot_spend_survival_checked /> 
         <label class="radio_principle_label" for="cannot_spend_survival"> Cannot spend survival </label>


         $survival_actions
        </p>
        <hr />
        $fighting_arts
        $departure_buffs
        $abilities_and_impairments
        $disorders

        <a id="edit_attribs" />

        <hr/> <!-- logical break; same form -->

        <input id="movementBox" class="big_number_square" type="number" name="Movement" value="$movement"/>
        <div class="big_number_caption">Movement<br />
            <div>
            <button class="incrementer" onclick="increment('movementBox');">+</button>
            <button class="decrementer" onclick="decrement('movementBox');">-</button>
            </div>
        </div>
        <br /><hr/>
        <input id="accuracyBox" class="big_number_square" type="number" name="Accuracy" value="$accuracy"/>
        <div class="big_number_caption">Accuracy<br/>
            <div>
            <button class="incrementer" onclick="increment('accuracyBox');">+</button>
            <button class="decrementer" onclick="decrement('accuracyBox');">-</button>
            </div>
        </div>
        <br /><hr/>
        <input id="strengthBox" class="big_number_square" type="number" name="Strength" value="$strength"/>
        <div class="big_number_caption">Strength<br/>
            <div>
            <button class="incrementer" onclick="increment('strengthBox');">+</button>
            <button class="decrementer" onclick="decrement('strengthBox');">-</button>
            </div>
        </div>
        <br /><hr/>
        <input id="evasionBox" class="big_number_square" type="number" name="Evasion" value="$evasion"/>
        <div class="big_number_caption">Evasion<br/>
            <div>
            <button class="incrementer" onclick="increment('evasionBox');">+</button>
            <button class="decrementer" onclick="decrement('evasionBox');">-</button>
            </div>
        </div>
        <br /><hr/>
        <input id="luckBox" class="big_number_square" type="number" name="Luck" value="$luck"/>
        <div class="big_number_caption">Luck<br/>
            <div>
            <button class="incrementer" onclick="increment('luckBox');">+</button>
            <button class="decrementer" onclick="decrement('luckBox');">-</button>
            </div>
        </div>
        <br /><hr/>
        <input id="speedBox" class="big_number_square" type="number" name="Speed" value="$speed"/>
        <div class="big_number_caption">Speed<br/>
            <div>
            <button class="incrementer" onclick="increment('speedBox');">+</button>
            <button class="decrementer" onclick="decrement('speedBox');">-</button>
            </div>
        </div>
        <br /><hr/>


        <h3>Bonuses</h3>
        $settlement_buffs


        <a id="edit_hit_boxes" />

        <hr/>   <!-- LOGICAL break -->

                        <!-- HIT BOXES ; still the same form -->


        <div id="survivor_hit_box">
            <div class="big_number_container right_border">
                <button class="incrementer" onclick="increment('insanityBox');">+</button>
                    <input id="insanityBox" type="number" class="shield" name="Insanity" value="$insanity" style="color: $insanity_number_style; "/>
                    <font id="hit_box_insanity">Insanity</font>
                <button class="decrementer" onclick="decrement('insanityBox');">-</button>
            </div>

            <div class="hit_box_detail">
             <input type='hidden' value='unchecked' name='toggle_brain_damage_light'/>
             <input type="checkbox" id="brain_damage_light" class="radio_principle" name="toggle_brain_damage_light" $brain_damage_light_checked /> 
             <label id="damage_box" class="radio_principle_label" for="brain_damage_light"> L </label>
                <h2>Brain</h2>
                If your insanity is 3+, you are <b>Insane</b>.
            </div>
        </div> <!-- survivor_hit_box -->

                <!-- HEAD -->
        <div id="survivor_hit_box">
            <div class="big_number_container right_border">
                <button class="incrementer" onclick="increment('headBox');">+</button>
                    <input id="headBox" type="number" class="shield" name="Head" value="$head"/>
                <button class="decrementer" onclick="decrement('headBox');">-</button>
            </div>
            <div class="hit_box_detail">
             <input type='hidden' value='unchecked' name='toggle_head_damage_heavy'/>
             <input type="checkbox" id="head_damage_heavy" class="radio_principle" name="toggle_head_damage_heavy" $head_damage_heavy_checked /> 
             <label id="damage_box" class="radio_principle_label" for="head_damage_heavy"> H </label>
                <h2>Head</h2>
                <font color="#C60000">H</font>eavy Injury: Knocked Down
            </div>
        </div> <!-- survivor_hit_box -->

                <!-- ARMS -->
        <div id="survivor_hit_box">
            <div class="big_number_container right_border">
                <button class="incrementer" onclick="increment('armsBox');">+</button>
                    <input id="armsBox" type="number" class="shield" name="Arms" value="$arms"/>
                <button class="decrementer" onclick="decrement('armsBox');">-</button>
            </div>
            <div class="hit_box_detail">
             <input type='hidden' value='unchecked' name='toggle_arms_damage_heavy'/>
             <input type="checkbox" id="arms_damage_heavy" class="radio_principle" name="toggle_arms_damage_heavy" $arms_damage_heavy_checked /> 
             <label id="damage_box" class="radio_principle_label" for="arms_damage_heavy"> H </label>
             <input type='hidden' value='unchecked' name='toggle_arms_damage_light'/>
             <input type="checkbox" id="arms_damage_light" class="radio_principle" name="toggle_arms_damage_light" $arms_damage_light_checked /> 
             <label id="damage_box" class="radio_principle_label" for="arms_damage_light"> L </label>
                <h2>Arms</h2>
                <font color="#C60000">H</font>eavy Injury: Knocked Down
            </div>
        </div> <!-- survivor_hit_box -->

                <!-- BODY -->
        <div id="survivor_hit_box">
            <div class="big_number_container right_border">
                <button class="incrementer" onclick="increment('bodyBox');">+</button>
                    <input id="bodyBox" type="number" class="shield" name="Body" value="$body"/>
                <button class="decrementer" onclick="decrement('bodyBox');">-</button>
            </div>
            <div class="hit_box_detail">
             <input type='hidden' value='unchecked' name='toggle_body_damage_heavy'/>
             <input type="checkbox" id="body_damage_heavy" class="radio_principle" name="toggle_body_damage_heavy" $body_damage_heavy_checked /> 
             <label id="damage_box" class="radio_principle_label" for="body_damage_heavy"> H </label>
             <input type='hidden' value='unchecked' name='toggle_body_damage_light'/>
             <input type="checkbox" id="body_damage_light" class="radio_principle" name="toggle_body_damage_light" $body_damage_light_checked /> 
             <label id="damage_box" class="radio_principle_label" for="body_damage_light"> L </label>
                <h2>Body</h2>
                <font color="#C60000">H</font>eavy Injury: Knocked Down
            </div>
        </div> <!-- survivor_hit_box -->

                <!-- WAIST -->
        <div id="survivor_hit_box">
            <div class="big_number_container right_border">
                <button class="incrementer" onclick="increment('waistBox');">+</button>
                    <input id="waistBox" type="number" class="shield" name="Waist" value="$waist"/>
                <button class="decrementer" onclick="decrement('waistBox');">-</button>
            </div>
            <div class="hit_box_detail">
             <input type='hidden' value='unchecked' name='toggle_waist_damage_heavy'/>
             <input type="checkbox" id="waist_damage_heavy" class="radio_principle" name="toggle_waist_damage_heavy" $waist_damage_heavy_checked /> 
             <label id="damage_box" class="radio_principle_label" for="waist_damage_heavy"> H </label>
             <input type='hidden' value='unchecked' name='toggle_waist_damage_light'/>
             <input type="checkbox" id="waist_damage_light" class="radio_principle" name="toggle_waist_damage_light" $waist_damage_light_checked /> 
             <label id="damage_box" class="radio_principle_label" for="waist_damage_light"> L </label>
                <h2>Waist</h2>
                <font color="#C60000">H</font>eavy Injury: Knocked Down
            </div>
        </div> <!-- survivor_hit_box -->

        <!-- LEGS -->
        <div id="survivor_hit_box">
            <div class="big_number_container right_border">
                <button class="incrementer" onclick="increment('legsBox');">+</button>
                    <input id="legsBox" type="number" class="shield" name="Legs" value="$legs"/>
                <button class="decrementer" onclick="decrement('legsBox');">-</button>
            </div>
            <div class="hit_box_detail">
             <input type='hidden' value='unchecked' name='toggle_legs_damage_heavy'/>
             <input type="checkbox" id="legs_damage_heavy" class="radio_principle" name="toggle_legs_damage_heavy" $legs_damage_heavy_checked /> 
             <label id="damage_box" class="radio_principle_label" for="legs_damage_heavy"> H </label>
             <input type='hidden' value='unchecked' name='toggle_legs_damage_light'/>
             <input type="checkbox" id="legs_damage_light" class="radio_principle" name="toggle_legs_damage_light" $legs_damage_light_checked /> 
             <label id="damage_box" class="radio_principle_label" for="legs_damage_light"> L </label>
                <h2>Legs</h2>
                <font color="#C60000">H</font>eavy Injury: Knocked Down
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


        <hr />  <!-- logical break -->


                        <!-- HUNT XP and AGE -->

        <div class="big_number_container left_margin">
            <button class="incrementer" onclick="increment('huntXpBox');">+</button>
            <input id="huntXpBox" class="big_number_square" type="number" name="hunt_xp" value="$hunt_xp" min="0"/>
            <button class="decrementer" onclick="decrement('huntXpBox');">-</button>
        </div>
        <div class="big_number_caption">Hunt XP</div>
        <br />
        <p>
            <img class="icon" src="$MEDIA_URL/icons/trigger_story_event.png" /> <b>Age</b> occurs at 2, 6, 10 and 15. The Survivor retires at 16.
        </p>

        <hr/>

                        <!-- WEAPON PROFICIENCY -->
        <h3>Weapon Proficiency</h3>
        <div class="big_number_container left_margin">
            <button class="incrementer" onclick="increment('proficiencyBox');">+</button>
            <input id="proficiencyBox" class="big_number_square" type="number" name="Weapon Proficiency" value="$weapon_proficiency" min="0"/>
            <button class="decrementer" onclick="decrement('proficiencyBox');">-</button>
        </div>
        <div class="big_number_caption">
            <input type="text" class="full_width" placeholder="Type: Select before hunt" value="$weapon_proficiency_type" name="weapon_proficiency_type" style="width: 50%; clear: none; "/>
        </div>
        <p>       <b>Specialist</b> at 3<br/><b>Master</b> at 8   </p>

        <br/>
        <hr/>

                        <!-- COURAGE AND UNDERSTANDING -->

        <div id="block_group">
        <br />
        <div class="big_number_container left_margin">
            <button class="incrementer" onclick="increment('courageBox');">+</button>
            <input id="courageBox" class="big_number_square" type="number" name="Courage" value="$courage" min="0"/>
            <button class="decrementer" onclick="decrement('courageBox');">-</button>
        </div>
        <div class="big_number_caption">Courage</div>
        <br />
        <p>
        <img class="icon" src="$MEDIA_URL/icons/trigger_story_event.png" /> <b>Bold</b> occurs at 3<br/><img class="icon" src="$MEDIA_URL/icons/trigger_story_event.png" /> <b>See the Truth</b> occurs at 9.

          <input type="radio" id="stalwart_button" class="radio_principle" name="courage_attribute" value="Stalwart" $stalwart_checked />
          <label class="radio_principle_label" for="stalwart_button"> <b>Stalwart:</b> can't be knocked down by brain trauma or intimidate. </label>
          <input type="radio" id="prepared_button" class="radio_principle" name="courage_attribute" value="Prepared" $prepared_checked />
          <label class="radio_principle_label" for="prepared_button"> <b>Prepared:</b> Add hunt XP to your roll when determining a straggler. </label>
          <input type="radio" id="matchmaker_button" class="radio_principle" name="courage_attribute" value="Matchmaker" $matchmaker_checked />
          <label class="radio_principle_label" for="matchmaker_button"> <b>Matchmaker:</b> Spend 1 endeavor to trigger intimacy story event. </label>
        </div>
        <div id="block_group">
        <br />
        <div class="big_number_container left_margin">
            <button class="incrementer" onclick="increment('understandingBox');">+</button>
            <input id="understandingBox" class="big_number_square" type="number" name="Understanding" value="$understanding" min="0"/>
            <button class="decrementer" onclick="decrement('understandingBox');">-</button>
        </div>
        <div class="big_number_caption">Understanding</div>
        <br />
        <p>
        <img class="icon" src="$MEDIA_URL/icons/trigger_story_event.png" /> <b>Insight</b> occurs at 3<br/><img class="icon" src="$MEDIA_URL/icons/trigger_story_event.png" /> <b>White Secret</b> occurs at 9.
          <input type="radio" id="analyze_button" class="radio_principle" name="understanding_attribute" value="Analyze" $analyze_checked />
          <label class="radio_principle_label" for="analyze_button"> <b>Analyze:</b> Look at top AI card and return it to the top of the deck.</label>
          <input type="radio" id="explore_button" class="radio_principle" name="understanding_attribute" value="Explore" $explore_checked />
          <label class="radio_principle_label" for="explore_button"> <b>Explore:</b>  Add +2 to your investigate roll results.</label>
          <input type="radio" id="tinker_button" class="radio_principle" name="understanding_attribute" value="Tinker" $tinker_checked />
          <label class="radio_principle_label" for="tinker_button"> <b>Tinker:</b> +1 endeavor when a returning survivor. </label>

        </div>
    </form>


    <a id="edit_fighting_arts" />


    <hr/> <!-- logical division; new form starts here too -->



                        <!-- FIGHTING ARTS -->


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
            $add_fighting_arts<br/>
            $rm_fighting_arts

    <a id="edit_disorders"/>

        <hr/>
    </form>

                        <!-- DISORDERS - HAS ITS OWN FORM-->

    <form method="POST" id="autoForm" action="#edit_disorders">
        <input type="hidden" name="form_id" value="survivor_edit_disorders" />
        <input type="hidden" name="modify" value="survivor" />
        <input type="hidden" name="asset_id" value="$survivor_id" />
        <h3>Disorders</h3>
        <p>Maximum 3.</p>

        $disorders
        $add_disorders<br />
        $rm_disorders

        <a id="edit_abilities"/>

    </form>


    <hr/>

                        <!-- ABILITIES AND IMPAIRMENTS -->

    <form method="POST" id="autoForm" action="#edit_abilities">
        <input type="hidden" name="form_id" value="survivor_edit_abilities" />
        <input type="hidden" name="modify" value="survivor" />
        <input type="hidden" name="asset_id" value="$survivor_id" />

        <h3>Abilities & Impairments</h3>
        <p>
         <input type='hidden' value='unchecked' name='toggle_skip_next_hunt'/>
         <input onchange="this.form.submit()" type="checkbox" id="skip_next_hunt" class="radio_principle" name="toggle_skip_next_hunt" value="checked" $skip_next_hunt_checked />
         <label class="radio_principle_label" for="skip_next_hunt" id="float_right_toggle"> Skip Next<br/>Hunt </label>
            $abilities_and_impairments<br/>
            $add_abilities_and_impairments
        <input onchange="this.form.submit()" class="full_width" type="text" name="add_ability" placeholder="add ability or impairment"/>
            $remove_abilities_and_impairments

        </p>
        <hr/>

        <input onchange="this.form.submit()" class="full_width" type="text" name="email" placeholder="email" value="$email"/>
        <hr />

    </form>


    <br/><hr/>


    <form method="POST" onsubmit="return confirm('This cannot be undone! Press OK to permanently delete this survivor forever, which is NOT THE SAME THING as marking it dead: permanently deleting the survivor prevents anyone from viewing and/or editing it ever again!');"><input type="hidden" name="remove_survivor" value="$survivor_id"/><button class="error">Permanently Delete Survivor</button></form>
    <hr/>
    <br />

    \n""")
    new = Template("""\n\
    <h3>Create a New Survivor</h3>
    <form method="POST" action="#">
    <input type="hidden" name="new" value="survivor" />
    <input type="hidden" name="created_by" value="$created_by" />
    <input type="hidden" name="settlement_id" value="$home_settlement">
    <input type="text" name="name" placeholder="Survivor Name"/ class="full_width">
    <input type="text" name="email" placeholder="Survivor Email"/ class="full_width" value="$user_email">
    <div id="block_group">
    <h2>Survivor Sex</h2>
    <input type="radio" id="male_button" class="radio_principle" name="sex" value="Male" checked/> 
      <label class="radio_principle_label" for="male_button"> Male </label>
    <input type="radio" id="female_button" class="radio_principle" name="sex" value="Female"/> 
      <label class="radio_principle_label" for="female_button"> Female </label>
    </div>
    <button class="success">SAVE</button>
    </form>
    \n""")


class settlement:
    return_hunting_party = Template("""\n\
        <form method="POST">
            <input type="hidden" name="return_hunting_party" value="$settlement_id"/>
            <button>Return Hunting Party</button>
        </form>
    \n""")
    summary = Template("""\n\
        <h1> %s $settlement_name</h1>
        <p>Population: $population ($death_count deaths)</p><hr/>
        <p>Survival Limit: $survival_limit</p><hr/>
        <a id="edit_hunting_party"/>
        <h3>Survivors</h3>
        $survivors
        <hr/>
        <form method="POST">
        <input type="hidden" name="change_view" value="new_survivor"/>
        <button class="success">+ Create New Survivor</button>
        </form>
        <hr/>
        <h3>Principles</h3>
        $principles
        <h3>Innovations</h3>
        $innovations
        <hr/>
        <h3>Bonuses</h3>
        <h4>Departing</h4>
        $departure_bonuses
        <h4>During Settlement</h4>
        $settlement_bonuses
        $survivor_bonuses
        <hr/>
        <h3>Locations</h3>
        <p>$locations</p>
        <hr/>
        <h3>Monsters</h3>
        <h4>Defeated</h4>
        <p>$defeated_monsters</p>
        <h4>Quarries</h4>
        <p>$quarries</p>
        <h4>Nemeses</h4>
        <p>$nemesis_monsters</p>
    \n""" % dashboard.campaign_flash)
    form = Template("""\n\
    $game_link

    <form method="POST" id="autoForm" action="#">
        <button id="save_button" class="success">Save</button>
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />

        <input id="topline_name" onchange="this.form.submit()" class="full_width" type="text" name="name" value="$name" placeholder="Settlement Name"/>
        <hr />
        <div class="big_number_container left_margin">
            <button class="incrementer" onclick="increment('survivalLimitBox');">+</button>
            <input id="survivalLimitBox" class="big_number_square" type="number" name="survival_limit" value="$survival_limit" min="$min_survival_limit"/>
            <button class="decrementer" onclick="decrement('survivalLimitBox');">-</button>
        </div>
        <div class="big_number_caption">Survival Limit<br />(min: $min_survival_limit)</div>
        <br /><hr />

            <h3>On Departure</h3>
            $departure_bonuses

        <hr/>

            <h3>During Settlement Phase</h3>
            $settlement_bonuses

        <hr />

        <div class="big_number_container left_margin">
            <button class="incrementer" onclick="increment('populationBox');">+</button>
            <input id="populationBox" class="big_number_square" type="number" name="population" value="$population" min="0"/>
            <button class="decrementer" onclick="decrement('populationBox');">-</button>
        </div>
        <div class="big_number_caption">Population</div>

        <br /><hr />

        <div class="big_number_container left_margin">
            <button class="incrementer" onclick="increment('deathCountBox');">+</button>
            <input id="deathCountBox" class="big_number_square" type="number" name="death_count" value="$death_count" min="0"/>
            <button class="decrementer" onclick="decrement('deathCountBox');">-</button>
        </div>
        <div class="big_number_caption">Death Count</div>

        <br />

    </form> <!-- ending the first form -->

    <hr /> <!-- Logical section Break -->


                    <!-- STORAGE - THIS IS ITS OWN FORM-->
    <form id="autoForm" method="POST" action="#edit_storage">
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />

        <div id="block_group">
        <h2>Storage</h2>
        <p>Gear and Resources may be stored without limit. Tap items to remove them.</p>
        <hr />

    <a id="edit_storage" />

        $storage
        $items_options<br />
         <input onchange="this.form.submit()" type="text" class="full_width" name="add_item" placeholder="add gear or resource"/>
        </div>
    </form>


                    <!-- LOCATIONS - THIS HAS ITS OWN FORM  -->

    <a id="edit_locations"/>
    <form id="autoForm" method="POST" action="#edit_locations">
    <input type="hidden" name="modify" value="settlement" />
    <input type="hidden" name="asset_id" value="$settlement_id" />

    <div id="block_group">
     <h2>Settlement Locations</h2>
     <p>Locations in your settlement.</p>
     $locations
     $locations_add
     $locations_rm
    </div>
    </form>



    <hr />  <!-- Logical Section Break -->

                    <!-- INNOVATIONS - HAS ITS OWN FORM-->

    <a id="edit_innovations"/>
    <form id="autoForm" method="POST" action="#edit_innovations">
    <input type="hidden" name="modify" value="settlement" />
    <input type="hidden" name="asset_id" value="$settlement_id" />
    <div id="block_group">
     <h2>Innovations</h2>
     <p>The settlement's innovations (including weapon masteries).</p>
     $innovations
     $innovations_add
     $innovations_rm
     $innovation_deck
    </div>
    </form>



                    <!-- PRINCIPLES - HAS ITS OWN FORM-->

    <a id="edit_principles"/>
    <form id="autoForm" method="POST" action="#edit_principles">
    <input type="hidden" name="modify" value="settlement" />
    <input type="hidden" name="asset_id" value="$settlement_id" />
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
    </form>

    <hr />  <!-- Logical Section Break -->



                    <!-- MILESTONES - HAS ITS OWN FORM-->

    <a id="edit_milestones"/>
    <form id="autoForm" method="POST" action="#edit_milestones">
    <input type="hidden" name="modify" value="settlement" />
    <input type="hidden" name="asset_id" value="$settlement_id" />
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
    </form>


    <hr /> <!-- Logical Section Break Here -->


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
     <input onchange="this.form.submit()" type="text" class="full_width" name="add_nemesis" placeholder="add nemesis"/>
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
     <p>$defeated_monsters</p>
     <input onchange="this.form.submit()" type="text" class="full_width" name="add_defeated_monster" placeholder="add defeated monster"/>
    </div>
    </form>

                    <!-- TIMELINE: HAS ITS OWN FORM  -->

    <a id="edit_timeline"/>
    <form id="autoForm" method="POST" action="#edit_timeline">
    <input type="hidden" name="modify" value="settlement" />
    <input type="hidden" name="asset_id" value="$settlement_id" />

    <br/>
    <h2 class="clickable" onclick="showHide('timelineBlock')">Timeline <img class="dashboard_down_arrow" src="http://media.kdm-manager.com/icons/down_arrow.png"/> </h2>
    <div id="timelineBlock" class="block_group" style="display: none;">
     <div class="big_number_container left_margin">
         <button class="incrementer" onclick="increment('lanternYearBox');">+</button>
         <input id="lanternYearBox" onchange="this.form.submit()" class="big_number_square" type="number" name="lantern_year" value="$lantern_year" min="1"/>
         <button class="decrementer" onclick="decrement('lanternYearBox');">-</button>
     </div>
     <div class="big_number_caption">Lantern Year</div>
     <br /><hr />
     $timeline
    </div> <!-- timelineBlock -->
    </form>
    <br/>

    <hr /> <!-- Logical Section Break Here -->

                    <!-- LOST SETTLEMENTS HAS ITS OWN FORM-->
    <a id="edit_lost_settlements"/>
    <form id="autoForm" method="POST" action="#edit_lost_settlements">
    <input type="hidden" name="modify" value="settlement" />
    <input type="hidden" name="asset_id" value="$settlement_id" />
    <input onchange="this.form.submit()" class="big_number_square" type="number" name="lost_settlements" value="$lost_settlements"/>
    <div class="big_number_caption">Lost Settlements</div>
    </form>
    <br/><hr/>

    <h3>Survivors</h3>
    $survivors

    <br />
    <hr />

    <form method="POST">
    <input type="hidden" name="change_view" value="new_survivor"/>
    <button class="success">+ Create New Survivor</button>
    </form>

    <hr/>

    <form method="POST" onsubmit="return confirm('This cannot be undone! Press OK to permanently delete this settlement AND ALL SURVIVORS WHO BELONG TO THIS SETTLEMENT forever.');"><input type="hidden" name="remove_settlement" value="$settlement_id"/><button class="error">Permanently Delete Settlement</button></form>
    \n""")



class login:
    """ The HTML for form-based authentication goes here."""
    form = """\n\
    <form method="POST">
    <input class="full_width" type="text" name="login" placeholder="email"/>
    <input class="full_width" type="password" name="password" placeholder="password"/>
    <button>Sign In (or Register)</button>
    </form>
    \n"""
    new_user = Template("""\n\
    <form method="POST">
    <input class="full_width" type="text" name="login" value="$login"/>
    <input class="full_width" type="password" name="password" placeholder="password"/>
    <input class="full_width" type="password" name="password_again" placeholder="password (again)"/>
    <button>Register New Email</button>
    </form>
    \n""")




class meta:
    """ This is for HTML that doesn't really fit anywhere else, in terms of
    views, etc. Use this for helpers/containers/administrivia/etc. """
    start_head = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n<title>%s</title>\n' % settings.get("application","title")
    stylesheet = Template('<link rel="stylesheet" type="text/css" href="$url">\n')
    close_head = '</head>\n<body>\n <div id="container">\n'
    false_body = 'Caught exception while rendering the current view!<hr/>The current session will be ended. Please try again.'
    close_body = '\n </div><!-- container -->\n</body>\n</html>'
    saved_dialog = '\n    <div id="saved_dialog" class="success">Saved!</div>'
    log_out_button = Template('\n\t<hr/><form id="logout" method="POST"><input type="hidden" name="remove_session" value="$session_id"/><button class="warn">SIGN OUT</button>\n\t</form>')




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
            create_new = admin.create_new_user(params["login"].value.strip().lower(), params["password"].value.strip(), params["password_again"].value.strip())
            if create_new == False:
                output = user_error_msg.safe_substitute(err_class="warn", err_msg="Passwords did not match! Please re-enter.")
            elif create_new is None:
                output = user_error_msg.safe_substitute(err_class="warn", err_msg="Email address could not be verified! Please re-enter.")
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
        elif auth == True:
            s = Session()
            session_id = s.new(params["login"].value.strip().lower())
            render(s.current_view_html(), head=[set_cookie_js(session_id)])
    else:
        output = login.form
    return output



#
#   render() func is the only thing that goes below here.
#

def render(view_html, head=[], http_headers=False):
    """ This is our basic render: feed it HTML to change what gets rendered. """

    output = http_headers
    if not http_headers:
        output = "Content-type: text/html\n\n"
    output += meta.start_head
    output += meta.stylesheet.safe_substitute(url=settings.get("application", "stylesheet"))

    output += """\n\
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

    output += meta.close_head
    if view_html:
        output += view_html
    else:
        output += meta.false_body
    output += meta.close_body

    print(output)
    sys.exit(0)     # this seems redundant, but it's necessary in case we want
                    #   to call a render() in the middle of a load, e.g. to just
                    #   finish whatever we're doing and show a page.
