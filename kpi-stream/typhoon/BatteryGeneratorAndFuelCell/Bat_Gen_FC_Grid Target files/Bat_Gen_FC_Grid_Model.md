Model Bat_Gen_FC_Grid

REM *****************************************:
REM * Common entries:
REM *****************************************:

REM Setting the simulation time step...
rtds_write 0x00000000 0x00000140

REM Module block enable
rtds_write 0x00000003 0x01010003
rtds_file_write 0x00820000 wound_sync_machine_voltage_imem.txt
rtds_file_write 0x00810010 wound_sync_machine_voltage_gprst.txt
rtds_write 0x00810000 0x00000004
rtds_write 0x00810001 0x00000006
rtds_write 0x00810002 0x00000008
rtds_write 0x00810400 0x40400000
rtds_write 0x00810401 0x00000000
rtds_write 0x00810402 0x3F7FFDF2
rtds_write 0x00810403 0x82484000
rtds_write 0x00810404 0x365C5EF5
rtds_write 0x00810405 0xCB49C000
rtds_write 0x00810406 0x37D0D980
rtds_write 0x00810407 0x07D5C000
rtds_write 0x00810408 0x3F7FFD73
rtds_write 0x00810409 0x70E78000
rtds_write 0x0081040A 0x380E5402
rtds_write 0x0081040B 0x4DF1C000
rtds_write 0x0081040C 0x38542A67
rtds_write 0x0081040D 0x32044000
rtds_write 0x0081040E 0x3F7FFBCA
rtds_write 0x0081040F 0x9507C000
rtds_write 0x00810410 0x374B20AD
rtds_write 0x00810411 0x846E0000
rtds_write 0x00810412 0x389D782E
rtds_write 0x00810413 0x1FC48000
rtds_write 0x00810414 0x3F7FFAD3
rtds_write 0x00810415 0x6EBC0000
rtds_write 0x00810416 0x351962E2
rtds_write 0x00810417 0x25D7C000
rtds_write 0x00810418 0x329AF412
rtds_write 0x00810419 0x15B90000
rtds_write 0x0081041A 0x3F7FFFF5
rtds_write 0x0081041B 0xD23B8000
rtds_write 0x0081041C 0xB6063733
rtds_write 0x0081041D 0x44934000
rtds_write 0x0081041E 0x36063733
rtds_write 0x0081041F 0x44934000
rtds_write 0x00810420 0x2DDAFEA3
rtds_write 0x00810421 0xE7A4C000
rtds_write 0x00810422 0xB6063711
rtds_write 0x00810423 0xF531C000
rtds_write 0x00810424 0x36063711
rtds_write 0x00810425 0xF531C000
rtds_write 0x00810426 0xAE5E78C7
rtds_write 0x00810427 0x90BCC000
rtds_write 0x00810428 0x2E5E78C7
rtds_write 0x00810429 0x90BCC000
rtds_write 0x0081042A 0x2D54FEA9
rtds_write 0x0081042B 0xA8780000
rtds_write 0x0081042C 0xAEA51E62
rtds_write 0x0081042D 0x77860000
rtds_write 0x0081042E 0x2EA51E62
rtds_write 0x0081042F 0x77860000
rtds_write 0x00810430 0xAB20D64F
rtds_write 0x00810431 0xBF9C0000
rtds_write 0x00810432 0x2B20D64F
rtds_write 0x00810433 0xBF9C0000
rtds_write 0x00810434 0x360637BA
rtds_write 0x00810435 0x5A994000
rtds_write 0x00810436 0x44D04289
rtds_write 0x00810437 0x5F0BC000
rtds_write 0x00810438 0xC32EAD79
rtds_write 0x00810439 0x6BC44000
rtds_write 0x0081043A 0xC4A58A32
rtds_write 0x0081043B 0xA1E88000
rtds_write 0x0081043C 0x45015051
rtds_write 0x0081043D 0xEF6F0000
rtds_write 0x0081043E 0xC4E1A2DA
rtds_write 0x0081043F 0xDFB44000
rtds_write 0x00810440 0x435DC22B
rtds_write 0x00810441 0x37F60000
rtds_write 0x00810442 0xC22739AF
rtds_write 0x00810443 0x54CD4000
rtds_write 0x00810444 0x44ED3E6E
rtds_write 0x00810445 0xD672C000
rtds_write 0x00810446 0x44AFC3A3
rtds_write 0x00810447 0x43F64000
rtds_write 0x00800001 2e-06
rtds_write 0x00800011 1.2689550155446987e-06
rtds_write 0x00800012 0.5
rtds_write 0x00800005 0x00000000
rtds_write 0x00800020 0x00000000
rtds_write 0x0080001E 0.0
rtds_write 0x0080001F 1.0
rtds_write 0x00800013 0.006135923151542565
rtds_write 0x00800014 1024.0
rtds_write 0x00800015 0x00000400
rtds_write 0x00800016 0.0009765625
rtds_write 0x00800021 0x00000010
rtds_write 0x00800023 0x00000000
rtds_write 0x00800022 0x00000001
rtds_write 0x0080002B 1.0
rtds_write 0x0080002C 0.06283185307179585
rtds_write 0x0080002D 0x00000000
rtds_write 0x0080002E 0x00000000
rtds_write 0x00800026 0.0
rtds_write 0x00800027 1.0
rtds_file_write 0x00860000 wound_sync_machine_voltage_imem.txt
rtds_file_write 0x00850010 wound_sync_machine_voltage_gprst.txt
rtds_write 0x00850000 0x00000217
rtds_write 0x00850001 0x00000219
rtds_write 0x00850002 0x0000021B
rtds_write 0x00850400 0x40400000
rtds_write 0x00850401 0x00000000
rtds_write 0x00850402 0x3F7FFDE7
rtds_write 0x00850403 0x503CC000
rtds_write 0x00850404 0x3661BEED
rtds_write 0x00850405 0x73964000
rtds_write 0x00850406 0x37D57664
rtds_write 0x00850407 0x582EC000
rtds_write 0x00850408 0x3F7FFD67
rtds_write 0x00850409 0x33C8C000
rtds_write 0x0085040A 0x3810EB7A
rtds_write 0x0085040B 0x55E8C000
rtds_write 0x0085040C 0x3858E9EA
rtds_write 0x0085040D 0x152CC000
rtds_write 0x0085040E 0x3F7FFBBD
rtds_write 0x0085040F 0xDCAC0000
rtds_write 0x00850410 0x3745C786
rtds_write 0x00850411 0x825E0000
rtds_write 0x00850412 0x389FFDEB
rtds_write 0x00850413 0xC3208000
rtds_write 0x00850414 0x3F7FFAC1
rtds_write 0x00850415 0x9FE7C000
rtds_write 0x00850416 0x36A048E7
rtds_write 0x00850417 0x77E04000
rtds_write 0x00850418 0x341A8E35
rtds_write 0x00850419 0x657FC000
rtds_write 0x0085041A 0x3F7FFFAB
rtds_write 0x0085041B 0x292F8000
rtds_write 0x0085041C 0xB6063730
rtds_write 0x0085041D 0x55424000
rtds_write 0x0085041E 0x36063730
rtds_write 0x0085041F 0x55424000
rtds_write 0x00850420 0x2DDFD4E5
rtds_write 0x00850421 0x25BA4000
rtds_write 0x00850422 0xB606370E
rtds_write 0x00850423 0xBFDD8000
rtds_write 0x00850424 0x3606370E
rtds_write 0x00850425 0xBFDD8000
rtds_write 0x00850426 0xAE637355
rtds_write 0x00850427 0xE3C60000
rtds_write 0x00850428 0x2E637355
rtds_write 0x00850429 0xE3C60000
rtds_write 0x0085042A 0x2D4F6300
rtds_write 0x0085042B 0x9DABC000
rtds_write 0x0085042C 0xAEA7C37E
rtds_write 0x0085042D 0x2F9D4000
rtds_write 0x0085042E 0x2EA7C37E
rtds_write 0x0085042F 0x2F9D4000
rtds_write 0x00850430 0xACA8121E
rtds_write 0x00850431 0x57B88000
rtds_write 0x00850432 0x2CA8121E
rtds_write 0x00850433 0x57B88000
rtds_write 0x00850434 0x360637A6
rtds_write 0x00850435 0xC83A8000
rtds_write 0x00850436 0x42816B9C
rtds_write 0x00850437 0x399E0000
rtds_write 0x00850438 0xC0D9C1F4
rtds_write 0x00850439 0xDB544000
rtds_write 0x0085043A 0xC24DE719
rtds_write 0x0085043B 0xCAE54000
rtds_write 0x0085043C 0x42A051B5
rtds_write 0x0085043D 0x61B00000
rtds_write 0x0085043E 0xC28BCB1C
rtds_write 0x0085043F 0xE82E8000
rtds_write 0x00850440 0x4108CBA4
rtds_write 0x00850441 0x5A5BC000
rtds_write 0x00850442 0xBFC68904
rtds_write 0x00850443 0x23938000
rtds_write 0x00850444 0x42929CD3
rtds_write 0x00850445 0x63E5C000
rtds_write 0x00850446 0x4259F80D
rtds_write 0x00850447 0xEE23C000
rtds_write 0x00840001 2e-06
rtds_write 0x00840011 8.324877189297489e-08
rtds_write 0x00840012 0.5
rtds_write 0x00840005 0x00000000
rtds_write 0x00840020 0x00000000
rtds_write 0x0084001E 0.0
rtds_write 0x0084001F 1.0
rtds_write 0x00840013 0.006135923151542565
rtds_write 0x00840014 1024.0
rtds_write 0x00840015 0x00000400
rtds_write 0x00840016 0.0009765625
rtds_write 0x00840021 0x00000010
rtds_write 0x00840023 0x00000000
rtds_write 0x00840022 0x00000001
rtds_write 0x0084002B 1.0
rtds_write 0x0084002C 0.06283185307179585
rtds_write 0x0084002D 0x00000000
rtds_write 0x0084002E 0x00000000
rtds_write 0x00840026 0.0
rtds_write 0x00840027 1.0

