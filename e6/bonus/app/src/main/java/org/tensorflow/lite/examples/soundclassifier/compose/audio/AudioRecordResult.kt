package org.tensorflow.lite.examples.soundclassifier.compose.audio

import android.annotation.SuppressLint
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import be.tarsos.dsp.io.TarsosDSPAudioFormat

data class AudioRecordResult(val audioRecord: AudioRecord, val format: TarsosDSPAudioFormat, val bufferSize: Int)

private val RECORDER_CHANNELS = shortArrayOf(AudioFormat.CHANNEL_IN_MONO.toShort(), AudioFormat.CHANNEL_IN_STEREO.toShort())
private val RECORDER_AUDIO_FORMATS = shortArrayOf(AudioFormat.ENCODING_PCM_16BIT.toShort(), AudioFormat.ENCODING_PCM_8BIT.toShort())
private val RECORDER_SAMPLE_RATES = intArrayOf(8000) //, 11025, 22050, 44100

private const val LOG_TAG = "AudioDemo"

@SuppressLint("MissingPermission")
fun initAudioRecord(): AudioRecordResult? {
    for (rate in RECORDER_SAMPLE_RATES.reversed()) {
        for (audioFormat in RECORDER_AUDIO_FORMATS) {
            for (channelConfig in RECORDER_CHANNELS) {
                try {
                    val bufferSize = AudioRecord.getMinBufferSize(rate, channelConfig.toInt(), audioFormat.toInt())
                    val bytesPerElement = if (audioFormat == AudioFormat.ENCODING_PCM_8BIT.toShort()) 8 else 16
                    val channels = if (channelConfig == AudioFormat.CHANNEL_IN_MONO.toShort()) 1 else 2
                    val signed = true
                    val bigEndian = false
                    if (bufferSize != AudioRecord.ERROR_BAD_VALUE) {
                        val recorder = AudioRecord(MediaRecorder.AudioSource.DEFAULT, rate, channelConfig.toInt(), audioFormat.toInt(), bufferSize)
                        if (recorder.state == AudioRecord.STATE_INITIALIZED) {
                            Log.d(LOG_TAG,"Initialized recorder. Sample rate: %d, format: %d, channel: %d".format( rate, audioFormat, channelConfig))
                            return AudioRecordResult(recorder, TarsosDSPAudioFormat(rate.toFloat(), bytesPerElement, channels, signed, bigEndian), bufferSize)
                        }
                    }
                } catch (e: Exception) {
                    Log.e(LOG_TAG, rate.toString() + "Exception, keep trying.")
                }

            }
        }
    }
    return null
}

