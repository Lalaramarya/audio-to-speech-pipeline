from audio_transcription.constants import CONFIG_NAME, CLEAN_AUDIO_PATH, LANGUAGE


class AudioTranscription:

    LOCAL_PATH = None

    @staticmethod
    def get_instance(data_processor, gcs_instance, audio_commons):
        return AudioTranscription(data_processor, gcs_instance, audio_commons)

    def __init__(self, data_processor, gcs_instance, audio_commons):
        self.data_processor = data_processor
        self.gcs_instance = gcs_instance
        self.transcription_clients = audio_commons.get('transcription_clients')
        self.audio_transcription_config = None

    def process(self, **kwargs):

        self.audio_transcription_config = self.data_processor.config_dict.get(
            CONFIG_NAME)

        source = kwargs.get('audio_source')
        audio_id = kwargs.get('audio_id')
        stt_api = kwargs.get("speech_to_text_client")

        language = self.audio_transcription_config.get(LANGUAGE)
        remote_path_of_dir = self.audio_transcription_config.get(
            CLEAN_AUDIO_PATH)
        remote_dir_path_for_given_audio_id = f'{remote_path_of_dir}/{source}/{audio_id}/clean/'
        remote_stt_output_path = self.audio_transcription_config.get(
            'remote_stt_audio_file_path')

        transcription_client = self.transcription_clients[stt_api]

        all_path = self.gcs_instance.list_blobs_in_a_path(remote_dir_path_for_given_audio_id)

        local_file_path = self.call_stt(all_path, language, transcription_client)

        local_dir_path = self.get_local_dir_path(local_file_path)

        self.move_to_gcs(local_dir_path, remote_stt_output_path)

        self.delete_audio_id(remote_dir_path_for_given_audio_id)


    def delete_audio_id(self,remote_dir_path_for_given_audio_id):
        self.gcs_instance.delete_object(remote_dir_path_for_given_audio_id)

    def move_to_gcs(self, local_path, remote_stt_output_path):
        self.gcs_instance.upload_to_gcs(local_path, remote_stt_output_path)

    def save_transcription(self, transcription, output_file_path):
        with open(output_file_path, "w") as f:
            f.write(transcription)

    def call_stt(self, all_path, language, transcription_client):
        
        for file_path in all_path:
            LOCAL_PATH = f"/tmp/{file_path.name}"
            transcription_file_name = LOCAL_PATH.replace('.wav','.txt')
            self.gcs_instance.download_to_local(
                file_path.name,LOCAL_PATH, False)
            
            transcript = transcription_client.generate_transcription(
                language, LOCAL_PATH)

            self.save_transcription(transcript, transcription_file_name)
        return LOCAL_PATH

    def get_local_dir_path(self,local_file_path):
        path_array = local_file_path.split('/')
        path_array.pop()
        return '/'.join(path_array)