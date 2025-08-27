from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

print(f'detected packages: {setuptools.find_packages()}')

setuptools.setup(
    name="streamlit-image-carousel",
    # packages=['image-carousel'],
    version="0.0.11",
    author="Tristan Cotte",
    author_email="tristan.cotte@sgs.com",
    description="Streamlit component that allows you to display carousel images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    package_data={
        "streamlit_image_carousel": [
            "frontend/build/*",
        ],
    },
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 0.63",
    ],
    extras_require={
        "devel": [
            "wheel",
            "pytest==7.4.0",
            "playwright==1.48.0",
            "requests==2.31.0",
            "pytest-playwright-snapshot==1.0",
            "pytest-rerunfailures==12.0",
        ]
    }
)