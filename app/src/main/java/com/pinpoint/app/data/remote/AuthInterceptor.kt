package com.pinpoint.app.data.remote

import com.pinpoint.app.data.TokenManager
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.Response

class AuthInterceptor(
    private val tokenManager: TokenManager
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        
        // Skip token for auth endpoints
        val isAuthEndpoint = originalRequest.url.encodedPath.contains("/auth/")
        
        if (!isAuthEndpoint) {
            val accessToken = runBlocking {
                tokenManager.accessToken.first()
            }
            
            if (accessToken != null) {
                val authenticatedRequest = originalRequest.newBuilder()
                    .header("Authorization", "Bearer $accessToken")
                    .build()
                return chain.proceed(authenticatedRequest)
            }
        }
        
        return chain.proceed(originalRequest)
    }
}
