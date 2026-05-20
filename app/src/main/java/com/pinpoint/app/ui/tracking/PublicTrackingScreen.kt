package com.pinpoint.app.ui.tracking

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.pinpoint.app.domain.model.OrderTracking

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PublicTrackingScreen(
    orderTracking: OrderTracking?,
    isLoading: Boolean,
    error: String?,
    onTrack: (String) -> Unit
) {
    var trackingHash by remember { mutableStateOf("") }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Buyurtmani Kuzatish") }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            error?.let {
                Text(
                    text = it,
                    color = MaterialTheme.colorScheme.error
                )
            }

            Card(
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = "Kuzatish kodini kiriting",
                        style = MaterialTheme.typography.titleMedium
                    )
                    OutlinedTextField(
                        value = trackingHash,
                        onValueChange = { trackingHash = it },
                        label = { Text("Tracking Hash") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true
                    )
                    Button(
                        onClick = { onTrack(trackingHash) },
                        modifier = Modifier.fillMaxWidth(),
                        enabled = trackingHash.isNotBlank() && !isLoading
                    ) {
                        if (isLoading) {
                            CircularProgressIndicator(
                                modifier = Modifier.size(24.dp),
                                color = MaterialTheme.colorScheme.onPrimary
                            )
                        } else {
                            Text("Kuzatish")
                        }
                    }
                }
            }

            orderTracking?.let { tracking ->
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "Buyurtma Ma'lumotlari",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text("Buyurtma kodi: ${tracking.orderCode}")
                        Text("Holat: ${tracking.status}")
                        Text("Kuryer ID: ${tracking.courierId}")
                        Text("Kuryer ismi: ${tracking.courierName}")
                        Text("Olib ketish manzili: ${tracking.pickupAddress}")
                        Text("Yetkazib berish manzili: ${tracking.dropoffAddress}")
                        Text("Yaratilgan: ${tracking.createdAt}")
                        tracking.acceptedAt?.let { Text("Qabul qilingan: $it") }
                        tracking.pickedUpAt?.let { Text("Olib ketilgan: $it") }
                        tracking.deliveredAt?.let { Text("Yetkazib berilgan: $it") }
                        tracking.estimatedDelivery?.let { Text("Taxminiy yetkazib berish: $it") }
                    }
                }
            }
        }
    }
}
