![qd_logo](https://qdusa.com/images/QD_logo.png)
# MultiPyVu

* [Introduction](#intro)
* [Requirements](#requirements)
* [Example Scripts](#examples)
* [Getting Started](#getting-started)
* [Using Using MultiPyVu.Server() and MultiPyVu.Client()](#using)
* [Starting the Server Using the GUI](#gui)
* [Commands](#commands)
    * [set_temperature() / get_temperature()](#temp)
    * [set_field() / get_field()](#field)
    * [set_chamber() / get_chamber()](#chamber)
    * [wait_for()](#waitfor)
    * [is_steady()](#is_steady)
    * [get_aux_temperature()](#aux_therm)
    * [resistivity option](#brt)
    * [horizontal rotator option](#rotator)
* [Saving & Opening a MultiVu Data File](#save)
* [Querying the Server Status](#server_status)
* [Testing the Server Using Scaffolding](#scaffolding)
* [Troubleshooting](#troubleshooting)
* [Changelog](#changelog)
* [Contact](#Contact)
***
---
### Introduction<a class="anchor" id="intro"></a>
MultiPyVu provides the ability to control the temperature, magnetic field, and chamber status of Quantum Design, Inc. products using python.  This module includes MultiPyVu.Server, which runs on the same computer as MultiVu, MultiPyVu.Client, which is used to send commands to the cryostat, and MultiPyVu.DataFile, which is used to save data to a *.dat* file and read a *.dat* file into a Pandas DataFrame.

MultiPyVu.Client can run (1) locally on the same PC which is running the MultiVu executable along with MultiVu.Server, or (2) remotely on another computer that has TCP access to the computer running MultiPyVu.Server.

The components of MultiPyVu enable access to the set and read the temperature, field, and chamber on the following QD platforms: PPMS, DynaCool, VersaLab, MPMS3, and OptiCool. MultiPyVu.Client can run on a PC, Mac, or Linux, including a RaspberryPi.

### Module Requirements<a class="anchor" id="requirements"></a>
MultiPyVu uses the following modules:
- python version 3.7 or higher
- pywin32 - version 300 or higher.
- pandas - data read back from a *.dat* file is a Pandas Dataframe
- pillow - supports server gui
- pyyaml - supports logging

For the Python 3 distribution Quantum Design recommends [Anaconda](https://www.anaconda.com/products/individual) as it includes most modules needed for this server and other packages useful for scientific computing.  To find which version of Python is used, from a command prompt type:
```
python --version
```
MultiPyVu can be installed using pip via the following command:
```
pip install --upgrade MultiPyVu
```
### Included Example Scripts<a class="anchor" id="examples"></a>
Several examples have been uploaded to [Quantum Design's Pharos database](https://www.qdusa.com/pharos/view.php?fDocumentId=4780).  These examples demonstrate various capabilities of the module, and serve as templates upon which users can add their own code to integrate external hardware operations with the environmental controls of the Quantum Design instrument.
| Filename | Description|
-----|-----
example_local.py | A simple script which starts the server, then the client, on the PC running MultiVu.  It relays instrument parameters and status to demonstrate communication, serving as a minimum working example useful for testing basic functionality.
example_command_demos.py | Utilizes most functions of the module, setting temperature/field/chamber operations, reading back the values and status of those parameters, and waiting for stability conditions to be met.  This also saves data to a MultiVu .dat file and plots the results. As-written, it runs in local mode.
example_experiment.py | Demonstrates an example experiment where a remote connection is used to measure the resistance of the 3 bridge channels while cycling temperature. The data is saved to a .dat file and then plotted with matplotlib.
Remote Connection\run_server.py | For remote operation; this script must be running on the on the control PC along with the MultiVu executable.
Remote Connection\example_remote_client.py | For remote operation; this script runs on a separate PC and relays instrument parameters and status to demonstration communication.
Remote Connection\example_MVDataFile_VISA.py | Simple example showing how to route environmental parameters and data from external instruments into a single MultiVu-readable *.dat* file.  As-written, it runs in local mode.
Data Processing\example_save_open_dat.py | Script showing how to save and read a MultiVu *.dat* file into a Pandas DataFrame, then plot with matplotlib.
Measuring\example_stabilize.py | Measures the temperature while stabilizing at each temperature.
Measuring\example_sweep.py | Measures the temperature while sweeping the temperature.
Measuring\example_get_setpoints.py | Shows how to get the temperature and magnetic field setpoints.
Options\example_aux_therm.py | Gets the temperature of the auxiliary thermometer from the OptiCool.
Options\example_resistivity_option.py | Demonstrates how to set up the BRT module bridges for resistivity measurements and how to save the data.
Options\example_horizontal_rotator.py | Demonstrates how to move the horizontal rotator to a new position.
UsefulBatchFiles\whats_my_ip_address.cmd | This batch file script prints out the IP address for the computer, providing an easy way to get the server IP address needed for remote operation. Alternatively, the gui can be used to get the IP address by calling ```python -m MultiPyVu```.
UsefulBatchFiles\show_process_with_port.cmd | Shows that active processes are running and what port is being used. By default, this looks for processes running on port 5000.  To query a different port number, append it to the command line arguments.  ```$ show_processes_with_port.cmd 4567```
UsefulBatchFiles\RunServer.cmd | This runs the server GUI.
UsefulBatchFiles\kill_process.cmd | This ends the processes with the specified PID (which can be identified using show_process_with_port.cmd). Run using ```$ kill_process.cmd 13579```

### Getting Started<a class="anchor" id="getting-started"></a>
 Once the MultiPyVu module has been installed, be sure that the MultiVu executable is running on the PC connected to the cryostat before starting the server. For testing purposes, you can use MultiVu in simulation mode on an office computer, or run mpv.Server with the -s flag which runs the python code in scaffolding that mimics MultiVu. This is especially helpful for developing a script on a computer that does not have MultiVu running (Mac, Linux, or any PC without MultiVu).  When running MultiVu and MultiPyVu, be sure that they are running under the same permissions.

**Local Operation:**
It is suggested to run first run the 'example_local.py' script with no changes on the MultiVu PC connected to the instrument- this should verify that the underlying resources required by the module are all present and functioning properly.  If this is successful, proceed to the 'example_command_demos.py' script for a brief demonstration of the commands used to set and monitor the sample space environmental parameters, as well as the wait command.

**Remote Operation:**
After confirming the local example scripts have executed correctly, remote operation can be attempted.  First, on the MultiVu PC, open the server by running Remote Connection\run_server.py
```cmd
$ python run_server.py
```
Ths server can also be started using the gui by calling:
```cmd
$ python -m MultiPyVu
```
or, to start the gui using scaffolding to simulate MultiVu running you can specify the flavor of MultiVu as below:
```cmd
$ python -m MultiPyVu -s opticool
```
When the gui opens, it will show the IP address of the host computer, which must be included in the client script if it is running remotely.  The IP address can also be obtained from the command line using:
```cmd
$ python -m MultiPyVu -get_ip
```

On the client PC, update the 'host' variable of the 'example_Remote-Client.py' script *with the same server PC IPV4 address* and run it.  The script will report the present temperature and field value/status a few times to show the connection is functioning.

**Next Steps:**
It may sometimes be desirable to combine the sample environment parameters (temperature, field) with readings from a user's own instrumentation into a single *.dat* file which can be plotted in MultiVu.  This functionality, accomplished using the MultiPyVu.DataFile module, is demonstrated using PyVISA to communicate with a VISA-compatible instrument in the  'Remote Connection/example_MvDataFile_VISA.py' example.  Note that for this routine to execute properly, the correct instrument bus/address and query string need to be updated in the script.

For further information on the detailed operation of the components of the module, see the following sections.

### Using MultiPyVu.Server() and MultiPyVu.Client()<a class="anchor" id="using"></a>
To start the server on localhost, open MultiVu, and type:
```cmd
$ python -m MultiPyVu
```
One can also use the example script _run_server.py_, go to a command prompt and type:
```cmd
$ python run_server.py
```

As mentioned above, if the client and the server are running on the same computer as MultiVu, then one can use example_local.py as a guide to set up the whole script in one file.

There are a list of flags to specify settings.  These can be found by typing -h, which brings up help information:
```cmd
$ python -m MultiPyVu -h
```

One can specify the Quantum Design platform, but if MultiVu is running, specifying the platform should not be necessary.  For example:
```cmd
$ python run_server.py opticool
```

If the Server and Client are going to be running on two different computers, the Server's IP address must be specified when instantiating the Client.

Both the Server and the Client are context managers, which means to write a script which connects to the server from a client machine, put all of the commands to control the cryostat inside a with-block:
```python
import MultiPyVu as mpv

with mpv.Client('127.0.0.1') as client:
    # put scripting commands here
# do post-processing once the client has been closed
```

If the host or port are not default values (localhost and 5000, respectively), then these parameters must be specified when instantiating MultiPyVu.Client().

Alternatively, one can start a connection to the server using:
```python
client = mpv.Client(host='127.0.0.1')
client.open()
# put scripting commands here
client.close_client()
# do post-processing once the client has been closed
```
Using the above method could end up with the server hung up because errors need to be correctly accounted for.  It is safer to use the Client as a context manager using a with-block.  In addition, a client object can only connect to the server once.  For a second connection, one must instantiate a new client instance.

The client can also close the server directly using:
```python
client.close_server()
```
instead of client.close_client().  Note that once this is called, the server will need to be reopened.  Also, this can not be accessed from within a with-block.

If the client and server are being run on the same computer, then a single script can control them both.
```python
import MultiPyVu as mpv

with mpv.Server() as server:
    with mpv.Client() as client:
        # put scripting commands here
# do post-processing now that the client and server have been closed
```

This is convenient as it does not require running two different scripts.

### Starting the Server Using the GUI<a class="anchor" id="gui"></a>
The Server can be run using a simple graphical user interface which helps to show information about its status.

Start the gui from the command line using the -m flag when calling the module:

```cmd
$ python -m MultiPyVu
```
or, to start the gui using scaffolding to simulate a flavor of MultiVu:
```cmd
$ python -m MultiPyVu -s opticool
```

This brings up a window with a button to start the server, quit, and a window to view the IP address.  Status information is also displayed in the gui.

### Commands<a class="anchor" id="commands"></a>
The commands to set and get the temperature, field, and chamber status are defined here:

**Temperature**<a class="anchor" id="temp"></a>
```python
client.set_temperature(set_point,
                       rate_K_per_min,
                       client.temperature.approach_mode.<enum_option>)
```
The <enum_options> mode is set using the client.temperature.approach_mode enum, which has items *fast_settle* and *no_overshoot.* The temperature and status are read back using:
```python
temperature, status = client.get_temperature()
```
One can also retrieve the setpoint, rate, and approach mode:
```python
temperature, rate, approach = client.get_temperature_setpoints()
```

**Field**<a class="anchor" id="field"></a>
```python
client.set_field(set_point,
                 rate_oe_per_sec,
                 client.field.approach_mode.<enum_option>)
```
The <enum_option> approach mode is set using the client.field.approach_mode enum, which has items *linear,* *no_overshoot,* and *oscillate.* The VersaLab does not support *no_overshoot*. In addition, the PPMS magnet can be run *driven* or *persistent*, so it has a fourth input
which is specified using the client.field.driven_mode enum.  For the PPMS flavor:
```python
client.set_field(set_point,
                 rate_oe_per_sec,
                 client.field.approach_mode.<enum_option>,
                 client.field.driven_mode.<enum_option>)
```
Specifying the driven_mode for other platforms will result in a MultiPyVuError.

The field and status are read back using:
```python
field, status = client.get_field()
```
One can also retrieve the setpoint, rate, and approach mode:
```python
field, rate, approach, driven = client.get_field_setpoints()
```

**Chamber**<a class="anchor" id="chamber"></a>
```python
client.set_chamber(client.chamber.mode.<enum_option>)
```
This is set using the <enum_option> client.chamber.mode enum, which has items *seal,* *purge_seal,* *vent_seal,* *pump_continuous,* *vent_continuous,* and *high_vacuum.*
And read back using:
```python
chamber = client.get_chamber()
```
Note that this command is not used by the OptiCool.

**Wait For**<a class="anchor" id="waitfor"></a>
When a setting on a cryostat is configured, it will take time to reach the new set point.  If desired, one can wait for the setting to become stable using the .wait_for(delay, timeout, bitmask) command.  A delay will set the time in seconds after the setting is stable, which can be useful to make sure a sample has time to thermalize; timeout is the seconds until the command will give up; bitmask tells the system which settings need to be stable.  This can be set using the waitfor handle, and multiple parameters are combined using bit-wise or.  In the example below, the wait_for command will wait at least 90 seconds for the temperature, field, and chamber to stabilize, and will then immediately go on to the next command.
```python
client.wait_for(0, 90, client.temperature.waitfor | client.field.waitfor | 
client.chamber.waitfor)
```

**Is Steady**<a class="anchor" id="is_steady"></a>
Similar to the .wait_for() command is a method to see if the cryostat has stabilized using .is_steady(bitmask). One useful example of this command is to set a temperature, then have a script collect data while .is_steady(bitmask) returns False.  The bitmask is defined the same way as for the .wait_for() command.
```python
client.set_temperature(1.8,
                       5.0,
                       client.temperature.approach_mode.fast_settle)
while not client.is_steady(client.temperature.waitfor):
    t, s = client.get_temperature()
```  

**OptiCool Auxillary Thermometer**<a class="anchor" id="aux_therm"></a>

To read the OptiCool auxillary thermometer, use the following command.  This will throw a MultiPyVuException for all other platforms.
```python
aux_temperature, status = client.get_aux_temperature()
```

**Resistivity Option**<a class="anchor" id="brt"></a>

MultiPyVu provides access to several commands used to collect electrical resistance data if you have a BRT CAN module installed.  The bridge channels must be configured for the resistivity option.  This can be done in MultiVu with the resistivty option, and then python can be used to simply collect data, or the bridges can be configured using python.  Note that bridge configuration using python will not show up in MultiVu. Implementation of the resistivity option is not implemented for the PPMS model 6000.

The command to configure each channel is client.resistivity.bridge_setup(bridge_number, channel_on, current_limit_uA, power_limit_uW, voltage_limit_mV).  An example for how to configure the bridge is:
```python
client.resistivity.bridge_setup(bridge_number=1,
                                channel_on=True,
                                current_limit_uA=8000.0,
                                power_limit_uW=500.0,
                                voltage_limit_mV=1000.0)
```
Note that when using this command, the module will take some time to properly configure itself, so we recommend adding a pause of about 5 seconds before collecting data.  

If desired, each bridge can be configured to source a constant current.  This is done using the ```client.resistivity.set_current(bridge_number, current_uA)``` command.  

Once configured, MultiPyVu gives access to the following commands:
```python
client.resistivity.get_resistance(bridge_number)
client.resistivity.get_current(bridge_number)
```

**Horizontal Rotator Option**<a class="anchor" id="rotator"></a>

For DynaCool, VersaLab, and PPMS customers with the horizontal rotator option, MultiPyVu can be used to adjust the rotator position.  The option must be configured before using MultiPyVu. Note that the rate_deg_per_sec is ignored for the PPMS.

Once configured, the following commands are simple to use:
```python
position = 374.5
rate_deg_per_sec = 100.0
client.set_position(position, rate_deg_per_sec)
pos, status = client.get_position()
```

### Saving & Opening a MultiVu Data File<a class="anchor" id="save"></a>
The MultiPyVu.Client class can be used in conjunction with 3rd party tools in order to expand the capabilities of measurements from a Quantum Design cryostat. One can set up a VISA connection to a voltmeter, for example, and then collect information while controlling the cryostat temperature, field, and chamber status.  This data can be collected into a MultiVu data file using MultiPyVu.DataFile.  One can also use this to read a data file into a Pandas DataFrame.

To begin using this in a script to save data, assign the column headers and create the file:
```python
import MultiPyVu as mpv

# configure the MultiVu columns
data = mpv.DataFile()
data.add_multiple_columns(['Temperature', 'Field', 'Chamber Status'])
data.create_file_and_write_header('myMultiVuFile.dat', 'Special Data')
```
Data is loaded into the file using .set_value(column_name, value), and then a line of data is written to the file using .write_data() For example:
```python
temperature, status = client.get_temperature()
data.set_value('Temperature', temperature)
data.write_data()
```

In order to import a data file into a Pandas Dataframe, one would use the following example:
```python
import pandas as pd
import MultiPyVu as mpv

data = mpv.DataFile()

myDataFrame = data.parse_MVu_data_file('myMultiVuFile.dat')
```
Putting all of this together, an example script might look like:
```python
import matplotlib.pyplot as plt
import MultiPyVu as mpv

# configure the data file
data = mpv.DataFile()
data.add_column('myY2Column', data.startup_axis.Y2)
data.add_multiple_columns(['T', 'status'])
data.create_file_and_write_header('my_graphing_file.dat', 'Using Python')

# collect some data
with mpv.Server() as server:
    with mpv.Client() as client:
        mode = client.temperature.approach_mode.fast_settle
        client.set_temperature(273.15,
                               7.0,
                               mode)

        mask = client.temperature.waitfor
        while not client.is_steady(mask):
            temperature, status = client.get_temperature()
            data.set_value('T', temperature)
            data.set_value('status', status)
            data.write_data()

# read data from the file and plot it
my_dataframe = data.parse_MVu_data_file('my_graphing_file.dat')
fig, ax = plt.subplots(1, 1)
fig.suptitle('Fun plot')
ax.scatter(x='Time Stamp (sec)',
           y='T',
           data=my_dataframe,
           )
plt.show()
```

### Querying the Server Status<a class="anchor" id="server_status"></a>
The server status can be queried from the command line.  First, we can see if the server is running using:
```cmd
$ python -m MultiPyVu -running
```
By default, this queries the server at IP address = localhost and port = 5000.  To query a different address, use the *-ip=* or *-p=* flags.

Similarly, in order to get the server status at a specific ip address, use:
```cmd
$ python -m MultiPyVu -status -ip=127.0.0.1
```

From the command line, one can get the computer's IP address:
```cmd
$ python -m MultiPyVu -get_ip
```

Finally, the server can be closed from the command line using:
```cmd
$ python -m MultiPyVu -quit
```
where again, the IP address and port can be defined using the *-ip=* and *-p=* flags.

### Testing the Server Using Scaffolding<a class="anchor" id="scaffolding"></a>
For testing the a script, QD has supplied scaffolding for the MultiVu commands to simulate their interactions with the server. This can be helpful for writing scripts on a computer which is not running MultiVu. To use this, start the server in scaffolding mode by using the -s flag.  The scaffolding does not need MultiVu running, so it is also necessary to specify the platform.  For example, to use scaffolding to test a script on a local computer which will be used with Dynacool:
```cmd
$ python -m MultiPyVu -s dynacool
```
or, using only a command line interface:
```cmd
$ python run_mv_server.py -s Dynacool
```
One could also run in scaffolding mode with one script using the following:
```python
import MultiPyVu as mpv

with mpv.Server(flags=['-s', 'DYNACOOL']) as server:
    with mpv.Client() as client:
        # put scripting commands here
# do post-processing now that the client and server have been closed
```

### Troubleshooting<a class="anchor" id="troubleshooting"></a>
Typical connection issues are due to:
- Firewall. You might need to allow connections on port 5000 (the default port number) in your firewall. Windows Firewall may cause issues depending upon your network settings. If the server is open and a connection fails disabling Firewalls temporarily may be your best option to troubleshoot. If your computers are on the same domain disabling the Domain Firewall may be sufficient.
- Port conflict. If port 5000 is in use, a different number can be specified when instantiating MultiPyVu.Server() and MultiPyVu.Client().
```python
server = mpv.Server(port=6000)
client = mpv.Client(port=6000)
```
- Ensure that MultiVu and Python are installed and run at the same permissions level. If Python was installed as administrator it may have issues if MultiVu is not run as administrator.
- A log file named QdMultiVu.log shows the traffic between the server and client which can also be useful during troubleshooting.

## Changelog<a class="anchor" id="changelog"></a>
**3.6.1**
- August 2025
- Add commands to get the temperature and field setpoints.
- Remove dependencies on the distutils module.
- Minimum python version 3.7

**3.5.4**
- June 2025
- Add the horizontal rotator option for DynaCool, VersaLab, and PPMS.

**3.4.0**
- May 2025
- Minimum python version now 3.9.
- Implemented socket handshaking to improve the reliability of the socket
communications.

**3.3.0**
- April 2025
- Bugfix which didn't allow this to be run on Mac or Linux platforms.
- Refactored mpv.DataFile() so that if a script is saving data to a file,
it can later load the file into a Pandas Dataframe without specifying the
filename.  This means the file path is now optional in 
.parse_MVu_data_file().

**3.2.0**
- November 2024
- Improvements in determining the running version of MultiVu.

**3.1.2**
- October 2024
- Fixed a bug which truncated numbers

**3.1.1**
- October 2024
- Updated the installer to include missing files.

**3.1.0**
- October 2024
- Log the version number when the Client connects to the Server.
- Check that the Server and Client are running the same version.
- Increase the number of backup logs to 5.
- Bugfix to allow Client to run on Linux or Mac systems.
- Limit server to hosting only one client at a time.
- Add the ability to call -quit, -is_running, -status, -get_ip from the command line using python -m MultiPyVu
- Miscellaneous bug fixes and refactoring.

**2.2.0**
- January 2024
- Corrected a bug that prevented the Server from recognizing PPMS and MPMS3 MultiVu flavors

**2.1.4**
- October 2023
- Import full module as MultiPyVu. Instead of loading the three sub-modules as:
```python
from MultiPyVu import MultiVuServer as mvs
from MultiPyVu import MultiVuClient as mvc
from MultiVuDataFile import MultiVuDataFile as mvd
  use: 
import MultiPyVu as mpv
```
- Working with *.dat* files uses MultiPyVu.DataFile() instead of MultiVuDataFile.MultiVuDataFile()
- MultiPyVu.DataFile() enums have been updated:
    - data.TScaleType -> data.scale
    - data.TStartupAxisType -> data.startup_axis
    - data.TTimeUnits -> data.time_units
    - data.TTimeMode -> data.time_mode
- Correct a bug so that a keyboard interrupt will actually close the Server.
- Provide another way to set the bitmap when calling the wait_for() method.  Can now call Client.temperature.waitfor, Client.field.waitfor, and Client.chamber.waitfor
- Add MultiPyVu.Client() commands:
    - get_aux_temperature() to read the OptiCool auxiliary thermometer.
    - add support for the resistivity option
- Only support pywin32com version 300 or higher.
- Add support for a gui to control MultiPyVu.Server()

**1.2.0**
- January 2022:  Initial release

## Contact<a class="anchor" id="Contact"></a>
Please reach out to apps@qdusa.com with questions or concerns concerning MultiPyVu.

![qd_logo](https://qdusa.com/images/QD_logo.png)
