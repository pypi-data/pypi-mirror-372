from setuptools import setup
from distutils.util import convert_path

main_ns = {}
ver_path = convert_path('wizata_dsapi/version.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

core_dependencies = [
    'pandas==1.5.3',
    'numpy==1.26.4',
    'dill==0.3.6',
    'protobuf==3.20.3',
    'msal>=1.24.0',
    'joblib==1.2.0',
    'requests==2.28.2',
    'setuptools==67.6.0',
    'plotly==5.13.1'
]

ml_dependencies = [
    'matplotlib==3.7.1',
    "tensorflow==2.15.0; sys_platform != 'darwin' or platform_machine != 'arm64'",
    "tensorflow-macos==2.15.0; sys_platform == 'darwin' and platform_machine == 'arm64'",
    "keras==2.15.0; sys_platform != 'darwin' or platform_machine != 'arm64'",
    "keras==2.15.0; sys_platform == 'darwin' and platform_machine == 'arm64'",
    'tensorflow_probability==0.15.0',
    'scikit-learn==1.2.2',
    'adtk==0.6.2',
    'scipy==1.10.1',
    'xgboost==1.7.4',
    'u8darts==0.25.0',
    'optuna==3.3.0',
    'explainerdashboard==0.4.2.1',
    'ipywidgets==8.0.4',
    'kaleido==0.2.1',
    'pytest==7.2.2',
    'pytest-cov==4.0.0',
    'shapely==2.0.1',
    'pyodbc==4.0.35'
]
all_dependencies = core_dependencies + ml_dependencies

setup(
    name='wizata_dsapi',
    version=main_ns['__version__'],
    description='Wizata Data Science Toolkit',
    author='Wizata S.A.',
    author_email='info@wizata.com',
    packages=['wizata_dsapi',
              'wizata_dsapi.plots',
              'wizata_dsapi.scripts',
              'wizata_dsapi.models'],
    install_requires=core_dependencies,
    extras_require={
        'all': all_dependencies
    },
)
