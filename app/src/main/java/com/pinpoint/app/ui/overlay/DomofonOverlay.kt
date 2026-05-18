package com.pinpoint.app.ui.overlay

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import com.pinpoint.app.R

@Composable
fun DomofonOverlay(
    code: String,
    onCopy: () -> Unit,
    onSpeak: () -> Unit
) {
    Surface(
        modifier = Modifier.fillMaxWidth(),
        tonalElevation = 4.dp,
        shadowElevation = 12.dp,
        shape = MaterialTheme.shapes.large
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(text = "Domofon kodi", style = MaterialTheme.typography.titleLarge)
            Text(text = code, style = MaterialTheme.typography.displaySmall)
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Button(onClick = onCopy, modifier = Modifier.weight(1f)) {
                    Icon(painter = painterResource(id = R.drawable.ic_copy), contentDescription = null)
                    Text(text = "Nusxa olish")
                }
                Button(onClick = onSpeak, modifier = Modifier.weight(1f)) {
                    Icon(painter = painterResource(id = R.drawable.ic_voice), contentDescription = null)
                    Text(text = "Ovoz bilan aytish")
                }
            }
        }
    }
}
