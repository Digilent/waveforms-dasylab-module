# Development Machine Setup
1. Install DASYLab 202x
1. Clone this repo.
1. Simlink python dependencies into the appropriate DASYLab directories.
   - `<REPO_ROOT>/digilent_waveforms` to `<DASYLAB_DIR>\python\Lib\site-packages\digilent_waveforms`
   - `<REPO_ROOT>/digilent_waveforms_dasylab` to `<DASYLAB_DIR>\python\Lib\site-packages\digilent_waveforms_dasylab`
   - Example powershell commands:  
       - `cmd /c mklink /d "C:\Program Files (x86)\DASYLab 2022_en\python\Lib\site-packages\digilent_waveforms" "C:\git\digilent\sw-waveforms-dasylab-module\digilent_waveforms"`
       - `cmd /c mklink /d "C:\Program Files (x86)\DASYLab 2022_en\python\Lib\site-packages\digilent_waveforms_dasylab" "C:\git\digilent\sw-waveforms-dasylab-module\digilent_waveforms_dasylab"`

1. Place a script block on the DASYLab worksheet and select **Only outputs**

1. Click **Load**
1. Select <REPO_ROOT>/digilent_waveforms_dasylab_module.py file 
1. Click **OK**
1. Save the worksheet.

# Development process
1. Open the DASYLab worksheet `<REPO_ROOT>/Digilent WaveForms Module.DSB`
2. Make changes to `digilent_waveforms_dasylab_module.py`
3. Reload the python file to get the changes.
   1. On the DASYLab worksheet, double click the **Script Module** named **DWF**
   1. Click **Load**
   1. Select `<REPO_ROOT>/digilent_waveforms_dasylab_module.py` 
   1. Click **OK**
4. Run the worksheet.  
5. Repeat setps 3-4

# Release
1. Double click the script module on the DASYLab worksheet
1. Click **Export**

# Developer Notes
- DASYLab looks for python imports in `<DASYLAB_DIR>\python\Lib\site-packages\`.  In order to minimize name collisions it is best to place all python dependencies in a subdirectory and include the subdirectory when importing.
  - Ex. **_version.py** lives in `./digilent_waveforms_dasylab/` rather than at the project root and imported with `from digilent_waveforms_dasylab._version import __version__`
- Needs verification - DASYLab appears to cache python dependencies at start time.  Therefor if you make changes to a python module that is symlinked into `<DASYLAB_DIR>\python\Lib\site-packages\` the changes won't take effect until DASYLab is restarted.