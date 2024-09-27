help([[
loads HAFS application level modulefile on Gaea C6
]])

ncl_ver=os.getenv("ncl") or "6.6.2"
--load(pathJoin("ncl", ncl_ver))

prepend_path("MODULEPATH", "/autofs/ncrc-svm1_proj/epic/spack-stack/spack-stack-1.6.0/envs/unified-env-c6/install/modulefiles/Core")

PrgEnv_intel_ver=os.getenv("PrgEnv_intel_ver") or "8.5.0"
load(pathJoin("PrgEnv-intel", PrgEnv_intel_ver))

stack_intel_ver=os.getenv("stack_intel_ver") or "2023.2.0" 
load(pathJoin("stack-intel", stack_intel_ver))

stack_mpich_ver=os.getenv("stack_mpich_ver") or "8.1.29"
load(pathJoin("stack-cray-mpich", stack_mpich_ver))

craype_ver=os.getenv("craype_ver") or "2.7.30"
load(pathJoin("craype", craype_ver))

hdf5_ver=os.getenv("hdf5_ver") or "1.14.0"
load(pathJoin("hdf5", hdf5_ver)) 

netcdf_c_ver=os.getenv("netcdf_c_ver") or "4.9.2"
load(pathJoin("netcdf-c", netcdf_c_ver))

netcdf_fortran_ver=os.getenv("netcdf_fortran_ver") or "4.6.1"
load(pathJoin("netcdf-fortran", netcdf_fortran_ver))

prod_util_ver=os.getenv("prod_util_ver") or "2.1.1"
load(pathJoin("prod_util", prod_util_ver))

wgrib2_ver=os.getenv("wgrib2_ver") or "2.0.8"
load(pathJoin("wgrib2", wgrib2_ver))

pyyaml_ver=os.getenv("pyyaml_ver") or "6.0"
load(pathJoin("py-pyyaml", pyyaml_ver))

jasper_ver=os.getenv("jasper_ver") or "2.0.32"
load(pathJoin("jasper", jasper_ver))

libpng_ver=os.getenv("libpng_ver") or "1.6.37"
load(pathJoin("libpng", libpng_ver))

libjpeg_ver=os.getenv("libjpeg_ver") or "2.1.0"
load(pathJoin("libjpeg", libjpeg_ver))

prepend_path("MODULEPATH", "/autofs/ncrc-svm1_proj/hurr1/hafs/shared/modulefiles")

imagemagick_ver=os.getenv("imagemagick_ver") or "7.1.1-38"
load(pathJoin("ImageMagick", imagemagick_ver))

prepend_path("PATH", "/ncrc/proj/hurr1/hafs/shared/miniconda3/envs/WCOSS2_env/bin")

prepend_path("PYTHONPATH", "/ncrc/proj/hurr1/hafs/shared/miniconda3/envs/WCOSS2_env")

setenv("MPISERIAL", "/gpfs/f6/drsa-hurr1/world-shared/noscrub/local/bin/mpiserial")

setenv("cartopyDataDir", "/gpfs/f6/drsa-hurr1/world-shared/noscrub/local/share/cartopy")

whatis("Description: HAFS Graphics environment")
