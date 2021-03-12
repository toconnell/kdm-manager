"""

    The webapp help lives here in the form of dictionaries containing the topic
    questions and their answers.

"""

TIPS = {
    # loading screen tips will go here; this is TBD
}

HELP = {
    'Frequently Asked Questions': [
        {
            'question': (
                'Who develops this application? If you are not affiliated with '
                'Kingdom Death, where do the subscription fees go?'
            ),
            'answer': (
                '<p>The Manager is developed and maintained by an independent '
                'production company based in Chicago, IL called '
                '<a href="https://thelaborinvain.com">The Labor in Vain</a>.'
                '</p>'
                '<p>Please review the "About" panel on the dashboard '
                'for more information.</p>'
            ),
        },
        {
            'question': 'What devices does the Manager support?',
            'answer': (
                '<p>The Manager is developed to support the current version of '
                'Chrome on Windows 10. <a href="https://blog.kdm-manager.com" '
                'target="top">Check the development blog</a> for more '
                'information about supported devices.</p>'
            ),
        },
        {
            'question': 'How do I report a bug or a problem with the Manager?',
            'answer': (
                '<p>There are two ways to report issues.</p>'
                '<p>The fastest way is to click or tap on the navigation menu, '
                'select "Report Error", use the form to describe '
                'the issue and click "Submit".</p>'
                '<p>This emails the maintainers of the Manager directly and '
                'includes information about you and your settlements that '
                'makes issues easier to research and/or recreate.</p>'
                '<p>Alternately, if you use GitHub, feel free to open issues '
                'in <a href="https://github.com/toconnell/kdm-manager/issues" '
                'target="top">the Manager\'s public repository</a>.'
            ),
        },
    ],
    'System': [
        {
            'question': (
                'Why are certain items on the navigation bar and the '
                'settlement sheet greyed out and disabled?'
            ),
            'answer': (
                '<p> Certain features of the Manager are available to '
                'subscribers only: this includes the Gear Card Lookup, the '
                "ability to apply settlement 'macros', create multiple new "
                'survivors at once, etc.</p>'
                '<p>Subscriptions of various durations can be purchased at '
                '<a href="https://shop.thelaborinvain.com">'
                'shop.thelaborinvain.com</a>.</p>'
            ),
        },
        {
            'question': 'Why can\'t I create a new settlement?',
            'answer': (
                '<p>Nonsubscriber users of the Manager may only create a '
                'total of <b>'
                '{a apiStat.meta.api.limits.nonsubscriber_settlements a}'
                '</b> settlements.</p>'
                '<p>"Abandoned" settlements count towards this total.</p>'
                '<p>If you '
                'are not a subscriber to the Manager, please '
                '<a href="https://thelaborinvain-2.myshopify.com/" '
                'target="top">consider purchasing a subscription</a>. '
                'Alternately, you may wish to remove one of your existing '
                'settlements.</p>'
                '<p>To do this, make sure that you have enabled the '
                '"Delete" button (check the "System" panel on the dashboard) '
                'and then, from the Settlement Sheet, permanently delete the '
                'settlement.</p>'
            ),
        },
    ],
    'Players': [
        {
            'question': 'How do I add players to a campaign?',
            'answer': (
                '<p>To add players to a settlement/campaign, open the Survivor '
                'Sheet of any survivor, click on "Survivor Administration" '
                'and set the email address of the survivor to the email '
                'address of the player who you want to use it.</p>'
                '<p>Doing this <i>does not</i> send an email or alert to that '
                'person (for security/privacy reasons).</p>'
                '<p>Assuming that the email address belongs to a registered '
                'user of the Manager, making them the "owner" of the survivor '
                'will allow that player to access your settlement (they will '
                'see it on their dashboard) and to manage the survivor and any '
                '"public" survivors in your settlement.</p>'
            ),
        },
    ],
    'Settlements': [
        {
            'question': (
                'What version of <i>Monster</i> does the Manager currently '
                'support?'
            ),
            'answer': (
                '<p>As of Friday, October 10th, 2017, the Manager supports '
                'version 1.5 of <i>Monster</i> as its default/base version. '
                'Lower versions <b>are not supported</b>.</p>'
                '<p>Beginning in 2021, all subsequent versions of '
                '<i>Monster</i> will be supported. An individual '
                'settlement\'s version can be set on the "Admin" tab of '
                'the Settlement Sheet.</p>'
            ),
        },
        {
            'question': 'Can I configure my settlement to use other versions?',
            'answer': (
                '<p>Versions 1.3.1 and 1.4 are not supported by the KD:M API '
                'and there is no plan to add support for those versions.</p>'
                '<p>Versions 1.5 and later, however, are supported.<p>'
                '<p>Subscribers may change their settlement\'s ruleset on '
                'the "Admin" tab of the Settlement Sheet.</p>'
                '<p>(Non-subscriber users\' settlements always use the API\'s'
                'default version, whatever that happens to be.</p>'
            ),
        },
        {
            'question': 'Why does my Timeline include Lantern Year 0?',
            'answer': (
                '<p>All settlement timelines begin with Lantern Year 0. The '
                '<a href="http://tools.kingdomdeath.com/faq/" target="top"> '
                'offical FAQ</a> confirms that the Prologue takes place '
                'during "Lantern Year 0. When the Timeline is updated in the '
                'first Settlement Phase it becomes Lantern Year 1."</p>'
            ),
        },
        {
            'question': (
                'When I return Departing survivors, does the Manager check if '
                'any have the "Tinker" ability?'
            ),
            'answer': (
                '<p>No.</p>'
                '<p>For now, the Manager only evaluates whether survivors are '
                'alive or dead when returned and uses that information to '
                'determine how many Endeavors to add. In the future, this may '
                'change, but for now, this is how it works.</p>'
            ),
        },
        {
            'question': 'My settlement disappeared!',
            'answer': (
                '<p>Settlements created by users who do not subscribe to the '
                'Manager are removed after they reach 180 days of age (the '
                'settlements, not the users).</p>'
                '<p>If you believe that your settlement was removed in error, '
                'please use the "Report an Issue or Error" controls on the '
                'left-side menu to ask for help.</p>'
            ),
        },
    ],
    'Strain System': [
        {
            'question': 'How do I add Strain Fighting Arts?',
            'answer': (
                '<p>When creating a new campaign (or updating an old one), add '
                'one of the <i>Echoes of Death</i> or, if you have any of the '
                '<i>Echoes of Death</i> expansions in your '
                '<b>KD Collection</b>, enable the "Fighting Arts & Disorders" '
                'from your collection.</p>'
                '<p>At that point, the appropriate Strain Fighting Arts will '
                'be available in the Fighting Arts drop-down on Survivor '
                'Sheets for that campaign.</p>'
                '<p>Please note that <i>all Strain Fighting Arts will be '
                'available</i>, even if their Strain Milestone has not been '
                'recorded on the Settlement Sheet.</p>'
            )
        },
        {
            'question': (
                'Will the Manager assign locked Strain Fighting Arts if I '
                'choose a random Fighting Art on the Survivor Sheet?'
            ),
            'answer': (
                '<p>No.</p>'
                '<p>Selecting the "* Random Fighting Art" option from the '
                'drop-down will pick a random Fighting Art from a list that '
                '<i>does not</i> include Strain Fighting Arts that have not '
                'yet been recorded on the Settlement Sheet.</p>'
            ),
        },
        {
            'question': (
                'Does the Manager enforce the five card limit on Strain '
                'Fighting Arts?'
            ),
            'answer': (
                '<p>No.</p>'
                '<p>As mentioned above, your settlement\'s Fighting Arts '
                'drop-down will always let you pick any Strain Fighting Art '
                'from your enabled expansion content.</p>'
            ),
        },
    ],
    'Survivors': [
        {
            'question': (
                'What is the difference between "New" and "Newborn" survivors?'
            ),
            'answer': (
                '<p>The Manager distinguishes between "new" and "newborn" '
                'survivors: survivors created without parents are considered '
                '"new", while survivors created <i>with</i> parents are '
                'considered "newborn."</p>'
                '<p>Bonuses and effects that apply to "newborn" survivors will '
                'be automatically applied to them at "birth" (i.e. creation), '
                'but those bonuses will <i>not</i> be applied at creation time '
                'to survivors who are merely "new".</p>'
            ),
        },
        {
            'question': 'How do I create survivors with parents?',
            'answer': (
                '<p>Advance the Timeline to Lantern Year 1 or later.</p>'
                '<p>Survivors added to the settlement in LY 0 may not have '
                'parents. Such survivors are considered "new" and are not '
                'subject to "newborn" benefits inherent to campaign or '
                'expansion content.</p>'
            ),
        },
        {
            'question': (
                'Why can\'t I add the <i>Lovelorn Rock</i> to my gear grid?'
            ),
            'answer': (
                '<p>The Rock\'s gear card is not part of the core game. '
                'Rather, it is part of the <b>Vignettes of Death: White '
                'Gigalion</b> and, if you want to equip it (or add it to '
                'settlement storage for some reason), you must first add that '
                'expansion content to your settlement.</p>'
            ),
        },
    ],
}
