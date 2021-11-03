import pathlib
# get filepath of the program
cwd_path = pathlib.Path(__file__)
main_path = str(cwd_path.parents[2])
src_path = str(cwd_path.parents[1])
log_path = str(pathlib.PurePath(main_path, "logs"))
conf_path = str(pathlib.PurePath(main_path, "config", "config.yaml"))
