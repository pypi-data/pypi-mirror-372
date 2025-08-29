from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    long_description = f.read()

with open("LICENSE", 'r') as f:
    license = f.read()

project_urls = {
  'GitHub': 'https://github.com/sidqdev/django-morest',
  'Telegram': 'https://t.me/sidqdev'
}

setup(
    name='django-morest',
    version='0.1.2',
    author='Sidq',
    author_email='abba.dmytro@gmail.com',
    description='Django api manager and unifier',
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    license=license,
    project_urls=project_urls,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        "django",
        "djangorestframework"
    ],
    package_data={'morest': ['templates/*.html']},
    include_package_data=True,
    python_requires='>=3.9',
)

