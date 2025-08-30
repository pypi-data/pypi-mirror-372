"""Frontend for working with data"""

from __future__ import annotations
import os
import base64
from dataclasses import dataclass
from typing import List, Union, Optional, TYPE_CHECKING
import funcnodes_core as fn
from pathlib import Path
from urllib.parse import unquote
from io import BytesIO
import shutil
from asynctoolkit.defaults.http import HTTPTool

if TYPE_CHECKING:
    from funcnodes_react_flow import ReactPlugin


__version__ = "0.5.0"


def path_encoder(obj, preview=False):
    """
    Encodes Path objects to strings.
    """
    if isinstance(obj, Path):
        return fn.Encdata(data=obj.as_posix(), handeled=True)
    return fn.Encdata(data=obj, handeled=False)


fn.JSONEncoder.add_encoder(path_encoder, enc_cls=[Path])


@dataclass
class FileInfoData:
    name: str
    path: str
    size: int
    modified: float
    created: float


@dataclass
class PathDictData:
    path: str
    files: List[FileInfoData]
    dirs: List["PathDictData"]
    name: str


class FileDataBytes(fn.types.databytes):
    """
    Custom data type for file data.
    """

    fileinfo: FileInfoData

    def __new__(cls, *args, fileinfo: FileInfoData, **kwargs):
        self = super().__new__(cls, *args, **kwargs)
        self.fileinfo = fileinfo
        return self


def make_file_info(fullpath: Union[Path, str], root: Union[Path, str]) -> FileInfoData:
    fullpath = Path(fullpath)
    root = Path(root)
    return FileInfoData(
        name=fullpath.name,
        path=fullpath.relative_to(root).as_posix(),
        size=os.path.getsize(fullpath),
        modified=os.path.getmtime(fullpath),
        created=os.path.getctime(fullpath),
    )


def make_path_dict(
    fullpath: Union[Path, str], root: Union[Path, str], levels=999
) -> PathDictData:
    fullpath = Path(fullpath)
    root = Path(root)

    def _recurisive_fill(
        path: Path,
        _levels: int,
    ) -> PathDictData:
        files = []
        dirs = []
        if _levels > 0:
            content = os.listdir(path)
            for f in content:
                fpath = path / f
                if os.path.isdir(fpath):
                    dirs.append(_recurisive_fill(fpath, _levels=_levels - 1))
                else:
                    files.append(
                        make_file_info(
                            fullpath=fpath,
                            root=root,
                        )
                    )
        relpath = path.relative_to(root)
        return PathDictData(
            path=relpath.as_posix(),
            files=files,
            dirs=dirs,
            name=relpath.name,
        )

    return _recurisive_fill(fullpath, _levels=levels)


def validate_path(path: Union[Path, str], root: Union[Path, str]):
    root = Path(root)
    path = Path(path)
    if not path.is_absolute():
        path = (root / path).resolve()
    # check if path is in root
    if not path.is_relative_to(root):
        fn.FUNCNODES_LOGGER.debug("Path is not in root: %s %s", path, root)
        raise Exception("Path is not in root")

    return path


def string_to_pathdict(path: str, node: fn.Node, levels=1) -> PathDictData:
    try:
        if not isinstance(path, str):
            return path
        if not node:
            return path
        if not path:
            return path
        if node.nodespace is None:
            return path
        root = Path(node.nodespace.get_property("files_dir"))
        fullpath = validate_path(Path(path), root)
        return make_path_dict(fullpath, root, levels=levels)
    except Exception:
        return path


