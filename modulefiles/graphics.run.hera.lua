help([[
loads HAFS application level modulefile on Hera
]])

ncl_ver=os.getenv("ncl") or "6.5.0"
load(pathJoin("ncl", ncl_ver))

prepend_path("MODULEPATH", "/scratch1/NCEPDEV/hwrf/noscrub/local/modulefiles")
load(pathJoin("python","wcoss2_env"))

prepend_path("MODULEPATH", "/scratch2/NCEPDEV/nwprod/hpc-stack/libs/hpc-stack/modulefiles/stack")

hpc_ver=os.getenv("hpc_ver") or "1.2.0"
load(pathJoin("hpc", hpc_ver))

hpc_intel_ver=os.getenv("hpc_intel_ver") or "2022.1.2"
load(pathJoin("hpc-intel", hpc_intel_ver))

hpc_impi_ver=os.getenv("hpc_impi_ver") or "2022.1.2"
load(pathJoin("hpc-impi", hpc_impi_ver))

hdf5_ver=os.getenv("hdf5_ver") or "1.10.6"
load(pathJoin("hdf5", hdf5_ver))

netcdf_ver=os.getenv("netcdf_ver") or "4.7.4"
load(pathJoin("netcdf", netcdf_ver))

wgrib2_ver=os.getenv("wgrib2_ver") or "2.0.8"
load(pathJoin("wgrib2", wgrib2_ver))

setenv("MPISERIAL", "/scratch1/NCEPDEV/hwrf/noscrub/local/bin/mpiserial")

setenv("cartopyDataDir", "/scratch1/NCEPDEV/hwrf/noscrub/local/share/cartopy")

whatis("Description: HAFS Graphics environment")
