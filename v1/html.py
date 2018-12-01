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


class meta:
    """ This is a class whose 'methods' are all attributes, and each attribute
    is a stub or fragment of HTML used to render the head/container/etc.
    elements that frame the main template used in each view.

    Ultimately, this is a class whose days are numbered, but for now, we need
    it to render the head/foot of each view.
    """


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

    start_head = Template("""<!DOCTYPE html>\n<html ng-app="kdmManager" ng-controller="rootController">
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
        <link ng-if="user.user === undefined || user.user.preferences.night_mode === true" rel="stylesheet" type="text/css" href="/media/night_mode.css?v=$version">
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

    <!-- private app -->
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
    output += '\n<body class="%s">\n' % body_class

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

