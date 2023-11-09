from clients.supabase_clients import supabase_client
from models.data_model import BaseDataModel
from models.history_model import BaseHistoryModel
from uuid import uuid4
import traceback

def upload_service(data: list[BaseDataModel], history: BaseHistoryModel) -> dict:
    """Upload data from Raspberry to Supabase database"""
    # Generate history id using module uuid4
    bit_size = 64
    history.id = uuid4().int >> bit_size

    # insert history to database
    supabase_client.table('history').insert(history.dict()).execute()
    
    # insert all data to database
    for identifikasi_udang in data:
        # Generate data id using module uuid4
        identifikasi_udang.id = uuid4().int >> bit_size
        identifikasi_udang.history_id = history.id
        try:
            # insert data to database
            supabase_client.table('identifikasi_udang').insert(identifikasi_udang.dict()).execute()
        except Exception as e:
            # print error message
            traceback.print_exc()
            return {'success': False,
                    'message': f'Error when uploading data: {e}'}
    
    # return success message
    return {'success': True,
            'message': 'Upload data success'}