@ECHO OFF

IF %1.==. GOTO MissingURL
IF %2.==. GOTO MissingDataset
IF %3.==. GOTO MissingAPIKey

ECHO Sending diesel generator and transformer data...
dps_client --input=DieselGeneratorAndTransformer.csv ^
           --dbm-url=%1                              ^
	   --dataset=%2                              ^
	   --api-key=%3                              ^
	   --time-column=Time                        ^
	   --time-offset=3600
ECHO Diesel generator and transformer data sent.

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
