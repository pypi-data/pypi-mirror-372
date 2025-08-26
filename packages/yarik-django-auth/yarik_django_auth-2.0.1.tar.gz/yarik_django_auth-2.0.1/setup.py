from setuptools import setup, find_packages

setup(
    name="yarik-django-auth",
    version="2.0.01",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django>=5.1.7",
        "PyJWT==2.9.0",
        "asgiref==3.8.1",
        "requests==2.32.3",
        "cryptography==44.0.1",
    ],
    classifiers=[
    "Environment :: Web Environment",
    "Framework :: Django",
    "Framework :: Django :: 5.2",  
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
