import streamlit as st
import soundfile as sf
import pyloudnorm as pyln
import sounddevice as sd 
from scipy.io.wavfile import write
import numpy as np
from tempfile import NamedTemporaryFile
import pysepm
import speechmetrics

window_length = 3 

def record(sr=16000, channels=1, duration=window_length):
	recording = sd.rec(int(duration * sr), samplerate=sr, channels=channels).reshape(-1)
	sd.wait()
	write('temp.wav', sr, recording)

st.header("Audio and Speech Evaluation")
st.set_option('deprecation.showfileUploaderEncoding', False)


task = st.sidebar.selectbox("Select task:", ["Intelligibility", "Loudness", "Naturalness", "Quality"])


if task == "Intelligibility":

	st.subheader("Speech Intelligibility Evaluation")

	buffer1 = st.file_uploader(label="Clean file", type=["ogg", "wav"])
	temp_file1 = NamedTemporaryFile(delete=False)
	
	if buffer1:
		temp_file1.write(buffer1.getvalue())

		buffer2 = st.file_uploader(label="Processed file", type=["ogg", "wav"])
		temp_file2 = NamedTemporaryFile(delete=False)
		
		if buffer2:
			temp_file2.write(buffer2.getvalue())


			clean_speech, fs = sf.read(temp_file1.name)
			noisy_speech, fs = sf.read(temp_file2.name)

			model = st.sidebar.selectbox("Select measure:", ["STOI", "CSII", "NCM"])

			if model == "STOI":

				st.subheader("STOI")

				st.write(pysepm.stoi(clean_speech, noisy_speech, fs))

			if model == "NCM":

				st.subheader("NCM")

				st.write(pysepm.ncm(clean_speech, noisy_speech, fs))


			if model == "CSII":

				st.subheader("CSII")

				st.write(pysepm.csii(clean_speech, noisy_speech, fs))


elif task == "Loudness":

	st.subheader("Speech Loudness Evaluation")

	type_metric = st.sidebar.selectbox("Select measure type:", ["Subjective measures", "Objective measures"])

	if type_metric == "Objective measures":

		st.markdown("An implementation of [ITU-R BS.1770-4](https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.1770-4-201510-I!!PDF-E.pdf) recommendation for objective loudness assessment.")
		
		st.sidebar.markdown("---")
		st.sidebar.markdown("**Select data source:**")

		if st.sidebar.button("Record sample"):

			record()
			data, rate = sf.read("temp.wav") # load audio (with shape (samples, channels))
			meter = pyln.Meter(rate) # create BS.1770 meter
			loudness = np.round(meter.integrated_loudness(data), 2) # measure loudness

			st.write("Estimated loudness: ", loudness, " LKFS")
			st.write("""This designation signifies: Loudness, K-weighted, relative to nominal full scale. The LKFS unit is equivalent to a decibel in that an increase in the level of a signal by 1 dB will cause the loudness reading to increase by 1 LKFS.""")

			st.audio("temp.wav")


		buffer = st.sidebar.file_uploader(label="Upload an audio file", type=["ogg", "wav"])
		temp_file = NamedTemporaryFile(delete=False)
		
		if buffer:
			temp_file.write(buffer.getvalue())
			
			data, rate = sf.read(temp_file.name) # load audio (with shape (samples, channels))
			meter = pyln.Meter(rate) # create BS.1770 meter
			loudness = np.round(meter.integrated_loudness(data), 2) # measure loudness

			st.write("Estimated loudness: ", loudness, " LKFS")
			st.write("""This designation signifies: Loudness, K-weighted, relative to nominal full scale. The LKFS unit is equivalent to a decibel in that an increase in the level of a signal by 1 dB will cause the loudness reading to increase by 1 LKFS.""")

			st.audio(temp_file.name)

	elif type_metric == "Subjective measures":

		st.write("None")

elif task == "Naturalness":
	
	st.subheader("Speech Naturalness Evaluation")

	st.write("To be implemented")

