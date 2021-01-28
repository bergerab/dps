@ECHO OFF

IF %1.==. GOTO MissingURL
IF %2.==. GOTO MissingDataset
IF %3.==. GOTO MissingAPIKey
IF %4.==. GOTO MissingStartTime

ECHO Sending PV and wind data...
dps_client --input=PVAndWind.csv                     ^
           --dbm-url=%1                              ^
	   --dataset=%2                              ^
	   --api-key=%3                              ^
	   --time-column=Time                        ^
           --start-time=%4                           ^
	   --time-offset=3600
ECHO PV and wind data sent.

GOTO End

:MissingStartTime
  ECHO Sending PV and wind data...
dps_client --input=PVAndWind.csv                     ^
           --dbm-url=%1                              ^
	   --dataset=%2                              ^
	   --api-key=%3                              ^
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
:MissingAPIKey
  ECHO Missing third required parameter "API Key".
GOTO ErrorEnd

:ErrorEnd

ECHO Example command: ".\upload.bat http://localhost:9002 SampleDatasetName \"APIKey\""
ECHO Make sure to surround the API key with quotation marks.

:End
