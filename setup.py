from setuptools import setup, find_packages
import os


setup_dir = os.path.dirname(__file__)
version_path = os.path.join(
    setup_dir, 'cloudwatch_logs_environment/version.py')
requirements_path = os.path.join(setup_dir, "requirements.txt")
requirements_dev_path = os.path.join(setup_dir, "requirements-dev.txt")

__version__ = None
with open(version_path) as f:
    code = compile(f.read(), version_path, 'exec')
    exec(code)

with open(requirements_path) as req_file:
    requirements = req_file.read().splitlines()

with open(requirements_dev_path) as req_file:
    requirements_dev = req_file.read().splitlines()

setup(
    name='cloudwatch_logs_environment',
    version=__version__,
    author='Nicholas Robinson-Wall',
    author_email='nick@robinson-wall.com',
    packages=find_packages(),
    url='https://github.com/nickrw/cloudwatch_logs_environment',
    description=(
        'CloudWatch logs configuration management '
        'via environment variables'),
    install_requires=requirements,
    tests_require=requirements_dev,
    package_data={'cloudwatch_logs_environment': ['requirements.txt',
                                                  'requirements-dev.txt']},
    entry_points={
        'console_scripts': [
            'cwlogs_env_runner=cloudwatch_logs_environment.runner:main'
        ],
    },
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Developers',
    ],
)
