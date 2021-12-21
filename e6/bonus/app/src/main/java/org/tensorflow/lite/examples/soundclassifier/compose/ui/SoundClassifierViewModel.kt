/*
 * Copyright 2021 The TensorFlow Authors. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package org.tensorflow.lite.examples.soundclassifier.compose.ui

import android.annotation.SuppressLint
import android.app.Application
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.Handler
import android.os.HandlerThread
import android.util.Log
import android.widget.Toast
import androidx.core.os.HandlerCompat
import androidx.lifecycle.AndroidViewModel
import org.tensorflow.lite.examples.soundclassifier.compose.ml.WakeWordStopLite
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

import org.tensorflow.lite.DataType
import org.tensorflow.lite.Interpreter
import org.tensorflow.lite.examples.soundclassifier.compose.audio.Decimate
import org.tensorflow.lite.examples.soundclassifier.compose.audio.MFCC

import org.tensorflow.lite.support.audio.TensorAudio
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer


@SuppressLint("StaticFieldLeak")
class SoundClassifierViewModel(application: Application) : AndroidViewModel(application) {
  private val classificationInterval: Long=500L

  // Changing this value triggers turning classification on/off
  private val _classifierEnabled = MutableStateFlow(true)
  val classifierEnabled = _classifierEnabled.asStateFlow()

  // How often should classification run in milliseconds
  private var tfModel: WakeWordStopLite? = null
  private var record: AudioRecord? = null
  private var handler: Handler

  init {
    // Create a handler to run classification in a background thread
    val handlerThread = HandlerThread("backgroundThread")
    handlerThread.start()
    handler = HandlerCompat.createAsync(handlerThread.looper)
  }

  fun setClassifierEnabled(value: Boolean) {
    _classifierEnabled.value = value
  }

  @SuppressLint("MissingPermission")
  fun startAudioClassification() {
    // If the audio classifier is initialized and running, do nothing.
    if (tfModel != null) {
      setClassifierEnabled(true)
      return
    }

    //model
    val model = WakeWordStopLite.newInstance(getApplication())

    val bufferSize = AudioRecord.getMinBufferSize(44100, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_FLOAT)
    val recorder = AudioRecord(
      MediaRecorder.AudioSource.MIC, 44100, AudioFormat.CHANNEL_IN_MONO, AudioFormat.ENCODING_PCM_FLOAT, bufferSize
    )

    recorder.startRecording()
    val blocksize = (44100 * 0.5).toInt()
    var buffer = FloatArray(blocksize)
    val decimate = Decimate(44100,8000)
    val mfcc = MFCC()
    mfcc.setSampleRate(8000)
    mfcc.setN_mfcc(16)

    // Define the classification runnable
    val run = object : Runnable {
      override fun run() {
        val startTime = System.currentTimeMillis()

        recorder.read(buffer, 0, blocksize, AudioRecord.READ_NON_BLOCKING )

        // Load the latest audio sample
        val signal = decimate.process(buffer)
        val mfccs = mfcc.process(signal)

        val tensor = TensorAudio.create(
          TensorAudio.TensorAudioFormat.create(
            AudioFormat.Builder().setSampleRate(8000)
              .setChannelMask(1)
              .setChannelMask(1)
              .setEncoding(AudioFormat.ENCODING_PCM_FLOAT)
              .build()
          ),
          256
        )
        tensor.load(mfccs)

        // Creates inputs for reference.
        val inputFeature0 = TensorBuffer.createFixedSize(intArrayOf(1, 16, 16, 1), DataType.FLOAT32)
        inputFeature0.loadBuffer(tensor.tensorBuffer.buffer)


        // Runs model inference and gets result.
        val outputs = model.process(inputFeature0)
        val outputFeature0 = outputs.outputFeature0AsTensorBuffer
        Log.d(LOG_TAG, "stop confidence: ${outputFeature0.floatArray[0]}")

        if (outputFeature0.floatArray[0]> 0.5){
          Toast.makeText(getApplication(),"STOP",Toast.LENGTH_LONG)
        }

        val finishTime = System.currentTimeMillis()
        Log.d(LOG_TAG, "Latency = ${finishTime - startTime} ms")

        // Rerun the classification after a certain interval
        handler.postDelayed(this, classificationInterval)
      }
    }

    // Start the classification process
    handler.post(run)

    // Save the instances we just created for use later
    record= recorder
    tfModel = model
  }

  private fun transposeArray(array: FloatArray): FloatArray {
    val m: Int = array.size
    val transposedMatrix = FloatArray(m)

    for (y in 0 until m) {
      transposedMatrix[y] = array.get(y)
    }
    return transposedMatrix
  }

  fun stopAudioClassification() {
    handler.removeCallbacksAndMessages(null)
    record?.stop()
    record = null
    tfModel?.close()
    tfModel = null

  }

  companion object {
    private const val LOG_TAG = "AudioDemo"
    private const val MINIMUM_DISPLAY_THRESHOLD: Float = 0.3f
  }
}

