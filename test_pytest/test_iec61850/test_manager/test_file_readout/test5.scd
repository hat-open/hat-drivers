<?xml version="1.0" encoding="UTF-8"?>
<SCL version="2007" revision="B" release="4" xmlns="http://www.iec.ch/61850/2003/SCL" xsi:schemaLocation="http://www.iec.ch/61850/2003/SCL SCL.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:IEC_60870_5_104="http://www.iec.ch/61850-80-1/2007/SCL" xmlns:siebase="http://www.siemens.com/energy/2009/09/siprotec5/SieBase" xmlns:siedig="http://www.siemens.com/energy/2011/11/Siedig">
	<Private type="Siemens-SclLib-V5-Version">V03.20.01.000</Private>
	<Private type="Siemens-SclLib-V5-EditTime">16.10.2020 15:21:01</Private>
	<Private type="Siemens-Configurator-Version">6.30.132</Private>
	<Private type="Siemens_SiedigGooseApplicationStorage">
		<siedig:GooseApplicationStorage>
			<siedig:MacAddrMin>01-0C-CD-01-00-00</siedig:MacAddrMin>
			<siedig:MacAddrMax>01-0C-CD-01-01-FF</siedig:MacAddrMax>
		</siedig:GooseApplicationStorage>
	</Private>
	<Header id="IEC station 1" version="1" revision="9" toolID="IEC 61850 System Configurator, Version: 6.30.132" nameStructure="IEDName">
		<Text>IEC station 1</Text>
		<History>
			<Hitem version="1" revision="1" when="Tuesday, October 13, 2020 3:22:29 PM" who="Licenced User:  Marko Malecic Machine: LAPTOP-IV5KV3IL User: Marko Malecic" what="Device SIP is imported from C:\Users\Marko Malecic\AppData\Local\Temp\y1q1zing.z1l\SIP.iid" why="IEC 61850 System Configurator Automatic Startup: Insert Comment" />
			<Hitem version="1" revision="2" when="Thursday, October 15, 2020 11:09:35 AM" who="Licenced User:  Marko Malecic Machine: LAPTOP-IV5KV3IL User: Marko Malecic" what="Device SIP updated from C:\Users\Marko Malecic\AppData\Local\Temp\cdu20vbt.qme\SIP.iid." why="IEC 61850 System Configurator Automatic Startup: Insert Comment" />
			<Hitem version="1" revision="3" when="Thursday, October 15, 2020 1:42:51 PM" who="Licenced User:  Marko Malecic Machine: LAPTOP-IV5KV3IL User: Marko Malecic" what="Device SIP updated from C:\Users\Marko Malecic\AppData\Local\Temp\ltasjpal.1en\SIP.iid." why="IEC 61850 System Configurator Automatic Startup: Insert Comment" />
			<Hitem version="1" revision="4" when="Friday, October 16, 2020 10:27:47 AM" who="Licenced User:  Marko Malecic Machine: LAPTOP-IV5KV3IL User: Marko Malecic" what="Device SIP updated from C:\Users\Marko Malecic\AppData\Local\Temp\3rjybg3b.e4o\SIP.iid." why="IEC 61850 System Configurator Automatic Startup: Insert Comment" />
			<Hitem version="1" revision="5" when="Friday, October 16, 2020 12:11:26 PM" who="Licenced User:  Marko Malecic Machine: LAPTOP-IV5KV3IL User: Marko Malecic" what="Device SIP updated from C:\Users\Marko Malecic\AppData\Local\Temp\24rxdoft.any\SIP.iid." why="IEC 61850 System Configurator Automatic Startup: Insert Comment" />
			<Hitem version="1" revision="6" when="Friday, October 16, 2020 12:12:11 PM" who="Licenced User:  Marko Malecic Machine: LAPTOP-IV5KV3IL User: Marko Malecic" what="Device SIP updated from C:\Users\Marko Malecic\AppData\Local\Temp\qalvrkid.loa\SIP.iid." why="IEC 61850 System Configurator Automatic Startup: Insert Comment" />
			<Hitem version="1" revision="7" when="Friday, October 16, 2020 12:15:55 PM" who="Licenced User:  Marko Malecic Machine: LAPTOP-IV5KV3IL User: Marko Malecic" what="Device SIP updated from C:\Users\Marko Malecic\AppData\Local\Temp\5qjmzy2f.hmi\SIP.iid." why="IEC 61850 System Configurator Automatic Startup: Insert Comment" />
			<Hitem version="1" revision="8" when="Friday, October 16, 2020 2:57:17 PM" who="Licenced User:  Marko Malecic Machine: LAPTOP-IV5KV3IL User: Marko Malecic" what="Device SIP updated from C:\Users\Marko Malecic\AppData\Local\Temp\cgoxleur.ibl\SIP.iid." why="IEC 61850 System Configurator Automatic Startup: Insert Comment" />
			<Hitem version="1" revision="9" when="Friday, October 16, 2020 3:21:01 PM" who="Licenced User:  Marko Malecic Machine: LAPTOP-IV5KV3IL User: Marko Malecic" what="SCD file exported as Edition2B4." why="IEC 61850 System Configurator User Action" />
		</History>
	</Header>
	<Communication>
		<SubNetwork name="Default_subnet" type="8-MMS">
			<Private type="Siemens-Start-Address">172.16.0.1</Private>
			<ConnectedAP iedName="SIP" apName="E">
				<Address>
					<P type="IP" xsi:type="tP_IP">192.168.29.163</P>
					<P type="IP-SUBNET" xsi:type="tP_IP-SUBNET">255.255.255.0</P>
					<P type="OSI-AP-Title">1,3,9999,23</P>
					<P type="OSI-AE-Qualifier">23</P>
					<P type="OSI-PSEL">00000001</P>
					<P type="OSI-SSEL">0001</P>
					<P type="OSI-TSEL">0001</P>
				</Address>
			</ConnectedAP>
		</SubNetwork>
	</Communication>
	<IED desc="7SJ85" name="SIP" type="7SJ85" manufacturer="SIEMENS" configVersion="V08.03.03" originalSclVersion="2007" originalSclRevision="B" owner="IEC station 1" originalSclRelease="4">
		<Private type="Siemens-MasterId">b507e6e7-e774-4703-a1d8-d2cee1188784</Private>
		<Private type="Siemens-s7ManagerName">7SJ85</Private>
		<Private type="Siemens-ICD-Language">en-US</Private>
		<Private type="Siemens-Siprotec5-Product-Code">7SJ85-DAAA-AA0-0AAAA0-AG0112-23111B-AAA000-000AC0-CB1BA1-CB1</Private>
		<Private type="Siemens-Siprotec5-Application-Template">7SJ85_Non_Directional_OC</Private>
		<Private type="Siemens-Siprotec5-Communication-Configuration-Version">80303</Private>
		<Private type="Siemens-Siprotec5-Configuration-Version">V08.03.03</Private>
		<Private type="Siemens-IsSiprotec5IED" />
		<Private type="Siemens-IED-Id">b507e6e7-e774-4703-a1d8-d2cee1188784</Private>
		<Private type="Siemens-ModifiedDate">10/16/2020 12:58:28</Private>
		<Private type="Siemens-ModificationCounter">16</Private>
		<Services nameLength="64">
			<ClientServices goose="true" gsse="false" bufReport="false" unbufReport="false" readLog="false" sv="false" supportsLdName="true" maxGOOSE="128" rGOOSE="false" rSV="false" noIctBinding="false">
				<TimeSyncProt sntp="true" c37_238="false" other="false" iec61850_9_3="true" />
			</ClientServices>
			<DynAssociation max="6" />
			<SettingGroups>
				<SGEdit resvTms="true" />
			</SettingGroups>
			<GetDirectory />
			<GetDataObjectDefinition />
			<DataObjectDirectory />
			<GetDataSetValue />
			<DataSetDirectory />
			<ConfDataSet max="50" maxAttributes="100" modify="true" />
			<DynDataSet max="30" maxAttributes="60" />
			<ReadWrite />
			<ConfReportControl max="60" bufMode="both" bufConf="true" />
			<GetCBValues />
			<ReportSettings cbName="Conf" datSet="Dyn" rptID="Dyn" optFields="Dyn" bufTime="Dyn" trgOps="Dyn" intgPd="Dyn" resvTms="true" />
			<GSESettings cbName="Conf" datSet="Conf" appID="Conf" dataLabel="Fix" kdaParticipant="false" />
			<ConfLNs fixPrefix="false" fixLnInst="false" />
			<ConfLdName />
			<GOOSE max="16" fixedOffs="false" goose="true" rGOOSE="false" />
			<FileHandling />
			<SupSubscription maxGo="0" maxSv="0" />
			<ValueHandling setToRO="false" />
			<RedProt hsr="true" prp="true" rstp="true" />
			<CommProt ipv6="false" />
		</Services>
		<AccessPoint desc="Port E" name="E" router="false" clock="false">
			<Server timeout="0">
				<Authentication none="true" />
				<LDevice desc="Application" inst="Application">
					<Private type="Siemens-MasterId">c595d2a7-3593-470c-a6b2-18a21f0b066c</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_Application" desc="General">
						<Private type="Siemens-MasterId">3723e42a-cebf-4e5d-a414-e6e488d98a50</Private>
						<DataSet name="DataSet">
							<FCDA ldInst="CB1" prefix="" lnClass="CSWI" lnInst="1" doName="Pos" fc="ST" />
							<FCDA ldInst="CB1" prefix="" lnClass="CILO" lnInst="1" doName="EnaOpn" fc="ST" />
							<FCDA ldInst="CB1" prefix="" lnClass="CILO" lnInst="1" doName="EnaCls" fc="ST" />
							<FCDA ldInst="Dc1" prefix="" lnClass="CSWI" lnInst="1" doName="Pos" fc="ST" />
							<FCDA ldInst="Dc1" prefix="" lnClass="CILO" lnInst="1" doName="EnaOpn" fc="ST" />
							<FCDA ldInst="Dc1" prefix="" lnClass="CILO" lnInst="1" doName="EnaCls" fc="ST" />
							<FCDA ldInst="Dc2" prefix="" lnClass="CILO" lnInst="1" doName="EnaOpn" fc="ST" />
							<FCDA ldInst="Dc2" prefix="" lnClass="CILO" lnInst="1" doName="EnaCls" fc="ST" />
							<FCDA ldInst="Dc2" prefix="" lnClass="CSWI" lnInst="1" doName="Pos" fc="ST" />
							<FCDA ldInst="Dc3" prefix="" lnClass="CSWI" lnInst="1" doName="Pos" fc="ST" />
							<FCDA ldInst="Dc3" prefix="" lnClass="CILO" lnInst="1" doName="EnaOpn" fc="ST" />
							<FCDA ldInst="Dc3" prefix="" lnClass="CILO" lnInst="1" doName="EnaCls" fc="ST" />
							<FCDA ldInst="VI3p1_5051NOCgndB1" prefix="ND_" lnClass="PTOC" lnInst="1" doName="Str" fc="ST" />
							<FCDA ldInst="VI3p1_5051NOCgndB1" prefix="ND_" lnClass="PTOC" lnInst="1" doName="Op" fc="ST" />
							<FCDA ldInst="VI3p1_5051OC3phase1" prefix="ID_" lnClass="PTOC" lnInst="1" doName="Str" fc="ST" />
							<FCDA ldInst="VI3p1_5051OC3phase1" prefix="ID_" lnClass="PTOC" lnInst="1" doName="Op" fc="ST" />
							<FCDA ldInst="Application" prefix="" lnClass="LLN0" doName="LocKey" fc="ST" />
							<FCDA ldInst="Application" prefix="" lnClass="LLN0" doName="LocSta" fc="ST" />
							<FCDA ldInst="Application" prefix="" lnClass="CALH" lnInst="0" doName="GrAlm" fc="ST" />
							<FCDA ldInst="Application" prefix="" lnClass="CALH" lnInst="0" doName="GrWrn" fc="ST" />
							<FCDA ldInst="Application" prefix="" lnClass="CALH" lnInst="0" doName="GrInd" fc="ST" />
							<FCDA ldInst="Application" prefix="" lnClass="LPHD" lnInst="0" doName="PhyHealth" fc="ST" />
							<FCDA ldInst="PowS_MeasPointV3ph1" prefix="VTCB_" lnClass="SFFM" lnInst="1" doName="Mod" fc="ST" />
							<FCDA ldInst="UD1" prefix="RSLED" lnClass="GAPC" lnInst="1" doName="SPS" fc="ST" />
							<FCDA ldInst="VI3p1_27Undervoltage1" prefix="" lnClass="PTUV" lnInst="1" doName="Op" fc="ST" />
							<FCDA ldInst="VI3p1_27Undervoltage1" prefix="" lnClass="PTUV" lnInst="1" doName="Str" fc="ST" />
							<FCDA ldInst="VI3p1_27Undervoltage1" prefix="" lnClass="PTUV" lnInst="2" doName="Str" fc="ST" />
							<FCDA ldInst="VI3p1_27Undervoltage1" prefix="" lnClass="PTUV" lnInst="2" doName="Op" fc="ST" />
							<FCDA ldInst="VI3p1_46I21" prefix="I2_" lnClass="PTOC" lnInst="1" doName="Op" fc="ST" />
							<FCDA ldInst="VI3p1_46I21" prefix="I2_" lnClass="PTOC" lnInst="1" doName="Str" fc="ST" />
							<FCDA ldInst="VI3p1_51VOC3phVdep1" prefix="DEP_" lnClass="PVOC" lnInst="1" doName="Str" fc="ST" />
							<FCDA ldInst="VI3p1_51VOC3phVdep1" prefix="DEP_" lnClass="PVOC" lnInst="1" doName="Op" fc="ST" />
							<FCDA ldInst="VI3p1_51VOC3phVdep1" prefix="UVSI_" lnClass="PTOC" lnInst="1" doName="Str" fc="ST" />
							<FCDA ldInst="VI3p1_51VOC3phVdep1" prefix="UVSI_" lnClass="PTOC" lnInst="1" doName="Op" fc="ST" />
							<FCDA ldInst="VI3p1_59Overvoltage1" prefix="" lnClass="PTOV" lnInst="1" doName="Str" fc="ST" />
							<FCDA ldInst="VI3p1_59Overvoltage1" prefix="" lnClass="PTOV" lnInst="1" doName="Op" fc="ST" />
							<FCDA ldInst="VI3p1_59Overvoltage1" prefix="" lnClass="PTOV" lnInst="2" doName="Str" fc="ST" />
							<FCDA ldInst="VI3p1_59Overvoltage1" prefix="" lnClass="PTOV" lnInst="2" doName="Op" fc="ST" />
							<FCDA ldInst="VI3p1_67DirOC3phA1" prefix="DID_" lnClass="PTOC" lnInst="1" doName="Str" fc="ST" />
							<FCDA ldInst="VI3p1_67DirOC3phA1" prefix="DID_" lnClass="PTOC" lnInst="1" doName="Op" fc="ST" />
							<FCDA ldInst="VI3p1_67DirOC3phA1" prefix="DID_" lnClass="PTOC" lnInst="2" doName="Str" fc="ST" />
							<FCDA ldInst="VI3p1_67DirOC3phA1" prefix="DID_" lnClass="PTOC" lnInst="2" doName="Op" fc="ST" />
							<FCDA ldInst="VI3p1_81OverfrequA1" prefix="A_" lnClass="PTOF" lnInst="1" doName="Str" fc="ST" />
							<FCDA ldInst="VI3p1_81OverfrequA1" prefix="A_" lnClass="PTOF" lnInst="1" doName="Op" fc="ST" />
							<FCDA ldInst="VI3p1_81OverfrequA1" prefix="A_" lnClass="PTOF" lnInst="2" doName="Str" fc="ST" />
							<FCDA ldInst="VI3p1_81OverfrequA1" prefix="A_" lnClass="PTOF" lnInst="2" doName="Op" fc="ST" />
							<FCDA ldInst="VI3p1_81UnderfrequA1" prefix="A_" lnClass="PTUF" lnInst="1" doName="Str" fc="ST" />
							<FCDA ldInst="VI3p1_81UnderfrequA1" prefix="A_" lnClass="PTUF" lnInst="1" doName="Op" fc="ST" />
							<FCDA ldInst="VI3p1_81UnderfrequA1" prefix="A_" lnClass="PTUF" lnInst="2" doName="Str" fc="ST" />
							<FCDA ldInst="VI3p1_81UnderfrequA1" prefix="A_" lnClass="PTUF" lnInst="2" doName="Op" fc="ST" />
						</DataSet>
						<DataSet name="DataSet_1">
							<FCDA ldInst="VI3p1_OperationalValues" prefix="RPRE_" lnClass="MMXU" lnInst="1" doName="PPV.phsAB" fc="MX" />
							<FCDA ldInst="VI3p1_OperationalValues" prefix="RPRE_" lnClass="MMXU" lnInst="1" doName="PPV.phsBC" fc="MX" />
							<FCDA ldInst="VI3p1_OperationalValues" prefix="RPRE_" lnClass="MMXU" lnInst="1" doName="PPV.phsCA" fc="MX" />
							<FCDA ldInst="VI3p1_OperationalValues" prefix="RPRE_" lnClass="MMXU" lnInst="1" doName="PhV.phsA" fc="MX" />
							<FCDA ldInst="VI3p1_OperationalValues" prefix="RPRE_" lnClass="MMXU" lnInst="1" doName="PhV.phsB" fc="MX" />
							<FCDA ldInst="VI3p1_OperationalValues" prefix="RPRE_" lnClass="MMXU" lnInst="1" doName="PhV.phsC" fc="MX" />
							<FCDA ldInst="VI3p1_OperationalValues" prefix="RPRE_" lnClass="MMXU" lnInst="1" doName="PhV.res" fc="MX" />
							<FCDA ldInst="VI3p1_OperationalValues" prefix="RPRE_" lnClass="MMXU" lnInst="1" doName="A.phsA" fc="MX" />
							<FCDA ldInst="VI3p1_OperationalValues" prefix="RPRE_" lnClass="MMXU" lnInst="1" doName="A.phsB" fc="MX" />
							<FCDA ldInst="VI3p1_OperationalValues" prefix="RPRE_" lnClass="MMXU" lnInst="1" doName="A.phsC" fc="MX" />
							<FCDA ldInst="VI3p1_OperationalValues" prefix="RPRE_" lnClass="MMXU" lnInst="1" doName="A.res" fc="MX" />
							<FCDA ldInst="VI3p1_OperationalValues" prefix="PPRE_" lnClass="MMXU" lnInst="1" doName="TotW" fc="MX" />
							<FCDA ldInst="VI3p1_OperationalValues" prefix="PPRE_" lnClass="MMXU" lnInst="1" doName="TotVAr" fc="MX" />
							<FCDA ldInst="VI3p1_OperationalValues" prefix="PPRE_" lnClass="MMXU" lnInst="1" doName="TotVA" fc="MX" />
							<FCDA ldInst="VI3p1_OperationalValues" prefix="PPRE_" lnClass="MMXU" lnInst="1" doName="TotPF" fc="MX" />
							<FCDA ldInst="VI3p1_OperationalValues" prefix="PPRE_" lnClass="MMXU" lnInst="1" doName="Hz" fc="MX" />
						</DataSet>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB" confRev="1" buffered="false" name="A_URCB">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_1" confRev="1" buffered="false" name="A_URCB_1">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_2" confRev="1" buffered="false" name="A_URCB_2">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_3" confRev="1" buffered="false" name="A_URCB_3">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_4" confRev="1" buffered="false" name="A_URCB_4">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_5" confRev="1" buffered="false" name="A_URCB_5">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_6" confRev="1" buffered="false" name="A_URCB_6">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_7" confRev="1" buffered="false" name="A_URCB_7">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_8" confRev="1" buffered="false" name="A_URCB_8">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_9" confRev="1" buffered="false" name="A_URCB_9">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_10" confRev="1" buffered="false" name="A_URCB_10">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_11" confRev="1" buffered="false" name="A_URCB_11">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_12" confRev="1" buffered="false" name="A_URCB_12">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_13" confRev="1" buffered="false" name="A_URCB_13">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_14" confRev="1" buffered="false" name="A_URCB_14">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_15" confRev="1" buffered="false" name="A_URCB_15">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_16" confRev="1" buffered="false" name="A_URCB_16">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_17" confRev="1" buffered="false" name="A_URCB_17">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_18" confRev="1" buffered="false" name="A_URCB_18">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_19" confRev="1" buffered="false" name="A_URCB_19">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_20" confRev="1" buffered="false" name="A_URCB_20">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_21" confRev="1" buffered="false" name="A_URCB_21">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_22" confRev="1" buffered="false" name="A_URCB_22">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_23" confRev="1" buffered="false" name="A_URCB_23">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_24" confRev="1" buffered="false" name="A_URCB_24">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_25" confRev="1" buffered="false" name="A_URCB_25">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_26" confRev="1" buffered="false" name="A_URCB_26">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_27" confRev="1" buffered="false" name="A_URCB_27">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_28" confRev="1" buffered="false" name="A_URCB_28">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$RP$A_URCB_29" confRev="1" buffered="false" name="A_URCB_29">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB" confRev="1" buffered="true" name="A_BRCB">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_1" confRev="1" buffered="true" name="A_BRCB_1">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_2" confRev="1" buffered="true" name="A_BRCB_2">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_3" confRev="1" buffered="true" name="A_BRCB_3">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_4" confRev="1" buffered="true" name="A_BRCB_4">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_5" confRev="1" buffered="true" name="A_BRCB_5">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_6" confRev="1" buffered="true" name="A_BRCB_6">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_7" confRev="1" buffered="true" name="A_BRCB_7">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_8" confRev="1" buffered="true" name="A_BRCB_8">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_9" confRev="1" buffered="true" name="A_BRCB_9">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_10" confRev="1" buffered="true" name="A_BRCB_10">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_11" confRev="1" buffered="true" name="A_BRCB_11">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_12" confRev="1" buffered="true" name="A_BRCB_12">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_13" confRev="1" buffered="true" name="A_BRCB_13">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_14" confRev="1" buffered="true" name="A_BRCB_14">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_15" confRev="1" buffered="true" name="A_BRCB_15">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_16" confRev="1" buffered="true" name="A_BRCB_16">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_17" confRev="1" buffered="true" name="A_BRCB_17">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_18" confRev="1" buffered="true" name="A_BRCB_18">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_19" confRev="1" buffered="true" name="A_BRCB_19">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_20" confRev="1" buffered="true" name="A_BRCB_20">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_21" confRev="1" buffered="true" name="A_BRCB_21">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_22" confRev="1" buffered="true" name="A_BRCB_22">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl rptID="SIPApplication/LLN0$BR$A_BRCB_23" confRev="1" buffered="true" name="A_BRCB_23">
							<Private type="Siemens-Siprotec5-IsPredefined" />
							<OptFields />
						</ReportControl>
						<ReportControl datSet="DataSet" rptID="SIP/Application/LLN0$RP$Report" confRev="310001" buffered="false" bufTime="100" name="Report">
							<TrgOps dchg="true" qchg="true" dupd="true" period="true" gi="true" />
							<OptFields seqNum="true" timeStamp="true" dataSet="true" reasonCode="true" dataRef="false" entryID="false" configRef="true" bufOvfl="false" />
							<RptEnabled max="4" />
						</ReportControl>
						<ReportControl datSet="DataSet_1" rptID="SIP/Application/LLN0$BR$Report_1" confRev="1" buffered="true" bufTime="100" name="Report_1">
							<TrgOps dchg="true" qchg="true" dupd="true" period="true" gi="true" />
							<OptFields seqNum="true" timeStamp="true" dataSet="true" reasonCode="true" dataRef="false" entryID="false" configRef="true" bufOvfl="false" />
							<RptEnabled max="4" />
						</ReportControl>
						<DOI name="Mod" desc="Test mode">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health (61850 only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="LEDRs" desc="LED reset">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="LocKey" desc="Sw.authority key/set">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="dataNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="LocSta" desc="Switching auth. station">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="dataNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="MltLev" desc="Multiple sw.auth. levels">
							<DAI name="setVal">
								<Val>false</Val>
							</DAI>
							<DAI name="dataNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<SettingControl numOfSGs="1" actSG="1">
							<Private type="Siemens-MasterId">a78cf56c-eb65-49ae-a82a-83e6eb1be5c5</Private>
						</SettingControl>
					</LN0>
					<LN prefix="" lnClass="LPHD" inst="0" lnType="SIPROTEC5_LNType_LPHD" desc="Device">
						<Private type="Siemens-MasterId">0c62cad6-dbd0-43c3-8d18-f068577eb77a</Private>
						<DOI name="PhyNam" desc="Physical device name">
							<DAI name="vendor">
								<Val>SIEMENS</Val>
							</DAI>
							<DAI name="hwRev">
								<Val>7SJ85-DAAA-AA0-0AAAA0-AG0112-23111B-AAA000-000AC0-CB1BA1-CB1</Val>
							</DAI>
							<DAI name="swRev">
								<Val>V08.03</Val>
							</DAI>
							<DAI name="model">
								<Val>7SJ85</Val>
							</DAI>
						</DOI>
						<DOI name="PhyHealth" desc="Physical health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Proxy" desc="Proxy">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="PwrUp" desc="Device startup">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Sim" desc="GOOSE/SV sim.mode">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="ctlModel">
								<Val>sbo-with-normal-security</Val>
							</DAI>
							<DAI name="sboTimeout">
								<Val>30000</Val>
							</DAI>
							<DAI name="SBO" valKind="Conf" />
							<SDI name="SBOw">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
							<SDI name="Cancel">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="OpTmh" desc="Device operating hours">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>h</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="PrcModIna" desc="Process mode inactive">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
							<DAI name="blkEna" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="" lnClass="CALH" inst="0" lnType="SIPROTEC5_LNType_CALH_Application" desc="Alarm handling">
						<Private type="Siemens-MasterId">d329afd0-883e-4a52-80a0-f38c5600bcf7</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="GrAlm" desc="Group alarm">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="GrWrn" desc="Group warning">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="GrInd" desc="Group indication">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="" lnClass="LTIM" inst="0" lnType="SIPROTEC5_LNType_LTIM_Application" desc="Time managem.">
						<Private type="Siemens-MasterId">46b32325-9926-437a-bfb8-dbbd35cacae6</Private>
						<DOI name="Mod" desc="Mode (status only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="TmDT" desc="Daylight saving time">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="TmOfsTmm" desc="Time zone offset to UTC">
							<DAI name="setVal">
								<Val>60</Val>
							</DAI>
							<DAI name="minVal">
								<Val>-720</Val>
							</DAI>
							<DAI name="maxVal">
								<Val>840</Val>
							</DAI>
							<DAI name="stepSize">
								<Val>15</Val>
							</DAI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>min</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="TmUseDT" desc="Switch daylight sav. time">
							<DAI name="setVal">
								<Val>true</Val>
							</DAI>
						</DOI>
						<DOI name="TmChgDT" desc="Start of daylight sav. time">
							<SDI name="setCal">
								<DAI name="occ" valKind="Conf">
									<Val>0</Val>
								</DAI>
								<DAI name="occType" valKind="Conf">
									<Val>WeekDay</Val>
								</DAI>
								<DAI name="occPer" valKind="Conf">
									<Val>Year</Val>
								</DAI>
								<DAI name="weekDay" valKind="Conf">
									<Val>Sunday</Val>
								</DAI>
								<DAI name="month" valKind="Conf">
									<Val>March</Val>
								</DAI>
								<DAI name="day" valKind="Conf">
									<Val>0</Val>
								</DAI>
								<DAI name="hr" valKind="Conf">
									<Val>2</Val>
								</DAI>
								<DAI name="mn" valKind="Conf">
									<Val>0</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="TmChgST" desc="End of daylight sav. time">
							<SDI name="setCal">
								<DAI name="occ" valKind="Conf">
									<Val>0</Val>
								</DAI>
								<DAI name="occType" valKind="Conf">
									<Val>WeekDay</Val>
								</DAI>
								<DAI name="occPer" valKind="Conf">
									<Val>Year</Val>
								</DAI>
								<DAI name="weekDay" valKind="Conf">
									<Val>Sunday</Val>
								</DAI>
								<DAI name="month" valKind="Conf">
									<Val>October</Val>
								</DAI>
								<DAI name="day" valKind="Conf">
									<Val>0</Val>
								</DAI>
								<DAI name="hr" valKind="Conf">
									<Val>3</Val>
								</DAI>
								<DAI name="mn" valKind="Conf">
									<Val>0</Val>
								</DAI>
							</SDI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="LTMS" inst="0" lnType="SIPROTEC5_LNType_LTMS_Application" desc="Time sync.">
						<Private type="Siemens-MasterId">7678ded3-a4a4-45d3-ab9b-cb24d266f1fc</Private>
						<DOI name="Mod" desc="Mode (status only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="TmSrc" desc="Current time source">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="TmSrcTyp" desc="Type of clock source">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="TmChSt1" desc="Status time source 1">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="TmChSt2" desc="Status time source 2">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="" lnClass="LTRK" inst="0" lnType="SIPROTEC5_LNType_LTRK_Application" desc="Service track.">
						<Private type="Siemens-MasterId">4146dcb8-54e8-432c-ab25-bb1e65c9614e</Private>
						<DOI name="Mod" desc="Mode (status only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="GenTrk" desc="Common Tracking">
							<DAI name="objRef" valKind="Conf" />
							<DAI name="serviceType" valKind="Conf" />
							<DAI name="errorCode" valKind="Conf" />
							<DAI name="originatorID" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="SgcbTrk" desc="Settings grps. access">
							<DAI name="objRef" valKind="Conf" />
							<DAI name="serviceType" valKind="Conf" />
							<DAI name="errorCode" valKind="Conf" />
							<DAI name="originatorID" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="numOfSG" valKind="Conf" />
							<DAI name="actSG" valKind="Conf" />
							<DAI name="editSG" valKind="Conf" />
							<DAI name="cnfEdit" valKind="Conf" />
							<DAI name="lActTm" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="RSLED" lnClass="GAPC" inst="0" lnType="SIPROTEC5_LNType_ResetLed" desc="LED not in FG">
						<Private type="Siemens-MasterId">b33d8da1-d869-45da-87c6-24e0b909bd6b</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="CB1" inst="CB1">
					<Private type="Siemens-MasterId">956c9f4d-10e9-475d-9bb7-e2533610c41f</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="CB1/LLN0/LLN0">
						<Private type="Siemens-MasterId">a8d6da5d-c58c-4564-9e27-ce31c3cd49c1</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@Application</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="" lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_ResetLed" desc="General">
						<Private type="Siemens-MasterId">28fae328-a054-4da8-a9eb-3a73795a0b33</Private>
						<DOI name="Mod" desc="Mode (status only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="PTRC" inst="1" lnType="SIPROTEC5_LNType_PTRC_Trip_3pol" desc="Trip logic">
						<Private type="Siemens-MasterId">9f5a13de-77e4-4c74-9a26-617dcebf6b15</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Tr" desc="Trip indication">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="neut" valKind="Conf" />
							<DAI name="dirNeut" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="" lnClass="XCBR" inst="1" lnType="SIPROTEC5_LNType_XCBR_3pol_Ctl" desc="Circuit break.">
						<Private type="Siemens-MasterId">d7e3ab61-c1c3-4109-9cbf-cf8ccb6fe591</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Loc" desc="Switching auth. local">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="EEHealth" desc="External health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="OpCnt" desc="Op.ct.">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Pos" desc="Position">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="stSeld" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
							<DAI name="blkEna" valKind="Conf" />
							<SDI name="pulseConfig">
								<DAI name="cmdQual">
									<Val>pulse</Val>
								</DAI>
								<DAI name="onDur">
									<Val>100</Val>
								</DAI>
								<DAI name="offDur">
									<Val>0</Val>
								</DAI>
								<DAI name="numPls">
									<Val>1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="BlkOpn" desc="Block opening">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="BlkCls" desc="Block closing">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="SumSwARs" desc="ΣI Brk.">
							<DAI name="actVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>A</Val>
								</DAI>
							</SDI>
							<DAI name="pulsQty">
								<Val>0.001</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="GAPC" inst="2" lnType="SIPROTEC5_LNType_GAPC_ManualClose" desc="Manual close">
						<Private type="Siemens-MasterId">045962dc-a528-4874-8b78-fb6dca78a34c</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Blk" desc="&gt;Block manual close">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="RSLED" lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_ResetLed" desc="Reset LED Group">
						<Private type="Siemens-MasterId">67d61cf9-1f57-435e-bc87-ba8eca023854</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="CSWI" inst="1" lnType="SIPROTEC5_LNType_CSWI" desc="Control">
						<Private type="Siemens-MasterId">8791d6db-cdd0-479e-936f-3ed357387d69</Private>
						<Private type="Siemens-LN-Dependency" />
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Loc" desc="Switching auth. local">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Pos" desc="Cmd. with feedback">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="stSeld" valKind="Conf" />
							<DAI name="ctlModel">
								<Val>sbo-with-enhanced-security</Val>
							</DAI>
							<DAI name="sboTimeout">
								<Val>30000</Val>
							</DAI>
							<DAI name="operTimeout">
								<Val>1000</Val>
							</DAI>
							<DAI name="SBO" valKind="Conf" />
							<SDI name="SBOw">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
							<SDI name="Cancel">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="LocKey" desc="Sw.author. key switch">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="LocSta" desc="Switching auth. station">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="ctlModel">
								<Val>status-only</Val>
							</DAI>
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="CILO" inst="1" lnType="SIPROTEC5_LNType_CILO" desc="Interlocking">
						<Private type="Siemens-MasterId">22d06bc3-2fe6-4b0d-80e7-1169f7ea9e61</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="EnaOpn" desc="&gt;Enable opening">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="EnaCls" desc="&gt;Enable closing">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="CBT_" lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_ResetLed" desc="CB test">
						<Private type="Siemens-MasterId">ac7ceeb2-08d8-4c83-8616-7a6545d01636</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="CB1_FdOMV" inst="CB1_Fundamental">
					<Private type="Siemens-MasterId">47046d3a-26ac-48b7-8809-8c8aeee0b4ca</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="CB1_Fundamental/LLN0/LLN0">
						<Private type="Siemens-MasterId">ec4758ff-cc92-4e70-9549-33467722c499</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@CB1</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="FPRE_" lnClass="MMXU" inst="1" lnType="SIPROTEC5_LNType_MMXU_OpMeas_Fund_3ph_Pres" desc="Fundam">
						<Private type="Siemens-MasterId">92c080fa-5f03-435f-9bba-ec10af19d415</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="PPV" desc="Vpp">
							<SDI name="phsAB" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="phsBC" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="phsCA" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="PhV" desc="Vph">
							<SDI name="phsA" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="phsB" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="phsC" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="res" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>20000</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="A" desc="Iph">
							<SDI name="phsA" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>A</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="phsB" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>A</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="phsC" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>A</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="res" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>A</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>100000</Val>
								</DAI>
							</SDI>
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="Dc1" inst="Dc1">
					<Private type="Siemens-MasterId">cbc434db-dd52-49d9-bc0e-c6f449f30b69</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="Dc1/LLN0/LLN0">
						<Private type="Siemens-MasterId">a7b9070f-d5ab-4720-93e3-15e5301e0646</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@Application</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="" lnClass="CSWI" inst="1" lnType="SIPROTEC5_LNType_CSWI" desc="Control">
						<Private type="Siemens-MasterId">8033bd17-adf7-4e54-9cde-9618be5cac0d</Private>
						<Private type="Siemens-LN-Dependency" />
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Loc" desc="Switching auth. local">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Pos" desc="Cmd. with feedback">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="stSeld" valKind="Conf" />
							<DAI name="ctlModel">
								<Val>sbo-with-enhanced-security</Val>
							</DAI>
							<DAI name="sboTimeout">
								<Val>30000</Val>
							</DAI>
							<DAI name="operTimeout">
								<Val>10000</Val>
							</DAI>
							<DAI name="SBO" valKind="Conf" />
							<SDI name="SBOw">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
							<SDI name="Cancel">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="LocKey" desc="Sw.author. key switch">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="LocSta" desc="Switching auth. station">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="ctlModel">
								<Val>status-only</Val>
							</DAI>
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="CILO" inst="1" lnType="SIPROTEC5_LNType_CILO" desc="Interlocking">
						<Private type="Siemens-MasterId">f4ce1128-b7ed-4e09-8831-e4cf8aaec374</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="EnaOpn" desc="&gt;Enable opening">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="EnaCls" desc="&gt;Enable closing">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="" lnClass="XSWI" inst="1" lnType="SIPROTEC5_LNType_XSWI_Ctl" desc="Disconnector">
						<Private type="Siemens-MasterId">a5724014-9fe6-4fe6-9531-c6fbd331e456</Private>
						<DOI name="Mod" desc="Mode (status only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Loc" desc="Switching auth. local">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="OpCnt" desc="Op.ct.">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Pos" desc="Position">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="stSeld" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
							<DAI name="blkEna" valKind="Conf" />
							<SDI name="pulseConfig">
								<DAI name="cmdQual">
									<Val>pulse</Val>
								</DAI>
								<DAI name="onDur">
									<Val>10000</Val>
								</DAI>
								<DAI name="offDur">
									<Val>0</Val>
								</DAI>
								<DAI name="numPls">
									<Val>1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="BlkOpn" desc="Block opening">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="BlkCls" desc="Block closing">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="SwTyp" desc="Switching-device type">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="Dc2" inst="Dc2">
					<Private type="Siemens-MasterId">5534c904-b995-406e-956f-0cd1a00e4597</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="Dc2/LLN0/LLN0">
						<Private type="Siemens-MasterId">977cd32c-0c9f-4738-8b63-3baf82df4bd7</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@Application</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="" lnClass="CSWI" inst="1" lnType="SIPROTEC5_LNType_CSWI" desc="Control">
						<Private type="Siemens-MasterId">22a5ccc9-a71d-441b-aaf5-3069bc1991ff</Private>
						<Private type="Siemens-LN-Dependency" />
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Loc" desc="Switching auth. local">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Pos" desc="Cmd. with feedback">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="stSeld" valKind="Conf" />
							<DAI name="ctlModel">
								<Val>sbo-with-enhanced-security</Val>
							</DAI>
							<DAI name="sboTimeout">
								<Val>30000</Val>
							</DAI>
							<DAI name="operTimeout">
								<Val>10000</Val>
							</DAI>
							<DAI name="SBO" valKind="Conf" />
							<SDI name="SBOw">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
							<SDI name="Cancel">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="LocKey" desc="Sw.author. key switch">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="LocSta" desc="Switching auth. station">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="ctlModel">
								<Val>status-only</Val>
							</DAI>
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="CILO" inst="1" lnType="SIPROTEC5_LNType_CILO" desc="Interlocking">
						<Private type="Siemens-MasterId">2c3b901f-8f4f-48bc-9343-7cec6d006513</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="EnaOpn" desc="&gt;Enable opening">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="EnaCls" desc="&gt;Enable closing">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="" lnClass="XSWI" inst="1" lnType="SIPROTEC5_LNType_XSWI_Ctl" desc="Disconnector">
						<Private type="Siemens-MasterId">1e92b3c7-c750-4499-96d4-00ad02aaefb0</Private>
						<DOI name="Mod" desc="Mode (status only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Loc" desc="Switching auth. local">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="OpCnt" desc="Op.ct.">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Pos" desc="Position">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="stSeld" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
							<DAI name="blkEna" valKind="Conf" />
							<SDI name="pulseConfig">
								<DAI name="cmdQual">
									<Val>pulse</Val>
								</DAI>
								<DAI name="onDur">
									<Val>10000</Val>
								</DAI>
								<DAI name="offDur">
									<Val>0</Val>
								</DAI>
								<DAI name="numPls">
									<Val>1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="BlkOpn" desc="Block opening">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="BlkCls" desc="Block closing">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="SwTyp" desc="Switching-device type">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="Dc3" inst="Dc3">
					<Private type="Siemens-MasterId">2eab13c6-3d18-4ca8-86bb-ba76d294a571</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="Dc3/LLN0/LLN0">
						<Private type="Siemens-MasterId">b60011c9-32e8-4ee2-baa3-53eaed3c4b4d</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 13:22:19</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@Application</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="" lnClass="CSWI" inst="1" lnType="SIPROTEC5_LNType_CSWI" desc="Control">
						<Private type="Siemens-MasterId">ca44699b-2d01-48f1-92f8-96a1c0be1179</Private>
						<Private type="Siemens-LN-Dependency" />
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 13:22:19</Val>
							</DAI>
						</DOI>
						<DOI name="Loc" desc="Switching auth. local">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Pos" desc="Cmd. with feedback">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="stSeld" valKind="Conf" />
							<DAI name="ctlModel">
								<Val>sbo-with-enhanced-security</Val>
							</DAI>
							<DAI name="sboTimeout">
								<Val>30000</Val>
							</DAI>
							<DAI name="operTimeout">
								<Val>10000</Val>
							</DAI>
							<DAI name="SBO" valKind="Conf" />
							<SDI name="SBOw">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
							<SDI name="Cancel">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="LocKey" desc="Sw.author. key switch">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="LocSta" desc="Switching auth. station">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="ctlModel">
								<Val>status-only</Val>
							</DAI>
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="CILO" inst="1" lnType="SIPROTEC5_LNType_CILO" desc="Interlocking">
						<Private type="Siemens-MasterId">297c11d2-e48c-4609-9420-3f50441f2dfe</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 13:22:19</Val>
							</DAI>
						</DOI>
						<DOI name="EnaOpn" desc="&gt;Enable opening">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="EnaCls" desc="&gt;Enable closing">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="" lnClass="XSWI" inst="1" lnType="SIPROTEC5_LNType_XSWI_Ctl" desc="Disconnector">
						<Private type="Siemens-MasterId">7da291f7-28ae-4f89-8755-d0e92becfc21</Private>
						<DOI name="Mod" desc="Mode (status only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 13:22:19</Val>
							</DAI>
						</DOI>
						<DOI name="Loc" desc="Switching auth. local">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="OpCnt" desc="Op.ct.">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Pos" desc="Position">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="stSeld" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
							<DAI name="blkEna" valKind="Conf" />
							<SDI name="pulseConfig">
								<DAI name="cmdQual">
									<Val>pulse</Val>
								</DAI>
								<DAI name="onDur">
									<Val>10000</Val>
								</DAI>
								<DAI name="offDur">
									<Val>0</Val>
								</DAI>
								<DAI name="numPls">
									<Val>1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="BlkOpn" desc="Block opening">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="BlkCls" desc="Block closing">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="SwTyp" desc="Switching-device type">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="J:Onboard Ethernet" inst="Mod1">
					<Private type="Siemens-MasterId">ddc5c209-b581-440a-a631-4a3a29d474e0</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="Mod1/LLN0/LLN0">
						<Private type="Siemens-MasterId">61662f07-ff0d-4b27-9962-8df59d4b720a</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@Application</Val>
							</DAI>
						</DOI>
					</LN0>
				</LDevice>
				<LDevice desc="J:Onboard Ethernet_Chan.1" inst="Mod1_Channel1">
					<Private type="Siemens-MasterId">7d1183b7-bc96-4f65-a90e-54cf4c7f0e18</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="Mod1_Channel1/LLN0/LLN0">
						<Private type="Siemens-MasterId">152036a5-8b7c-4e62-8884-5ea05bdc203a</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@Mod1</Val>
							</DAI>
						</DOI>
					</LN0>
				</LDevice>
				<LDevice desc="E:ETH-BA-2EL" inst="Mod2">
					<Private type="Siemens-MasterId">494dc950-a06f-462c-888e-6a2b97236d68</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="Mod2/LLN0/LLN0">
						<Private type="Siemens-MasterId">f7a4bf92-7b45-4abf-9e8e-71ce52738e81</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@Application</Val>
							</DAI>
						</DOI>
					</LN0>
				</LDevice>
				<LDevice desc="E:ETH-BA-2EL_Chan.1" inst="Mod2_Channel1">
					<Private type="Siemens-MasterId">cd03ebd0-dcfe-4985-abd7-4e765b54c8c8</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="Mod2_Channel1/LLN0/LLN0">
						<Private type="Siemens-MasterId">95e2d0a5-860a-4038-a96a-9e80226f02c2</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@Mod2</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="Line_" lnClass="LCCH" inst="1" lnType="SIPROTEC5_LNType_LCCH_LineMode" desc="Line Mode">
						<Private type="Siemens-MasterId">8e282aba-f623-43f2-8e9a-7a9a8558155a</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="ChLiv" desc="Channel Live">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="RedChLiv" desc="Redund. Channel Live">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="" lnClass="LCCH" inst="1" lnType="SIPROTEC5_LNType_LCCH_61850" desc="IEC 61850-8-1">
						<Private type="Siemens-MasterId">1715d4db-332e-4b6b-9403-4a71220c2546</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 13:22:19</Val>
							</DAI>
						</DOI>
						<DOI name="ChLiv" desc="Channel Live">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="" lnClass="LCCH" inst="2" lnType="SIPROTEC5_LNType_LCCH_61850" desc="SNTP">
						<Private type="Siemens-MasterId">81decd75-28aa-432c-8560-63c2ccf9e726</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 13:22:19</Val>
							</DAI>
						</DOI>
						<DOI name="ChLiv" desc="Channel Live">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="" lnClass="LCCH" inst="3" lnType="SIPROTEC5_LNType_LCCH_61850" desc="SNMP">
						<Private type="Siemens-MasterId">c98ea80f-2f4e-4ed7-995a-81f571a62102</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 13:22:19</Val>
							</DAI>
						</DOI>
						<DOI name="ChLiv" desc="Channel Live">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="LCCH" inst="4" lnType="SIPROTEC5_LNType_LCCH_61850" desc="IEEE 1588" prefix="">
						<Private type="Siemens-MasterId">f71bca52-a1cc-4ded-b007-925593b23913</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 12:57:02</Val>
							</DAI>
						</DOI>
						<DOI name="ChLiv" desc="Channel Live">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="PowS" inst="PowS">
					<Private type="Siemens-MasterId">f4d4f91d-0b8b-44cc-94ff-476365f7c3df</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="PowS/LLN0/LLN0">
						<Private type="Siemens-MasterId">c5f4e5e1-82b5-4a95-a00d-b66b15b0fd1e</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@Application</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="" lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_ResetLed" desc="General">
						<Private type="Siemens-MasterId">cfec091e-3304-47a5-9c7f-6bc2487ff6e6</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="PowS_MPI3p1" inst="PowS_MeasPointI3ph1">
					<Private type="Siemens-MasterId">3146e95c-fb42-4d9f-96e6-04f0bdb85ddf</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="PowS_MeasPointI3ph1/LLN0/LLN0">
						<Private type="Siemens-MasterId">67ff4072-b2b6-4652-b091-fca4cffa6bd5</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@PowS</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="CT3P_" lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_ResetLed" desc="CT 3-phase">
						<Private type="Siemens-MasterId">8ecbe2dd-8051-46da-a86f-b9c1363cc778</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="TCTR" inst="1" lnType="SIPROTEC5_LNType_TCTR" desc="CT 1">
						<Private type="Siemens-MasterId">db065c2d-f6e8-4073-b91b-7a2ee3e95ea5</Private>
						<DOI name="Mod" desc="Mode (status only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="lnNs">
								<Val>IEC 61869-9:2016A</Val>
							</DAI>
						</DOI>
						<DOI name="ARtg" desc="Rated primary current">
							<SDI name="setMag">
								<DAI name="f">
									<Val>300</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>A</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>1</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>100000</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Rat" desc="Rat">
							<SDI name="setMag">
								<DAI name="f">
									<Val>300</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="HzRtg" desc="Rated frequency">
							<SDI name="setMag">
								<DAI name="f">
									<Val>50</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>Hz</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>16.67</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>60</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Cor" desc="Magnitude correction">
							<SDI name="setMag">
								<DAI name="f">
									<Val>1</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.001</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="AmpSv" desc="Sampled val. current">
							<SDI name="instMag">
								<DAI name="i" valKind="Conf" />
							</SDI>
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>A</Val>
								</DAI>
							</SDI>
							<SDI name="sVC">
								<DAI name="scaleFactor">
									<Val>0.001</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Trp" desc="Transient perform. class">
							<DAI name="setVal">
								<Val>TPS</Val>
							</DAI>
						</DOI>
						<DOI name="ScndTmms" desc="Second. loop time const.">
							<DAI name="setVal">
								<Val>210</Val>
							</DAI>
							<DAI name="minVal">
								<Val>1</Val>
							</DAI>
							<DAI name="maxVal">
								<Val>2147483647</Val>
							</DAI>
						</DOI>
						<DOI name="Clip" desc="Ratio of clipping limit">
							<SDI name="setMag">
								<DAI name="f">
									<Val>100</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>100</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="AccMeas" desc="Meas. accuracy class">
							<DAI name="setVal">
								<Val>0.2S</Val>
							</DAI>
						</DOI>
						<DOI name="AccPro" desc="Prot. accuracy class">
							<DAI name="setVal">
								<Val>1</Val>
							</DAI>
						</DOI>
						<DOI name="HoldTmms" desc="Holdover time">
							<DAI name="setVal">
								<Val>1000</Val>
							</DAI>
							<DAI name="minVal">
								<Val>500</Val>
							</DAI>
							<DAI name="maxVal">
								<Val>90000</Val>
							</DAI>
						</DOI>
						<DOI name="NamAccRtg" desc="NamAccRtg">
							<DAI name="val">
								<Val>0,5S/5P20</Val>
							</DAI>
						</DOI>
						<DOI name="NamARtg" desc="NamARtg">
							<DAI name="val">
								<Val>200;400;800</Val>
							</DAI>
						</DOI>
						<DOI name="NamClipRtg" desc="NamClipRtg">
							<DAI name="val">
								<Val>20</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="TCTR" inst="2" lnType="SIPROTEC5_LNType_TCTR" desc="CT 1">
						<Private type="Siemens-MasterId">6370ccb4-b74c-4efb-971f-afa54161cdc2</Private>
						<DOI name="Mod" desc="Mode (status only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="lnNs">
								<Val>IEC 61869-9:2016A</Val>
							</DAI>
						</DOI>
						<DOI name="ARtg" desc="Rated primary current">
							<SDI name="setMag">
								<DAI name="f">
									<Val>300</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>A</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>1</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>100000</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Rat" desc="Rat">
							<SDI name="setMag">
								<DAI name="f">
									<Val>300</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="HzRtg" desc="Rated frequency">
							<SDI name="setMag">
								<DAI name="f">
									<Val>50</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>Hz</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>16.67</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>60</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Cor" desc="Magnitude correction">
							<SDI name="setMag">
								<DAI name="f">
									<Val>1</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.001</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="AmpSv" desc="Sampled val. current">
							<SDI name="instMag">
								<DAI name="i" valKind="Conf" />
							</SDI>
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>A</Val>
								</DAI>
							</SDI>
							<SDI name="sVC">
								<DAI name="scaleFactor">
									<Val>0.001</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Trp" desc="Transient perform. class">
							<DAI name="setVal">
								<Val>TPS</Val>
							</DAI>
						</DOI>
						<DOI name="ScndTmms" desc="Second. loop time const.">
							<DAI name="setVal">
								<Val>210</Val>
							</DAI>
							<DAI name="minVal">
								<Val>1</Val>
							</DAI>
							<DAI name="maxVal">
								<Val>2147483647</Val>
							</DAI>
						</DOI>
						<DOI name="Clip" desc="Ratio of clipping limit">
							<SDI name="setMag">
								<DAI name="f">
									<Val>100</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>100</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="AccMeas" desc="Meas. accuracy class">
							<DAI name="setVal">
								<Val>0.2S</Val>
							</DAI>
						</DOI>
						<DOI name="AccPro" desc="Prot. accuracy class">
							<DAI name="setVal">
								<Val>1</Val>
							</DAI>
						</DOI>
						<DOI name="HoldTmms" desc="Holdover time">
							<DAI name="setVal">
								<Val>1000</Val>
							</DAI>
							<DAI name="minVal">
								<Val>500</Val>
							</DAI>
							<DAI name="maxVal">
								<Val>90000</Val>
							</DAI>
						</DOI>
						<DOI name="NamAccRtg" desc="NamAccRtg">
							<DAI name="val">
								<Val>0,5S/5P20</Val>
							</DAI>
						</DOI>
						<DOI name="NamARtg" desc="NamARtg">
							<DAI name="val">
								<Val>200;400;800</Val>
							</DAI>
						</DOI>
						<DOI name="NamClipRtg" desc="NamClipRtg">
							<DAI name="val">
								<Val>20</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="TCTR" inst="3" lnType="SIPROTEC5_LNType_TCTR" desc="CT 1">
						<Private type="Siemens-MasterId">f8b9b433-615b-49bb-a155-8f30ab5e041f</Private>
						<DOI name="Mod" desc="Mode (status only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="lnNs">
								<Val>IEC 61869-9:2016A</Val>
							</DAI>
						</DOI>
						<DOI name="ARtg" desc="Rated primary current">
							<SDI name="setMag">
								<DAI name="f">
									<Val>300</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>A</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>1</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>100000</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Rat" desc="Rat">
							<SDI name="setMag">
								<DAI name="f">
									<Val>300</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="HzRtg" desc="Rated frequency">
							<SDI name="setMag">
								<DAI name="f">
									<Val>50</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>Hz</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>16.67</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>60</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Cor" desc="Magnitude correction">
							<SDI name="setMag">
								<DAI name="f">
									<Val>1</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.001</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="AmpSv" desc="Sampled val. current">
							<SDI name="instMag">
								<DAI name="i" valKind="Conf" />
							</SDI>
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>A</Val>
								</DAI>
							</SDI>
							<SDI name="sVC">
								<DAI name="scaleFactor">
									<Val>0.001</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Trp" desc="Transient perform. class">
							<DAI name="setVal">
								<Val>TPS</Val>
							</DAI>
						</DOI>
						<DOI name="ScndTmms" desc="Second. loop time const.">
							<DAI name="setVal">
								<Val>210</Val>
							</DAI>
							<DAI name="minVal">
								<Val>1</Val>
							</DAI>
							<DAI name="maxVal">
								<Val>2147483647</Val>
							</DAI>
						</DOI>
						<DOI name="Clip" desc="Ratio of clipping limit">
							<SDI name="setMag">
								<DAI name="f">
									<Val>100</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>100</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="AccMeas" desc="Meas. accuracy class">
							<DAI name="setVal">
								<Val>0.2S</Val>
							</DAI>
						</DOI>
						<DOI name="AccPro" desc="Prot. accuracy class">
							<DAI name="setVal">
								<Val>1</Val>
							</DAI>
						</DOI>
						<DOI name="HoldTmms" desc="Holdover time">
							<DAI name="setVal">
								<Val>1000</Val>
							</DAI>
							<DAI name="minVal">
								<Val>500</Val>
							</DAI>
							<DAI name="maxVal">
								<Val>90000</Val>
							</DAI>
						</DOI>
						<DOI name="NamAccRtg" desc="NamAccRtg">
							<DAI name="val">
								<Val>0,5S/5P20</Val>
							</DAI>
						</DOI>
						<DOI name="NamARtg" desc="NamARtg">
							<DAI name="val">
								<Val>200;400;800</Val>
							</DAI>
						</DOI>
						<DOI name="NamClipRtg" desc="NamClipRtg">
							<DAI name="val">
								<Val>20</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="TCTR" inst="4" lnType="SIPROTEC5_LNType_TCTR" desc="CT 1">
						<Private type="Siemens-MasterId">b3a5c9cc-cd90-4ff4-a14d-f7991a6c08c5</Private>
						<DOI name="Mod" desc="Mode (status only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="lnNs">
								<Val>IEC 61869-9:2016A</Val>
							</DAI>
						</DOI>
						<DOI name="ARtg" desc="Rated primary current">
							<SDI name="setMag">
								<DAI name="f">
									<Val>300</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>A</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>1</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>100000</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Rat" desc="Rat">
							<SDI name="setMag">
								<DAI name="f">
									<Val>300</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="HzRtg" desc="Rated frequency">
							<SDI name="setMag">
								<DAI name="f">
									<Val>50</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>Hz</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>16.67</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>60</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Cor" desc="Magnitude correction">
							<SDI name="setMag">
								<DAI name="f">
									<Val>1</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.001</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="AmpSv" desc="Sampled val. current">
							<SDI name="instMag">
								<DAI name="i" valKind="Conf" />
							</SDI>
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>A</Val>
								</DAI>
							</SDI>
							<SDI name="sVC">
								<DAI name="scaleFactor">
									<Val>0.001</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Trp" desc="Transient perform. class">
							<DAI name="setVal">
								<Val>TPS</Val>
							</DAI>
						</DOI>
						<DOI name="ScndTmms" desc="Second. loop time const.">
							<DAI name="setVal">
								<Val>210</Val>
							</DAI>
							<DAI name="minVal">
								<Val>1</Val>
							</DAI>
							<DAI name="maxVal">
								<Val>2147483647</Val>
							</DAI>
						</DOI>
						<DOI name="Clip" desc="Ratio of clipping limit">
							<SDI name="setMag">
								<DAI name="f">
									<Val>100</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>100</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="AccMeas" desc="Meas. accuracy class">
							<DAI name="setVal">
								<Val>0.2S</Val>
							</DAI>
						</DOI>
						<DOI name="AccPro" desc="Prot. accuracy class">
							<DAI name="setVal">
								<Val>1</Val>
							</DAI>
						</DOI>
						<DOI name="HoldTmms" desc="Holdover time">
							<DAI name="setVal">
								<Val>1000</Val>
							</DAI>
							<DAI name="minVal">
								<Val>500</Val>
							</DAI>
							<DAI name="maxVal">
								<Val>90000</Val>
							</DAI>
						</DOI>
						<DOI name="NamAccRtg" desc="NamAccRtg">
							<DAI name="val">
								<Val>0,5S/5P20</Val>
							</DAI>
						</DOI>
						<DOI name="NamARtg" desc="NamARtg">
							<DAI name="val">
								<Val>200;400;800</Val>
							</DAI>
						</DOI>
						<DOI name="NamClipRtg" desc="NamClipRtg">
							<DAI name="val">
								<Val>20</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="TR_" lnClass="SBWI" inst="1" lnType="SIPROTEC5_LNType_SBWS_BW_Tr" desc="Brk.wire det.">
						<Private type="Siemens-MasterId">0f90b1d5-36ce-4b06-a13b-23b075c125e2</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="I_" lnClass="SSYM" inst="1" lnType="SIPROTEC5_LNType_SSYM_CurBalSV" desc="Supv. balan. I">
						<Private type="Siemens-MasterId">9f09f273-d17e-40d4-9d38-9c9d86fe3165</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="I_" lnClass="SPSQ" inst="1" lnType="SIPROTEC5_LNType_SPSQ_CurPhSeqSV" desc="Supv. ph.seq.I">
						<Private type="Siemens-MasterId">6534feb7-f5b0-4ec2-b37c-b7e76b01c071</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="I_" lnClass="SSUM" inst="1" lnType="SIPROTEC5_LNType_SSUM_SlowCurSumSV" desc="Supv. sum I">
						<Private type="Siemens-MasterId">acc455cb-c0b9-4af9-bdc2-df07ee696101</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="ISUM_" lnClass="SADC" inst="1" lnType="SIPROTEC5_LNType_SADC_FastCurSumSV" desc="Supv.ADC sum I">
						<Private type="Siemens-MasterId">9d178fb8-5a83-4c7a-8d16-be0664ada807</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="PowS_MPV3p1" inst="PowS_MeasPointV3ph1">
					<Private type="Siemens-MasterId">5e5abda9-0060-4731-8caa-8055f9e9c75e</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="PowS_MeasPointV3ph1/LLN0/LLN0">
						<Private type="Siemens-MasterId">2cce5129-25a7-4b34-b597-08fd2a574a40</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@PowS</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="VT3P_" lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_ResetLed" desc="VT 3-phase">
						<Private type="Siemens-MasterId">ec918ad4-9a71-4ff0-824a-a9ab994ffa6f</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="TVTR" inst="1" lnType="SIPROTEC5_LNType_TVTR" desc="VT 1">
						<Private type="Siemens-MasterId">2d2ce124-9df2-403e-bff3-16001078fd2d</Private>
						<DOI name="Mod" desc="Mode (status only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="lnNs">
								<Val>IEC 61869-9:2016A</Val>
							</DAI>
						</DOI>
						<DOI name="VolSv" desc="Sampled val. voltage">
							<SDI name="instMag">
								<DAI name="i" valKind="Conf" />
							</SDI>
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>V</Val>
								</DAI>
							</SDI>
							<SDI name="sVC">
								<DAI name="scaleFactor">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="VRtg" desc="Rated primary voltage">
							<SDI name="setMag">
								<DAI name="f">
									<Val>110</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>V</Val>
								</DAI>
								<DAI name="multiplier">
									<Val>k</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>0.2</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>1200</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="HzRtg" desc="Rated frequency">
							<SDI name="setMag">
								<DAI name="f">
									<Val>50</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>Hz</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>16.67</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>60</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Rat" desc="Rat">
							<SDI name="setMag">
								<DAI name="f">
									<Val>1100</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Cor" desc="Magnitude correction">
							<SDI name="setMag">
								<DAI name="f">
									<Val>1</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.001</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Clip" desc="Ratio of clipping limit">
							<SDI name="setMag">
								<DAI name="f">
									<Val>2</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>100</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="AccMeas" desc="Meas. accuracy class">
							<DAI name="setVal">
								<Val>0.2S</Val>
							</DAI>
						</DOI>
						<DOI name="AccPro" desc="Prot. accuracy class">
							<DAI name="setVal">
								<Val>1</Val>
							</DAI>
						</DOI>
						<DOI name="HoldTmms" desc="Holdover time">
							<DAI name="setVal">
								<Val>1000</Val>
							</DAI>
							<DAI name="minVal">
								<Val>500</Val>
							</DAI>
							<DAI name="maxVal">
								<Val>90000</Val>
							</DAI>
						</DOI>
						<DOI name="NamAccRtg" desc="NamAccRtg">
							<DAI name="val">
								<Val>0,5/3P</Val>
							</DAI>
						</DOI>
						<DOI name="NamVRtg" desc="NamVRtg">
							<DAI name="val">
								<Val>173000</Val>
							</DAI>
						</DOI>
						<DOI name="NamClipRtg" desc="NamClipRtg">
							<DAI name="val">
								<Val>2</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="TVTR" inst="2" lnType="SIPROTEC5_LNType_TVTR" desc="VT 1">
						<Private type="Siemens-MasterId">8c103274-b63e-4ae9-9626-a9b945183795</Private>
						<DOI name="Mod" desc="Mode (status only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="lnNs">
								<Val>IEC 61869-9:2016A</Val>
							</DAI>
						</DOI>
						<DOI name="VolSv" desc="Sampled val. voltage">
							<SDI name="instMag">
								<DAI name="i" valKind="Conf" />
							</SDI>
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>V</Val>
								</DAI>
							</SDI>
							<SDI name="sVC">
								<DAI name="scaleFactor">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="VRtg" desc="Rated primary voltage">
							<SDI name="setMag">
								<DAI name="f">
									<Val>110</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>V</Val>
								</DAI>
								<DAI name="multiplier">
									<Val>k</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>0.2</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>1200</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="HzRtg" desc="Rated frequency">
							<SDI name="setMag">
								<DAI name="f">
									<Val>50</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>Hz</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>16.67</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>60</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Rat" desc="Rat">
							<SDI name="setMag">
								<DAI name="f">
									<Val>1100</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Cor" desc="Magnitude correction">
							<SDI name="setMag">
								<DAI name="f">
									<Val>1</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.001</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Clip" desc="Ratio of clipping limit">
							<SDI name="setMag">
								<DAI name="f">
									<Val>2</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>100</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="AccMeas" desc="Meas. accuracy class">
							<DAI name="setVal">
								<Val>0.2S</Val>
							</DAI>
						</DOI>
						<DOI name="AccPro" desc="Prot. accuracy class">
							<DAI name="setVal">
								<Val>1</Val>
							</DAI>
						</DOI>
						<DOI name="HoldTmms" desc="Holdover time">
							<DAI name="setVal">
								<Val>1000</Val>
							</DAI>
							<DAI name="minVal">
								<Val>500</Val>
							</DAI>
							<DAI name="maxVal">
								<Val>90000</Val>
							</DAI>
						</DOI>
						<DOI name="NamAccRtg" desc="NamAccRtg">
							<DAI name="val">
								<Val>0,5/3P</Val>
							</DAI>
						</DOI>
						<DOI name="NamVRtg" desc="NamVRtg">
							<DAI name="val">
								<Val>173000</Val>
							</DAI>
						</DOI>
						<DOI name="NamClipRtg" desc="NamClipRtg">
							<DAI name="val">
								<Val>2</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="TVTR" inst="3" lnType="SIPROTEC5_LNType_TVTR" desc="VT 1">
						<Private type="Siemens-MasterId">6dfa624e-48fe-46fe-97ae-5e2d2958ba81</Private>
						<DOI name="Mod" desc="Mode (status only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="lnNs">
								<Val>IEC 61869-9:2016A</Val>
							</DAI>
						</DOI>
						<DOI name="VolSv" desc="Sampled val. voltage">
							<SDI name="instMag">
								<DAI name="i" valKind="Conf" />
							</SDI>
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>V</Val>
								</DAI>
							</SDI>
							<SDI name="sVC">
								<DAI name="scaleFactor">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="VRtg" desc="Rated primary voltage">
							<SDI name="setMag">
								<DAI name="f">
									<Val>110</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>V</Val>
								</DAI>
								<DAI name="multiplier">
									<Val>k</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>0.2</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>1200</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="HzRtg" desc="Rated frequency">
							<SDI name="setMag">
								<DAI name="f">
									<Val>50</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>Hz</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>16.67</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>60</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Rat" desc="Rat">
							<SDI name="setMag">
								<DAI name="f">
									<Val>1100</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Cor" desc="Magnitude correction">
							<SDI name="setMag">
								<DAI name="f">
									<Val>1</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.001</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Clip" desc="Ratio of clipping limit">
							<SDI name="setMag">
								<DAI name="f">
									<Val>2</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>100</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="AccMeas" desc="Meas. accuracy class">
							<DAI name="setVal">
								<Val>0.2S</Val>
							</DAI>
						</DOI>
						<DOI name="AccPro" desc="Prot. accuracy class">
							<DAI name="setVal">
								<Val>1</Val>
							</DAI>
						</DOI>
						<DOI name="HoldTmms" desc="Holdover time">
							<DAI name="setVal">
								<Val>1000</Val>
							</DAI>
							<DAI name="minVal">
								<Val>500</Val>
							</DAI>
							<DAI name="maxVal">
								<Val>90000</Val>
							</DAI>
						</DOI>
						<DOI name="NamAccRtg" desc="NamAccRtg">
							<DAI name="val">
								<Val>0,5/3P</Val>
							</DAI>
						</DOI>
						<DOI name="NamVRtg" desc="NamVRtg">
							<DAI name="val">
								<Val>173000</Val>
							</DAI>
						</DOI>
						<DOI name="NamClipRtg" desc="NamClipRtg">
							<DAI name="val">
								<Val>2</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="TVTR" inst="4" lnType="SIPROTEC5_LNType_TVTR" desc="VT 1">
						<Private type="Siemens-MasterId">67b4975b-0c16-42f6-82d0-17108ad86209</Private>
						<DOI name="Mod" desc="Mode (status only)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="lnNs">
								<Val>IEC 61869-9:2016A</Val>
							</DAI>
						</DOI>
						<DOI name="VolSv" desc="Sampled val. voltage">
							<SDI name="instMag">
								<DAI name="i" valKind="Conf" />
							</SDI>
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>V</Val>
								</DAI>
							</SDI>
							<SDI name="sVC">
								<DAI name="scaleFactor">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="VRtg" desc="Rated primary voltage">
							<SDI name="setMag">
								<DAI name="f">
									<Val>110</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>V</Val>
								</DAI>
								<DAI name="multiplier">
									<Val>k</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>0.2</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>1200</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="HzRtg" desc="Rated frequency">
							<SDI name="setMag">
								<DAI name="f">
									<Val>50</Val>
								</DAI>
							</SDI>
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>Hz</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>16.67</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>60</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Rat" desc="Rat">
							<SDI name="setMag">
								<DAI name="f">
									<Val>635.838135</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.1</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Cor" desc="Magnitude correction">
							<SDI name="setMag">
								<DAI name="f">
									<Val>1</Val>
								</DAI>
							</SDI>
							<SDI name="minVal">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>10</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.001</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="Clip" desc="Ratio of clipping limit">
							<SDI name="setMag">
								<DAI name="f">
									<Val>2</Val>
								</DAI>
							</SDI>
							<SDI name="maxVal">
								<DAI name="f">
									<Val>100</Val>
								</DAI>
							</SDI>
							<SDI name="stepSize">
								<DAI name="f">
									<Val>0.01</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="AccMeas" desc="Meas. accuracy class">
							<DAI name="setVal">
								<Val>0.2S</Val>
							</DAI>
						</DOI>
						<DOI name="AccPro" desc="Prot. accuracy class">
							<DAI name="setVal">
								<Val>1</Val>
							</DAI>
						</DOI>
						<DOI name="HoldTmms" desc="Holdover time">
							<DAI name="setVal">
								<Val>1000</Val>
							</DAI>
							<DAI name="minVal">
								<Val>500</Val>
							</DAI>
							<DAI name="maxVal">
								<Val>90000</Val>
							</DAI>
						</DOI>
						<DOI name="NamAccRtg" desc="NamAccRtg">
							<DAI name="val">
								<Val>0,5/3P</Val>
							</DAI>
						</DOI>
						<DOI name="NamVRtg" desc="NamVRtg">
							<DAI name="val">
								<Val>173000</Val>
							</DAI>
						</DOI>
						<DOI name="NamClipRtg" desc="NamClipRtg">
							<DAI name="val">
								<Val>2</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="U_" lnClass="SSYM" inst="1" lnType="SIPROTEC5_LNType_SSYM_CurBalSV" desc="Supv. balan. V">
						<Private type="Siemens-MasterId">2919eb40-b6a4-43df-873b-a3d3cc9cd347</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="U_" lnClass="SPSQ" inst="1" lnType="SIPROTEC5_LNType_SPSQ_CurPhSeqSV" desc="Supv. ph.seq.V">
						<Private type="Siemens-MasterId">1d70b9b7-4880-48d2-ae85-d90191a5a85f</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="U_" lnClass="SSUM" inst="1" lnType="SIPROTEC5_LNType_SSUM_SlowCurSumSV" desc="Supv. sum V">
						<Private type="Siemens-MasterId">753fcea7-e9d8-4699-853c-8581fddfec4a</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="VTCB_" lnClass="SFFM" inst="1" lnType="SIPROTEC5_LNType_SFFM_SMCB" desc="VT miniatureCB">
						<Private type="Siemens-MasterId">33409137-86c7-4bbb-955a-1a9db1b504ef</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="Rec" inst="Rec">
					<Private type="Siemens-MasterId">07dfe484-4c60-44aa-be6d-5db08117f2bf</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="Rec/LLN0/LLN0">
						<Private type="Siemens-MasterId">388c4873-03d4-4207-84aa-c698b2a19090</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@Application</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="RCDG_" lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_ResetLed" desc="General">
						<Private type="Siemens-MasterId">b660acbc-37a1-420f-8899-7cfdeb8cbd6a</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="GFLG_" lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_ResetLed" desc="Grnd.-flt log">
						<Private type="Siemens-MasterId">d2961bde-9383-4f35-9a8c-1105905cebcb</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="Rec_FltRec" inst="Rec_FaultRecorder">
					<Private type="Siemens-MasterId">50ac9b3c-d9ae-4174-b5ff-3be57c648840</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="Rec_FaultRecorder/LLN0/LLN0">
						<Private type="Siemens-MasterId">49508ca1-b210-486f-8f2a-27f0ab6d79dd</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@Rec</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="RCDR_" lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_ResetLed" desc="General">
						<Private type="Siemens-MasterId">64598a82-10d7-465c-973a-c365db8b4a24</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="DEF_" lnClass="RDRE" inst="1" lnType="SIPROTEC5_LNType_RDRE_DEF" desc="Control">
						<Private type="Siemens-MasterId">f3cf96a9-8ae5-4313-83f7-9f3fc6c1dc9f</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="RcdTrg" desc="Start record">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="MemRs" desc="Reset memory">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="operTimeout" valKind="Conf">
								<Val>30000</Val>
							</DAI>
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="MemClr" desc="Clear memory">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="operTimeout" valKind="Conf">
								<Val>30000</Val>
							</DAI>
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="RcdMade" desc="Record made">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="FltNum" desc="Fault number">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="RcdStr" desc="Recording started">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="VI3p1" inst="VI3p1">
					<Private type="Siemens-MasterId">3c1523bb-beb2-4ca9-bf15-c6f56985f853</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="VI3p1/LLN0/LLN0">
						<Private type="Siemens-MasterId">cb15d6fc-195f-4a53-8c40-67016bae41b3</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@Application</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="VI3P_" lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_ResetLed" desc="General">
						<Private type="Siemens-MasterId">30d00dc2-3606-4ef5-811a-9c1729c2df74</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="PTRC" inst="1" lnType="SIPROTEC5_LNType_PTRC_FG_Line_3ph" desc="Group indicat.">
						<Private type="Siemens-MasterId">08d942d6-f0ea-45d0-9e7d-0f0c795d04d4</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="neut" valKind="Conf" />
							<DAI name="dirNeut" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="CF_" lnClass="SBWI" inst="1" lnType="SIPROTEC5_LNType_SBWS_BW_Tr" desc="Brk.wire conf">
						<Private type="Siemens-MasterId">e10378c3-dc0f-4e09-b557-fc73a5b1c04c</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="RSLED" lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_ResetLed" desc="Reset LED Group">
						<Private type="Siemens-MasterId">bd11496c-99e0-4471-977a-a01d35485f8b</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="" lnClass="PHAR" inst="1" lnType="SIPROTEC5_LNType_PHAR" desc="Inrush detect.">
						<Private type="Siemens-MasterId">5a955255-deea-49d0-956d-087c9b659fdb</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="neut" valKind="Conf" />
							<DAI name="dirNeut" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="OCGI" lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_OC_Group_Indication" desc="OC group ind.">
						<Private type="Siemens-MasterId">b56c1c5b-6ed3-40df-9820-56546bddc689</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="neut" valKind="Conf" />
							<DAI name="dirNeut" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="neut" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="VI3p1_51N-B1" inst="VI3p1_5051NOCgndB1">
					<Private type="Siemens-MasterId">cf8cdf93-0611-420a-836d-906d41168cd8</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="VI3p1_5051NOCgndB1/LLN0/LLN0">
						<Private type="Siemens-MasterId">bf557f1a-4ad6-46d8-96a9-591efeff25d5</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@VI3p1</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="" lnClass="PTRC" inst="1" lnType="SIPROTEC5_LNType_PTRC_FN_Str_NonPhsSel_Without_DirRouting_Op_3pol" desc="Group indicat.">
						<Private type="Siemens-MasterId">8a5933d1-b9fb-4604-bf25-15d972b8df2d</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="ND_" lnClass="PTOC" inst="1" lnType="SIPROTEC5_LNType_PTOC_Gnd_DOCP_Bas" desc="Definite-T 1">
						<Private type="Siemens-MasterId">5ec2b36d-e152-44df-aff1-fa04bba216f6</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="ND_" lnClass="PTOC" inst="2" lnType="SIPROTEC5_LNType_PTOC_Gnd_DOCP_Bas" desc="Definite-T 1">
						<Private type="Siemens-MasterId">084b265f-21e1-4c9a-a47f-cbb15029aba0</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="NI_" lnClass="PTOC" inst="1" lnType="SIPROTEC5_LNType_PTOC_Gnd_DOCP_Bas" desc="Inverse-T 1">
						<Private type="Siemens-MasterId">b141b8fb-3d39-4a00-9fed-538f7535f66a</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="VI3p1_51-B 1" inst="VI3p1_5051OC3phase1">
					<Private type="Siemens-MasterId">80f79f91-c61b-4cd3-b9df-da83ee7ed8f9</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="VI3p1_5051OC3phase1/LLN0/LLN0">
						<Private type="Siemens-MasterId">e7f48ace-78a3-45d3-98b5-456cca94988d</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@VI3p1</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="" lnClass="PTRC" inst="1" lnType="SIPROTEC5_LNType_PTRC_FN_Str_GABC_Without_DirRouting_Op_3pol" desc="Group indicat.">
						<Private type="Siemens-MasterId">b5c4a5d1-dc1b-41f0-9eed-f8cec040baaf</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="ID_" lnClass="PTOC" inst="1" lnType="SIPROTEC5_LNType_PTOC_3ph_DOCP_3pol_Bas" desc="Definite-T 1">
						<Private type="Siemens-MasterId">2cdcc6ae-8d28-4a14-9b6d-72b3a7733dc7</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="ID_" lnClass="PTOC" inst="2" lnType="SIPROTEC5_LNType_PTOC_3ph_DOCP_3pol_Bas" desc="Definite-T 1">
						<Private type="Siemens-MasterId">f8413b56-4ee7-4e3a-bde4-3cd829b35fc3</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN prefix="II_" lnClass="PTOC" inst="1" lnType="SIPROTEC5_LNType_PTOC_3ph_DOCP_3pol_Bas" desc="Inverse-T 1">
						<Private type="Siemens-MasterId">d69d0759-b85d-403f-a22a-b7c1373db4c4</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="VI3p1_Energ" inst="VI3p1_Energy">
					<Private type="Siemens-MasterId">5b12b084-6248-4837-8bed-38a1a861e588</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="VI3p1_Energy/LLN0/LLN0">
						<Private type="Siemens-MasterId">bff4f836-e6b3-42c6-9ae1-86b82d3fb4de</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@VI3p1</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="XPRE_" lnClass="MMTR" inst="1" lnType="SIPROTEC5_LNType_MMTR_OpMeas_Energy_3ph" desc="Energy">
						<Private type="Siemens-MasterId">1f59d0dd-d1d5-42c0-975d-a7cd29757145</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="SupWh" desc="Wp+">
							<DAI name="actVal" valKind="Conf" />
							<DAI name="frVal" valKind="Conf" />
							<DAI name="frTm" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>Wh</Val>
								</DAI>
								<DAI name="multiplier">
									<Val>M</Val>
								</DAI>
							</SDI>
							<DAI name="pulsQty">
								<Val>0.0115470048</Val>
							</DAI>
						</DOI>
						<DOI name="SupVArh" desc="Wq+">
							<DAI name="actVal" valKind="Conf" />
							<DAI name="frVal" valKind="Conf" />
							<DAI name="frTm" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>VArh</Val>
								</DAI>
								<DAI name="multiplier">
									<Val>M</Val>
								</DAI>
							</SDI>
							<DAI name="pulsQty">
								<Val>0.0115470048</Val>
							</DAI>
						</DOI>
						<DOI name="DmdWh" desc="Wp-">
							<DAI name="actVal" valKind="Conf" />
							<DAI name="frVal" valKind="Conf" />
							<DAI name="frTm" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>Wh</Val>
								</DAI>
								<DAI name="multiplier">
									<Val>M</Val>
								</DAI>
							</SDI>
							<DAI name="pulsQty">
								<Val>0.0115470048</Val>
							</DAI>
						</DOI>
						<DOI name="DmdVArh" desc="Wq-">
							<DAI name="actVal" valKind="Conf" />
							<DAI name="frVal" valKind="Conf" />
							<DAI name="frTm" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>VArh</Val>
								</DAI>
								<DAI name="multiplier">
									<Val>M</Val>
								</DAI>
							</SDI>
							<DAI name="pulsQty">
								<Val>0.0115470048</Val>
							</DAI>
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="VI3p1_FdSym" inst="VI3p1_FundSymComp">
					<Private type="Siemens-MasterId">54f3f005-4ce6-49e7-b632-8ccf9241dacb</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="VI3p1_FundSymComp/LLN0/LLN0">
						<Private type="Siemens-MasterId">03c8f869-d1ff-46af-9d87-d5bc2f2536d9</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@VI3p1</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="FPRE_" lnClass="MMXU" inst="1" lnType="SIPROTEC5_LNType_MMXU_OpMeas_Fund_3ph_Pres" desc="Fundam">
						<Private type="Siemens-MasterId">f410cd5f-e000-4b24-aa3e-831319aa5916</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="PPV" desc="Vpp">
							<SDI name="phsAB" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="phsBC" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="phsCA" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="PhV" desc="Vph">
							<SDI name="phsA" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="phsB" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="phsC" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="res" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>20000</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="A" desc="Iph">
							<SDI name="phsA" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>A</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="phsB" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>A</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="phsC" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>A</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="res" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>A</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>100000</Val>
								</DAI>
							</SDI>
						</DOI>
					</LN>
					<LN prefix="FPRE_" lnClass="MMXN" inst="1" lnType="SIPROTEC5_LNType_MMXN_OpMeas_Fund_1ph_Pres" desc="Fundam">
						<Private type="Siemens-MasterId">62c25952-eaae-4118-ac93-454dd3111508</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="XPRE_" lnClass="MSQI" inst="1" lnType="SIPROTEC5_LNType_MSQI_OpMeas_Symm_Pres" desc="Sy.co.">
						<Private type="Siemens-MasterId">e2b5d05f-b720-4161-840c-ae22b7fd59bd</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="SeqA" desc="Iseq">
							<SDI name="c1" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>A</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="c2" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>A</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="c3" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>A</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<DAI name="seqT" valKind="Conf" />
						</DOI>
						<DOI name="SeqV" desc="Vseq">
							<SDI name="c1" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="c2" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="c3" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<DAI name="seqT" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="VI3p1_OMV" inst="VI3p1_OperationalValues">
					<Private type="Siemens-MasterId">d5596b28-6ef3-4ed3-ab1a-1f62361677a8</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="VI3p1_OperationalValues/LLN0/LLN0">
						<Private type="Siemens-MasterId">43d810d4-0221-47fa-a10b-7091d49ffe61</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@VI3p1</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="RPRE_" lnClass="MMXU" inst="1" lnType="SIPROTEC5_LNType_MMXU_OpMeas_RMS_3ph_Pres" desc="RMS">
						<Private type="Siemens-MasterId">670f638e-f0a1-44b2-a5fe-5480ec4a52df</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="PPV" desc="Vpp">
							<SDI name="phsAB" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="phsBC" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="phsCA" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="PhV" desc="Vph">
							<SDI name="phsA" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="phsB" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="phsC" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>k</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>2000</Val>
								</DAI>
							</SDI>
							<SDI name="res" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>V</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>20000</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="A" desc="Iph">
							<SDI name="phsA" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>A</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="phsB" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>A</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="phsC" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>A</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="res" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>A</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>100000</Val>
								</DAI>
							</SDI>
						</DOI>
					</LN>
					<LN prefix="RPRE_" lnClass="MMXN" inst="1" lnType="SIPROTEC5_LNType_MMXN_OpMeas_Fund_1ph_Pres" desc="RMS">
						<Private type="Siemens-MasterId">4eb73eb5-8b36-415f-823e-7f0b97f55ed8</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="PPRE_" lnClass="MMXU" inst="1" lnType="SIPROTEC5_LNType_MMXU_OpMeas_Power_3ph_Pres" desc="Power">
						<Private type="Siemens-MasterId">11e45f53-767d-4281-b269-c1ae8e20a4c6</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
						<DOI name="TotW" desc="P tot">
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>W</Val>
								</DAI>
								<DAI name="multiplier">
									<Val>M</Val>
								</DAI>
							</SDI>
							<DAI name="db">
								<Val>10000</Val>
							</DAI>
						</DOI>
						<DOI name="TotVAr" desc="Q tot">
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>VAr</Val>
								</DAI>
								<DAI name="multiplier">
									<Val>M</Val>
								</DAI>
							</SDI>
							<DAI name="db">
								<Val>10000</Val>
							</DAI>
						</DOI>
						<DOI name="TotVA" desc="S tot">
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>VA</Val>
								</DAI>
								<DAI name="multiplier">
									<Val>M</Val>
								</DAI>
							</SDI>
							<DAI name="db">
								<Val>10000</Val>
							</DAI>
						</DOI>
						<DOI name="TotPF" desc="cosφ">
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>cos(phi)</Val>
								</DAI>
							</SDI>
							<DAI name="db">
								<Val>10000</Val>
							</DAI>
						</DOI>
						<DOI name="Hz" desc="f">
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="units">
								<DAI name="SIUnit">
									<Val>Hz</Val>
								</DAI>
							</SDI>
							<DAI name="db">
								<Val>100</Val>
							</DAI>
							<DAI name="dbRef">
								<Val>50</Val>
							</DAI>
						</DOI>
						<DOI name="W" desc="P">
							<SDI name="phsA" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>W</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>M</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="phsB" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>W</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>M</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="phsC" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>W</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>M</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="VAr" desc="Q">
							<SDI name="phsA" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>VAr</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>M</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="phsB" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>VAr</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>M</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="phsC" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>VAr</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>M</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
						</DOI>
						<DOI name="VA" desc="S">
							<SDI name="phsA" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>VA</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>M</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="phsB" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>VA</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>M</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
							<SDI name="phsC" desc="Vpp:AB">
								<DAI name="q" valKind="Conf" />
								<DAI name="t" valKind="Conf" />
								<SDI name="units">
									<DAI name="SIUnit">
										<Val>VA</Val>
									</DAI>
									<DAI name="multiplier">
										<Val>M</Val>
									</DAI>
								</SDI>
								<DAI name="db">
									<Val>10000</Val>
								</DAI>
							</SDI>
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="VI3p1_ProMon" inst="VI3p1_ProcessMonitor">
					<Private type="Siemens-MasterId">c399a6d9-ebc5-4bc2-8a2b-7142ddfbb34d</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="VI3p1_ProcessMonitor/LLN0/LLN0">
						<Private type="Siemens-MasterId">8882f4fe-d17c-461c-82fe-73f5c869d495</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@VI3p1</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN prefix="PROM_" lnClass="ROPA" inst="1" lnType="SIPROTEC5_LNType_ROPA_OpenPoleCurrent" desc="Curr.criterion">
						<Private type="Siemens-MasterId">bb40a20f-ea99-4cdf-b7a4-9beaa97c42db</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
					<LN prefix="PROM_" lnClass="RSSR" inst="1" lnType="SIPROTEC5_LNType_RSSR_SwitchingStateRecognitionBasic" desc="Closure detec.">
						<Private type="Siemens-MasterId">8b5766cf-fe29-4fc8-b59e-ec4e9356dd66</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-13 10:09:28</Val>
							</DAI>
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="Signali" inst="UD1">
					<Private type="Siemens-MasterId">710ab97c-75f3-48ac-aa9a-4e818c2faa2a</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="UD1/LLN0/LLN0">
						<Private type="Siemens-MasterId">3f8f6d66-10f7-4758-ab32-2114acff754b</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-15 11:42:42</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@Application</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_ResetLed_1" desc="Signali" prefix="RSLED">
						<Private type="Siemens-MasterId">07c52e46-ec8f-4b10-9c3d-9416f1d89607</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-15 11:42:42</Val>
							</DAI>
						</DOI>
						<DOI name="SPS" desc="VOD POD NAPONOM">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
							<DAI name="blkEna" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="VI3p1_27 1" inst="VI3p1_27Undervoltage1">
					<Private type="Siemens-MasterId">df6a13c5-cf56-4111-aa14-55099ccd3f37</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="VI3p1_27Undervoltage1/LLN0/LLN0">
						<Private type="Siemens-MasterId">b6cb6a8e-6e84-4445-8236-b03d1a3152ef</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@VI3p1</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_ResetLed" desc="General" prefix="">
						<Private type="Siemens-MasterId">5db794e0-f1e7-49ff-974a-ce5913316ce3</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
					</LN>
					<LN lnClass="PTRC" inst="1" lnType="SIPROTEC5_LNType_PTRC_FN_Str_GABC_Without_DirRouting_Op_3pol" desc="Group indicat." prefix="">
						<Private type="Siemens-MasterId">adfa7af2-f9a3-45d9-a59a-67921a8ff152</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTUV" inst="1" lnType="SIPROTEC5_LNType_PTUV" desc="Definite-T 1" prefix="">
						<Private type="Siemens-MasterId">a8ab5aa9-0969-4ce2-8e24-66c7329d3559</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTUV" inst="2" lnType="SIPROTEC5_LNType_PTUV" desc="Definite-T 1" prefix="">
						<Private type="Siemens-MasterId">de9e5c53-da73-4ec3-8bf8-9a3474906516</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="VI3p1_46 1" inst="VI3p1_46I21">
					<Private type="Siemens-MasterId">0291af32-8315-48fa-a7fb-5807469a007e</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="VI3p1_46I21/LLN0/LLN0">
						<Private type="Siemens-MasterId">0566fb79-1191-49d4-89f2-e03bda4a35ff</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@VI3p1</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_GAPC_FB0_NSP" desc="General" prefix="">
						<Private type="Siemens-MasterId">45387619-2749-4818-8ec9-4bbddd7d3294</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
					</LN>
					<LN lnClass="PTRC" inst="1" lnType="SIPROTEC5_LNType_PTRC_FN_Str_NonPhsSel_Without_DirRouting_Op_3pol" desc="Group indicat." prefix="">
						<Private type="Siemens-MasterId">7ee6d8b5-4f31-4923-8f8c-6d3d87fc8b93</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTOC" inst="1" lnType="SIPROTEC5_LNType_PTOC_Gnd_DOCP_Bas" desc="Definite-T 1" prefix="I2_">
						<Private type="Siemens-MasterId">6d6cd9e9-81cd-42f3-ba94-6f0947e0e8f9</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTOC" inst="2" lnType="SIPROTEC5_LNType_PTOC_Gnd_DOCP_Bas" desc="Definite-T 1" prefix="I2_">
						<Private type="Siemens-MasterId">635d81f2-5026-4936-8b51-6848ae6971db</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="VI3p1_51V1" inst="VI3p1_51VOC3phVdep1">
					<Private type="Siemens-MasterId">361afe6a-f57b-4c08-91fb-bb3f15fb81d5</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="VI3p1_51VOC3phVdep1/LLN0/LLN0">
						<Private type="Siemens-MasterId">8b22bf70-3693-4df5-93cf-f088dfc29531</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@VI3p1</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN lnClass="PTRC" inst="1" lnType="SIPROTEC5_LNType_PTRC_FN_Str_GABC_Without_DirRouting_Op_3pol" desc="Group indicat." prefix="">
						<Private type="Siemens-MasterId">44435f48-61b2-48ab-b4cd-f3dc5410cf6e</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PVOC" inst="1" lnType="SIPROTEC5_LNType_PVOC_3ph_IOCP_3pol_Vol_Dep_Threshold" desc="V-dependent 1" prefix="DEP_">
						<Private type="Siemens-MasterId">eaae1083-3fab-4808-bcc6-021e85995acf</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTOC" inst="1" lnType="SIPROTEC5_LNType_PTOC_3ph_DOCP_3pol_Bas" desc="V-seal-in 1" prefix="UVSI_">
						<Private type="Siemens-MasterId">1a61cf35-5103-4caa-b75c-9a80fec05821</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="VI3p1_59 1" inst="VI3p1_59Overvoltage1">
					<Private type="Siemens-MasterId">3d12e2d8-c210-48e9-b27d-c259dd034b15</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="VI3p1_59Overvoltage1/LLN0/LLN0">
						<Private type="Siemens-MasterId">8ef1beea-0eca-4b3c-9edd-ba705ba2527e</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@VI3p1</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN lnClass="PTRC" inst="1" lnType="SIPROTEC5_LNType_PTRC_FN_Str_GABC_Without_DirRouting_Op_3pol" desc="Group indicat." prefix="">
						<Private type="Siemens-MasterId">05cfa4a4-4e60-48a3-971d-1db1c70b359a</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTOV" inst="1" lnType="SIPROTEC5_LNType_PTOV" desc="Definite-T 1" prefix="">
						<Private type="Siemens-MasterId">c9559c6b-5aee-4dc2-864a-946fff47b5f5</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTOV" inst="2" lnType="SIPROTEC5_LNType_PTOV" desc="Definite-T 1" prefix="">
						<Private type="Siemens-MasterId">b5553e82-3c43-45a4-8572-619452454af0</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTRC" inst="2" lnType="SIPROTEC5_LNType_PTRC_FN_Str_NonPhsSel_Without_DirRouting_Op_3pol" desc="Group indicat." prefix="">
						<Private type="Siemens-MasterId">9787f4c3-dc72-4492-bdaf-56c14d3d5d56</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTOV" inst="1" lnType="SIPROTEC5_LNType_V0_PTOV" desc="Stage 1" prefix="V0x">
						<Private type="Siemens-MasterId">dd5f3b6d-61ac-4022-81be-1272f99dedd7</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="VI3p1_67-A1" inst="VI3p1_67DirOC3phA1">
					<Private type="Siemens-MasterId">83a4e767-ed7a-4cb5-8850-57229cb9b584</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="VI3p1_67DirOC3phA1/LLN0/LLN0">
						<Private type="Siemens-MasterId">d1b077db-2ccd-402a-8d81-e77e47ab86c3</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@VI3p1</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_GAPC_FB0_NSP" desc="General" prefix="">
						<Private type="Siemens-MasterId">cf07c07d-2750-446d-b506-aa24f94ca790</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
					</LN>
					<LN lnClass="PTRC" inst="1" lnType="SIPROTEC5_LNType_PTRC_FN_Str_GABC_Without_DirRouting_Op_3pol" desc="Group indicat." prefix="">
						<Private type="Siemens-MasterId">1231f0e3-91a7-4d7f-8fde-a500b015e861</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTOC" inst="1" lnType="SIPROTEC5_LNType_PTOC_3ph_DOCP_3pol_Bas" desc="Definite-T 1" prefix="DID_">
						<Private type="Siemens-MasterId">b9a87679-444f-4556-b510-c455547dd6f8</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTOC" inst="2" lnType="SIPROTEC5_LNType_PTOC_3ph_DOCP_3pol_Bas" desc="Definite-T 1" prefix="DID_">
						<Private type="Siemens-MasterId">3af45c63-5c69-462c-932d-d4e4a42486eb</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTOC" inst="1" lnType="SIPROTEC5_LNType_PTOC_3ph_DOCP_3pol_Bas" desc="Inverse-T 1" prefix="DII_">
						<Private type="Siemens-MasterId">7eacc6c1-76d3-4043-a588-c62cf6959c43</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="phsA" valKind="Conf" />
							<DAI name="dirPhsA" valKind="Conf" />
							<DAI name="phsB" valKind="Conf" />
							<DAI name="dirPhsB" valKind="Conf" />
							<DAI name="phsC" valKind="Conf" />
							<DAI name="dirPhsC" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="VI3p1_81OA 1" inst="VI3p1_81OverfrequA1">
					<Private type="Siemens-MasterId">e5adf01e-44db-44ac-9266-b147cb5aad03</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="VI3p1_81OverfrequA1/LLN0/LLN0">
						<Private type="Siemens-MasterId">2d318df1-1a4c-4636-b069-81696aad311c</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@VI3p1</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_ResetLed" desc="General" prefix="POFA_">
						<Private type="Siemens-MasterId">50321733-4b22-42b9-ab3c-9b900a2d1485</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Operate">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
					</LN>
					<LN lnClass="PTRC" inst="1" lnType="SIPROTEC5_LNType_PTRC_FN_Str_NonPhsSel_Without_DirRouting_Op_3pol" desc="Group indicat." prefix="">
						<Private type="Siemens-MasterId">dca5e268-7df5-4991-89bd-72323a104c71</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTOF" inst="1" lnType="SIPROTEC5_LNType_PTOF" desc="Stage 1" prefix="A_">
						<Private type="Siemens-MasterId">8a6b5ff3-d8cd-459c-9921-5e4a606cff87</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTOF" inst="2" lnType="SIPROTEC5_LNType_PTOF" desc="Stage 1" prefix="A_">
						<Private type="Siemens-MasterId">34bf8e1c-fb80-44ae-b1b1-d88e083717bd</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
				<LDevice desc="VI3p1_81UA 1" inst="VI3p1_81UnderfrequA1">
					<Private type="Siemens-MasterId">5d51f45c-dd23-43a4-aa54-3f3c867c74e9</Private>
					<LN0 lnClass="LLN0" inst="" lnType="SIPROTEC5_LNType_LLN0_LDevice_Generic" desc="VI3p1_81UnderfrequA1/LLN0/LLN0">
						<Private type="Siemens-MasterId">51fefd1a-07e8-4d30-a08b-63a69290eda0</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
							<DAI name="ldNs">
								<Val>IEC 61850-7-4:2007B</Val>
							</DAI>
						</DOI>
						<DOI name="GrRef" desc="GrRef">
							<DAI name="setSrcRef">
								<Val>@VI3p1</Val>
							</DAI>
						</DOI>
					</LN0>
					<LN lnClass="GAPC" inst="1" lnType="SIPROTEC5_LNType_ResetLed" desc="General" prefix="PUFA_">
						<Private type="Siemens-MasterId">adb21061-060d-437e-96f4-6319548b8cb7</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Operate">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
					</LN>
					<LN lnClass="PTRC" inst="1" lnType="SIPROTEC5_LNType_PTRC_FN_Str_NonPhsSel_Without_DirRouting_Op_3pol" desc="Group indicat." prefix="">
						<Private type="Siemens-MasterId">a9e6b96f-5f03-44fc-aa49-ca0ff0a8af32</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTUF" inst="1" lnType="SIPROTEC5_LNType_PTUF" desc="Stage 1" prefix="A_">
						<Private type="Siemens-MasterId">27fa1de9-05f0-4548-ac01-5474f1111095</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTUF" inst="2" lnType="SIPROTEC5_LNType_PTUF" desc="Stage 1" prefix="A_">
						<Private type="Siemens-MasterId">93828a7c-d6ca-42bf-9376-9e3ede9e8052</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
					<LN lnClass="PTUF" inst="3" lnType="SIPROTEC5_LNType_PTUF" desc="Stage 1" prefix="A_">
						<Private type="Siemens-MasterId">dec1e190-288d-4adb-9b96-01d9079c2b3a</Private>
						<DOI name="Mod" desc="Mode (controllable)">
							<SDI name="origin">
								<DAI name="orCat" valKind="Conf" />
								<DAI name="orIdent" valKind="Conf" />
							</SDI>
							<DAI name="ctlNum" valKind="Conf" />
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<SDI name="Oper">
								<DAI name="ctlVal" valKind="Conf" />
								<SDI name="origin">
									<DAI name="orCat" valKind="Conf" />
									<DAI name="orIdent" valKind="Conf" />
								</SDI>
								<DAI name="ctlNum" valKind="Conf" />
								<DAI name="T" valKind="Conf" />
								<DAI name="Test" valKind="Conf" />
								<DAI name="Check" valKind="Conf" />
							</SDI>
						</DOI>
						<DOI name="Beh" desc="Behavior">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Health" desc="Health">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="NamPlt" desc="Name plate">
							<DAI name="configRev">
								<Val>2020-10-16 08:27:37</Val>
							</DAI>
						</DOI>
						<DOI name="Str" desc="Pickup">
							<DAI name="general" valKind="Conf" />
							<DAI name="dirGeneral" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Op" desc="Operate">
							<DAI name="general" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
						</DOI>
						<DOI name="Blk" desc="&gt;Block stage">
							<DAI name="stVal" valKind="Conf" />
							<DAI name="q" valKind="Conf" />
							<DAI name="t" valKind="Conf" />
							<DAI name="subEna" valKind="Conf" />
							<DAI name="subVal" valKind="Conf" />
							<DAI name="subQ" valKind="Conf" />
							<DAI name="subID" valKind="Conf" />
						</DOI>
					</LN>
				</LDevice>
			</Server>
		</AccessPoint>
	</IED>
	<DataTypeTemplates>
		<LNodeType id="SIPROTEC5_LNType_LLN0_Application" lnClass="LLN0">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_Test_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_LLN0_V08.03.03_V07.90.00" />
			<DO name="LEDRs" type="SIPROTEC5_DOType_SPC_dir_with_nor_sec_V08.03.03_V07.90.00" />
			<DO name="LocKey" type="SIPROTEC5_DOType_SPS_with_dataNs_V08.03.03_V07.90.00" />
			<DO name="LocSta" type="SIPROTEC5_DOType_SPC_dir_with_nor_sec_and_dataNs_V08.03.03_V07.90.00" />
			<DO name="MltLev" type="SIPROTEC5_DOType_SPG_readOnly_with_dataNs_V08.03.03_V07.90.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_LPHD" lnClass="LPHD">
			<DO name="PhyNam" type="SIPROTEC5_DOType_DPL_V08.03.03_V08.00.00" />
			<DO name="PhyHealth" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="Proxy" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
			<DO name="PwrUp" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
			<DO name="Sim" type="SIPROTEC5_DOType_SPC_controllable_V08.03.03_V07.90.00" />
			<DO name="OpTmh" type="SIPROTEC5_DOType_INS_INT32_with_units_V08.03.03_V08.00.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="PrcModIna" type="SIPROTEC5_DOType_SPS_UDEF_with_dataNs_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_CALH_Application" lnClass="CALH">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="GrAlm" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
			<DO name="GrWrn" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
			<DO name="GrInd" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_LTIM_Application" lnClass="LTIM">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="TmDT" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
			<DO name="TmOfsTmm" type="SIPROTEC5_DOType_ING_INT32_edit_V08.03.03_V08.00.00" />
			<DO name="TmUseDT" type="SIPROTEC5_DOType_SPG_edit_V08.03.03_V07.90.00" />
			<DO name="TmChgDT" type="SIPROTEC5_DOType_TSG_V08.03.03_V08.01.00" />
			<DO name="TmChgST" type="SIPROTEC5_DOType_TSG_V08.03.03_V08.01.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_LTMS_Application" lnClass="LTMS">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="TmSrc" type="SIPROTEC5_DOType_VSS_V08.03.03_V07.90.00" />
			<DO name="TmSrcTyp" type="SIPROTEC5_DOType_ENS_TmSrcTyp_V08.03.03_V08.01.00" />
			<DO name="TmChSt1" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
			<DO name="TmChSt2" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_LTRK_Application" lnClass="LTRK">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="GenTrk" type="SIPROTEC5_DOType_CST_V08.03.03_V07.90.00" />
			<DO name="SgcbTrk" type="SIPROTEC5_DOType_STS_V08.03.03_V07.90.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_ResetLed" lnClass="GAPC">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_LLN0_LDevice_Generic" lnClass="LLN0">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_LLN0_V08.03.03_V07.90.00" />
			<DO name="GrRef" type="SIPROTEC5_DOType_ORG_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_PTRC_Trip_3pol" lnClass="PTRC">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_V08.03.03_V07.90.00" />
			<DO name="Tr" type="SIPROTEC5_DOType_ACT_3pol_V08.03.03_V07.90.00" />
			<DO name="Op" type="SIPROTEC5_DOType_ACT_3pol_V08.03.03_V07.90.00" />
			<DO name="Str" type="SIPROTEC5_DOType_ACD_PhsSel_GABCN_Without_DirRouting_V08.03.03_V07.90.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_XCBR_3pol_Ctl" lnClass="XCBR">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="Loc" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
			<DO name="EEHealth" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="OpCnt" type="SIPROTEC5_DOType_INS_INT32_V08.03.03_V07.90.00" />
			<DO name="Pos" type="SIPROTEC5_DOType_DPC_XCBR_Pos_V08.03.03_V07.90.00" />
			<DO name="BlkOpn" type="SIPROTEC5_DOType_SPC_status_only_V08.03.03_V07.90.00" />
			<DO name="BlkCls" type="SIPROTEC5_DOType_SPC_status_only_V08.03.03_V07.90.00" />
			<DO name="SumSwARs" type="SIPROTEC5_DOType_BCR_noFreeze_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_GAPC_ManualClose" lnClass="GAPC">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="Blk" type="SIPROTEC5_DOType_SPS_for_Input_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_CSWI" lnClass="CSWI">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="Loc" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
			<DO name="Pos" type="SIPROTEC5_DOType_DPC_CSWI_Pos_V08.03.03_V08.00.00" />
			<DO name="LocKey" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
			<DO name="LocSta" type="SIPROTEC5_DOType_SPC_statusOnly_and_dir_with_nor_sec_V08.03.03_V07.90.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_CILO" lnClass="CILO">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_V08.03.03_V07.90.00" />
			<DO name="EnaOpn" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
			<DO name="EnaCls" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_MMXU_OpMeas_Fund_3ph_Pres" lnClass="MMXU">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="PPV" type="SIPROTEC5_DOType_DEL_V08.03.03_V08.00.00" />
			<DO name="PhV" type="SIPROTEC5_DOType_WYE_ABCRes_V08.03.03_V08.00.00" />
			<DO name="A" type="SIPROTEC5_DOType_WYE_ABCRes_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_XSWI_Ctl" lnClass="XSWI">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="Loc" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
			<DO name="OpCnt" type="SIPROTEC5_DOType_INS_INT32_V08.03.03_V07.90.00" />
			<DO name="Pos" type="SIPROTEC5_DOType_DPC_XCBR_Pos_V08.03.03_V07.90.00" />
			<DO name="BlkOpn" type="SIPROTEC5_DOType_SPC_status_only_V08.03.03_V07.90.00" />
			<DO name="BlkCls" type="SIPROTEC5_DOType_SPC_status_only_V08.03.03_V07.90.00" />
			<DO name="SwTyp" type="SIPROTEC5_DOType_ENS_SwitchType_V08.03.03_V07.90.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_LCCH_LineMode" lnClass="LCCH">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="ChLiv" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
			<DO name="RedChLiv" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_LCCH_61850" lnClass="LCCH">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="ChLiv" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_TCTR" lnClass="TCTR">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="ARtg" type="SIPROTEC5_DOType_ASG_FLOAT32_edit_V08.03.03_V08.00.00" />
			<DO name="Rat" type="SIPROTEC5_DOType_ASG_FLOAT32_readOnly_V08.03.03_V08.00.00" />
			<DO name="HzRtg" type="SIPROTEC5_DOType_ASG_FLOAT32_readOnly_V08.03.03_V08.00.00" />
			<DO name="Cor" type="SIPROTEC5_DOType_ASG_FLOAT32_edit_V08.03.03_V08.00.00" />
			<DO name="AmpSv" type="SIPROTEC5_DOType_SAV_VDEWChannelNumber_V08.03.03_V08.00.00" />
			<DO name="Trp" type="SIPROTEC5_DOType_ENG_TextList_Trp_edit_V08.03.03_V08.00.00" />
			<DO name="ScndTmms" type="SIPROTEC5_DOType_ING_INT32_div_readOnly_V08.03.03_V08.00.00" />
			<DO name="Clip" type="SIPROTEC5_DOType_ASG_FLOAT32_edit_with_dataNs_V08.03.03_V08.00.00" />
			<DO name="AccMeas" type="SIPROTEC5_DOType_ENG_TextList_AccMeas_edit_with_dataNs_V08.03.03_V08.00.00" />
			<DO name="AccPro" type="SIPROTEC5_DOType_ENG_TextList_AccPro_edit_with_dataNs_V08.03.03_V08.00.00" />
			<DO name="HoldTmms" type="SIPROTEC5_DOType_ING_INT32_div_readOnly_V08.03.03_V08.00.00" />
			<DO name="NamAccRtg" type="SIPROTEC5_DOType_VSD_readOnly_V08.03.03_V08.00.00" />
			<DO name="NamARtg" type="SIPROTEC5_DOType_VSD_readOnly_V08.03.03_V08.00.00" />
			<DO name="NamClipRtg" type="SIPROTEC5_DOType_VSD_readOnly_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_SBWS_BW_Tr" lnClass="SBWI">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_SIEMENS_LN_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_SSYM_CurBalSV" lnClass="SSYM">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_SIEMENS_LN_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_SPSQ_CurPhSeqSV" lnClass="SPSQ">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_SIEMENS_LN_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_SSUM_SlowCurSumSV" lnClass="SSUM">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_SIEMENS_LN_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_SADC_FastCurSumSV" lnClass="SADC">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_SIEMENS_LN_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_TVTR" lnClass="TVTR">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="VolSv" type="SIPROTEC5_DOType_SAV_VDEWChannelNumber_V08.03.03_V08.00.00" />
			<DO name="VRtg" type="SIPROTEC5_DOType_ASG_FLOAT32_readOnly_V08.03.03_V08.00.00" />
			<DO name="HzRtg" type="SIPROTEC5_DOType_ASG_FLOAT32_readOnly_V08.03.03_V08.00.00" />
			<DO name="Rat" type="SIPROTEC5_DOType_ASG_FLOAT32_readOnly_V08.03.03_V08.00.00" />
			<DO name="Cor" type="SIPROTEC5_DOType_ASG_FLOAT32_edit_V08.03.03_V08.00.00" />
			<DO name="Clip" type="SIPROTEC5_DOType_ASG_FLOAT32_edit_with_dataNs_V08.03.03_V08.00.00" />
			<DO name="AccMeas" type="SIPROTEC5_DOType_ENG_TextList_AccMeas_edit_with_dataNs_V08.03.03_V08.00.00" />
			<DO name="AccPro" type="SIPROTEC5_DOType_ENG_TextList_AccPro_edit_with_dataNs_V08.03.03_V08.00.00" />
			<DO name="HoldTmms" type="SIPROTEC5_DOType_ING_INT32_div_readOnly_V08.03.03_V08.00.00" />
			<DO name="NamAccRtg" type="SIPROTEC5_DOType_VSD_readOnly_V08.03.03_V08.00.00" />
			<DO name="NamVRtg" type="SIPROTEC5_DOType_VSD_readOnly_V08.03.03_V08.00.00" />
			<DO name="NamClipRtg" type="SIPROTEC5_DOType_VSD_readOnly_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_SFFM_SMCB" lnClass="SFFM">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_SIEMENS_LN_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_RDRE_DEF" lnClass="RDRE">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_V08.03.03_V07.90.00" />
			<DO name="RcdTrg" type="SIPROTEC5_DOType_SPC_dir_with_nor_sec_V08.03.03_V07.90.00" />
			<DO name="MemRs" type="SIPROTEC5_DOType_SPC_dir_with_enh_sec_FnKey_on_V08.03.03_V07.90.00" />
			<DO name="MemClr" type="SIPROTEC5_DOType_SPC_dir_with_enh_sec_FnKey_on_V08.03.03_V07.90.00" />
			<DO name="RcdMade" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
			<DO name="FltNum" type="SIPROTEC5_DOType_INS_INT32_V08.03.03_V07.90.00" />
			<DO name="RcdStr" type="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_PTRC_FG_Line_3ph" lnClass="PTRC">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_V08.03.03_V07.90.00" />
			<DO name="Op" type="SIPROTEC5_DOType_ACT_1_3pol_GABC_simpleConversions_V08.03.03_V07.90.00" />
			<DO name="Str" type="SIPROTEC5_DOType_ACD_PhsSel_GABCN_Without_DirRouting_V08.03.03_V07.90.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_PHAR" lnClass="PHAR">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="Str" type="SIPROTEC5_DOType_ACD_PhsSel_GABCN_Without_DirRouting_V08.03.03_V07.90.00" />
			<DO name="Blk" type="SIPROTEC5_DOType_SPS_for_Input_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_OC_Group_Indication" lnClass="GAPC">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_V08.03.03_V07.90.00" />
			<DO name="Str" type="SIPROTEC5_DOType_ACD_PhsSel_GABCN_Without_DirRouting_V08.03.03_V07.90.00" />
			<DO name="Op" type="SIPROTEC5_DOType_ACT_1_3pol_GABCN_V08.03.03_V07.90.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_PTRC_FN_Str_NonPhsSel_Without_DirRouting_Op_3pol" lnClass="PTRC">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_V08.03.03_V07.90.00" />
			<DO name="Op" type="SIPROTEC5_DOType_ACT_3pol_V08.03.03_V07.90.00" />
			<DO name="Str" type="SIPROTEC5_DOType_ACD_NonPhsSel_Without_DirRouting_V08.03.03_V07.90.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_PTOC_Gnd_DOCP_Bas" lnClass="PTOC">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="Str" type="SIPROTEC5_DOType_ACD_NonPhsSel_Without_DirRouting_V08.03.03_V07.90.00" />
			<DO name="Op" type="SIPROTEC5_DOType_ACT_3pol_V08.03.03_V07.90.00" />
			<DO name="Blk" type="SIPROTEC5_DOType_SPS_for_Input_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_PTRC_FN_Str_GABC_Without_DirRouting_Op_3pol" lnClass="PTRC">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_V08.03.03_V07.90.00" />
			<DO name="Op" type="SIPROTEC5_DOType_ACT_3pol_V08.03.03_V07.90.00" />
			<DO name="Str" type="SIPROTEC5_DOType_ACD_PhsSel_GABC_Without_DirRouting_V08.03.03_V07.90.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_PTOC_3ph_DOCP_3pol_Bas" lnClass="PTOC">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="Str" type="SIPROTEC5_DOType_ACD_PhsSel_GABC_Without_DirRouting_V08.03.03_V07.90.00" />
			<DO name="Op" type="SIPROTEC5_DOType_ACT_3pol_V08.03.03_V07.90.00" />
			<DO name="Blk" type="SIPROTEC5_DOType_SPS_for_Input_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_MMTR_OpMeas_Energy_3ph" lnClass="MMTR">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_V08.03.03_V07.90.00" />
			<DO name="SupWh" type="SIPROTEC5_DOType_BCR_V08.03.03_V08.01.00" />
			<DO name="SupVArh" type="SIPROTEC5_DOType_BCR_V08.03.03_V08.01.00" />
			<DO name="DmdWh" type="SIPROTEC5_DOType_BCR_V08.03.03_V08.01.00" />
			<DO name="DmdVArh" type="SIPROTEC5_DOType_BCR_V08.03.03_V08.01.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_MMXN_OpMeas_Fund_1ph_Pres" lnClass="MMXN">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_MSQI_OpMeas_Symm_Pres" lnClass="MSQI">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="SeqA" type="SIPROTEC5_DOType_SEQ_V08.03.03_V08.00.00" />
			<DO name="SeqV" type="SIPROTEC5_DOType_SEQ_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_MMXU_OpMeas_RMS_3ph_Pres" lnClass="MMXU">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="PPV" type="SIPROTEC5_DOType_DEL_mag_V08.03.03_V08.00.00" />
			<DO name="PhV" type="SIPROTEC5_DOType_WYE_ABCRes_mag_V08.03.03_V08.00.00" />
			<DO name="A" type="SIPROTEC5_DOType_WYE_ABCRes_mag_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_MMXU_OpMeas_Power_3ph_Pres" lnClass="MMXU">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="TotW" type="SIPROTEC5_DOType_MV_Float_V08.03.03_V08.00.00" />
			<DO name="TotVAr" type="SIPROTEC5_DOType_MV_Float_V08.03.03_V08.00.00" />
			<DO name="TotVA" type="SIPROTEC5_DOType_MV_Float_V08.03.03_V08.00.00" />
			<DO name="TotPF" type="SIPROTEC5_DOType_MV_Float_V08.03.03_V08.00.00" />
			<DO name="Hz" type="SIPROTEC5_DOType_MV_Float_V08.03.03_V08.00.00" />
			<DO name="W" type="SIPROTEC5_DOType_WYE_ABC_mag_V08.03.03_V08.00.00" />
			<DO name="VAr" type="SIPROTEC5_DOType_WYE_ABC_mag_V08.03.03_V08.00.00" />
			<DO name="VA" type="SIPROTEC5_DOType_WYE_ABC_mag_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_ROPA_OpenPoleCurrent" lnClass="ROPA">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_SIEMENS_LN_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_RSSR_SwitchingStateRecognitionBasic" lnClass="RSSR">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_SIEMENS_LN_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_ResetLed_1" lnClass="GAPC">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="SPS" type="SIPROTEC5_DOType_SPS_UDEF_with_dataNs_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_PTUV" lnClass="PTUV">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="Str" type="SIPROTEC5_DOType_ACD_PhsSel_GABC_Without_DirRouting_V08.03.03_V07.90.00" />
			<DO name="Op" type="SIPROTEC5_DOType_ACT_3pol_V08.03.03_V07.90.00" />
			<DO name="Blk" type="SIPROTEC5_DOType_SPS_for_Input_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_GAPC_FB0_NSP" lnClass="GAPC">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_PVOC_3ph_IOCP_3pol_Vol_Dep_Threshold" lnClass="PVOC">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="Str" type="SIPROTEC5_DOType_ACD_PhsSel_GABC_Without_DirRouting_V08.03.03_V07.90.00" />
			<DO name="Op" type="SIPROTEC5_DOType_ACT_3pol_V08.03.03_V07.90.00" />
			<DO name="Blk" type="SIPROTEC5_DOType_SPS_for_Input_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_PTOV" lnClass="PTOV">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="Str" type="SIPROTEC5_DOType_ACD_PhsSel_GABC_Without_DirRouting_V08.03.03_V07.90.00" />
			<DO name="Op" type="SIPROTEC5_DOType_ACT_3pol_V08.03.03_V07.90.00" />
			<DO name="Blk" type="SIPROTEC5_DOType_SPS_for_Input_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_V0_PTOV" lnClass="PTOV">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="Str" type="SIPROTEC5_DOType_ACD_NonPhsSel_Without_DirRouting_V08.03.03_V07.90.00" />
			<DO name="Op" type="SIPROTEC5_DOType_ACT_3pol_V08.03.03_V07.90.00" />
			<DO name="Blk" type="SIPROTEC5_DOType_SPS_for_Input_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_PTOF" lnClass="PTOF">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="Str" type="SIPROTEC5_DOType_ACD_NonPhsSel_Without_DirRouting_V08.03.03_V07.90.00" />
			<DO name="Op" type="SIPROTEC5_DOType_ACT_3pol_V08.03.03_V07.90.00" />
			<DO name="Blk" type="SIPROTEC5_DOType_SPS_for_Input_V08.03.03_V08.00.00" />
		</LNodeType>
		<LNodeType id="SIPROTEC5_LNType_PTUF" lnClass="PTUF">
			<DO name="Mod" type="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" />
			<DO name="Beh" type="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" />
			<DO name="Health" type="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" />
			<DO name="NamPlt" type="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" />
			<DO name="Str" type="SIPROTEC5_DOType_ACD_NonPhsSel_Without_DirRouting_V08.03.03_V07.90.00" />
			<DO name="Op" type="SIPROTEC5_DOType_ACT_3pol_V08.03.03_V07.90.00" />
			<DO name="Blk" type="SIPROTEC5_DOType_SPS_for_Input_V08.03.03_V08.00.00" />
		</LNodeType>
		<DOType id="SIPROTEC5_DOType_SPG_readOnly_with_dataNs_V08.03.03_V07.90.00" cdc="SPG">
			<DA fc="SE" name="setVal" bType="BOOLEAN" valKind="RO" />
			<DA fc="EX" name="dataNs" bType="VisString255" valKind="RO">
				<Val>SIPROTEC5</Val>
			</DA>
		</DOType>
		<DOType id="SIPROTEC5_DOType_SPC_dir_with_nor_sec_and_dataNs_V08.03.03_V07.90.00" cdc="SPC">
			<DA fc="ST" name="origin" bType="Struct" type="SIPROTEC5_DAType_origin_V08.03.03_V07.90.00" />
			<DA fc="ST" name="ctlNum" bType="INT8U" />
			<DA dchg="true" fc="ST" name="stVal" bType="BOOLEAN" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="ctlModel" bType="Enum" valKind="RO" type="SIPROTEC5_Textlist_ctlModel_dir_with_nor_sec_V08.03.03_V07.90.00">
				<Val>direct-with-normal-security</Val>
			</DA>
			<DA fc="EX" name="dataNs" bType="VisString255" valKind="RO">
				<Val>SIPROTEC5</Val>
			</DA>
			<DA fc="CO" name="Oper" bType="Struct" type="SIPROTEC5_DAType_Oper_Boolean_V08.03.03_V07.90.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_SPS_with_dataNs_V08.03.03_V07.90.00" cdc="SPS">
			<DA dchg="true" fc="ST" name="stVal" bType="BOOLEAN" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA fc="EX" name="dataNs" bType="VisString255" valKind="RO">
				<Val>SIPROTEC5</Val>
			</DA>
		</DOType>
		<DOType id="SIPROTEC5_DOType_SPC_dir_with_nor_sec_V08.03.03_V07.90.00" cdc="SPC">
			<DA fc="ST" name="origin" bType="Struct" type="SIPROTEC5_DAType_origin_V08.03.03_V07.90.00" />
			<DA fc="ST" name="ctlNum" bType="INT8U" />
			<DA dchg="true" fc="ST" name="stVal" bType="BOOLEAN" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="ctlModel" bType="Enum" valKind="RO" type="SIPROTEC5_Textlist_ctlModel_dir_with_nor_sec_V08.03.03_V07.90.00">
				<Val>direct-with-normal-security</Val>
			</DA>
			<DA fc="CO" name="Oper" bType="Struct" type="SIPROTEC5_DAType_Oper_Boolean_V08.03.03_V07.90.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_LPL_NamPlt_for_LLN0_V08.03.03_V07.90.00" cdc="LPL">
			<DA fc="DC" name="vendor" bType="VisString255" valKind="RO">
				<Val>SIEMENS</Val>
			</DA>
			<DA fc="DC" name="swRev" bType="VisString255" valKind="RO" />
			<DA fc="DC" name="d" bType="VisString255" valKind="RO" />
			<DA fc="DC" name="configRev" bType="VisString255" valKind="RO" />
			<DA fc="EX" name="ldNs" bType="VisString255" valKind="RO" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ENS_Health_V08.03.03_V07.90.00" cdc="ENS">
			<DA dchg="true" fc="ST" name="stVal" bType="Enum" type="SIPROTEC5_Textlist_Health_V08.03.03_V07.90.00" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ENS_Behavior_V08.03.03_V07.90.00" cdc="ENS">
			<DA dchg="true" fc="ST" name="stVal" bType="Enum" type="SIPROTEC5_Textlist_Behavior_V08.03.03_V07.90.00" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_Mod_controllable_Test_with_InitVal_V08.03.03_V07.90.00" cdc="ENC">
			<DA fc="ST" name="origin" bType="Struct" type="SIPROTEC5_DAType_origin_V08.03.03_V07.90.00" />
			<DA fc="ST" name="ctlNum" bType="INT8U" />
			<DA dchg="true" fc="ST" name="stVal" bType="Enum" type="SIPROTEC5_Textlist_Behavior_SetTestMod_V08.03.03_V07.90.00" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="ctlModel" bType="Enum" valKind="RO" type="SIPROTEC5_Textlist_ctlModel_dir_with_nor_sec_V08.03.03_V07.90.00">
				<Val>direct-with-normal-security</Val>
			</DA>
			<DA fc="CO" name="Oper" bType="Struct" type="SIPROTEC5_DAType_Oper_Mod_OnTest_V08.03.03_V07.90.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_SPS_UDEF_with_dataNs_V08.03.03_V08.00.00" cdc="SPS">
			<DA dchg="true" fc="ST" name="stVal" bType="BOOLEAN" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA fc="SV" name="subEna" bType="BOOLEAN" />
			<DA fc="SV" name="subVal" bType="BOOLEAN" />
			<DA fc="SV" name="subQ" bType="Quality" />
			<DA fc="SV" name="subID" bType="VisString64" />
			<DA fc="BL" name="blkEna" bType="BOOLEAN" />
			<DA fc="EX" name="dataNs" bType="VisString255" valKind="RO">
				<Val>SIPROTEC5/userdefined</Val>
			</DA>
		</DOType>
		<DOType id="SIPROTEC5_DOType_LPL_NamPlt_for_Ed2_LN_V08.03.03_V08.00.00" cdc="LPL">
			<DA fc="DC" name="vendor" bType="VisString255" valKind="RO">
				<Val>SIEMENS</Val>
			</DA>
			<DA fc="DC" name="swRev" bType="VisString255" valKind="RO" />
			<DA fc="DC" name="d" bType="VisString255" valKind="RO" />
			<DA fc="DC" name="configRev" bType="VisString255" valKind="RO" />
			<DA fc="EX" name="lnNs" bType="VisString255" valKind="RO">
				<Val>IEC 61850-7-4:2007B</Val>
			</DA>
		</DOType>
		<DOType id="SIPROTEC5_DOType_INS_INT32_with_units_V08.03.03_V08.00.00" cdc="INS">
			<DA dchg="true" fc="ST" name="stVal" bType="INT32" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="units" bType="Struct" type="SIPROTEC5_DAType_Units_1_V08.03.03_V08.00.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_SPC_controllable_V08.03.03_V07.90.00" cdc="SPC">
			<DA fc="ST" name="origin" bType="Struct" type="SIPROTEC5_DAType_origin_V08.03.03_V07.90.00" />
			<DA fc="ST" name="ctlNum" bType="INT8U" />
			<DA dchg="true" fc="ST" name="stVal" bType="BOOLEAN" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="ctlModel" bType="Enum" valKind="RO" type="SIPROTEC5_Textlist_ctlModel_V08.03.03_V07.90.00">
				<Val>status-only</Val>
			</DA>
			<DA dchg="true" fc="CF" name="sboTimeout" bType="INT32U" valKind="RO">
				<Val>0</Val>
			</DA>
			<DA dchg="true" fc="CF" name="sboClass" bType="Enum" valKind="RO" type="SIPROTEC5_Textlist_sboClass_V08.03.03_V07.90.00">
				<Val>operate-once</Val>
			</DA>
			<DA fc="CO" name="SBO" bType="VisString129">
				<ProtNs type="8-MMS">IEC 61850-8-1:2003</ProtNs>
			</DA>
			<DA fc="CO" name="SBOw" bType="Struct" type="SIPROTEC5_DAType_Oper_Boolean_V08.03.03_V07.90.00" />
			<DA fc="CO" name="Oper" bType="Struct" type="SIPROTEC5_DAType_Oper_Boolean_V08.03.03_V07.90.00" />
			<DA fc="CO" name="Cancel" bType="Struct" type="SIPROTEC5_DAType_Cancel_Boolean_V08.03.03_V07.90.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_SPS_V08.03.03_V07.90.00" cdc="SPS">
			<DA dchg="true" fc="ST" name="stVal" bType="BOOLEAN" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_DPL_V08.03.03_V08.00.00" cdc="DPL">
			<DA fc="DC" name="vendor" bType="VisString255" valKind="RO" />
			<DA fc="DC" name="hwRev" bType="VisString255" valKind="RO" />
			<DA fc="DC" name="swRev" bType="VisString255" valKind="RO" />
			<DA fc="DC" name="serNum" bType="VisString255" valKind="RO" />
			<DA fc="DC" name="model" bType="VisString255" valKind="RO" />
			<DA fc="DC" name="location" bType="VisString255" valKind="RO" />
			<DA fc="DC" name="owner" bType="VisString255" valKind="RO" />
			<DA fc="DC" name="d" bType="VisString255" valKind="RO" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_Mod_status_only_with_InitVal_V08.03.03_V07.90.00" cdc="ENC">
			<DA dchg="true" fc="ST" name="stVal" bType="Enum" type="SIPROTEC5_Textlist_Behavior_V08.03.03_V07.90.00">
				<Val>on</Val>
			</DA>
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="ctlModel" bType="Enum" valKind="RO" type="SIPROTEC5_Textlist_ctlModel_status_only_V08.03.03_V07.90.00">
				<Val>status-only</Val>
			</DA>
		</DOType>
		<DOType id="SIPROTEC5_DOType_TSG_V08.03.03_V08.01.00" cdc="TSG">
			<DA fc="SE" name="setCal" bType="Struct" type="SIPROTEC5_DAType_CalendarTime_V08.03.03_V07.90.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_SPG_edit_V08.03.03_V07.90.00" cdc="SPG">
			<DA fc="SE" name="setVal" bType="BOOLEAN" valKind="Set" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ING_INT32_edit_V08.03.03_V08.00.00" cdc="ING">
			<DA fc="SE" name="setVal" bType="INT32" valKind="Set" />
			<DA dchg="true" fc="CF" name="minVal" bType="INT32" valKind="RO">
				<Val>0</Val>
			</DA>
			<DA dchg="true" fc="CF" name="maxVal" bType="INT32" valKind="RO">
				<Val>0</Val>
			</DA>
			<DA dchg="true" fc="CF" name="stepSize" bType="INT32U" valKind="RO">
				<Val>0</Val>
			</DA>
			<DA dchg="true" fc="CF" name="units" bType="Struct" type="SIPROTEC5_DAType_Units_1_V08.03.03_V08.00.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ENS_TmSrcTyp_V08.03.03_V08.01.00" cdc="ENS">
			<DA dchg="true" fc="ST" name="stVal" bType="Enum" type="SIPROTEC5_Textlist_TmSrcTyp_V08.03.03_V08.01.00" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_VSS_V08.03.03_V07.90.00" cdc="VSS">
			<DA dchg="true" fc="ST" name="stVal" bType="VisString255" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_STS_V08.03.03_V07.90.00" cdc="STS">
			<DA dupd="true" fc="SR" name="objRef" bType="ObjRef" />
			<DA fc="SR" name="serviceType" bType="Enum" type="SIPROTEC5_Textlist_ServiceType_V08.03.03_V07.90.00" />
			<DA fc="SR" name="errorCode" bType="Enum" type="SIPROTEC5_Textlist_ServiceError_V08.03.03_V07.90.00" />
			<DA fc="SR" name="originatorID" bType="Octet64" />
			<DA fc="SR" name="t" bType="Timestamp" />
			<DA fc="SR" name="numOfSG" bType="INT8U" />
			<DA fc="SR" name="actSG" bType="INT8U" />
			<DA fc="SR" name="editSG" bType="INT8U" />
			<DA fc="SR" name="cnfEdit" bType="BOOLEAN" />
			<DA fc="SR" name="lActTm" bType="Timestamp" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_CST_V08.03.03_V07.90.00" cdc="CST">
			<DA dupd="true" fc="SR" name="objRef" bType="ObjRef" />
			<DA fc="SR" name="serviceType" bType="Enum" type="SIPROTEC5_Textlist_ServiceType_V08.03.03_V07.90.00" />
			<DA fc="SR" name="errorCode" bType="Enum" type="SIPROTEC5_Textlist_ServiceError_V08.03.03_V07.90.00" />
			<DA fc="SR" name="originatorID" bType="Octet64" />
			<DA fc="SR" name="t" bType="Timestamp" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ORG_V08.03.03_V08.00.00" cdc="ORG">
			<DA dchg="true" fc="SP" name="setSrcRef" bType="ObjRef" valKind="RO" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ACD_PhsSel_GABCN_Without_DirRouting_V08.03.03_V07.90.00" cdc="ACD">
			<DA dchg="true" fc="ST" name="general" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="dirGeneral" bType="Enum" type="SIPROTEC5_Textlist_DirectionGeneral_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="ST" name="phsA" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="dirPhsA" bType="Enum" type="SIPROTEC5_Textlist_DirectionPhase_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="ST" name="phsB" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="dirPhsB" bType="Enum" type="SIPROTEC5_Textlist_DirectionPhase_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="ST" name="phsC" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="dirPhsC" bType="Enum" type="SIPROTEC5_Textlist_DirectionPhase_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="ST" name="neut" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="dirNeut" bType="Enum" type="SIPROTEC5_Textlist_DirectionPhase_V08.03.03_V07.90.00" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ACT_3pol_V08.03.03_V07.90.00" cdc="ACT">
			<DA dchg="true" fc="ST" name="general" bType="BOOLEAN" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_LPL_NamPlt_V08.03.03_V07.90.00" cdc="LPL">
			<DA fc="DC" name="vendor" bType="VisString255" valKind="RO">
				<Val>SIEMENS</Val>
			</DA>
			<DA fc="DC" name="swRev" bType="VisString255" valKind="RO" />
			<DA fc="DC" name="d" bType="VisString255" valKind="RO" />
			<DA fc="DC" name="configRev" bType="VisString255" valKind="RO" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_BCR_noFreeze_V08.03.03_V08.00.00" cdc="BCR">
			<DA dchg="true" fc="ST" name="actVal" bType="INT64" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="units" bType="Struct" type="SIPROTEC5_DAType_Units_1_V08.03.03_V08.00.00" />
			<DA dchg="true" fc="CF" name="pulsQty" bType="FLOAT32" valKind="RO">
				<Val>1</Val>
			</DA>
		</DOType>
		<DOType id="SIPROTEC5_DOType_SPC_status_only_V08.03.03_V07.90.00" cdc="SPC">
			<DA dchg="true" fc="ST" name="stVal" bType="BOOLEAN" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="ctlModel" bType="Enum" valKind="RO" type="SIPROTEC5_Textlist_ctlModel_status_only_V08.03.03_V07.90.00">
				<Val>status-only</Val>
			</DA>
		</DOType>
		<DOType id="SIPROTEC5_DOType_DPC_XCBR_Pos_V08.03.03_V07.90.00" cdc="DPC">
			<DA fc="ST" name="origin" bType="Struct" type="SIPROTEC5_DAType_origin_V08.03.03_V07.90.00" />
			<DA fc="ST" name="ctlNum" bType="INT8U" />
			<DA dchg="true" fc="ST" name="stVal" bType="Dbpos" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA dchg="true" fc="ST" name="stSeld" bType="BOOLEAN" />
			<DA fc="SV" name="subEna" bType="BOOLEAN" />
			<DA fc="SV" name="subVal" bType="Dbpos" />
			<DA fc="SV" name="subQ" bType="Quality" />
			<DA fc="SV" name="subID" bType="VisString64" />
			<DA fc="BL" name="blkEna" bType="BOOLEAN" />
			<DA dchg="true" fc="CF" name="pulseConfig" bType="Struct" type="SIPROTEC5_DAType_PulseConfig_XCBR_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="CF" name="ctlModel" bType="Enum" valKind="RO" type="SIPROTEC5_Textlist_ctlModel_status_only_V08.03.03_V07.90.00">
				<Val>status-only</Val>
			</DA>
		</DOType>
		<DOType id="SIPROTEC5_DOType_INS_INT32_V08.03.03_V07.90.00" cdc="INS">
			<DA dchg="true" fc="ST" name="stVal" bType="INT32" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_SPS_for_Input_V08.03.03_V08.00.00" cdc="SPS">
			<DA dchg="true" fc="ST" name="stVal" bType="BOOLEAN" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA fc="SV" name="subEna" bType="BOOLEAN" />
			<DA fc="SV" name="subVal" bType="BOOLEAN" />
			<DA fc="SV" name="subQ" bType="Quality" />
			<DA fc="SV" name="subID" bType="VisString64" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_Mod_controllable_with_InitVal_V08.03.03_V07.90.00" cdc="ENC">
			<DA fc="ST" name="origin" bType="Struct" type="SIPROTEC5_DAType_origin_V08.03.03_V07.90.00" />
			<DA fc="ST" name="ctlNum" bType="INT8U" />
			<DA dchg="true" fc="ST" name="stVal" bType="Enum" type="SIPROTEC5_Textlist_Behavior_V08.03.03_V07.90.00" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="ctlModel" bType="Enum" valKind="RO" type="SIPROTEC5_Textlist_ctlModel_dir_with_nor_sec_V08.03.03_V07.90.00">
				<Val>direct-with-normal-security</Val>
			</DA>
			<DA fc="CO" name="Oper" bType="Struct" type="SIPROTEC5_DAType_Oper_Mod_V08.03.03_V07.90.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_SPC_statusOnly_and_dir_with_nor_sec_V08.03.03_V07.90.00" cdc="SPC">
			<DA fc="ST" name="origin" bType="Struct" type="SIPROTEC5_DAType_origin_V08.03.03_V07.90.00" />
			<DA fc="ST" name="ctlNum" bType="INT8U" />
			<DA dchg="true" fc="ST" name="stVal" bType="BOOLEAN" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="ctlModel" bType="Enum" valKind="RO" type="SIPROTEC5_Textlist_ctlModel_status_only_and_dir_with_nor_sec_V08.03.03_V07.90.00">
				<Val>direct-with-normal-security</Val>
			</DA>
			<DA fc="CO" name="Oper" bType="Struct" type="SIPROTEC5_DAType_Oper_Boolean_V08.03.03_V07.90.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_DPC_CSWI_Pos_V08.03.03_V08.00.00" cdc="DPC">
			<DA fc="ST" name="origin" bType="Struct" type="SIPROTEC5_DAType_origin_V08.03.03_V07.90.00" />
			<DA fc="ST" name="ctlNum" bType="INT8U" />
			<DA dchg="true" fc="ST" name="stVal" bType="Dbpos" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA dchg="true" fc="ST" name="stSeld" bType="BOOLEAN" />
			<DA dchg="true" fc="CF" name="ctlModel" bType="Enum" valKind="RO" type="SIPROTEC5_Textlist_ctlModel_V08.03.03_V07.90.00">
				<Val>status-only</Val>
			</DA>
			<DA dchg="true" fc="CF" name="sboTimeout" bType="INT32U" valKind="RO">
				<Val>0</Val>
			</DA>
			<DA dchg="true" fc="CF" name="operTimeout" bType="INT32U" valKind="RO">
				<Val>0</Val>
			</DA>
			<DA fc="CO" name="SBO" bType="VisString129">
				<ProtNs type="8-MMS">IEC 61850-8-1:2003</ProtNs>
			</DA>
			<DA fc="CO" name="SBOw" bType="Struct" type="SIPROTEC5_DAType_Oper_Boolean_V08.03.03_V07.90.00" />
			<DA fc="CO" name="Oper" bType="Struct" type="SIPROTEC5_DAType_Oper_Boolean_V08.03.03_V07.90.00" />
			<DA fc="CO" name="Cancel" bType="Struct" type="SIPROTEC5_DAType_Cancel_Boolean_V08.03.03_V07.90.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_WYE_ABCRes_V08.03.03_V08.00.00" cdc="WYE">
			<SDO name="phsA" type="SIPROTEC5_DOType_CMV_without_convertions_V08.03.03_V08.00.00" />
			<SDO name="phsB" type="SIPROTEC5_DOType_CMV_without_convertions_V08.03.03_V08.00.00" />
			<SDO name="phsC" type="SIPROTEC5_DOType_CMV_without_convertions_V08.03.03_V08.00.00" />
			<SDO name="res" type="SIPROTEC5_DOType_CMV_without_convertions_V08.03.03_V08.00.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_CMV_without_convertions_V08.03.03_V08.00.00" cdc="CMV">
			<DA fc="MX" name="instCVal" bType="Struct" type="SIPROTEC5_DAType_Vector_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="MX" name="cVal" bType="Struct" type="SIPROTEC5_DAType_Vector_V08.03.03_V07.90.00" />
			<DA qchg="true" fc="MX" name="q" bType="Quality" />
			<DA fc="MX" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="units" bType="Struct" type="SIPROTEC5_DAType_Units_1_V08.03.03_V08.00.00" />
			<DA dchg="true" fc="CF" name="db" bType="INT32U" valKind="Set">
				<Val>0</Val>
			</DA>
			<DA dchg="true" fc="CF" name="dbAng" bType="INT32U" valKind="Set">
				<Val>333</Val>
			</DA>
			<DA dchg="true" fc="CF" name="dbRef" bType="FLOAT32" valKind="RO">
				<Val>0</Val>
			</DA>
			<DA dchg="true" fc="CF" name="dbAngRef" bType="FLOAT32" valKind="RO">
				<Val>360</Val>
			</DA>
		</DOType>
		<DOType id="SIPROTEC5_DOType_DEL_V08.03.03_V08.00.00" cdc="DEL">
			<SDO name="phsAB" type="SIPROTEC5_DOType_CMV_without_convertions_V08.03.03_V08.00.00" />
			<SDO name="phsBC" type="SIPROTEC5_DOType_CMV_without_convertions_V08.03.03_V08.00.00" />
			<SDO name="phsCA" type="SIPROTEC5_DOType_CMV_without_convertions_V08.03.03_V08.00.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ENS_SwitchType_V08.03.03_V07.90.00" cdc="ENS">
			<DA dchg="true" fc="ST" name="stVal" bType="Enum" type="SIPROTEC5_EnType_SwitchType_V08.03.03_V07.90.00" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_VSD_readOnly_V08.03.03_V08.00.00" cdc="VSD">
			<DA fc="DC" name="val" bType="VisString255" valKind="RO" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ING_INT32_div_readOnly_V08.03.03_V08.00.00" cdc="ING">
			<DA fc="SE" name="setVal" bType="INT32" valKind="RO" />
			<DA dchg="true" fc="CF" name="minVal" bType="INT32" valKind="RO">
				<Val>0</Val>
			</DA>
			<DA dchg="true" fc="CF" name="maxVal" bType="INT32" valKind="RO">
				<Val>0</Val>
			</DA>
			<DA dchg="true" fc="CF" name="stepSize" bType="INT32U" valKind="RO">
				<Val>0</Val>
			</DA>
		</DOType>
		<DOType id="SIPROTEC5_DOType_ENG_TextList_AccPro_edit_with_dataNs_V08.03.03_V08.00.00" cdc="ENG">
			<DA fc="SE" name="setVal" bType="Enum" valKind="Set" type="SIPROTEC5_EnType_InstrumentTransformerProtectionRatingKind_V08.03.03_V08.00.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ENG_TextList_AccMeas_edit_with_dataNs_V08.03.03_V08.00.00" cdc="ENG">
			<DA fc="SE" name="setVal" bType="Enum" valKind="Set" type="SIPROTEC5_EnType_InstrumentTransformerMeasurementRatingKind_V08.03.03_V08.00.00" />
			<DA fc="EX" name="dataNs" bType="VisString255" valKind="RO">
				<Val>SIPROTEC5</Val>
			</DA>
		</DOType>
		<DOType id="SIPROTEC5_DOType_ASG_FLOAT32_edit_with_dataNs_V08.03.03_V08.00.00" cdc="ASG">
			<DA fc="SE" name="setMag" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="CF" name="units" bType="Struct" type="SIPROTEC5_DAType_Units_1_V08.03.03_V08.00.00" />
			<DA dchg="true" fc="CF" name="minVal" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_readOnly_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="CF" name="maxVal" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_readOnly_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="CF" name="stepSize" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_readOnly_V08.03.03_V07.90.00" />
			<DA fc="EX" name="dataNs" bType="VisString255" valKind="RO">
				<Val>SIPROTEC5</Val>
			</DA>
		</DOType>
		<DOType id="SIPROTEC5_DOType_ENG_TextList_Trp_edit_V08.03.03_V08.00.00" cdc="ENG">
			<DA fc="SE" name="setVal" bType="Enum" valKind="Set" type="SIPROTEC5_Textlist_Trp_V08.03.03_V08.00.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_SAV_VDEWChannelNumber_V08.03.03_V08.00.00" cdc="SAV">
			<DA fc="MX" name="instMag" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_INT32_V08.03.03_V07.90.00" />
			<DA qchg="true" fc="MX" name="q" bType="Quality" />
			<DA fc="MX" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="units" bType="Struct" type="SIPROTEC5_DAType_Units_1_V08.03.03_V08.00.00" />
			<DA dchg="true" fc="CF" name="sVC" bType="Struct" type="SIPROTEC5_DAType_ScaledValueConfig_readOnly_VisAsProperty_V08.03.03_V08.00.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ASG_FLOAT32_edit_V08.03.03_V08.00.00" cdc="ASG">
			<DA fc="SE" name="setMag" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="CF" name="units" bType="Struct" type="SIPROTEC5_DAType_Units_1_V08.03.03_V08.00.00" />
			<DA dchg="true" fc="CF" name="minVal" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_readOnly_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="CF" name="maxVal" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_readOnly_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="CF" name="stepSize" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_readOnly_V08.03.03_V07.90.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ASG_FLOAT32_readOnly_V08.03.03_V08.00.00" cdc="ASG">
			<DA fc="SE" name="setMag" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_readOnly_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="CF" name="units" bType="Struct" type="SIPROTEC5_DAType_Units_1_V08.03.03_V08.00.00" />
			<DA dchg="true" fc="CF" name="minVal" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_readOnly_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="CF" name="maxVal" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_readOnly_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="CF" name="stepSize" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_readOnly_V08.03.03_V07.90.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_LPL_NamPlt_for_SIEMENS_LN_V08.03.03_V08.00.00" cdc="LPL">
			<DA fc="DC" name="vendor" bType="VisString255" valKind="RO">
				<Val>SIEMENS</Val>
			</DA>
			<DA fc="DC" name="swRev" bType="VisString255" valKind="RO" />
			<DA fc="DC" name="d" bType="VisString255" valKind="RO" />
			<DA fc="DC" name="configRev" bType="VisString255" valKind="RO" />
			<DA fc="EX" name="lnNs" bType="VisString255" valKind="RO">
				<Val>SIPROTEC5</Val>
			</DA>
		</DOType>
		<DOType id="SIPROTEC5_DOType_SPC_dir_with_enh_sec_FnKey_on_V08.03.03_V07.90.00" cdc="SPC">
			<DA fc="ST" name="origin" bType="Struct" type="SIPROTEC5_DAType_origin_V08.03.03_V07.90.00" />
			<DA fc="ST" name="ctlNum" bType="INT8U" />
			<DA dchg="true" fc="ST" name="stVal" bType="BOOLEAN" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="ctlModel" bType="Enum" valKind="RO" type="SIPROTEC5_Textlist_ctlModel_dir_with_enh_sec_V08.03.03_V07.90.00">
				<Val>direct-with-enhanced-security</Val>
			</DA>
			<DA dchg="true" fc="CF" name="operTimeout" bType="INT32U">
				<Val>0</Val>
			</DA>
			<DA fc="CO" name="Oper" bType="Struct" type="SIPROTEC5_DAType_Oper_Boolean_V08.03.03_V07.90.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ACT_1_3pol_GABC_simpleConversions_V08.03.03_V07.90.00" cdc="ACT">
			<DA dchg="true" fc="ST" name="general" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="phsA" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="phsB" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="phsC" bType="BOOLEAN" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ACT_1_3pol_GABCN_V08.03.03_V07.90.00" cdc="ACT">
			<DA dchg="true" fc="ST" name="general" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="phsA" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="phsB" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="phsC" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="neut" bType="BOOLEAN" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ACD_NonPhsSel_Without_DirRouting_V08.03.03_V07.90.00" cdc="ACD">
			<DA dchg="true" fc="ST" name="general" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="dirGeneral" bType="Enum" type="SIPROTEC5_Textlist_DirectionGeneral_V08.03.03_V07.90.00" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_ACD_PhsSel_GABC_Without_DirRouting_V08.03.03_V07.90.00" cdc="ACD">
			<DA dchg="true" fc="ST" name="general" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="dirGeneral" bType="Enum" type="SIPROTEC5_Textlist_DirectionGeneral_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="ST" name="phsA" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="dirPhsA" bType="Enum" type="SIPROTEC5_Textlist_DirectionPhase_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="ST" name="phsB" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="dirPhsB" bType="Enum" type="SIPROTEC5_Textlist_DirectionPhase_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="ST" name="phsC" bType="BOOLEAN" />
			<DA dchg="true" fc="ST" name="dirPhsC" bType="Enum" type="SIPROTEC5_Textlist_DirectionPhase_V08.03.03_V07.90.00" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_BCR_V08.03.03_V08.01.00" cdc="BCR">
			<DA dchg="true" fc="ST" name="actVal" bType="INT64" />
			<DA dupd="true" fc="ST" name="frVal" bType="INT64" />
			<DA fc="ST" name="frTm" bType="Timestamp" />
			<DA qchg="true" fc="ST" name="q" bType="Quality" />
			<DA fc="ST" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="units" bType="Struct" type="SIPROTEC5_DAType_Units_1_V08.03.03_V08.00.00" />
			<DA dchg="true" fc="CF" name="pulsQty" bType="FLOAT32" valKind="RO">
				<Val>1</Val>
			</DA>
			<DA dchg="true" fc="CF" name="frEna" bType="BOOLEAN" valKind="RO">
				<Val>false</Val>
			</DA>
			<DA dchg="true" fc="CF" name="strTm" bType="Timestamp" valKind="RO" />
			<DA dchg="true" fc="CF" name="frPd" bType="INT32" valKind="RO">
				<Val>0</Val>
			</DA>
			<DA dchg="true" fc="CF" name="frRs" bType="BOOLEAN" valKind="RO">
				<Val>false</Val>
			</DA>
		</DOType>
		<DOType id="SIPROTEC5_DOType_SEQ_V08.03.03_V08.00.00" cdc="SEQ">
			<SDO name="c1" type="SIPROTEC5_DOType_CMV_without_convertions_V08.03.03_V08.00.00" />
			<SDO name="c2" type="SIPROTEC5_DOType_CMV_without_convertions_V08.03.03_V08.00.00" />
			<SDO name="c3" type="SIPROTEC5_DOType_CMV_without_convertions_V08.03.03_V08.00.00" />
			<DA fc="MX" name="seqT" bType="Enum" type="SIPROTEC5_Textlist_SEQtype_V08.03.03_V07.90.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_WYE_ABCRes_mag_V08.03.03_V08.00.00" cdc="WYE">
			<SDO name="phsA" type="SIPROTEC5_DOType_CMV_mag_without_convertions_V08.03.03_V08.00.00" />
			<SDO name="phsB" type="SIPROTEC5_DOType_CMV_mag_without_convertions_V08.03.03_V08.00.00" />
			<SDO name="phsC" type="SIPROTEC5_DOType_CMV_mag_without_convertions_V08.03.03_V08.00.00" />
			<SDO name="res" type="SIPROTEC5_DOType_CMV_mag_without_convertions_V08.03.03_V08.00.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_CMV_mag_without_convertions_V08.03.03_V08.00.00" cdc="CMV">
			<DA fc="MX" name="instCVal" bType="Struct" type="SIPROTEC5_DAType_Vector_mag_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="MX" name="cVal" bType="Struct" type="SIPROTEC5_DAType_Vector_mag_V08.03.03_V07.90.00" />
			<DA qchg="true" fc="MX" name="q" bType="Quality" />
			<DA fc="MX" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="units" bType="Struct" type="SIPROTEC5_DAType_Units_1_V08.03.03_V08.00.00" />
			<DA dchg="true" fc="CF" name="db" bType="INT32U" valKind="Set">
				<Val>0</Val>
			</DA>
			<DA dchg="true" fc="CF" name="dbRef" bType="FLOAT32" valKind="RO">
				<Val>0</Val>
			</DA>
		</DOType>
		<DOType id="SIPROTEC5_DOType_DEL_mag_V08.03.03_V08.00.00" cdc="DEL">
			<SDO name="phsAB" type="SIPROTEC5_DOType_CMV_mag_without_convertions_V08.03.03_V08.00.00" />
			<SDO name="phsBC" type="SIPROTEC5_DOType_CMV_mag_without_convertions_V08.03.03_V08.00.00" />
			<SDO name="phsCA" type="SIPROTEC5_DOType_CMV_mag_without_convertions_V08.03.03_V08.00.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_WYE_ABC_mag_V08.03.03_V08.00.00" cdc="WYE">
			<SDO name="phsA" type="SIPROTEC5_DOType_CMV_mag_without_convertions_V08.03.03_V08.00.00" />
			<SDO name="phsB" type="SIPROTEC5_DOType_CMV_mag_without_convertions_V08.03.03_V08.00.00" />
			<SDO name="phsC" type="SIPROTEC5_DOType_CMV_mag_without_convertions_V08.03.03_V08.00.00" />
		</DOType>
		<DOType id="SIPROTEC5_DOType_MV_Float_V08.03.03_V08.00.00" cdc="MV">
			<DA fc="MX" name="instMag" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_V08.03.03_V07.90.00" />
			<DA dchg="true" fc="MX" name="mag" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_V08.03.03_V07.90.00" />
			<DA qchg="true" fc="MX" name="q" bType="Quality" />
			<DA fc="MX" name="t" bType="Timestamp" />
			<DA dchg="true" fc="CF" name="units" bType="Struct" type="SIPROTEC5_DAType_Units_1_V08.03.03_V08.00.00" />
			<DA dchg="true" fc="CF" name="db" bType="INT32U" valKind="Set">
				<Val>0</Val>
			</DA>
			<DA dchg="true" fc="CF" name="dbRef" bType="FLOAT32" valKind="RO">
				<Val>0</Val>
			</DA>
		</DOType>
		<DAType id="SIPROTEC5_DAType_origin_V08.03.03_V07.90.00">
			<BDA name="orCat" bType="Enum" type="SIPROTEC5_Textlist_orCategory_V08.03.03_V07.90.00" />
			<BDA name="orIdent" bType="Octet64" />
		</DAType>
		<DAType id="SIPROTEC5_DAType_Oper_Boolean_V08.03.03_V07.90.00">
			<BDA name="ctlVal" bType="BOOLEAN" />
			<BDA name="origin" bType="Struct" type="SIPROTEC5_DAType_origin_V08.03.03_V07.90.00" />
			<BDA name="ctlNum" bType="INT8U" />
			<BDA name="T" bType="Timestamp" />
			<BDA name="Test" bType="BOOLEAN" />
			<BDA name="Check" bType="Check" />
			<ProtNs type="8-MMS">IEC 61850-8-1:2003</ProtNs>
		</DAType>
		<DAType id="SIPROTEC5_DAType_Oper_Mod_OnTest_V08.03.03_V07.90.00">
			<BDA name="ctlVal" bType="Enum" type="SIPROTEC5_Textlist_Behavior_SetTestMod_V08.03.03_V07.90.00" />
			<BDA name="origin" bType="Struct" type="SIPROTEC5_DAType_origin_V08.03.03_V07.90.00" />
			<BDA name="ctlNum" bType="INT8U" />
			<BDA name="T" bType="Timestamp" />
			<BDA name="Test" bType="BOOLEAN" />
			<BDA name="Check" bType="Check" />
			<ProtNs type="8-MMS">IEC 61850-8-1:2003</ProtNs>
		</DAType>
		<DAType id="SIPROTEC5_DAType_Units_1_V08.03.03_V08.00.00">
			<BDA name="SIUnit" bType="Enum" valKind="RO" type="SIPROTEC5_EnType_SIUnit_V08.03.03_V08.00.00" />
			<BDA name="multiplier" bType="Enum" valKind="RO" type="SIPROTEC5_EnType_Multiplier_V08.03.03_V07.90.00" />
		</DAType>
		<DAType id="SIPROTEC5_DAType_Cancel_Boolean_V08.03.03_V07.90.00">
			<BDA name="ctlVal" bType="BOOLEAN" />
			<BDA name="origin" bType="Struct" type="SIPROTEC5_DAType_origin_V08.03.03_V07.90.00" />
			<BDA name="ctlNum" bType="INT8U" />
			<BDA name="T" bType="Timestamp" />
			<BDA name="Test" bType="BOOLEAN" />
			<ProtNs type="8-MMS">IEC 61850-8-1:2003</ProtNs>
		</DAType>
		<DAType id="SIPROTEC5_DAType_CalendarTime_V08.03.03_V07.90.00">
			<BDA name="occ" bType="INT16U" />
			<BDA name="occType" bType="Enum" type="SIPROTEC5_EnType_Cal_Occ_Type_V08.03.03_V07.90.00" />
			<BDA name="occPer" bType="Enum" type="SIPROTEC5_EnType_Cal_Occ_Period_V08.03.03_V07.90.00" />
			<BDA name="weekDay" bType="Enum" type="SIPROTEC5_EnType_Cal_WeekDay_V08.03.03_V07.90.00" />
			<BDA name="month" bType="Enum" type="SIPROTEC5_EnType_Cal_Month_V08.03.03_V07.90.00" />
			<BDA name="day" bType="INT8U" />
			<BDA name="hr" bType="INT8U" />
			<BDA name="mn" bType="INT8U" />
		</DAType>
		<DAType id="SIPROTEC5_DAType_PulseConfig_XCBR_V08.03.03_V07.90.00">
			<BDA name="cmdQual" bType="Enum" valKind="RO" type="SIPROTEC5_Textlist_PulseConfigCmdQual_V08.03.03_V07.90.00" />
			<BDA name="onDur" bType="INT32U" valKind="RO" />
			<BDA name="offDur" bType="INT32U" valKind="RO" />
			<BDA name="numPls" bType="INT32U" valKind="RO" />
		</DAType>
		<DAType id="SIPROTEC5_DAType_Oper_Mod_V08.03.03_V07.90.00">
			<BDA name="ctlVal" bType="Enum" type="SIPROTEC5_Textlist_Behavior_V08.03.03_V07.90.00" />
			<BDA name="origin" bType="Struct" type="SIPROTEC5_DAType_origin_V08.03.03_V07.90.00" />
			<BDA name="ctlNum" bType="INT8U" />
			<BDA name="T" bType="Timestamp" />
			<BDA name="Test" bType="BOOLEAN" />
			<BDA name="Check" bType="Check" />
			<ProtNs type="8-MMS">IEC 61850-8-1:2003</ProtNs>
		</DAType>
		<DAType id="SIPROTEC5_DAType_Vector_V08.03.03_V07.90.00">
			<BDA name="mag" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_V08.03.03_V07.90.00" />
			<BDA name="ang" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_V08.03.03_V07.90.00" />
		</DAType>
		<DAType id="SIPROTEC5_DAType_AnalogValue_FLOAT32_V08.03.03_V07.90.00">
			<BDA name="f" bType="FLOAT32" valKind="Set">
				<Val>0</Val>
			</BDA>
		</DAType>
		<DAType id="SIPROTEC5_DAType_AnalogValue_FLOAT32_readOnly_V08.03.03_V07.90.00">
			<BDA name="f" bType="FLOAT32" valKind="RO">
				<Val>0</Val>
			</BDA>
		</DAType>
		<DAType id="SIPROTEC5_DAType_AnalogValue_INT32_V08.03.03_V07.90.00">
			<BDA name="i" bType="INT32" />
		</DAType>
		<DAType id="SIPROTEC5_DAType_ScaledValueConfig_readOnly_VisAsProperty_V08.03.03_V08.00.00">
			<BDA name="scaleFactor" bType="FLOAT32" valKind="Set">
				<Val>1</Val>
			</BDA>
			<BDA name="offset" bType="FLOAT32" valKind="Set">
				<Val>0</Val>
			</BDA>
		</DAType>
		<DAType id="SIPROTEC5_DAType_Vector_mag_V08.03.03_V07.90.00">
			<BDA name="mag" bType="Struct" type="SIPROTEC5_DAType_AnalogValue_FLOAT32_V08.03.03_V07.90.00" />
		</DAType>
		<EnumType id="SIPROTEC5_Textlist_orCategory_V08.03.03_V07.90.00">
			<EnumVal ord="0">not-supported</EnumVal>
			<EnumVal ord="1">bay-control</EnumVal>
			<EnumVal ord="2">station-control</EnumVal>
			<EnumVal ord="3">remote-control</EnumVal>
			<EnumVal ord="4">automatic-bay</EnumVal>
			<EnumVal ord="5">automatic-station</EnumVal>
			<EnumVal ord="6">automatic-remote</EnumVal>
			<EnumVal ord="7">maintenance</EnumVal>
			<EnumVal ord="8">process</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_ctlModel_dir_with_nor_sec_V08.03.03_V07.90.00">
			<EnumVal ord="1">direct-with-normal-security</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_Health_V08.03.03_V07.90.00">
			<EnumVal ord="1">Ok</EnumVal>
			<EnumVal ord="2">Warning</EnumVal>
			<EnumVal ord="3">Alarm</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_Behavior_V08.03.03_V07.90.00">
			<EnumVal ord="1">on</EnumVal>
			<EnumVal ord="3">test</EnumVal>
			<EnumVal ord="5">off</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_Behavior_SetTestMod_V08.03.03_V07.90.00">
			<EnumVal ord="1">on</EnumVal>
			<EnumVal ord="3">test</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_EnType_SIUnit_V08.03.03_V08.00.00">
			<EnumVal ord="-38">kV/mA</EnumVal>
			<EnumVal ord="-37">kA/V</EnumVal>
			<EnumVal ord="-36">ohm/m</EnumVal>
			<EnumVal ord="-35">ppm/°C</EnumVal>
			<EnumVal ord="-34">F/m</EnumVal>
			<EnumVal ord="-33">H/m</EnumVal>
			<EnumVal ord="-32">ms/kPa</EnumVal>
			<EnumVal ord="-31">kPa</EnumVal>
			<EnumVal ord="-30">ms/V</EnumVal>
			<EnumVal ord="-29">ms/K</EnumVal>
			<EnumVal ord="-28">V/s</EnumVal>
			<EnumVal ord="-27">I/Ir*s</EnumVal>
			<EnumVal ord="-26">1/week</EnumVal>
			<EnumVal ord="-25">1/d</EnumVal>
			<EnumVal ord="-24">1/h</EnumVal>
			<EnumVal ord="-23">1/min</EnumVal>
			<EnumVal ord="-22">periods</EnumVal>
			<EnumVal ord="-21">GB</EnumVal>
			<EnumVal ord="-19">cycle</EnumVal>
			<EnumVal ord="-18">mile</EnumVal>
			<EnumVal ord="-17">inch</EnumVal>
			<EnumVal ord="-16">°F</EnumVal>
			<EnumVal ord="-15">I/IrObj</EnumVal>
			<EnumVal ord="-14">MB</EnumVal>
			<EnumVal ord="-13">KB</EnumVal>
			<EnumVal ord="-12">Bytes</EnumVal>
			<EnumVal ord="-11">p.u.</EnumVal>
			<EnumVal ord="-10">day(s)</EnumVal>
			<EnumVal ord="-7">%</EnumVal>
			<EnumVal ord="-4">F/mi</EnumVal>
			<EnumVal ord="-3">ohm/mi</EnumVal>
			<EnumVal ord="-2">F/km</EnumVal>
			<EnumVal ord="-1">ohm/km</EnumVal>
			<EnumVal ord="1" />
			<EnumVal ord="2">m</EnumVal>
			<EnumVal ord="3">kg</EnumVal>
			<EnumVal ord="4">s</EnumVal>
			<EnumVal ord="5">A</EnumVal>
			<EnumVal ord="6">K</EnumVal>
			<EnumVal ord="7">mol</EnumVal>
			<EnumVal ord="8">cd</EnumVal>
			<EnumVal ord="9">deg</EnumVal>
			<EnumVal ord="10">rad</EnumVal>
			<EnumVal ord="11">sr</EnumVal>
			<EnumVal ord="21">Gy</EnumVal>
			<EnumVal ord="23">°C</EnumVal>
			<EnumVal ord="24">Sv</EnumVal>
			<EnumVal ord="25">F</EnumVal>
			<EnumVal ord="26">C</EnumVal>
			<EnumVal ord="27">S</EnumVal>
			<EnumVal ord="28">H</EnumVal>
			<EnumVal ord="29">V</EnumVal>
			<EnumVal ord="30">ohm</EnumVal>
			<EnumVal ord="31">J</EnumVal>
			<EnumVal ord="32">N</EnumVal>
			<EnumVal ord="33">Hz</EnumVal>
			<EnumVal ord="34">lx</EnumVal>
			<EnumVal ord="35">Lm</EnumVal>
			<EnumVal ord="36">Wb</EnumVal>
			<EnumVal ord="37">T</EnumVal>
			<EnumVal ord="38">W</EnumVal>
			<EnumVal ord="39">Pa</EnumVal>
			<EnumVal ord="41">m²</EnumVal>
			<EnumVal ord="42">m³</EnumVal>
			<EnumVal ord="43">m/s</EnumVal>
			<EnumVal ord="44">m/s²</EnumVal>
			<EnumVal ord="45">m³/s</EnumVal>
			<EnumVal ord="46">m/m³</EnumVal>
			<EnumVal ord="47">M</EnumVal>
			<EnumVal ord="48">kg/m³</EnumVal>
			<EnumVal ord="49">m²/s</EnumVal>
			<EnumVal ord="50">W/m K</EnumVal>
			<EnumVal ord="51">J/K</EnumVal>
			<EnumVal ord="52">ppm</EnumVal>
			<EnumVal ord="53">1/s</EnumVal>
			<EnumVal ord="54">rad/s</EnumVal>
			<EnumVal ord="55">W/m²</EnumVal>
			<EnumVal ord="56">J/m²</EnumVal>
			<EnumVal ord="57">S/m</EnumVal>
			<EnumVal ord="58">K/s</EnumVal>
			<EnumVal ord="59">Pa/s</EnumVal>
			<EnumVal ord="60">J/kg K</EnumVal>
			<EnumVal ord="61">VA</EnumVal>
			<EnumVal ord="63">VAr</EnumVal>
			<EnumVal ord="64">phi</EnumVal>
			<EnumVal ord="65">cos(phi)</EnumVal>
			<EnumVal ord="66">Vs</EnumVal>
			<EnumVal ord="67">V²</EnumVal>
			<EnumVal ord="68">As</EnumVal>
			<EnumVal ord="69">A²</EnumVal>
			<EnumVal ord="70">A²t</EnumVal>
			<EnumVal ord="71">VAh</EnumVal>
			<EnumVal ord="72">Wh</EnumVal>
			<EnumVal ord="73">VArh</EnumVal>
			<EnumVal ord="74">V/Hz</EnumVal>
			<EnumVal ord="75">Hz/s</EnumVal>
			<EnumVal ord="76">char</EnumVal>
			<EnumVal ord="77">char/s</EnumVal>
			<EnumVal ord="78">kgm²</EnumVal>
			<EnumVal ord="79">dB</EnumVal>
			<EnumVal ord="80">J/Wh</EnumVal>
			<EnumVal ord="81">W/s</EnumVal>
			<EnumVal ord="82">l/s</EnumVal>
			<EnumVal ord="83">dBm</EnumVal>
			<EnumVal ord="84">h</EnumVal>
			<EnumVal ord="85">min</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_EnType_Multiplier_V08.03.03_V07.90.00">
			<EnumVal ord="-24">y</EnumVal>
			<EnumVal ord="-21">z</EnumVal>
			<EnumVal ord="-18">a</EnumVal>
			<EnumVal ord="-15">f</EnumVal>
			<EnumVal ord="-12">p</EnumVal>
			<EnumVal ord="-9">n</EnumVal>
			<EnumVal ord="-6">µ</EnumVal>
			<EnumVal ord="-3">m</EnumVal>
			<EnumVal ord="-2">c</EnumVal>
			<EnumVal ord="-1">d</EnumVal>
			<EnumVal ord="0" />
			<EnumVal ord="1">da</EnumVal>
			<EnumVal ord="2">h</EnumVal>
			<EnumVal ord="3">k</EnumVal>
			<EnumVal ord="6">M</EnumVal>
			<EnumVal ord="9">G</EnumVal>
			<EnumVal ord="12">T</EnumVal>
			<EnumVal ord="15">P</EnumVal>
			<EnumVal ord="18">E</EnumVal>
			<EnumVal ord="21">Z</EnumVal>
			<EnumVal ord="24">Y</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_ctlModel_V08.03.03_V07.90.00">
			<EnumVal ord="0">status-only</EnumVal>
			<EnumVal ord="1">direct-with-normal-security</EnumVal>
			<EnumVal ord="2">sbo-with-normal-security</EnumVal>
			<EnumVal ord="3">direct-with-enhanced-security</EnumVal>
			<EnumVal ord="4">sbo-with-enhanced-security</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_sboClass_V08.03.03_V07.90.00">
			<EnumVal ord="0">operate-once</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_ctlModel_status_only_V08.03.03_V07.90.00">
			<EnumVal ord="0">status-only</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_EnType_Cal_Occ_Type_V08.03.03_V07.90.00">
			<EnumVal ord="0">Time</EnumVal>
			<EnumVal ord="1">WeekDay</EnumVal>
			<EnumVal ord="2">WeekOfYear</EnumVal>
			<EnumVal ord="3">DayOfMonth</EnumVal>
			<EnumVal ord="4">DayOfYear</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_EnType_Cal_Occ_Period_V08.03.03_V07.90.00">
			<EnumVal ord="0">Hour</EnumVal>
			<EnumVal ord="1">Day</EnumVal>
			<EnumVal ord="2">Week</EnumVal>
			<EnumVal ord="3">Month</EnumVal>
			<EnumVal ord="4">Year</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_EnType_Cal_WeekDay_V08.03.03_V07.90.00">
			<EnumVal ord="1">Monday</EnumVal>
			<EnumVal ord="2">Tuesday</EnumVal>
			<EnumVal ord="3">Wednesday</EnumVal>
			<EnumVal ord="4">Thursday</EnumVal>
			<EnumVal ord="5">Friday</EnumVal>
			<EnumVal ord="6">Saturday</EnumVal>
			<EnumVal ord="7">Sunday</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_EnType_Cal_Month_V08.03.03_V07.90.00">
			<EnumVal ord="1">January</EnumVal>
			<EnumVal ord="2">February</EnumVal>
			<EnumVal ord="3">March</EnumVal>
			<EnumVal ord="4">April</EnumVal>
			<EnumVal ord="5">May</EnumVal>
			<EnumVal ord="6">June</EnumVal>
			<EnumVal ord="7">July</EnumVal>
			<EnumVal ord="8">August</EnumVal>
			<EnumVal ord="9">September</EnumVal>
			<EnumVal ord="10">October</EnumVal>
			<EnumVal ord="11">November</EnumVal>
			<EnumVal ord="12">December</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_TmSrcTyp_V08.03.03_V08.01.00">
			<EnumVal ord="-15">ERR</EnumVal>
			<EnumVal ord="-14">T104</EnumVal>
			<EnumVal ord="-13">T103</EnumVal>
			<EnumVal ord="-12">RTC</EnumVal>
			<EnumVal ord="-11">IEEE1588</EnumVal>
			<EnumVal ord="-10">EXTERN_SIPROTEC</EnumVal>
			<EnumVal ord="-9">MINUTE_PULS</EnumVal>
			<EnumVal ord="-8">DNP30</EnumVal>
			<EnumVal ord="-7">MODBUS</EnumVal>
			<EnumVal ord="-6">PROFIBUS</EnumVal>
			<EnumVal ord="-5">GALILEO</EnumVal>
			<EnumVal ord="-4">SYNC_BOX</EnumVal>
			<EnumVal ord="-3">DCF77</EnumVal>
			<EnumVal ord="-2">GPS</EnumVal>
			<EnumVal ord="-1">HMI</EnumVal>
			<EnumVal ord="1">Unknown</EnumVal>
			<EnumVal ord="2">SNTP</EnumVal>
			<EnumVal ord="3">PTP</EnumVal>
			<EnumVal ord="4">IRIG-B</EnumVal>
			<EnumVal ord="5">Substation internal</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_ServiceType_V08.03.03_V07.90.00">
			<EnumVal ord="-3">CancelEditSG</EnumVal>
			<EnumVal ord="-2">None</EnumVal>
			<EnumVal ord="-1">Unknown</EnumVal>
			<EnumVal ord="1">Associate</EnumVal>
			<EnumVal ord="2">Abort</EnumVal>
			<EnumVal ord="3">Release</EnumVal>
			<EnumVal ord="4">GetServerDirectory</EnumVal>
			<EnumVal ord="5">GetLogicalDeviceDirectory</EnumVal>
			<EnumVal ord="6">GetAllDataValues</EnumVal>
			<EnumVal ord="7">GetDataValues</EnumVal>
			<EnumVal ord="8">SetDataValues</EnumVal>
			<EnumVal ord="9">GetDataDirectory</EnumVal>
			<EnumVal ord="10">GetDataDefinition</EnumVal>
			<EnumVal ord="11">GetDataSetValues</EnumVal>
			<EnumVal ord="12">SetDataSetValues</EnumVal>
			<EnumVal ord="13">CreateDataSet</EnumVal>
			<EnumVal ord="14">DeleteDataSet</EnumVal>
			<EnumVal ord="15">GetDataSetDirectory</EnumVal>
			<EnumVal ord="16">SelectActiveSG</EnumVal>
			<EnumVal ord="17">SelectEditSG</EnumVal>
			<EnumVal ord="18">SetEditSGValue</EnumVal>
			<EnumVal ord="19">ConfirmEditSGValues</EnumVal>
			<EnumVal ord="20">GetEditSGValue</EnumVal>
			<EnumVal ord="21">GetSGCBValues</EnumVal>
			<EnumVal ord="22">Report</EnumVal>
			<EnumVal ord="23">GetBRCBValues</EnumVal>
			<EnumVal ord="24">SetBRCBValues</EnumVal>
			<EnumVal ord="25">GetURCBValues</EnumVal>
			<EnumVal ord="26">SetURCBValues</EnumVal>
			<EnumVal ord="27">GetLCBValues</EnumVal>
			<EnumVal ord="28">SetLCBValues</EnumVal>
			<EnumVal ord="29">QueryLogByTime</EnumVal>
			<EnumVal ord="30">QueryLogAfter</EnumVal>
			<EnumVal ord="31">GetLogStatusValues</EnumVal>
			<EnumVal ord="32">SendGOOSEMessage</EnumVal>
			<EnumVal ord="33">GetGoCBValues</EnumVal>
			<EnumVal ord="34">SetGoCBValues</EnumVal>
			<EnumVal ord="35">GetGoReference</EnumVal>
			<EnumVal ord="36">GetGOOSEElementNumber</EnumVal>
			<EnumVal ord="37">SendMSVMessage</EnumVal>
			<EnumVal ord="38">GetMSVCBValues</EnumVal>
			<EnumVal ord="39">SetMSVCBValues</EnumVal>
			<EnumVal ord="40">SendUSVMessage</EnumVal>
			<EnumVal ord="41">GetUSVCBValues</EnumVal>
			<EnumVal ord="42">SetUSVCBValues</EnumVal>
			<EnumVal ord="43">Select</EnumVal>
			<EnumVal ord="44">SelectWithValue</EnumVal>
			<EnumVal ord="45">Cancel</EnumVal>
			<EnumVal ord="46">Operate</EnumVal>
			<EnumVal ord="47">CommandTermination</EnumVal>
			<EnumVal ord="48">TimeActivatedOperate</EnumVal>
			<EnumVal ord="49">GetFile</EnumVal>
			<EnumVal ord="50">SetFile</EnumVal>
			<EnumVal ord="51">DeleteFile</EnumVal>
			<EnumVal ord="52">GetFileAttributeValues</EnumVal>
			<EnumVal ord="53">TimeSynchronization</EnumVal>
			<EnumVal ord="54">InternalChange</EnumVal>
			<EnumVal ord="55">GetLogicalNodeDirectory</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_ServiceError_V08.03.03_V07.90.00">
			<EnumVal ord="0">no-error</EnumVal>
			<EnumVal ord="1">instance-not-available</EnumVal>
			<EnumVal ord="2">instance-in-use</EnumVal>
			<EnumVal ord="3">access-violation</EnumVal>
			<EnumVal ord="4">access-not-allowed-in-current-state</EnumVal>
			<EnumVal ord="5">parameter-value-inappropriate</EnumVal>
			<EnumVal ord="6">parameter-value-inconsistent</EnumVal>
			<EnumVal ord="7">class-not-supported</EnumVal>
			<EnumVal ord="8">instance-locked-by-other-client</EnumVal>
			<EnumVal ord="9">control-must-be-selected</EnumVal>
			<EnumVal ord="10">type-conflict</EnumVal>
			<EnumVal ord="11">failed-due-to-communications-constraint</EnumVal>
			<EnumVal ord="12">failed-due-to-server-constraint</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_DirectionGeneral_V08.03.03_V07.90.00">
			<EnumVal ord="0">unknown</EnumVal>
			<EnumVal ord="1">forward</EnumVal>
			<EnumVal ord="2">backward</EnumVal>
			<EnumVal ord="3">both</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_DirectionPhase_V08.03.03_V07.90.00">
			<EnumVal ord="0">unknown</EnumVal>
			<EnumVal ord="1">forward</EnumVal>
			<EnumVal ord="2">backward</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_PulseConfigCmdQual_V08.03.03_V07.90.00">
			<EnumVal ord="0">pulse</EnumVal>
			<EnumVal ord="1">persistent</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_ctlModel_status_only_and_dir_with_nor_sec_V08.03.03_V07.90.00">
			<EnumVal ord="0">status-only</EnumVal>
			<EnumVal ord="1">direct-with-normal-security</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_EnType_SwitchType_V08.03.03_V07.90.00">
			<EnumVal ord="1">Load Break</EnumVal>
			<EnumVal ord="2">Disconnector</EnumVal>
			<EnumVal ord="3">Earthing Switch</EnumVal>
			<EnumVal ord="4">High Speed Earthing Switch</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_EnType_InstrumentTransformerProtectionRatingKind_V08.03.03_V08.00.00">
			<EnumVal ord="1">1</EnumVal>
			<EnumVal ord="2">3</EnumVal>
			<EnumVal ord="3">5</EnumVal>
			<EnumVal ord="4">6</EnumVal>
			<EnumVal ord="5">10</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_EnType_InstrumentTransformerMeasurementRatingKind_V08.03.03_V08.00.00">
			<EnumVal ord="1">0.05</EnumVal>
			<EnumVal ord="2">0.1</EnumVal>
			<EnumVal ord="3">0.2</EnumVal>
			<EnumVal ord="4">0.2S</EnumVal>
			<EnumVal ord="5">0.5</EnumVal>
			<EnumVal ord="6">0.5S</EnumVal>
			<EnumVal ord="7">1</EnumVal>
			<EnumVal ord="8">3</EnumVal>
			<EnumVal ord="9">5</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_Trp_V08.03.03_V08.00.00">
			<EnumVal ord="1">Unknown</EnumVal>
			<EnumVal ord="2">P</EnumVal>
			<EnumVal ord="3">PR</EnumVal>
			<EnumVal ord="4">PX</EnumVal>
			<EnumVal ord="5">PXR</EnumVal>
			<EnumVal ord="6">TPX</EnumVal>
			<EnumVal ord="7">TPY</EnumVal>
			<EnumVal ord="8">TPZ</EnumVal>
			<EnumVal ord="9">TPE</EnumVal>
			<EnumVal ord="10">TPS</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_ctlModel_dir_with_enh_sec_V08.03.03_V07.90.00">
			<EnumVal ord="3">direct-with-enhanced-security</EnumVal>
		</EnumType>
		<EnumType id="SIPROTEC5_Textlist_SEQtype_V08.03.03_V07.90.00">
			<EnumVal ord="0">pos-neg-zero</EnumVal>
			<EnumVal ord="1">dir-quad-zero</EnumVal>
		</EnumType>
	</DataTypeTemplates>
</SCL>
