set -ex
python3 /home/sheng/Diffusion/miccai_2024/AnyDirs_test.py \
--dataroot /home/sheng/Diffusion/data \
--name HCPDirGeo_100 \
--model DirGeo \
--epoch latest \
--net DirGeo \
--input_nc 7  \
--output_nc 6  \
--dataset_mode HCPAnyDirsTest \
--data_norm z_scoreV2 \
--serial_batches \
--batch_size 1 \
--bounding \
--patch_shape 64 \
--patch_overlap 32 \
--input_batch_sizes 30 \
--eval \
--num_threads 0 \
--num_test 20 \
--save_prediction 1 \
--gpu_ids 0