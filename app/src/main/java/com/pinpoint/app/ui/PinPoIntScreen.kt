package com.pinpoint.app.ui

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.pinpoint.app.R
import com.pinpoint.app.ui.overlay.DomofonOverlay
import com.pinpoint.app.util.SpeechHelper
import com.pinpoint.app.ui.map.OsmMapView
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.overlay.Marker

@Composable
fun PinPoIntScreen(
    state: PinPoIntState,
    onDelivered: () -> Unit,
    onRequestDomofonCode: () -> Unit,
    onCopyCode: () -> Unit,
    onCallClient: () -> Unit
) {
    val context = LocalContext.current

    Surface {
        Column(modifier = Modifier.fillMaxSize()) {
            MapPreview(
                state = state,
                modifier = Modifier.weight(1f)
            )
            DeliveryInfoPanel(
                state = state,
                onDelivered = onDelivered,
                onRequestDomofonCode = onRequestDomofonCode,
                onCopyCode = onCopyCode,
                onCallClient = onCallClient,
                context = context
            )
        }
    }
}

@Composable
fun MapPreview(state: PinPoIntState, modifier: Modifier = Modifier) {
    val context = LocalContext.current
    Box(modifier = modifier.fillMaxWidth()) {
        OsmMapView(modifier = Modifier.fillMaxSize()) { mapView ->
            val basePoint = state.adjustedCoordinate ?: state.building?.coordinate
            basePoint?.let {
                val geoPoint = GeoPoint(it.latitude, it.longitude)
                mapView.controller.setCenter(geoPoint)
                mapView.overlays.clear()

                val pinMarker = Marker(mapView).apply {
                    position = geoPoint
                    title = state.building?.address ?: "Aniq manzil"
                    icon = context.getDrawable(R.drawable.ic_map_pin)
                }
                mapView.overlays.add(pinMarker)

                state.building?.entrances?.forEach { entrance ->
                    val entranceMarker = Marker(mapView).apply {
                        position = GeoPoint(entrance.coordinate.latitude, entrance.coordinate.longitude)
                        title = "Podyezd ${entrance.label}"
                        icon = context.getDrawable(R.drawable.ic_entrance)
                    }
                    mapView.overlays.add(entranceMarker)
                }
                mapView.invalidate()
            }
        }
    }
}

@Composable
fun DeliveryInfoPanel(
    state: PinPoIntState,
    onDelivered: () -> Unit,
    onRequestDomofonCode: () -> Unit,
    onCopyCode: () -> Unit,
    onCallClient: () -> Unit,
    context: android.content.Context
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.surface)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        state.building?.let { building ->
            Column {
                Text(
                    text = building.address,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(text = "Qiyinchilik: ${building.difficultyIndex}/5")
                if (!state.domofonCode.isNullOrEmpty()) {
                    DomofonOverlay(
                        code = state.domofonCode,
                        onCopy = onCopyCode,
                        onSpeak = { SpeechHelper.speak(context, state.domofonCode) }
                    )
                } else {
                    TextButton(onClick = onRequestDomofonCode) {
                        Text(text = "Domofon kodini ko'rsat")
                    }
                }
            }
        }

        state.projection?.let { projection ->
            TemperatureWidget(projection = projection)
        }

        state.thermalAdvice?.let { advice ->
            Text(text = "ETA (bino bilan): ${advice.totalEtaMinutes} daqiqa", fontWeight = FontWeight.Medium)
            advice.warningMessage?.let {
                WarningCard(message = it)
            }
        }

        if (state.alerts.isNotEmpty()) {
            AlertsList(alerts = state.alerts)
        }

        Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
            Button(onClick = onCallClient, modifier = Modifier.weight(1f)) {
                Text(text = "Qo'ng'iroq")
            }
            Spacer(modifier = Modifier.width(12.dp))
            Button(onClick = onDelivered, modifier = Modifier.weight(1f)) {
                Text(text = "Yetkazdim")
            }
        }
    }
}

@Composable
fun TemperatureWidget(projection: com.pinpoint.app.domain.model.ThermalProjection) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.primaryContainer, RoundedCornerShape(16.dp))
            .padding(16.dp)
    ) {
        Text(text = "Harorat", fontWeight = FontWeight.Bold)
        Spacer(modifier = Modifier.height(8.dp))
        Text(text = "Boshlang'ich: ${projection.currentTemperature}°C",
            fontSize = 16.sp)
        Text(text = "Prognoz: ${projection.predictedTemperature}°C",
            fontSize = 16.sp)
        Text(text = "Risk: ${projection.riskLevel}", fontSize = 16.sp)
    }
}

@Composable
fun WarningCard(message: String) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .background(Color(0xFFFFEB3B), RoundedCornerShape(12.dp))
            .padding(12.dp)
    ) {
        Text(text = message, color = Color(0xFF3E2723), fontWeight = FontWeight.Medium)
    }
}

@Composable
fun AlertsList(alerts: List<String>) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        alerts.forEach { alert ->
            WarningCard(message = alert)
        }
    }
}
