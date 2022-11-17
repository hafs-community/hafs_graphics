help([[
loads HAFS application level modulefile on Orion
]])

ncl_ver=os.getenv("ncl") or "6.6.2"
load(pathJoin("ncl", ncl_ver))

prepend_path("MODULEPATH", "/work/noaa/hwrf/noscrub/local/modulefiles")
load(pathJoin("python", "wcoss2_env"))

prepend_path("MODULEPATH", "/work/noaa/epic-ps/hpc-stack/libs/intel/2022.1.2/modulefiles/stack")

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
setenv("WGRIB2", "/apps/contrib/NCEP/libs/hpc-stack/intel-2018.4/impi-2018.4/wgrib2/2.0.8/bin/wgrib2")

setenv("MPISERIAL", "/work/noaa/hwrf/noscrub/local/bin/mpiserial")

setenv("cartopyDataDir", "/work/noaa/hwrf/noscrub/local/share/cartopy")

whatis("Description: HAFS Graphics environment")
