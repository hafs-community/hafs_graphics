help([[
loads HAFS application level modulefile on Hera
]])

purge()

prepend_path("MODULEPATH", "/contrib/spack-stack/spack-stack-1.9.2/envs/wgrib2-oneapi-2024.2.1/install/modulefiles/Core")
prepend_path("MODULEPATH", "/contrib/spack-stack/spack-stack-1.9.2/envs/wgrib2-oneapi-2024.2.1/install/modulefiles/intel-oneapi-mpi/2021.13-sbi3u54/gcc/13.3.0")

stack_oneapi_ver=os.getenv("stack_oneapi_ver") or "2024.2.1"
load(pathJoin("stack-oneapi", stack_oneapi_ver))

load("graphics_common")

imagemagick_ver=os.getenv("imagemagick_ver") or "7.1.1-11"
load(pathJoin("imagemagick", imagemagick_ver))

prepend_path("PATH", "/scratch3/NCEPDEV/hwrf/noscrub/local/miniconda3/envs/WCOSS2_env/bin")

prepend_path("PYTHONPATH", "/scratch3/NCEPDEV/hwrf/noscrub/local/miniconda3/envs/WCOSS2_env")

setenv("MPISERIAL", "/scratch3/NCEPDEV/hwrf/noscrub/local/bin/mpiserial")

setenv("cartopyDataDir", "/scratch3/NCEPDEV/hwrf/noscrub/local/cartopy")

whatis("Description: HAFS Graphics environment")
