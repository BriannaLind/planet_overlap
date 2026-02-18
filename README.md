# PlanetOverlap
Find and organize satellite images for area/time of interest (tailored for Planet Labs Imagery)

**planet_overlap** is a scalable satellite imagery query engine for retrieving and filtering PlanetScope imagery over large areas and long time periods.

It supports:

- 📍 Multiple Areas of Interest (AOIs)
- 📌 Automatic buffering of point inputs
- 🗺 Automatic spatial tiling (in degrees)
- 📅 Flexible date range filtering
- ☁ Cloud cover filtering (0–1 fraction)
- ☀ Sun angle filtering (degrees)
- 📊 Progress tracking
- 🔁 Retry + timeout handling
- 🧠 Runtime and memory profiling
- 🧪 Automated testing (CI-enabled)

---

# 🚀 What It Does

You provide:

- A geographic area (GeoJSON file)
- A date range (YYYY-MM-DD format)
- Image quality filters (cloud cover, sun angle)
- An output directory

The system:

1. Connects to the Planet API
2. Filters imagery by date and quality
3. Automatically tiles large areas (if needed)
4. Tracks progress during execution
5. Logs runtime (seconds) and peak memory usage (MB)
6. Saves structured output


---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/your-username/planet_overlap.git
cd planet_overlap
```
Install locally:

```bash
pip install .
```
---
## 🔑 Planet API Key
Set your API key as an environment variable:
#### macOS/Linux


```bash
export PLANET_API_KEY=your_api_key_here
```

#### Windows (PowerShell)
```bash
setx PLANET_API_KEY "your_api_key_here"
```
---
## 🛰 Basic Usage

Run from CLI:
```bash
planet_overlap \
  --aoi-file aoi.geojson \
  --start-date 2023-01-01 \
  --end-date 2023-01-31 \
  --output-dir ./output
```

## 📅 Date Filtering

Dates must be provided in ISO format:
```bash
YYYY-MM-DD
```
Example: 
```bash
2023-01-01
```
**The system calculates the total date span in days. If the date range exceeds 30 days, spatial tiling is automatically applied.**


---
## ☁ Cloud Cover Filtering
Cloud cover is expressed as a fraction between 0.0 and 1.0:
| Value | Meaning          |
| ----- | ---------------- |
| 0.0   | 0% cloud cover   |
| 0.5   | 50% cloud cover  |
| 1.0   | 100% cloud cover |

```bash
--max-cloud 0.5
```
---
## ☀ Sun Angle Filtering
Sun angle is measured in degrees (°) above the horizon. Lower values may produce long shadows.
| Sun Angle (°) | Interpretation |
| ------------- | -------------- |
| 0°            | Sun at horizon |
| 10°           | Low sun        |
| 30°           | Moderate sun   |
| 60°+          | High sun       |


```bash
--min-sun-angle 10
```
## 🗺 Spatial Tiling
Large AOIs are automatically divided into grid tiles. This can also occur for long date ranges and memory-sensitive runs. Tile size is specified in decimal degrees (°):

```bash
--tile-size 1.0
```
Meaning:

* 1.0° latitude ≈ 111 km
* 1.0° longitude ≈ 111 km × cos(latitude)

At mid-latitudes (e.g., California):

* 1° ≈ ~80–111 km per side
* So a 1.0° tile is roughly: ~80–111 km × ~111 km

---
## 📌 Point Inputs
If your AOI contains:

* Point
* MultiPoint

They are automatically buffered into polygons.

Buffer size is specified in decimal degrees (°):


```bash
--point-buffer 0.001
```
0.001° ≈ 111 meters (latitude direction)

---
## 📊 Performance Tracking
Each run reports:

* Total runtime (seconds)
* Peak memory usage (megabytes, MB)
* Number of spatial tiles processed
* Progress percentage

Example log:


```yaml
Starting: run_pagination
Processing 138 tiles
Completed: run_pagination | Runtime: 270.41s | Peak Memory: 184.73 MB
```

---
## 🧪 Running Tests
Tests verify:

* Geometry handling
* Tiling behavior
* Point buffering
* Filter construction

Run all unit tests:


```bash
python -m unittest discover planet_overlap/tests
```

---
## 🔄 Continuous Integration (CI)
This repository includes GitHub Actions. On every push:
* Tests are executed
* Linting is performed (automatically analyzing your code (or configuration files) for errors, stylistic issues, or potential bugs as part of a workflow)
* Failures prevent merge

Workflow file:

```bash
.github/workflows/ci.yml
```

---
## 📂 Project Structure

```bash
README.md                 # Project documentation
pyproject.toml            # Project configuration
.gitignore                # Files Git should ignore
planet_overlap/
├── cli.py
├── geometry.py
├── filters.py
├── pagination.py
├── quality.py
├── analysis.py
├── performance.py
├── logger.py
├── client.py
├── io.py
└── tests/
    ├── __init__.py
    ├── test_geometry.py        # Test loading AOIs, point detection, buffering, polygons
    ├── test_filters.py         # Test single/multiple .geojson AOIs, date ranges, cloud/sun filters
    ├── test_client.py          # Test Planet API session creation, authentication, pagination
    ├── test_io.py              # Test reading/writing lists and CSV/GeoDataFrames
    ├── test_quality.py         # Test filtering by view_angle, sun_angle, cloud cover
    ├── test_overlap.py         # Test polygon intersection, area and sun angle calculations
    ├── test_analysis.py        # Test overall analysis pipeline logic, derived columns
    ├── test_cli.py             # Test CLI argument parsing, dynamic config, and default overrides
    ├── test_utils.py           # Test scene estimation, temporal tiling, and helper functions
    └── test_tiling.py          # Test automatic spatial and temporal tiling logic
```

---
## ⚙ Requirements
* Python ≥ 3.9
* requests
* geopandas
* shapely
* tqdm

