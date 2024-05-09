from pathlib import Path
from hloc import extract_features, match_features, reconstruction, visualization, pairs_from_retrieval
import os


def ReconstructionFromImages(pathstring, num_matched=5):
    pathstring += "/"
    imagesstring = pathstring + 'images'
    images = Path(imagesstring)
    pathoutputsstring = pathstring + 'output/'
    outputs = Path(pathoutputsstring)
    sfm_pairs = outputs / 'pairs-netvlad.txt'
    pathsfm_dirstring = pathoutputsstring + 'sparse'
    sfm_dir = outputs / 'sparse'

    retrieval_conf = extract_features.confs['netvlad']
    feature_conf = extract_features.confs['superpoint_max']
    matcher_conf = match_features.confs['superglue']

    retrieval_path = extract_features.main(retrieval_conf, images, outputs)
    pairs_from_retrieval.main(retrieval_path, sfm_pairs, num_matched=num_matched)

    feature_path = extract_features.main(feature_conf, images, outputs)

    match_path = match_features.main(matcher_conf, sfm_pairs, feature_conf['output'], outputs)

    reconstruction.main(sfm_dir, images, sfm_pairs, feature_path, match_path)

    dense_path = pathoutputsstring + "dense"
    converter = "colmap image_undistorter --image_path " + imagesstring + " --output_path " + dense_path + " --input_path " + pathsfm_dirstring
    converter = converter + "\n"

    converter = converter + "colmap patch_match_stereo --workspace_path " + dense_path
    converter = converter + "\n"

    converter = converter + "colmap stereo_fusion --workspace_path " + dense_path + " --output_path " + dense_path + "/fused-rgb.ply"
    converter = converter + "\n"
    os.system(converter)

    os.system(converter)

    return 0


if __name__ == '__main__':
    path = "YOUR/PATH"
    ReconstrucionFromImages(path)
