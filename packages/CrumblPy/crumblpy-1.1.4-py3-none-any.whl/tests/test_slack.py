import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from CrumblPy.slack import SlackToolKit


class TestSlackToolKit:
    
    @patch.dict('os.environ', {'SLACK_TOKEN': 'test_token'})
    @patch('CrumblPy.slack.WebClient')
    def test_init_with_env_var(self, mock_webclient):
        slack = SlackToolKit()
        assert slack.token == 'test_token'
        assert slack.default_channel == 'U04RAQM788L'
        mock_webclient.assert_called_once_with(token='test_token')
    
    @patch('CrumblPy.slack.WebClient')
    def test_init_with_explicit_token(self, mock_webclient):
        slack = SlackToolKit(token='explicit_token')
        assert slack.token == 'explicit_token'
        mock_webclient.assert_called_once_with(token='explicit_token')
    
    @patch('CrumblPy.slack.WebClient')
    def test_init_with_custom_default_channel(self, mock_webclient):
        slack = SlackToolKit(token='test_token', default_channel='C123456789')
        assert slack.default_channel == 'C123456789'
    
    @patch('CrumblPy.slack.WebClient')
    def test_get_channel_id_with_user_id(self, mock_webclient):
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        mock_client.conversations_open.return_value = {"channel": {"id": "D123456789"}}
        
        slack = SlackToolKit(token='test_token')
        result = slack._get_channel_id('U123456789')
        
        assert result == 'D123456789'
        mock_client.conversations_open.assert_called_once_with(users=['U123456789'])
    
    @patch('CrumblPy.slack.WebClient')
    def test_get_channel_id_with_channel_id(self, mock_webclient):
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        
        slack = SlackToolKit(token='test_token')
        result = slack._get_channel_id('C123456789')
        
        assert result == 'C123456789'
        mock_client.conversations_open.assert_not_called()
    
    @patch('CrumblPy.slack.WebClient')
    def test_get_channel_id_with_none(self, mock_webclient):
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        
        slack = SlackToolKit(token='test_token', default_channel='C987654321')
        result = slack._get_channel_id(None)
        
        assert result == 'C987654321'
    
    @patch('CrumblPy.slack.WebClient')
    def test_post_message_basic(self, mock_webclient):
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        
        slack = SlackToolKit(token='test_token')
        slack.post_message('Hello World', 'C123456789')
        
        mock_client.chat_postMessage.assert_called_once_with(
            channel='C123456789',
            thread_ts=None,
            text='Hello World',
            blocks=None
        )
    
    @patch('CrumblPy.slack.WebClient')
    def test_post_message_with_blocks(self, mock_webclient):
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        
        blocks = [{"type": "section", "text": {"type": "mrkdwn", "text": "Hello *World*"}}]
        
        slack = SlackToolKit(token='test_token')
        slack.post_message('Hello World', 'C123456789', blocks=blocks)
        
        mock_client.chat_postMessage.assert_called_once_with(
            channel='C123456789',
            thread_ts=None,
            text='Hello World',
            blocks=blocks
        )
    
    @patch('CrumblPy.slack.WebClient')
    def test_post_message_with_thread(self, mock_webclient):
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        
        slack = SlackToolKit(token='test_token')
        slack.post_message('Hello World', 'C123456789', thread_id='1234567890.123456')
        
        mock_client.chat_postMessage.assert_called_once_with(
            channel='C123456789',
            thread_ts='1234567890.123456',
            text='Hello World',
            blocks=None
        )
    
    @patch('os.remove')
    @patch('CrumblPy.slack.WebClient')
    def test_post_file(self, mock_webclient, mock_remove):
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        
        slack = SlackToolKit(token='test_token')
        slack.post_file('/path/to/file.txt', 'Here is a file', 'C123456789')
        
        mock_client.files_upload_v2.assert_called_once_with(
            channels='C123456789',
            file='/path/to/file.txt',
            title='/path/to/file.txt',
            initial_comment='Here is a file',
            thread_ts=None
        )
        mock_remove.assert_called_once_with('/path/to/file.txt')
    
    @patch('os.remove')
    @patch('CrumblPy.slack.WebClient')
    def test_post_file_with_thread(self, mock_webclient, mock_remove):
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        
        slack = SlackToolKit(token='test_token')
        slack.post_file('/path/to/file.txt', 'Here is a file', 'C123456789', '1234567890.123456')
        
        mock_client.files_upload_v2.assert_called_once_with(
            channels='C123456789',
            file='/path/to/file.txt',
            title='/path/to/file.txt',
            initial_comment='Here is a file',
            thread_ts='1234567890.123456'
        )
        mock_remove.assert_called_once_with('/path/to/file.txt')
    
    @patch('CrumblPy.slack.WebClient')
    def test_get_thread_id(self, mock_webclient):
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        mock_client.conversations_history.return_value = {
            'messages': [{'ts': '1234567890.123456'}]
        }
        
        slack = SlackToolKit(token='test_token')
        result = slack.get_thread_id('C123456789')
        
        assert result == '1234567890.123456'
        mock_client.conversations_history.assert_called_once_with(channel='C123456789')
    
    @patch('CrumblPy.slack.WebClient')
    def test_push_notification_success(self, mock_webclient):
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        
        slack = SlackToolKit(token='test_token')
        with patch.object(slack, 'post_message') as mock_post_message:
            slack.push_notification(project='Test Project', channel='C123456789')
            
            mock_post_message.assert_called_once_with(
                'Successfully completed the task for Test Project.',
                'C123456789'
            )
    
    @patch('CrumblPy.slack.WebClient')
    def test_push_notification_error(self, mock_webclient):
        mock_client = Mock()
        mock_webclient.return_value = mock_client
        
        test_exception = Exception('Test error message')
        
        slack = SlackToolKit(token='test_token')
        with patch.object(slack, 'post_message') as mock_post_message:
            slack.push_notification(project='Test Project', channel='C123456789', e=test_exception)
            
            mock_post_message.assert_called_once_with(
                'An error occurred for Test Project:\nTest error message',
                'C123456789'
            )