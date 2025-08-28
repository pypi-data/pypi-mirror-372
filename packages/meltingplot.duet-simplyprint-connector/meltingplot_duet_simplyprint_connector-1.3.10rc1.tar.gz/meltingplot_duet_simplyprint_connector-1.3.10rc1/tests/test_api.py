import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

import aiohttp

from .context import RepRapFirmware


@pytest.fixture
def mock_session():
    session = AsyncMock(aiohttp.ClientSession)
    session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={'err': 0})
    session.post.return_value.__aenter__.return_value.read = AsyncMock(return_value=b'Response')
    session.post.return_value.__aenter__.return_value.json = AsyncMock(return_value={'err': 0})
    session.get.return_value.__aenter__.return_value.text = AsyncMock(return_value='Response')
    session.closed = False
    return session


@pytest.fixture
def reprapfirmware(mock_session):
    return RepRapFirmware(session=mock_session)


@pytest.mark.asyncio
async def test_connect(reprapfirmware, mock_session):
    response = await reprapfirmware.connect()
    assert response == {'err': 0}
    mock_session.get.assert_called_once_with('http://10.42.0.2/rr_connect', params={'password': 'meltingplot', 'sessionKey': 'yes'})


@pytest.mark.asyncio
async def test_disconnect(reprapfirmware, mock_session):
    response = await reprapfirmware.disconnect()
    assert response == {'err': 0}
    mock_session.get.assert_called_once_with('http://10.42.0.2/rr_disconnect')


@pytest.mark.asyncio
async def test_rr_model(reprapfirmware, mock_session):
    response = await reprapfirmware.rr_model(key='test', frequently=True, verbose=True, depth=99, array=10)
    assert response == {'err': 0}
    mock_session.get.assert_called_once_with('http://10.42.0.2/rr_model', params={'key': 'test', 'flags': 'fvd99a10'})


@pytest.mark.asyncio
async def test_rr_gcode(reprapfirmware, mock_session):
    orig_reply = reprapfirmware.rr_reply
    reprapfirmware.rr_reply = AsyncMock(return_value='Response')
    response = await reprapfirmware.rr_gcode('G28')
    assert response == 'Response'
    mock_session.get.assert_called_once_with('http://10.42.0.2/rr_gcode', params={'gcode': 'G28'})
    reprapfirmware.rr_reply = orig_reply


@pytest.mark.asyncio
async def test_rr_reply(reprapfirmware, mock_session):
    response = await reprapfirmware.rr_reply()
    assert response == 'Response'
    mock_session.get.assert_called_once_with('http://10.42.0.2/rr_reply')


@pytest.mark.asyncio
async def test_rr_download(reprapfirmware, mock_session):
    async def chunks(size):
        data = [b'chunk1', b'chunk2']
        for item in data:
            yield item

    mock_session.get.return_value.__aenter__.return_value.content.iter_chunked = chunks
    async for _ in reprapfirmware.rr_download('test.txt'):
        break

    #async for chunk in reprapfirmware.rr_download('test.txt'):
    #    assert chunk in chunks
    mock_session.get.assert_called_once_with('http://10.42.0.2/rr_download', params={'name': 'test.txt'})


@pytest.mark.asyncio
async def test_rr_upload(reprapfirmware, mock_session):
    content = b'testtttttt'
    response = await reprapfirmware.rr_upload('test.txt', content)
    assert response == {'err': 0}
    mock_session.post.assert_called_once_with('http://10.42.0.2/rr_upload', data=content, params={'name': 'test.txt', 'crc32': '075b1c7c'}, headers={'Content-Length': '10'})


@pytest.mark.asyncio
async def test_rr_upload_stream(reprapfirmware, mock_session):
    file = MagicMock()
    file.tell.return_value = 10
    file.read.side_effect = [b'chunk1', b'chunk2', b'']
    mock_session.reset_mock()
    response = await reprapfirmware.rr_upload_stream('test.txt', file)
    assert response == {'err': 0}
    mock_session.post.assert_called_once()
    assert mock_session.post.call_args[1]['url'] == 'http://10.42.0.2/rr_upload'
    assert mock_session.post.call_args[1]['params'] == {'name': 'test.txt', 'crc32': 'be0e1d1b'}


@pytest.mark.asyncio
async def test_rr_filelist(reprapfirmware, mock_session):
    response = await reprapfirmware.rr_filelist('/path/to/directory')
    assert response == {'err': 0}
    mock_session.get.assert_called_once_with('http://10.42.0.2/rr_filelist', params={'dir': '/path/to/directory'})


@pytest.mark.asyncio
async def test_rr_fileinfo(reprapfirmware, mock_session):
    response = await reprapfirmware.rr_fileinfo('test.txt')
    assert response == {'err': 0}
    mock_session.get.assert_called_once_with('http://10.42.0.2/rr_fileinfo', params={'name': 'test.txt'})


@pytest.mark.asyncio
async def test_rr_mkdir(reprapfirmware, mock_session):
    response = await reprapfirmware.rr_mkdir('/path/to/directory')
    assert response == {'err': 0}
    mock_session.get.assert_called_once_with('http://10.42.0.2/rr_mkdir', params={'dir': '/path/to/directory'})

@pytest.mark.asyncio
async def test_reconnect_success(reprapfirmware, mock_session):
    response = await reprapfirmware.reconnect()
    assert response == {'err': 0}
    mock_session.get.assert_called_once_with('http://10.42.0.2/rr_connect', params={'password': 'meltingplot', 'sessionKey': 'yes'})

@pytest.mark.skip
@pytest.mark.asyncio
async def test_reconnect_multiple_calls(reprapfirmware, mock_session):
    # Simulate multiple reconnect calls
    # TODO make mock_session make a context switch/yield to make the test work
    mock_session.get.return_value.__aenter__.return_value.json.side_effect = lambda: asyncio.sleep(1)
    responses = await asyncio.gather(reprapfirmware.reconnect(), reprapfirmware.reconnect(), reprapfirmware.reconnect())
    for response in responses:
        assert response == {'err': 0}
    mock_session.get.assert_called_once_with('http://10.42.0.2/rr_connect', params={'password': 'meltingplot', 'sessionKey': 'yes'})

@pytest.mark.asyncio
async def test_reconnect_with_session_key(reprapfirmware, mock_session):
    mock_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={'err': 0, 'sessionKey': 'test_key'})
    response = await reprapfirmware.reconnect()
    assert response == {'err': 0, 'sessionKey': 'test_key'}
    #assert reprapfirmware.session.headers['X-Session-Key'] == 'test_key'
    mock_session.get.assert_called_once_with('http://10.42.0.2/rr_connect', params={'password': 'meltingplot', 'sessionKey': 'yes'})

@pytest.mark.asyncio
async def test_reconnect_with_session_timeout(reprapfirmware, mock_session):
    mock_session.get.return_value.__aenter__.return_value.json = AsyncMock(return_value={'err': 0, 'sessionTimeout': 10000})
    response = await reprapfirmware.reconnect()
    assert response == {'err': 0, 'sessionTimeout': 10000}
    assert reprapfirmware.session_timeout == 10000
    mock_session.get.assert_called_once_with('http://10.42.0.2/rr_connect', params={'password': 'meltingplot', 'sessionKey': 'yes'})