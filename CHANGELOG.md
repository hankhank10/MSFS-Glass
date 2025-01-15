# Change Log

**Update 01/15/2025 Version 2.0.0-alpha-1 Changelog:**
- Credit where credit is due:
   - [https://github.com/mracko/MSFS-Mobile-Companion-App](https://github.com/mracko/MSFS-Mobile-Companion-App/)
   - [https://github.com/odwdinc/Python-SimConnect](https://github.com/odwdinc/Python-SimConnect)
- Created a new repo, due to abandoning the original repos
- Updated DLL and header definitions to the SDK of MSFS2024
- Implemented [Input events](https://docs.flightsimulator.com/html/Programming_Tools/SimConnect/SimConnect_API_Reference.htm#inputevents) to be able to control avionics without an external WASM (MobiFlight) module
- Started working on Frontend revamp 
- Merged some pull requests on the original repos
- Cherry-picked changes from each repo to have all the changes in one place
- Updated OpenAIP integration for maps to load
- Added API key inputs for OpenAIP
- Started implementing G1000 avionics to work with Input Events
- Started implementing airliners (A32x) to work with Input Events
- Started implementing automatic UI selection for selected aircraft
- Started optimizing imports and memory footprint
- Created a framework for logging & easier debugging
- **NO BINARIES HAVE BEEN BUILT FOR THIS VERSION**

**v1.9.1 November 3, 2021:**
- Added controls profile for the Ju-52 Classic and Retrofit by Asobo
- Improved UI for all NAV controls
- Removed pop-up for panel switches
- Added approximate G-forces at touchdown in the Data tab

**v1.9 August 30, 2021:**
- Updated and improved controls profile for FBW's A32NX stable v0.6.3 and development version
- Added feature to upload custom KML files (thanks to @luka97)
- Added ADF 1/2 selector for PMDG's DC-6
- Added feature to hide the plane icon on the map. The lower left map button has 3 states now: "Follow plane" -> "Unfollow plane" -> "Hide plane"

**v1.8.2 July 11, 2021:**
- Added controls profile for the DC-6 by PMDG. Supports NAV, ADF, COM, XPNDR, Gyropilot and the Artificial Flight Engineer.
- Minor UI improvements.

**v1.8.1 June 14, 2021:**
- CPU performance issue hotfix.

**v1.8 June 14, 2021:**
- Added controls profile for the FG-1D Corsair by MilViz.
- Improved UI especially for the default AP and the PA-28R.
- Added ability to read L:vars thanks to https://github.com/Koseng/MSFSPythonSimConnectMobiFlightExtension

**v1.7 May 14, 2021:**
- Added controls profile for MB-339 and Long-EZ by IndiaFoxtEcho.
- Added gear, flaps, spoilers and trim (elevator, rudder and aileron) controls.
- Added press-and-hold button functionality for frequency tune buttons.
- Improved performance for map tracking (fixed jagged lines).
- Fixed logo lights button status being mapped to cabin lights.

**v1.6.1 April 20, 2021:**
- Added controls profile for CRJ-550/700 (Aerosoft). The profile includes controls for FCP, Side Panel, NAV, and COM and introduces press-and-hold button functionality for knobs.
- Updated controls profile for PA-28R (Just Flight) to reflect v0.4.0 changes.
- Fixed zoom when double-tapping on iOS.

**v1.6 March 29, 2021:**
- Added aircraft controls profile selection.
- Added controls profiles for GNS430/530, G1000, A32NX (FBW), and PA-28R (Just Flight).
- Added integration with Mobiflight WASM Event Module.
- Added Data tab with IAS, ALT, HDG data
- Added Sync HDG bug to current heading
- Fixed NAV frequency display UI for iOS (padding for NAV frequency display)

**v1.5.2 Hotfix March 4, 2021:**
- Fixed bug for iOS devices not being able to type in decimal numbers in COM/NAV frequencies.

**v1.5.1 Hotfix February 8, 2021:**
- Fixed Load Flight Plan not working on Steam versions.

**v1.5 February 5, 2021:**
- Added landscape mode (split-screen for map and controls).
- Added option to load your current flight plan.
- Switched active and stand-by NAV/COM displays.

**v1.4 January 6, 2021:**
- Dedicated A320 autopilot controls (tested with default A320 and FBW A32NX v0.5.1).
- Various UI fixes, especially for iOS devices.
- UI improvements for color-blind users.

**v1.3 December 16, 2020:**
- FLC autopilot implemented.
- Added GPS track line for the VFR map.
- Added light controls.
- Added pitot heat and deicing controls (deicing controls may be limited depending on the plane, windshield deicing is not yet supported by SimConnect).

**v1.2 November 20, 2020:**
- Added COM1/2 and transponder.
- Added vertical speed at touchdown.
- Added simulation rate controls.
- Improved stability and performance. Multiple devices/browsers can now connect to the app concurrently.
- Added dark moving map style.
- Fixed default moving map not displaying.
- Various minor bug fixes.

**v1.1 November 11, 2020:**
- Improved AP functionality. ALT AP can now be used with current or set altitude.
- Added autothrottle toggle.
- Added NAV1/NAV2 source switch for AP and/or CDI.
- Added ADF direct frequency tune option.
- Improved UI for the NAV tab.
- The application doesn't crash when launching before MSFS is running.
- Various other minor bug fixes.

**v1.0 November 3, 2020:**
- Initial release.
- Moving Map (Open Street Maps).
- NAV 1 frequency and OBS 1 selection.
- NAV 2 frequency and OBS 2 selection.
- ADF frequency and ADF card selection.
- Autopilot with altitude, vertical speed, and airspeed settings.
- Gyro drift and altimeter pressure settings.
