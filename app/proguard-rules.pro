# PinPoInt ProGuard Rules
-keep class com.pinpoint.app.data.** { *; }
-keep class com.pinpoint.app.domain.model.** { *; }
-keepclassmembers class * implements android.os.Parcelable { *; }
-keep class org.osmdroid.** { *; }
