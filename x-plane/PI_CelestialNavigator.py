import socket
from celestialnavigator import NetworkInterfacePacket, EasyDref, EasyCommand, UTC
from datetime import datetime
from XPLMDefs import *
from XPLMProcessing import *
from XPLMDataAccess import *
from XPLMUtilities import *
from XPLMPlanes import *
from XPLMPlugin import *
from XPLMMenus import *
from XPWidgetDefs import *
from XPWidgets import *
from XPStandardWidgets import *
from XPLMScenery import *
from XPLMDisplay import *
from SandyBarbourUtilities import *
from PythonScriptMessaging import *

__VERSION__='alpha1'

class PythonInterface:
    def XPluginStart(self):
        self.Name = "CelestialNavigator"
        self.Sig = "LukeFrisken.Python.CelestialNavigator"
        self.Desc = "A celestial navigator"

        # Sim pause
        self.paused = EasyDref('sim/time/paused', 'int')

        self.stellariumConnectorWindow, self.aboutWindow = [False] * 2

        self.Mmenu = self.mainMenuCB

        self.mPluginItem = XPLMAppendMenuItem(XPLMFindPluginsMenu(), 'Celestial Navigator', 0, 1)
        self.mMain       = XPLMCreateMenu(self, 'Celestial Navigator', XPLMFindPluginsMenu(), self.mPluginItem, self.Mmenu, 0)

        self.mStellariumConnectorIndex = 1
        self.mStellariumConnector = XPLMAppendMenuItem(self.mMain, 'Stellarium Connector...', self.mStellariumConnectorIndex, 1)
        self.mAboutIndex = 2
        self.mAbout     =  XPLMAppendMenuItem(self.mMain, 'About', self.mAboutIndex, 1)

        # Register commands
        self.cmd = []


        # Aircraft Data Access
        self.aircraft = Aircraft()

        # Time Data Access
        self.time = Time()




        return self.Name, self.Sig, self.Desc

    def XPluginStop(self):
        self.reset()

        XPLMDestroyMenu(self, self.mMain)

    def XPluginEnable(self):
        return 1

    def XPluginDisable(self):
        pass

    def XPluginReceiveMesage(self, inFromWho, inMessage, inParam):
        pass

    def reset(self):
        if self.aboutWindow:
            XPDestroyWidget(self, self.aboutWindowWidget, 1)
            self.aboutWindow = False
        if self.stellariumConnectorWindow:
            XPDestroyWidget(self, self.stellariumConnectorWindowWidget, 1)
            self.stellariumConnectorWindow = False

    def mainMenuCB(self, menuRef, menuItem):
        if menuItem == self.mStellariumConnectorIndex:
            if (not self.stellariumConnectorWindow):
                self.CreateStellariumConnectorWindow(221, 640, 300, 165)
                self.stellariumConnectorWindow = True
            elif (not XPIsWidgetVisible(self.stellariumConnectorWindowWidget)):
                XPShowWidget(self.stellariumConnectorWindowWidget)
        elif menuItem == self.mAboutIndex:
            if (not self.aboutWindow):
                self.CreateAboutWindow(221, 640, 200, 165)
                self.aboutWindow = True
            elif (not XPIsWidgetVisible(self.aboutWindowWidget)):
                XPShowWidget(self.aboutWindowWidget)

    def CreateAboutWindow(self, x, y, w, h):
        x2 = x + w
        y2 = y - 40 - 20 * 8
        Buffer = "About Celestial Navigator"

        # Create the About Widget Main Window
        self.aboutWindowWidget = XPCreateWidget(x, y, x2, y2, 1, Buffer, 1,0 , xpWidgetClass_MainWindow)
        window = self.aboutWindowWidget

        # Create the Sub window
        subw = XPCreateWidget(x+10, y-30, x2-20 + 10, y2+40 -25, 1, "" ,  0,window, xpWidgetClass_SubWindow)
        # Set the style to sub window
        XPSetWidgetProperty(subw, xpProperty_SubWindowType, xpSubWindowStyle_SubWindow)
        x += 20
        y -= 30

        # Add Close Box decorations to the Main Widget
        XPSetWidgetProperty(window, xpProperty_MainWindowHasCloseBoxes, 1)

        from sys import version_info

        # Get Open Scenery X Version
        osxlib = open('%s/Custom Scenery/OpenSceneryX/library.txt' % XPLMGetSystemPath())
        if osxlib:
            for line in iter(osxlib):
                if 'Version' in line:
                    osxversion = line[line.find('v'):]
                    break
            if not osxversion:
                osxversion = 'Not found'
        else:
            osxversion = 'Not found'
        XPlaneVersion, XPLMVersion, HostID = XPLMGetVersions()

        sysinfo = [
        'Celestial Navigator: %s' % __VERSION__,
        '(c) Luke Frisken 2016',
        ]
        for label in sysinfo:
            y -= 15
            XPCreateWidget(x, y, x+40, y-20, 1, label, 0, window, xpWidgetClass_Caption)

        # Visit site
        self.aboutVisit = XPCreateWidget(x+20, y-20, x+120, y-60, 1, "Visit site", 0, window, xpWidgetClass_Button)
        XPSetWidgetProperty(self.aboutVisit, xpProperty_ButtonType, xpPushButton)

        y -= 40
        sysinfo = [
        'System information:',
        'X-plane: %.2f' % (int(XPlaneVersion)/1000.0),
        'Python: %i.%i.%i' % (version_info[0], version_info[1], version_info[2]),
        'OpenSceneryX: %s' % osxversion
        ]

        for label in sysinfo:
            y -= 15
            XPCreateWidget(x, y, x+40, y-20, 1, label, 0, window, xpWidgetClass_Caption)

        # Register our widget handler
        self.aboutWindowHandlerCB = self.aboutWindowHandler
        XPAddWidgetCallback(self, window, self.aboutWindowHandlerCB)

    def aboutWindowHandler(self, inMessage, inWidget, inParam1, inParam2):
        if (inMessage == xpMessage_CloseButtonPushed):
            if (self.aboutWindow):
                XPHideWidget(self.aboutWindowWidget)
            return 1

        # Handle any button pushes
        if (inMessage == xpMsg_PushButtonPressed):

            if (inParam1 == self.aboutVisit):
                from webbrowser import open_new
                open_new('http://forums.x-plane.org/index.php?app=downloads&showfile=14790');
                return 1
        return 0

    def CreateStellariumConnectorWindow(self, x, y, w, h):
        x2 = x + w
        y2 = y - 40 - 20 * 8

        Buffer = "Stellarium Connector"

        # Create the About Widget Main Window
        self.stellariumConnectorWindowWidget = XPCreateWidget(x, y, x2, y2, 1, Buffer, 1,0 , xpWidgetClass_MainWindow)
        window = self.stellariumConnectorWindowWidget

        # Create the Sub window
        subw = XPCreateWidget(x+10, y-30, x2-20 + 10, y2+40 -25, 1, "" ,  0,window, xpWidgetClass_SubWindow)
        # Set the style to sub window
        XPSetWidgetProperty(subw, xpProperty_SubWindowType, xpSubWindowStyle_SubWindow)

        # Add Close Box decorations to the Main Widget
        XPSetWidgetProperty(window, xpProperty_MainWindowHasCloseBoxes, 1)

        x += 20
        # ip address
        XPCreateWidget(x, y-40, x+40, y-60, 1, 'IP Address', 0, window, xpWidgetClass_Caption)
        self.stellariumIPInput = XPCreateWidget(x+80, y-40, x+250, y-62, 1, '127.0.0.1', 0, window, xpWidgetClass_TextField)
        XPSetWidgetProperty(self.stellariumIPInput, xpProperty_TextFieldType, xpTextEntryField)
        XPSetWidgetProperty(self.stellariumIPInput, xpProperty_Enabled, 1)

        y -= 30
        # port
        XPCreateWidget(x, y-40, x+40, y-60, 1, 'Port', 0, window, xpWidgetClass_Caption)
        self.stellariumPortInput = XPCreateWidget(x+80, y-40, x+140, y-62, 1, '7755', 0, window, xpWidgetClass_TextField)
        XPSetWidgetProperty(self.stellariumPortInput, xpProperty_TextFieldType, xpTextEntryField)
        XPSetWidgetProperty(self.stellariumPortInput, xpProperty_Enabled, 1)

        y -= 30
        # year
        XPCreateWidget(x, y-40, x+40, y-60, 1, 'Year', 0, window, xpWidgetClass_Caption)
        yearString = str(datetime.now().year)
        self.stellariumYearInput = XPCreateWidget(x+80, y-40, x+140, y-62, 1, yearString, 0, window, xpWidgetClass_TextField)
        XPSetWidgetProperty(self.stellariumYearInput, xpProperty_TextFieldType, xpTextEntryField)
        XPSetWidgetProperty(self.stellariumYearInput, xpProperty_Enabled, 1)

        y -= 25
        # Connect Button
        width = 100
        self.connectStellariumButton = XPCreateWidget(x+80, y-60, x+80+width, y-80, 1, "CONNECT", 0, window, xpWidgetClass_Button)
        XPSetWidgetProperty(self.connectStellariumButton, xpProperty_ButtonType, xpPushButton)

        # Stop Button 
        self.stopStellariumButton = XPCreateWidget(x+80, y-60, x+80+width, y-80, 1, "STOP", 0, window, xpWidgetClass_Button)
        XPSetWidgetProperty(self.stopStellariumButton, xpProperty_ButtonType, xpPushButton)
        XPHideWidget(self.stopStellariumButton)
        


        # Register our widget handler
        self.stellariumConnectorWindowCB = self.stellariumConnectorWindowHandler
        XPAddWidgetCallback(self, window, self.stellariumConnectorWindowCB)

    def stellariumConnectorWindowHandler(self, inMessage, inWidget, inParam1, inParam2):
        if (inMessage == xpMessage_CloseButtonPushed):
            if (self.stellariumConnectorWindow):
                XPHideWidget(self.stellariumConnectorWindowWidget)
            return 1

        # Handle any button pushes
        if (inMessage == xpMsg_PushButtonPressed):
            if (inParam1 == self.connectStellariumButton):
                self.stellariumConnectorSend()

        return 0

    def float(self, string):
        # try to convert to float or return 0
        try: 
            val = float(string)
        except ValueError:
            val = 0.0
        return val

    def int(self, string):
        # try to convert to integer or return 0
        try: 
            val = int(string)
        except ValueError:
            val = 0
        return val

    def stellariumConnectorSend(self):

        buff = []
        XPGetWidgetDescriptor(self.stellariumIPInput, buff, 256)
        self.stellariumIP = buff[0]
        
        buff = []
        XPGetWidgetDescriptor(self.stellariumPortInput, buff, 256)
        self.stellariumPort = self.int(buff[0])

        buff = []
        XPGetWidgetDescriptor(self.stellariumYearInput, buff, 256)
        self.stellariumYear = self.int(buff[0])

        print("IP", self.stellariumIP)
        print("Port", self.stellariumPort)
        print("Year", self.stellariumYear)

        print("sending the packet to stellarium")
        packet = NetworkInterfacePacket.NetworkInterfacePacket()
        packet.vehicleName = "AircraftPosition"

        year = self.stellariumYear
        month = self.time.current_month.value
        day = self.time.current_day.value
        hour = self.time.zulu_time_hours.value
        minute = self.time.zulu_time_minutes.value
        second = self.time.zulu_time_seconds.value

        print("month", month)
        print("day", day)
        print("hour", hour)
        print("second", second)

        altitude = self.aircraft.elevation.value
        latitude = self.aircraft.latitude.value
        longitude = self.aircraft.longitude.value
        
        print("altitude", altitude)
        print("latitude", latitude)
        print("longitude", longitude)

        time = datetime(year, month, day, hour, minute, second)
        time = time.replace(tzinfo=UTC())
        packet.time = time.isoformat()
        packet.weather = NetworkInterfacePacket.CLEAR

        location = packet.location
        location.latitude = latitude
        location.longitude = longitude
        location.altitude = altitude

        packet_data = packet.SerializeToString()
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        s.connect((self.stellariumIP, self.stellariumPort))
        s.send(packet_data)
        s.close()



class Time:
    def __init__(self):
        self.current_day = EasyDref('sim/cockpit2/clock_timer/current_day', 'int')
        self.current_month = EasyDref('sim/cockpit2/clock_timer/current_month', 'int')
        self.zulu_time_hours = EasyDref('sim/cockpit2/clock_timer/zulu_time_hours', 'int')
        self.zulu_time_minutes = EasyDref('sim/cockpit2/clock_timer/zulu_time_minutes', 'int')
        self.zulu_time_seconds = EasyDref('sim/cockpit2/clock_timer/zulu_time_seconds', 'int')

    def refresh(self):
        # refresh values on acf change
        pass


class Aircraft:
    def __init__(self):
        self.elevation = EasyDref('sim/flightmodel/position/elevation' , 'double')
        self.latitude = EasyDref('sim/flightmodel/position/latitude', 'double')
        self.longitude = EasyDref('sim/flightmodel/position/longitude', 'double')

    def refresh(self):
        # refresh values on acf change
        pass
