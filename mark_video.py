'''
This file includes some function useful for annotating the Lip Video 
Correct Pronunciation is marked with green frame
Wrong Pronunciation is marked with red frame

Canonical phoneme: (the phonemes that are supposed to be pronunced) put to the up left corner
Actual phoneme: (the phonemes that are actually pronunced by the L2 learners) are put to the up right corner
'''

import argparse
import os

import cv2
import math
import json
import subprocess
from pydub import AudioSegment
from pydub.utils import mediainfo
from pathlib import Path


def edit_frame(frame, error_dict):
    # cv2.putText(frame, 'Error Type: ' + error_dict['type'], (5, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 1 )
    # cv2.putText(frame, 'Correct: ' + error_dict['canonical'], (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 1 )
    # cv2.putText(frame, 'Read: ' + error_dict['hyp'], (5, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 1 )
    cv2.putText(frame, error_dict['canonical'] , (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (100,255,0), 1 )
    cv2.putText(frame, error_dict['hyp'], (160, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 1 )


def make_border(frame, correct):
    value = [0, 255, 0] if correct else [0,0,255]
    frame = cv2.copyMakeBorder(frame, 5, 5, 5, 5, cv2.BORDER_CONSTANT, value=value)
    return frame

def edit_audio(audio_path, silence_audio_path, mark_dict):
    sound = AudioSegment.from_file(audio_path, format="wav")
    combined = AudioSegment.empty()
    silence = AudioSegment.silent(duration=1000)
    start = 0
    for i in range(len(mark_dict['start'])):
        end_time = (mark_dict['start'][i] + mark_dict['dur'][i]) * 1000
        combined += sound[start:end_time]
        start = end_time
        combined += silence
    combined += sound[start:]


    combined.export(silence_audio_path, format="mp3")




def edit_video(vid_path, silence_vid_path, aud_path, silence_aud_path, mark_dict, silence):

    mark_dict['start'] = [float(start) for start in mark_dict['start']]
    mark_dict['dur'] = [float(start) for start in mark_dict['dur']]
    # return
    edit_audio(aud_path, silence_aud_path, mark_dict)

    video = cv2.VideoCapture(str(vid_path))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    frameCount = video.get(cv2.CAP_PROP_FRAME_COUNT)
    size = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH))+10, int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))+10)

    videoWriter = cv2.VideoWriter(silence_vid_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, size)

    success, frame = video.read()
    frame_num = 1
    print("====num wrong phone: {}".format(len(mark_dict['start'])))
    for i in range(len(mark_dict['start'])):
        phone_start_time = mark_dict['start'][i]
        phone_end_time = phone_start_time + mark_dict['dur'][i]

        start_frame = math.floor(fps * phone_start_time) + 1
        end_frame = math.ceil(fps * phone_end_time) + 1

        error_dict = {}
        error_dict['type'] = "S" if "*" not in mark_dict['hyp'] else "D"
        error_dict['canonical'] = mark_dict['canonical'][i]
        error_dict['hyp'] = mark_dict['hyp'][i]

        while success and frame_num <= end_frame:
            if start_frame <= frame_num <= end_frame:
                edit_frame(frame, error_dict)
                frame = make_border(frame, False)
            else:
                frame = make_border(frame, True)

            videoWriter.write(frame)
            # cv2.imshow("new video", frame)
            cv2.waitKey(int(1000 / int(fps)))

            if silence and frame_num == end_frame:
                for f in range(fps):
                    videoWriter.write(frame)
                    # cv2.imshow("new video", frame)
                    cv2.waitKey(int(1000 / int(fps)))

            success, frame = video.read()
            frame_num += 1

    while success:
        frame = make_border(frame, True)
        videoWriter.write(frame)
        cv2.waitKey(int(1000 / int(fps)))
        success, frame = video.read()
        frame_num += 1

    video.release()
    cv2.destroyAllWindows()

def get_id(video_path):
    name = video_path.stem
    l = name.split("_")
    id = l[0].lower() + '_' + l[-1]
    return id



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Mark video frames using wav2lip and mdd results',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-video', help='path to the video file', required=True)
    parser.add_argument('-audio', help='path to the audio file', required=True)
    parser.add_argument('-dict', help='path to the forced mdd dictionary', required=True)
    args = parser.parse_args()

    video_path = Path(args.video)
    id = get_id(video_path)
    audio_path = Path(args.audio)
    dict_path = Path(args.dict)


    silence_audio_path = os.getcwd() + '/temp/' + id + "_with_silence.mp3"
    border_video_path = os.getcwd() + '/temp/' + id + "_mark_no_silence.mp4"
    silence_video_path = os.getcwd() + '/temp/' + id + "_mark_silence.mp4"

    combine_video_silence = '/home/l/liushiru/nsp/mark_videos/' + id + '_combine_with_silence.mp4'
    combine_video_no_silence = '/home/l/liushiru/nsp/mark_videos/' + id + '_combine_no_silence.mp4'

    with open(dict_path) as f:
        mark_dict = json.load(f)

    dict = mark_dict[id]
    edit_video(video_path, border_video_path, audio_path, silence_audio_path, dict, False)
    edit_video(video_path, silence_video_path, audio_path, silence_audio_path, dict, True)

    command = 'ffmpeg -y -i {} -i {} -strict -2 -q:v 1 {}'.format(silence_audio_path, silence_video_path, combine_video_silence)
    subprocess.call(command, shell=True)

    command = 'ffmpeg -y -i {} -i {} -strict -2 -q:v 1 {}'.format(audio_path, border_video_path, combine_video_no_silence)
    subprocess.call(command, shell=True)

    print("=======================inspect video {} =======================".format(id))
    print("num wrong phone: ", len(dict['start']))
    print(dict['start'])
    print(dict['dur'])
#    print("raw sample rate", mediainfo(str(audio_path)))
    raw_audio = AudioSegment.from_file(audio_path, format="wav")
    print("raw audio length: ", len(raw_audio)/1000)
    

    print(silence_audio_path)
    silence_audio = AudioSegment.from_file(silence_audio_path, format="mp3")
    print("silence audio length: ", len(silence_audio) / 1000)

    border_video = cv2.VideoCapture(border_video_path)
    fps = int(border_video.get(cv2.CAP_PROP_FPS))
    frameCount = border_video.get(cv2.CAP_PROP_FRAME_COUNT)
    print('border video length: ', (frameCount/fps))


    silence_video = cv2.VideoCapture(silence_video_path)
    fps = int(silence_video.get(cv2.CAP_PROP_FPS))
    frameCount = silence_video.get(cv2.CAP_PROP_FRAME_COUNT)
    print('silence video length: ', (frameCount/fps))
    print()

    # video = cv2.VideoCapture('trans.mp4')
    # fps = int(video.get(cv2.CAP_PROP_FPS))
    # frameCount = video.get(cv2.CAP_PROP_FRAME_COUNT)
    # print('trans_vid_dur: ', (frameCount/fps))
