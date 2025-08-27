import numpy as np
import whisper
import librosa
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import soundfile as sf

# 1. 加载Whisper模型
model = whisper.load_model("base")  # 也可以选择 "medium" 或 "large"

# 2. 音频路径
audio_path = "multi_speaker_audio.wav"

# 3. 转录音频并获取片段
result = model.transcribe(audio_path, verbose=True)
segments = result["segments"]  # 每个片段包含 start, end, text

# 4. 提取语音特征（MFCC）
def extract_features(wav_path, segment):
    y, sr = librosa.load(wav_path, sr=None)
    start_frame = int(segment["start"] * sr)
    end_frame = int(segment["end"] * sr)
    segment_audio = y[start_frame:end_frame]
    
    # 提取MFCC特征
    mfcc = librosa.feature.mfcc(y=segment_audio, sr=sr, n_mfcc=13)
    return mfcc.mean(axis=1)  # 取均值作为特征向量

# 5. 提取所有片段的特征
features = []
for seg in segments:
    feature = extract_features(audio_path, seg)
    features.append(feature)

features = np.array(features)
features = StandardScaler().fit_transform(features)  # 特征标准化

# 6. 说话人聚类（假设已知说话人数量为2）
num_speakers = 2
kmeans = KMeans(n_clusters=num_speakers, random_state=42)
speaker_labels = kmeans.fit_predict(features)

# 7. 输出结果
for i, seg in enumerate(segments):
    print(f"说话人: S{speaker_labels[i]+1} | 时间: {seg['start']:.1f}-{seg['end']:.1f}s | 文本: {seg['text']}")
