package com.pinpoint.app.ui.courier

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.OfflineBolt
import androidx.compose.material.icons.filled.Wifi
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.pinpoint.app.domain.model.CourierStatus
import com.pinpoint.app.domain.model.CourierStatusEnum

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CourierStatusScreen(
    courierStatus: CourierStatus?,
    onBack: () -> Unit,
    onUpdateStatus: (CourierStatusEnum) -> Unit,
    onCollectCash: (Double) -> Unit
) {
    var selectedAmount by remember { mutableStateOf("") }
    var showCashDialog by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Kuryer Statusi") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Orqaga")
                    }
                }
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
            courierStatus?.let { status ->
                StatusCard(status = status)
                
                Spacer(modifier = Modifier.height(16.dp))

                Text(
                    text = "Statusni o'zgartirish",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    StatusButton(
                        status = CourierStatusEnum.ONLINE,
                        currentStatus = status.status,
                        onClick = { onUpdateStatus(CourierStatusEnum.ONLINE) },
                        modifier = Modifier.weight(1f)
                    )
                    StatusButton(
                        status = CourierStatusEnum.ON_BREAK,
                        currentStatus = status.status,
                        onClick = { onUpdateStatus(CourierStatusEnum.ON_BREAK) },
                        modifier = Modifier.weight(1f)
                    )
                }

                StatusButton(
                    status = CourierStatusEnum.OFFLINE,
                    currentStatus = status.status,
                    onClick = { onUpdateStatus(CourierStatusEnum.OFFLINE) },
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(16.dp))

                CashBalanceCard(
                    cashBalance = status.cashBalance,
                    onCollectCash = { showCashDialog = true }
                )
            } ?: run {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
        }
    }

    if (showCashDialog) {
        AlertDialog(
            onDismissRequest = { showCashDialog = false },
            title = { Text("Pul yig'ish") },
            text = {
                Column {
                    Text("Yig'iladigan summani kiriting:")
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedTextField(
                        value = selectedAmount,
                        onValueChange = { selectedAmount = it },
                        placeholder = { Text("Summa (so'm)...") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("Joriy balans: ${courierStatus?.cashBalance ?: 0} so'm")
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        selectedAmount.toDoubleOrNull()?.let {
                            onCollectCash(it)
                            showCashDialog = false
                            selectedAmount = ""
                        }
                    },
                    enabled = selectedAmount.isNotBlank() && selectedAmount.toDoubleOrNull() != null
                ) {
                    Text("Yig'ish")
                }
            },
            dismissButton = {
                TextButton(onClick = { showCashDialog = false }) {
                    Text("Bekor qilish")
                }
            }
        )
    }
}

@Composable
fun StatusCard(status: CourierStatus) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = when (status.status) {
                CourierStatusEnum.ONLINE -> MaterialTheme.colorScheme.primaryContainer
                CourierStatusEnum.BUSY -> MaterialTheme.colorScheme.tertiaryContainer
                CourierStatusEnum.OFFLINE -> MaterialTheme.colorScheme.secondaryContainer
                CourierStatusEnum.ON_BREAK -> MaterialTheme.colorScheme.errorContainer
            }
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(
                    imageVector = when (status.status) {
                        CourierStatusEnum.ONLINE -> Icons.Default.Wifi
                        CourierStatusEnum.BUSY -> Icons.Default.CheckCircle
                        CourierStatusEnum.OFFLINE -> Icons.Default.OfflineBolt
                        CourierStatusEnum.ON_BREAK -> Icons.Default.Close
                    },
                    contentDescription = null
                )
                Text(
                    text = status.status.name,
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "Oxirgi yangilanish: ${status.updatedAt}",
                style = MaterialTheme.typography.bodySmall
            )

            status.lastOnlineAt?.let {
                Text(
                    text = "Oxirgi online: $it",
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

@Composable
fun StatusButton(
    status: CourierStatusEnum,
    currentStatus: CourierStatusEnum,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val isActive = status == currentStatus
    Button(
        onClick = onClick,
        modifier = modifier,
        enabled = !isActive,
        colors = ButtonDefaults.buttonColors(
            containerColor = when (status) {
                CourierStatusEnum.ONLINE -> MaterialTheme.colorScheme.primary
                CourierStatusEnum.BUSY -> MaterialTheme.colorScheme.tertiary
                CourierStatusEnum.OFFLINE -> MaterialTheme.colorScheme.secondary
                CourierStatusEnum.ON_BREAK -> MaterialTheme.colorScheme.error
            }
        )
    ) {
        Text(status.name)
    }
}

@Composable
fun CashBalanceCard(
    cashBalance: Double,
    onCollectCash: () -> Unit
) {
    Card(
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = "Naqd pul balansi",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "$cashBalance so'm",
                style = MaterialTheme.typography.headlineSmall,
                fontWeight = FontWeight.Bold
            )
            if (cashBalance > 0) {
                Spacer(modifier = Modifier.height(8.dp))
                Button(
                    onClick = onCollectCash,
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text("Pul yig'ish")
                }
            }
        }
    }
}
