help([[
loads HAFS application level modulefile on Hercules
]])

prepend_path("MODULEPATH", "/apps/contrib/spack-stack/spack-stack-1.9.2/envs/ue-oneapi-2024.1.0/install/modulefiles/Core")
prepend_path("MODULEPATH", "/apps/contrib/spack-stack/spack-stack-1.9.2/envs/ue-oneapi-2024.1.0/install/modulefiles/intel-oneapi-mpi/2021.13-sqiixt7/gcc/13.3.0")

stack_oneapi_ver=os.getenv("stack_oneapi_ver") or "2024.2.1"
load(pathJoin("stack-oneapi", stack_oneapi_ver))

stack_impi_ver=os.getenv("stack_impi_ver") or "2021.13"
load(pathJoin("stack-intel-oneapi-mpi", stack_impi_ver))

load("graphics_common")

imagemagick_ver=os.getenv("imagemagick_ver") or "7.1.1-29"
load(pathJoin("imagemagick", magemagick_ver))

unload("py-numpy")
unload("py-pandas")
unload("py-scipy")
unload("py-netcdf4")

prepend_path("MODULEPATH", "/work/noaa/hwrf/noscrub/local/modulefiles")
load(pathJoin("python", "wcoss2_env"))

setenv("MPISERIAL", "/work/noaa/hwrf/noscrub/local/bin/mpiserial")

setenv("cartopyDataDir", "/work/noaa/hwrf/noscrub/local/share/cartopy")

whatis("Description: HAFS Graphics environment")
