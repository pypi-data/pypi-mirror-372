from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup
import pybind11
import platform

# 根据操作系统设置不同的编译器参数
if platform.system() == "Windows":
    extra_compile_args = [
        "/utf-8",      # MSVC: 指定源文件编码为UTF-8
        "/wd4819",     # MSVC: 禁用编码警告C4819
    ]
else:
    extra_compile_args = [
        "-fvisibility=hidden",  # 隐藏符号表中的非必要符号
        "-g0",                  # 不生成调试信息
    ]

ext_modules = [
    Pybind11Extension(
        "leda_upc",
        ["src/main.cpp"],
        include_dirs=[pybind11.get_include()],
        language='c++',
        cxx_std=14,
        extra_compile_args=extra_compile_args,
    ),
]

setup(
    name="leda-upc",
    version="1.0",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=["pybind11>=2.6.0"], 
    # 添加平台支持信息
    platforms=["any"],
)
