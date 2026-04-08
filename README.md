# MyVpn

Repository for the Android client and the VPN panel backend.

Structure:
- `app/` and root Gradle files: Android client
- `server/vpn_panel_mvp/`: FastAPI admin panel for Xray/VLESS Reality

## Android client

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

Build:

```powershell
cd C:\Users\v2ray-android
```

Then open the folder in Android Studio and let it:
- install the Android SDK if requested
- create the Gradle wrapper files
- sync the project
- run `assembleDebug`

Prerequisites:
- Android Studio with SDK 35
- JDK 17

## VPN panel backend

FastAPI panel for managing Xray clients.

Features:
- clients list
- create / enable / disable / delete client
- VLESS link generation
- QR generation
- accumulated traffic stats
- login page protected by `APP_SECRET`

Backend code is in [`server/vpn_panel_mvp`](server/vpn_panel_mvp).
