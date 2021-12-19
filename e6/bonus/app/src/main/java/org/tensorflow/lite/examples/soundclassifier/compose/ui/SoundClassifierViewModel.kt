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
import android.os.HandlerThread
import android.widget.Toast
import androidx.lifecycle.AndroidViewModel
import be.tarsos.dsp.AudioDispatcher
import be.tarsos.dsp.io.android.AndroidAudioInputStream
import be.tarsos.dsp.mfcc.MFCC
import org.tensorflow.lite.examples.soundclassifier.compose.ml.WakeWordStopLite
import org.tensorflow.lite.examples.soundclassifier.compose.audio.AudioRecordResult
import org.tensorflow.lite.examples.soundclassifier.compose.audio.initAudioRecord
import be.tarsos.dsp.AudioEvent

import be.tarsos.dsp.AudioProcessor
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow

import org.tensorflow.lite.DataType
import org.tensorflow.lite.support.tensorbuffer.TensorBuffer


@SuppressLint("StaticFieldLeak")
class SoundClassifierViewModel(application: Application) : AndroidViewModel(application) {
  // Changing this value triggers turning classification on/off
  private val _classifierEnabled = MutableStateFlow(true)
  val classifierEnabled = _classifierEnabled.asStateFlow()

  // How often should classification run in milliseconds

  private var dispatcher: AudioDispatcher? = null
  private var tfModel: WakeWordStopLite? = null
  private var audioRecord: AudioRecordResult? = null

  init {
    // Create a handler to run classification in a background thread
    val handlerThread = HandlerThread("backgroundThread")
    handlerThread.start()
  }

  fun setClassifierEnabled(value: Boolean) {
    _classifierEnabled.value = value
  }

  fun startAudioClassification() {
    // If the audio classifier is initialized and running, do nothing.
    if (tfModel != null) {
      setClassifierEnabled(true)
      return
    }

    //model
    val model = WakeWordStopLite.newInstance(getApplication())

    // Initialize the audio recorder
    val record: AudioRecordResult? = initAudioRecord()
    if(record==null){
      throw ExceptionInInitializerError("Dude!")
    }
    val mInputStream = AndroidAudioInputStream(record.audioRecord, record.format)
    val mDispatcher = AudioDispatcher(mInputStream, record.bufferSize, record.bufferSize / 2)

    val mfcc = MFCC(record.bufferSize,record.audioRecord.sampleRate )

    mDispatcher.addAudioProcessor(mfcc)
    mDispatcher.addAudioProcessor(object : AudioProcessor {
      override fun processingFinished() {}
      override fun process(audioEvent: AudioEvent): Boolean {
        // Creates inputs for reference.
        val inputFeature = TensorBuffer.createFixedSize(intArrayOf(1, 16, 16, 1), DataType.FLOAT32)
        inputFeature.loadArray(mfcc.mfcc)

        // Runs model inference and gets result.
        val outputs = model.process(inputFeature)
        val outputFeature0 = outputs.outputFeature0AsTensorBuffer
        val data=outputFeature0.floatArray

        if(data[0] > 0.5) {
          Toast.makeText(getApplication(),"STOP",Toast.LENGTH_LONG)
        }

        return true
      }
    })
    Thread(mDispatcher, "Audio dispatching").start()
    record.audioRecord.startRecording()


    // Save the instances we just created for use later
    tfModel = model
    audioRecord = record
    dispatcher = mDispatcher
  }

  fun stopAudioClassification() {
    audioRecord?.audioRecord?.stop()
    audioRecord = null
    tfModel?.close()
    tfModel = null
    dispatcher?.stop()
    dispatcher = null

  }

  companion object {
    private const val LOG_TAG = "AudioDemo"
    private const val MINIMUM_DISPLAY_THRESHOLD: Float = 0.3f
  }
}
