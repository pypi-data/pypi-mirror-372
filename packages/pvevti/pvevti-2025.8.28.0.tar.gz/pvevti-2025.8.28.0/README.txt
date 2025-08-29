 == STRUCTURE ==

 Directory Tree					     File/Directory explanation

FPT Source Code/
├─ build/                                     		The build directory contains a subdir for each .spec file that is run.
│  ├─ guitest/
│  ├─ guitest_dev/
├─ cache/											The cache directory is used for temporary file storage during a build.
├─ dist/											The dist directory is used to place the executable file.
│  ├─ File Processing Tool Development Fork.exe
├─ fptenv/											The fptenv directory is a packaged virtual environment with all the necessary packages.
├─ icons/											The icons directory stores all the UI's icons and is fully bundled with the executable.
│  ├─ all icons for the UI
│  ├─ logo.png
├─ guitest.py										The guitest.py file is the actual python script that creates the GUI and performs actions.
├─ guitest.spec										Each spec file contains instructions for pyinstaller to follow while building.
├─ guitest_dev.spec
├─ icon.ico											The non-development icon file
├─ icon_dev.ico										The development icon file
├─ README.txt										This!


 == DEVELOPMENT == 

To start to work on the project, first change your working directory to the location of guitest.py. Never work on a network-drive directory, always work on a local directory (copy all files).

 > cd C:\Users\USERNAME\PATH_TO_DIR\

To build a new version of the executable, run pyinstaller with the guitest_dev spec file:

 > pyinstaller guitest_dev.spec

Once it is done building, the new executable will be available. If pyinstaller errors out after (~) 20 attempts to complete an action and cites a permission issue (or something along those lines), just try again. Oftentimes system resources are reserved by open applications and that can cause a failure to build.

You don't strictly need to delete the executables in the dist/ directory before building, but doing so allows you to perform a 'clean' build and might fix issues if you're having any.

There's also a non development spec file which operates identically but doesn't open the console when it is run. This spec file can be built into an executable by running pyinstaller like so:

 > pyinstaller guitest.spec

Each of the included .spec files may be altered to allow bundling more images, icons, or other media directly with the application. Changes in one .spec file will not be reflected in the other--be sure to alter both accordingly.