from setuptools import setup, find_packages

setup(
    name="cosmotalker",
    version="2.45",  # Updated version
    author="Bhuvanesh M",
    author_email="bhuvaneshm.developer@gmail.com",
    description="CosmoTalker is your gateway to the universe! Whether you're fascinated by stars, planets, or scientific phenomena, this tool brings the cosmos closer to you.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/bhuvanesh-m-dev/cosmotalker",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "cosmotalker": ["celestial_knowledge.txt", "ss.txt","data.txt"]  # Ensure both files are included
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    project_urls={
        "Portfolio": "https://bhuvaneshm.in",
        "LinkedIn": "https://www.linkedin.com/in/bhuvaneshm-developer",
        "GitHub Repository": "https://github.com/bhuvanesh-m-dev/cosmotalker",
    },
)
