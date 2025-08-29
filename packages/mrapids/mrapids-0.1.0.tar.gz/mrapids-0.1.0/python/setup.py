import os
import sys
import platform
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install
import urllib.request
import tarfile
import zipfile

BINARY_URLS = {
    'Darwin-x86_64': {
        'mrapids': 'https://github.com/deepwissen/api-runtime/releases/download/v0.1.0/mrapids-darwin-x64.tar.gz',
        'mrapids-agent': 'https://github.com/deepwissen/api-runtime/releases/download/v0.1.0/mrapids-agent-darwin-x64.tar.gz'
    },
    'Darwin-arm64': {
        'mrapids': 'https://github.com/deepwissen/api-runtime/releases/download/v0.1.0/mrapids-darwin-arm64.tar.gz',
        'mrapids-agent': 'https://github.com/deepwissen/api-runtime/releases/download/v0.1.0/mrapids-agent-darwin-arm64.tar.gz'
    },
    'Linux-x86_64': {
        'mrapids': 'https://github.com/deepwissen/api-runtime/releases/download/v0.1.0/mrapids-linux-x64.tar.gz',
        'mrapids-agent': 'https://github.com/deepwissen/api-runtime/releases/download/v0.1.0/mrapids-agent-linux-x64.tar.gz'
    },
    'Windows-AMD64': {
        'mrapids': 'https://github.com/deepwissen/api-runtime/releases/download/v0.1.0/mrapids-win32-x64.zip',
        'mrapids-agent': 'https://github.com/deepwissen/api-runtime/releases/download/v0.1.0/mrapids-agent-win32-x64.zip'
    }
}

class InstallBinaries(install):
    def run(self):
        install.run(self)
        self.install_binaries()
    
    def install_binaries(self):
        system = platform.system()
        machine = platform.machine()
        platform_key = f"{system}-{machine}"
        
        if platform_key not in BINARY_URLS:
            print(f"Warning: No binaries available for {platform_key}")
            return
        
        bin_dir = os.path.join(self.install_scripts, 'microrapid_bin')
        os.makedirs(bin_dir, exist_ok=True)
        
        for binary, url in BINARY_URLS[platform_key].items():
            print(f"Downloading {binary}...")
            ext = 'zip' if url.endswith('.zip') else 'tar.gz'
            archive_path = os.path.join(bin_dir, f"{binary}.{ext}")
            
            # Download
            urllib.request.urlretrieve(url, archive_path)
            
            # Extract
            if ext == 'zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(bin_dir)
            else:
                with tarfile.open(archive_path, 'r:gz') as tar_ref:
                    tar_ref.extractall(bin_dir)
            
            # Clean up
            os.remove(archive_path)
            
            # Make executable
            binary_path = os.path.join(bin_dir, binary)
            if system != 'Windows':
                os.chmod(binary_path, 0o755)
            
            # Create wrapper script
            wrapper_path = os.path.join(self.install_scripts, binary)
            with open(wrapper_path, 'w') as f:
                if system == 'Windows':
                    f.write(f'@echo off\n"{binary_path}" %*')
                else:
                    f.write(f'#!/bin/sh\nexec "{binary_path}" "$@"')
            
            if system != 'Windows':
                os.chmod(wrapper_path, 0o755)
        
        print("✅ MicroRapid binaries installed successfully!")

setup(
    name='microrapid',
    version='0.1.0',
    description='MicroRapid - Your OpenAPI, but executable',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='MicroRapid Team',
    author_email='team@microrapid.dev',
    url='https://github.com/deepwissen/api-runtime',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
    cmdclass={
        'install': InstallBinaries,
    },
    entry_points={
        'console_scripts': [
            'mrapids=microrapid:main',
            'mrapids-agent=microrapid:agent_main',
        ],
    },
)