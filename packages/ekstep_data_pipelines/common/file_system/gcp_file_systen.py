from ekstep_data_pipelines.common.utils import get_logger

Logger = get_logger("GCPFileSystem")


class GCPFileSystem:
    def __init__(self, gcp_operations):
        self.gcp_operations = gcp_operations

    def ls(self, dir_path):
        paths = self.gcp_operations.list_blobs_in_a_path(dir_path)
        return list(map(lambda p: p.name, paths))

    def mv(self, source_dir, target_dir, is_dir=True):
        # if is_dir and self.gcp_operations.check_path_exists(self, source_dir):
        #     Logger.info("source dir does not exist:%s", source_dir)
        #     return
        Logger.info("Moving path %s --> %s", source_dir, target_dir)
        files = self.ls(source_dir)
        for file in files:
            self.mv_file(file, target_dir)

    def mv_file(self, file, target_dir):
        paths = file.split("/")
        paths.pop()
        source_dir = "/".join(paths)
        destination_blob_name = file.replace(source_dir, target_dir)
        Logger.info("Moving file %s --> %s", file, destination_blob_name)
        self.gcp_operations.move_blob(file, destination_blob_name)
