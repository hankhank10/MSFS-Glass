# MSFS Glass Pyinstaller Instructions

To compile an executable version of MSFS Glass using pyinstaller follow these 4 steps:

## 1. Rename SimConnect.dll

Rename the *SimConnect.dll* file into *SimConnect.dllc*.

## 2. Compile MSFS Glass using pyinstaller

Use the following pyinstaller settings to compile MSFS Glass:

```
pyinstaller -F --onefile --add-data "templates;templates" --add-data "static;static" --add-data "SimConnect;SimConnect" glass_server.py
```

## 3. Enjoy and have fun!
