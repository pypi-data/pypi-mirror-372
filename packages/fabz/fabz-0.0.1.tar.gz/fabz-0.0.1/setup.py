from setuptools import setup

# Minimal placeholder to reserve the 'fabz' name on PyPI
setup(
    name="fabz",
    version="0.0.1",
    description="Hierarchical Docker Compose deployment tool - Coming Soon",
    long_description="""
# fabz

A hierarchical Docker Compose deployment tool that merges YAML properties 
into compose files across deployment models.

**This package is currently under development and not ready for use.**

## Planned Features

- Hierarchical model structure with property merging
- Custom templating system with conditional logic  
- Dynamic property resolution
- Machine-based deployment with SSH integration
- Global configuration support
- Extensible command system

## Repository

Development: https://github.com/your-username/fabz

**Please check back later for the full release!**
""",
    long_description_content_type="text/markdown",
    author="Ritchie",
    author_email="your.email@example.com",  # Replace with your email
    url="https://github.com/your-username/fabz",  # Replace with your repo
    py_modules=['fabz_placeholder'],  # Single module approach
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Build Tools",
    ],
    keywords="docker, compose, deployment, devops, placeholder",
    entry_points={
        'console_scripts': [
            'fabz=fabz_placeholder:main',
        ],
    },
)