REM LUT solver inputs...
rtds_write 0x01000000 0x00000001
rtds_write 0x01000200 0x00000403
rtds_write 0x01000300 4175365.344467641
rtds_write 0x01000400 4.79e-06
rtds_write 0x01000600 498.0
rtds_file_write 0x01200000 Lithium-Ion_350.0V_1500.0Ah.ibt
rtds_write 0x01000100 0x00000001

REM HSSL configuration files...
rtds_file_write 0x01C80000 hssl_tx_config.txt
rtds_file_write 0x01D00000 hssl_rx_config.txt

REM Parallel DTV configuration...
rtds_write 0x02400000 0x00000000
rtds_write 0x02400020 0x00000000
rtds_write 0x02400040 0x00000000


REM *****************************************:
REM * SPC0 entries:
REM *****************************************:

REM SPC0 Topology Selector (TS) initialization...
rtds_file_write 0x08180000 SPC0_red_table.txt

rtds_write 0x08100020 0x00000001
rtds_write 0x08100021 0x00000000
rtds_write 0x08100023 0x00000000
rtds_write 0x08100024 0x00000000
rtds_write 0x08100025 0x00000000
rtds_write 0x08100026 0x00000000
rtds_write 0x08100027 0x00000000
rtds_write 0x08100030 0x00000000
rtds_write 0x08100031 0x00000000
rtds_write 0x08100032 0x00000000
rtds_write 0x08100033 0x00000000
rtds_write 0x08100034 0x00000000
rtds_write 0x08100035 0x00000000
rtds_write 0x08100036 0x00000000
rtds_write 0x08100037 0x00000000
rtds_write 0x08100038 0x00000000
rtds_write 0x08100039 0x00000000
rtds_write 0x0810003A 0x00000000
rtds_write 0x0810003B 0x00000000
rtds_file_write 0x08140000 trivial_imem.txt
rtds_file_write 0x08142000 trivial_lut.txt
rtds_write 0x08100040 0x00000001
rtds_write 0x08100041 0x00000000
rtds_write 0x08100043 0x00000000
rtds_write 0x08100044 0x00000000
rtds_write 0x08100045 0x00000000
rtds_write 0x08100046 0x00000000
rtds_write 0x08100047 0x00000000
rtds_write 0x08100050 0x00000000
rtds_write 0x08100051 0x00000000
rtds_write 0x08100052 0x00000000
rtds_write 0x08100053 0x00000000
rtds_write 0x08100054 0x00000000
rtds_write 0x08100055 0x00000000
rtds_write 0x08100056 0x00000000
rtds_write 0x08100057 0x00000000
rtds_write 0x08100058 0x00000000
rtds_write 0x08100059 0x00000000
rtds_write 0x0810005A 0x00000000
rtds_write 0x0810005B 0x00000000
rtds_file_write 0x08148000 trivial_imem.txt
rtds_file_write 0x0814A000 trivial_lut.txt
rtds_write 0x08100060 0x00000001
rtds_write 0x08100061 0x00000000
rtds_write 0x08100063 0x00000000
rtds_write 0x08100064 0x00000000
rtds_write 0x08100065 0x00000000
rtds_write 0x08100066 0x00000000
rtds_write 0x08100067 0x00000000
rtds_write 0x08100070 0x00000000
rtds_write 0x08100071 0x00000000
rtds_write 0x08100072 0x00000000
rtds_write 0x08100073 0x00000000
rtds_write 0x08100074 0x00000000
rtds_write 0x08100075 0x00000000
rtds_write 0x08100076 0x00000000
rtds_write 0x08100077 0x00000000
rtds_write 0x08100078 0x00000000
rtds_write 0x08100079 0x00000000
rtds_write 0x0810007A 0x00000000
rtds_write 0x0810007B 0x00000000
rtds_file_write 0x08150000 trivial_imem.txt
rtds_file_write 0x08152000 trivial_lut.txt

