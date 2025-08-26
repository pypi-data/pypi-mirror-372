# 🚀 User Guide: Deploying Anomaly Detection Models in JetMET Monitoring

This guide explains how to use the provided **template format** to deploy multiple anomaly detection models (PyTorch, TensorFlow, ONNX, XGBoost, LightGBM, NMF) for monitoring JetMET elements such as **METSig** or **CHFrac_highPt_EndCap**.

The template is written in **YAML** and describes a set of **`InferenceService` resources** that can be deployed to your inference cluster.

---

## 📄 Template Overview

```yaml
TemplateFormatVersion: "2025-03-31"
Description: Deploy multiple models to spot anomalies in the JME METSig monitoring element
Resources:
  <ResourceName>:
    Type: <InferenceServiceType>
    Workspace: <workspace-name>
    Properties:
      ...
```

- **TemplateFormatVersion**: Version of the template schema. Always use the latest supported version (e.g., `2025-03-31`).
- **Description**: A human-readable description of what this template does.
- **Resources**: A list of models or services you want to deploy. Each resource corresponds to **one model**.

---

## ⚙️ Anatomy of a Resource

Each resource follows this general structure:

```yaml
<ResourceName>:
  Type: InferenceService::<Runtime>::<ModelFormat>
  Workspace: <workspace>
  Properties:
    Description: <text>
    Name: <service-name>
    MetricKey: <primary-output-key>
    BuiltinThreshold: <true|false>
    AnomalyThreshold: <float>
    InputSignature: [...]
    OutputSignature: [...]
    MaxBatchSize: <int>
    ModelUri | SavedModelUri | CodeUri: <path>
    Handler: <entrypoint-function>   # MLServer runtimes only
    Image: <container-image>         # Optional for custom runtimes
    Tags: [...]                      # Optional metadata
    Resources:
      Requests:
        cpu: <amount>
        memory: <amount>
        gpu: <amount>                # If requested, registration request will be further analyzed
      Limits:
        cpu: <amount>
        memory: <amount>
        gpu: <amount>                # If requested, registration request will be further analyzed
```

---

## 🧩 Field-by-Field Explanation

### 🔑 Top-level fields
- **Type**
  Defines the backend runtime and model format. Supported values include:
  - `InferenceService::Tritonserver::Torchscript`
  - `InferenceService::Tritonserver::TensorflowSavedModel`
  - `InferenceService::Tritonserver::ONNX`
  - `InferenceService::MLServer::XGBoost`
  - `InferenceService::MLServer::SKLearn`

- **Workspace**
  Logical grouping of services (e.g., `jetmet`) in DIALS.

---

### 📝 Properties

- **Description**
  Explains what the model does (e.g., "Spot anomalies in the MetSig distribution").

- **Name**
  A unique service identifier used for deployment and monitoring. Do note include the workspace name or your username.

- **MetricKey**
  The **output tensor name** from the model that will be used for anomaly scoring.
  - Example: `"output_1"`, `"Identity_1:0"`, or `"tf.math.reduce_mean_44"`

- **BuiltinThreshold**
  Whether to use a **built-in anomaly threshold**.
  - `true`: The model already outputs a binary anomaly flag.
  - `false`: Use **`AnomalyThreshold`** below to compute anomaly score.

- **AnomalyThreshold**
  A floating-point value used when `BuiltinThreshold: false`.
  Any output above this threshold is considered anomalous.
  This value can be later updated through DIALS user interface.

- **FlaggingKey** *(optional)*
  For models with built-in flagging outputs. Specifies which tensor contains the anomaly flag.

---

### 📥 InputSignature

Defines the input monitoring element and expected tensor format.

Example:
```yaml
InputSignature:
  - Name: input_0
    MonitoringElement: JetMET/MET/pfMETT1/Cleaned/METSig
    DataType: TYPE_FP32
    Dims:
      - -1     # batch dimension
      - 51    # feature size
```

- **Name**: Input tensor name (must match the model).
- **MonitoringElement**: Path in the monitoring framework (e.g., CMS DQM histogram).
- **DataType**: Data type (`TYPE_FP32`, `TYPE_INT64`, etc.).
- **Dims**: Tensor dimensions. Use `-1` for variable batch size.

---

### 📤 OutputSignature

Describes model outputs:

Example:
```yaml
OutputSignature:
  - Name: output_0
    DataType: TYPE_FP32
    Dims:
      - -1
      - 51
  - Name: output_1
    DataType: TYPE_FP32
    Dims:
      - -1
```

- **Name**: Output tensor name.
- **DataType**: Tensor data type.
- **Dims**: Tensor shape (`-1` = variable).

---

### 📦 Model Paths

- **ModelUri**
  Path to the model artifact (Torchscript `.pt`, ONNX `.onnx`, etc.).

- **SavedModelUri**
  Used for TensorFlow SavedModels (directory containing `saved_model.pb`).

- **CodeUri**
  Path to custom model handler code (for MLServer runtimes).

- **Handler**
  Entry function that loads and serves the model (Python).

- **Image**
  Optional custom runtime container image, the image should be publicly reachable so that Kubeflow can download it.

---

### 🏷 Tags

