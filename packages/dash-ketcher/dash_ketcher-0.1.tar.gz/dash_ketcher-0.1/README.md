# Dash Ketcher

### About Ketcher
Ketcher is an open-source web-based chemical structure editor available on https://lifescience.opensource.epam.com/ketcher/

### About Dash Ketcher
Dash Ketcher is a Dash component library, allowing to use Ketcher in Dash.

Currently, interactions include:
* output the current drawn structure as a SMILES string, 
* draw the structure corresponding to a provided SMILES string.

Other functionalities will be implemented later.



## Get started
All the commands below are given for a regular python installation on Linux-based systems,
and can be adapted to other systems or conda-based installation.

1. Create a local environment

   This step is optional but highly recommended to avoid conflicts with the base environment.
    ```
    $ virtualenv venv
    $ . venv/bin/activate
    ```
    _Note: venv\Scripts\activate for windows_

2. Install dash_ketcher

   Dash Ketcher can be installed from PyPI or Github repository.

   * From PyPi
      ```
      $ pip install dash_ketcher
      ```

   * From GitHub
      ```
      $ pip install git+https://dash_ketcher
      ```

3. Download Ketcher

   Download Ketcher's standalone version >= 3.2 and add it to your Dash project, e.g. in assets/

4. Adapt & use the code

   * Using the provided exemple
   
     1. Adapt `usage.py` with your local settings, notably with the path to your local Ketcher standalone
     2. Run `python usage.py`
     3. Visit http://localhost:8050 in your web browser to test it

   * Using your own code or Dash app

      Import dash_ketcher and use it as shown in `usage.py`

  

## Contributing
Everyone is welcome to contribute and send pull requests. 
This package was initially generated using the [dash-component-boilerplate](https://github.com/plotly/dash-component-boilerplate)



## Copyright
2025-present Philippe Gantzer
