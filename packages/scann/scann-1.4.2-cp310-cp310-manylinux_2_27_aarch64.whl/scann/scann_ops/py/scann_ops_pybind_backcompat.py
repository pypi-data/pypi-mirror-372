"""Back-compatibility shim with old-style scann_ops_pybind serialization."""

import os

from scann.scann_ops import scann_assets_pb2


def path_exists(path: str) -> bool:
  """Wrapper around Google/OSS check for if file/directory exists."""
  return os.path.exists(path)


def populate_and_save_assets_proto(
    artifacts_dir: str) -> scann_assets_pb2.ScannAssets:
  """Populate and write a ScannAssets proto listing assets in `artifacts_dir`.

  Args:
    artifacts_dir: the directory for which this function finds ScaNN assets. The
      resulting proto is written in plaintext format to
      `artifacts_dir/scann_assets.pbtxt`.
  Returns:
    The ScannAssets proto object.
  """
  assets = scann_assets_pb2.ScannAssets()

  def add_if_exists(filename, asset_type):
    file_path = os.path.join(artifacts_dir, filename)
    if path_exists(file_path):
      assets.assets.append(
          scann_assets_pb2.ScannAsset(
              asset_path=file_path, asset_type=asset_type))

  add_if_exists("ah_codebook.pb", scann_assets_pb2.ScannAsset.AH_CENTERS)
  add_if_exists("serialized_partitioner.pb",
                scann_assets_pb2.ScannAsset.PARTITIONER)
  add_if_exists("datapoint_to_token.npy",
                scann_assets_pb2.ScannAsset.TOKENIZATION_NPY)
  add_if_exists("hashed_dataset.npy",
                scann_assets_pb2.ScannAsset.AH_DATASET_NPY)
  add_if_exists("int8_dataset.npy",
                scann_assets_pb2.ScannAsset.INT8_DATASET_NPY)
  add_if_exists("int8_multipliers.npy",
                scann_assets_pb2.ScannAsset.INT8_MULTIPLIERS_NPY)
  add_if_exists("dp_norms.npy", scann_assets_pb2.ScannAsset.INT8_NORMS_NPY)
  add_if_exists("dataset.npy", scann_assets_pb2.ScannAsset.DATASET_NPY)

  with open(os.path.join(artifacts_dir, "scann_assets.pbtxt"), "w") as f:
    f.write(str(assets))
  return assets
