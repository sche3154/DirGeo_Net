set -ex
python3 /home/sheng/Diffusion/miccai_2024/PPMIAnyDirs_train.py \
--dataroot /home/sheng/Diffusion/PPMI \
--name PPMIDirGeo_100 \
--model DirGeo \
--net DirGeo \
--input_nc 7  \
--output_nc 6  \
--lr 0.0001 \
--dataset_mode PPMIAnyDirs \
--padded_dirs 6 \
--data_norm z_scoreV2 \
--num_threads 0 \
--batch_size 1 \
--input_batch_sizes 15 \
--patch_shape 64 \
--patch_overlap 32 \
--bounding \
--n_epochs 50 \
--n_epochs_decay 0 \
--display_freq 1 \
--save_epoch_freq 10 \
--gpu_ids 1