class PathDict(fn.Node):
    """
    Seriealizes a path to dict
    """

    node_id = "files.path_dict"
    node_name = "Path Dict"
    parent = fn.NodeInput(type=Union[str, PathDictData], default=".", name="Parent")
    path = fn.NodeInput(type=str, default=".")
    data = fn.NodeOutput(type=PathDictData)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_input("parent").on("after_set_value", self._update_keys)
        self.on("after_set_nodespace", self._update_keys)

    def _update_keys(self, *args, **kwargs):
        try:
            d = self.get_input("parent").value
        except KeyError:
            return
        d = string_to_pathdict(d, self, levels=1)
        if isinstance(d, PathDictData):
            self.get_input("path").update_value_options(
                options=fn.io.EnumOf(
                    type="enum",
                    values=[sub.name for sub in d.dirs],
                    keys=[sub.name for sub in d.dirs],
                    nullable=False,
                )
            )
        else:
            self.get_input("path").update_value_options(options=None)

    async def func(self, path: str, parent: Union[str, PathDictData] = ".") -> None:
        if self.nodespace is None:
            raise Exception("Node not in a nodespace")

        root = Path(self.nodespace.get_property("files_dir"))
        if isinstance(parent, str):
            parent = make_path_dict(validate_path(Path(parent), root), root, levels=1)

        if path == "." and parent:
            self.outputs["data"].value = parent
            return
        if parent:
            path = Path(parent.path) / path
        targetpath = Path(path)
        fullpath = validate_path(targetpath, root)

        self.outputs["data"].value = make_path_dict(fullpath, root)


class BrowseFolder(fn.Node):
    """
    Browse a folder
    """

    node_id = "files.browse_folder"
    node_name = "Browse Folder"

    path = fn.NodeInput(type=Union[str, PathDictData], default=".")
    files = fn.NodeOutput(type=List[FileInfoData])
    dirs = fn.NodeOutput(type=List[PathDictData])

    async def func(self, path: Union[str, PathDictData]) -> None:
        if self.nodespace is None:
            raise Exception("Node not in a nodespace")
        root = Path(self.nodespace.get_property("files_dir"))
        if not isinstance(path, PathDictData):
            fullpath = validate_path(Path(path), root)
            path = make_path_dict(fullpath, root)

        validate_path(path.path, root)

        self.inputs["path"].set_value(path.path, does_trigger=False)
        self.outputs["files"].value = path.files
        self.outputs["dirs"].value = path.dirs


class OpenFile(fn.Node):
    """
    Open a file
    """

    node_id = "files.open_file"
    node_name = "Open File"
    parent = fn.NodeInput(type=Union[str, PathDictData], default=".")
    path = fn.NodeInput(
        type=Union[str, FileInfoData],
    )

    data = fn.NodeOutput(type=FileDataBytes)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_input("parent").on("after_set_value", self._update_keys)
        self.on("after_set_nodespace", self._update_keys)

    def _update_keys(self, *args, **kwargs):
        try:
            d = self.get_input("parent").value
        except KeyError:
            return

        d = string_to_pathdict(d, self, levels=1)
        if isinstance(d, PathDictData):
            self.get_input("path").update_value_options(
                options=fn.io.EnumOf(
                    type="enum",
                    values=[sub.name for sub in d.files],
                    keys=[sub.name for sub in d.files],
                    nullable=False,
                )
            )
        else:
            self.get_input("path").update_value_options(options=None)

    async def func(
        self,
        path: Union[str, FileInfoData],
        parent: Union[str, PathDictData] = ".",
    ) -> None:
        if self.nodespace is None:
            raise Exception("Node not in a nodespace")
        root = Path(self.nodespace.get_property("files_dir"))
        if isinstance(parent, str):
            parent = make_path_dict(validate_path(Path(parent), root), root, levels=1)
        if isinstance(path, str):
            if parent:
                path = Path(parent.path) / path
            fullpath = validate_path(Path(path), root)
            path = make_file_info(fullpath, root)

        fullpath = validate_path(path.path, root)
        with open(fullpath, "rb") as file:
            self.outputs["data"].value = FileDataBytes(file.read(), fileinfo=path)


