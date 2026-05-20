package com.pinpoint.app.ui.order

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.ExperimentalMaterial3Api
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
fun OrderListScreen(
    orders: List<Order>,
    onOrderClick: (Order) -> Unit,
    onRefresh: () -> Unit,
    isLoading: Boolean = false
) {
    Column(
        modifier = Modifier.fillMaxSize()
    ) {
        TopAppBar(
            title = { Text("Buyurtmalar") },
            actions = {
                IconButton(onClick = onRefresh) {
                    Icon(Icons.Default.Refresh, contentDescription = "Yangilash")
                }
            }
        )

        if (isLoading) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                CircularProgressIndicator()
            }
        } else if (orders.isEmpty()) {
            Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center
            ) {
                Text("Buyurtmalar yo'q")
            }
        } else {
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(orders) { order ->
                    OrderItem(
                        order = order,
                        onClick = { onOrderClick(order) }
                    )
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OrderItem(
    order: Order,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        onClick = onClick
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = order.orderCode,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                StatusBadge(status = order.status)
            }

            Spacer(modifier = Modifier.height(8.dp))

            order.pickupAddress?.let {
                Text(text = "Olib ketish: $it", style = MaterialTheme.typography.bodySmall)
            }

            order.dropoffAddress?.let {
                Text(text = "Tashrif: $it", style = MaterialTheme.typography.bodySmall)
            }

            Spacer(modifier = Modifier.height(8.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(text = "To'lov: ${order.paymentMethod.name}")
                order.totalAmount?.let {
                    Text(text = "${it} so'm", fontWeight = FontWeight.Bold)
                }
            }

            if (order.status == OrderStatus.UNASSIGNABLE) {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Kuryerlar tugadi!",
                    color = MaterialTheme.colorScheme.error,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

@Composable
fun StatusBadge(status: OrderStatus) {
    val (color, text) = when (status) {
        OrderStatus.PENDING -> MaterialTheme.colorScheme.secondary to "Kutilmoqda"
        OrderStatus.ACCEPTED -> MaterialTheme.colorScheme.primary to "Qabul qilindi"
        OrderStatus.READY_FOR_PICKUP -> MaterialTheme.colorScheme.primary to "Olib ketishga tayyor"
        OrderStatus.PICKED_UP -> MaterialTheme.colorScheme.tertiary to "Olib ketildi"
        OrderStatus.DELIVERED -> MaterialTheme.colorScheme.primaryContainer to "Yetkazib berildi"
        OrderStatus.CANCELED -> MaterialTheme.colorScheme.error to "Bekor qilindi"
        OrderStatus.DELIVERY_FAILED -> MaterialTheme.colorScheme.error to "Yetkazib berilmadi"
        OrderStatus.UNASSIGNABLE -> MaterialTheme.colorScheme.error to "Biriktirilmadi"
        OrderStatus.RETURNED_TO_RESTAURANT -> MaterialTheme.colorScheme.secondary to "Restoranga qaytarildi"
    }

    Surface(
        color = color.copy(alpha = 0.2f),
        shape = MaterialTheme.shapes.small
    ) {
        Text(
            text = text,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            style = MaterialTheme.typography.labelSmall,
            color = color
        )
    }
}
