from setuptools import setup, find_packages

setup(
    name='django-ant-admin',
    version='0.1.0',
    description='自动生成 DRF CRUD 接口和文档的 Django app',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Daxu',
    author_email='xuh@daxu.cc',
    url='https://github.com/buslink/Dango-Ant-Admin',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=[
        'Django>=5.2',
        'djangorestframework>=3.15',
        'djangorestframework-simplejwt',
        'drf-spectacular',
        'django-filter',
    ],
    classifiers=[
        'Framework :: Django',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
)