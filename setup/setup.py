# coding=utf-8
import argparse
import os
from distutils.core import setup
from Cython.Build import cythonize
from shutil import copyfile
BUILD_DIR = "setup_build"
DIST_DIR = "setup_dist"

# 循环获取要编译的pyhton文件，并将被exclude的文件存入exclude_list中
def get_py(root_path, exclude_pattern, exclude_list):
    try:
        files = os.listdir(root_path)
        for f in files:
            full_path = root_path + "/" + f
            if os.path.isdir(full_path):
                # 目录
                for r in get_py(full_path, exclude_pattern, exclude_list):
                    yield r
            elif os.path.isfile(full_path):
                # 文件
                # 判断是否为python文件
                if len(f) >= 3 and f[-3:] == ".py":
                    # 判断文件是否被排除
                    is_exclude = False
                    for ef in exclude_pattern:
                        if ef in full_path:
                            is_exclude = True
                            exclude_list.append(full_path)
                            break
                    if not is_exclude:
                        # 文件未被排除
                        yield full_path
    except OSError:
        pass


# 1. 获取命令行参数
parser = argparse.ArgumentParser(description='Compile python project')
parser.add_argument('main_file', metavar='MAIN', type=str, help='main_file')
parser.add_argument('-p', dest='path_dep', nargs="+", help='path dependency')
parser.add_argument('-n', dest='name', type=str, help='name')
parser.add_argument('-j', dest='jobs', type=str, help='use like make -j', default="4")
arg = parser.parse_args()
print("main_file: " + arg.main_file)
print("path_dep: " + str(arg.path_dep))
print("jobs: " + str(arg.jobs))

# 2. 获取需要被编译的文件（主函数除外）
module_list = []  # 需要编译的文件
exclude_list = []  # 不被包含的文件
exclude_pattern = ["__init__.py", arg.main_file]
for p in arg.path_dep:
    el = []
    module_list.extend(list(get_py(p, exclude_pattern, el)))
    exclude_list.extend(el)
exclude_list.append(arg.main_file)
exclude_list = list(set(exclude_list))
module_list = list(set(module_list))
print("module_list: " + str(module_list))
print("exclude_list: " + str(exclude_list))

# 3. 编译module_list
setup(name=arg.name,
      ext_modules=cythonize(module_list=module_list,
                            compiler_directives=dict(
                                always_allow_keywords=True,
                                c_string_encoding='utf-8',
                                language_level=3
                            ),
                            build_dir=BUILD_DIR),
      script_args=["build_ext", "-b", DIST_DIR, "-j", arg.jobs])

# 4. 将__init__.py和main_file拷贝过去
for exclude_file in exclude_list:
    try:
        copyfile(exclude_file, os.path.join(DIST_DIR, exclude_file))
    except IOError:
        pass