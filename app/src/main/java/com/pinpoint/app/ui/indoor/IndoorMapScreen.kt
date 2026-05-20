package com.pinpoint.app.ui.indoor

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.pinpoint.app.domain.model.IndoorMap
import com.pinpoint.app.domain.model.IndoorPathDetail
import com.pinpoint.app.domain.model.IsometricTile

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun IndoorMapScreen(
    indoorMap: IndoorMap?,
    indoorPaths: List<IndoorPathDetail>,
    floorTiles: List<IsometricTile> = emptyList(),
    courierPosition: Pair<Int, Int>? = null,
    isLoading: Boolean,
    error: String?,
    onLoadMap: (String) -> Unit,
    onCreatePath: (String) -> Unit
) {
    var externalId by remember { mutableStateOf("") }
    var floorNumber by remember { mutableStateOf("1") }
    var startX by remember { mutableStateOf("0") }
    var startY by remember { mutableStateOf("0") }
    var endX by remember { mutableStateOf("0") }
    var endY by remember { mutableStateOf("0") }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Ichki Xarita") }
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

            // Load Map Section
            Card(
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = "Xaritani yuklash",
                        style = MaterialTheme.typography.titleMedium
                    )
                    OutlinedTextField(
                        value = externalId,
                        onValueChange = { externalId = it },
                        label = { Text("Bino External ID") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true
                    )
                    Button(
                        onClick = { onLoadMap(externalId) },
                        modifier = Modifier.fillMaxWidth(),
                        enabled = externalId.isNotBlank() && !isLoading
                    ) {
                        Text("Xaritani yuklash")
                    }
                }
            }

            // Indoor Map Display
            indoorMap?.let { map ->
                Card(
                    modifier = Modifier.fillMaxWidth()
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
                            Text(
                                text = "2.5D Ichki Xarita",
                                style = MaterialTheme.typography.titleMedium
                            )
                            Text(
                                text = "Qavat: ${map.floorNumber}",
                                style = MaterialTheme.typography.bodySmall
                            )
                        }

                        if (floorTiles.isNotEmpty()) {
                            IsometricMapRenderer(
                                tiles = floorTiles,
                                courierPosition = courierPosition,
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(300.dp)
                            )
                        } else {
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .height(200.dp),
                                contentAlignment = Alignment.Center
                            ) {
                                Text("Xarita plitkalari yuklanmoqda...")
                            }
                        }

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceEvenly
                        ) {
                            Text("ID: ${map.id}", style = MaterialTheme.typography.bodySmall)
                            Text("O'lcham: ${map.width ?: "?"}x${map.height ?: "?"}", style = MaterialTheme.typography.bodySmall)
                        }
                    }
                }
            }

            // Create Path Section
            Card(
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Text(
                        text = "Ichki Yo'l Yaratish",
                        style = MaterialTheme.typography.titleMedium
                    )
                    OutlinedTextField(
                        value = floorNumber,
                        onValueChange = { floorNumber = it },
                        label = { Text("Qavat raqami") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true
                    )
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        OutlinedTextField(
                            value = startX,
                            onValueChange = { startX = it },
                            label = { Text("Boshlang'ich X") },
                            modifier = Modifier.weight(1f),
                            singleLine = true
                        )
                        OutlinedTextField(
                            value = startY,
                            onValueChange = { startY = it },
                            label = { Text("Boshlang'ich Y") },
                            modifier = Modifier.weight(1f),
                            singleLine = true
                        )
                    }
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        OutlinedTextField(
                            value = endX,
                            onValueChange = { endX = it },
                            label = { Text("Tugash X") },
                            modifier = Modifier.weight(1f),
                            singleLine = true
                        )
                        OutlinedTextField(
                            value = endY,
                            onValueChange = { endY = it },
                            label = { Text("Tugash Y") },
                            modifier = Modifier.weight(1f),
                            singleLine = true
                        )
                    }
                    Button(
                        onClick = { onCreatePath(externalId) },
                        modifier = Modifier.fillMaxWidth(),
                        enabled = externalId.isNotBlank() && !isLoading
                    ) {
                        Text("Yo'l yaratish")
                    }
                }
            }

            // Paths List
            if (indoorPaths.isNotEmpty()) {
                Card(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        Text(
                            text = "Ichki Yo'llar (${indoorPaths.size})",
                            style = MaterialTheme.typography.titleMedium
                        )
                        indoorPaths.forEach { path ->
                            Text("ID: ${path.id}, Qavat: ${path.floorNumber}")
                        }
                    }
                }
            }
        }
    }
}