REM SPC0 Variable Delay initialization...
rtds_write 0x08100001 0x0

REM SPC0 Output voltage compare mode...
rtds_write 0x08100005 0x00000000

REM SPC0 Matrix multiplier initialization...
rtds_file_write 0x08000000 SPC0_Com_Word.txt
rtds_file_write 0x08020000 SPC0_Com_LUT.txt
rtds_file_write 0x08080000 SPC0_MAC0.txt
rtds_file_write 0x08082000 SPC0_MAC1.txt
rtds_file_write 0x08084000 SPC0_MAC2.txt
rtds_file_write 0x08086000 SPC0_MAC3.txt

rtds_write 0x08100004 0x00000001
REM SPC0 Contactors initialization...
rtds_write 0x08240000 0x00000000
rtds_write 0x08240080 0x00000000
rtds_write 0x08240100 0x00000000
rtds_write 0x08240180 0x00000000
rtds_write 0x08240200 0x00000000
rtds_write 0x08240280 0x00000000
rtds_write 0x08240300 0x00000000
rtds_write 0x08240380 0x00000000
rtds_write 0x08240400 0x00000001

REM SPC0 GDS compensation settings...
rtds_write 0x080C0000 0x00000001
rtds_write 0x080C0001 0x00000003
rtds_write 0x080C0004 0x3B4CCCCC
rtds_write 0x080C0005 0xCCCD0000
rtds_write 0x08100000 0x00000140

REM SPC0 FSM digital input pin assignments...

REM SPC0 Comparators initialization...

REM SPC0 DTSM initialization...

REM *****************************************:
REM * SPC1 entries:
REM *****************************************:

REM SPC1 Topology Selector (TS) initialization...
rtds_file_write 0x08580000 SPC1_red_table.txt

