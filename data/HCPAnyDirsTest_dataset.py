import os
import torch
import numpy as np
import pickle
from data.base_dataset import BaseDataset
from data_loading.HCPAnyDirs_sample_loader import HCPAnyDirsSampleLoader
from processing.Nonorm_processing import NonormProcessing


class HCPAnyDirsTestDataset(BaseDataset):  # Can only run sequentially (batch size 1)

    def __init__(self, opt):
        """
        Initialize this dataset class.
        """
        BaseDataset.__init__(self, opt)

        hcp_split_path = os.path.join(self.root, 'HCP_list_split_80_20.pickle')
        if not os.path.exists(hcp_split_path):
            raise IOError(
                "hcp splited list path, {}, could not be resolved".format(hcp_split_path)
            )
            exit(0)
        
        with open(hcp_split_path, 'rb') as handle:
            sub_list = pickle.load(handle)
            if opt.isTrain:
                self.sample_list = sub_list['train']
            else:
                self.sample_list = sub_list['test']

        # debugging uncomment it
        # self.sample_list = [self.sample_list[0]]

        self.sample_loader = HCPAnyDirsSampleLoader(root = self.root, isTrain = self.opt.isTrain)
        self.padded_dirs = 6
        self.processing = NonormProcessing(norm = opt.data_norm, bounding = opt.bounding
                        , crop = True, isTrain = opt.isTrain, patch_shape = opt.patch_shape , patch_overlap = opt.patch_overlap)


    def modify_commandline_options(parser, is_train):
        """Add new dataset-specific options, and rewrite default values for existing options.

        Parameters:
            parser          -- original option parser
            is_train (bool) -- whether training phase or test phase. You can use this flag to add training-specific or test-specific options.

        Returns:
            the modified parser.
        """
      
        return parser


    def __len__(self):
        """Return the total number of images in the dataset."""

        return len(self.sample_list)


    def __getitem__(self, index):
        """Return a data point and its metadata information.

        Parameters:
            index - - a random integer for data indexing

        Returns:
            a dictionary of data with their names. It ususally contains the data itself and its metadata information.
        """
        uni = self.sample_list[index]
        # debug uncomment it
        # uni = '111312'
        sample = self.sample_loader.load_sample(uni, 6)
        self.preprocessing(sample)
        
        dwi_patches = []
        t1_patches = []
        dwi_unnorm_patches = []

        gt_dti = torch.from_numpy(sample.gt_dti)
        wm_mask = torch.from_numpy(sample.wm_mask)
        grad = torch.from_numpy(np.concatenate(([[0.,0.,0.]], sample.grad[...,0:-1]), axis = 0)) # (7, 3)


        for patch_coord in sample.coords_data:
            x_start = patch_coord['x_start']
            x_end = patch_coord['x_end']
            y_start = patch_coord['y_start']
            y_end = patch_coord['y_end']
            z_start = patch_coord['z_start']
            z_end = patch_coord['z_end']

            dwi_patch = torch.from_numpy(sample.dwi[x_start:x_end, y_start:y_end, z_start:z_end])
            t1_patch = torch.from_numpy(sample.t1[x_start:x_end, y_start:y_end, z_start:z_end])
            # dwi_unnorm_patch = torch.from_numpy(sample.dwi_unnorm[x_start:x_end, y_start:y_end, z_start:z_end])

            dwi_patch = dwi_patch.permute(3,0,1,2)
            t1_patch = t1_patch.unsqueeze(0)
            # dwi_unnorm_patch = dwi_unnorm_patch.permute(3,0,1,2)

            dwi_patches.append(dwi_patch)
            t1_patches.append(t1_patch)
            # dwi_unnorm_patches.append(dwi_unnorm_patch)

        dwi_patches = torch.stack(dwi_patches, dim = 0)
        t1_patches = torch.stack(t1_patches, dim = 0)
        # dwi_unnorm_patches = torch.stack(dwi_unnorm_patches, dim = 0)
   
        return {'index': sample.index, 'dwi' : dwi_patches, 't1': t1_patches, 'gt_dti': gt_dti, 'wm_mask': wm_mask
        ,'grad': grad}


    def preprocessing(self, sample):
        self.processing.preprocessing(sample)
        self.preprocessed_sample = sample
        # print(sample.wm_mask.shape)
        

    def postprocessing(self, preds):
        predictions_dict = self.processing.postprocessing(self.preprocessed_sample, preds)

        for key, pred in predictions_dict.items():
            print('shape of post-processed {:}: {:}'.format(key, pred.shape))

        return predictions_dict


    def save_prediction(self, prediction, suffix):
        output_name = os.path.join(self.opt.results_dir, self.opt.name, 
                    self.preprocessed_sample.index + suffix + '.nii.gz')

        self.sample_loader.save_prediction(prediction, self.preprocessed_sample.aff, output_name = output_name)
