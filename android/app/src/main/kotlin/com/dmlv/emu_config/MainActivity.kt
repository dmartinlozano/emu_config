package com.dmlv.emu_config

import android.hardware.input.InputManager
import android.os.Handler
import android.view.InputDevice
import android.view.KeyEvent
import android.view.MotionEvent
import androidx.annotation.NonNull
import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine
import io.flutter.plugin.common.MethodChannel
import org.flame_engine.gamepads_android.GamepadsCompatibleActivity
import android.os.Build

class MainActivity: FlutterActivity(), GamepadsCompatibleActivity {
    private val CHANNEL = "com.dmlv.emu_config/gamepad"

    var keyListener: ((KeyEvent) -> Boolean)? = null
    var motionListener: ((MotionEvent) -> Boolean)? = null

    data class CustomGamepad(val descriptor: String?, val vendorId: Int, val productId: Int, val sources: Int)

    override fun configureFlutterEngine(@NonNull flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, CHANNEL).setMethodCallHandler { call, result ->
            when (call.method) {
                "getCustomGamepadController" -> {
                    val gamepadId = call.argument<Int>("gamepadId")!!
                    val gamepadData = getCustomGamepadController(gamepadId)
                    result.success(gamepadData)
                }
                else -> {
                    result.notImplemented()
                }
            }
        }
    }

    override fun dispatchGenericMotionEvent(motionEvent: MotionEvent): Boolean {
        return motionListener?.invoke(motionEvent) ?: false
    }

    override fun dispatchKeyEvent(keyEvent: KeyEvent): Boolean {
        return keyListener?.invoke(keyEvent) ?: false
    }

    override fun registerInputDeviceListener(
      listener: InputManager.InputDeviceListener, handler: Handler?) {
        val inputManager = getSystemService(INPUT_SERVICE) as InputManager
        inputManager.registerInputDeviceListener(listener, null)
    }

    override fun registerKeyEventHandler(handler: (KeyEvent) -> Boolean) {
        keyListener = handler
    }

    override fun registerMotionEventHandler(handler: (MotionEvent) -> Boolean) {
        motionListener = handler
    }

    private fun getCustomGamepadController(gamepadId: Int): Map<String, Any?> {
        val inputDevice = InputDevice.getDevice(gamepadId)
        val descriptor = inputDevice?.descriptor
        val vendorId = inputDevice?.vendorId ?: 0
        val productId = inputDevice?.productId ?: 0
        val sources = inputDevice?.sources ?: 0

        return mapOf(
                "descriptor" to descriptor,
                "vendorId" to vendorId as Int,
                "productId" to productId as Int,
                "sources" to sources as Int
        )
    }
}
