import sys
import uuid
from typing import Optional
from uuid import UUID

from .dataframe_toolkit import generate_epoch


def get_streamlit_token():
    if 'streamlit' in sys.modules:
        st = sys.modules['streamlit']
        if st.query_params is not None and "auth_token" in st.query_params:
            auth_token = st.query_params["auth_token"]
            return auth_token
    return None


def get_streamlit_domain():
    if 'streamlit' in sys.modules:
        st = sys.modules['streamlit']
        if st.query_params is not None and "dsapi" in st.query_params:
            domain = st.query_params["dsapi"]
            return domain
    return None

def get_streamlit_twin_id() -> Optional[UUID]:
    """
    return current selected twin_id.
    :return:
    """
    if 'streamlit' in sys.modules:
        st = sys.modules['streamlit']
        if st.query_params is not None and "twin_id" in st.query_params:
            twin_id = uuid.UUID(st.query_params["twin_id"])
            return twin_id
    return None


def get_streamlit_from() -> Optional[int]:
    """
    timestamp representation of from parameter on UI (ms)
    :return:
    """
    if 'streamlit' in sys.modules:
        st = sys.modules['streamlit']
        if st.query_params is not None and "from" in st.query_params:
            param = st.query_params["from"]
            if 'now' in param:
                return generate_epoch(param)
            else:
                return int(param)
    return None


def get_streamlit_to() -> Optional[int]:
    """
    timestamp representation of to parameter on UI (ms)
    :return:
    """
    if 'streamlit' in sys.modules:
        st = sys.modules['streamlit']
        if st.query_params is not None and "to" in st.query_params:
            param = st.query_params["to"]
            if 'now' in param:
                return generate_epoch(param)
            else:
                return int(param)
    return None