rtds_write 0x08500020 0x00000001
rtds_write 0x08500021 0x00000000
rtds_write 0x08500023 0x00000000
rtds_write 0x08500024 0x00000000
rtds_write 0x08500025 0x00000000
rtds_write 0x08500026 0x00000000
rtds_write 0x08500027 0x00000000
rtds_write 0x08500030 0x00000000
rtds_write 0x08500031 0x00000000
rtds_write 0x08500032 0x00000000
rtds_write 0x08500033 0x00000000
rtds_write 0x08500034 0x00000000
rtds_write 0x08500035 0x00000000
rtds_write 0x08500036 0x00000000
rtds_write 0x08500037 0x00000000
rtds_write 0x08500038 0x00000000
rtds_write 0x08500039 0x00000000
rtds_write 0x0850003A 0x00000000
rtds_write 0x0850003B 0x00000000
rtds_file_write 0x08540000 trivial_imem.txt
rtds_file_write 0x08542000 trivial_lut.txt
rtds_write 0x08500040 0x00000001
rtds_write 0x08500041 0x00000000
rtds_write 0x08500043 0x00000000
rtds_write 0x08500044 0x00000000
rtds_write 0x08500045 0x00000000
rtds_write 0x08500046 0x00000000
rtds_write 0x08500047 0x00000000
rtds_write 0x08500050 0x00000000
rtds_write 0x08500051 0x00000000
rtds_write 0x08500052 0x00000000
rtds_write 0x08500053 0x00000000
rtds_write 0x08500054 0x00000000
rtds_write 0x08500055 0x00000000
rtds_write 0x08500056 0x00000000
rtds_write 0x08500057 0x00000000
rtds_write 0x08500058 0x00000000
rtds_write 0x08500059 0x00000000
rtds_write 0x0850005A 0x00000000
rtds_write 0x0850005B 0x00000000
rtds_file_write 0x08548000 trivial_imem.txt
rtds_file_write 0x0854A000 trivial_lut.txt
rtds_write 0x08500060 0x00000001
rtds_write 0x08500061 0x00000000
rtds_write 0x08500063 0x00000000
rtds_write 0x08500064 0x00000000
rtds_write 0x08500065 0x00000000
rtds_write 0x08500066 0x00000000
rtds_write 0x08500067 0x00000000
rtds_write 0x08500070 0x00000000
rtds_write 0x08500071 0x00000000
rtds_write 0x08500072 0x00000000
rtds_write 0x08500073 0x00000000
rtds_write 0x08500074 0x00000000
rtds_write 0x08500075 0x00000000
rtds_write 0x08500076 0x00000000
rtds_write 0x08500077 0x00000000
rtds_write 0x08500078 0x00000000
rtds_write 0x08500079 0x00000000
rtds_write 0x0850007A 0x00000000
rtds_write 0x0850007B 0x00000000
rtds_file_write 0x08550000 trivial_imem.txt
rtds_file_write 0x08552000 trivial_lut.txt

REM SPC1 Variable Delay initialization...
rtds_write 0x08500001 0x0

REM SPC1 Output voltage compare mode...
rtds_write 0x08500005 0x00000000

REM SPC1 Matrix multiplier initialization...
rtds_file_write 0x08400000 SPC1_Com_Word.txt
rtds_file_write 0x08420000 SPC1_Com_LUT.txt
rtds_file_write 0x08480000 SPC1_MAC0.txt
rtds_file_write 0x08482000 SPC1_MAC1.txt
rtds_file_write 0x08484000 SPC1_MAC2.txt
rtds_file_write 0x08486000 SPC1_MAC3.txt

rtds_write 0x08500004 0x0000001F
REM SPC1 Contactors initialization...
rtds_write 0x08640000 0x00000000
rtds_write 0x08640080 0x00000000
rtds_write 0x08640100 0x00000000
rtds_write 0x08640180 0x00000000
rtds_write 0x08640200 0x00000000
rtds_write 0x08640280 0x00000000
rtds_write 0x08640300 0x00000000
rtds_write 0x08640380 0x00000000
rtds_write 0x08640400 0x00000001
rtds_write 0x08640001 0x00000000
rtds_write 0x08640081 0x00000000
rtds_write 0x08640101 0x00000000
rtds_write 0x08640181 0x00000000
rtds_write 0x08640201 0x00000000
rtds_write 0x08640281 0x00000000
rtds_write 0x08640301 0x00000000
rtds_write 0x08640381 0x00000000
rtds_write 0x08640401 0x00000000
rtds_write 0x08640002 0x00000000
rtds_write 0x08640082 0x00000000
rtds_write 0x08640102 0x00000000
rtds_write 0x08640182 0x00000000
rtds_write 0x08640202 0x00000000
rtds_write 0x08640282 0x00000000
rtds_write 0x08640302 0x00000000
rtds_write 0x08640382 0x00000000
rtds_write 0x08640402 0x00000000
rtds_write 0x08640003 0x00000000
rtds_write 0x08640083 0x00000000
rtds_write 0x08640103 0x00000000
rtds_write 0x08640183 0x00000000
rtds_write 0x08640203 0x00000000
rtds_write 0x08640283 0x00000000
rtds_write 0x08640303 0x00000000
rtds_write 0x08640383 0x00000000
rtds_write 0x08640403 0x00000000
rtds_write 0x08640004 0x00000000
rtds_write 0x08640084 0x00000000
rtds_write 0x08640104 0x00000000
rtds_write 0x08640184 0x00000000
rtds_write 0x08640204 0x00000000
rtds_write 0x08640284 0x00000000
rtds_write 0x08640304 0x00000000
rtds_write 0x08640384 0x00000000
rtds_write 0x08640404 0x00000001

REM SPC1 GDS compensation settings...
rtds_write 0x084C0000 0x00000001
rtds_write 0x084C0001 0x00000016
rtds_write 0x084C0004 0x3B4CCCCC
rtds_write 0x084C0005 0xCCCD0000
rtds_write 0x08500000 0x00000140

REM SPC1 FSM digital input pin assignments...

REM SPC1 Comparators initialization...

REM SPC1 DTSM initialization...

REM *****************************************:
REM * SPC2 entries:
REM *****************************************:

REM SPC2 Topology Selector (TS) initialization...
rtds_file_write 0x08980000 SPC2_red_table.txt

