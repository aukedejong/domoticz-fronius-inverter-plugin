#           Fronius Inverter Plugin
#
#           Author:     ADJ, 2018
#
"""
<plugin key="froniusInverter" name="Fronius Inverter" author="ADJ" version="0.0.1" wikilink="https://github.com/aukedejong/domoticz-fronius-inverter-plugin.git" externallink="http://www.fronius.com">
    <params>
        <param field="Mode1" label="IP Address" required="true" width="200px" />
        <param field="Mode2" label="Device ID" required="true" width="100px" />
        <param field="Mode6" label="Debug" width="100px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
                <option label="Logging" value="File"/>
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import sys
import json
import datetime
import urllib.request
import urllib.error

class BasePlugin:
    inverterWorking = True
    intervalCounter = None
    heartbeat = 30
    previousTotalWh = 0
    previousCurrentWatt = 0
    whFraction = 0

    def onStart(self):
        if Parameters["Mode6"] != "Normal":
            Domoticz.Debugging(1)

        if (len(Devices) == 0):
            Domoticz.Device(Name="Current power",  Unit=1, TypeName="Custom", Options = { "Custom" : "1;Watt"}, Used=1).Create()
            Domoticz.Device(Name="Total power",  Unit=2, TypeName="kWh", Used=1).Create()
            logDebugMessage("Devices created.")

        Domoticz.Heartbeat(self.heartbeat)
        self.intervalCounter = 0

        if ('FroniusInverter' not in Images): Domoticz.Image('Fronius Inverter Icons.zip').Create()
        if ('FroniusInverterOff' not in Images): Domoticz.Image('Fronius Inverter Off Icons.zip').Create()

        Devices[1].Update(0, sValue=str(Devices[1].sValue), Image=Images["FroniusInverter"].ID)
        Devices[2].Update(0, sValue=str(Devices[2].sValue), Image=Images["FroniusInverter"].ID)
        return True


    def onHeartbeat(self):

        if self.intervalCounter == 1:

            ipAddress = Parameters["Mode1"]
            deviceId = Parameters["Mode2"]
            jsonObject = self.getInverterRealtimeData( ipAddress, deviceId )

            if (self.isInverterActive(jsonObject)):

                self.updateDeviceCurrent(jsonObject)
                self.updateDeviceMeter(jsonObject)

                if (self.inverterWorking == False):
                    self.inverterWorking = True

            else:
                self.logErrorCode(jsonObject)

                if (self.inverterWorking == True):
                    self.inverterWorking = False
                    self.updateDeviceOff()


            self.intervalCounter = 0

        else:
            self.intervalCounter = 1
            #logDebugMessage("Do nothing: " + str(self.intervalCounter))


        return True


    def getInverterRealtimeData(self, ipAddress, deviceId):

        url = "http://" + ipAddress + "/solar_api/v1/GetInverterRealtimeData.cgi?Scope=Device&DeviceID=" + deviceId + "&DataCollection=CommonInverterData"
        logDebugMessage('Retrieve solar data from ' + url)

        try:
            req = urllib.request.Request(url)
            jsonData = urllib.request.urlopen(req).read()
            jsonObject = json.loads(jsonData.decode('utf-8'))
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            logErrorMessage("Error: " + str(e) + " URL: " + url)
            return

        #logDebugMessage("JSON: " + str(jsonData))

        return jsonObject



    def isInverterActive(self, jsonObject):

        return jsonObject["Head"]["Status"]["Code"] == 0


    def logErrorCode(self, jsonObject):

        code = jsonObject["Head"]["Status"]["Code"]
        reason = jsonObject["Head"]["Status"]["Reason"]
        if (code != 12):
            logErrorMessage("Code: " + str(code) + ", reason: " + reason)

        return


    def updateDeviceCurrent(self, jsonObject):

        currentWatts = jsonObject["Body"]["Data"]["PAC"]["Value"]

        Devices[1].Update(currentWatts, str(currentWatts), Images["FroniusInverter"].ID)

        return

    def updateDeviceMeter(self, jsonObject):
        totalWh = jsonObject["Body"]["Data"]["TOTAL_ENERGY"]["Value"]
        currentWatts = jsonObject["Body"]["Data"]["PAC"]["Value"]

        if (self.previousTotalWh < totalWh):
            logDebugMessage("New total recieved: prev:" + str(self.previousTotalWh) + " - new:" + str(totalWh) + " - last faction: " + str(self.whFraction))
            self.whFraction = 0
            self.previousTotalWh = totalWh

        else:
            averageWatts =  (self.previousCurrentWatt + currentWatts) / 2
            self.whFraction = self.whFraction + int(round(averageWatts / 60))
            logDebugMessage("Fraction calculated: " + str(currentWatts) + " - " + str(self.whFraction))


        self.previousCurrentWatt = currentWatts
        calculatedWh = totalWh + self.whFraction
        Devices[2].Update(0, str(currentWatts) + ";" + str(calculatedWh))

        return


    def updateDeviceOff(self):

        Devices[1].Update(0, "0", Images["FroniusInverterOff"].ID)
        calculatedWh = self.previousTotalWh + self.whFraction
        Devices[2].Update(0, "0;" + str(calculatedWh))


    def onStop(self):
        logDebugMessage("onStop called")
        return True

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

def logDebugMessage(message):
    if (Parameters["Mode6"] == "Debug"):
        now = datetime.datetime.now()
        f = open(Parameters["HomeFolder"] + "fronius-inverter-plugin.log", "a")
        f.write("DEBUG - " + now.isoformat() + " - " + message + "\r\n")
        f.close()
    Domoticz.Debug(message)

def logErrorMessage(message):
    if (Parameters["Mode6"] == "Debug"):
        now = datetime.datetime.now()
        f = open(Parameters["HomeFolder"] + "fronius-inverter-plugin.log", "a")
        f.write("ERROR - " + now.isoformat() + " - " + message + "\r\n")
        f.close()
    Domoticz.Error(message)
