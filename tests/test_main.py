from benchlingapi import BenchlingAPI as api
import re


def test_init(api):
    # Init called from fixture once per test run
    assert api is not None


def test_folders(api):
    assert len(api.folders) > 0
    assert len(api.folders[0]) > 0


def test_folder_exists(api):
    f = api.folders[0]
    assert api.folder_exists(f["name"], query="name", regex=False)
    assert api.folder_exists(f["id"], query="id", regex=False)
    assert api.folder_exists(".+"+f["name"]+".*", query="name", regex=True)
    assert not api.folder_exists(".+"+f["name"]+".*", query="name", regex=False)
    # https: // docs.pytest.org / en / latest / builtin.html
    # def test1():
    #     with pytest.raises(ValueError) as e:
    #         dosomething()
    #     pytest.approx
    #


def test_search(api):
    x = api.search("cas9", querytype="text", limit=10, offset=0)
    print(x)


def test_gets(api):
    assert len(api.sequences) > 0
    assert len(api.folders) > 0
    assert len(api.getme()) > 0

    s = api.get_sequence(api.sequences[0]["id"])


def test_sharelink(api, config):
    sharelinks = config["sharelinks"]
    for link in sharelinks:
        soup = api._opensharelink(link)
        seqid = api._getsequenceidfromsharelink(link)
        s = api.getsequencefromsharelink(link)
        assert "id" in s
        assert "name" in s


def test_finds(api):
    f = api.folders[0]
    assert api.find_folder(f["name"], query="name", regex=False)
    assert api.folder_exists(f["id"], query="id", regex=False)
    assert api.folder_exists(".+"+f["name"]+".*", query="name", regex=True)
    assert not api.folder_exists(".+"+f["name"]+".*", query="name", regex=False)


def test_create_patch_and_delete_folder(api):
    pass


def test_create_patch_and_delete_sequence(api):
    pass


def test_alignments(api):
    raise ValueError("Not implemented")


def test_main(api):
    s = api.get_sequence("seq_uT2Pj9eV")
    print(s)