rtds_write 0x08900020 0x00000004
rtds_write 0x08900021 0x00000003
rtds_write 0x08900023 0x00000001
rtds_write 0x08900024 0x00000000
rtds_write 0x08900025 0x00000000
rtds_write 0x08900026 0x00000000
rtds_write 0x08900027 0x00000000
rtds_write 0x08900030 0x00000000
rtds_write 0x08900031 0x00000000
rtds_write 0x08900032 0x00000000
rtds_write 0x08900033 0x00000000
rtds_write 0x08900034 0x00000001
rtds_write 0x08900035 0x00000001
rtds_write 0x08900036 0x00000000
rtds_write 0x08900037 0x00000000
rtds_write 0x08900038 0x00000000
rtds_write 0x08900039 0x00000000
rtds_write 0x0890003A 0x00000000
rtds_write 0x0890003B 0x00000000
rtds_file_write 0x08940000 igbt_leg_imem.txt
rtds_file_write 0x08942000 igbt_leg_lut.txt
rtds_write 0x08900040 0x00000004
rtds_write 0x08900041 0x00000003
rtds_write 0x08900043 0x00000001
rtds_write 0x08900044 0x00000000
rtds_write 0x08900045 0x00000000
rtds_write 0x08900046 0x00000000
rtds_write 0x08900047 0x00000000
rtds_write 0x08900050 0x00000000
rtds_write 0x08900051 0x00000000
rtds_write 0x08900052 0x00000000
rtds_write 0x08900053 0x00000000
rtds_write 0x08900054 0x00000001
rtds_write 0x08900055 0x00000001
rtds_write 0x08900056 0x00000000
rtds_write 0x08900057 0x00000000
rtds_write 0x08900058 0x00000000
rtds_write 0x08900059 0x00000000
rtds_write 0x0890005A 0x00000000
rtds_write 0x0890005B 0x00000000
rtds_file_write 0x08948000 igbt_leg_imem.txt
rtds_file_write 0x0894A000 igbt_leg_lut.txt
rtds_write 0x08900060 0x00000004
rtds_write 0x08900061 0x00000003
rtds_write 0x08900063 0x00000001
rtds_write 0x08900064 0x00000000
rtds_write 0x08900065 0x00000000
rtds_write 0x08900066 0x00000000
rtds_write 0x08900067 0x00000000
rtds_write 0x08900070 0x00000000
rtds_write 0x08900071 0x00000000
rtds_write 0x08900072 0x00000000
rtds_write 0x08900073 0x00000000
rtds_write 0x08900074 0x00000001
rtds_write 0x08900075 0x00000001
rtds_write 0x08900076 0x00000000
rtds_write 0x08900077 0x00000000
rtds_write 0x08900078 0x00000000
rtds_write 0x08900079 0x00000000
rtds_write 0x0890007A 0x00000000
rtds_write 0x0890007B 0x00000000
rtds_file_write 0x08950000 igbt_leg_imem.txt
rtds_file_write 0x08952000 igbt_leg_lut.txt

REM SPC2 Variable Delay initialization...
rtds_write 0x08900001 0x0

REM SPC2 Output voltage compare mode...
rtds_write 0x08900005 0x00000000

REM SPC2 Matrix multiplier initialization...
rtds_file_write 0x08800000 SPC2_Com_Word.txt
rtds_file_write 0x08820000 SPC2_Com_LUT.txt
rtds_file_write 0x08880000 SPC2_MAC0.txt
rtds_file_write 0x08882000 SPC2_MAC1.txt
rtds_file_write 0x08884000 SPC2_MAC2.txt
rtds_file_write 0x08886000 SPC2_MAC3.txt

rtds_write 0x08900004 0x00000001
REM SPC2 Contactors initialization...
rtds_write 0x08A40000 0x00000000
rtds_write 0x08A40080 0x00000000
rtds_write 0x08A40100 0x00000000
rtds_write 0x08A40180 0x00000000
rtds_write 0x08A40200 0x00000000
rtds_write 0x08A40280 0x00000000
rtds_write 0x08A40300 0x00000000
rtds_write 0x08A40380 0x00000000
rtds_write 0x08A40400 0x00000001

REM SPC2 GDS compensation settings...
rtds_write 0x088C0000 0x00000001
rtds_write 0x088C0001 0x0000000A
rtds_write 0x088C0004 0x3B4CCCCC
rtds_write 0x088C0005 0xCCCD0000
rtds_write 0x08900000 0x00000140

REM SPC2 FSM digital input pin assignments...
rtds_write 0x08900028 0x00000000
rtds_write 0x08900029 0x00000000
rtds_write 0x0890002A 0x00000000
rtds_write 0x0890002B 0x00000000
rtds_write 0x0890002C 0x00000040
rtds_write 0x0890002D 0x00000041
rtds_write 0x08900022 0x00000000
rtds_write 0x08900048 0x00000000
rtds_write 0x08900049 0x00000000
rtds_write 0x0890004A 0x00000000
rtds_write 0x0890004B 0x00000000
rtds_write 0x0890004C 0x00000042
rtds_write 0x0890004D 0x00000043
rtds_write 0x08900042 0x00000000
rtds_write 0x08900068 0x00000000
rtds_write 0x08900069 0x00000000
rtds_write 0x0890006A 0x00000000
rtds_write 0x0890006B 0x00000000
rtds_write 0x0890006C 0x00000044
rtds_write 0x0890006D 0x00000045
rtds_write 0x08900062 0x00000000

REM SPC2 Comparators initialization...

REM SPC2 DTSM initialization...

