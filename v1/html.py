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


class survivor:
    form = Template("""\n\
    $game_link

    <form method="POST" id="autoForm" action="#">
        <input type="hidden" name="form_id" value="survivor_top" />
        <button id="save_button" class="success">Save</button>
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
         <input type="checkbox" id="dead" class="radio_principle" name="toggle_dead" value="checked" $dead_checked /> 
         <label class="radio_principle_label" for="dead" style="float: right; clear: none; "> Dead </label>

            <!-- retired -->
         <input type='hidden' value='unchecked' name='toggle_retired'/>
         <input type="checkbox" id="retired" class="radio_principle" name="toggle_retired" value="checked" $retired_checked/> 
         <label class="radio_principle_label" for="retired" style="float: right; clear: none;"> Retired </label>
        </p>

         <hr/>

        <input class="big_number_square" type="number" name="survival" value="$survival" max="$survival_limit"/>
        <div class="big_number_caption">Survival (max: $survival_limit)</div>
        <br />
        <p>
         <input type='hidden' value='unchecked' name='toggle_cannot_spend_survival'/>
         <input onchange="this.form.submit()" type="checkbox" id="cannot_spend_survival" class="radio_principle" name="toggle_cannot_spend_survival" value="checked" $cannot_spend_survival_checked /> 
         <label class="radio_principle_label" for="cannot_spend_survival"> Cannot spend survival </label>


         $survival_actions
        </p>
        <hr />

        <h3>On Departure</h3>
        $departure_buffs

        <a id="edit_attribs" />

        <hr/> <!-- logical break; same form -->

        <input class="big_number_square" type="number" name="Movement" value="$movement"/>
        <div class="big_number_caption">Movement</div>
        <br /><hr/>
        <input class="big_number_square" type="number" name="Accuracy" value="$accuracy"/>
        <div class="big_number_caption">Accuracy</div>
        <br /><hr/>
        <input class="big_number_square" type="number" name="Strength" value="$strength"/>
        <div class="big_number_caption">Strength</div>
        <br /><hr/>
        <input class="big_number_square" type="number" name="Evasion" value="$evasion"/>
        <div class="big_number_caption">Evasion</div>
        <br /><hr/>
        <input class="big_number_square" type="number" name="Luck" value="$luck"/>
        <div class="big_number_caption">Luck</div>
        <br /><hr/>
        <input class="big_number_square" type="number" name="Speed" value="$speed"/>
        <div class="big_number_caption">Speed</div>
        <br /><hr/>


        <h3>Bonuses</h3>
        $settlement_buffs


        <a id="edit_hit_boxes" />

        <hr/>   <!-- LOGICAL break -->

                        <!-- HIT BOXES ; still the same form -->


        <div id="survivor_hit_box">
            <div id="shield_box">
                <input type="number" class="shield" name="Insanity" value="$insanity" style="color: $insanity_number_style; "/>
                <font id="hit_box_insanity">Insanity</font>
            </div>

            <div id="info_box">
             <input type='hidden' value='unchecked' name='toggle_brain_damage_light'/>
             <input type="checkbox" id="brain_damage_light" class="radio_principle" name="toggle_brain_damage_light" $brain_damage_light_checked /> 
             <label id="damage_box" class="radio_principle_label" for="brain_damage_light"> L </label>
                <h2>Brain</h2>
                If your insanity is 3+, you are <b>Insane</b>.
            </div>
        </div> <!-- survivor_hit_box -->

                <!-- HEAD -->
        <div id="survivor_hit_box">
            <div id="shield_box">
                <input type="number" class="shield" name="Head" value="$head"/>
            </div>
            <div id="info_box">
             <input type='hidden' value='unchecked' name='toggle_head_damage_heavy'/>
             <input type="checkbox" id="head_damage_heavy" class="radio_principle" name="toggle_head_damage_heavy" $head_damage_heavy_checked /> 
             <label id="damage_box" class="radio_principle_label" for="head_damage_heavy"> H </label>
                <h2>Head</h2>
                <font color="#C60000">H</font>eavy Injury: Knocked Down
            </div>
        </div> <!-- survivor_hit_box -->

                <!-- ARMS -->
        <div id="survivor_hit_box">
            <div id="shield_box">
                <input type="number" class="shield" name="Arms" value="$arms"/>
            </div>
            <div id="info_box">
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
            <div id="shield_box">
                <input type="number" class="shield" name="Body" value="$body"/>
            </div>
            <div id="info_box">
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
            <div id="shield_box">
                <input type="number" class="shield" name="Waist" value="$waist"/>
            </div>
            <div id="info_box">
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
            <div id="shield_box">
                <input type="number" class="shield" name="Legs" value="$legs"/>
            </div>
            <div id="info_box">
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

        <input class="big_number_square" type="number" name="hunt_xp" value="$hunt_xp" />
        <div class="big_number_caption">Hunt XP</div>
        <br />
        <p>
            <img class="icon" src="$MEDIA_URL/icons/trigger_story_event.png" /> <b>Age</b> occurs at 2, 6, 10 and 15. The Survivor retires at 16.
        </p>

        <hr/>

                        <!-- WEAPON PROFICIENCY -->
        <h3>Weapon Proficiency</h3>
        <input class="big_number_square" type="number" name="Weapon Proficiency" value="$weapon_proficiency" />
        <div class="big_number_caption">
            <input type="text" class="full_width" placeholder="Type: Select before hunt" value="$weapon_proficiency_type" name="weapon_proficiency_type" style="width: 50%; clear: none; "/>
        </div>
        <p>       <b>Specialist</b> at 3; <b>Master</b> at 8.   </p>

        <hr/>

                        <!-- COURAGE AND UNDERSTANDING -->

        <div id="block_group">
        <br />
        <input class="big_number_square" type="number" name="Courage" value="$courage" />
        <div class="big_number_caption">Courage</div>
        <br />
        <p>
        <img class="icon" src="$MEDIA_URL/icons/trigger_story_event.png" /> <b>Bold</b> occurs at 3, <img class="icon" src="$MEDIA_URL/icons/trigger_story_event.png" /> <b>See the Truth</b> occurs at 9.

          <input type="radio" id="stalwart_button" class="radio_principle" name="courage_attribute" value="Stalwart" $stalwart_checked />
          <label class="radio_principle_label" for="stalwart_button"> <b>Stalwart:</b> can't be knocked down by brain trauma or intimidate. </label>
          <input type="radio" id="prepared_button" class="radio_principle" name="courage_attribute" value="Prepared" $prepared_checked />
          <label class="radio_principle_label" for="prepared_button"> <b>Prepared:</b> Add hunt XP to your roll when determining a straggler. </label>
          <input type="radio" id="matchmaker_button" class="radio_principle" name="courage_attribute" value="Matchmaker" $matchmaker_checked />
          <label class="radio_principle_label" for="matchmaker_button"> <b>Matchmaker:</b> Spend 1 endeavor to trigger intimacy story event. </label>
        </div>
        <div id="block_group">
        <br />
        <input class="big_number_square" type="number" name="Understanding" value="$understanding" />
        <div class="big_number_caption">Understanding</div>
        <br />
        <p>
        <img class="icon" src="$MEDIA_URL/icons/trigger_story_event.png" /> <b>Insight</b> occurs at 3, <img class="icon" src="$MEDIA_URL/icons/trigger_story_event.png" /> <b>White Secret</b> occurs at 9.
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


    <form method="POST" id="autoForm" action="#edit_fighting_Arts">
        <input type="hidden" name="form_id" value="survivor_edit_fighting_arts" />
        <button class="hidden"></button>
        <input type="hidden" name="modify" value="survivor" />
        <input type="hidden" name="asset_id" value="$survivor_id" />

        <h3>Fighting Arts</h3>
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
         <label class="radio_principle_label" for="skip_next_hunt" id="skip_next_hunt"> Skip Next<br/>Hunt </label>
            $abilities_and_impairments<br/>
            $add_abilities_and_impairments
        <input onchange="this.form.submit()" class="full_width" type="text" name="add_ability" placeholder="add ability or impairment"/>
            $remove_abilities_and_impairments

        </p>
        <hr/>

        <input class="full_width" type="text" name="email" placeholder="email" value="$email"/>
        <hr />

    </form>


    <br/><hr/>


    <form method="POST" onsubmit="return confirm('This cannot be undone! Press OK to permanently delete this survivor forever, which is NOT THE SAME THING as marking it dead: permanently deleting the survivor prevents anyone from viewing and/or editing it ever again!');"><input type="hidden" name="remove_survivor" value="$survivor_id"/><button class="error">Permanently Delete Survivor</button></form>
    <hr/>
    <br />

    \n""")
    new = Template("""\n\
    <h3>Create a New Survivor</h3>
    <form method="POST">
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
    summary = Template("""\n\
        <h1>&#x02261; $settlement_name</h1>
        <p class="subhead_p_block">$principles</p>
        <p>Population: $population ($death_count deaths)</p><hr/>
        <p>Survival Limit: $survival_limit</p><hr/>
        <h3>Survivors</h3>
        $survivors
        <form method="POST">
        <input type="hidden" name="change_view" value="new_survivor"/>
        <button class="success">+ Create New Survivor</button>
        </form>
        <hr/>
        <h3>Innovations and Principles</h3>
        <p>$innovations</p>
        <hr/>
        <h3>Bonuses</h3>
        <h4>Departing</h4>
        $departure_bonuses
        <h4>During Settlement</h4>
        <p>$settlement_bonuses</p>
        <p>$survivor_bonuses</p>
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
    \n""")
    form = Template("""\n\
    $game_link

    <form method="POST" id="autoForm" action="#">
        <button id="save_button" class="success">Save</button>
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />

        <input id="topline_name" onchange="this.form.submit()" class="full_width" type="text" name="name" value="$name" placeholder="Settlement Name"/>
        <hr />
        <input class="big_number_square" type="number" name="survival_limit" value="$survival_limit" min="$min_survival_limit"/>
        <div class="big_number_caption">Survival Limit<br />(min: $min_survival_limit)</div>
        <br /><hr />

            <h3>On Departure</h3>
            $departure_bonuses

        <hr/>

            <h3>During Settlement Phase</h3>
            $settlement_bonuses

        <hr />

        <input class="big_number_square" type="number" name="population" value="$population"/>
        <div class="big_number_caption">Population</div>
        <br /><hr />
        <input class="big_number_square" type="number" name="death_count" value="$death_count"/>
        <div class="big_number_caption">Death Count</div>
        <br />

    </form> <!-- ending the first form -->

    <hr /> <!-- Logical section Break -->


                    <!-- STORAGE - THIS IS ITS OWN FORM-->
    <a id="edit_storage" />
    <form id="autoForm" method="POST" action="#edit_storage">
        <input type="hidden" name="modify" value="settlement" />
        <input type="hidden" name="asset_id" value="$settlement_id" />

        <div id="block_group">
        <h2>Storage</h2>
        <p>Gear and Resources may be stored without limit. Tap items to remove them.</p>
        <hr />
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
        <hr />
     <p>$locations</p>
     $locations_options
     <input onchange="this.form.submit()" type="text" class="full_width" name="add_location" placeholder="add custom location"/>
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
        <hr />
     <p>$innovations</p>
     <select name="add_innovation" onchange="this.form.submit()">
      <option selected disabled hidden value=''>Add Innovation</option>
      <option>$innovation_options</option>
     </select>
     <input onchange="this.form.submit()" type="text" class="full_width" name="add_innovation" placeholder="add custom innovation"/>
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

    <div id="block_group">
    <h2>Timeline</h2>
    <input onchange="this.form.submit()" class="big_number_square" type="number" name="lantern_year" value="$lantern_year"/>
    <div class="big_number_caption">Lantern Year</div>
    <br /><hr />
    $timeline
    </div>
    </form>


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

    <form method="POST">
    <input type="hidden" name="change_view" value="new_survivor"/>
    <button class="success">+ Create New Survivor</button>
    </form>


    <br />
    <br /><hr/>
    <form method="POST" onsubmit="return confirm('This cannot be undone! Press OK to permanently delete this settlement AND ALL SURVIVORS WHO BELONG TO THIS SETTLEMENT forever.');"><input type="hidden" name="remove_settlement" value="$settlement_id"/><button class="error">Permanently Delete Settlement</button></form>
    <hr/>
    <br />
    \n""")

class dashboard:
    home_button = '<hr/><form method="POST"><input type="hidden" name="change_view" value="dashboard"/><button> Return to Dashboard</button></form>\n'
    headline = Template('<h2 class="$h_class">$title</h2><p>$desc</p>\n')
    settlement_flash = '<font size="50px">&#x02261;</font> '
    new_settlement_button = '<form method="POST"><input type="hidden" name="change_view" value="new_settlement" /><button class="success">+ New Settlement</button></form>\n'
    new_settlement_form = """\n\
    <h3>Create a New Settlement</h3>
    <form method="POST">
    <input type="hidden" name="new" value="settlement" />
    <input type="text" name="settlement_name" placeholder="Settlement Name"/ class="full_width">
    <button class="success">SAVE</button>
    </form>
    \n"""
    view_asset_button = Template("""\n\
    <form method="POST">
    <input type="hidden" name="view_$asset_type" value="$asset_id" />
    <button id="$button_id" class="$button_class" $disabled>$asset_name</button>
    </form>
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


class changeLog:
    log_text = file("change_log.txt", "rb").read()
    body = """\n\
<h1>KD:M Manager!</h1><h2 class="no_border">Change Log and Updates</h2>
<p><a href="/">Return to KD:M Manager</a></p>
<hr/><pre>%s</pre><hr/>
<p><a href="/">Return to KD:M Manager</a></p>
    \n""" % log_text


class meta:
    """ This is for HTML that doesn't really fit anywhere else, in terms of
    views, etc. Use this for helpers/containers/administrivia/etc. """
    start_head = '<!DOCTYPE html>\n<html>\n<head>\n<meta charset="UTF-8">\n<title>%s</title>\n' % settings.get("application","title")
    stylesheet = Template('<link rel="stylesheet" type="text/css" href="$url">\n')
    close_head = '</head>\n<body>\n <div id="container">\n'
    false_body = 'Caught exception while rendering the current view!<hr/>The current session will be ended. Please try again.'
    close_body = '\n </div><!-- container -->\n</body>\n</html>'
    saved_dialog = '\n    <div id="saved_dialog" class="success">Saved!</div>'
    log_out_button = Template('\n\t<hr/><form id="logout" method="POST"><input type="hidden" name="remove_session" value="$session_id"/><button class="warn">LOG OUT</button>\n\t</form>')




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
      (function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
      (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
      m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
      })(window,document,'script','//www.google-analytics.com/analytics.js','ga');

      ga('create', 'UA-71038485-1', 'auto');
      ga('send', 'pageview');

    </script>
    """

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
