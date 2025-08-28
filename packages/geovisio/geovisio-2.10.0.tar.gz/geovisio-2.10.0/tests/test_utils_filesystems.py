import fs.base
import os

from geovisio.utils import filesystems


def test_openFilesystemsFromConfig_single(tmp_path):
    res = filesystems.openFilesystemsFromConfig({"FS_URL": str(tmp_path)})

    assert os.path.isdir(tmp_path / "tmp")
    assert os.path.isdir(tmp_path / "permanent")
    assert os.path.isdir(tmp_path / "derivates")
    assert isinstance(res.tmp, fs.base.FS)
    assert isinstance(res.permanent, fs.base.FS)
    assert isinstance(res.derivates, fs.base.FS)

    res.tmp.writetext("test.txt", "test")
    res.permanent.writetext("test.txt", "test")
    res.derivates.writetext("test.txt", "test")


def test_openFilesystemsFromConfig_multi(tmp_path):
    mytmp = tmp_path / "my_tmp"
    mytmp.mkdir()
    myperm = tmp_path / "my_perm"
    myperm.mkdir()
    myderiv = tmp_path / "my_deriv"
    myderiv.mkdir()

    res = filesystems.openFilesystemsFromConfig(
        {
            "FS_TMP_URL": str(mytmp),
            "FS_PERMANENT_URL": str(myperm),
            "FS_DERIVATES_URL": str(myderiv),
        }
    )

    assert isinstance(res.tmp, fs.base.FS)
    assert isinstance(res.permanent, fs.base.FS)
    assert isinstance(res.derivates, fs.base.FS)


def test_openFilesystems_ok(tmp_path):
    # Prepare folders
    fstmp = tmp_path / "tmp"
    fstmp.mkdir()
    fspermanent = tmp_path / "permanent"
    fspermanent.mkdir()
    fsderivates = tmp_path / "derivates"
    fsderivates.mkdir()

    # Create container
    fses = filesystems.FilesystemsURL(tmp=str(fstmp), permanent=str(fspermanent), derivates=str(fsderivates))

    res = filesystems.openFilesystems(fses)

    assert isinstance(res.tmp, fs.base.FS)
    assert isinstance(res.permanent, fs.base.FS)
    assert isinstance(res.derivates, fs.base.FS)

    res.tmp.writetext("test.txt", "test")
    res.permanent.writetext("test.txt", "test")
    res.derivates.writetext("test.txt", "test")
