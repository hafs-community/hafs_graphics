help([[
loads HAFS application level modulefile on Gaea C6
]])

prepend_path("MODULEPATH", "/ncrc/proj/epic/spack-stack/c6/spack-stack-1.9.2/envs/ue-intel-2023.2.0/install/modulefiles/Core")
prepend_path("MODULEPATH", "/ncrc/proj/epic/spack-stack/c6/modulefiles")

stack_intel_ver=os.getenv("stack_intel_ver") or "2023.2.0"
load(pathJoin("stack-intel", stack_intel_ver))

stack_cray_mpich_ver=os.getenv("stack_cray_mpich_ver") or "8.1.30"
load(pathJoin("stack-cray-mpich", stack_cray_mpich_ver))

craype_ver=os.getenv("craype_ver") or "2.7.30"
load(pathJoin("craype", craype_ver))

load("graphics_common")

prepend_path("MODULEPATH", "/autofs/ncrc-svm1_proj/hurr1/hafs/shared/modulefiles")

imagemagick_ver=os.getenv("imagemagick_ver") or "7.1.1-38"
load(pathJoin("ImageMagick", imagemagick_ver))

prepend_path("PATH", "/ncrc/proj/hurr1/hafs/shared/miniconda3/envs/WCOSS2_env/bin")

prepend_path("PYTHONPATH", "/ncrc/proj/hurr1/hafs/shared/miniconda3/envs/WCOSS2_env")

setenv("MPISERIAL", "/gpfs/f6/drsa-hurr1/world-shared/noscrub/local/bin/mpiserial")

setenv("cartopyDataDir", "/gpfs/f6/drsa-hurr1/world-shared/noscrub/local/share/cartopy")

whatis("Description: HAFS Graphics environment")
