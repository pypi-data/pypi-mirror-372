from setuptools import find_packages, setup

with(open("README.md", "r", encoding="utf-8")) as f:
    long_description = f.read()

    setup(
    name="teaching_sim_eval",
    version="0.1.3",
    entry_points={
        "console_scripts": [
            "teaching-sim-eval=teaching_sim_eval.app:main",
        ],
    },
    package_dir={"": "src"},
    packages=find_packages(where="src", include=["teaching_sim_eval*"]),
    include_package_data=True,
     package_data={
        "teaching_sim_eval": [
            "*.py",
            "static/*.css",  # Include CSS files
            "static/*"       # Include all static files
        ]
    },
    description="Evaluating in-classroom teaching simulations leveraging the power of large language models.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xrtze/teaching_sim_eval",
    author="Jami Schorling",
    author_email="js68jynu@uni-leipzig.de",
    license="CC BY-NC 4.0",
    python_requires=">=3.12",
    install_requires=[
        "faicons==0.2.2",
        "groq==0.20.0",
        "jinja2==3.1.6",
        "keyring==25.6.0",
        "matplotlib==3.10.1",
        "openai==1.93.0",
        "pandas==2.2.3",
        "pyparsing==3.2.1",
        "python-docx==1.1.2",
        "shiny==1.4.0"
    ],
    extras_require={
        "dev": ["twine>=4.0.2"],
        }
    )