package com.pinpoint.app.ui.order

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.pinpoint.app.domain.model.Order
import com.pinpoint.app.domain.model.OrderStatus
import com.pinpoint.app.domain.model.PaymentMethod

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OrderDetailScreen(
    order: Order,
    onBack: () -> Unit,
    onUpdateStatus: (OrderStatus) -> Unit,
    onDecline: (String) -> Unit,
    onCallClient: () -> Unit
) {
    var showDeclineDialog by remember { mutableStateOf(false) }
    var declineReason by remember { mutableStateOf("") }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Buyurtma ${order.orderCode}") },
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
            StatusBadge(status = order.status)
            
            order.pickupAddress?.let {
                InfoCard(title = "Olib ketish manzili", value = it)
            }

            order.dropoffAddress?.let {
                InfoCard(title = "Tashrif manzili", value = it)
            }

            InfoCard(title = "To'lov usuli", value = order.paymentMethod.name)
            
            order.totalAmount?.let {
                InfoCard(title = "Summa", value = "$it so'm")
            }

            if (order.declinedCourierIds != null) {
                InfoCard(
                    title = "Rad etgan kuryerlar",
                    value = order.declinedCourierIds,
                    color = MaterialTheme.colorScheme.error
                )
            }

            InfoCard(title = "Urinishlar", value = "${order.retryCount}/${order.maxRetries}")

            if (order.status == OrderStatus.UNASSIGNABLE) {
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text(
                            text = "Kuryerlar tugadi!",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onErrorContainer
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Barcha kuryerlar rad qildi yoki online emas. Operator bilan bog'laning.",
                            color = MaterialTheme.colorScheme.onErrorContainer
                        )
                    }
                }
            }

            if (order.status == OrderStatus.DELIVERY_FAILED) {
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.tertiaryContainer
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text(
                            text = "Yetkazib berilmadi",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.onTertiaryContainer
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = "Ovqatni restoranga qaytaring",
                            color = MaterialTheme.colorScheme.onTertiaryContainer
                        )
                    }
                }
            }

            when (order.status) {
                OrderStatus.ACCEPTED,
                OrderStatus.READY_FOR_PICKUP -> {
                    ActionButtons(
                        onPrimary = { onUpdateStatus(OrderStatus.PICKED_UP) },
                        primaryText = "Olib ketdim",
                        onSecondary = { showDeclineDialog = true },
                        secondaryText = "Rad qilish"
                    )
                }
                OrderStatus.PICKED_UP -> {
                    ActionButtons(
                        onPrimary = { onUpdateStatus(OrderStatus.DELIVERED) },
                        primaryText = "Yetkazdim",
                        onSecondary = { onUpdateStatus(OrderStatus.DELIVERY_FAILED) },
                        secondaryText = "Yetkazib berolmadim"
                    )
                }
                OrderStatus.DELIVERY_FAILED -> {
                    Button(
                        onClick = { onUpdateStatus(OrderStatus.RETURNED_TO_RESTAURANT) },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Restoranga qaytardim")
                    }
                }
                else -> {}
            }

            if (order.paymentMethod == PaymentMethod.CASH && order.status == OrderStatus.DELIVERED) {
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text(
                            text = "Naqd pul to'lov",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(text = "Summa: ${order.totalAmount ?: 0} so'm")
                    }
                }
            }
        }
    }

    if (showDeclineDialog) {
        AlertDialog(
            onDismissRequest = { showDeclineDialog = false },
            title = { Text("Buyurtmani rad qilish") },
            text = {
                Column {
                    Text("Sababni kiriting:")
                    Spacer(modifier = Modifier.height(8.dp))
                    OutlinedTextField(
                        value = declineReason,
                        onValueChange = { declineReason = it },
                        placeholder = { Text("Sabab...") },
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        onDecline(declineReason)
                        showDeclineDialog = false
                    },
                    enabled = declineReason.isNotBlank()
                ) {
                    Text("Rad qilish")
                }
            },
            dismissButton = {
                TextButton(onClick = { showDeclineDialog = false }) {
                    Text("Bekor qilish")
                }
            }
        )
    }
}

@Composable
fun InfoCard(title: String, value: String, color: androidx.compose.ui.graphics.Color = MaterialTheme.colorScheme.onSurface) {
    Card {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = value,
                style = MaterialTheme.typography.bodyLarge,
                fontWeight = FontWeight.Medium,
                color = color
            )
        }
    }
}

@Composable
fun ActionButtons(
    onPrimary: () -> Unit,
    primaryText: String,
    onSecondary: () -> Unit,
    secondaryText: String
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Button(
            onClick = onSecondary,
            modifier = Modifier.weight(1f),
            colors = ButtonDefaults.buttonColors(
                containerColor = MaterialTheme.colorScheme.secondary
            )
        ) {
            Text(secondaryText)
        }
        Button(
            onClick = onPrimary,
            modifier = Modifier.weight(1f)
        ) {
            Text(primaryText)
        }
    }
}
