package com.pinpoint.app.ui.payment

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.CreditCard
import androidx.compose.material.icons.filled.Money
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableDoubleStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

enum class PaymentTab { CASH, DIGITAL }

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PaymentScreen(
    orderCode: String,
    totalAmount: Double,
    paymentMethod: String,
    onConfirmCash: (Double) -> Unit,
    onConfirmDigital: () -> Unit,
    onBack: () -> Unit
) {
    var selectedTab by remember {
        mutableStateOf(if (paymentMethod == "CASH") PaymentTab.CASH else PaymentTab.DIGITAL)
    }
    var receivedAmount by remember { mutableStateOf("") }
    var changeAmount by remember { mutableDoubleStateOf(0.0) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("To'lov — $orderCode") },
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
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer
                )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(20.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Jami summa",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Text(
                        text = "${String.format("%,.0f", totalAmount)} so'm",
                        style = MaterialTheme.typography.headlineLarge,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                OutlinedButton(
                    onClick = { selectedTab = PaymentTab.CASH },
                    modifier = Modifier.weight(1f),
                    colors = if (selectedTab == PaymentTab.CASH) {
                        ButtonDefaults.outlinedButtonColors(
                            containerColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.12f)
                        )
                    } else {
                        ButtonDefaults.outlinedButtonColors()
                    }
                ) {
                    Icon(Icons.Default.Money, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Naqd")
                }
                OutlinedButton(
                    onClick = { selectedTab = PaymentTab.DIGITAL },
                    modifier = Modifier.weight(1f),
                    colors = if (selectedTab == PaymentTab.DIGITAL) {
                        ButtonDefaults.outlinedButtonColors(
                            containerColor = MaterialTheme.colorScheme.primary.copy(alpha = 0.12f)
                        )
                    } else {
                        ButtonDefaults.outlinedButtonColors()
                    }
                ) {
                    Icon(Icons.Default.CreditCard, contentDescription = null)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Karta / QR")
                }
            }

            when (selectedTab) {
                PaymentTab.CASH -> CashPaymentSection(
                    totalAmount = totalAmount,
                    receivedAmount = receivedAmount,
                    changeAmount = changeAmount,
                    onReceivedAmountChange = { value ->
                        receivedAmount = value
                        val received = value.toDoubleOrNull() ?: 0.0
                        changeAmount = if (received >= totalAmount) received - totalAmount else 0.0
                    },
                    onQuickAmount = { amount ->
                        receivedAmount = amount.toInt().toString()
                        changeAmount = if (amount >= totalAmount) amount - totalAmount else 0.0
                    },
                    onConfirm = {
                        val received = receivedAmount.toDoubleOrNull() ?: 0.0
                        onConfirmCash(received)
                    }
                )

                PaymentTab.DIGITAL -> DigitalPaymentSection(
                    totalAmount = totalAmount,
                    orderCode = orderCode,
                    onConfirm = onConfirmDigital
                )
            }
        }
    }
}

@Composable
private fun CashPaymentSection(
    totalAmount: Double,
    receivedAmount: String,
    changeAmount: Double,
    onReceivedAmountChange: (String) -> Unit,
    onQuickAmount: (Double) -> Unit,
    onConfirm: () -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        OutlinedTextField(
            value = receivedAmount,
            onValueChange = onReceivedAmountChange,
            label = { Text("Qabul qilingan summa") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            suffix = { Text("so'm") }
        )

        Text(
            text = "Tez tanlash:",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            val quickAmounts = listOf(
                totalAmount,
                Math.ceil(totalAmount / 1000) * 1000,
                Math.ceil(totalAmount / 5000) * 5000,
                Math.ceil(totalAmount / 10000) * 10000
            ).distinct().take(4)

            quickAmounts.forEach { amount ->
                OutlinedButton(
                    onClick = { onQuickAmount(amount) },
                    modifier = Modifier.weight(1f)
                ) {
                    Text(
                        text = "${(amount / 1000).toInt()}K",
                        fontSize = 12.sp
                    )
                }
            }
        }

        if (changeAmount > 0) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = Color(0xFFE8F5E9)
                )
            ) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "Qaytim",
                        style = MaterialTheme.typography.bodyMedium
                    )
                    Text(
                        text = "${String.format("%,.0f", changeAmount)} so'm",
                        style = MaterialTheme.typography.headlineSmall,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF2E7D32)
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        val received = receivedAmount.toDoubleOrNull() ?: 0.0
        Button(
            onClick = onConfirm,
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp),
            enabled = received >= totalAmount
        ) {
            Icon(Icons.Default.Check, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("Naqd to'lovni tasdiqlash", fontSize = 16.sp)
        }
    }
}

@Composable
private fun DigitalPaymentSection(
    totalAmount: Double,
    orderCode: String,
    onConfirm: () -> Unit
) {
    Column(
        verticalArrangement = Arrangement.spacedBy(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "QR kodni skanerlang",
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center,
            modifier = Modifier.fillMaxWidth()
        )

        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = Color.White
            )
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Box(
                    modifier = Modifier
                        .size(200.dp)
                        .border(2.dp, Color.Black, RoundedCornerShape(8.dp))
                        .padding(8.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        Text(
                            text = "QR CODE",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = orderCode,
                            style = MaterialTheme.typography.bodySmall,
                            color = Color.Gray
                        )
                        Text(
                            text = "${String.format("%,.0f", totalAmount)} so'm",
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    PaymentProviderChip(name = "Payme", color = Color(0xFF00BCD4))
                    PaymentProviderChip(name = "Click", color = Color(0xFF2196F3))
                    PaymentProviderChip(name = "Uzum", color = Color(0xFF7B1FA2))
                }
            }
        }

        Spacer(modifier = Modifier.height(8.dp))

        Button(
            onClick = onConfirm,
            modifier = Modifier
                .fillMaxWidth()
                .height(56.dp)
        ) {
            Icon(Icons.Default.Check, contentDescription = null)
            Spacer(modifier = Modifier.width(8.dp))
            Text("To'lov tasdiqlandi", fontSize = 16.sp)
        }
    }
}

@Composable
private fun PaymentProviderChip(name: String, color: Color) {
    Box(
        modifier = Modifier
            .clip(RoundedCornerShape(20.dp))
            .background(color.copy(alpha = 0.15f))
            .padding(horizontal = 16.dp, vertical = 8.dp)
    ) {
        Text(
            text = name,
            color = color,
            fontWeight = FontWeight.Bold,
            fontSize = 14.sp
        )
    }
}
