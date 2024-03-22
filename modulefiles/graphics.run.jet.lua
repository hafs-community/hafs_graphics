help([[
loads HAFS application level modulefile on Jet
]])

prepend_path("MODULEPATH", "/mnt/lfs4/HFIP/hfv3gfs/role.epic/spack-stack/spack-stack-1.5.0/envs/unified-env/install/modulefiles/Core")

stack_intel_ver=os.getenv("stack_intel_ver") or "2021.5.0"
load(pathJoin("stack-intel", stack_intel_ver))

ncl_ver=os.getenv("ncl") or "6.5.0"
load(pathJoin("ncl", ncl_ver))

stack_impi_ver=os.getenv("stack_impi_ver") or "2021.5.1"
load(pathJoin("stack-intel-oneapi-mpi", stack_impi_ver))

hdf5_ver=os.getenv("hdf5_ver") or "1.14.0"
load(pathJoin("hdf5", hdf5_ver))

netcdf_c_ver=os.getenv("netcdf_c_ver") or "4.9.2"
load(pathJoin("netcdf-c", netcdf_c_ver))

netcdf_fortran_ver=os.getenv("netcdf_fortran_ver") or "4.6.0"
load(pathJoin("netcdf-fortran", netcdf_fortran_ver)) 

wgrib2_ver=os.getenv("wgrib2_ver") or "2.0.8"
load(pathJoin("wgrib2", wgrib2_ver))
setenv("WGRIB2", "/mnt/lfs4/HFIP/hwrfv3/Jili.Dong/hafs_tools/grib2/wgrib2/wgrib2")

prepend_path("MODULEPATH", "/mnt/lfs4/HFIP/hwrfv3/local/modulefiles")
load(pathJoin("python", "wcoss2_env"))

setenv("MPISERIAL", "/mnt/lfs4/HFIP/hwrfv3/local/bin/mpiserial")

setenv("cartopyDataDir", "/mnt/lfs4/HFIP/hwrfv3/local/share/cartopy")

whatis("Description: HAFS Graphics environment")
