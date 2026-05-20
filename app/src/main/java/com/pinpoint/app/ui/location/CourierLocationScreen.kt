package com.pinpoint.app.ui.location

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.pinpoint.app.domain.model.CourierLocation

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CourierLocationScreen(
    courierLocation: CourierLocation?,
    currentLocation: Pair<Double, Double>?,
    isLoading: Boolean,
    isTracking: Boolean,
    error: String?,
    onUpdateLocation: (Double, Double) -> Unit,
    onRefresh: () -> Unit,
    onStartTracking: () -> Unit,
    onStopTracking: () -> Unit
) {
    var latitude by remember { mutableStateOf(currentLocation?.first?.toString() ?: courierLocation?.latitude?.toString() ?: "") }
    var longitude by remember { mutableStateOf(currentLocation?.second?.toString() ?: courierLocation?.longitude?.toString() ?: "") }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Kuryer Joylashuvi") }
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
                    color = MaterialTheme.colorScheme.error,
                    modifier = Modifier.padding(bottom = 8.dp)
                )
            }

            // Real-time tracking status
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = if (isTracking) CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                ) else CardDefaults.cardColors()
            ) {
                Row(
                    modifier = Modifier.padding(16.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = if (isTracking) "Real-time tracking ON" else "Real-time tracking OFF",
                            style = MaterialTheme.typography.titleMedium
                        )
                        currentLocation?.let { (lat, lon) ->
                            Text(
                                text = "Hozirgi: $lat, $lon",
                                style = MaterialTheme.typography.bodySmall
                            )
                        }
                    }
                    Switch(
                        checked = isTracking,
                        onCheckedChange = { if (it) onStartTracking() else onStopTracking() }
                    )
                }
            }

            courierLocation?.let { location ->
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "Server joylashuvi",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = "Kuryer ID: ${location.courierId}",
                            style = MaterialTheme.typography.bodyLarge
                        )
                        Text(
                            text = "Latitude: ${location.latitude}",
                            style = MaterialTheme.typography.bodyLarge
                        )
                        Text(
                            text = "Longitude: ${location.longitude}",
                            style = MaterialTheme.typography.bodyLarge
                        )
                        Text(
                            text = "Yangilangan: ${location.updatedAt}",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
            } ?: Text("Joylashuv ma'lumotlari yo'q")

            OutlinedTextField(
                value = latitude,
                onValueChange = { latitude = it },
                label = { Text("Latitude") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )

            OutlinedTextField(
                value = longitude,
                onValueChange = { longitude = it },
                label = { Text("Longitude") },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true
            )

            Button(
                onClick = {
                    val lat = latitude.toDoubleOrNull() ?: 0.0
                    val lon = longitude.toDoubleOrNull() ?: 0.0
                    onUpdateLocation(lat, lon)
                },
                modifier = Modifier.fillMaxWidth(),
                enabled = latitude.isNotBlank() && longitude.isNotBlank() && !isLoading
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                } else {
                    Text("Joylashuvni yangilash")
                }
            }

            Button(
                onClick = onRefresh,
                modifier = Modifier.fillMaxWidth(),
                enabled = !isLoading
            ) {
                Text("Yangilash")
            }
        }
    }
}
