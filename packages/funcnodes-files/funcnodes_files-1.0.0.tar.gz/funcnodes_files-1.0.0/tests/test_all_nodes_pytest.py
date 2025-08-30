import pytest
from pytest_funcnodes import nodetest, all_nodes_tested
import funcnodes_core as fn
import funcnodes_files as fnmodule  # noqa
from pathlib import Path
import os


@pytest.fixture(scope="session")
def root():
    return Path(__file__).parent / "files"


@pytest.fixture(scope="function")
def ns():
    ns = fn.NodeSpace()
    root = Path(__file__).parent / "files"
    ns.set_property("files_dir", root.as_posix())
    return ns


@pytest.fixture(scope="session")
def reltestfilepath():
    root = Path(__file__).parent / "files"
    testfile = root / "test.txt"
    reltestfilepath = testfile.relative_to(root)
    return reltestfilepath


@pytest.fixture(scope="session")
def testfile():
    root = Path(__file__).parent / "files"
    return root / "test.txt"


def test_all_nodes_tested(all_nodes):
    all_nodes_tested(all_nodes, fnmodule.NODE_SHELF, ignore=[])


@nodetest(fnmodule.FileDownloadNode)
async def test_file_download():
    node = fnmodule.FileDownloadNode()
    node.inputs[
        "url"
    ].value = "https://upload.wikimedia.org/wikipedia/commons/2/2b/Cyborglog-of-eating-old-apple-d360.jpg"
    await node
    assert isinstance(node.get_output("data").value, bytes)


@nodetest(fnmodule.FileUploadNode)
async def test_file_upload(ns, reltestfilepath):
    node = fnmodule.FileUploadNode()

    ns.add_node_instance(node)
    data = fnmodule.FileUpload(reltestfilepath)

    node.inputs["input_data"].value = data
    node.inputs["save"].value = True

    assert node.inputs_ready()
    await node

    assert (
        node.get_output("data").value.strip() == b"hello\n".strip()
    )  # since load is turnedd off
    fid = node.get_output("file").value
    assert isinstance(fid, fnmodule.FileInfoData)
    assert fid.name == reltestfilepath.name
    assert fid.path == reltestfilepath.as_posix()


@nodetest(fnmodule.FolderUploadNode)
async def test_folder_upload(ns, testfile):
    node = fnmodule.FolderUploadNode()
    ns.add_node_instance(node)
    data = fnmodule.FolderUpload(".")

    node.inputs["input_data"].value = data
    await node
    pathdict = node.get_output("dir").value
    assert isinstance(pathdict, fnmodule.PathDictData)
    assert (
        pathdict.files[0].path
        == fnmodule.make_file_info(testfile, testfile.parent).path
    )


@nodetest(fnmodule.FileDownloadLocal)
async def test_file_download_local():
    node = fnmodule.FileDownloadLocal()
    data = fnmodule.FileDownload(filename="test.txt", bytedata=b"AAAA")
    node.inputs["data"].value = data.bytedata
    node.inputs["filename"].value = data.filename
    await node
    node.get_output("output_data").value == data


@nodetest(fnmodule.BrowseFolder)
async def test_browse_folder(ns):
    node = fnmodule.BrowseFolder()
    node = ns.add_node_instance(node)

    await node
    assert isinstance(node.get_output("dirs").value, list)
    assert isinstance(node.get_output("files").value, list)


@nodetest(fnmodule.OpenFile)
async def test_open_file(ns, reltestfilepath):
    node = fnmodule.OpenFile()
    ns.add_node_instance(node)
    node.inputs["path"].value = reltestfilepath.as_posix()
    await node
    assert isinstance(node.get_output("data").value, bytes)
    assert node.get_output("data").value.fileinfo.name == "test.txt"


@nodetest(fnmodule.FileInfo)
async def test_fileinfo(ns, reltestfilepath):
    node = fnmodule.FileInfo()
    ns.add_node_instance(node)
    node.inputs["path"].value = reltestfilepath.as_posix()
    await node
    assert isinstance(node.get_output("size").value, int)
    assert isinstance(node.get_output("created").value, float)
    assert isinstance(node.get_output("modified").value, float)
    node.get_output("filename").value == "test.txt"


@nodetest(fnmodule.PathDict)
async def test_pathdict(ns):
    node = fnmodule.PathDict()
    ns.add_node_instance(node)
    node.inputs["path"].value = "."
    await node
    assert isinstance(node.get_output("data").value, fnmodule.PathDictData)


@nodetest(fnmodule.FileDeleteNode)
async def test_delete_file(ns, testfile):
    node = fnmodule.FileDeleteNode()
    ns.add_node_instance(node)

    testfile = testfile.parent / "test_delete.txt"
    with open(testfile, "w") as f:
        f.write("test")

    assert testfile.exists()

    node.inputs["data"].value = fnmodule.make_file_info(testfile, testfile.parent)
    await node
    assert not testfile.exists()


@nodetest(fnmodule.SaveFile)
async def test_save_file(ns, root):
    node = fnmodule.SaveFile()
    ns.add_node_instance(node)
    node.inputs["data"].value = b"test"
    node.inputs["filename"].value = "test_save.txt"
    await node
    assert (root / "test_save.txt").exists()
    os.remove(root / "test_save.txt")

    node.inputs["path"].value = "savetest"
    await node
    assert (root / "savetest" / "test_save.txt").exists()
    os.remove(root / "savetest" / "test_save.txt")
    os.rmdir(root / "savetest")


@nodetest(fnmodule.BrowseFolder)
async def test_browse_folder_with_path(ns, root):
    node = fnmodule.BrowseFolder()
    ns.add_node_instance(node)
    node.inputs["path"].value = root.as_posix()
    await node
    assert isinstance(node.get_output("dirs").value, list)
    assert isinstance(node.get_output("files").value, list)
    assert len(node.get_output("dirs").value) == 1
    assert len(node.get_output("files").value) == 1

    path_dict_a = fnmodule.PathDict()
    ns.add_node_instance(path_dict_a)
    await path_dict_a
    print(path_dict_a.inputs["path"].value_options["options"])
    assert path_dict_a.inputs["path"].value_options["options"]["values"] == ["a"]
    path_dict_a.inputs["path"].value = "a"
    await path_dict_a
    assert isinstance(path_dict_a.get_output("data").value, fnmodule.PathDictData)
    assert len(path_dict_a.get_output("data").value.dirs) == 1
    assert path_dict_a.get_output("data").value.dirs[0].name == "b"

    path_dict_b = fnmodule.PathDict()
    ns.add_node_instance(path_dict_b)
    path_dict_b.inputs["parent"].connect(path_dict_a.get_output("data"))
    await path_dict_b
    assert path_dict_b.inputs["path"].value_options["options"]["values"] == ["b"]
    path_dict_b.inputs["path"].value = "b"
    await path_dict_b

    assert isinstance(path_dict_b.get_output("data").value, fnmodule.PathDictData)
    assert len(path_dict_b.get_output("data").value.files) == 1
    assert path_dict_b.get_output("data").value.files[0].name == "c.txt"
