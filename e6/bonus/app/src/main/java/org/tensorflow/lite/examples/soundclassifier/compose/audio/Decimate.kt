package org.tensorflow.lite.examples.soundclassifier.compose.audio

import com.github.psambit9791.jdsp.signal.Decimate


class Decimate(val oldSampleRate: Int, newSampleRate: Int ) {
    private val decimateFactor = oldSampleRate / newSampleRate


    fun process(floatArray: FloatArray):DoubleArray {

        val d = Decimate(toDouble(floatArray) , oldSampleRate, false)
        //return toFloat(d.decimate(decimateFactor))
        return d.decimate(decimateFactor)

    }

    private fun toDouble(floatArray: FloatArray):DoubleArray{
        val double = DoubleArray(floatArray.size)
        for (i in floatArray.indices) {
            double[i]=floatArray[i].toDouble()
        }
        return double
    }

    private fun toFloat(double: DoubleArray):FloatArray{
        val float = FloatArray(double.size)
        for (i in double.indices) {
            float[i]=double[i].toFloat()
        }
        return float
    }
}