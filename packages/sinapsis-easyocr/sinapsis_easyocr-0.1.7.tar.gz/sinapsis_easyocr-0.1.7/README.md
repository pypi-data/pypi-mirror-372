<h1 align="center">
<br>
<a href="https://sinapsis.tech/">
  <img
    src="https://github.com/Sinapsis-AI/brand-resources/blob/main/sinapsis_logo/4x/logo.png?raw=true"
    alt="" width="300">
</a><br>
Sinapsis EasyOCR
<br>
</h1>

<h4 align="center">EasyOCR-based Optical Character Recognition (OCR) for images</h4>

<p align="center">
<a href="#installation">🐍 Installation</a> •
<a href="#features">🚀 Features</a> •
<a href="#usage">📚 Usage example</a> •
<a href="#webapp">🌐 Webapp</a> •
<a href="#documentation">📙 Documentation</a> •
<a href="#license">🔍 License</a>
</p>

**Sinapsis EasyOCR** provides a powerful and flexible implementation for extracting text from images using the EasyOCR engine. It enables users to easily configure and run OCR tasks with minimal setup.

<h2 id="installation">🐍 Installation</h2>

Install using your package manager of choice. We encourage the use of <code>uv</code>

Example with <code>uv</code>:

```bash
  uv pip install sinapsis-easyocr --extra-index-url https://pypi.sinapsis.tech
```
 or with raw <code>pip</code>:
```bash
  pip install sinapsis-easyocr --extra-index-url https://pypi.sinapsis.tech
```

> [!IMPORTANT]
> Templates may require extra dependencies. For development, we recommend installing the package with all the optional dependencies:
>

with <code>uv</code>:

```bash
  uv pip install sinapsis-easyocr[all] --extra-index-url https://pypi.sinapsis.tech
```
 or with raw <code>pip</code>:
```bash
  pip install sinapsis-easyocr[all] --extra-index-url https://pypi.sinapsis.tech
```

> [!TIP]
> Use CLI command ```sinapsis info --all-template-names``` to show a list with all the available Template names installed with Sinapsis OCR.

> [!TIP]
> Use CLI command ```sinapsis info --example-template-config EasyOCR``` to produce an example Agent config for the EasyOCR template.

<h2 id="features">🚀 Features</h2>

<h3>Templates Supported</h3>

This module includes a template tailored for the EasyOCR engine:

- **EasyOCR**: Extracts text from images using EasyOCR, along with their bounding boxes and confidence scores.

<details>
<summary><strong><span style="font-size: 1.25em;">EasyOCR Attributes</span></strong></summary>

- **`reader_params`** (dict): Parameters for initializing the EasyOCR Reader. Defaults to `{"lang_list": ["en"]}`.
- **`read_text_params`** (dict, optional): Parameters for the EasyOCR readtext method. Defaults to `None`.
- **`get_full_text`** (bool): Whether to save detected text in a TextPacket. Defaults to `False`.

</details>

<h2 id="usage">📚 Usage example</h2>

<details>
<summary><strong><span style="font-size: 1.4em;">EasyOCR Example</span></strong></summary>

```yaml
agent:
  name: easyocr_inference
  description: agent to run inference with EasyOCR, performs on images read, recognition and save

templates:
- template_name: InputTemplate
  class_name: InputTemplate
  attributes: {}

- template_name: FolderImageDatasetCV2
  class_name: FolderImageDatasetCV2
  template_input: InputTemplate
  attributes:
    data_dir: dataset/input

- template_name: EasyOCR
  class_name: EasyOCR
  template_input: FolderImageDatasetCV2
  attributes: {}

- template_name: BBoxDrawer
  class_name: BBoxDrawer
  template_input: EasyOCR
  attributes:
    draw_confidence: True
    draw_extra_labels: True

- template_name: ImageSaver
  class_name: ImageSaver
  template_input: BBoxDrawer
  attributes:
    save_dir: output
    root_dir: dataset
```
</details>

To run, simply use:

```bash
sinapsis run name_of_the_config.yml
```

<h2 id="webapp">🌐 Webapp</h2>

The webapp provides a simple interface to extract text from images using EasyOCR. Upload your image, and the app will process it and display the detected text with bounding boxes.

> [!IMPORTANT]
> To run the app you first need to clone the sinapsis-ocr repository:

```bash
git clone https://github.com/Sinapsis-ai/sinapsis-ocr.git
cd sinapsis-ocr
```

> [!NOTE]
> If you'd like to enable external app sharing in Gradio, `export GRADIO_SHARE_APP=True`

> [!TIP]
> By default, the webapp uses EasyOCR. No additional configuration is needed.

<details>
<summary id="docker"><strong><span style="font-size: 1.4em;">🐳 Docker</span></strong></summary>

**IMPORTANT** This docker image depends on the sinapsis:base image. Please refer to the official [sinapsis](https://github.com/Sinapsis-ai/sinapsis?tab=readme-ov-file#docker) instructions to Build with Docker.

1. **Build the sinapsis-ocr image**:

```bash
docker compose -f docker/compose.yaml build
```

2. **Start the app container**:

```bash
docker compose -f docker/compose_app.yaml up
```

3. **Check the status**:

```bash
docker logs -f sinapsis-ocr-app
```

4. The logs will display the URL to access the webapp, e.g.:

**NOTE**: The url can be different, check the output

```bash
Running on local URL:  http://127.0.0.1:7860
```

5. To stop the app:

```bash
docker compose -f docker/compose_app.yaml down
```

</details>

<details>
<summary id="uv"><strong><span style="font-size: 1.4em;">💻 UV</span></strong></summary>

To run the webapp using the <code>uv</code> package manager, please:

1. **Create the virtual environment and sync the dependencies**:

```bash
uv sync --frozen
```

2. **Install packages**:
```bash
uv pip install sinapsis-easyocr[all] --extra-index-url https://pypi.sinapsis.tech
```
3. **Run the webapp**:

```bash
uv run webapps/gradio_ocr.py
```

4. **The terminal will display the URL to access the webapp, e.g.**:

```bash
Running on local URL:  http://127.0.0.1:7860
```
NOTE: The url can be different, check the output of the terminal

5. To stop the app press `Control + C` on the terminal

</details>

<h2 id="documentation">📙 Documentation</h2>

Documentation for this and other sinapsis packages is available on the [sinapsis website](https://docs.sinapsis.tech/docs)

Tutorials for different projects within sinapsis are available at [sinapsis tutorials page](https://docs.sinapsis.tech/tutorials)

<h2 id="license">🔍 License</h2>

This project is licensed under the AGPLv3 license, which encourages open collaboration and sharing. For more details, please refer to the [LICENSE](LICENSE) file.

For commercial use, please refer to our [official Sinapsis website](https://sinapsis.tech) for information on obtaining a commercial license.
