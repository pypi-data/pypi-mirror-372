from setuptools import setup, find_packages

setup(
    name="django_auth_package",          
    version="0.1.0",
    description="A reusable authentication package for Django + DRF",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="NIYOKWIZERA JEAN D AMOUR",
    author_email="niyokwizerajd123@gmail.com",
    url="https://github.com/jeid12/django_auth",  
    packages=find_packages(),
    install_requires=[
        "asgiref==3.9.1",
        "Django==5.2.5",
        "django-filter==25.1",
        "djangorestframework==3.16.1",
        "djangorestframework_simplejwt==5.5.1",
        "Markdown==3.8.2",
        "PyJWT==2.10.1",
        "sqlparse==0.5.3",
        "tzdata==2025.2",
    ],
    python_requires=">=3.8",
    classifiers=[
        "Framework :: Django",
        "Framework :: Django :: 5.2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
