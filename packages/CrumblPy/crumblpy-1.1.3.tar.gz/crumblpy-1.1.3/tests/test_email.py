import pytest
from unittest.mock import Mock, patch
from CrumblPy.email import send_gmail, generate_token


class TestSendGmailSimple:
    
    @patch('CrumblPy.email.Credentials.from_authorized_user_info')
    @patch('CrumblPy.email.build')
    @patch('time.sleep')
    def test_send_gmail_basic_simple(self, mock_sleep, mock_build, mock_creds_from_info):
        mock_token = {'token': 'test_token'}
        
        mock_creds = Mock()
        mock_creds.expired = False
        mock_creds_from_info.return_value = mock_creds
        
        mock_service = Mock()
        mock_build.return_value = mock_service
        
        send_gmail(
            sender='test@example.com',
            recipient='recipient@example.com',
            subject='Test Subject',
            body='Test body',
            token=mock_token
        )
        
        mock_build.assert_called_once()
        mock_service.users().messages().send.assert_called_once()
    
    @patch('CrumblPy.email.InstalledAppFlow.from_client_config')
    def test_generate_token_simple(self, mock_flow_from_config):
        mock_credential = {'installed': {'client_id': 'test'}}
        
        mock_flow = Mock()
        mock_creds = Mock()
        mock_flow.run_local_server.return_value = mock_creds
        mock_flow_from_config.return_value = mock_flow
        
        result = generate_token(mock_credential)
        
        assert result is True
        mock_flow.run_local_server.assert_called_once_with(port=0)