else:

	st.subheader("Speech Quality Evaluation")

	type_metric = st.sidebar.selectbox("Select measure type:", ["Subjective measures", "Objective measures"])

	if type_metric == "Objective measures":
		intru = st.sidebar.selectbox("Select intrusiveness:", ["Intrusive", "Non-intrusive"])

		if intru == "Intrusive":

			buffer1 = st.file_uploader(label="Clean file", type=["ogg", "wav"])
			temp_file1 = NamedTemporaryFile(delete=False)
			
			if buffer1:
				temp_file1.write(buffer1.getvalue())

				buffer2 = st.file_uploader(label="Processed file", type=["ogg", "wav"])
				temp_file2 = NamedTemporaryFile(delete=False)
				
				if buffer2:
					temp_file2.write(buffer2.getvalue())


					clean_speech, fs = sf.read(temp_file1.name)
					noisy_speech, fs = sf.read(temp_file2.name)


					domain = st.sidebar.selectbox("Select domain:", ["Time domain", "Frequency domain", "Perceptual domain"])

					if domain == "Time domain":

						model = st.sidebar.selectbox("Select measure:", ["SNRseg", "Cepstrum distance"])

						if model == "SNRseg":

							st.subheader("SNRseg")

							st.write(pysepm.SNRseg(clean_speech, noisy_speech, fs))
						
						if model == "Cepstrum distance":

							st.subheader("Cepstrum distance")

							st.write(pysepm.cepstrum_distance(clean_speech, noisy_speech, fs))

					elif domain == "Frequency domain":

						model = st.sidebar.selectbox("Select measure:", ["fwSRNseg", "WSS", "LLR"])

						if model == "WSS":

							st.subheader("WSS")

							st.write(pysepm.wss(clean_speech, noisy_speech, fs))

						if model == "fwSRNseg":

							st.subheader("fwSRNseg")

							st.write(pysepm.fwSNRseg(clean_speech, noisy_speech, fs))

						if model == "LLR":

							st.subheader("LLR")

							st.write(pysepm.llr(clean_speech, noisy_speech, fs))

					elif domain == "Perceptual domain":

						model = st.sidebar.selectbox("Select measure:", ["PESQ"])

						if model == "PESQ":

							st.sidebar.write("Scale: Higher is better. 0 = very bad, 5 = very good")

							st.subheader("PESQ")

							st.write(list(pysepm.pesq(clean_speech, noisy_speech, fs))[1])

		elif intru == "Non-intrusive":

			model = st.sidebar.selectbox("Select measure:", ["MOSNet", "SRMR"])

			if model == "MOSNet":

				metrics = speechmetrics.load('absolute', window_length)

				st.sidebar.markdown("---")
				st.sidebar.markdown("**Select data source:**")

				if st.sidebar.button("Record sample"):

					record()
					scores = metrics("temp.wav")
					st.write(scores["mosnet"][0])
					st.audio("temp.wav")


				buffer = st.sidebar.file_uploader(label="Upload an audio file", type=["ogg", "wav"])
				temp_file = NamedTemporaryFile(delete=False)
				
				if buffer:
					temp_file.write(buffer.getvalue())
					scores = metrics(temp_file.name)
					st.write(scores["mosnet"][0])

					st.audio(temp_file.name)


			if model == "SRMR":

				metrics = speechmetrics.load('absolute', window_length)

				st.sidebar.markdown("---")
				st.sidebar.markdown("**Select data source:**")

				if st.sidebar.button("Record sample"):

					record()
					scores = metrics("temp.wav")
					st.write(scores["srmr"][0])
					st.audio("temp.wav")


				buffer = st.sidebar.file_uploader(label="Upload an audio file", type=["ogg", "wav"])
				temp_file = NamedTemporaryFile(delete=False)
				
				if buffer:
					temp_file.write(buffer.getvalue())
					scores = metrics(temp_file.name)
					st.write(scores["srmr"][0])

					st.audio(temp_file.name)
