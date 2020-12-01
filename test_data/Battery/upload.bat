@ECHO OFF

IF %1.==. GOTO MissingURL
IF %2.==. GOTO MissingDataset

ECHO Sending battery discharge data...
dps_client --input=BatteryDischarge.csv    ^
           --dbm-url=%1                    ^
	   --dataset=%2                    ^
	   --time-column=DischargeTimestep ^
	   --time-offset=3600              ^
	   --include-time-column=true
ECHO Battery discharge data sent.	   

ECHO Sending battery charge data...
dps_client --input=BatteryCharge.csv       ^
           --dbm-url=%1                    ^
	   --dataset=%2                    ^
	   --time-column=ChargeTimestep    ^
	   --time-offset=1800              ^
	   --include-time-column=true
ECHO Battery charge data sent.

GOTO End

:MissingURL
  ECHO Missing first required parameter "Database Manager URL".
GOTO ErrorEnd
:MissingDataset
  ECHO Missing second required parameter "Dataset".
GOTO ErrorEnd

:ErrorEnd

ECHO Example command: ".\upload.bat http://localhost:9002 SampleDatasetName"

:End
