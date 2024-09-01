help([[
loads HAFS application level modulefile on Jet
]])

prepend_path("MODULEPATH", "/contrib/spack-stack/spack-stack-1.6.0/envs/unified-env-rocky8/install/modulefiles/Core")

stack_intel_ver=os.getenv("stack_intel_ver") or "2021.5.0"
load(pathJoin("stack-intel", stack_intel_ver))

ncl_ver=os.getenv("ncl") or "6.6.2"
load(pathJoin("ncl", ncl_ver))

stack_impi_ver=os.getenv("stack_impi_ver") or "2021.5.1"
load(pathJoin("stack-intel-oneapi-mpi", stack_impi_ver))

hdf5_ver=os.getenv("hdf5_ver") or "1.14.0"
load(pathJoin("hdf5", hdf5_ver))

netcdf_c_ver=os.getenv("netcdf_c_ver") or "4.9.2"
load(pathJoin("netcdf-c", netcdf_c_ver))

netcdf_fortran_ver=os.getenv("netcdf_fortran_ver") or "4.6.1"
load(pathJoin("netcdf-fortran", netcdf_fortran_ver)) 

prod_util_ver=os.getenv("prod_util_ver") or "2.1.1"
--load(pathJoin("prod_util", prod_util_ver))

wgrib2_ver=os.getenv("wgrib2_ver") or "2.0.8"
load(pathJoin("wgrib2", wgrib2_ver))

imagemagick_ver=os.getenv("imagemagick_ver") or "7.1.1-11"
load(pathJoin("imagemagick", imagemagick_ver))

unload("py-numpy")
unload("py-pandas")
unload("py-scipy")
unload("py-netcdf4")
prepend_path("MODULEPATH", "/mnt/lfs5/HFIP/hwrfv3/local/modulefiles")
load(pathJoin("python", "wcoss2_env"))

setenv("MPISERIAL", "/mnt/lfs5/HFIP/hwrfv3/local/bin/mpiserial")

setenv("cartopyDataDir", "/mnt/lfs5/HFIP/hwrfv3/local/share/cartopy")

whatis("Description: HAFS Graphics environment")
