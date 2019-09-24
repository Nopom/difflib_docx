from zipfile import ZipFile
import zipfile

class ZipManager(ZipFile):

    def remove(self, member):
        if "a" not in self.mode:
            raise RuntimeError('remove() requires mode "a"')
        if not self.fp:
            raise RuntimeError(
                "Attempt to modify ZIP archive that was already closed")

        # Make sure we have an info object
        if isinstance(member, zipfile.ZipInfo):
            # 'member' is already an info object
            zinfo = member
        else:
            # Get info object for member
            zinfo = self.getinfo(member)

        # To remove the member we need its size and location in the archive
        fname = zinfo.filename
        zlen = len(zinfo.FileHeader()) + zinfo.compress_size
        fileofs = zinfo.header_offset

        # Modify all the relevant file pointers
        for info in self.infolist():
            if info.header_offset > fileofs:
                info.header_offset = info.header_offset - zlen

        # Remove the zipped data
        self.fp.seek(fileofs + zlen)
        after = self.fp.read()
        self.fp.seek(fileofs)
        self.fp.write(after)
        self.fp.truncate()

        # Fix class members with state
        self._didModify = True
        self.filelist.remove(zinfo)
        del self.NameToInfo[fname]

        # 删除zip包中的文件夹

    def delete_dir(self, dir_name):
        entrys = self.namelist()
        is_dir_existed = False
        for delete_entry in entrys:
            if delete_entry.startswith(dir_name):
                is_dir_existed = True
                self.remove(delete_entry)
        if not is_dir_existed:
            print('entry dir  which you input is not existed')
