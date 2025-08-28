from dataclasses import dataclass
import fs.base
from fs import open_fs
from fs.errors import ResourceNotFound
from fs_s3fs import S3FS
from .. import errors


@dataclass
class FilesystemsURL:
    """Filesystem URLs for all necessary storage"""

    tmp: str
    permanent: str
    derivates: str


@dataclass
class Filesystems:
    """Container for all opened filesystems"""

    tmp: fs.base.FS
    permanent: fs.base.FS
    derivates: fs.base.FS


def openFilesystemsFromConfig(config):
    """Open filesystem from env variables (either single or 3 filesystems)"""

    urlBase = None if not config.get("FS_URL") else config.get("FS_URL")
    urlTmp = None if not config.get("FS_TMP_URL") else config.get("FS_TMP_URL")
    urlDeriv = None if not config.get("FS_DERIVATES_URL") else config.get("FS_DERIVATES_URL")
    urlPerm = None if not config.get("FS_PERMANENT_URL") else config.get("FS_PERMANENT_URL")
    oneOf3 = urlTmp is not None or urlDeriv is not None or urlPerm is not None
    allOf3 = urlTmp is not None and urlDeriv is not None and urlPerm is not None

    if urlBase is None and oneOf3:
        if allOf3:
            fsesUrl = FilesystemsURL(tmp=urlTmp, permanent=urlPerm, derivates=urlDeriv)
            return openFilesystems(fsesUrl)
        else:
            raise Exception("One of the filesystem env variable (FS_TMP_URL, FS_PERMANENT_URL, FS_DERIVATES_URL) is missing")

    elif urlBase is not None and not allOf3:
        fsSingle = _open_fs(urlBase, name="", envvar="FS_URL")

        # Create directories
        tmp = fsSingle.makedir("/tmp", recreate=True)
        perm = fsSingle.makedir("/permanent", recreate=True)
        derivates = fsSingle.makedir("/derivates", recreate=True)

        return Filesystems(tmp, perm, derivates)

    elif urlBase is None and not allOf3:
        raise Exception(
            "You must define a filesystem environment variables (either FS_URL or FS_TMP_URL+FS_PERMANENT_URL+FS_DERIVATES_URL)"
        )
    else:
        raise Exception("You can't set both FS_URL and FS_TMP_URL+FS_PERMANENT_URL+FS_DERIVATES_URL environment variables")


def openFilesystems(fses: FilesystemsURL):
    """Creates access to all needed filesystems

    Parameters
    ----------
    fses : FilesystemsURL
            Filesystems container

    Returns
    -------
    Filesystems
            Connector for each filesystem

    Raises
    ------
    Exception
            If one of the filesystems is not working
    """

    fstmp = _open_fs(fses.tmp, "temporary", "FS_TMP_URL")
    fsperm = _open_fs(fses.permanent, "permanent", "FS_PERMANENT_URL")
    fsder = _open_fs(fses.derivates, "derivates", "FS_DERIVATES_URL")

    return Filesystems(fstmp, fsperm, fsder)


def _open_fs(url: str, name: str, envvar: str) -> fs.base.FS:
    """Open a filesystem and initialise it

    Parameters
    ----------
    url : str
            url of the filesystem
    name : str
            name of the filesystem
    envvar : str
            name of the environment variable it's stored in

    Returns
    -------
    fs.base.FS
            an opened filesystem

    Raises
    ------
    Exception
            If one of the filesystems is not accessible
    """
    try:
        f = open_fs(url)
    except Exception as e:
        raise errors.UnavailableFilesystem(
            f"Filesystem for {name} ({envvar}) is not accessible. Please check your URL is correct: {url}"
        ) from e

    if isinstance(f, S3FS):
        # set s3fs to unstrict mode to not check directories on file upload to speedup download/upload
        f.strict = False
        # in s3 we don't care about directory creation as they have no meaning in s3 and can save some time
        f.make_dirs = False
    return f


def removeFsTreeEvenNotFound(fs, path):
    """Deletes tree from given fs without raising ResourceNotFound exception"""
    try:
        fs.removetree(path)
    except ResourceNotFound:
        pass


def removeFsEvenNotFound(fs, path):
    """Deletes file from given fs without raising ResourceNotFound exception"""
    try:
        fs.remove(path)
    except ResourceNotFound:
        pass
