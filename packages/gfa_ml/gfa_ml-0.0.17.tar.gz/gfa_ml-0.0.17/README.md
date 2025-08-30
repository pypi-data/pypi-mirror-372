# Green Factory AI ML Library - gfa-ml

This is the library to support data scientist in building end-to-end ML pipeline


<figure>
<p style="text-align:center">
<img src="docs/img/ML_pipeline.svg" alt="pipeline overview" width="1000"/>
</p>
<figcaption>
<p style="text-align:center">
Fig 1. Pipeline Overview
</p>
</figcaption>
</figure>


## 1. Data Analysis
More details can be found in the [data_analysis](docs/data_analysis.md) folder.
<figure>
<p style="text-align:center">
<img src="docs/img/data_analysis.svg" alt="data analysis" width="1000"/>
</p>
<figcaption>
<p style="text-align:center">
Fig 2. Overview of the data analysis process
</p>
</figcaption>
</figure>



## 2.Serving Pipeline
Progress: on going

<figure>
<p style="text-align:center">
<img src="docs/img/serving_pipeline.svg" alt="serving pipeline" width="1000"/>
</p>
<figcaption>
<p style="text-align:center">
Fig 3. End-to-end ML serving pipeline
</p>
</figcaption>
</figure>

## 3. DevOps
### 3.1. Lifecycle overview
More details can be found in the [devops_lifecycle](docs/dev.md) folder.

<figure>
<p style="text-align:center">
<img src="docs/img/lifecycle.svg" alt="DevOps Lifecycle" width="1000"/>
</p>
<figcaption>
<p style="text-align:center">
Fig 4. DevOps Lifecycle
</p>
</figcaption>
</figure>

### 3.2. [dev](dev)
Implements tools and utilities to support the DevOps lifecycle
- Generate UML diagrams for the codebase

### 3.3. [gfa_ml](gfa_ml)
Contains the main library code, including data model abstractions, data analysis, and serving pipeline. 

#### 3.3.1. [Lib](gfa_ml/lib)
- Common functions using the data model abstractions is implemented in `lib/common.py`
- Utilities (not using the data model abstractions) are implemented in `lib/utils.py`
- Constant values are defined in `lib/constant.py`

#### 3.3.2. Data Model
This module provides abstract classes for the whole framework.
More details can be found in the [data_model](docs/data_model.md) folder

## 5. Testing
Can be found in the [test](test) folder. It includes unit tests for data model abstractions, data analysis, and serving pipeline.

## 6. Data 
Contains some data from relevant projects (e.g., [enocell_pilot](data/enocell_pilot))