help([[
loads HAFS application level modulefile on Orion
]])

ncl_ver=os.getenv("ncl") or "6.6.2"
load(pathJoin("ncl", ncl_ver))

prepend_path("MODULEPATH", "/work/noaa/epic/role-epic/spack-stack/hercules/spack-stack-1.5.0/envs/unified-env/install/modulefiles/Core")

stack_intel_ver=os.getenv("stack_intel_ver") or "2021.9.0" 
load(pathJoin("stack-intel", stack_intel_ver))

stack_impi_ver=os.getenv("stack_impi_ver") or "2021.9.0" 
load(pathJoin("stack-intel-oneapi-mpi", stack_impi_ver))

hdf5_ver=os.getenv("hdf5_ver") or "1.14.0"
load(pathJoin("hdf5", hdf5_ver)) 

netcdf_c_ver=os.getenv("netcdf_c_ver") or "4.9.2"
load(pathJoin("netcdf-c", netcdf_c_ver))

netcdf_fortran_ver=os.getenv("netcdf_fortran_ver") or "4.6.0"
load(pathJoin("netcdf-fortran", netcdf_fortran_ver))

wgrib2_ver=os.getenv("wgrib2_ver") or "3.1.1"
load(pathJoin("wgrib2", wgrib2_ver))

prepend_path("MODULEPATH", "/work/noaa/hwrf/noscrub/local/modulefiles")
load(pathJoin("python", "wcoss2_env"))

setenv("MPISERIAL", "/work/noaa/hwrf/noscrub/local/bin/mpiserial")

setenv("cartopyDataDir", "/work/noaa/hwrf/noscrub/local/share/cartopy")

whatis("Description: HAFS Graphics environment")
