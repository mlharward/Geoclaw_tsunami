"""This file was created by McKay Harward and Adam Robertson to merge a high
resolution topography file with a low resolution bathymetry file.
Specifically around the coast of the banda islands in Indonesia.
This file depends on CLAWPACK and its dependencies.

It can be generalized to cut any two low res and high res bathymetry/topography
files, interpolate over the low res file, and finish with a new file at desired
resolution cut to new coordinates
"""
import matplotlib.pyplot as plt
import clawpack.geoclaw.topotools as topo
import numpy as np
from scipy.interpolate import griddata
# for documentation on topotools please visit http://www.clawpack.org/topotools_module.html

def slice_region(topo_outfile="Tohoku/65_05_2_topo.tt3", bathy_outfile="Tohoku/65_05_2_bathy.tt3", \
    bathy_filename='./Tohoku/tohoku_topo_whitehead.tt3', topo_filename='./Tohoku/srtm_65_05.asc', shore_plots=False, \
    filter=[140,141.15,35,38.1]):
    """
    Takes in two different topography/bathymetry files, returns cutouts of those
    files at desired coordinates

    Parameters:
        topo_outfile(string): filename for writing out samller topography object
        bathy_outfile(string) : filename for writing out smaller bathymetry object
        bathy_filename(string) : filename to read in bathymetry(or lower resolution file)
        topo_filename(string) : filename to read in topography(or higher resolution file)
        shore_plots(bool) : If True, displays shore plots of the two cutout pieces
        filter(list) : Coordinates to create cutout of larger files in form [xlower,xupper,ylower,yupper]

    Note: In some distributions of Topotools the plot function has not been
    updated to new matplotlib standards and will not work. In this case you may
    either plot shores or change source code in topotools.py to the correct parameter
    """
    # Create instance of Topography class for topo file and bathymetry file
    topo_file = topo.Topography()
    bathy_file = topo.Topography()

    # read in topography and bathymetry files

    topo_file.read(topo_filename, topo_type=3)    # high res topography with -9999 values on sea
    bathy_file.read(bathy_filename, topo_type=3)  # low res bathymetry and topography
    # specify topo_type(format) for your files
    # topotools has a built in function to tell you topo_type of any file if needed

    # Crop both files to the same coordinates, [xlower,xupper,ylower,yupper]
    bathy_small = bathy_file.crop(filter_region=filter)
    topo_small = topo_file.crop(filter_region=bathy_small.extent)

    # At this point I recommend creating a shoreline and plotting to verify filter region cut
    if shore_plots == True:
        # Create shorelines in 2xn matrix
        shore_topo_small = topo_small.make_shoreline_xy()
        shore_bathy_small = bathy_small.make_shoreline_xy()
        # Plot both shorelines next to each other
        plt.subplot(221)
        plt.plot(shore_topo_small[:,0],shore_topo_small[:,1])
        plt.subplot(222)
        plt.plot(shore_bathy_small[:,0],shore_bathy_small[:,1])
        plt.show()

    # Write out both files for use in interpolation written by Adam Robertson
    bathy_small.write(bathy_outfile, topo_type=3) # low res
    topo_small.write(topo_outfile, topo_type=3)   # high res


def test_plot(filename='./Tohoku/65_05_1_bathy.tt3', shores=False):
    """
    Multipurpose function to plot any topography/bathymetry file with a normal plot
    or shoreline plot

    Parameters:
        filename(string) : name of file you want to plot
        shores(bool) : whether it should plot shores(True) or full map(False)

    Note: In some distributions of Topotools the plot function has not been
    updated to new matplotlib standards and will not work. In this case you may
    either plot shores or change source code in topotools.py to the correct parameter
    """
    # Read in topography/bathymetry
    test = topo.Topography()
    test.read(filename)
    # If shores is False, normal plot
    if shores == False:
        test.plot()
    # If shores is true, plot shoreline graph
    else:
        shore_test = test.make_shoreline_xy()
        plt.plot(shore_test[:,0], shore_test[:,1])
    plt.show()


def overlay(topo_filename='Tohoku/65_05_1_topo.tt3', bathy_filename='Tohoku/65_05_1_wiped.tt3', \
outfile='65_05_1_merged.tt3', nan_value="-9.9990000e+03"):
    """
    Function to merge interpolated lower resolution bathymetry(or any) and high
    res topography, writes out file.

    Parameters:
        topo_filename(string) : filename to read in topography(or higher resolution file)
        bathy_filename(string) : interpolated filename to read in bathymetry(or lower resolution file)
        outfile(string) : filename for writing out smaller bathymetry object
        nan_value(string) : Nan used in topography file to overwrite

    """
    #Read in both files
    with open(bathy_filename, 'r') as infile:
        data_bathy = [[n for n in line.split()] for line in infile.readlines()]
    print(np.array(data_bathy).shape)
    with open(topo_filename, 'r') as infile:
        data_topo = [[n for n in line.split()] for line in infile.readlines()]
    print(np.array(data_topo).shape)
    #Replace nan's in topo file with values form bathymetry file
    for i in range(len(data_topo)):
        for j in range(len(data_topo[i])):
            if data_topo[i][j] == nan_value: #Put your topography nan value here
                data_topo[i][j] = data_bathy[i][j+20]

    #write out merged file
    with open(outfile, 'x') as f:
        for i in range(len(data_topo)):
            for j in range(len(data_topo[i])):
                print(data_topo[i][j], end=' ', file=f)
            print("", file=f)

