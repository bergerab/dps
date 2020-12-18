@ECHO OFF

IF %1.==. GOTO MissingURL
IF %2.==. GOTO MissingDataset
IF %3.==. GOTO MissingAPIKey

ECHO Sending battery discharge data...
dps_client --input=BatteryCharge.csv       ^
           --dbm-url=%1                    ^
	   --dataset=%2                    ^
	   --api-key=%3                    ^
	   --time-column=ChargeTimestep    ^
	   --time-offset=7200              ^
	   --include-time-column=true
ECHO Battery discharge data sent.	   

ECHO Sending battery charge data...
dps_client --input=BatteryDischarge.csv    ^
           --dbm-url=%1                    ^
	   --dataset=%2                    ^
	   --api-key=%3                    ^
	   --time-column=DischargeTimestep ^
	   --time-offset=3600              ^
	   --include-time-column=true
ECHO Battery charge data sent.

GOTO End

:MissingURL
  ECHO Missing first required parameter "Database Manager URL".
GOTO ErrorEnd
:MissingDataset
  ECHO Missing second required parameter "Dataset".
GOTO ErrorEnd
:MissingAPIKey
  ECHO Missing third required parameter "API Key".
GOTO ErrorEnd

:ErrorEnd

ECHO Example command: ".\upload.bat http://localhost:9002 SampleDatasetName \"APIKey\""
ECHO Make sure to surround the API key with quotation marks.

:End
