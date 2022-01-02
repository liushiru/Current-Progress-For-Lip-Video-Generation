# Need to utilize the results from https://github.com/weiwei-ww/neural_sp/blob/mdd/examples/l2_arctic_vae/s5/run_l2_forced_alignment.sh
# and the model trained from Weiwei's Project neural_sp: https://github.com/weiwei-ww/neural_sp


export WD=$PWD/..
export WAV2LIP_ROOT=$WD/Wav2Lip
export NEURALSP_ROOT=$WD/neural_sp
export L2_ROOT=$NEURALSP_ROOT/examples/l2_arctic_vae

result_dir=$L2_ROOT/results


model_name="20210706_04_41_08"   

start_stage=0
end_stage=2

readarray -t test_spk_list < $L2_ROOT/s5/conf/l2_arctic/test_spk.list
test_spk_list=(${test_spk_list[2]})
num_spk=${#test_spk_list[@]}

if [ $start_stage -le 0 ] && [ $end_stage -ge 0 ]; then
	# copy test audio
	for (( i=0; i<num_spk; i++));
	do
		curr_spk=${test_spk_list[$i]}
		#echo $curr_spk
		mkdir -p $WD/audios/
		cp -r $NEURALSP_ROOT/examples/l2_arctic_vae/original_l2_arctic/$curr_spk/wav $WD/audios/$curr_spk
	done
fi

# step 1 generate video
if [ $start_stage -le 1 ] && [ $end_stage -ge 1 ]; then
	for (( i=0; i<num_spk; i++));
	do
		curr_spk=${test_spk_list[$i]}
		audio_list=($WD/audios/$curr_spk/*)
		
		num_aud = ${#audio_list[@]}
		echo $num_audio
		mkdir -p $WD/videos/$curr_spk
		for (( j=7; j<8; j++));
		do
			curr_audio=${audio_list[$j]}
			echo $curr_spk
			echo $curr_audio
			echo "start generating"
			file="$(basename -- $curr_audio)"
			aud_name="${file%.wav}"
			out_file="${curr_spk}_${aud_name}.mp4"
			cd $WAV2LIP_ROOT
			python $WAV2LIP_ROOT/inference.py \
				--checkpoint_path $WAV2LIP_ROOT/checkpoints/wav2lip_gan.pth \
				--face $WAV2LIP_ROOT/faces/female.jpg \
				--audio $curr_audio \
				--outfile $WD/videos/$curr_spk/$out_file \
				--fps 60
			

			cd $WD
			mkdir -p $WD/temp/
			echo "start marking"
			python $WD/script/mark_video.py \
				-video $WD/videos/$curr_spk/$out_file \
				-audio $curr_audio \
				-dict $WD/mark_videos/mark_dict.json
		done
	done
fi



if [ $start_stage -le 2 ] && [ $end_stage -ge 2 ]; then
	model_dir=$(ls -d -v $result_dir/$model_name/*/*)

	# get the best epoch
	epoch=$(ls -d -v $model_dir/decode_test_ep* | tail -n 1 | sed -e "s:^.*ep\([0-9]*\).*$:\1:")
	echo "Evaluate epoch $epoch."

	for set_name in test; do
		echo "-----${set_name} set-----"
		output_dir=$(ls -d $model_dir/decode_${set_name}_ep${epoch}*)
		alignment_result_path=$output_dir/alignment.txt
		canonical_path=$L2_ROOT/processed_data_l2_arctic_original/$set_name/canonical
		forced_alignment_path=$L2_ROOT/processed_data_l2_arctic_forced_alignment/$set_name/alignment_phoneme_id.txt

		echo $output_dir
		python $L2_ROOT/s5/local/mark_mdd.py \
			-canonical $canonical_path \
			-alignment $alignment_result_path \
			-forced_alignment $forced_alignment_path
	done
fi


