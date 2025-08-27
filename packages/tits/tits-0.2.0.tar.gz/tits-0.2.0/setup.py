from setuptools import setup, find_packages

setup(
    name="tits",
    version="0.2.0",
    author="حسو ال علي",
    author_email="lyhasneen70@gmail.com",
    description="مكتبة بايثون لتسهيل الفحص وغيره",
    long_description="لاتنوصف",
    long_description_content_type="text/markdown",
    url="https://hso1.netlify.app",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["requests", "user_agent"],  # ← أضفتها
    python_requires=">=3.8",
)