Arbitrary key/value pairs for metadata, such as training run numbers:

```yaml
Tags:
  - Name: trained-run
    Value: "398407"
```

Those values can be later used for filtering models in DIALS user interface.

---

### 🖥 Resources

Defines **CPU/memory requests and limits**:

```yaml
Resources:
  Requests:
    cpu: "0.1m"    # minimum CPU
    memory: "250m"
    gpu: "0"
  Limits:
    cpu: "1"       # max CPU
    memory: "2Gi"
    gpu: "0"
```

- **Requests**: Minimum guaranteed resources.
- **Limits**: Maximum resources allocated.

---

## 📚 Example: Deploying a PyTorch Autoencoder

```yaml
MetSigPyTorchAutoEncoder:
  Type: InferenceService::Tritonserver::Torchscript
  Workspace: jetmet
  Properties:
    Description: Spot anomalies in the MetSig distribution
    Name: metsig-torchscript-autoencoder
    MetricKey: output_1
    BuiltinThreshold: false
    AnomalyThreshold: 0.1
    InputSignature:
      - Name: input_0
        MonitoringElement: JetMET/MET/pfMETT1/Cleaned/METSig
        DataType: TYPE_FP32
        Dims:
          - -1
          - 51
    OutputSignature:
      - Name: output_0
        DataType: TYPE_FP32
        Dims:
          - -1
          - 51
      - Name: output_1
        DataType: TYPE_FP32
        Dims:
          - -1
    MaxBatchSize: 0
    ModelUri: examples/models/torchscript/model.pt
    Resources:
      Requests:
        cpu: "0.1m"
        memory: "250m"
      Limits:
        cpu: "1"
        memory: "2Gi"
```

## 📚 Example: Deploying a NMF model

```yaml
  MetSigNMFRegressor:
    Type: InferenceService::MLServer::SKLearn
    Workspace: jetmet
    Properties:
      Description: Spot anomalies in the MetSig distribution
      Name: metsig-nmf-autoencoder
      MetricKey: output_1
      BuiltinThreshold: false
      AnomalyThreshold: 0.1
      InputSignature:
        - Name: input_0
          MonitoringElement: JetMET/MET/pfMETT1/Cleaned/METSig
          DataType: TYPE_FP32
          Dims:
            - -1
            - 51
      OutputSignature:
        - Name: output_0
          DataType: TYPE_FP32
          Dims:
            - -1
            - 51
        - Name: output_1
          DataType: TYPE_FP32
          Dims:
            - -1
      CodeUri: examples/models/sklearn_nmf/
      Handler: app.Handler
      ModelUri: examples/models/sklearn_nmf/model.joblib
      Resources:
        Requests:
          cpu: "0.1m"
          memory: "250m"
        Limits:
          cpu: "1"
          memory: "2Gi"
```

---

## ✅ Best Practices

- Always **match tensor names** (`input_0`, `output_1`, etc.) with your model’s exported graph.
- Use **`BuiltinThreshold: true`** only if your model outputs anomaly flags directly.
- Use **tags** to track training runs and provenance.
- Always specify a **workspace** that you are responsible for deploying models.

---

## 📌 Supported Runtimes & Formats

| Runtime                  | Formats Supported   |
|---------------------------|---------------------|
| Tritonserver              | Torchscript, TensorflowSavedModel, ONNX |
| MLServer                  | XGBoost, LightGBM, SKLearn (LightGBM, NMF, etc.) |

---

## 🛠 How to Build Your Own Template

1. Copy the **skeleton YAML**.
2. Pick a **runtime** (`Tritonserver` or `MLServer`).
3. Fill in:
   - Model path (`ModelUri`, `SavedModelUri`, or `CodeUri`)
   - Input/Output signatures
   - Resource requests/limits
   - MetricKey and thresholds

---

## 📑 Quick Reference Cheatsheet

| Field              | Description |
|--------------------|-------------|
| TemplateFormatVersion | Schema version for the template |
| Description        | Human-readable summary of the template |
| Resources          | Collection of deployed inference services |
| Type               | Runtime + model format (Tritonserver / MLServer) |
| Workspace          | Namespace grouping services |
| Properties         | Configuration of the model service |
| Name               | Unique deployment name |
| MetricKey          | Output tensor used for anomaly scoring |
| BuiltinThreshold   | Whether to use model’s built-in anomaly flag |
| AnomalyThreshold   | Threshold value when BuiltinThreshold is false |
| FlaggingKey        | Output tensor with anomaly flag (optional) |
| InputSignature     | Input tensor specs (name, type, dims, source ME) |
| OutputSignature    | Output tensor specs (name, type, dims) |
| MaxBatchSize       | Maximum supported batch size |
| ModelUri           | Path to model artifact (Torchscript/ONNX/etc.) |
| SavedModelUri      | Path to TensorFlow SavedModel directory |
| CodeUri            | Path to custom model handler code |
| Handler            | Entrypoint function for MLServer runtimes |
| Image              | (Optional) Custom runtime container image |
| Tags               | Any kind of metadata |
| Resources.Requests | Minimum guaranteed CPU/memory |
| Resources.Limits   | Maximum allocated CPU/memory |

---
