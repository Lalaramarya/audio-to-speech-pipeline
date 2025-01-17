import json
import unittest
from unittest import mock

from ekstep_data_pipelines.common.dao.catalogue_dao import CatalogueDao


class CatalogueTests(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test_get_utterances(self, mock_postgres_client):
        mock_postgres_client.execute_query.return_value = [
            (
                '[{"name": "190_Bani_Rahengi_Kitaabe_dr__sunita_rani_ghosh.wav", '
                '"duration": "13.38", "snr_value": 38.432806, "status": "Clean"}]',
            )
        ]
        catalogueDao = CatalogueDao(mock_postgres_client)
        audio_id = "2020"
        actual_utterances = catalogueDao.get_utterances(audio_id)
        expected_utterances = [
            {
                "name": "190_Bani_Rahengi_Kitaabe_dr__sunita_rani_ghosh.wav",
                "duration": "13.38",
                "snr_value": 38.432806,
                "status": "Clean",
            }
        ]
        self.assertEqual(expected_utterances, actual_utterances)

    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test_get_utterances_as_empty_if_no_records(self, mock_postgres_client):
        mock_postgres_client.execute_query.return_value = []
        catalogueDao = CatalogueDao(mock_postgres_client)
        audio_id = "2020"
        actual_utterances = catalogueDao.get_utterances(audio_id)
        expected_utterances = []
        self.assertEqual(expected_utterances, actual_utterances)

    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test_update_utterances(self, mock_postgres_client):
        mock_postgres_client.execute_update.return_value = None
        catalogueDao = CatalogueDao(mock_postgres_client)
        audio_id = "2020"
        utterances = [
            {
                "name": "190_Bani_Rahengi_Kitaabe_dr__sunita_rani_ghosh.wav",
                "duration": "13.38",
                "snr_value": 38.432806,
                "status": "Clean",
            }
        ]

        rows_updated = catalogueDao.update_utterances(audio_id, utterances)
        args = mock_postgres_client.execute_update.call_args_list
        called_with_params = {
            "utterances": json.dumps(utterances),
            "audio_id": audio_id,
        }
        called_with_sql = (
            "update media_metadata_staging set utterances_files_list "
            "= :utterances where audio_id = :audio_id"
        )
        self.assertEqual(rows_updated, True)
        self.assertEqual(called_with_sql, args[0][0][0])
        self.assertEqual(called_with_params, args[0][1])

    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test_utterance_by_name(self, mock_postgres_client):
        catalogueDao = CatalogueDao(mock_postgres_client)
        name = "190_Bani_Rahengi_Kitaabe_dr__sunita_rani_ghosh.wav"
        utterances = [
            {
                "name": "190_Bani_Rahengi_Kitaabe_dr__sunita_rani_ghosh.wav",
                "duration": "13.38",
                "snr_value": 38.432806,
                "status": "Clean",
            },
            {
                "name": "91_Bani_Rahengi_Kitaabe_dr__sunita_rani_ghosh.wav",
                "duration": "3.27",
                "snr_value": 37.0,
                "status": "Clean",
            },
        ]
        utterance = catalogueDao.find_utterance_by_name(utterances, name)
        self.assertEqual(
            {
                "name": "190_Bani_Rahengi_Kitaabe_dr__sunita_rani_ghosh.wav",
                "duration": "13.38",
                "snr_value": 38.432806,
                "status": "Clean",
            },
            utterance,
        )

    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test_utterance_by_name_return_None_if_not_found(self, mock_postgres_client):
        catalogueDao = CatalogueDao(mock_postgres_client)
        name = "not_exists.wav"
        utterances = [
            {
                "name": "190_Bani_Rahengi_Kitaabe_dr__sunita_rani_ghosh.wav",
                "duration": "13.38",
                "snr_value": 38.432806,
                "status": "Clean",
            },
            {
                "name": "91_Bani_Rahengi_Kitaabe_dr__sunita_rani_ghosh.wav",
                "duration": "3.27",
                "snr_value": 37.0,
                "status": "Clean",
            },
        ]

        utterance = catalogueDao.find_utterance_by_name(utterances, name)
        self.assertEqual(None, utterance)

    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test_update_utterance_status(self, mock_postgres_client):
        catalogueDao = CatalogueDao(mock_postgres_client)
        audio_id = "2020"
        utterance = {
            "name": "190_Bani_Rahengi_Kitaabe_dr__sunita_rani_ghosh.wav",
            "duration": "13.38",
            "is_transcribed": True,
            "stt_api": 'google',
            "snr_value": 38.432806,
            "status": "Clean",
            "reason": "stt error",
        }

        rows_updated = catalogueDao.update_utterance_status(audio_id, utterance)

        args = mock_postgres_client.execute_update.call_args_list
        called_with_query = (
            "update media_speaker_mapping set status = :status, fail_reason = :reason,is_transcribed = (SELECT case when is_transcribed = TRUE then true else :is_transcribed end as e from unnest(ARRAY[is_transcribed])),stt_api_used =(select array_agg(distinct e) from unnest(stt_api_used || ARRAY[:stt_api_used]) e) where audio_id = :audio_id and clipped_utterance_file_name = :name"
        )

        called_with_args = {'status': 'Clean', 'is_transcribed': True, 'stt_api_used': 'google', 'reason': 'stt error',
                            'audio_id': '2020', 'name': '190_Bani_Rahengi_Kitaabe_dr__sunita_rani_ghosh.wav'}
        print("**********************", called_with_args)
        print("*********************", args[0][1])
        self.assertEqual(True, rows_updated)
        self.assertEqual(called_with_query, args[0][0][0])
        self.assertEqual(called_with_args, args[0][1])

    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test_get_utterances_by_source(self, mock_postgres_client):
        source = "test_source"
        status = "Clean"
        language = "hindi"
        data_set = "test"
        # speaker_id, clipped_utterance_file_name, clipped_utterance_duration, audio_id, snr
        expected_utterances = [
            (1, "file_1.wav", "10", "2010123", 16),
            (2, "file_2.wav", "11", "2010124", 17),
            (3, "file_3.wav", "12", "2010125", 18),
            (4, "file_4.wav", "13", "2010126", 19),
        ]
        called_with_sql = (
            "select speaker_id, clipped_utterance_file_name, clipped_utterance_duration, "
            "audio_id, snr "
            "from media_speaker_mapping "
            "where audio_id in "
            "(select audio_id from media_metadata_staging "
            'where "source" = :source and "language" = :language and (data_set_used_for IS NULL or data_set_used_for = :data_set)) '
            "and status = :status "
            "and staged_for_transcription = false "
            "and clipped_utterance_duration >= 0.5 and clipped_utterance_duration <= 15"
        )
        mock_postgres_client.execute_query.return_value = expected_utterances
        catalogueDao = CatalogueDao(mock_postgres_client)
        args = mock_postgres_client.execute_query.call_args_list
        utterances = catalogueDao.get_utterances_by_source(source, status, language, data_set)
        self.assertEqual(utterances, expected_utterances)
        self.assertEqual(called_with_sql, args[0][0][0])

    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test__should_update_utterance_staged_for_transcription(
            self, mock_postgres_client
    ):
        mock_postgres_client.execute_batch.return_value = 2
        utterances = [
            (1, "file_1.wav", "10", 2010123, 16),
            (2, "file_2.wav", "11", 2010124, 16),
        ]
        catalogueDao = CatalogueDao(mock_postgres_client)
        catalogueDao.update_utterances_staged_for_transcription(
            utterances, "test_source", "hindi", "test"
        )
        called_with_query = (
            "update media_speaker_mapping set staged_for_transcription = true,"
            "data_type = :data_set "
            "where audio_id in (select audio_id from media_metadata_staging "
            "where \"source\" = :source and \"language\" = :language) and clipped_utterance_file_name in ('file_1.wav',"
            "'file_2.wav')"
        )

        called_with_args = {"source": "test_source", "language": "hindi", "data_set": "test"}
        args = mock_postgres_client.execute_update.call_args
        self.assertEqual(called_with_query, args[0][0])
        self.assertEqual(called_with_args, args[1])

    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test__should_update_utterance_staged_for_transcription_empty_list(
            self, mock_postgres_client
    ):
        mock_postgres_client.execute_update.return_value = 2
        utterances = []
        catalogueDao = CatalogueDao(mock_postgres_client)
        catalogueDao.update_utterances_staged_for_transcription(
            utterances, "test_source", "hindi", "test"
        )
        args = mock_postgres_client.execute_update.call_args
        self.assertEqual(None, args)

    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test__should_return_a_unique_id(self, mock_postgres_client):
        mock_postgres_client.execute_query.return_value = [[231]]
        args = mock_postgres_client.execute_query.call_args_list

        catalogueDao = CatalogueDao(mock_postgres_client)
        actul_value = catalogueDao.get_unique_id()

        self.assertEqual(actul_value, 231)

        self.assertEqual("SELECT nextval('audio_id_seq');", args[0][0][0])

    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test__should_check_in_db_file_present_or_not(self, mock_postgres_client):
        mock_postgres_client.execute_query.return_value = [[True]]
        args = mock_postgres_client.execute_query.call_args_list
        calling_args = {"file_name": "test_file", "hash_code": "dummy_hash_code"}

        catalogueDao = CatalogueDao(mock_postgres_client)
        actul_value = catalogueDao.check_file_exist_in_db(
            "test_file", "dummy_hash_code"
        )

        self.assertEqual(actul_value, True)

        self.assertEqual(
            "select exists(select 1 from media_metadata_staging where raw_file_name="
            " :file_name or media_hash_code = :hash_code);",
            args[0][0][0],
        )

        self.assertEqual(calling_args, args[0][1])

    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test__should_update_utterance_speaker(self, mock_postgres_client):
        mock_postgres_client.execute_update.return_value = 2
        utterances = ["file_1.wav", "file_2.wav"]
        speaker_name = "xyz"
        catalogueDao = CatalogueDao(mock_postgres_client)
        catalogueDao.update_utterance_speaker(utterances, speaker_name, 0)
        called_with_query = (
            "update media_speaker_mapping set "
            "speaker_id=(select speaker_id from speaker where speaker_name=:speaker_name limit 1) "
            ", was_noise=:was_noise "
            "where clipped_utterance_file_name in ('file_1.wav','file_2.wav')"
        )
        called_with_args = {"speaker_name": speaker_name, "was_noise": 0}
        args = mock_postgres_client.execute_update.call_args
        self.assertEqual(called_with_query, args[0][0])
        self.assertEqual(called_with_args, args[1])

    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test__should_insert_speakers(self, mock_postgres_client):
        mock_postgres_client.execute_update.return_value = 2
        catalogueDao = CatalogueDao(mock_postgres_client)
        catalogueDao.insert_speaker("test_source", "test_speaker")
        called_with_query = (
            "insert into speaker (source, speaker_name) values (:source, :speaker_name)"
        )
        called_with_args = {"source": "test_source", "speaker_name": "test_speaker"}
        args = mock_postgres_client.execute_update.call_args
        self.assertEqual(called_with_query, args[0][0])
        self.assertEqual(called_with_args, args[1])

    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test_get_utterance_details_by_source(self, mock_postgres_client):
        source = "test_source"
        language = "Hindi"
        # speaker_id, clipped_utterance_file_name, clipped_utterance_duration, audio_id, snr
        expected_utterances = [
            (
                "sample1.wav",
                13.38,
                38.432806,
                "dummy_speaker_name",
                "dummy_main_source",
                "dummy_collection_source",
                "m",
                'Clean'

            ),
            (
                "sample2.wav",
                15.38,
                40.432806,
                "dummy_speaker_name_2",
                "dummy_main_source_2",
                "dummy_collection_source_2",
                "f",
                'Rejected'
            )
        ]
        called_with_sql = (
            """
            select msp.clipped_utterance_file_name as audio_file_name, 
            msp.clipped_utterance_duration as duration, msp.snr , s.speaker_name, 
            mms.source_url as collection_source , mms.source_website as main_source, msp.speaker_gender as gender,
            msp.audio_id, msp.status
            from media_speaker_mapping msp 
                inner join media_metadata_staging mms 
                    on msp.audio_id = mms.audio_id
            left outer join speaker s 
                    on s.speaker_id = msp.speaker_id 
            where mms.source = :source and mms.language=:language and msp.status in ('Clean','Rejected') and artifact_name is null
            and msp.is_transcribed = :is_transcribed
            limit :count
            """
        )
        call_with_params = {"source": source, "status": "('Clean','Rejected')",
                            "language": language, "count": 2, "is_transcribed": True}

        mock_postgres_client.execute_query.return_value = expected_utterances
        catalogueDao = CatalogueDao(mock_postgres_client)
        args = mock_postgres_client.execute_query.call_args_list
        utterances = catalogueDao.get_utterance_details_by_source(source, language, 2, True, True)
        self.assertEqual(utterances, expected_utterances)
        self.assertEqual(called_with_sql, args[0][0][0])
        self.assertEqual(call_with_params, args[0][1])

    # @unittest.skip
    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test_get_utterance_details_by_source_with_is_transcriped_false(self, mock_postgres_client):
        source = "test_source"
        language = "Hindi"
        # speaker_id, clipped_utterance_file_name, clipped_utterance_duration, audio_id, snr
        expected_utterances = [
            (
                "sample1.wav",
                13.38,
                38.432806,
                "dummy_speaker_name",
                "dummy_main_source",
                "dummy_collection_source",
                "m",
                'Clean'

            ),
            (
                "sample2.wav",
                15.38,
                40.432806,
                "dummy_speaker_name_2",
                "dummy_main_source_2",
                "dummy_collection_source_2",
                "f",
                'Rejected'
            )
        ]
        called_with_sql = (
            """
            select msp.clipped_utterance_file_name as audio_file_name, 
            msp.clipped_utterance_duration as duration, msp.snr , s.speaker_name, 
            mms.source_url as collection_source , mms.source_website as main_source, msp.speaker_gender as gender,
            msp.audio_id, msp.status
            from media_speaker_mapping msp 
                inner join media_metadata_staging mms 
                    on msp.audio_id = mms.audio_id
            left outer join speaker s 
                    on s.speaker_id = msp.speaker_id 
            where mms.source = :source and mms.language=:language and msp.status in ('Clean','Rejected') and artifact_name is null
            and (msp.is_transcribed = :is_transcribed or msp.is_transcribed is null)
            limit :count
            """
        )
        call_with_params = {"source": source, "status": "('Clean','Rejected')",
                            "language": language, "count": 2, "is_transcribed": False}
        mock_postgres_client.execute_query.return_value = expected_utterances
        catalogueDao = CatalogueDao(mock_postgres_client)
        args = mock_postgres_client.execute_query.call_args_list
        utterances = catalogueDao.get_utterance_details_by_source(source, language, 2, False, True)
        self.assertEqual(utterances, expected_utterances)
        self.assertEqual(called_with_sql, args[0][0][0])
        self.assertEqual(call_with_params, args[0][1])

    @mock.patch("ekstep_data_pipelines.common.postgres_db_client.PostgresClient")
    def test__should_update_utterance_artifact_name(self, mock_postgres_client):
        mock_postgres_client.execute_update.return_value = 2
        utterances = ["file_1.wav", "file_2.wav"]
        artifact_name = "xyz"
        audio_id = "123"
        catalogueDao = CatalogueDao(mock_postgres_client)
        catalogueDao.update_utterance_artifact(utterances, artifact_name, audio_id)
        called_with_query = (
            "update media_speaker_mapping "
            "set artifact_name=:artifact_name "
            " where audio_id=:audio_id and clipped_utterance_file_name in ('file_1.wav','file_2.wav')"
        )
        called_with_args = {"artifact_name": artifact_name, "audio_id": audio_id}
        args = mock_postgres_client.execute_update.call_args
        self.assertEqual(called_with_query, args[0][0])
        self.assertEqual(called_with_args, args[1])
