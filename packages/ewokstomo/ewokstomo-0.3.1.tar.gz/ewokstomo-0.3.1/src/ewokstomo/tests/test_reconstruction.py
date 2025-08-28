import shutil
from pathlib import Path

import pytest
from ewokstomo.tasks.reconstruct_slice import ReconstructSlice


def get_data_dir(scan_name: str) -> Path:
    return Path(__file__).resolve().parent / "data" / scan_name


@pytest.fixture
def tmp_dataset_path(tmp_path) -> Path:
    src_dir = get_data_dir("TestEwoksTomo_0010")
    dst_dir = tmp_path / "TestEwoksTomo_0010"
    shutil.copytree(src_dir, dst_dir)
    # remove any existing darks/flats and gallery
    for pattern in ("*_darks.hdf5", "*_flats.hdf5", "gallery"):
        for f in dst_dir.glob(pattern):
            if f.is_dir():
                shutil.rmtree(f)
            else:
                f.unlink()
    # generate fresh darks/flats
    from ewokstomo.tasks.reducedarkflat import ReduceDarkFlat

    nx = dst_dir / "TestEwoksTomo_0010.nx"
    rd_task = ReduceDarkFlat(
        inputs={
            "nx_path": str(nx),
            "dark_reduction_method": "mean",
            "flat_reduction_method": "median",
            "overwrite": True,
            "return_info": False,
        },
    )
    rd_task.run()
    return dst_dir


@pytest.mark.order(5)
@pytest.mark.parametrize("Task", [ReconstructSlice])
def test_slice_reconstruction_task(Task, tmp_dataset_path):
    nx = tmp_dataset_path / "TestEwoksTomo_0010.nx"

    nx_path = "dontexist.nx"
    nabu_conf = {
        "dataset": {"location": None},
        "reconstruction": {
            "start_z": "middle",
            "end_z": "middle",
        },
        "output": {"location": ""},
    }
    with pytest.raises(FileNotFoundError):
        task = Task(
            inputs={
                "config_dict": nabu_conf,
                "slice_index": "middle",
                "nx_path": nx_path,
            }
        )
        task.run()

    nx_path = str(nx)
    task = Task(
        inputs={"config_dict": nabu_conf, "slice_index": "middle", "nx_path": nx_path}
    )
    task.run()

    rec_dir = Path(task.outputs.reconstructed_slice_path)
    assert rec_dir.exists(), "Reconstructed slices directory does not exist"
    assert rec_dir.is_file(), "Reconstructed slices path is not a file"
