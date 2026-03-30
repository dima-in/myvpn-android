# MyVpn Android

Minimal Android companion app for your Xray server.

What it does:
- stores the active `VLESS + Reality` profile from your server
- shows the connection parameters
- opens the `vless://` profile in an installed Android VPN client
- copies or shares a ready `vless://` link
- copies or shares an `Xray` JSON profile

What it does not do:
- it does not embed `xray-core`
- it does not create a system VPN tunnel by itself

How to use it:
- install the APK on Android
- install a compatible client such as `v2rayNG`
- press `Open In VPN Client` in the app
- if direct opening is not handled, copy the `VLESS URI` and import it manually

Build:

```powershell
cd C:\Users\fb.cadman\v2ray-android
```

Then open the folder in Android Studio and let it:
- install the Android SDK if requested
- create the Gradle wrapper files
- sync the project
- run `assembleDebug`

Prerequisites on the work computer:
- Android Studio with SDK 35
- JDK 17 (bundled with recent Android Studio)

Server profile currently embedded:
- address: `138.249.117.110`
- port: `8443`
- protocol: `VLESS + Reality`
- SNI: `www.google.com`