REM *****************************************:
REM * SPC3 entries:
REM *****************************************:

REM SPC3 Topology Selector (TS) initialization...
rtds_file_write 0x08D80000 SPC3_red_table.txt

rtds_write 0x08D00020 0x00000004
rtds_write 0x08D00021 0x00000003
rtds_write 0x08D00023 0x00000001
rtds_write 0x08D00024 0x00000000
rtds_write 0x08D00025 0x00000000
rtds_write 0x08D00026 0x00000000
rtds_write 0x08D00027 0x00000000
rtds_write 0x08D00030 0x00000000
rtds_write 0x08D00031 0x00000000
rtds_write 0x08D00032 0x00000000
rtds_write 0x08D00033 0x00000000
rtds_write 0x08D00034 0x00000001
rtds_write 0x08D00035 0x00000001
rtds_write 0x08D00036 0x00000000
rtds_write 0x08D00037 0x00000000
rtds_write 0x08D00038 0x00000000
rtds_write 0x08D00039 0x00000000
rtds_write 0x08D0003A 0x00000000
rtds_write 0x08D0003B 0x00000000
rtds_file_write 0x08D40000 igbt_leg_imem.txt
rtds_file_write 0x08D42000 igbt_leg_lut.txt
rtds_write 0x08D00040 0x00000004
rtds_write 0x08D00041 0x00000003
rtds_write 0x08D00043 0x00000001
rtds_write 0x08D00044 0x00000000
rtds_write 0x08D00045 0x00000000
rtds_write 0x08D00046 0x00000000
rtds_write 0x08D00047 0x00000000
rtds_write 0x08D00050 0x00000000
rtds_write 0x08D00051 0x00000000
rtds_write 0x08D00052 0x00000000
rtds_write 0x08D00053 0x00000000
rtds_write 0x08D00054 0x00000001
rtds_write 0x08D00055 0x00000001
rtds_write 0x08D00056 0x00000000
rtds_write 0x08D00057 0x00000000
rtds_write 0x08D00058 0x00000000
rtds_write 0x08D00059 0x00000000
rtds_write 0x08D0005A 0x00000000
rtds_write 0x08D0005B 0x00000000
rtds_file_write 0x08D48000 igbt_leg_imem.txt
rtds_file_write 0x08D4A000 igbt_leg_lut.txt
rtds_write 0x08D00060 0x00000004
rtds_write 0x08D00061 0x00000003
rtds_write 0x08D00063 0x00000001
rtds_write 0x08D00064 0x00000000
rtds_write 0x08D00065 0x00000000
rtds_write 0x08D00066 0x00000000
rtds_write 0x08D00067 0x00000000
rtds_write 0x08D00070 0x00000000
rtds_write 0x08D00071 0x00000000
rtds_write 0x08D00072 0x00000000
rtds_write 0x08D00073 0x00000000
rtds_write 0x08D00074 0x00000001
rtds_write 0x08D00075 0x00000001
rtds_write 0x08D00076 0x00000000
rtds_write 0x08D00077 0x00000000
rtds_write 0x08D00078 0x00000000
rtds_write 0x08D00079 0x00000000
rtds_write 0x08D0007A 0x00000000
rtds_write 0x08D0007B 0x00000000
rtds_file_write 0x08D50000 igbt_leg_imem.txt
rtds_file_write 0x08D52000 igbt_leg_lut.txt

REM SPC3 Variable Delay initialization...
rtds_write 0x08D00001 0x0

REM SPC3 Output voltage compare mode...
rtds_write 0x08D00005 0x00000000

REM SPC3 Matrix multiplier initialization...
rtds_file_write 0x08C00000 SPC3_Com_Word.txt
rtds_file_write 0x08C20000 SPC3_Com_LUT.txt
rtds_file_write 0x08C80000 SPC3_MAC0.txt
rtds_file_write 0x08C82000 SPC3_MAC1.txt
rtds_file_write 0x08C84000 SPC3_MAC2.txt
rtds_file_write 0x08C86000 SPC3_MAC3.txt

rtds_write 0x08D00004 0x00000001
REM SPC3 Contactors initialization...
rtds_write 0x08E40000 0x00000000
rtds_write 0x08E40080 0x00000000
rtds_write 0x08E40100 0x00000000
rtds_write 0x08E40180 0x00000000
rtds_write 0x08E40200 0x00000000
rtds_write 0x08E40280 0x00000000
rtds_write 0x08E40300 0x00000000
rtds_write 0x08E40380 0x00000000
rtds_write 0x08E40400 0x00000001

REM SPC3 GDS compensation settings...
rtds_write 0x08CC0000 0x00000001
rtds_write 0x08CC0001 0x0000000B
rtds_write 0x08CC0004 0x3B4CCCCC
rtds_write 0x08CC0005 0xCCCD0000
rtds_write 0x08D00000 0x00000140

REM SPC3 FSM digital input pin assignments...
rtds_write 0x08D00028 0x00000000
rtds_write 0x08D00029 0x00000000
rtds_write 0x08D0002A 0x00000000
rtds_write 0x08D0002B 0x00000000
rtds_write 0x08D0002C 0x00000046
rtds_write 0x08D0002D 0x00000047
rtds_write 0x08D00022 0x00000000
rtds_write 0x08D00048 0x00000000
rtds_write 0x08D00049 0x00000000
rtds_write 0x08D0004A 0x00000000
rtds_write 0x08D0004B 0x00000000
rtds_write 0x08D0004C 0x00000048
rtds_write 0x08D0004D 0x00000049
rtds_write 0x08D00042 0x00000000
rtds_write 0x08D00068 0x00000000
rtds_write 0x08D00069 0x00000000
rtds_write 0x08D0006A 0x00000000
rtds_write 0x08D0006B 0x00000000
rtds_write 0x08D0006C 0x0000004A
rtds_write 0x08D0006D 0x0000004B
rtds_write 0x08D00062 0x00000000

