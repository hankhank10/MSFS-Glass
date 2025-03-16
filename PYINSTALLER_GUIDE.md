# MSFS Glass Pyinstaller Instructions

To compile an executable version of MSFS Glass using pyinstaller follow these 4 steps:

## 1. Create SimConnect.dllc

Copy the *SimConnect.dll* file into *SimConnect.dllc*.

## 2. Compile MSFS Glass using pyinstaller

Use the following pyinstaller settings to compile MSFS Glass:

```
pyinstaller -F  --add-data "templates;templates" --add-data "static;static" --add-data "SimConnect;SimConnect" --icon="images/icon.ico" --name="glass_server.exe" glass_server.py
```

## 3. Enjoy and have fun!
