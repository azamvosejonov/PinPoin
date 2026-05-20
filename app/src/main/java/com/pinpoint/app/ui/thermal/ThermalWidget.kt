package com.pinpoint.app.ui.thermal

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Thermostat
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@Composable
fun ThermalWidget(
    currentTemp: Double?,
    predictedTemp: Double?,
    etaMinutes: Int?,
    riskLevel: String?,
    modifier: Modifier = Modifier
) {
    val riskColor by animateColorAsState(
        targetValue = when (riskLevel) {
            "LOW" -> Color(0xFF4CAF50)
            "MEDIUM" -> Color(0xFFFFC107)
            "HIGH" -> Color(0xFFF44336)
            else -> Color.Gray
        },
        animationSpec = tween(500),
        label = "riskColor"
    )

    val tempProgress by animateFloatAsState(
        targetValue = ((currentTemp ?: 0.0) / 100.0).toFloat().coerceIn(0f, 1f),
        animationSpec = tween(800),
        label = "tempProgress"
    )

    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = riskColor.copy(alpha = 0.08f)
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        Icons.Default.Thermostat,
                        contentDescription = null,
                        tint = riskColor,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Harorat nazorati",
                        style = MaterialTheme.typography.titleSmall,
                        fontWeight = FontWeight.Bold
                    )
                }

                riskLevel?.let { risk ->
                    RiskBadge(risk = risk, color = riskColor)
                }
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceEvenly
            ) {
                TempColumn(
                    label = "Hozirgi",
                    temp = currentTemp,
                    color = riskColor
                )
                TempColumn(
                    label = "Bashorat",
                    temp = predictedTemp,
                    color = riskColor.copy(alpha = 0.6f)
                )
                etaMinutes?.let {
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text(
                            text = "ETA",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                        Text(
                            text = "${it} daq",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }

            LinearProgressIndicator(
                progress = tempProgress,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(6.dp),
                color = riskColor,
                trackColor = riskColor.copy(alpha = 0.15f),
                strokeCap = StrokeCap.Round
            )

            if (riskLevel == "HIGH") {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Icon(
                        Icons.Default.Warning,
                        contentDescription = null,
                        tint = Color(0xFFF44336),
                        modifier = Modifier.size(16.dp)
                    )
                    Text(
                        text = "Ovqat sovub qolish xavfi bor! Tezroq yetkazib bering.",
                        style = MaterialTheme.typography.bodySmall,
                        color = Color(0xFFF44336)
                    )
                }
            }
        }
    }
}

@Composable
private fun TempColumn(label: String, temp: Double?, color: Color) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = if (temp != null) "${String.format("%.1f", temp)}°C" else "—",
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = color
        )
    }
}

@Composable
private fun RiskBadge(risk: String, color: Color) {
    val label = when (risk) {
        "LOW" -> "Past"
        "MEDIUM" -> "O'rta"
        "HIGH" -> "Yuqori"
        else -> risk
    }
    Box(
        modifier = Modifier
            .padding(horizontal = 4.dp)
    ) {
        Card(
            colors = CardDefaults.cardColors(containerColor = color.copy(alpha = 0.15f)),
            shape = RoundedCornerShape(8.dp)
        ) {
            Text(
                text = label,
                modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                color = color,
                fontSize = 12.sp,
                fontWeight = FontWeight.Bold
            )
        }
    }
}