class FileInfo(fn.Node):
    """
    Get file
    """

    node_id = "files.file_info"
    node_name = "File Info"
    parent = fn.NodeInput(type=Union[str, PathDictData], default=".")
    path = fn.NodeInput(
        type=Union[str, FileInfoData],
    )
    size = fn.NodeOutput(type=int)
    modified = fn.NodeOutput(type=float)
    created = fn.NodeOutput(type=float)
    filename = fn.NodeOutput(type=str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.get_input("parent").on("after_set_value", self._update_keys)
        self.on("after_set_nodespace", self._update_keys)

    def _update_keys(self, *args, **kwargs):
        try:
            d = self.get_input("parent").value
        except KeyError:
            return
        d = string_to_pathdict(d, self, levels=1)
        if isinstance(d, PathDictData):
            self.get_input("path").update_value_options(
                options=fn.io.EnumOf(
                    type="enum",
                    values=[sub.name for sub in d.files],
                    keys=[sub.name for sub in d.files],
                    nullable=False,
                )
            )
        else:
            self.get_input("path").update_value_options(options=None)

    async def func(
        self,
        path: Union[str, FileInfoData],
        parent: Optional[PathDictData] = None,
    ) -> None:
        if self.nodespace is None:
            raise Exception("Node not in a nodespace")

        root = Path(self.nodespace.get_property("files_dir"))
        if isinstance(parent, str):
            parent = make_path_dict(validate_path(Path(parent), root), root, levels=1)

        if isinstance(path, str):
            if parent:
                path = Path(parent.path) / path
            fullpath = validate_path(Path(path), root)
            path = make_file_info(fullpath, root)

        fullpath = validate_path(path.path, root)
        self.outputs["size"].value = os.path.getsize(fullpath)
        self.outputs["modified"].value = os.path.getmtime(fullpath)
        self.outputs["created"].value = os.path.getctime(fullpath)
        self.outputs["filename"].value = fullpath.name


class FileUpload(str):
    pass


class FileUploadNode(fn.Node):
    """
    Uploads a file
    """

    node_id = "files.upl"
    node_name = "File Upload"

    parent = fn.NodeInput(
        type=Union[str, PathDictData],
        default=".",
        does_trigger=False,
    )
    input_data = fn.NodeInput(type=FileUpload)
    load = fn.NodeInput(type=bool, default=True, does_trigger=False)
    save = fn.NodeInput(type=bool, default=False, does_trigger=False)

    data = fn.NodeOutput(type=FileDataBytes)
    file = fn.NodeOutput(type=FileInfoData)

    async def func(
        self,
        input_data: FileUpload,
        load: bool = True,
        save: bool = False,
        parent: Optional[PathDictData] = None,  # noqa F821
    ) -> None:
        """
        Uploads a file to a given URL.

        Args:
          url (str): The URL to upload the file to.
          file (str): The path to the file to upload.
        """

        if not load and not save:
            raise Exception("Either load or save must be True")

        if self.nodespace is None:
            raise Exception("Node not in a nodespace")

        if isinstance(
            input_data, list
        ):  # input data could be a list if it comes from a folder like upload
            input_data = input_data[0]

        root = Path(self.nodespace.get_property("files_dir"))
        fp = validate_path(Path(input_data), root)
        if fp is None or not os.path.exists(fp):
            raise Exception(f"File not found: {input_data}")

        fileinfo = make_file_info(fp, root)
        if load:
            with open(fp, "rb") as file:
                filedata = file.read()
            self.outputs["data"].value = FileDataBytes(filedata, fileinfo=fileinfo)
        else:
            self.outputs["data"].value = fn.NoValue

        if not save:
            os.remove(fp)
            self.outputs["file"].value = fn.NoValue
        else:
            self.outputs["file"].value = fileinfo


class FolderUpload(str):
    pass


class FolderUploadNode(fn.Node):
    """
    Uploads a file
    """

    node_id = "files.upl_folder"
    node_name = "Folder Upload"

    parent = fn.NodeInput(
        type=Union[str, PathDictData],
        default=".",
        does_trigger=False,
    )
    input_data = fn.NodeInput(type=FolderUpload, name="Folder")

    dir = fn.NodeOutput(type=PathDictData)

    async def func(
        self, input_data: FolderUpload, parent: Union[str, PathDictData] = "."
    ) -> None:
        """
        Uploads a file to a given URL.

        Args:
          url (str): The URL to upload the file to.
          file (str): The path to the file to upload.
        """

        if self.nodespace is None:
            raise Exception("Node not in a nodespace")

        root = Path(self.nodespace.get_property("files_dir"))
        fp = validate_path(Path(input_data), root)

        if not os.path.exists(fp):
            raise Exception(f"Folder not found: {input_data}")

        pathdict = make_path_dict(fp, root)
        self.outputs["dir"].value = pathdict


_DEFAULT_USER_AGENT = f"funcnodes-files/{__version__} funcnodes/{fn.__version__}"


class FileDownloadNode(fn.Node):
    """
    Downloads a file from a given URL and returns the file's content as bytes.
    """

    node_id = "files.dld"
    node_name = "File Download"

    url = fn.NodeInput(type="str")
    parent = fn.NodeInput(
        type=Union[str, PathDictData],
        default=".",
        does_trigger=False,
    )
    load = fn.NodeInput(type=bool, default=True, does_trigger=False)
    save = fn.NodeInput(type=bool, default=False, does_trigger=False)
    filename = fn.NodeInput(type=Optional[str], default=None, does_trigger=False)

    data = fn.NodeOutput(type=FileDataBytes)
    file = fn.NodeOutput(type=FileInfoData)

    user_agent = fn.NodeInput(
        type=str, default=_DEFAULT_USER_AGENT, hidden=True, name="User Agent"
    )
    headers = fn.NodeInput(type=Optional[dict], default=None, hidden=True)
    default_trigger_on_create = False

    async def func(
        self,
        url: str,
        parent: Union[str, PathDictData] = ".",
        load: bool = True,
        save: bool = False,
        filename: Optional[str] = None,
        user_agent: str = _DEFAULT_USER_AGENT,
        headers: Optional[dict] = None,
    ) -> None:
        """
        Downloads a file from a given URL and sets the "data" output to the file's content as bytes.

        Args:
          url (str): The URL of the file to download.
          timeout (float): The timeout in seconds for the download request.
        """
        if not load and not save:
            raise Exception("Either load or save must be True")

        if save:
            if self.nodespace is None:
                raise Exception("Node not in a nodespace")
            root = Path(self.nodespace.get_property("files_dir"))
            if isinstance(parent, str):
                parent = make_path_dict(
                    validate_path(Path(parent), root), root, levels=1
                )
            if parent:
                path = validate_path(parent.path, root)
            else:
                path = root

        if headers is None:
            headers = {}
        if user_agent:
            headers["User-Agent"] = user_agent

        async with await HTTPTool().run(url, headers=headers, stream=True) as response:
            await response.raise_for_status()

            headers = await response.headers()
            content_disposition = headers.get("Content-Disposition")
            if filename is None and save:
                if content_disposition:
                    # Extract filename from Content-Disposition header
                    filename = (
                        content_disposition.split("filename=")[-1].strip('"').strip("'")
                    )
                    filename = unquote(filename)
                else:
                    # Fallback: Use the URL's last segment as filename
                    filename = unquote(url.split("/")[-1])

            total_size = headers.get("Content-Length", 0) or None
            try:
                total_size = int(total_size)
            except ValueError:
                total_size = None
            value = fn.NoValue
            fileinfo = fn.NoValue
            if save:
                fullpath = path / filename
                with (
                    open(fullpath, "wb") as f,
                    self.progress(
                        total=total_size,
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=filename,
                    ) as progress,
                ):
                    async for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress.update(len(chunk))

                fileinfo = make_file_info(fullpath, root)
                if load:
                    with open(fullpath, "rb") as f:
                        value = FileDataBytes(f.read(), fileinfo=fileinfo)
            else:
                with (
                    BytesIO() as f,
                    self.progress(
                        total=total_size,
                        unit="B",
                        unit_scale=True,
                        unit_divisor=1024,
                        desc=filename,
                    ) as progress,
                ):
                    async for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            progress.update(len(chunk))
                    value = fn.types.databytes(f.getvalue())

        self.outputs["data"].value = value
        self.outputs["file"].value = fileinfo


@dataclass
class FileDownload:
    filename: str
    bytedata: bytes

    @property
    def content(self):
        return base64.b64encode(self.bytedata).decode("utf-8")

    def __str__(self) -> str:
        return f"FileDownload(filename={self.filename})"

    def __repr__(self) -> str:
        return self.__str__()

def file_download_json_handler(obj, preview=False):
    """
    Encodes dataclasses to dictionaries.
    """
    if isinstance(obj, FileDownload):
        return fn.Encdata(data=obj.filename, handeled=True,done=True)
    return fn.Encdata(data=obj, handeled=False)


fn.JSONEncoder.add_encoder(file_download_json_handler,enc_cls=[FileDownload])

def file_download_byte_handler(obj, preview=False):
    """
    Encodes dataclasses to dictionaries.
    """
    if isinstance(obj, FileDownload):
        return fn.BytesEncdata(data=obj.bytedata, handeled=True,mime="application/octet-stream")
    return fn.BytesEncdata(data=obj, handeled=False)

fn.ByteEncoder.add_encoder(file_download_byte_handler,enc_cls=[FileDownload])

class FileDownloadLocal(fn.Node):
    """
    Downloads a file the funcnodes stream to a local file
    """

    node_id = "files.dld_local"
    node_name = "File Download Local"

    output_data = fn.NodeOutput(type=FileDownload)
    data = fn.NodeInput(type=Union[fn.types.databytes, FileDataBytes, FileInfoData])
    filename = fn.NodeInput(type=Optional[str], default=None)

    async def func(
        self,
        data: Union[fn.types.databytes, FileDataBytes, FileInfoData],
        filename: str = None,
    ) -> None:
        """
        Downloads a file from a given URL and sets the "data" output to the file's content as bytes.

        Args:
          url (str): The URL of the file to download.
          timeout (float): The timeout in seconds for the download request.
        """
        if isinstance(data, FileInfoData):
            if self.nodespace is None:
                raise Exception("Node not in a nodespace")
            root = Path(self.nodespace.get_property("files_dir"))
            fullpath = validate_path(data.path, root)
            if filename is None:
                filename = data.name
            with open(fullpath, "rb") as file:
                data = file.read()
        elif isinstance(data, FileDataBytes):
            if filename is None:
                filename = data.fileinfo.name
        if filename is None:
            raise Exception("Filename must be provided if the data is passed as bytes")

        self.outputs["output_data"].value = FileDownload(
            filename=filename,
            bytedata=data,
        )


class FileDeleteNode(fn.Node):
    """
    Deletes a file
    """

    node_id = "files.delete"
    node_name = "Delete File"

    data = fn.NodeInput(
        type=Union[PathDictData, FileInfoData],
        does_trigger=False,
    )

    async def func(self, data: Optional[Union[PathDictData, FileInfoData]]) -> None:
        """
        Deletes a file from the given path.

        Args:
          path (str): The path to the file to delete.
        """
        if self.nodespace is None:
            raise Exception("Node not in a nodespace")
        root = Path(self.nodespace.get_property("files_dir"))
        fullpath = validate_path(data.path, root)

        if os.path.isfile(fullpath):
            os.remove(fullpath)
        elif os.path.isdir(fullpath):
            # if fullpath is root, delete only the content
            if fullpath == root:
                for f in os.listdir(fullpath):
                    shutil.rmtree(fullpath / f)
            else:
                shutil.rmtree(fullpath)


class SaveFile(fn.Node):
    """
    Saves a file
    """

    node_id = "files.save"
    node_name = "Save File"

    data = fn.NodeInput(type=Union[fn.types.databytes, FileDataBytes])
    filename = fn.NodeInput(type=str)
    path = fn.NodeInput(type=Optional[Union[str, PathDictData]], default=None)

    async def func(
        self,
        data: Union[fn.types.databytes, FileDataBytes],
        filename: str,
        path: Optional[Union[str, PathDictData]] = None,
    ) -> None:
        if self.nodespace is None:
            raise Exception("Node not in a nodespace")
        root = Path(self.nodespace.get_property("files_dir"))
        if isinstance(path, PathDictData):
            path = path.path
        elif path is None:
            path = root
        else:
            path = Path(path)

        path = path / filename

        path = validate_path(path, root)

        if not os.path.exists(path.parent):
            os.makedirs(path.parent)

        with open(path, "wb") as file:
            file.write(data)


NODE_SHELF = fn.Shelf(
    name="Files",  # The name of the shelf.
    nodes=[
        FileDownloadNode,
        FileUploadNode,
        FolderUploadNode,
        FileDownloadLocal,
        BrowseFolder,
        OpenFile,
        SaveFile,
        PathDict,
        FileInfo,
        FileDeleteNode,
    ],  # A list of node classes to include in the shelf.
    description="Nodes for working with data and files.",
    subshelves=[],
)


REACT_PLUGIN: ReactPlugin = {
    "js": [],
    "css": [],
    "module": os.path.join(os.path.dirname(__file__), "react_plugin", "js", "main.js"),
}
