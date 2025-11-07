# OMAV Thimble Utils

Forked from the [eFlesh](https://github.com/notvenky/eFlesh) repo, this is a trimmed down version for the OMAV platform.
#####

## Getting Started

LATER @luceharris will make a docker on crazy that you can use for making the thimble

```
git clone --recurse-submodules git@github.com:ethz-asl/omav_thimble_utils.git
cd omav_thimble_utils
```

create python env e.g.
```
conda env create -f env.yml
conda activate thimble
```

or venv (recommended)
```
python -m venv /path/to/venv/thimble
source /path/to/thimble/bin/activate
pip install numpy scipy reskin-sensor matplotlib meshio tqdm libigl
```

## Prerequisits

- design the STL/OBJ file of your desired shape for the sensor. Other designs are on [FILL IN LATER]
- get [N52 neodymium magnets](https://www.supermagnete.ch/scheibenmagnete-neodym/scheibenmagnet-9mm-3mm_S-09-03-N52N?group=lp-n52) N52 Ø9 mm, height 3 mm. This size is the best for SNR and provide a strong magnetism. 
- 


## Mesh generation
### Tested on Ubuntu 20.04, 22.04 and 24.04
System pre-requisites
```
sudo apt-get update && sudo apt-get install -y build-essential cmake libgmp-dev libmpfr-dev libcgal-dev libeigen3-dev libsuitesparse-dev libboost-all-dev
```
### Note: Running the following command as it is, uses 12 CPU nodes. You can customize by running ```./build.sh cpu_nodes=n``` where you can choose 'n' based on your system.
```
cd microstructure/microstructure_inflators && chmod +x build.sh && ./build.sh
```

You're now all set to use ```cut-cell.ipynb```to make your own eFlesh sensors, ensure to provide the correct paths against all marked placeholders - like path to your OBJ/STL fle.

## Sensor Fabrication

<p align="center">
  <img src="https://github.com/user-attachments/assets/de48d4cc-23c9-44f1-8513-785790dfbc8a" width="400" alt="fabrication_only">
</p>

### 3D Print with TPU

We slice the generated STL file with pouches, using [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer) or [Bambu Studio](https://bambulab.com/en/download/studio) and 3D print it with [TPU 95A](https://www.amazon.com/Polymaker-Filament-Flexible-1-75mm-Cardboard/dp/B09KKRYHS6) on a Bambu Lab X1 Carbon 3D printer.

### Neodymium Magnets

We use [N52 neodymium magnets](https://www.mcmaster.com/products/magnets/magnets-2~/neodymium-magnets-7/) of dimensions: [1/8" thickness, 3/8" diameter](https://www.mcmaster.com/5862K104/) for the standard cuboidal instance and many of the medium-large form factor sensors. For the fingertips, we use N52 magnets of dimensions [1/16" thickness, 3/16" diameter](https://www.mcmaster.com/5862K139/). According to the user's requirements, the magnet pouches can be easily tweaked, and so magnets of [any dimensions](https://www.mcmaster.com/products/magnets/magnets-2~/neodymium-magnets-7/) can be used.

### Hall Sensors / Magnetometers

Please upload the arduino code located in ```arduino/5X_eflesh_stream/5X_eflesh_stream.ino``` to the qtPy. We use the rigid magnetometer PCBs used in Reskin and AnySkin. Details can be found in the [circuit section](https://github.com/raunaqbhirangi/reskin_sensor/tree/main/circuits) of [Reskin](https://reskin.dev/)'s repository.

## Sensor Characterization

Data recording [data_collection.md]




