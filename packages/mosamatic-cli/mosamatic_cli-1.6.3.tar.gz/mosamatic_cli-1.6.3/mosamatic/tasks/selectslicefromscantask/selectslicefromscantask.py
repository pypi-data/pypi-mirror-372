import os
import math
import tempfile
import shutil
import nibabel as nib
import numpy as np

from mosamatic.tasks.task import Task
from mosamatic.logging import LogManager
from mosamatic.utils import (
    is_dicom, 
    load_dicom,
)

LOG = LogManager()

TOTAL_SEGMENTATOR_OUTPUT_DIR = os.path.join(tempfile.gettempdir(), 'total_segmentator_output')
Z_DELTA_OFFSETS = {
    'vertebrae_L3': 0.333,
    'vertebrae_T4': 0.5,
}


class SelectSliceFromScanTask(Task):
    def __init__(self, scans_dir, output_dir, vertebral_level, overwrite):
        super(SelectSliceFromScanTask, self).__init__(
            input={'scans_dir': scans_dir},
            output=output_dir,
            params={'vertebral_level': vertebral_level},
            overwrite=overwrite,
        )

    def load_scan_dirs(self):
        scan_dirs = []
        for d in os.listdir(self.input('scans_dir')):
            scan_dir = os.path.join(self.input('scans_dir'), d)
            if os.path.isdir(scan_dir):
                scan_dirs.append(scan_dir)
        return scan_dirs
    
    def extract_masks(self, scan_dir):
        os.makedirs(TOTAL_SEGMENTATOR_OUTPUT_DIR, exist_ok=True)
        os.system(f'TotalSegmentator -i {scan_dir} -o {TOTAL_SEGMENTATOR_OUTPUT_DIR} --fast')

    def delete_total_segmentator_output(self):
        if os.path.exists(TOTAL_SEGMENTATOR_OUTPUT_DIR):
            shutil.rmtree(TOTAL_SEGMENTATOR_OUTPUT_DIR)

    def get_z_delta_offset_for_mask(self, mask_name):
        if mask_name not in Z_DELTA_OFFSETS.keys():
            return None
        return Z_DELTA_OFFSETS[mask_name]

    def find_slice(self, scan_dir, vertebral_level):
        # Find Z-positions DICOM images
        z_positions = {}
        for f in os.listdir(scan_dir):
            f_path = os.path.join(scan_dir, f)
            p = load_dicom(f_path, stop_before_pixels=True)
            if p is not None:
                z_positions[p.ImagePositionPatient[2]] = f_path
        # Find Z-position L3 image
        mask_file = os.path.join(TOTAL_SEGMENTATOR_OUTPUT_DIR, f'{vertebral_level}.nii.gz')
        mask_obj = nib.load(mask_file)
        mask = mask_obj.get_fdata()
        affine_transform = mask_obj.affine
        indexes = np.array(np.where(mask == 1))
        index_min = indexes.min(axis=1)
        index_max = indexes.max(axis=1)
        world_min = nib.affines.apply_affine(affine_transform, index_min)
        world_max = nib.affines.apply_affine(affine_transform, index_max)
        z_direction = affine_transform[:3, 2][2]
        z_sign = math.copysign(1, z_direction)
        z_delta_offset = self.get_z_delta_offset_for_mask(vertebral_level)
        if z_delta_offset is None:
            return None
        z_delta = 0.333 * abs(world_max[2] - world_min[2]) # This needs to be vertebra-specific perhaps
        z_l3 = world_max[2] - z_sign * z_delta
        # Find closest L3 image in DICOM set
        positions = sorted(z_positions.keys())
        closest_file = None
        for z1, z2 in zip(positions[:-1], positions[1:]):
            if min(z1, z2) <= z_l3 <= max(z1, z2):
                closest_z = min(z_positions.keys(), key=lambda z: abs(z - z_l3))
                closest_file = z_positions[closest_z]
                LOG.info(f'Closest image: {closest_file}')
                break
        return closest_file

    def run(self):
        scan_dirs = self.load_scan_dirs()
        vertebral_level = self.param('vertebral_level')
        nr_steps = len(scan_dirs)
        for step in range(nr_steps):
            scan_dir = scan_dirs[step]
            scan_name = os.path.split(scan_dir)[1]
            self.extract_masks(scan_dir)
            file_path = self.find_slice(scan_dir, vertebral_level)
            if file_path is not None:
                extension = '' if file_path.endswith('.dcm') else '.dcm'
                target_file_path = os.path.join(self.output(), vertebral_level + '_' + scan_name + extension)
                shutil.copyfile(file_path, target_file_path)
            else:
                LOG.error(f'Could not find slice for vertebral level: {vertebral_level}')
            self.delete_total_segmentator_output()
            self.set_progress(step, nr_steps)