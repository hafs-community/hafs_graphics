help([[
loads HAFS application level modulefile on Ursa
]])

ncl_ver=os.getenv("ncl") or "6.6.2"
--load(pathJoin("ncl", ncl_ver))

prepend_path("MODULEPATH", "/contrib/spack-stack/spack-stack-1.9.1/envs/ue-oneapi-2024.2.1/install/modulefiles/Core")

stack_oneapi_ver=os.getenv("stack_oneapi_ver") or "2024.2.1"
load(pathJoin("stack-oneapi", stack_oneapi_ver))

stack_impi_ver=os.getenv("stack_impi_ver") or "2021.13"
load(pathJoin("stack-intel-oneapi-mpi", stack_impi_ver))


hdf5_ver=os.getenv("hdf5_ver") or "1.14.3"
load(pathJoin("hdf5", hdf5_ver))

netcdf_c_ver=os.getenv("netcdf_c_ver") or "4.9.2"
load(pathJoin("netcdf-c", netcdf_c_ver)) 

netcdf_fortran_ver=os.getenv("netcdf_fortran_ver") or "4.6.1"
load(pathJoin("netcdf-fortran", netcdf_fortran_ver)) 

prod_util_ver=os.getenv("prod_util_ver") or "2.1.1"
load(pathJoin("prod_util", prod_util_ver))

wgrib2_ver=os.getenv("wgrib2_ver") or "3.6.0"
load(pathJoin("wgrib2", wgrib2_ver))

yafyaml_ver=os.getenv("yafyaml_ver") or "0.2.5"
load(pathJoin("libyaml", yafyaml_ver))

jasper_ver=os.getenv("jasper_ver") or "2.0.32"
load(pathJoin("jasper", jasper_ver))

libpng_ver=os.getenv("libpng_ver") or "1.6.37"
load(pathJoin("libpng", libpng_ver))

libjpeg_ver=os.getenv("libjpeg_ver") or "2.1.0"
load(pathJoin("libjpeg", libjpeg_ver))

imagemagick_ver=os.getenv("imagemagick_ver") or "7.1.1-29"
load(pathJoin("imagemagick", imagemagick_ver))

prepend_path("PATH", "/tds_scratch2/SYSADMIN/pilot-users/Biju.Thomas/noscrub/shared/miniconda3/envs/WCOSS2_env/bin")

prepend_path("PYTHONPATH", "/tds_scratch2/SYSADMIN/pilot-users/Biju.Thomas/noscrub/shared/miniconda3/envs/WCOSS2_env")

setenv("MPISERIAL", "/tds_scratch2/SYSADMIN/pilot-users/Biju.Thomas/noscrub/local/bin/mpiserial")

setenv("cartopyDataDir", "/tds_scratch2/SYSADMIN/pilot-users/Biju.Thomas/noscrub/shared/cartopy")

whatis("Description: HAFS Graphics environment")
