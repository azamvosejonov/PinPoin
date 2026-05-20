package com.pinpoint.app.ui.indoor

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectTransformGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Fill
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.translate
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.input.pointer.pointerInput
import com.pinpoint.app.domain.model.IsometricTile
import com.pinpoint.app.domain.model.TileType

private const val TILE_WIDTH = 48f
private const val TILE_HEIGHT = 24f
private const val TILE_DEPTH = 12f

@Composable
fun IsometricMapRenderer(
    tiles: List<IsometricTile>,
    courierPosition: Pair<Int, Int>?,
    modifier: Modifier = Modifier
) {
    var scale by remember { mutableFloatStateOf(1.5f) }
    var offsetX by remember { mutableFloatStateOf(0f) }
    var offsetY by remember { mutableFloatStateOf(0f) }

    Box(
        modifier = modifier
            .fillMaxSize()
            .pointerInput(Unit) {
                detectTransformGestures { _, pan, zoom, _ ->
                    scale = (scale * zoom).coerceIn(0.5f, 4f)
                    offsetX += pan.x
                    offsetY += pan.y
                }
            }
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val centerX = size.width / 2 + offsetX
            val centerY = size.height / 3 + offsetY

            translate(left = centerX, top = centerY) {
                val sortedTiles = tiles.sortedWith(compareBy({ it.y }, { it.x }))

                for (tile in sortedTiles) {
                    val screenX = (tile.x - tile.y) * TILE_WIDTH * scale / 2
                    val screenY = (tile.x + tile.y) * TILE_HEIGHT * scale / 2
                    drawIsometricTile(
                        screenX = screenX,
                        screenY = screenY,
                        tileType = tile.type,
                        label = tile.label,
                        scale = scale
                    )
                }

                courierPosition?.let { (cx, cy) ->
                    val courierScreenX = (cx - cy) * TILE_WIDTH * scale / 2
                    val courierScreenY = (cx + cy) * TILE_HEIGHT * scale / 2
                    drawCourierMarker(courierScreenX, courierScreenY, scale)
                }
            }
        }
    }
}

private fun DrawScope.drawIsometricTile(
    screenX: Float,
    screenY: Float,
    tileType: TileType,
    label: String?,
    scale: Float
) {
    val tw = TILE_WIDTH * scale / 2
    val th = TILE_HEIGHT * scale / 2
    val td = TILE_DEPTH * scale

    val topColor = getTileTopColor(tileType)
    val leftColor = getTileLeftColor(tileType)
    val rightColor = getTileRightColor(tileType)

    val topFace = Path().apply {
        moveTo(screenX, screenY - th)
        lineTo(screenX + tw, screenY)
        lineTo(screenX, screenY + th)
        lineTo(screenX - tw, screenY)
        close()
    }
    drawPath(topFace, topColor, style = Fill)
    drawPath(topFace, Color(0x33000000), style = Stroke(width = 0.5f))

    if (tileType == TileType.WALL || tileType == TileType.DOOR) {
        val wallHeight = td * 2

        val leftFace = Path().apply {
            moveTo(screenX - tw, screenY)
            lineTo(screenX, screenY + th)
            lineTo(screenX, screenY + th + wallHeight)
            lineTo(screenX - tw, screenY + wallHeight)
            close()
        }
        drawPath(leftFace, leftColor, style = Fill)
        drawPath(leftFace, Color(0x22000000), style = Stroke(width = 0.5f))

        val rightFace = Path().apply {
            moveTo(screenX + tw, screenY)
            lineTo(screenX, screenY + th)
            lineTo(screenX, screenY + th + wallHeight)
            lineTo(screenX + tw, screenY + wallHeight)
            close()
        }
        drawPath(rightFace, rightColor, style = Fill)
        drawPath(rightFace, Color(0x22000000), style = Stroke(width = 0.5f))

        val topFaceRaised = Path().apply {
            moveTo(screenX, screenY - th - wallHeight)
            lineTo(screenX + tw, screenY - wallHeight)
            lineTo(screenX, screenY + th - wallHeight)
            lineTo(screenX - tw, screenY - wallHeight)
            close()
        }
        drawPath(topFaceRaised, topColor.copy(alpha = 0.9f), style = Fill)
    }

    label?.let {
        drawContext.canvas.nativeCanvas.apply {
            val paint = android.graphics.Paint().apply {
                color = android.graphics.Color.BLACK
                textSize = 9f * scale
                textAlign = android.graphics.Paint.Align.CENTER
                isAntiAlias = true
            }
            drawText(it, screenX, screenY + 4f * scale, paint)
        }
    }
}

private fun DrawScope.drawCourierMarker(screenX: Float, screenY: Float, scale: Float) {
    val radius = 8f * scale
    drawCircle(
        color = Color(0xFF1565C0),
        radius = radius + 3f,
        center = Offset(screenX, screenY - 6f * scale)
    )
    drawCircle(
        color = Color(0xFF42A5F5),
        radius = radius,
        center = Offset(screenX, screenY - 6f * scale)
    )
    drawCircle(
        color = Color.White,
        radius = radius * 0.4f,
        center = Offset(screenX, screenY - 6f * scale)
    )

    val pulseRadius = radius * 2f
    drawCircle(
        color = Color(0x3342A5F5),
        radius = pulseRadius,
        center = Offset(screenX, screenY - 6f * scale)
    )
}

private fun getTileTopColor(type: TileType): Color = when (type) {
    TileType.FLOOR -> Color(0xFFE8E0D4)
    TileType.WALL -> Color(0xFF8D8D8D)
    TileType.DOOR -> Color(0xFF6D4C41)
    TileType.ELEVATOR -> Color(0xFF90CAF9)
    TileType.STAIRS -> Color(0xFFFFCC80)
    TileType.APARTMENT -> Color(0xFFA5D6A7)
    TileType.HIGHLIGHT_PATH -> Color(0xFFFFF176)
    TileType.COURIER_POSITION -> Color(0xFF42A5F5)
}

private fun getTileLeftColor(type: TileType): Color = when (type) {
    TileType.WALL -> Color(0xFF6D6D6D)
    TileType.DOOR -> Color(0xFF4E342E)
    else -> Color(0xFFD5CFC6)
}

private fun getTileRightColor(type: TileType): Color = when (type) {
    TileType.WALL -> Color(0xFF7A7A7A)
    TileType.DOOR -> Color(0xFF5D4037)
    else -> Color(0xFFCBC5B9)
}