REM SPC3 Comparators initialization...

REM SPC3 DTSM initialization...

REM *****************************************:
REM * SPC4 entries:
REM *****************************************:

REM SPC4 Topology Selector (TS) initialization...
rtds_file_write 0x09180000 SPC4_red_table.txt

rtds_write 0x09100020 0x00000000
rtds_write 0x09100021 0x00000000
rtds_write 0x09100023 0x00000000
rtds_write 0x09100024 0x00000000
rtds_write 0x09100025 0x00000000
rtds_write 0x09100026 0x00000000
rtds_write 0x09100027 0x00000000
rtds_write 0x09100030 0x00000000
rtds_write 0x09100031 0x00000000
rtds_write 0x09100032 0x00000000
rtds_write 0x09100033 0x00000000
rtds_write 0x09100034 0x00000000
rtds_write 0x09100035 0x00000000
rtds_write 0x09100036 0x00000000
rtds_write 0x09100037 0x00000000
rtds_write 0x09100038 0x00000000
rtds_write 0x09100039 0x00000000
rtds_write 0x0910003A 0x00000000
rtds_write 0x0910003B 0x00000000
rtds_file_write 0x09140000 trivial_imem.txt
rtds_file_write 0x09142000 trivial_lut.txt
rtds_write 0x09100040 0x00000000
rtds_write 0x09100041 0x00000000
rtds_write 0x09100043 0x00000000
rtds_write 0x09100044 0x00000000
rtds_write 0x09100045 0x00000000
rtds_write 0x09100046 0x00000000
rtds_write 0x09100047 0x00000000
rtds_write 0x09100050 0x00000000
rtds_write 0x09100051 0x00000000
rtds_write 0x09100052 0x00000000
rtds_write 0x09100053 0x00000000
rtds_write 0x09100054 0x00000000
rtds_write 0x09100055 0x00000000
rtds_write 0x09100056 0x00000000
rtds_write 0x09100057 0x00000000
rtds_write 0x09100058 0x00000000
rtds_write 0x09100059 0x00000000
rtds_write 0x0910005A 0x00000000
rtds_write 0x0910005B 0x00000000
rtds_file_write 0x09148000 trivial_imem.txt
rtds_file_write 0x0914A000 trivial_lut.txt
rtds_write 0x09100060 0x00000000
rtds_write 0x09100061 0x00000000
rtds_write 0x09100063 0x00000000
rtds_write 0x09100064 0x00000000
rtds_write 0x09100065 0x00000000
rtds_write 0x09100066 0x00000000
rtds_write 0x09100067 0x00000000
rtds_write 0x09100070 0x00000000
rtds_write 0x09100071 0x00000000
rtds_write 0x09100072 0x00000000
rtds_write 0x09100073 0x00000000
rtds_write 0x09100074 0x00000000
rtds_write 0x09100075 0x00000000
rtds_write 0x09100076 0x00000000
rtds_write 0x09100077 0x00000000
rtds_write 0x09100078 0x00000000
rtds_write 0x09100079 0x00000000
rtds_write 0x0910007A 0x00000000
rtds_write 0x0910007B 0x00000000
rtds_file_write 0x09150000 trivial_imem.txt
rtds_file_write 0x09152000 trivial_lut.txt

REM SPC4 Variable Delay initialization...
rtds_write 0x09100001 0x0

REM SPC4 Output voltage compare mode...
rtds_write 0x09100005 0x00000000

REM SPC4 Matrix multiplier initialization...
rtds_file_write 0x09000000 SPC4_Com_Word.txt
rtds_file_write 0x09020000 SPC4_Com_LUT.txt
rtds_file_write 0x09080000 SPC4_MAC0.txt
rtds_file_write 0x09082000 SPC4_MAC1.txt
rtds_file_write 0x09084000 SPC4_MAC2.txt
rtds_file_write 0x09086000 SPC4_MAC3.txt

rtds_write 0x09100004 0x00000000
REM SPC4 Contactors initialization...

REM SPC4 GDS compensation settings...
rtds_write 0x090C0000 0x00000000
rtds_write 0x090C0001 0x00000000
rtds_write 0x090C0004 0x00000000
rtds_write 0x090C0005 0x00000000
rtds_write 0x09100000 0x00000000

REM SPC4 FSM digital input pin assignments...

REM SPC4 Comparators initialization...

REM SPC4 DTSM initialization...

REM *****************************************:
REM * SPC5 entries:
REM *****************************************:

REM SPC5 Topology Selector (TS) initialization...
rtds_file_write 0x09580000 SPC5_red_table.txt

