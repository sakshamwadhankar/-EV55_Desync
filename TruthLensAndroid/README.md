# TruthLens Android Client

This is the Android frontend for the TruthLens project.

## Prerequisites
- Android Studio Iguana or newer
- JDK 17
- Android SDK 34

## Setup
1. Open this folder `TruthLensAndroid` in Android Studio.
2. Allow Gradle sync to complete.

## Configuration
⚠️ **CRITICAL: You must set your backend URL before building.**

1. Open `app/src/main/java/com/truthlens/app/MainActivity.java`
2. Locate the line:
   ```java
   private static final String BASE_URL = "https://YOUR-BACKEND-API/";
   ```
3. Replace `"https://YOUR-BACKEND-API/"` with the actual URL of your deployed Django backend (e.g., from Hugging Face Spaces or Render). 
   - **Note**: Ensure the URL ends with a slash `/`.

## Building the APK
1. In Android Studio, go to `Build > Build Bundle(s) / APK(s) > Build APK(s)`.
2. Once complete, the APK will be located in `app/build/outputs/apk/debug/app-debug.apk`.

## Features
- Verifies news claims against the backend ML model.
- Displays Verdict, Confidence, and Source count.
- Dark theme (Charcoal & Emerald).
