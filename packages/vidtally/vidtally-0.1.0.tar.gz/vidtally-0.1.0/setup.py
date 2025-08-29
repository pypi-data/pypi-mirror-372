from setuptools import setup, find_packages
from setuptools.command.install import install

class CustomInstall(install):
    def run(self):
        install.run(self)
        print("\nIMPORTANT: This tool requires ffmpeg to be installed on your system.")
        print("Please follow the instructions in README.md to install ffmpeg for your OS.")
        print("Without it, the tool will not work.\n")

setup(
    name='vidtally',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['rich', 'pyfiglet', 'typer'],
    entry_points={
        'console_scripts': [
            'vidtally = video_duration_tool.duration:app'
        ]
    },
    author='Abdul Rehman Yousaf',
    author_email='abdul@9to5ml.com',
    description='VidTally: A beautiful CLI tool to tally durations of MP4 files in a folder',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    cmdclass={'install': CustomInstall},
)