rtds_write 0x09500020 0x00000000
rtds_write 0x09500021 0x00000000
rtds_write 0x09500023 0x00000000
rtds_write 0x09500024 0x00000000
rtds_write 0x09500025 0x00000000
rtds_write 0x09500026 0x00000000
rtds_write 0x09500027 0x00000000
rtds_write 0x09500030 0x00000000
rtds_write 0x09500031 0x00000000
rtds_write 0x09500032 0x00000000
rtds_write 0x09500033 0x00000000
rtds_write 0x09500034 0x00000000
rtds_write 0x09500035 0x00000000
rtds_write 0x09500036 0x00000000
rtds_write 0x09500037 0x00000000
rtds_write 0x09500038 0x00000000
rtds_write 0x09500039 0x00000000
rtds_write 0x0950003A 0x00000000
rtds_write 0x0950003B 0x00000000
rtds_file_write 0x09540000 trivial_imem.txt
rtds_file_write 0x09542000 trivial_lut.txt
rtds_write 0x09500040 0x00000000
rtds_write 0x09500041 0x00000000
rtds_write 0x09500043 0x00000000
rtds_write 0x09500044 0x00000000
rtds_write 0x09500045 0x00000000
rtds_write 0x09500046 0x00000000
rtds_write 0x09500047 0x00000000
rtds_write 0x09500050 0x00000000
rtds_write 0x09500051 0x00000000
rtds_write 0x09500052 0x00000000
rtds_write 0x09500053 0x00000000
rtds_write 0x09500054 0x00000000
rtds_write 0x09500055 0x00000000
rtds_write 0x09500056 0x00000000
rtds_write 0x09500057 0x00000000
rtds_write 0x09500058 0x00000000
rtds_write 0x09500059 0x00000000
rtds_write 0x0950005A 0x00000000
rtds_write 0x0950005B 0x00000000
rtds_file_write 0x09548000 trivial_imem.txt
rtds_file_write 0x0954A000 trivial_lut.txt
rtds_write 0x09500060 0x00000000
rtds_write 0x09500061 0x00000000
rtds_write 0x09500063 0x00000000
rtds_write 0x09500064 0x00000000
rtds_write 0x09500065 0x00000000
rtds_write 0x09500066 0x00000000
rtds_write 0x09500067 0x00000000
rtds_write 0x09500070 0x00000000
rtds_write 0x09500071 0x00000000
rtds_write 0x09500072 0x00000000
rtds_write 0x09500073 0x00000000
rtds_write 0x09500074 0x00000000
rtds_write 0x09500075 0x00000000
rtds_write 0x09500076 0x00000000
rtds_write 0x09500077 0x00000000
rtds_write 0x09500078 0x00000000
rtds_write 0x09500079 0x00000000
rtds_write 0x0950007A 0x00000000
rtds_write 0x0950007B 0x00000000
rtds_file_write 0x09550000 trivial_imem.txt
rtds_file_write 0x09552000 trivial_lut.txt

REM SPC5 Variable Delay initialization...
rtds_write 0x09500001 0x0

REM SPC5 Output voltage compare mode...
rtds_write 0x09500005 0x00000000

REM SPC5 Matrix multiplier initialization...
rtds_file_write 0x09400000 SPC5_Com_Word.txt
rtds_file_write 0x09420000 SPC5_Com_LUT.txt
rtds_file_write 0x09480000 SPC5_MAC0.txt
rtds_file_write 0x09482000 SPC5_MAC1.txt
rtds_file_write 0x09484000 SPC5_MAC2.txt
rtds_file_write 0x09486000 SPC5_MAC3.txt

rtds_write 0x09500004 0x00000000
REM SPC5 Contactors initialization...

REM SPC5 GDS compensation settings...
rtds_write 0x094C0000 0x00000000
rtds_write 0x094C0001 0x00000000
rtds_write 0x094C0004 0x00000000
rtds_write 0x094C0005 0x00000000
rtds_write 0x09500000 0x00000000

REM SPC5 FSM digital input pin assignments...

REM SPC5 Comparators initialization...

REM SPC5 DTSM initialization...

*****************************************:


REM SP data configuration...
*****************************************:


REM Setting the capture sample step...


REM post SP Init calculation...
rtds_write  
rtds_write 0x00000041 0x000011C1
rtds_write 0x00000005 0x00000002
glbl_write 0x41200008 0x00000000
glbl_write 0x42200008 0x00000001
glbl_write 0x43200008 0x00000000
rtds_write 0x00000043 0x00002710
rtds_write 0x00000042 0x000001F3
rtds_write 0x0000000A 0x00000001


REM CoProcessors uBlaze_1, uBlaze_2 and uBlaze_3 configuration
glbl_write 0x40800000 0x7
glbl_write 0xf8000008 0xdf0d


REM CoProcessor ARM_1 configuration...
glbl_write 0xfffffff0 0xffffff2c  
glbl_write 0xFFFFFF00 0xe3e0000f
glbl_write 0xFFFFFF04 0xe3a01000
glbl_write 0xFFFFFF08 0xe5801000
glbl_write 0xFFFFFF0C 0xe320f002
glbl_write 0xFFFFFF10 0xe5902000
glbl_write 0xFFFFFF14 0xe1520001
glbl_write 0xFFFFFF18 0x0afffffb
glbl_write 0xFFFFFF1C 0xe1a0f002
glbl_write 0x00000000 0xe3e0f0ff
glbl_write 0xf8000244 0x2
glbl_write 0xf8000244 0x22
glbl_write 0xf8000244 0x20
glbl_write 0xf8000244 0x0
glbl_file_write 0x20a00000 cop_2_app_imem.bin
glbl_file_write 0xfffc0000 cop_2_app_dmem.bin


REM disable can devices
sys_command 0x2


REM ifconfig eth0 up
sys_command 0x1


REM enable ETH0 Intr on Core0 CPU
glbl_write 0xF8F01834 0x01010101
glbl_write 0x40800000 0x7
glbl_write 0xfffffff0 0x20a00000


REM Restart counter for collected Linux OS communication apps
app_file_write 0x0 app_init
rtds_write 0x00000027 0x00000140
rtds_write 0x00000040 0x00FFFFFF