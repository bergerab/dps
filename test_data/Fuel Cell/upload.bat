@ECHO OFF

IF %1.==. GOTO MissingURL
IF %2.==. GOTO MissingDataset

ECHO Sending fuel cell data...
dps_client --input=FuelCell.csv                      ^
           --dbm-url=%1                              ^
	   --dataset=%2                              ^
	   --time-column=Time                        ^
	   --time-offset=3600
ECHO Fuel cell data sent.

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
