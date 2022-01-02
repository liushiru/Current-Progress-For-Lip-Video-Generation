## Lip Video Generation

Currently the talking face generation part is done by [Wav2Lip](https://github.com/Rudrabha/Wav2Lip)
It is the project that can generate the best Lip Video up until 2021 Aug. This github is very friendly and the performance can be reproduced easily.

Another possible project is Talking Face Generation by [Adversarially Disentangled Audio-Visual Representation (ADAR)](https://github.com/Hangz-nju-cuhk/Talking-Face-Generation-DAVS) 
The video produce by this project is not as good as Wav2Lip. 

Here’s the comparison videos: 

[Wav2Lip Video](https://drive.google.com/file/d/1r7UhP5jfI1YIJ_HKUSxdf6LLZ2KfvK1t/view?usp=sharing)

[ADAR Video](https://drive.google.com/file/d/1r7UhP5jfI1YIJ_HKUSxdf6LLZ2KfvK1t/view?usp=sharing)



## Phoneme Detection

To identify the phoneme pronounced by the L2 learners as well as the timestamp of each phoneme, one needs to utilize the models and results from Weiwei’s project.
1.	[Phoneme identification](https://github.com/weiwei-ww/neural_sp/blob/mdd/examples/l2_arctic_vae/s5/run_supervised_kaldi.sh)
2.	[Time identification](https://github.com/weiwei-ww/neural_sp/blob/mdd/examples/l2_arctic_vae/s5/run_l2_forced_alignment.sh)



## Indicative Lip Video Generation
Combining the results from the above two points, [indicative lip videos](https://drive.google.com/file/d/1_kszRFTXMxO0hrT5yz2pNnygkRvqSm9Z/view?usp=sharing) can be generated.
The scripts used to do the combination are `gen_vid.sh` and `mark_video.py`. 

More videos coule be found [here](https://drive.google.com/drive/folders/1GbLuG65DxAUDy6n1iCgweNvCX6Fj5xgB?usp=sharing)
