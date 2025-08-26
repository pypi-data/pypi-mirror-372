# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

This is an MLflow Plugin Manager that integrates with MLflow's web interface to allow users to install, update, and uninstall MLflow plugins. The project has two main components:

1. **MLflow Plugin Component** (`mlflow_plugin_manager/`): A Flask app that integrates with MLflow via entry points
2. **Standalone Server** (`server/`): A separate Flask server that maintains a plugin database and serves plugin metadata

### Key Components

- `mlflow_plugin_manager/__init__.py`: Main MLflow integration that extends the MLflow server with plugin management routes
- `mlflow_plugin_manager/api/endpoints.py`: API endpoints for plugin operations (install, uninstall, update, list)
- `mlflow_plugin_manager/templates/plugin_manager_modern.html`: Modern UI template matching MLflow 3's design
- `mlflow_plugin_manager/static/mlflow-style.css`: CSS styles matching MLflow 3's look and feel
- `server/app.py`: Standalone Flask server with SQLAlchemy models for Plugin and User management
- `server/reindex_plugins.py`: Script to populate the database with available MLflow plugins from PyPI

## Quick Start Guide

### Prerequisites
- Python 3.8+
- pyenv (recommended for managing Python versions)
- pip

### Initial Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd mlflow-plugin-manager
```

2. **Create and activate Python environment**
```bash
# Using pyenv (recommended)
pyenv virtualenv 3.11.0 mlflow-plugin-manager
pyenv activate mlflow-plugin-manager

# Or using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install the package in development mode**
```bash
pip install -e .
```

4. **Initialize the plugin database**
```bash
cd server
python reindex_plugins.py
cd ..
```

### Running the Application

#### Option 1: Run with MLflow Server (Recommended)

1. **Activate the environment**
```bash
pyenv activate mlflow-plugin-manager
```

2. **Start MLflow server with plugin manager**
```bash
mlflow server --app-name plugin_manager
```

3. **Access the application**
- MLflow UI: http://localhost:5000
- Plugin Manager: http://localhost:5000/plugin-manager/
- Click "Plugins" in the sidebar to access the plugin manager

#### Option 2: Run Standalone Server (for development)

1. **Start the standalone server**
```bash
cd server
python app.py
```
The server will run on http://localhost:5001

### Common Commands

#### Environment Activation
```bash
# Always activate the environment first
pyenv activate mlflow-plugin-manager

# Or if using venv
source venv/bin/activate
```

#### Running MLflow with Plugin Manager
```bash
# For local development with local plugin server
export PLUGIN_SERVER_URL="http://localhost:5001"

# For production (uses api.mlflowplugins.com by default)
# No need to set PLUGIN_SERVER_URL

# Run MLflow with the plugin manager
mlflow server --app-name plugin_manager
```

#### Refreshing Plugin Database
```bash
cd server
python reindex_plugins.py
```

## Troubleshooting

### Issue: "mlflow: command not found"
**Solution:** Activate the Python environment first:
```bash
pyenv activate mlflow-plugin-manager
```

### Issue: "Address already in use"
**Solution:** Kill existing MLflow processes:
```bash
pkill -f "mlflow server"
# or
lsof -i :5000  # Find process using port 5000
kill <PID>     # Kill the process
```

### Issue: Template not updating
**Solution:** The server may be caching templates. Restart the MLflow server:
```bash
pkill -f "mlflow server"
mlflow server --app-name plugin_manager
```

### Issue: Plugin installation fails
**Solution:** Ensure you have proper permissions and pip is up to date:
```bash
pip install --upgrade pip
# Try installing with user flag
pip install --user <plugin-name>
```

## Development Workflow

### Making UI Changes

1. **Edit templates**: Update files in `mlflow_plugin_manager/templates/`
2. **Edit styles**: Modify `mlflow_plugin_manager/static/mlflow-style.css`
3. **Restart server**: Changes require server restart to take effect
```bash
pkill -f "mlflow server"
mlflow server --app-name plugin_manager
```

### Testing Plugin Operations

1. **Install a test plugin**:
   - Navigate to http://localhost:5000/plugin-manager/
   - Click "Install" on any available plugin
   
2. **Check for updates**:
   - Click "Check for Updates" button
   
3. **Uninstall a plugin**:
   - Click "Uninstall" on any installed plugin

### Database Management

The project uses SQLAlchemy with Flask-Migrate for database management. Database files are located at:
- `mlflow_plugin_manager/instance/plugins.db`
- `server/instance/plugins.db`

Migration files are in `server/migrations/`.

## Configuration

### Environment Variables

- `PLUGIN_SERVER_URL`: URL of the plugin metadata server
  - Default: `https://api.mlflowplugins.com`
  - For local development: `http://localhost:5001`
  
Example:
```bash
export PLUGIN_SERVER_URL="http://localhost:5001"
mlflow server --app-name plugin_manager
```

## Plugin Discovery and Installation

The system discovers MLflow plugins by:
1. Querying PyPI for packages containing "mlflow" 
2. Storing plugin metadata in a local SQLite database
3. Using `pip` commands to install/uninstall plugins via subprocess calls
4. Supporting version-specific installations (e.g., `mlflow-skinny==2.9.2`)

## UI Design

The plugin manager UI follows MLflow 3's design language:
- **Color Scheme**: Blue primary color (#1890ff)
- **Typography**: System fonts with clean, modern styling
- **Layout**: Clean white cards with minimal shadows
- **Icons**: SVG icons instead of emoji
- **Responsive**: Works on desktop and mobile devices

## Logging

Logs are written to:
- `mlflow_plugin_manager/logs/plugin_manager.log`
- `server/logs/plugin_manager.log`

## Important Notes

- Always run commands from the project root unless specified otherwise
- The plugin manager integrates directly with MLflow's web interface
- Plugin installation/uninstallation affects the current Python environment
- The UI automatically matches MLflow 3's look and feel for consistency