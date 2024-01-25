# The IEC 61162 Python Package

# Description

The IEC 61162 Python Package implements parts of the IEC 61162 series of standards, 'Maritime Navigation and Radiocommunication Equipment and Systems - Digital Interfaces'. Currently, support is included for the following parts:

* Part 1: Single talker and multiple listeners; and
* Part 450: Multiple talkers and multiple listeners - Ethernet interconnection.

The package has been developed using Python v.3.11.1.

## Installation

1. Ensure [Python](https://www.python.org/downloads/) and the [PDM](https://pdm-project.org/) dependency manager are installed.

1. Clone the GRAD `py_iec_61162` repository.
    ```
    git clone https://github.com/jan-safar/py_iec_61162.git
    ```

1. Navigate to the local repository.
    ```
    cd py_iec_61162
    ```

1. Install the IEC 61162 package and its dependencies from the `pdm.lock` file.
    ```
    pdm sync --prod
    ```
    Upon successful execution of the above command, `pdm` will generate a virtual Python environment in `./.venv/` and install the package along with its required dependencies into it in *production mode*.

## Code Usage

The main modules of the Rec. ITU-R M.1371 package are located under `./src/iec_61162/`. The code is structured as outlined below.

For examples of usage, see the source code in this repository and the repositories linked under 'Related Projects'.

### Subpackage: `part_1`

#### Module: `sentences.py`

This module contains classes and function for representing, generating and, in the future, parsing presenation interface sentences compliant with the IEC 61162-1:2016 standard.

Currently, support has been implemented for the following sentence formatters:
* BBM, 'AIS binary broadcast message'; and
* VDM, 'AIS VHF data-link message'.

### Subpackage: `part_450`

#### Module: `messages.py`

This module contains classes and functions for representing, generating and, in the future,
parsing messages compliant with the IEC 61162-450:2018 standard.

Currently, support has been implemented for messages encapsulating IEC 61162-1-like sentences.

## Contributing

We welcome contributions! If you wish to contribute to this project, please follow these steps:

1. Fork the repository and create a new branch.
1. Clone your repository to your local machine.
    
    ```
    git clone <your_repository_address>
    cd py_iec_61162
    ```
1. Install the package in *development mode* using PDM.
    ```
    pdm sync --dev
    ```    
    
    Note: The development installation includes dependencies for the [Spyder IDE](https://www.spyder-ide.org/), which may not be necessary if you are using a different IDE.
1. Make your changes and test thoroughly.
1. Submit a pull request with a clear description of your changes.

## Tests

This is currently work in progress.

Unit test modules are expected to be located under `./tests/`. The chosen testing framework for this project is [pytest](https://pytest.org), included as part of the development installation.

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](./LICENSE) file for details.

## Support

Email: Jan.Safar@gla-rad.org

Issue Tracker: [GitHub Issues](https://github.com/jan-safar/py_iec_61162/issues)

## Related Projects

### Python

* [Rec. ITU-R M.1371 package](https://github.com/jan-safar/py_rec_itu_r_m_1371.git)
* [IEC 62320 package](https://github.com/jan-safar/py_iec_62320.git)
* [IEC PAS 63343 package](https://github.com/jan-safar/py_iec_pas_63343.git)
* [VDES1000 package](https://github.com/jan-safar/py_vdes1000.git)

### Java

* [VDES1000 Library](https://github.com/gla-rad/VDES1000Lib) - a Java port of the VDES1000 package.
