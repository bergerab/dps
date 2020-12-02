@ECHO OFF

IF %1.==. GOTO MissingURL
IF %2.==. GOTO MissingDataset

ECHO Sending PV and wind data...
dps_client --input=PVAndWind.csv                     ^
           --dbm-url=%1                              ^
	   --dataset=%2                              ^
	   --time-column=Time                        ^
	   --time-offset=3600
ECHO PV and wind data sent.

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