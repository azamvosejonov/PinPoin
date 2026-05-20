package com.pinpoint.app.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Map
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.NavController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.hilt.navigation.compose.hiltViewModel
import com.pinpoint.app.ui.courier.CourierStatusScreen
import com.pinpoint.app.ui.location.CourierLocationScreen
import com.pinpoint.app.ui.location.CourierLocationViewModel
import com.pinpoint.app.ui.indoor.IndoorMapScreen
import com.pinpoint.app.ui.indoor.IndoorMapViewModel
import com.pinpoint.app.ui.tracking.PublicTrackingScreen
import com.pinpoint.app.ui.tracking.PublicTrackingViewModel
import com.pinpoint.app.ui.order.OrderDetailScreen
import com.pinpoint.app.ui.order.OrderListScreen
import com.pinpoint.app.ui.order.OrderViewModel
import com.pinpoint.app.ui.auth.LoginScreen
import com.pinpoint.app.ui.auth.AuthViewModel
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel.initialize()
        setContent {
            MaterialTheme {
                Surface(modifier = Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                    val navController = rememberNavController()
                    val uiState by viewModel.uiState.collectAsState()
                    val authViewModel: AuthViewModel = hiltViewModel()
                    val isLoggedIn by authViewModel.isLoggedIn.collectAsState()

                    if (!isLoggedIn) {
                        LoginScreen(
                            onLogin = { email, password -> authViewModel.login(email, password) },
                            onRegister = { /* Navigate to register */ },
                            isLoading = authViewModel.isLoading.collectAsState().value,
                            error = authViewModel.error.collectAsState().value
                        )
                    } else {
                        Scaffold(
                            bottomBar = {
                                NavigationBar {
                                    NavigationBarItem(
                                        selected = navController.currentDestination?.route == "map",
                                        onClick = { navController.navigate("map") },
                                        icon = { Icon(Icons.Default.Map, contentDescription = "Xarita") },
                                        label = { Text("Xarita") }
                                    )
                                    NavigationBarItem(
                                        selected = navController.currentDestination?.route == "orders",
                                        onClick = { navController.navigate("orders") },
                                        icon = { Icon(Icons.Default.List, contentDescription = "Buyurtmalar") },
                                        label = { Text("Buyurtmalar") }
                                    )
                                    NavigationBarItem(
                                        selected = navController.currentDestination?.route == "status",
                                        onClick = { navController.navigate("status") },
                                        icon = { Icon(Icons.Default.Person, contentDescription = "Status") },
                                        label = { Text("Status") }
                                    )
                                }
                            }
                        ) { padding ->
                            NavHost(
                                navController = navController,
                                startDestination = "map",
                                modifier = Modifier.padding(padding)
                            ) {
                                composable("map") {
                                    PinPoIntScreen(
                                        state = uiState,
                                        onDelivered = { viewModel.onDelivered() },
                                        onRequestDomofonCode = { viewModel.onDomofonInfoRequested() },
                                        onCopyCode = { viewModel.onCopyDomofonCode() },
                                        onCallClient = { viewModel.onCallClient() }
                                    )
                                }
                                composable("orders") {
                                    OrderNavigation()
                                }
                                composable("status") {
                                    CourierStatusNavigation()
                                }
                                // Contextual screens accessible from order detail
                                composable("location") {
                                    CourierLocationNavigation()
                                }
                                composable("indoor") {
                                    IndoorMapNavigation()
                                }
                                // Public tracking accessible via deep link
                                composable("tracking/{trackingHash}") { backStackEntry ->
                                    val trackingHash = backStackEntry.arguments?.getString("trackingHash") ?: ""
                                    PublicTrackingNavigation(trackingHash)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun OrderNavigation() {
    val navController = rememberNavController()
    val orderViewModel: OrderViewModel = hiltViewModel()
    
    LaunchedEffect(Unit) {
        orderViewModel.loadOrders()
    }
    
    NavHost(
        navController = navController,
        startDestination = "order_list"
    ) {
        composable("order_list") {
            val orders by orderViewModel.orders.collectAsState()
            val isLoading by orderViewModel.isLoading.collectAsState()
            
            OrderListScreen(
                orders = orders,
                onOrderClick = { order ->
                    orderViewModel.selectOrder(order)
                    navController.navigate("order_detail")
                },
                onRefresh = { orderViewModel.loadOrders() },
                isLoading = isLoading
            )
        }
        composable("order_detail") {
            val selectedOrder by orderViewModel.selectedOrder.collectAsState()
            
            selectedOrder?.let { order ->
                OrderDetailScreen(
                    order = order,
                    onBack = { navController.popBackStack() },
                    onUpdateStatus = { status ->
                        orderViewModel.updateOrderStatus(order.id, status)
                    },
                    onDecline = { reason ->
                        orderViewModel.declineOrder(order.id, reason)
                        navController.popBackStack()
                    },
                    onCallClient = { /* TODO: Implement call client */ }
                )
            }
        }
    }
}

@Composable
fun CourierStatusNavigation() {
    val orderViewModel: OrderViewModel = hiltViewModel()
    val courierStatus by orderViewModel.courierStatus.collectAsState()
    
    LaunchedEffect(Unit) {
        orderViewModel.loadCourierStatus()
    }
    
    CourierStatusScreen(
        courierStatus = courierStatus,
        onBack = { /* No back button needed */ },
        onUpdateStatus = { status ->
            orderViewModel.updateCourierStatus(status)
        },
        onCollectCash = { amount ->
            courierStatus?.let { orderViewModel.collectCash(it.courierId, amount) }
        }
    )
}

@Composable
fun CourierLocationNavigation() {
    val courierLocationViewModel: CourierLocationViewModel = hiltViewModel()
    val courierLocation by courierLocationViewModel.courierLocation.collectAsState()
    val currentLocation by courierLocationViewModel.currentLocation.collectAsState()
    val isLoading by courierLocationViewModel.isLoading.collectAsState()
    val isTracking by courierLocationViewModel.isTracking.collectAsState()
    val error by courierLocationViewModel.error.collectAsState()
    
    LaunchedEffect(Unit) {
        courierLocationViewModel.loadCourierLocation()
    }
    
    CourierLocationScreen(
        courierLocation = courierLocation,
        currentLocation = currentLocation,
        isLoading = isLoading,
        isTracking = isTracking,
        error = error,
        onUpdateLocation = { lat, lon ->
            courierLocationViewModel.updateLocation(lat, lon)
        },
        onRefresh = {
            courierLocationViewModel.loadCourierLocation()
        },
        onStartTracking = {
            courierLocationViewModel.startRealtimeTracking()
        },
        onStopTracking = {
            courierLocationViewModel.stopRealtimeTracking()
        }
    )
}

@Composable
fun IndoorMapNavigation() {
    val indoorMapViewModel: IndoorMapViewModel = hiltViewModel()
    val indoorMap by indoorMapViewModel.indoorMap.collectAsState()
    val indoorPaths by indoorMapViewModel.indoorPaths.collectAsState()
    val floorTiles by indoorMapViewModel.floorTiles.collectAsState()
    val courierPosition by indoorMapViewModel.courierTilePosition.collectAsState()
    val isLoading by indoorMapViewModel.isLoading.collectAsState()
    val error by indoorMapViewModel.error.collectAsState()
    
    IndoorMapScreen(
        indoorMap = indoorMap,
        indoorPaths = indoorPaths,
        floorTiles = floorTiles,
        courierPosition = courierPosition,
        isLoading = isLoading,
        error = error,
        onLoadMap = { externalId ->
            indoorMapViewModel.loadIndoorMap(externalId)
        },
        onCreatePath = { externalId ->
            val path = com.pinpoint.app.domain.model.IndoorPathCreate(
                floorNumber = 1,
                startX = 0.0,
                startY = 0.0,
                endX = 10.0,
                endY = 10.0,
                pathData = ""
            )
            indoorMapViewModel.createIndoorPath(externalId, path)
        }
    )
}

@Composable
fun PublicTrackingNavigation(trackingHash: String = "") {
    val publicTrackingViewModel: PublicTrackingViewModel = hiltViewModel()
    val orderTracking by publicTrackingViewModel.orderTracking.collectAsState()
    val isLoading by publicTrackingViewModel.isLoading.collectAsState()
    val error by publicTrackingViewModel.error.collectAsState()
    
    LaunchedEffect(trackingHash) {
        if (trackingHash.isNotEmpty()) {
            publicTrackingViewModel.trackOrder(trackingHash)
        }
    }
    
    PublicTrackingScreen(
        orderTracking = orderTracking,
        isLoading = isLoading,
        error = error,
        onTrack = { hash ->
            publicTrackingViewModel.trackOrder(hash)
        }
    )
}
