from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='strongmind-platform-sdk',
    version='3.8.2',
    packages=find_packages(),
    url='https://github.com/StrongMind/platform-python-sdk',
    license='',
    author='Team Platform',
    author_email='platform@strongmind.com',
    description='Common utilities, models, and clients used with StrongMind Platform APIs',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.7',
    install_requires=[
        'pytz',
        'strongmind-oneroster-client>=2.0.3',
        'pydantic>=1.10.11',
        'cryptography>=37.0.4',
        'sentry-sdk'
    ],
)
