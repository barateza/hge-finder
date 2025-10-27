# Copilot Instructions: Software Requirements Specifications (SRS) for HGE Notifier App

## 1. Introduction

### 1.1 Purpose
This document outlines the Software Requirements Specifications (SRS) for a Python application designed to monitor Elite Dangerous Data Network (EDDN) for High Grade Emission (HGE) signals, compare them with the user’s latest location from their Elite Dangerous journal, and provide both command-line and web interfaces to inform the user about the nearest HGE location.

### 1.2 Scope
The targeted software will fetch and parse HGE-related system data in real-time from EDDN, track the user’s own latest location by parsing their local journal files, compute distances to HGE systems, and notify the user with a summary through:
- Command Line Interface (CLI)
- Web Interface (optional, for real-time status)

### 1.3 Audience
- Elite Dangerous players interested in HGE location tracking
- Developers wishing to extend or improve the tool

## 2. Functional Requirements

### 2.1 EDDN Data Ingestion
- The system must connect to EDDN and continuously listen for system signals related to HGE USS (Unidentified Signal Sources).
- The app must filter for message types that contain High Grade Emission events, extracting system name and timestamp.

### 2.2 User Location Tracking
- The system must monitor or parse the user’s Elite Dangerous journal file to update the latest known commander location in real time.
- If possible, this process should run live, updating as the player moves.

### 2.3 Distance Calculation
- The software must compute the distance (in light years) between the user’s current/last system and the system of the last-detected HGE. 
- Distance must be calculated using 3D coordinates (x, y, z) of star systems, sourced either from an online API or local database.

### 2.4 Notification/Reporting
#### CLI
- The CLI should at all times present:
  - Latest HGE system name and signal age
  - User’s current/last known location
  - Distance to the HGE system
- Provide a refresh or auto-update mechanism.

#### Web Interface
- A basic Flask web interface should mirror the core information:
  - Latest HGE details (system, time, etc.)
  - User location
  - Current distance
  - Auto-refresh or near real-time updates
- Option to trigger data refresh via UI.

### 2.5 Configuration
- Allow user to specify path to journal directory.
- Allow user to set refresh intervals and notification preferences.

## 3. Non-Functional Requirements

- Code should follow top Python PEP-8 standards for readability and maintainability.
- Use type hints and docstrings where appropriate.
- Modular structure to separate concerns (data ingestion, location, interface, etc.).
- Appropriately handle connection failures to EDDN, missing journal files, API timeouts, etc.
- Easily extensible to support additional data sources or notification methods.

## 4. System Architecture & Tech Stack

- **Language:** Python 3.9+
- **Web Framework:** Flask
- **EDDN Interface:** Existing Python libraries for EDDN (e.g., pyEDDN) or raw ZMQ implementation
- **Journal Parsing:** File streaming/monitoring or periodic directory scan
- **Distance Calculation:** Use of system coordinates from Elite Dangerous public API or local JSON dump
- **Testing:** pytest, flake8
- **Deployment:** No special requirements (standard Python environment)

IMPORTANT: Development will be made on a local machine with Windows OS with PowerShell as the primary terminal.

## 5. Security and Privacy
- No user credentials or sensitive data transmission required
- All data processing is local; journal files and location stay on user’s machine

## 6. Documentation & Standards
- Codebase must include internal docstrings and external documentation on setup, use, and extension.
- All key classes and methods must have docblocks with type signatures and clear descriptions.
- Basic README for software deployment and usage.
- Follow industry standard best practices for error handling, logging, and modularity.

## 7. Future Extensions (Optional/Ideas)
- Support for multiple users (fleet tracking)
- Push notifications (Discord, email)
- Advanced web UI with filtering and visualization

---