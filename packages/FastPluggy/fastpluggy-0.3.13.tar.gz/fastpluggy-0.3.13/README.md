
# FastPluggy

**FastPluggy** is a FastAPI-based framework that simplifies the process of building modular applications with plugin management and database handling. It allows you to easily configure plugins, static files, Jinja2 templates, and databases, making it a powerful and flexible solution for FastAPI projects.

## Features

- **Plugin Management**: Easily manage, enable, disable, and configure plugins.
- **Database Integration**: Supports SQLAlchemy for database handling.
- **Static Files and Templates**: Serve static files and Jinja2 templates seamlessly.
- **Extensibility**: Use FastPluggy as a library to extend your FastAPI applications.
- **Simple Setup**: Configure your project with a single class, easy initialization.

## Installation

You can install **FastPluggy** using pip:

```bash
pip install FastPluggy
```

## Getting Started

### 1. Create a FastAPI App with FastPluggy

In your FastAPI project, import `FastPluggy` from **FastPluggy** and use it to configure your app:

```python
from fastapi import FastAPI
from fastpluggy.fastpluggy import FastPluggy

app = FastAPI()

# Initialize the FastPluggy class which sets up everything
fast_pluggy = FastPluggy(app)

# Run the application using Uvicorn or another ASGI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fast_pluggy.app, host="0.0.0.0", port=8000)

```

### 2. Running the Application

Once the configuration is complete, you can run the FastAPI app using Uvicorn:

```bash
uvicorn your_project:app --reload
```

### 3. Plugin Management

With **FastPluggy**, managing plugins is straightforward. 
The `PluginManager` class handles loading, enabling, disabling, and configuring plugins in your application.
You can define plugins and control their behavior from the admin interface or directly in code.

### Example Plugin Definition

To create a plugin, simply create a Python module with a FastAPI router and define plugin-specific functionality.

```python
from fastapi import APIRouter

plugin_router = APIRouter()

@plugin_router.get("/hello")
def hello_plugin():
    return {"message": "Hello from the plugin!"}
```

**FastPluggy** will automatically detect and integrate this plugin into your application.

## File Structure

After installing **FastPluggy**, your project structure might look like this:

```
your_project/
│
├── src/
│   ├── your_project/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── core/
│   │   ├── templates/
│   │   ├── static/
│   └── your_project.egg-info/
│
├── tests/
├── README.md
├── setup.py
└── pyproject.toml
```

- **main.py**: Entry point for your application.
- **core/**: Core logic for plugins, database handling, etc.
- **templates/**: Jinja2 templates for rendering HTML.
- **static/**: Static files like CSS and JavaScript.
- **tests/**: Directory for unit tests.

## Contributing

Contributions are welcome! If you'd like to contribute to **FastPluggy**, please fork the repository and submit a pull request. Be sure to follow the contribution guidelines.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Links

- [Homepage](https://fastpluggy.xyz)
- [Documentation](https://docs.fastpluggy.xyz)
