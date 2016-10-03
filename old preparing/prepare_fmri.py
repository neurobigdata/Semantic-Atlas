import nibabel
import glob
import os
import numpy as np
import pickle

def allocate_active_voxels(file_in_path, file_out_path, activity_threshold=500):

    mri = nibabel.load(file_in_path)
    data = mri.get_data()

    voxels_activity_flags = data.max(axis=3) > activity_threshold
    number_active_voxels = voxels_activity_flags.sum()

    voxels_activity_flags = np.array( [voxels_activity_flags] * data.shape[-1])
    voxels_activity_flags = np.transpose(voxels_activity_flags, axes=[1,2,3,0])

    proccessed_data = np.multiply(data, voxels_activity_flags)
    total_voxels = data.shape[0] * data.shape[1] * data.shape[2] * 1.

    print 'path: {}, shape: {}'.format(file_in_path, data.shape)
    print ("fraction of active voxels: {}".format(number_active_voxels / total_voxels))

    with open(file_out_path, 'wb') as f:
        pickle.dump(proccessed_data, f)

if __name__ == '__main__':
    input_dir = 'data/fmri'
    output_dir = 'data/fmri_processed/'

    all_input_files_paths = glob.glob(os.path.join(input_dir, '*'))

    for i, in_filename_path in enumerate(all_input_files_paths):
        out_filename = os.path.basename(in_filename_path)
        allocate_active_voxels(in_filename_path, output_dir + out_filename)
