import tarfile
from io import BytesIO
from unittest import mock

import pytest

from pygitguardian.client import ContentTooLarge, _create_tar


def test_create_tar(tmp_path):
    """
    GIVEN a list of filenames, representing paths relative to the tmp directory
    WHEN the _create_tar method is called
    THEN a bytes object is outputted, representing a tar of the files, with paths relative to the tmp directory
    """
    file1_name = "file1.txt"
    dir_path = "my_test_dir"
    file2_name = f"{dir_path}/file2.txt"
    file1_content = "My first document"
    file2_content = "My second document"

    (tmp_path / file1_name).write_text(file1_content)
    (tmp_path / dir_path).mkdir(parents=True, exist_ok=True)
    (tmp_path / file2_name).write_text(file2_content)

    tar_stream = _create_tar(tmp_path, [file1_name, file2_name])

    # Create tar archive from bytes stream and write it in the tmp_path/output directory
    (tmp_path / "output").mkdir(exist_ok=True)
    with tarfile.open(fileobj=BytesIO(tar_stream), mode="r:gz") as tar:
        tar.extractall(tmp_path / "output")

    assert file1_content == (tmp_path / f"output/{file1_name}").read_text()
    assert file2_content == (tmp_path / f"output/{file2_name}").read_text()


def test_create_tar_cannot_exceed_max_tar_content_size(tmp_path):
    with mock.patch("os.path.getsize", return_value=16 * 1024 * 1024):
        file1_name = "file1.txt"
        file2_name = "file2.txt"

        (tmp_path / file1_name).write_text("")
        (tmp_path / file2_name).write_text("")

        with pytest.raises(
            ContentTooLarge,
            match=r"The total size of the files processed exceeds \d+MB, please try again with less files",
        ):
            _create_tar(tmp_path, [file1_name, file2_name])
