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

import android.content.res.Configuration
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.sizeIn
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material.Divider
import androidx.compose.material.LinearProgressIndicator
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Scaffold
import androidx.compose.material.Slider
import androidx.compose.material.SliderDefaults
import androidx.compose.material.Surface
import androidx.compose.material.Switch
import androidx.compose.material.SwitchDefaults
import androidx.compose.material.Text
import androidx.compose.material.TopAppBar
import androidx.compose.material.primarySurface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.tooling.preview.Devices
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import org.tensorflow.lite.examples.soundclassifier.compose.R
import org.tensorflow.lite.examples.soundclassifier.compose.ui.theme.SoundClassifierTheme
import org.tensorflow.lite.examples.soundclassifier.compose.ui.theme.gray800
import org.tensorflow.lite.examples.soundclassifier.compose.ui.theme.orange500
import org.tensorflow.lite.examples.soundclassifier.compose.ui.theme.progressColorPairs
import org.tensorflow.lite.support.label.Category

@Composable
fun SoundClassifierScreen(viewModel: SoundClassifierViewModel) {
  val classifierEnabled by viewModel.classifierEnabled.collectAsState()


  SoundClassifierTheme {
    Surface(color = MaterialTheme.colors.background) {
      Scaffold(
        topBar = {
          TopAppBar(
            title = {
              Image(
                painter = painterResource(R.drawable.tfl2_logo),
                contentDescription = stringResource(id = R.string.tensorflow_lite_logo),
                modifier = Modifier.sizeIn(maxWidth = 180.dp),
              )
            },
            backgroundColor = MaterialTheme.colors.primarySurface
          )
        }
      ) { innerPadding ->
        SoundClassifierScreen(
          classifierEnabled = classifierEnabled,
          onClassifierToggle = viewModel::setClassifierEnabled,
          modifier = Modifier.padding(innerPadding),
        )
      }
    }
  }
}

@Composable
private fun SoundClassifierScreen(
  classifierEnabled: Boolean,
  onClassifierToggle: (Boolean) -> Unit,
  modifier: Modifier = Modifier,
) {
  Column(
    modifier = modifier.padding(16.dp)
  ) {
    ControlPanel(
      inputEnabled = classifierEnabled,
      onInputChanged = onClassifierToggle,
    )

    Divider(modifier = Modifier.padding(vertical = 24.dp))
  }
}

@Composable
fun ControlPanel(
  inputEnabled: Boolean,
  onInputChanged: ((Boolean) -> Unit) = {},
) {
  Row {
    val labelText = stringResource(id = R.string.label_input)
    Text(labelText, style = MaterialTheme.typography.body1)
    Switch(
      checked = inputEnabled,
      onCheckedChange = onInputChanged,
      modifier = Modifier.padding(start = 16.dp),
      colors = SwitchDefaults.colors(checkedThumbColor = orange500)
    )
  }
  Spacer(modifier = Modifier.height(12.dp))
}


@Preview(name = "Day mode, small device", widthDp = 360, heightDp = 640)
@Preview(
  name = "Night mode, small device", widthDp = 360, heightDp = 640,
  uiMode = Configuration.UI_MODE_NIGHT_YES,
)
@Preview(name = "Day mode", device = Devices.PIXEL_4_XL)
@Composable
fun Preview() {
  SoundClassifierTheme {
    Surface(color = MaterialTheme.colors.background) {
      SoundClassifierScreen(
        classifierEnabled = true,
        onClassifierToggle = {},
      )
    }
  }
}
