help([[
loads HAFS application level modulefile on Ursa
]])

prepend_path("MODULEPATH", "/contrib/spack-stack/spack-stack-1.9.2/envs/ue-oneapi-2024.2.1/install/modulefiles/Core")
prepend_path("MODULEPATH", "/contrib/spack-stack/spack-stack-1.9.2/envs/ue-oneapi-2024.2.1/install/modulefiles/intel-oneapi-mpi/2021.13-haww6b3/gcc/12.4.0")

stack_oneapi_ver=os.getenv("stack_oneapi_ver") or "2024.2.1"
load(pathJoin("stack-oneapi", stack_oneapi_ver))

stack_impi_ver=os.getenv("stack_impi_ver") or "2021.13"
load(pathJoin("stack-intel-oneapi-mpi", stack_impi_ver))

load("graphics_common")

imagemagick_ver=os.getenv("imagemagick_ver") or "7.1.1-29"
load(pathJoin("imagemagick", imagemagick_ver))

prepend_path("PATH", "/scratch3/NCEPDEV/hwrf/noscrub/local/miniconda3/envs/WCOSS2_env/bin")

prepend_path("PYTHONPATH", "/scratch3/NCEPDEV/hwrf/noscrub/local/miniconda3/envs/WCOSS2_env")

setenv("MPISERIAL", "/scratch3/NCEPDEV/hwrf/noscrub/local/bin/mpiserial")

setenv("cartopyDataDir", "/scratch3/NCEPDEV/hwrf/noscrub/local/cartopy")

whatis("Description: HAFS Graphics environment")
