package com.fbcadman.myvpn

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.weight
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Divider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MyVpnTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background,
                ) {
                    VpnProfileScreen()
                }
            }
        }
    }
}

private data class VpnProfile(
    val name: String,
    val serverAddress: String,
    val serverPort: Int,
    val uuid: String,
    val flow: String,
    val publicKey: String,
    val shortId: String,
    val serverName: String,
    val fingerprint: String,
)

private val profile = VpnProfile(
    name = "My VPN",
    serverAddress = "138.249.117.110",
    serverPort = 8443,
    uuid = "45c06f1f-5439-409b-8dd4-ead90f55afbd",
    flow = "xtls-rprx-vision",
    publicKey = "e-z7Q-rS0lTPXOmSG4xpMHA2UytXHcJNu7CUO25QV1E",
    shortId = "c6cf36b847265708",
    serverName = "www.google.com",
    fingerprint = "chrome",
)

private val rawServerJson = """
{
  "inbounds": [
    {
      "port": 8443,
      "protocol": "vless",
      "settings": {
        "clients": [
          {
            "id": "45c06f1f-5439-409b-8dd4-ead90f55afbd",
            "flow": "xtls-rprx-vision"
          }
        ],
        "decryption": "none"
      },
      "streamSettings": {
        "network": "tcp",
        "security": "reality",
        "realitySettings": {
          "serverNames": [
            "www.google.com"
          ],
          "shortIds": [
            "c6cf36b847265708"
          ]
        }
      }
    }
  ]
}
""".trimIndent()

private fun VpnProfile.asVlessUri(): String {
    val query = listOf(
        "type=tcp",
        "security=reality",
        "encryption=none",
        "flow=$flow",
        "fp=$fingerprint",
        "sni=$serverName",
        "pbk=$publicKey",
        "sid=$shortId",
    ).joinToString("&")
    return "vless://$uuid@$serverAddress:$serverPort?$query#$name"
}

private fun VpnProfile.asXrayJson(): String = """
    {
      "remarks": "$name",
      "log": {
        "loglevel": "warning"
      },
      "inbounds": [
        {
          "tag": "socks",
          "port": 10808,
          "listen": "127.0.0.1",
          "protocol": "socks",
          "settings": {
            "udp": true
          }
        }
      ],
      "outbounds": [
        {
          "tag": "proxy",
          "protocol": "vless",
          "settings": {
            "vnext": [
              {
                "address": "$serverAddress",
                "port": $serverPort,
                "users": [
                  {
                    "id": "$uuid",
                    "encryption": "none",
                    "flow": "$flow"
                  }
                ]
              }
            ]
          },
          "streamSettings": {
            "network": "tcp",
            "security": "reality",
            "realitySettings": {
              "serverName": "$serverName",
              "fingerprint": "$fingerprint",
              "publicKey": "$publicKey",
              "shortId": "$shortId"
            }
          }
        }
      ]
    }
""".trimIndent()

@Composable
private fun VpnProfileScreen() {
    val context = LocalContext.current
    val profileLink = profile.asVlessUri()
    val profileJson = profile.asXrayJson()

    Scaffold { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Text(
                text = profile.name,
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
            )
            Text(
                text = "Android profile for your Xray server. The app stores the active VLESS Reality settings and can copy or share them into any compatible client.",
                style = MaterialTheme.typography.bodyLarge,
            )

            ProfileCard(title = "Server") {
                ProfileLine("Address", profile.serverAddress)
                ProfileLine("Port", profile.serverPort.toString())
                ProfileLine("Protocol", "VLESS + Reality")
                ProfileLine("Flow", profile.flow)
                ProfileLine("SNI", profile.serverName)
                ProfileLine("Public key", profile.publicKey)
                ProfileLine("Short ID", profile.shortId)
            }

            ProfileCard(title = "Actions") {
                Button(
                    modifier = Modifier.fillMaxWidth(),
                    onClick = {
                        context.openVpnLink(profileLink)
                    },
                ) {
                    Text("Open In VPN Client")
                }

                Divider()

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Button(
                        modifier = Modifier.weight(1f),
                        onClick = {
                            context.copyToClipboard("VLESS URI", profileLink)
                            context.toast("VLESS link copied")
                        },
                    ) {
                        Text("Copy VLESS")
                    }
                    Button(
                        modifier = Modifier.weight(1f),
                        onClick = {
                            context.shareText("My VPN VLESS", profileLink)
                        },
                    ) {
                        Text("Share VLESS")
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Button(
                        modifier = Modifier.weight(1f),
                        onClick = {
                            context.copyToClipboard("Xray JSON", profileJson)
                            context.toast("Xray JSON copied")
                        },
                    ) {
                        Text("Copy JSON")
                    }
                    Button(
                        modifier = Modifier.weight(1f),
                        onClick = {
                            context.shareText("My VPN Xray JSON", profileJson)
                        },
                    ) {
                        Text("Share JSON")
                    }
                }
            }

            ProfileCard(title = "VLESS URI") {
                Text(text = profileLink, style = MaterialTheme.typography.bodyMedium)
                TextButton(onClick = { context.copyToClipboard("VLESS URI", profileLink) }) {
                    Text("Copy")
                }
            }

            ProfileCard(title = "Server JSON") {
                Text(text = rawServerJson, style = MaterialTheme.typography.bodyMedium)
                TextButton(onClick = { context.copyToClipboard("Server JSON", rawServerJson) }) {
                    Text("Copy")
                }
            }

            ProfileCard(title = "Notes") {
                Text(
                    text = "This personal shell app keeps your server settings in one place. Install a client such as v2rayNG, then use Open In VPN Client or import the copied VLESS link.",
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
        }
    }
}

@Composable
private fun ProfileCard(
    title: String,
    content: @Composable () -> Unit,
) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant,
        ),
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(10.dp),
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold,
            )
            content()
        }
    }
}

@Composable
private fun ProfileLine(
    label: String,
    value: String,
) {
    Column(verticalArrangement = Arrangement.spacedBy(2.dp)) {
        Text(
            text = label,
            style = MaterialTheme.typography.labelLarge,
            color = MaterialTheme.colorScheme.primary,
        )
        Text(text = value, style = MaterialTheme.typography.bodyLarge)
    }
}

private fun Context.copyToClipboard(label: String, text: String) {
    val clipboard = getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
    clipboard.setPrimaryClip(ClipData.newPlainText(label, text))
}

private fun Context.shareText(subject: String, text: String) {
    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(Intent.EXTRA_SUBJECT, subject)
        putExtra(Intent.EXTRA_TEXT, text)
    }
    startActivity(Intent.createChooser(intent, "Share VPN profile"))
}

private fun Context.openVpnLink(text: String) {
    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(text)).apply {
        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    }
    val chooser = Intent.createChooser(intent, "Open VPN profile")
    chooser.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    if (intent.resolveActivity(packageManager) != null) {
        startActivity(chooser)
    } else {
        toast("No compatible VPN client found")
    }
}

private fun Context.toast(message: String) {
    Toast.makeText(this, message, Toast.LENGTH_SHORT).show()
}
