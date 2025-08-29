from setuptools import setup, find_packages

setup(
    name='taman',
    version='0.1.0',
    description='A system monitoring API with real-time process tracking and resource usage',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Your Name',
    author_email='your.email@example.com',
    url='https://github.com/yourusername/taman',
    packages=find_packages(),
    install_requires=[
        'fastapi>=0.100.0',
        'psutil>=5.9.0',
        'uvicorn>=0.20.0',
        'wmi>=1.5.1; sys_platform == "win32"',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-asyncio>=0.21.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'taman=taman.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Topic :: System :: Monitoring',
        'Framework :: FastAPI',
    ],
    python_requires='>=3.8',
    keywords='system monitoring fastapi process resource',
)