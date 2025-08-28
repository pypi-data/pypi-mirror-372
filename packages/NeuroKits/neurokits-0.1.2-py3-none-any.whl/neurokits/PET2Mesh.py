import os
import numpy as np
import nibabel as nib
import pyvista as pv
from nilearn import datasets, image
from nilearn.image import smooth_img
from scipy.ndimage import map_coordinates
from scipy.spatial import cKDTree
from tqdm import tqdm


# 可视化相关
# VISUALIZE = True
VISUALIZE = False
SHOW_ROI_POINTS = True
DOWNSAMPLE_STEP = 5





def load_nifti(path):
    img = nib.load(path)
    data = img.get_fdata(dtype=np.float32)
    affine = img.affine
    return data, affine




def Plot_Mesh_Mask(mesh, masks):
    plotter = pv.Plotter()
    plotter.add_mesh(mesh, color='white', opacity=0.3, show_edges=False)

    if SHOW_ROI_POINTS:
        print("Collecting ROI point clouds for visualization (main thread)...")
        for m in tqdm(masks, desc="ROI point clouds"):
            mask_path = os.path.join(ROI_MASK_DIR, m)
            try:
                mask_vol, affine = load_nifti(mask_path)
                voxel_idx = np.argwhere(mask_vol > 0)
                if voxel_idx.size == 0:
                    continue
                world_coords = nib.affines.apply_affine(affine, voxel_idx)
                if DOWNSAMPLE_STEP and DOWNSAMPLE_STEP > 1:
                    world_coords = world_coords[::DOWNSAMPLE_STEP]
                roi_points = pv.PolyData(world_coords)
                color = np.random.rand(3)
                plotter.add_mesh(
                    roi_points,
                    color=color,
                    point_size=4.0,
                    render_points_as_spheres=True
                )
            except Exception as e:
                print(f"[WARN] Skip ROI points for {m}: {e}")
    plotter.show()


def interpolate_pet_to_mesh(pet_suvr, mesh, threshold, masks=None, merge_method = 'max'):
    mesh_points = mesh.points
    if masks is None:
        print('No mask provided, interpolation will be done on the whole mesh.')
        # world → voxel index
        inv_affine = np.linalg.inv(pet_image.affine)
        ijk = nib.affines.apply_affine(inv_affine, mesh_points)
        # 插值（3D 三次样条）
        suvr_field = map_coordinates(pet_suvr, ijk.T, order=1, mode='nearest')
        return suvr_field.astype(np.float32)
    else:
        suvr_field = np.zeros(mesh.points.shape[0], dtype=np.float32)
        for mask in tqdm(masks, desc="Interpolating PET to mesh with ROIs"):
            ref_mask_data, ref_mask_affine = load_nifti(mask)
            voxel_idx = np.argwhere(ref_mask_data > 0)
            if voxel_idx.size == 0:
                return np.zeros(mesh_points.shape[0], dtype=np.float32)

            world_coords = nib.affines.apply_affine(ref_mask_affine, voxel_idx)
            tree = cKDTree(world_coords)
            min_dist, nn_ids = tree.query(mesh_points, k=1)
            within = min_dist < threshold

            # 关键：用最近邻体素的 (i,j,k) 三元组索引到 pet_suvr，得到一维标量序列
            ijk_near = voxel_idx[nn_ids[within]]
            local_field = np.zeros(mesh_points.shape[0], dtype=np.float32)
            local_field[within] = suvr_field[within] = pet_suvr[ijk_near[:,0], ijk_near[:,1], ijk_near[:,2]]
            if merge_method == 'max':
                # suvr_field[within] = np.maximum(suvr_field[within], local_field[within])
                local_mean = np.mean(local_field[within])
                # print(local_mean)
                if local_mean > 1.1:
                    suvr_field[within] = local_mean
                else:
                    suvr_field[within] = 0.0
            elif merge_method == 'mean':
                suvr_field[within] = (suvr_field[within] + local_field[within])/2.0
    return suvr_field
    
def compute_suvr(pet_image, ref_mask_file):
    pet_data = pet_image.get_fdata()
    ref_mask_data, ref_mask_affine = load_nifti(ref_mask_file)
    # Mean uptake in reference region
    ref_mean = pet_data[ref_mask_data > 0].mean()
    print(ref_mean)
    # Calculate SUVR
    pet_suvr = pet_data / ref_mean
    pet_suvr_img = nib.Nifti1Image(pet_suvr, pet_image.affine)
    return pet_suvr
    


if __name__ == '__main__':
    field_name = 'SUVR'
    # =============================================================================================
    #                 Step 1: Load PET image
    # =============================================================================================
    pet_image = smooth_img("rAligned_PET.nii", fwhm=3) # fwhm: full width at half maximum (adjustable)
    pet_data = pet_image.get_fdata()
    
    # =============================================================================================
    #                 Step 2: Interpolate PET to FEM mesh nodes
    # =============================================================================================
    mesh = pv.read('whole_brain_orientation.vtk')
    
    ref_mask_file = os.path.join(os.getcwd(), 'Ref_masks', 'ref_mask.nii')
    # roi_mask_file = os.path.join(os.getcwd(), 'ROI_masks', '0017_Left-Hippocampus.nii')
    roi_mask_file = os.path.join(os.getcwd(), 'ROI_masks', '1030_ctx-lh-superiortemporal.nii')
    roi_masks_file = os.listdir(os.path.join(os.getcwd(), 'ROI_masks'))
    roi_masks_file = [os.path.join(os.getcwd(), 'ROI_masks', f) for f in roi_masks_file]
    pet_suvr = compute_suvr(pet_image, ref_mask_file)
    # pet_field = interpolate_pet_to_mesh(pet_suvr, mesh, threshold = 3, masks=roi_masks_file)
    pet_field = interpolate_pet_to_mesh(pet_suvr, mesh, threshold = 3)

    mesh[field_name] = pet_field
    mesh.save('whole_brain_orientation_scan1.vtk')
    
    
    roi_mask_data, roi_mask_affine = load_nifti(roi_mask_file)
    print(np.median(pet_suvr[roi_mask_data > 0]))
