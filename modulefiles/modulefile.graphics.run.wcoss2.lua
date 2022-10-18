help([[
loads HAFS application level modulefile on Cactus and Dogwood
]])

envvar_ver=os.getenv("envvar_ver") or "1.0"
load(pathJoin("envvar", envvar_ver))

PrgEnv_intel_ver=os.getenv("PrgEnv_intel_ver") or "8.1.0"
load(pathJoin("PrgEnv-intel", PrgEnv_intel_ver))

intel_ver=os.getenv("intel_ver") or "19.1.3.304"
load(pathJoin("intel", intel_ver))

craype_ver=os.getenv("craype_ver") or "2.7.13"
load(pathJoin("craype", craype_ver))

cray_mpich_ver=os.getenv("cray_mpich_ver") or "8.1.7"
load(pathJoin("cray-mpich", cray_mpich_ver))

cray_pals_ver=os.getenv("cray_pals_ver") or "1.0.12"
load(pathJoin("cray-pals", cray_pals_ver))

imagemagick_ver=os.getenv("imagemagick_ver") or "7.0.8-7"
load(pathJoin("imagemagick", imagemagick_ver))

python_ver=os.getenv("python_ver") or "3.8.6"
load(pathJoin("python", python_ver))

proj_ver=os.getenv("proj_ver") or "7.1.0"
load(pathJoin("proj", proj_ver))

geos_ver=os.getenv("geos_ver") or "3.8.1"
load(pathJoin("geos", geos_ver))

cmake_ver=os.getenv("cmake_ver") or "3.20.2"
load(pathJoin("cmake", cmake_ver))

prepend_path("MODULEPATH", "/lfs/h1/mdl/nbm/save/apps/modulefiles")

python_modules_ver=os.getenv("python_modules_ver") or "3.8.6"
load(pathJoin("python_modules", python_modules_ver))

setenv("HPC_OPT", "/apps/ops/para/libs")
prepend_path("MODULEPATH", "/apps/ops/para/libs/modulefiles/compiler/intel/19.1.3.304")
prepend_path("MODULEPATH", "/apps/ops/para/libs/modulefiles/mpi/intel/19.1.3.304/cray-mpich/8.1.7")

jasper_ver=os.getenv("jasper_ver") or "2.0.25"
load(pathJoin("jasper", jasper_ver))

zlib_ver=os.getenv("zlib_ver") or "1.2.11"
load(pathJoin("zlib", zlib_ver))

libpng_ver=os.getenv("libpng_ver") or "1.6.37"
load(pathJoin("libpng", libpng_ver))

libjpeg_ver=os.getenv("libjpeg_ver") or "9c"
load(pathJoin("libjpeg", libjpeg_ver))
setenv("JPEG_LIBRARIES", "/apps/spack/libjpeg/9c/intel/19.1.3.304/jkr3isi257ktoouprwaxcn4twtye747z/lib")

hdf5_ver=os.getenv("hdf5_ver") or "1.10.6"
load(pathJoin("hdf5", hdf5_ver))

netcdf_ver=os.getenv("netcdf_ver") or "4.7.4"
load(pathJoin("netcdf", netcdf_ver))

prod_util_ver=os.getenv("prod_util_ver") or "2.0.13"
load(pathJoin("prod_util", prod_util_ver))

grib_util_ver=os.getenv("grib_util_ver") or "1.2.4"
load(pathJoin("grib_util", grib_util_ver))

wgrib2_ver=os.getenv("wgrib2_ver") or "2.0.8_wmo"
load(pathJoin("wgrib2", wgrib2_ver))

cfp_ver=os.getenv("cfp_ver") or "2.0.4"
load(pathJoin("cfp", cfp_ver))

setenv("MPISERIAL", "/lfs/h2/emc/hur/noscrub/local/bin/mpiserial")
setenv("cartopyDataDir", "/lfs/h2/emc/hur/noscrub/local/share/cartopy")

gsl_ver=os.getenv("gsl_ver") or "2.7"
load(pathJoin("gsl", gsl_ver))

udunits_ver=os.getenv("udunits_ver") or "2.2.28"
load(pathJoin("udunits", udunits_ver))

nco_ver=os.getenv("nco_ver") or "4.7.9"
load(pathJoin("nco", nco_ver))

prepend_path("MODULEPATH", "/apps/ops/test/nco/modulefiles")

rocoto_ver=os.getenv("rocoto_ver") or "1.3.4"
load(pathJoin("core", "rocoto", rocoto_ver))

whatis("Description: HAFS Graphics environment")