def wipeout_topo(filename='Tohoku/65_05_1_bathy_interpolated.tt3',outfile="Tohoku/65_05_1_wiped.tt3", val="-2"):
    """
    Function to take interpolated bathymetry file and set all values above sea
    level to predefined number that defaults to -2

    Parameters:
        filename(string) : Name of file to level anyhting above sea level
        outfile(string) : Filename to write out finished product
        val(string) : value to set topography equal to. String under ascii formatting
    """
    with open(filename, 'r') as infile:
        data = [[n for n in line.split()] for line in infile.readlines()]
    for i in range(len(data[7:])):
        for j in range(len(data[i+7])):
            if float(data[i+7][j]) >= 0:
                data[i+7][j] = val
    with open(outfile, 'x') as f:
        for i in range(len(data)):
            for j in range(len(data[i])):
                print(data[i][j], end=' ', file=f)
            print("", file=f)

def interpolate(in_filename, res_in, out_filename, res_out):
    """Interpolates between the values in input file to produce a new file to
    the specified interpolation.

    Ex: interpolate("etopo.tt3", 60, "banda.tt3", 3)

    Parameters:
        in_file (string): the name of the file to interpolate
        res_in (int): the resolution of the input file (in arc_seconds). Must be larger than res_out
        out_file (string): the name of the new file with higher resolution
        res_out (int): the desired resolution of the output file (in arc_seconds)

    Raises:
        ValueError: incorrect resolution input
    """
    # Check input
    if type(res_in) != int or type(res_out) != int:
        print("USAGE: input_filename, resolution_in, output_filename, resolution_out")
        raise ValueError("Resolutions must be integers.")
    if res_in < 1 or res_out < 1:
        print("USAGE: input_filename, resolution_in, output_filename, resolution_out")
        raise ValueError("Invalid resolution.")
    if res_in < res_out:
        print("USAGE: input_filename, resolution_in, output_filename, resolution_out")
        raise ValueError("Resolutions measured in arcseconds. resolution_in must be a larger integer than resolution_out.")

    # Read in data from file, store in array
    with open(in_filename, 'r') as infile:
        data = infile.readlines()
    # Separate header and data of file
    header = data[:6]
    data = data[6:]
    # Convert data into numpy array
    data = [[int(float(n)) for n in line.split()] for line in data]
    data = np.array(data)
    # Stack data into matrix
    values = np.hstack(data)
    # Compute scale to multiply length and width of original array by to generate size of higher resolution array
    scale = res_in // res_out
    # Store size of original data array
    x = len(data)
    y = len(data[0])
    # Create an array of arrays to represent points in grid (used in griddata)
    # Create matrix of the form: [ [0,0], [0,1], [0,2], ..., [0,y],
    #                              [1,0], [1,1], [1,2], ..., [1,y],
    #                              ...
    #                              [x,0], [x,1], [x,2], ..., [x,y] ]
    points = np.array([[0,0]])
    for i in np.linspace(0, len(data), len(data)):
        for j in np.linspace(0,len(data[0]), len(data[0])):
            points = np.append(points, [[i, j]], axis=0)
    # Remove duplicate [0,0] vector
    points = points[1:]
    # Mesh grid
    grid_x, grid_y = np.mgrid[0:len(data):complex(x*scale), 0:len(data[0]):complex(y*scale)]
    # Use scipy.interpolate.griddata to interpolate data over points
    grid = griddata(points, values, (grid_x, grid_y), method="linear")
    # Create header string to include in output file
    # In the current version, the header in the output file is exactly the same as the header in the input file.
    hstring = str()
    for i in header:
        hstring += i
    hstring = hstring[:-1]
    # Write data and header to output file
    np.savetxt(out_filename, grid, delimiter='   ', header=hstring, comments="")


"""
[xlower,xupper,ylower,yupper]
coordinates to evaluate for Indonesia
10001[-4.517863, 129.7745653] srtm_62_13
    [129.5745653, 129.9745653, -4.717863, -4.317863]
    On banda file
    redone
10002[-3.76, 128.18] srtm_62_13
    [128, 128.4, -4, -3.5]
    Finished
    in process
10003[-4.5,129.85] srtm_62_13 banda
    [129.6,130,-4.6,-4.45]
    Done previously
    redone
10004[-3.376916, 127.115413] srtm_62_13
    [126.9, 127.3, -3.6, -3.2]
    ERROR-out of etopo range
    redone
10005[-3.6,128.68] srtm_62_13
    [128.5, 128.9, -3.8, -3.4]
    Finished
    In process
10006[-3.342209, 128.89] srtm_62_13
    [128.5, 129.1, -3.6, -3]
    Finished
    In process
"""

"""
Banda cut to try and add values from map
[129.85,129.98,-4.589,-4.48]
"""

"""
Slices for Tohoku
65_04
[141.7,145,41.8,43.1]
[140.2,141.7,40,42.7]
65_05
[140.9,142.185,38.1,40]
[140,141.15,35,38.1]

"""
